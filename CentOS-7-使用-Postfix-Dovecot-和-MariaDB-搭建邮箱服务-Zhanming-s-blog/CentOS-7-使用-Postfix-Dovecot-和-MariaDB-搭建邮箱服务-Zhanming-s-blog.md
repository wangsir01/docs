

# CentOS 7 使用 Postfix, Dovecot 和 MariaDB 搭建邮箱服务 - Zhanming's blog

## 前言

邮件服务是很常见的服务，有时公司内部需要使用，本文简述使用 Postfix, Dovecot 和 MariaDB 配置邮件服务的过程。

Postfix 是一个邮件传输代理软件 (MTA: Mail Transfer Agent)，支持 smtp 协议，主要用于接收和发送邮件。

Dovecot 是一个本地邮件传输服务 (LMTP: Local Mail Transfer Protocol service)，支持 imap 和 pop3 协议，主要用于验证身份，方便客户端连接服务器发送和下载邮件。

本例没有设置使用安全连接，如果希望使用安全连接，请参考 [Email with Postfix, Dovecot and MariaDB on CentOS 7](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mariadb-on-centos-7/)。

### 环境说明

CentOS 7（Minimal Install）

```terminal
$ cat /etc/centos-release
CentOS Linux release 7.6.1810 (Core)
```

### 准备域名

`邮件服务需要依赖域名服务(DNS)，您需要有修改域名配置的权限`

本例假设您已经有了自己的域名 `exmaple.com` 和服务器的入口公网 IP 地址(本例为: `12.34.56.78`) 和出口公网 IP 地址 (本例为: `18.18.18.19`)

需要设置 DNS 如下

| 记录名 | 记录类型 | 记录值 |
| --- | --- | --- |
| mail | A   | 12.34.56.78 |
| @   | MX  | mail.example.com |
| spf | TXT | v=spf1 ip4:18.18.18.19 -all |
| mail | TXT | v=spf1 include:spf.example.com -all |

说明：

1.  第一行，表示为域名 `mail.example.com` 服务器的公网 IP v4 入口地址
2.  第二行，表示域名为 `example.com`，MX 类型主要用于电子邮件服务
3.  第三行，使用于 SPF 协议，一种以IP地址认证电子邮件发件人身份的技术，记录值中 IP 设置为公网 IP v4 出口地址
4.  第四行，表示 `mail.example.com` 得 SPF 记录值，之后会查到 `spf.example.com` 得记录值

## 安装

### yum 方式安装

先更新系统

```terminal
$ sudo yum update
```

由于 postfix, dovecot 和 mariadb 都在默认的 yum 源中，可以直接 yum 安装需要的软件包

```terminal
$ sudo yum install postfix dovecot mariadb-server dovecot-mysql
...
...
Installed:
  dovecot.x86_64 1:2.2.36-3.el7
  dovecot-mysql.x86_64 1:2.2.36-3.el7
  mariadb-server.x86_64 1:5.5.60-1.el7_5  
...
...
Complete!
```

本例安装时，版本如下

-   Postfix 2.10.1
-   Dovecot 2.2.36
-   MariaDB 5.5.60

## MariaDB

### 初始化 MariaDB

配置数据库部分需要先配置 MariaDB，再创建数据库和表

开启数据库服务

```terminal
$ sudo systemctl start mariadb
```

设置开机启动

```terminal
$ sudo systemctl enable mariadb
```

