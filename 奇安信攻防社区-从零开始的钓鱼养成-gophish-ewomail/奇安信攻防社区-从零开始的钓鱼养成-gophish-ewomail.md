

# 奇安信攻防社区-从零开始的钓鱼养成-(gophish+ewomail)

### 从零开始的钓鱼养成-(gophish+ewomail)

详细讲解钓鱼搭建流程

# 0x00 前景

由于马上开始护网了,公司想要在护网前对公司员工进行钓鱼意识培训,所以要我搞一下钓鱼,好久没搞了,还是在网上找了下资料,本次使用ewomail和gophish联动,最后总算还是完成了任务,下面我对本次钓鱼实战进行下详细步骤复盘,以后要搞也方便,希望和师傅们多交流交流,有啥更好的方法可以给我留言,当然还是那句话,该篇文章只做学习交流使用,犯罪等一切行为与本文作者无关。

# 0x01 域名购买

1.本次演练由于是内部演练,未申请国外的域名,使用的是国内腾讯云的域名,注册购买也很简单,购买后进入我的域名进行解析,下一节配置邮箱的时候对着我的配置配就行了。

![图片.png](assets/1699927140-2174f643eb3ab4274af66640c4aaee12.png)

![图片.png](assets/1699927140-f39963ee5ed06ea885e1dd6601dcd0ae.png)

![图片.png](assets/1699927140-1e04259602bc1c57861e19c989c28c1c.png)

# 0X02 ewomail安装

1.关闭selinux

vi /etc/sysconfig/selinux

SELINUX\\=enforcing 改为 SELINUX\\=disabled

2.使用git进行安装

这里我们的vps是国外的,所有安装域名后面加空格加en，例如 sh ./start.sh ewomail.cn en,注意ewomail.cn替换为我们注册的邮件域名。

yum -y install git

cd /root

