
# CentOS7下给Postfix启用DKIM身份认证

邮件服务器搭建  
[https://www.jianshu.com/p/cecb77649f51](https://www.jianshu.com/p/cecb77649f51)

### SPF 记录的设置

向你的邮件域名添加一条 TXT 记录

v=spf1 ip4:发信服务器的IP ~all

当然您也可以添加多个 IP 地址，网上有很多教程。

### 反向解析

请联系你的机房，或 云服务商，国内目前仅阿里云可以联系客服进行免费设置，国外一般 VPS 的控制面板就可以。

### DKIM 签名

安装 opendkim  
添加 EPEL 库

```cobol
yum -y install epel-release
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
yum clean
```

安装

```undefined
yum install opendkim
```

安装报错 No package opendkim available.  
可能是epel/x86\_64 Extra Packages for Enterprise Linux 7 - x86\_64 源是disabled 状态，修改/etc/yum.repos.d/epel.repo的enabled=1即可

```cobol
vi /etc/yum.repos.d/epel.repo

[epel]
[epel]
name=Extra Packages for Enterprise Linux 7 - $basearch
#baseurl=http://download.fedoraproject.org/pub/epel/7/$basearch
mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch
failovermethod=priority
enabled=1
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
```

然后运行：  
yum makecache  
再检查一下：

```less
yum repolist all
```

![13034051-6282b85fb6d3240e.png](assets/1700819932-375abe23f61b2d15c09cb5506415ff0f.png)

image.png

  

如无意外，就能安装 OpenDKIM 了：

```undefined
yum install opendkim
```

修改 opendkim 配置文件（直接将原来的删除修改成下面的内容）

```cobol
UserID                  opendkim:opendkim
UMask                   022
Mode                    sv
PidFile                 /var/run/opendkim/opendkim.pid
Canonicalization        relaxed/relaxed
TemporaryDirectory      /var/tmp
ExternalIgnoreList      refile:/etc/opendkim/TrustedHosts
InternalHosts           refile:/etc/opendkim/TrustedHosts
KeyTable                refile:/etc/opendkim/KeyTable
SigningTable            refile:/etc/opendkim/SigningTable
MinimumKeyBits          1024
Socket                  inet:8891
LogWhy                  Yes
Syslog                  Yes
SyslogSuccess           Yes
```

创建密钥

```cobol
mkdir /etc/opendkim/keys/YourDomain.com
opendkim-genkey -D /etc/opendkim/keys/YourDomain.com/ -d YourDomain.com -s default
```

创建完毕后，将其添加到 /etc/opendkim/KeyTable 中

```cobol
default._domainkey.YourDomain.com YourDomain.com:default:/etc/opendkim/keys/YourDomain.com/default.private
```

然后添加 /etc/opendkim/SigningTable

```typescript
*@YourDomain.com default._domainkey.YourDomain.com
```

设置允许进行签名的主机 到 /etc/opendkim/TrustedHosts 中，一般情况下都是本机发信，我们将 127.0.0.1 和localhost加入即可。

```cobol
vim /etc/opendkim/TrustedHosts
```

![13034051-39971b4e3d6d33e3.png](assets/1700819932-e2024fe8025fbe39d76d03b267413075.png)

image.png

  

给opendkim指定用户和授权

```cobol
chown opendkim:opendkim -R /etc/opendkim/
chmod -R 700 /etc/opendkim
```

#### 设置 DNS 记录

到 /etc/opendkim/keys/YourDomain.com/default.txt 可以找到你的 key 。然后在域名服务商解析txt值，记录类型 TXT 子域名 default.\_domainkey ，记录内容就是 default.txt 里面从 v=DKIM1 开始的内容。

  

![13034051-4721b2acb2dd05d2.png](assets/1700819932-2d055e5d9fc1245ae0c54277b7c585f0.png)

image.png

  

此时 DKIM 签名软件已经可以正常工作了，接下来就要让 Postfix 所发的邮件经过其处理，  
打开 Postfix 的 main.cf 配置文件，到达底部，添加如下内容

```cobol
milter_default_action = accept
milter_protocol = 2
smtpd_milters = inet:8891
non_smtpd_milters = inet:8891
```

然后重新启动postfix和opendkim

```sql
systemctl start opendkim.service
systemctl start postfix.service
```

###### 设置DMARCK记录

1.  登录域名管理后台，找到需要添加DMARCK记录的域名，增加TXT记录;
2.  设置DMARC记录之前，请务必确保已设置SPF记录;

| 记录名 | 记录值 |
| --- | --- |
| 需要设置SPF的域名 | v=spf1 a mx ip4:xxx.xxx.xxx.xxx ~all |

3.  设置了SPF记录后，添加以下DMARC记录：

| 记录名 | 记录值 |
| --- | --- |
| \_dmarc | v=DMARC1; p=none; fo=1; ruf=mailto:[dmarc@qiye.163.com](https://links.jianshu.com/go?to=mailto%3Admarc%40qiye.163.com); rua=mailto:[dmarc\_report@qiye.163.com](https://links.jianshu.com/go?to=mailto%3Admarc_report%40qiye.163.com) |

注意：Dmarc记录里，有两个值可由您来自定义：

-   p：用于告知收件方，当检测到某邮件存在伪造发件人的情况，收件方要做出什么处理，reject为拒绝该邮件；none为不作任何处理；quarantine为将邮件标记为垃圾邮件。
-   ruf：用于当检测到伪造邮件，收件方须将检测结果发送到哪个邮箱地址。  
    建议：p值最优设置方式是第一次设置选择none，观察发信情况一个月，再改为quarantine，再观察一个月，最后再设为reject。

可以在[http://www.appmaildev.com/cn/dkim](https://links.jianshu.com/go?to=http%3A%2F%2Fwww.appmaildev.com%2Fcn%2Fdkim)测试  

![13034051-6846876f24684cc1.png](assets/1700819932-d3cb847879ea06405275bae8ffd6fa67.png)

image.png

发送给谷歌邮箱打开显示原始邮件可以看到

  

![13034051-b384322a39bf02e5.png](assets/1700819932-0e1a8485872184e5f24c219197a7a9de.png)

image.png

  

![13034051-057a4bab64ca8294.png](assets/1700819932-07f83398ae20ab2faec64209f4f7093a.png)

image.png

  

网页邮箱测试

  

![13034051-d885793386485606.png](assets/1700819932-a63661a0c26366c179a67c0ad49f4971.png)

image.png

  

![13034051-02f6fc387746d606.png](assets/1700819932-5710f5b988d60fccd4f2f4760199cba2.png)

image.png

一个不错的邮箱测试工具

-   [http://www.mail-tester.com/](https://links.jianshu.com/go?to=http%3A%2F%2Fwww.mail-tester.com%2F)
