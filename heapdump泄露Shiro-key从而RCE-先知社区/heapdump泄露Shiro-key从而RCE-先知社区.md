

# heapdump泄露Shiro key从而RCE - 先知社区

heapdump泄露Shiro key从而RCE

- - -

## 1\. 简介

我搭建了一个Spring heapdump泄露shiro key从而RCE的漏洞环境，Github地址：[https://github.com/P4r4d1se/heapdump\_shiro\_vuln](https://github.com/P4r4d1se/heapdump_shiro_vuln)  
漏洞利用条件：

-   Spring Shiro环境
-   存在heapdump文件泄露
-   存在可利用链

## 2\. 漏洞原理

Shiro相关的漏洞原理和调试分析已经有很多大佬分享过了，这里不再赘述，这里主要针对这个漏洞环境进行说明：  
（1）Spring其实是有自己默认安全框架的，叫Spring Security，但可能有的开发用Shiro用习惯了，将Spring Securiy替换成了Shiro，这种情况并不少见，比如若依就是Spring shiro。  
[![](assets/1701826073-eb207cb42631f379602ae5bbca07a1da.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172619-0c0ab6ce-7091-1.png)  
（2）在有key的情况下，即使是最新版的Shiro也一样存在漏洞，而且在很多时候都会因为开发、部署等问题导致shiro key的泄露。  
（3）Shiro大于1.2.4的版本中，在没有开发人员人工干预的情况下key改为了随机生成，这个随机生成是在每次启动Web环境的时候，重启前这个key不会改变，可以在JVM虚拟机内存里找到。  
[![](assets/1701826073-e28c945f53c09f6b04f56e7942ecad71.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172627-10e0b590-7091-1.png)  
（4）Spring的heapdump文件就是从JVM虚拟机内存导出的。  
综上所述导致了这个组合漏洞的产生。

## 3\. 漏洞演示

加载漏洞环境后，可以看到Shiro版本为1.8.0：  
[![](assets/1701826073-3f2defdeb3952be8a6ca3bd8a5cae2a7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172657-23125b56-7091-1.png)  
访问8080端口的/actuator/heapdump获取heapdump文件：  
[![](assets/1701826073-43eaaeb437226224af35e4f6a0103dec.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172704-26bfa8da-7091-1.png)  
获取其中的shiro key，我常用的有两种方式：  
（1）JDumpSpider：[https://github.com/whwlsfb/JDumpSpider](https://github.com/whwlsfb/JDumpSpider)  
这个小工具可以自动爬取heapdump中的变量信息，比较方便，坏处是可能会漏掉没在爬取列表中的信息。  
直接运行:java -jar JDumpSpider.jar heapdump即可自动获取变量信息，这里获取到ShiroKey：  
[![](assets/1701826073-fbe7547b57b48171820a01ce8e52acdf.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172718-2f9afe50-7091-1.png)  
（2）jvisualvm.exe：Java自带的工具，默认路径为：JDK目录/bin/jvisualvm.exe  
这个工具需要手动去找想要的信息，在过滤里输入org.apache.shiro.web.mgt.CookieRememberMeManager，圈出来的16个字节的值就是key：  
[![](assets/1701826073-75c4aa05a720944a919eca9d7c00d815.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172731-36d0914e-7091-1.png)  
用一个Python小脚本转成base64编码后的Shiro key：

```plain
import base64
import struct

print(base64.b64encode(struct.pack('<bbbbbbbbbbbbbbbb', 109,-96,12,-115,33,59,24,112,44,124,56,110,-15,59,1,-41)))
```

[![](assets/1701826073-4f01b147abf8d1677d5c32b367518d55.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172827-58bc8dc6-7091-1.png)  
使用获得的key进行利用成功：  
[![](assets/1701826073-f8edf26dffc80936ad1f2d004504c66c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172910-723fddf2-7091-1.png)  
重新启动服务器再次获取shiro key，可以看到key改变了，验证了漏洞原理的第3点，每次启动生成一个随机key：  
[![](assets/1701826073-5185c9baf2d79d69120e5e73422148b7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172921-7897c976-7091-1.png)  
改用新的key仍然可进行利用：  
[![](assets/1701826073-78296e74eb2ecdeb80fd94289800d495.png)](https://xzfile.aliyuncs.com/media/upload/picture/20221130172927-7c76e054-7091-1.png)
