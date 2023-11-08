

# LDAP 协议相关

## [](#1-%E7%9B%AE%E5%BD%95%E6%9C%8D%E5%8A%A1%E7%AE%80%E4%BB%8B)1 目录服务简介

日常生活中使用的电话薄内记录着亲朋好友的姓名、电话与地址等数据，它就是 telephone directory(电话目录)；计算机中的文件系统(file system)内记录着文件的文件名、大小与日期等数据，它就是 file directory(文件目录)。

如果这些目录内的数据能够由系统加以整理，用户就能够容易且迅速地查找到所需的数据，而 directory service(目录服务)提供的服务，就是要达到此目的。

目录服务是一个特殊的非关系型数据库，用来保存描述性的、基于属性的详细信息，支持过滤功能。 这种数据库与我们常⻅的关系型数据库(Mysql、SQL Server、Oracle等)的区别在于目录服务以树状的层次结构来存储数据，就好像 Linux/Unix 系统中的文件目录一样。此外，目录服务是一个专⻔为搜索和浏览而优化的数据库，有着优异的读性能，但写性能差，并且没有事务处理、回滚等复杂功能，不适于存储修改频繁的数据。

综上所述，目录服务更适用于存储如组织架构之类的信息。

## [](#2-ldap-%E7%AE%80%E4%BB%8B)2 LDAP 简介

LDAP(Light Directory Access Portocol)是基于 X.500 标准的轻量级目录访问协议。LDAP 协议之前有一个 X.500 DAP 协议规范，该协议十分复杂，是一个重量级的协议，后来对 X.500 进行了简化，诞生了 LDAP 协议，与 X.500 相比变得较为轻量，其实 LDAP 协议依然复杂。

LDAP 约定了 Client 与 Server 之间的信息交互格式、使用的端口号、认证方式等内容。而 LDAP 协议的实现，有着众多版本，例如微软的 `Active Directory` 是 LDAP 在 Windows 上的实现，AD 实现了 LDAP 所需的树形数据库、具体如何解析请求数据并到数据库查询然后返回结果等功能。再例如 `OpenLDAP` 是可以运行在 Linux 上的 LDAP 协议的开源实现。而我们平常说的 LDAP Server，一般指的是安装并配置了 `Active Directory`、`OpenLDAP` 这些程序的服务器。

## [](#3-ldap-%E7%9A%84%E5%9F%BA%E6%9C%AC%E6%A8%A1%E5%9E%8B)3 LDAP 的基本模型

每一个系统、协议都会有属于自己的模型，LDAP 也不例外，在了解 LDAP 的基本模型之前我们需要先了解几个 LDAP 的目录树概念:

1.  目录树：在一个目录服务系统中，整个目录信息集可以表示为一个目录信息树，树中的每个节点是 一个条目。
    
2.  条目：每个条目就是一条记录，每个条目有自己的唯一可区别的名称(DN)。
    
3.  对象类：objectClass，与某个实体类型对应的一组属性，对象类是可以继承的，这样父类的必须属
    
    性也会被继承下来。
    
4.  属性：描述条目的某个方面的信息，一个属性由一个属性类型和一个或多个属性值组成，属性有必须属性和非必须属性。
    

LDAP 目录以树状的层次结构来存储数据，最顶层即根部称作「基准DN」，形如 `dc=geekby,dc=xyz` 或者 `ou=geekby.xyz`，前一种方式更为灵活也是 Windows AD 中使用的方式。在根目录的下面有很多的文件和目录，为了把这些大量的数据从逻辑上分开，LDAP 像其它的目录服务协议一样使用 OU(Organization Unit)，可以用来表示公司内部机构，如部⻔等，也可以用来表示设备、人员等。同时 OU 还可以有子 OU，用来表示更为细致的分类。LDAP 中每一条记录都有一个唯一的区别于其它记录的名字 DN(Distinguished Name)，其处在「叶子」位置的部分称作 RDN；如 `dn:cn=tom,ou=animals,dc=geekby,dc=xyz` 中 `tom` 即为 `RDN`；`RDN` 在一个 `OU` 中必须是唯一的。

因为 LDAP 数据是「树」状的，而且这棵树是可以无限延伸的，假设你要树上的一条记录，如何寻找它的位置呢？当然首先要说明是哪一棵树(dc)，然后是从树根到那个苹果所经过的所有「分叉」(ou)，最后就是这个苹果的名字(cn)。知道了树(dc=geekby,dc=xyz)，分叉 (ou=IT,ou=Worker,ou=Pentester)，苹果(cn=abc)，就可以找到我们想要的苹果了：