使用 [mysql\_secure\_installation](https://mariadb.com/kb/en/library/mysql_secure_installation/) 初始化数据库

```terminal
$ sudo mysql_secure_installation

NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB
      SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!

In order to log into MariaDB to secure it, we'll need the current
password for the root user.  If you've just installed MariaDB, and
you haven't set the root password yet, the password will be blank,
so you should just press enter here.

Enter current password for root (enter for none): # 输入回车
OK, successfully used password, moving on...

Setting the root password ensures that nobody can log into the MariaDB
root user without the proper authorisation.

Set root password? [Y/n] y # 设置 root 密码
New password: # 输入新密码
Re-enter new password: # 再次输入新密码
Password updated successfully!
Reloading privilege tables..
 ... Success!


By default, a MariaDB installation has an anonymous user, allowing anyone
to log into MariaDB without having to have a user account created for
them.  This is intended only for testing, and to make the installation
go a bit smoother.  You should remove them before moving into a
production environment.

Remove anonymous users? [Y/n] y # 删除匿名用户
 ... Success!

Normally, root should only be allowed to connect from 'localhost'.  This
ensures that someone cannot guess at the root password from the network.

Disallow root login remotely? [Y/n] y # 不允许 root 远程登录
 ... Success!

By default, MariaDB comes with a database named 'test' that anyone can
access.  This is also intended only for testing, and should be removed
before moving into a production environment.

Remove test database and access to it? [Y/n] y # 删除测试数据库
 - Dropping test database...
 ... Success!
 - Removing privileges on test database...
 ... Success!

Reloading the privilege tables will ensure that all changes made so far
will take effect immediately.

Reload privilege tables now? [Y/n] y # 重新加载表权限
 ... Success!

Cleaning up...

All done!  If you've completed all of the above steps, your MariaDB
installation should now be secure.

Thanks for using MariaDB!
```

创建一个新的数据库

```terminal
$ sudo mysqladmin -u root -p create mailserver
```

登录 MySQL

```terminal
$ mysql -u root -p
```

创建 MySQL 用户，分配相应的权限，*注意* 替换 `mailuserpass` 为您自己的密码

```terminal
MariaDB [(none)]> GRANT SELECT ON mailserver.* TO 'mailuser'@'127.0.0.1' IDENTIFIED BY 'mailuserpass';
```

刷新 MySQL 权限，应用更改

```terminal
MariaDB [(none)]> FLUSH PRIVILEGES;
```

切换到新的数据库

```terminal
MariaDB [(none)]> USE mailserver;
Database changed
MariaDB [mailserver]> 
```

创建表来存储邮件的域名

```terminal
CREATE TABLE `virtual_domains` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

创建一个表来存储邮件地址和密码

```terminal
CREATE TABLE `virtual_users` (
  `id` int(11) NOT NULL auto_increment,
  `domain_id` int(11) NOT NULL,
  `password` varchar(106) NOT NULL,
  `email` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  FOREIGN KEY (domain_id) REFERENCES virtual_domains(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

创建一个表来存储邮件的别名

```terminal
CREATE TABLE `virtual_aliases` (
  `id` int(11) NOT NULL auto_increment,
  `domain_id` int(11) NOT NULL,
  `source` varchar(100) NOT NULL,
  `destination` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (domain_id) REFERENCES virtual_domains(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

### 添加数据

现在需要添加数据到表中

新增域名到 `virtual_domains` 表中

```terminal
INSERT INTO `mailserver`.`virtual_domains`
  (`id` ,`name`)
VALUES
  ('1', 'example.com');
```

注意，`id` ，由于三个表有主外键关系，这个 `id` 的值要插入到其他两个表中。

新增用户到 `vurtial_users` 表中。

```terminal
INSERT INTO `mailserver`.`virtual_users`
  (`id`, `domain_id`, `password` , `email`)
VALUES
  ('1', '1', ENCRYPT('password', CONCAT('$6$', SUBSTRING(SHA(RAND()), -16))), 'postmaster@example.com');
```

注意，请替换 `password` 为您的密码，替换 `postmaster@example.com` 为您的邮箱地址。

新增邮件别名，邮件别名可以主要用于转发，用于将别名的邮件转到真实的邮件地址。

```terminal
INSERT INTO `mailserver`.`virtual_aliases`
  (`id`, `domain_id`, `source`, `destination`)
VALUES
  ('1', '1', 'alias@example.com', 'postmaster@example.com');
```

### 测试插入结果

添加完数据之后，我们可以测试一下，查看一下插入的值

查看 `virtual_domains` 表的内容

```terminal
MariaDB [mailserver]> SELECT * FROM mailserver.virtual_domains;
+----+-------------+
| id | name        |
+----+-------------+
|  1 | example.com |
+----+-------------+
1 row in set (0.00 sec)
```

查看 `virtual_users` 表的内容

```terminal
MariaDB [mailserver]> SELECT * FROM mailserver.virtual_users;
+----+-----------+-----------------------------------------------------+------------------------+
| id | domain_id | password                                            | email                  |
+----+-----------+-----------------------------------------------------+------------------------+
|  1 |         1 | $6$10a9c084e87......h.NgJlUn.Nv0kbhnpqUHfBu4W6FWFq. | postmaster@example.com |
+----+-----------+-----------------------------------------------------+------------------------+
1 row in set (0.00 sec)
```

查看 `virtual_alias` 表的内容

```terminal
MariaDB [mailserver]> SELECT * FROM mailserver.virtual_aliases;
+----+-----------+-------------------+------------------------+
| id | domain_id | source            | destination            |
+----+-----------+-------------------+------------------------+
|  1 |         1 | alias@example.com | postmaster@example.com |
+----+-----------+-------------------+------------------------+
1 row in set (0.00 sec)
```

如果内容没有问题，我们可以退出数据库了

```terminal
MariaDB [mailserver]> exit
```

## Postfix

### 配置 main.cf

`main.cf` 是 Postfix 的主要配置文件，配置步骤如下

拷贝原始文件，以备恢复

```terminal
$ sudo cp /etc/postfix/main.cf /etc/postfix/main.cf.orig
```

编辑 `main.cf` 配置文件，*注意*，请替换 `example.com` 为您的域名

```terminal
$ sudo vi /etc/postfix/main.cf
```

对 `main.cf` 进行编辑，之后可以使用 `postconf -n` 查看结果

```terminal
$ sudo postconf -n
alias_database = hash:/etc/aliases
alias_maps = hash:/etc/aliases
broken_sasl_auth_clients = yes
command_directory = /usr/sbin
config_directory = /etc/postfix
daemon_directory = /usr/libexec/postfix
data_directory = /var/lib/postfix
debug_peer_level = 2
debugger_command = PATH=/bin:/usr/bin:/usr/local/bin:/usr/X11R6/bin ddd $daemon_directory/$process_name $process_id & sleep 5
html_directory = no
inet_interfaces = all
inet_protocols = all
mail_owner = postfix
mailq_path = /usr/bin/mailq.postfix
manpage_directory = /usr/share/man
mydestination =
mydomain = example.com
myhostname = mail.example.com
myorigin = $mydomain
newaliases_path = /usr/bin/newaliases.postfix
queue_directory = /var/spool/postfix
readme_directory = no
recipient_delimiter = +
relayhost =
sample_directory = /usr/share/doc/postfix-2.10.1/samples
sendmail_path = /usr/sbin/sendmail.postfix
setgid_group = postdrop
smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination
smtpd_sasl_auth_enable = yes
smtpd_sasl_local_domain = $myhostname
smtpd_sasl_path = /var/spool/postfix/private/auth
smtpd_sasl_security_options = noanonymous
smtpd_sasl_type = dovecot
unknown_local_recipient_reject_code = 550
virtual_alias_maps = mysql:/etc/postfix/mysql-virtual-alias-maps.cf, mysql:/etc/postfix/mysql-virtual-email2email.cf
virtual_mailbox_domains = mysql:/etc/postfix/mysql-virtual-mailbox-domains.cf
virtual_mailbox_maps = mysql:/etc/postfix/mysql-virtual-mailbox-maps.cf
virtual_transport = lmtp:unix:private/dovecot-lmtp
```

`main.cf` 声明了 `virtual_mailbox_domains`, `virtual_mailbox_maps`, `virtual-alias-maps` 和 `mysql-virtual-email2email` 的位置

创建 `mysql-virtual-alias-maps.cf`，注意修改相关参数值符合您的实际配置

```terminal
$ sudo vi /etc/postfix/mysql-virtual-mailbox-domains.cf
```

内容如下

```go
user = mailuser
password = mailuserpass
hosts = 127.0.0.1
dbname = mailserver
query = SELECT 1 FROM virtual_domains WHERE name='%s'
```

创建 `/etc/postfix/mysql-virtual-mailbox-maps.cf`

```terminal
$ sudo vi /etc/postfix/mysql-virtual-mailbox-maps.cf
```

内容如下

```go
user = mailuser
password = mailuserpass
hosts = 127.0.0.1
dbname = mailserver
query = SELECT 1 FROM virtual_users WHERE email='%s'
```

创建 `/etc/postfix/mysql-virtual-alias-maps.cf`

```terminal
$ sudo vi /etc/postfix/mysql-virtual-alias-maps.cf
```

内容如下

```go
user = mailuser
password = mailuserpass
hosts = 127.0.0.1
dbname = mailserver
query = SELECT destination FROM virtual_aliases WHERE source='%s'
```

创建 `/etc/postfix/mysql-virtual-email2email.cf`

```terminal
$ sudo vi /etc/postfix/mysql-virtual-email2email.cf
```

内容如下

```go
user = mailuser
password = mailuserpass
hosts = 127.0.0.1
dbname = mailserver
query = SELECT email FROM virtual_users WHERE email='%s'
```

重启 Postfix

```terminal
$ sudo systemctl restart postfix
```

使用 `postmap` 命令测试访问 `virtual_domains` 表，返回 `1` 表示成功

```terminal
$ sudo postmap -q example.com mysql:/etc/postfix/mysql-virtual-mailbox-domains.c
1
```

测试访问 `virtual_users` 表，返回 `1` 表示成功

```terminal
$ sudo postmap -q email1@example.com mysql:/etc/postfix/mysql-virtual-mailbox-maps.cf
1
```

测试 `virtual_users` 表 返回对应的 email 值

```terminal
$ sudo postmap -q postmaster@example.com mysql:/etc/postfix/mysql-virtual-email2email.cf
postmaster@example.com
```

测试 `virtual_alias` 表，返回对应的 destination 值

```terminal
$ sudo postmap -q alias@example.com mysql:/etc/postfix/mysql-virtual-alias-maps.cf
postmaster@example.com
```

### 配置 master.cf

本例没有使用加密传输，不需要配置 `/etc/postfix/master.cf`

如果需要使用加密传输，需要配置，请参考 [Email with Postfix, Dovecot and MariaDB on CentOS 7](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mariadb-on-centos-7/)

但是还是修改一下目录的权限

```terminal
$ sudo chmod -R o-rwx /etc/postfix
```

重启一下 Postfix 服务

```terminal
$ sudo systemctl restart postfix
```

## Dovecot

### 配置 Dovecot

备份需要配置的文件，以备恢复

```terminal
$ sudo cp /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.orig
$ sudo cp /etc/dovecot/conf.d/10-mail.conf /etc/dovecot/conf.d/10-mail.conf.orig
$ sudo cp /etc/dovecot/conf.d/10-auth.conf /etc/dovecot/conf.d/10-auth.conf.orig
$ sudo cp /etc/dovecot/conf.d/auth-sql.conf.ext /etc/dovecot/conf.d/auth-sql.conf.ext.orig
$ sudo cp /etc/dovecot/conf.d/10-master.conf /etc/dovecot/conf.d/10-master.conf.orig
$ sudo cp /etc/dovecot/conf.d/10-ssl.conf /etc/dovecot/conf.d/10-ssl.conf.orig
```

编辑 `/etc/dovecot/dovecot.conf` 文件，取消注释 `protocols = imap pop3 lmtp`

```terminal
$ sudo vi /etc/dovecot/dovecot.conf
```

取消如下注释内容

```terminal
# Protocols we want to be serving.
protocols = imap pop3 lmtp
```

编辑 `/etc/dovecot/conf.d/10-mail.conf`，设置邮件位置和权限的配置

```terminal
$ sudo vi /etc/dovecot/conf.d/10-mail.conf
```

修改为如下配置

```terminal
...
mail_location = maildir:/var/mail/vhosts/%d/%n
...
mail_privileged_group = mail
...
```

创建 `/var/mail/vhosts/` 目录，修改 `example.com` 为您的域名

```terminal
$ sudo mkdir -p /var/mail/vhosts/example.com
```

创建 `vmail` 用户组，用户组的 ID 为 `5000`，添加 `vmail` 用户到 `vmail` 用户组，这个系统用户将用于读取邮件

```terminal
$ sudo groupadd -g 5000 vmail
$ sudo useradd -g vmail -u 5000 vmail -d /var/mail/
useradd: warning: the home directory already exists.
Not copying any file from skel directory into it.
```

更改 `/var/mail` 的所属组和所属用户

```terminal
$ sudo chown -R vmail:vmail /var/mail/
```

更改用户授权配置文件 `/etc/dovecot/conf.d/10-auth.conf`，取消如下配置的注释

```terminal
$ sudo vi /etc/dovecot/conf.d/10-auth.conf
```

修改内容如下

```terminal
...
auth_mechanisms = plain login
...
!include auth-system.conf.ext
...
!include auth-sql.conf.ext
...
```

编辑 `/etc/dovecot/conf.d/auth-sql.conf.ext` 更改授权和存储的配置

```terminal
$ sudo vi /etc/dovecot/conf.d/auth-sql.conf.ext
```

确保如下配置

```terminal
...
passdb {
  driver = sql
  args = /etc/dovecot/dovecot-sql.conf.ext
}
...
userdb {
  driver = static
  args = uid=vmail gid=vmail home=/var/mail/vhosts/%d/%n
}
...
```

创建 `/etc/dovecot/dovecot-sql.conf.ext` 注意替换为您自己的 `dbname`, `user` 和 `password`

```terminal
$ sudo vi /etc/dovecot/dovecot-sql.conf.ext
```

输入如下内容

```terminal
driver = mysql
connect = host=127.0.0.1 dbname=mailserver user=mailuser password=mailuserpass
default_pass_scheme = SHA512-CRYPT
password_query = SELECT email as user, password FROM virtual_users WHERE email='%u';
```

更改 `/etc/dovecot` 目录的所属权限

```terminal
$ sudo chown -R vmail:dovecot /etc/dovecot
```

更改 `/etc/dovecot` 目录的读写权限

```terminal
$ sudo chmod -R o-rwx /etc/dovecot
```

编辑服务配置文件 `/etc/dovecot/conf.d/10-master.conf`

```terminal
$ sudo vi /etc/dovecot/conf.d/10-master.conf
```

添加或取消注释，主要涉及如下内容

```terminal
...
service imap-login {
  inet_listener imap {
    port = 143
  }
  inet_listener imaps {
    #port = 993
    #ssl = yes
  }
  ...
}
...
service pop3-login {
  inet_listener pop3 {
    port = 110
  }
  inet_listener pop3s {
    #port = 995
    #ssl = yes
  }
}
...
...
service lmtp {
  unix_listener /var/spool/postfix/private/dovecot-lmtp {
    #mode = 0666i
    mode = 0600
    user = postfix
    group = postfix
  }
...
}
...
service auth {
  ...
  unix_listener /var/spool/postfix/private/auth {
    mode = 0660
    user = postfix
    group = postfix
  }

  unix_listener auth-userdb {
    mode = 0600
    user = vmail
  }
...
  user = dovecot
}
...
service auth-worker {
  ...
  user = vmail
}
```

保存更改后，重启 dovecot 服务

```terminal
$ sudo systemctl restart dovecot
```

## 测试

测试一下邮件服务，本例已经新建了 `postmaster@example.com` 的邮箱，以此为例

本例使用 `mailx` 进行发邮件的测试，先进行安装

```terminal
$ sudo yum install mailx
```

使用如下命令进行测试

```terminal
$ sudo mail postmaster@example.com
Subject: Hello email
Hello
.
```

`*注意*` 输入 `Ctrl+D` 进行退出并发送

当邮件发送之后，我们可以通过查看日志 `/var/log/maillog` 进行确认

```terminal
$ sudo tail /var/log/maillog
Aug  9 10:11:42 localhost postfix/cleanup[3427]: C728062BF: message-id=<20190810101142.C728062BF@example.com>
Aug  9 10:11:42 localhost postfix/qmgr[3410]: C728062BF: from=<root@example.com>, size=515, nrcpt=1 (queue active)
Aug  9 10:11:42 localhost postfix/pipe[3435]: C728062BF: to=<postmaster@example.com>, relay=dovecot, delay=0.14, delays=0.04/0.01/0/0.09, dsn=2.0.0, $
Aug  9 10:11:42 localhost postfix/qmgr[3410]: C728062BF: removed
```

这表示邮件已经发送

也可以进入目录查看一下，使用 `mutt` 命令

```terminal
$ sudo yum install mutt
$ sudo mutt -f /var/mail/vhosts/example.com/postmaster
```

`mutt` 会提示新建邮箱，输入 `no` 即可，可以使用上下箭头进行邮件切换，使用 `q` 进行退出

## 配置防火墙

因为是邮件服务，需要外网访问，防火墙需要配置一下

邮件的几个默认端口说明如下

| Protocol | Default port | Description |
| --- | --- | --- |
| smtp | 25  | Mail (SMTP) |
| smtps | 465 | Mail (SMTP over SSL) |
| smtp-submission | 587 | Mail (SMTP-Submission) |
| imap | 143 | The Internet Message Access Protocol(IMAP) |
| imaps | 993 | IMAP over SSL |
| pop3 | 110 | The Post Office Protocol version 3 (POP3) |
| pop3s | 995 | POP-3 over SSL |

本例值配置了 `smtp` 和 `pop3` ，所以只要在防火墙开启这两个端口

```terminal
$ sudo firewall-cmd --add-service={smtp,pop3} --permanent
```

这样，在外网使用客户端配置既可以访问邮件服务

`注意`，外网访问邮箱的用户名是 `postmaster@example.com` 而不是 `postmaster`

## 问题调试

有时配置完了，但是发现不能访问，需要调试并解决问题，请参考 [Troubleshooting Problems with Postfix, Dovecot, and MySQL](https://www.linode.com/docs/email/postfix/troubleshooting-problems-with-postfix-dovecot-and-mysql/)

## 结束语

本例演示了使用 Postfix, Dovecot 和 MariaDB 进行邮箱服务配置。如果需要添加其他邮箱，请自己在数据库添加。

## 参考资料

[Email with Postfix, Dovecot and MariaDB on CentOS 7](https://www.linode.com/docs/email/postfix/email-with-postfix-dovecot-and-mariadb-on-centos-7/)  
[mysql\_secure\_installation Description](https://mariadb.com/kb/en/library/mysql_secure_installation/)  
[Troubleshooting Problems with Postfix, Dovecot, and MySQL](https://www.linode.com/docs/email/postfix/troubleshooting-problems-with-postfix-dovecot-and-mysql/)
