

# 奇安信攻防社区-【Web实战】记某次攻防演练之内网遨游

### 【Web实战】记某次攻防演练之内网遨游

由客户授权的一次攻防演练，从外网钓鱼到内网遨游，也算是幸不辱命，攻击路径绘制了流程图，接下来会按照我画的攻击流程图来进行讲解。

### 前言

由客户授权的一次攻防演练，从外网钓鱼到内网遨游，也算是幸不辱命，攻击路径绘制了流程图，接下来会按照我画的攻击流程图来进行讲解，流程图如下：  
![报告流程图.png](assets/1701072264-440f569022d0341ecae71188f6f8d9f6.png)

### 外网钓鱼

首先外网收集相关信息，添加微信，构造与客服业务相对  
应的话术，诱导对方点击木马，过程如下图：  
![image.png](assets/1701072264-96f09e40eb7e2a93376043af73103623.png)  
客服成功上线如下图：  
![image.png](assets/1701072264-be2ef979a71a28f2102e0cd4c0064303.png)  
然后对该企业的总监同样实施微信钓鱼，构造的话术为商务合作，诱导对方点击木马如下：  
![image.png](assets/1701072264-888069d1a4544807038ac52ccb19f0f6.png)

同样上线：  
![image.png](assets/1701072264-44ce47abe9c859ad35979b0de6d6f9c4.png)

### 内网遨游

#### 登陆相关系统

翻阅客服终端，发现密码本，成功登陆**邮箱系统**，发现大量内部办公邮件如下：  
![image.png](assets/1701072264-277deca2a592e04160fd5d50e23c25fe.png)

通过密码本登陆**运营平台**，发现2000w+记录如下：  
![image.png](assets/1701072264-d9f0f078cc0716a39b3a9338e8634c15.png)  
同时还发现该运营系统存在SQL注入如下：  
![image.png](assets/1701072264-b69406053c96f8d8d71a86481efe7088.png)  
使用sqlmap获取数据库用户密码如下：  
![image.png](assets/1701072264-eabba63329711d7f7d6d77394ba49e20.png)

通过密码本登陆**Zabbix**系统如下：  
![image.png](assets/1701072264-7df498fb4fe22aaf1ba721cbb2dc2b09.png)

#### 发现某源码，开审！

翻阅另一台终端文件时，发现了一个压缩包为install.zip,解压查看，发现为某系统源码：  
![image.png](assets/1701072264-e66392c7e5e52a2fa87e7b8969a432df.png)  
语言为PHP如下:

![image.png](assets/1701072264-8a0b9ac02dc1c1bee5559c094e8e69a9.png)

审计源码发现该系统后台插件添加处存在任意文件上传漏洞，通过添加插件的方式对向服务器中写入webshell获取到多台服务器权限。  
重点在Build()函数里  
![image.png](assets/1701072264-3e8e3aa166cd8a6d2563356b4d8ef70c.png)

直接把请求的config数据写入到插件目录下的config.php文件中了，如下：  
![image.png](assets/1701072264-6df385b33055cecf07574b61a96f712b.png)

burp构造数据包发包：  
![image.png](assets/1701072264-8c1b03e6a7ac74274e5f7f1c8e9e871b.png)  
解析成功，getshell如下：  
![image.png](assets/1701072264-72de9bae429082d24965e4a7d9583188.png)  
![image.png](assets/1701072264-e9ccb7546feca441574500f91dafae49.png)

通过此0day拿下多台服务器权限如下：

![image.png](assets/1701072264-4c0b9cdc858b75b693987fc90534704f.png)

#### 掌控云上资产

通过前面控制的机器，在其中一台机器中，翻阅配置文件，找到数据库账号密码，登陆数据库在其中一个表中发现了AK/SK如下：  
![image.png](assets/1701072264-074c4f3d536f3997ac714a3e97cd7c0f.png)  
可以接管阿里云所有系统：  
![image.png](assets/1701072264-9abc6a6768c9f619a2e6e5e7a9c875a2.png)

#### 拿下gitlab

通过linux历史记录获取到gitlab后台权限如下  
![image.png](assets/1701072264-919438bbd8be993178a312fbc3161e9d.png)

通过探测发现gitlab存在历史漏洞CVE-2021-22205，利用该漏洞获取到gitlab服务器权限  
![image.png](assets/1701072264-132f49cf4a7954f4c25751a48e6fbac7.png)

利用gitlab的redis未授权访问漏洞写入ssh密钥，获取到root权限如下：  
![image.png](assets/1701072264-2c7b59c5c9d427b2a2a8b2aacbc437b2.png)  
![image.png](assets/1701072264-e400e320acbfe31b5568e6c61d8b2c26.png)

在gitlab的代码中进行翻阅，发现禅道数据库账号密码，真香，同时也在这里提个小建议，如果进入内网并发现gitlab，第一时间拿下来，好处多多。  
![image.png](assets/1701072264-005a45d6ea3cc04af3ca42b4d73b4770.png)

数据库直接修改root密码进入后台：  
![image.png](assets/1701072264-0e7f8d6f612e47bac639d038e1eb2d21.png)  
通过后台功能getshell如下：  
![image.png](assets/1701072264-a0c7fd5f7033bd68469bcff700368a19.png)

#### 征服Jenkins

通过gitlab系统发现该机器存在nginx，通过**查看nginx配置文件**，发现对sonar\\jenkins\\等多个系统进行反向代理，通过在jenkins.conf文件中配置日志 获取cookie格式，获取到了jenkins用户登陆cookie如下：  
![image.png](assets/1701072264-9da9d6a887216f850d467af82bd7fd76.png)  
![image.png](assets/1701072264-097299b108f8ee0d5f3d87046be2f649.png)  
![image.png](assets/1701072264-3313081db31a7079fb3bd2ba263fa9a0.png)

使用获取到的cookie成功登陆Jenkins：  
![image.png](assets/1701072264-f0c3f46fff15e6a805e48851b047ea16.png)

### 小结

通过社工钓鱼撕开口子，内网转了一大圈，也获取了一些成果，咱们下期见。