|     |     |     |
| --- | --- | --- |
| ```plain<br>1<br>``` | ```fallback<br>dn:cn=abc,ou=IT,ou=Worker,ou=Pentester,dc=geekby,dc=xyz<br>``` |

LDAP 的功能模型中定义了一系列利用 LDAP 协议的操作。它包含了三个部分:

1.  查询操作(Interrogation Operations)：容许查询目录和取得数据。它包含 Search Operating 和 Compare Operation。
2.  更新操作(Update Operations)：容许添加(ADD)、删除(Delete)、重命名(Rename)和改变目录(Modify)
3.  认证和管理操作(Authentication And Control Operations)容许客户端在目录中识别自己，并且能够控制一个 Session 的性质。

## [](#4-ldap-%E5%92%8C-ad-%E7%9A%84%E5%85%B3%E7%B3%BB)4 LDAP 和 AD 的关系

Active Directory 是微软基于 LDAP 协议的一套解决方案(LDAP 服务器 + 应用)， 而 LDAP 是与 AD 交互的协议之一。

Active Directory 解决了细粒度的权限控制「谁」以 「什么权限」访问「什么」。AD 在 LDAP v3 规范之上还有自定义扩展，例如，帐户锁定，密码到期等。

## [](#5-%E5%88%A9%E7%94%A8-ldap-%E6%94%B6%E9%9B%86%E5%9F%9F%E4%BF%A1%E6%81%AF)5 利用 LDAP 收集域信息

通常情况下，任何一名认证用户都可以通过 LDAP 来获取大量有趣的域信息。因此，在信息收集阶段，可以利用 LDAP 查询、整理域环境的相关信息。

### [](#51-%E7%9B%B8%E5%85%B3%E5%B7%A5%E5%85%B7)5.1 相关工具

-   adfind 可以在命令下获取域的详细信息，用法参考：[http://www.joeware.net/freetools/tools/adfind/usage.htm](http://www.joeware.net/freetools/tools/adfind/usage.htm)
-   ADExplorer 是独立的可执行软件，无需安装。 除了查询域信息外，ADExplorer 还可以拍摄快照，可以快照保存在本地，并可以使用 ADExplorer 打开进行操作。
-   ldapsearch
-   LDAPDomainDump 为 python 开发，可以通过 LDAP 收集和解析数据，并将其输出为人类可读的 HTML 格式以及机器可读的 JSON 和 CSV/TSV 格式。

|     |     |     |
| --- | --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>``` | ```fallback<br>domain_groups: 目标域的组列表<br>domain_users: 目标域的用户列表<br>domain_computers: 目标域的计算机账号列表<br>domain_policy: 域策略，例如是否需要密码等<br>domain_trusts: 传入和传出域属性以及是否受信任<br>``` |

### [](#52-%E8%8E%B7%E5%8F%96%E5%9F%9F%E4%BF%A1%E6%81%AF%E5%AE%9E%E4%BE%8B)5.2 获取域信息实例

环境：

|     |     |     |
| --- | --- | --- |
| ```plain<br>1<br>2<br>3<br>``` | ```fallback<br> 域控:192.168.66.26 (dc.company.com) <br> 域用户凭证：pentest\win7user:123456aB<br> 使用工具 Adfind.exe<br>``` |

下面列出了 Adfind 的一些使用实例，主要是对工具参数进行介绍。我们可以根据需求修改命令，查 询我们所关注的任何信息。比如查询已控凭证所属的组、查询特定组的成员、根据计算机名推测用户可 能有权限的计算机等。

|     |     |     |
| --- | --- | --- |
| ```plain<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>``` | ```fallback<br>#查询域内所有用户详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc u:*<br><br>#查询域内特定用户详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc u:test<br><br>#查询域内特定用户特定信息(mail)<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc u:test mail<br><br>#查询域内所有用户dn信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc u:* -dn<br><br>#查询域内用户数量<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc u:* -c<br><br>#查询域内所有组详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc g:*<br><br>#查询域内组名内包含“Admin”的所有组详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc g:*Admin* #查询域内所有OU详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc o:* #查询域内所有计算机详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc c:* #查询域内所有站点详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc site:* #查询域内所有子网详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc subnet:* #查询域的信任关系<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc trustdmp #查询域内spn的详细信息<br>adfind -h 10.1.26.128 -u company\test -up Geekby -sc spn:*<br><br>#搜索禁用的用户dn<br>adfind -h 10.1.26.128 -u company\test -up Geekby -b DC=company,DC=com -f userAccountControl:AND:=514 -dn<br>``` |
