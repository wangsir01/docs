

# 奇安信攻防社区-【Web实战】一次空白页面的“妙手回春”嘎嘎出严重漏洞

### 【Web实战】一次空白页面的“妙手回春”嘎嘎出严重漏洞

某次企业SRC的一次实战。其中通过信息收集发现了一个站点，这里为内部系统，访问的时候居然直接一片空白，是空白页面。难道空白页面就没有漏洞吗？我就偏偏不信这个邪，上手就是干！

# 前言

某次企业SRC的一次实战。其中通过信息收集发现了一个站点，这里为内部系统，访问的时候居然直接一片空白，是空白页面。难道空白页面就没有漏洞吗？我就偏偏不信这个邪，上手就是干！

# 过程

[https://x,x.com/](https://x,x.com/)  
打开页面啥也没有，一片空白:  
![image.png](assets/1699416673-1b80bcb7953fb2e633f048d8c9e5ee7e.png)

其中这里按下键盘中的F12，通过审计js后，发现接口：

![image.png](assets/1699416673-08494cac782f21013ad6b7befaf48267.png)

其中的一个接口/api/plugin/directory/getLastUsedDirId拼接后，如下提示：

![image.png](assets/1699416673-cdcf751b584efe8727125fca7e9b8e21.png)

其中响应包中响应的“插件分类不能为空”让我百思不得其解，不知道是缺了什么参数。那么这里就再回到js中看看吧，果然，给我发现了端倪：  
这里再查看js，发现其中给出提示，原来是header要加如下字段：

![image.png](assets/1699416673-8300e70d13d71511ca9584ba0b6c204b.png)

那么我加了其中一个字段category，发现成功，但是却又报了非法用户登录。那么这里就必须需要Authorization认证字段了：

![image.png](assets/1699416673-a6f5ee07db2ba58465ccef9bec0495aa.png)

因此这里就又碰到了一个棘手的问题，Authorization认证字段这个一般都是成功登录系统后才会赋予给用户的一个值，而这个地方连页面都是空白的，那么这里到底去哪里寻找Authorization认证字段的值呢？

这里贯彻着遇事不决看js的思想，继续来审计js，终于发现了解决方法：  
其中在js中发现了login接口。这里存在该逻辑漏洞：id:t.id||"1234",name:t.name||"1234",organizationCode:t.organizationCode||-1。这里用了||或，那么言下之意就是如果不知道id、name和organizationCode的话，就可以直接id参数和name参数都填1234，organizationCode填-1

![image.png](assets/1699416673-a3f1a9190906137727a9590cbd98da38.png)

login接口，这里真成功了，其中获取到data

![image.png](assets/1699416673-d336b87f66b6c01345514008425939d2.png)

那么这里猜测data的值即为那个Authorization认证字段的值，这里填入：

发现成功调用接口：

![image.png](assets/1699416673-a5003935e67ff48cc16647b25f711e20.png)

那么这里其中的接口就都可以成功调用了：

像这里的获取内部数据等等

![image.png](assets/1699416673-15a5a831b5b5c09ae4eb1ea366a4566c.png)

这里最关键的一个接口来了：  
这里通过js审计到查看oss配置信息的接口：  
![image.png](assets/1699416673-e020812fbfb6a3c66bf7420c5efc9fbe.png)

![image.png](assets/1699416673-1fd02a5d4b7a1777d6b97d297ab7ecbd.png)

这里因为是阿里云的，所以这里直接使用oss browser来进行利用，利用成功：

![image.png](assets/1699416673-187743d99b5ae4fda6c1e3d26357eeec.png)

![image.png](assets/1699416673-8d848ad56ab7932140c8975bc8dd3a3e.png)

这些直接可以下载到后端的源码：

其中反编译出来直接为后端源码，泄露许多严重敏感信息

![image.png](assets/1699416673-7bdf6dc25c1cabac821047bbb70badb2.png)

后端的配置信息：

其中还有数据库密码等等敏感信息

![image.png](assets/1699416673-002e5584cf4b1883fec2f26eaeac8769.png)

反编译出来的后端源码：  
![image.png](assets/1699416673-211c71cae866eed45437d26f376379f4.png)

最后的最后，当然也是给了严重的漏洞等级，舒服了！