git clone [https://github.com/gyxuehu/EwoMail.git](https://github.com/gyxuehu/EwoMail.git)

cd /root/EwoMail/install

需要输入一个邮箱域名，不需要前缀，列如下面的ewomail.cn，域名后面要加空格加en

sh ./start.sh ewomail.cn en

3.访问地址

邮箱管理后台,默认口令admin,ewomail123!

[http://IP:8010](http://ip:8010/)

![图片.png](assets/1699927140-98f1b5975f4a437ea7ec102838452433.png)

![图片.png](assets/1699927140-b902d0f97da963700ca5870d56bd8ce5.png)

web邮件系统

[http://IP:8000](http://ip:8000/)

![图片.png](assets/1699927140-7a3d96de5ef41679730458edbd92b162.png)

4.配置邮箱

1.在购买的dns解析处配置,这里用腾讯云的配置,配置dkim值(DKIM是电子邮件验证标准，域名密钥识别邮件标准，主要是用来防止被判定为垃圾邮件)需要到服务器使用命令

amavisd -c /etc/amavisd/amavisd.conf showkeys

![图片.png](assets/1699927140-4523a15438906526a1e76c30cd28c425.png)

![图片.png](assets/1699927140-c5c14b9006ea5d8bc574bf9607571336.png)

![图片.png](assets/1699927140-5da29b6702f8728a6bcbf401ab59323c.png)

2.安装完成后邮箱系统配置如下马赛克的地方为你的域名。

![图片.png](assets/1699927140-a750ba9fe84532528dd3d24bc4ff07d5.png)

2.修改/etc/hostsname的配置文件,把主机改为mail.xxx,/etc/hosts里配置 127.0.0.1 mail.xxx smtp.xxx imap.xxx 这里的xxx为你的域名,设置完后重启生效。

![图片.png](assets/1699927140-5b903caa9a8f5d17613afee92279f3fd.png)

![图片.png](assets/1699927140-7f8e250d15297481aed9a40aad36ea4e.png)

![图片.png](assets/1699927140-59e0bb55b4a0008a18abf3d9301ab67d.png)

![图片.png](assets/1699927140-03b8b40f3c1a53ff51c9c87bceb67482.png)

5.添加邮箱用户,添加完毕可以点击右上角的web邮件系统,如果域名配置正确,这里地址应该变为域名:8000。  
![图片.png](assets/1699927140-88205ab51fb409cc395caa59f6d0a3fe.png)

![图片.png](assets/1699927140-accaa12a93cc0755b74cf12d9a55c5b0.png)

![图片.png](assets/1699927140-a5e979a06e673eb8593289447f576480.png)

![图片.png](assets/1699927140-0dfc875664fb70bdb2f7effe14e0b16b.png)

# 0x03 gophish配置

1.安装gophish

这里采用docker快捷安装

docker pull gophish/gophish

docker run -it -d --rm --name gophish -p 3333:3333 -p 8003:80 -p 8004:8080 gophish/gophish

docker logs gophish(查看安装日志中的登录密码)

2.配置gophish

1.访问地址,登录账号admin,密码为日志中的密码gophish

[https://VPS:3333](https://vps:3333/)

![图片.png](assets/1699927140-9774a73744a950149714374078f45175.png)

2.依次配置gophish的各个模块.如下:

1.设置Sending ProfileS,这里是添加发送邮箱服务器的地方,from:填写你刚才ewomail添加的邮箱账号,host:填写你注册域名:25,username:也是填写ewomail添加的邮箱账号,密码;填写添加邮箱账号是设置的密码,保存即可。

![图片.png](assets/1699927140-0eb2174c96cd765206c5f4c65c511acf.png)

2.设置Landing Pages.该页面为用于钓鱼的页面

1.这里系统自带的importsite可以直接输入要copy的网站地址,但是这种方法我尝试了一些网站,有许多网站都不能完美copy,这里我介绍一种方法,使用火狐带的插件,save page可以完美把网页给copy下来,然后把copy下的页面源码贴在HTML的位置就行了,这里我随便找个后台演示下。

![图片.png](assets/1699927140-404d1bed1b6914f2ab65a1b94ac5b75b.png)

![图片.png](assets/1699927140-e6694b43464bd4e9ac52b3fe0a777ac0.png)

![图片.png](assets/1699927140-44a13a1b4e15da540236107becb2e97d.png)

![图片.png](assets/1699927140-3b8e18de85fbede3445141e48ac877f2.png)

![图片.png](assets/1699927140-f25b58a9f3c77f0d438ee068999ca1a3.png)

![图片.png](assets/1699927140-b30d36e75ba433ae340ac3bd9d728e54.png)

![图片.png](assets/1699927140-639d0fbf17abdd93810a110880687f5f.png)  
3.配置Email Templates

这里使用import Email导入已经写好的.eml后缀的邮件原文,可以先配置好钓鱼邮件内容,然后自己测试发送下,到收件人那里获取邮件原文导入即可。

![图片.png](assets/1699927140-3c5f86fb23213ba1c966af6e1cab808f.png)

这里以qq邮箱为例,我们找到一封QQ邮件,在下图所示位置,打开邮件原文,复制里面的内容导入即可。

![图片.png](assets/1699927140-b94c81a05d8e7db91c96ca4968fba45a.png)

注意勾选Change Links to Point这个选项,后面我们针对邮件模板里的a href="xxxxxx"可以将xxxx替换为{{.URL}},这样邮件里面的钓鱼链接就会被系统自动替代了。

![图片.png](assets/1699927140-7eb907064bfd1a951b58c8474afd80be.png)

4.配置用户和组

这里主要是配置要发送的人,可以使用csv导入,如果是xlxs文件是不行的需要进行转换,只有要使用excel自带的另存为csv带逗号格式的就行了。

![图片.png](assets/1699927140-b59c8d0258eb97c21de85037d84a44d3.png)

![图片.png](assets/1699927140-46724a55e636f96f27d4949007bf561d.png)

![图片.png](assets/1699927140-380b71e68951cafbcc5eb6cf81c9e01d.png)

![图片.png](assets/1699927140-140e083cd465dc5acfb19f6ed48a0939.png)

![图片.png](assets/1699927140-671fef649afd8f5f6d14c11cfbc2936d.png)

5.这里配置Campains,这个模块主要就是拿来钓鱼了,依次勾选上诉这里我们配置好的选项就好了,ULR要设置为hppt://(这里可以为域名或者vps的Ip,具体看需求):8003,配置好就可以愉快钓鱼了。

![图片.png](assets/1699927140-84ba7a76d5b36be72fc582d02e07ca9f.png)

# 0x04 钓鱼结果展示

1.这里点击图中所示可以看到钓鱼详情,值得一提的是我是前一天发的,第二天发现只有9个人点击,但是其中5个人都上当提交了数据,虽然可以交差,但是总感觉哪里不对,为啥点击的这么少,最后才发现我那邮箱服务器一个时间内发送邮件数量太多会导致很多邮件被退回。。。,所以如果要发送大量邮件,服务器配置不行话,建议定个时间分组发送了。

![图片.png](assets/1699927140-c5184258c31b1e171278a3297beef020.png)

![图片.png](assets/1699927140-42b5f4529778e782fc1a8b30452a210e.png)

![图片.png](assets/1699927140-626d80f5bf955a9fa637fc39770721c7.png)

设置下分组再发有调了几个,哈哈,等今晚在看估计更多了,交差溜了。

![图片.png](assets/1699927140-dbd883ea0ea6a4be48840e44b5cae17d.png)
