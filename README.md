# Use-YOLO-to-train-your-own-database
The step of use YOLO to train your own database 

【利用YOLO训练自己的数据】

1.收集数据集以及制作标签：xml或者json格式

2.应用脚本文件对xml或json文件进行处理，提取出：
    类别索引object box中心坐标x/整个图片的w box中心坐标y/整个图片的h box的w/整个图片的w box的h/整个图片的h，
    并且，生成txt的形式要和训练图片的格式(文件夹存储结构)、名称完全一致
 
	eg.
  
    1 0.716797 0.395833 0.216406 0.147222
    
    0 0.687109 0.379167 0.255469 0.158333
    
    1 0.420312 0.395833 0.140625 0.166667

3.生成train图片的路径：

	①直接用训练图片生成：
	find /home/chensc/JPEGImage/...(绝对路径，图片根文件夹)/ | grep(查找的意思) jpg（要查找的包含关键字） > train.txt 
	然后将生成的train.txt放到XXX-project中
  
    ②用json转的labels中txt文件转换(因为这些labels中txt文件和图片名称对应)：
    
      (1)find /home/chensc/labels/...(绝对路径，特征labels的根文件夹)/ | grep(查找的意思) txt（要查找的包含关键字） > train.txt 
      (2)sed -i 's/labels（被替换的）/JPEGImage（替换后的）/g' train.txt（文件路径）
      (3)sed -i 's/txt/jpg/g' train.txt

4.在darknet中新建文件夹XXX-project，包括:

    ①XXX.cfg（网络模型）：
    [convolutional]
    filters=5*(classes+4+1)
		                     
    [region]
    classes=n

    ②obj.names：使用对象名称，每个都一行

    ③obj.data：（绝对/相对路径都可以）
          classes= n
          train  = XXX-project/train.txt
          valid  = XXX-project/test.txt（可以和train一样）
          names = XXX-project/obj.names
          backup = XXX-project/backup/ （存训练后模型的位置）

    ④为卷积图层下载预先训练的权重（76 MB）：http : //pjreddie.com/media/files/darknet19_448.conv.23，放到XXX-project

5.训练：cd 到darknet中

    ./darknet detector train XXX-project/obj.data XXX-project/XXX.cfg darknet19_448.conv.23(预训练的网络模型) 10(修改网络后，只取前10层) -clear(此处是为了将预训练迭代过的次数清0，使得cfg中的max batch可以直接写要迭代的次数) > log.txt(打印log日志)


6.可视化：

    ①将log.txt拷贝到包含.sh和.py的文件夹下
    ②bash general_cifar_log.sh log.txt，这是会有hand_log_data.txt生成
    ③python analzy_log.py

注意：

    1.yolo在训练的时候，obj、recall、IOU、calss以及loss就已经能表示训练的好坏了，val、test用不上，都写成和train一样的就行
    
    2.训练时候xml、json标注文件就没有用了，只有txt文件
    
    3.txt中类别只能用索引0123...表示，对应obj.names中的类别
    
    4.训练集文件夹名字只能叫：JPEGImages；标签文件夹名字只能叫：labels
    （解释）：必须把训练集JPEGImages和标签labels放在一起，darknet之所以不用标签的路径，是因为读取图片路径时候是自动把JPEGImages换成labels、把png换成txt
    
    5.cfg文件解析：(windows下写cfg会有回车键，ubuntu解析会出错，vi -b XXX.cfg ，delete删除^M)
       
        ①batch是并行运算的图片数量：64,128，指的是64张图片计算一个loss；subdivisions是将batch分成几份来跑，防止显存爆炸
        
        ②数据增强：angle=0、saturation = 1.5、exposure = 1.5、hue=.1
        
        ③初始学习率：learning_rate=0.0001、最大迭代次数：
                    max_batches = 100000、policy=steps、改变学习率的迭代次数：steps=100, 50000, 80000、每次改变学习率的倍数：scales=10,.1,.1
                    过程解释：此过程中初始到100次迭代学习率是0.0001，100-50000迭代是0.001,50000-80000迭代是0.0001,80000-100000迭代是0.00001
                    正常过程：应该是先给一个大的学习率，然后随着迭代次数的增加，应该减小学习率
                    初始膨胀学习率：为了防止大学习率跑出nan，最开始给一个小的学习率先跑到一个局部最优解，然后膨胀学习率跑出局部最优解，
                    在之后慢慢减小学习率

        ④yolo v2网络若输入是416*416，那最后的特征图输出应该必须是13*13(如果因为预训练中修改了输入图片大小，导致输出不是13*13了，需要修改网络)
        
        ⑤倒数第二层以及最后一层是：
        [convolutional]
        batch_normalize=1
        filters=512
        size=3
        stride=1
        pad=1
        activation=leaky
        #预训练锁死权重，等到loss不在下降时候在不锁权重(这样是因为最开始反向传播会打乱本来预训练好的模型的权重，不锁死的话特征白提取了)
        stopbackward=1
        
        [convolutional]
        size=3
        stride=1
        pad=1
        filters=35 #(classes+4+1)*anchor数5
        activation=linear #线性分类器

        ⑥后面：
        [region]
        anchors = 0.71, 5.15,  0.39, 1.21,  1.83, 3.46,  0.94, 1.83,  3.15, 6.56 #anchors尺寸大小，k-means算法得出
        bias_match=1
        classes=2 #类别数
        coords=4
        num=5 #每个单元格预测的anchors数
        softmax=1
        jitter=.2
        rescore=1

        #损失函数的权值
        object_scale=5 #包含目标的定位误差
        noobject_scale=1 #不包含目标的误差
        class_scale=1 #分类误差
        coord_scale=1 #包含目标的置信度误差
 
        #这些参数大多数网络都是这样的设置
        absolute=1
        thresh = .6
        random=1

        附上yolo参数解释帖子网址：http://blog.csdn.net/zhuiqiuk/article/details/70167963

        ⑦训练时候的log中，迭代次数后面的两个数字是loss，第一个是batch的loss，第二个是整个平均的loss 

        ⑧接着之前的训练：
        ./darknet detector train XXX-project/obj.data XXX-project/XXX.cfg darknet.backup(backup中产生的一个weights文件)  >> log.txt(用>>可以接着原来的log.txt继续打印日志)

        此处不能加-clean，-clean是将以前预训练的模型中记录的迭代次数清0，使得学习率在cfg文件里根据迭代次数判断，进行减小。
        如果接着之前的训练加-clean的话，那么迭代次数会被清0，这样学习率就会从初始的开始，对应不上之前训练的学习率。
