

# JAVA代码审计-某mall - 先知社区

JAVA代码审计-某mall

- - -

# 环境搭建

启动mysql，然后创建数据库。

[![](assets/1701678475-75bd738952e80336e013bf8c2946c906.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171538-dc46be1c-8e97-1.png)

然后导入.sql文件。

[![](assets/1701678475-69b6f3110250bdaa544c8194ed0e3bfc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171545-e07ce042-8e97-1.png)

修改数据库名和用户名。

[![](assets/1701678475-474f2a3ebbbd96102e773799f81baa03.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171551-e45fd2f0-8e97-1.png)

# 代码审计：

## 1.sql注入漏洞

全局搜素 ${ ，查看那些地方调用了这些参数，主要是查看${} 拼接 SQL 语句的地方。

[![](assets/1701678475-cf38471186e39e827ad2f51868bbc9e4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171601-ea650472-8e97-1.png)

进入src/main/resources/mapper/NewBeeMallGoodsMapper.xml 第 70 行

[![](assets/1701678475-279620e8ade3fd550dee424d97314c7d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171609-ef049952-8e97-1.png)

首发分析 NewBeeMallGoodsMapper.xml，该部分中 goodsName 参数存在 SQL 注入，使用了直接拼接的方式向数据库进行查询。

[![](assets/1701678475-fed52b5f014b512462428d3587c53212.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171619-f50d8fa2-8e97-1.png)

进入src/main/java/ltd/newbee/mall/dao/NewBeeMallGoodsMapper.java 源码。

[![](assets/1701678475-d171db1c577f3b3cac350dec67c166ee.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171626-f8f62070-8e97-1.png)

逆向追踪findNewBeeMallGoodsList 方法  
[![](assets/1701678475-1e1a81c90c10572b2fb654714bf3ca69.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171633-fd38af54-8e97-1.png)

进入src/main/java/ltd/newbee/mall/service/impl/NewBeeMallGoodsServiceImpl.java ，在  
getNewBeeMallGoodsPage 方法中使用了 goodsMapper.findNewBeeMallGoodsList 方法

[![](assets/1701678475-0b776334f618f3b2ad6b478b6d7abeef.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171646-04c5b582-8e98-1.png)

追踪查看谁调用了getNewBeeMallGoodsPage 方法，  
定位到位于src/main/java/ltd/newbee/mall/controller/admin/NewBeeMallGoodsController.java 。

[![](assets/1701678475-88e2d4c8297d4cc05afdb38bd074a887.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171655-0a12519e-8e98-1.png)

点击 133 行中 params，可以看到该参数来自第 129 行，是一个 Map 对象，它需要从请求中获取参数。

[![](assets/1701678475-2a4ae3edd067b99c42d81e2cbd5a2d18.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171701-0dfc5e4e-8e98-1.png)

## 漏洞复现：

进入商品管理。使用添加商品。

[![](assets/1701678475-5fcc7c05ae9073920addb2dfe2ede220.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171709-12cfa052-8e98-1.png)

然后使用burp抓包。

[![](assets/1701678475-862c0e0298cc399c22e09500545b09c3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171719-18ad7152-8e98-1.png)

然后在god参数后面添加分号，出现报错注入。

[![](assets/1701678475-7e6d7f383672d4ede10693b0f6b249de.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171728-1dc8b0de-8e98-1.png)

也可以使用sqlmap来进行验证。

[![](assets/1701678475-f018b9fb54cffafd9a3ce3dfd3f704d5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171735-222d6f20-8e98-1.png)

## 2.后台权限绕过

进入src/main/java/ltd/newbee/mall/interceptor/AdminLoginInterceptor.java

[![](assets/1701678475-a6fc8fffd38465a458bff325c3872ecd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171758-2fae7dba-8e98-1.png)

首先，关键点是第 23 行，使用了 request.getRequestURI() 方法获取路径。 getRequestURI 方法返回的路径是未经过服务器端处理的原始路径，可能包含特殊字符或路径跳转，从而绕过服务器端的安全控制。接着，第 24 行使用了 uri.startsWith("/admin") 判断 Uri 路径中是否以 /admin 开头，以及获取并判断Session 中的 loginUser 属性是否为 null，两个条件 && 在一起结果为 True 的话进入条件代码。

[![](assets/1701678475-75a9d124e769c8da407255b15015512a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171805-33e76b62-8e98-1.png)

## 漏洞复现：

登陆后台寻找一个后台接口。  
[![](assets/1701678475-8f850af9bcbb7bf55af86d5e05f7c070.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171822-3deaa2aa-8e98-1.png)

删除 Cookie 后，也就是没有访问权限了。

[![](assets/1701678475-30d9e59f32c6b09ab361fee8fd807161.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171834-451a454e-8e98-1.png)

发送数据包，显示需要跳转到登录页面

[![](assets/1701678475-f3fcea57c8e5e7017976ff60ba792131.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171848-4dd5cd16-8e98-1.png)

## 3.SQL注入漏洞

${ 关键字进行全局搜索 ${  
定位到源码：src/main/java/ltd/newbee/mall/dao/NewBeeMallGoodsMapper.java

[![](assets/1701678475-8354e9e7bfa686680ba6366c3d3de655.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171856-5281982c-8e98-1.png)

[![](assets/1701678475-4dafa2fabf0d5fde72584fc5c2fae689.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171903-569f1e48-8e98-1.png)

继续向上追踪查看谁调用 searchNewBeeMallGoods 方法，最终跳转到  
GoodsController，位于src/main/java/ltd/newbee/mall/controller/mall/GoodsController.java

[![](assets/1701678475-c10bf622cb3388cfa8195f5879ea4e94.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171936-6a3ac6c8-8e98-1.png)

漏洞点在第 57 行，传入了 pageUtil 参数，而该参数同样通过 PageQueryUtil 类创建一个 pageUtil 对  
象，传入 params 作为参数，以及 params 同样是个 Map 对象。未对其进行过滤处理。

## 漏洞复现：

进入漏洞接口处，然后使用burp进行抓包，然后在参数处输入单引号。

[![](assets/1701678475-30c8e997eb6a0f45e024c15497e854f8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171948-71865a64-8e98-1.png)

发现存在报错注入。

[![](assets/1701678475-c6a2a06f6221c157126b37aa0cb61f47.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129171957-76fff4be-8e98-1.png)

可以使用sqlmap进行验证。

[![](assets/1701678475-c4781ff7e42c054fc00ddf66c67c30da.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172005-7bca92b0-8e98-1.png)

## 4.XSS漏洞

进入前端搜索框界面，然后输入xss的paylaod，进行黑盒测试。  
没有实现弹框，然后去xss当中去看看。

[![](assets/1701678475-174918119c18230e4f9c1199b499ba7a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172016-8268e31a-8e98-1.png)

去源码中看看，发现存在转义。

[![](assets/1701678475-8583467b0f533b6b5182379da02c737c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172022-85e9692e-8e98-1.png)

thymeleaf模版在对th:text标签进行渲染的时候，默认对特殊字符进行了转义，  
接着进入/src/main/resources/templates/mall/search.html:33

[![](assets/1701678475-8f1f910bb5327b8d4674e13f80c0cb81.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172029-8a11ec6a-8e98-1.png)

找thymeleaf未作转义的输出，th:utext不会将字符转义  
发现以下模版中存在th:utext，所以这两个功能点存在XSS。其中第二个，detail.html因为显示的是商品信息，商品信息使用富文本编辑器，不能简单的转义处理，需要考虑正常的html标签传输，所以作者在这里使用th:utext来显示商品详细。

### xss漏洞1

进入商品信息，添加xss的payload

[![](assets/1701678475-d7321582b668aa6d82f4a398e0fc431a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172038-8f64d65a-8e98-1.png)

成功实现弹框。

[![](assets/1701678475-609281eaf220df66b985e8c10f60d8f4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172045-9333e348-8e98-1.png)

### xss漏洞2：

进入订单管理，然后添加payload

[![](assets/1701678475-18c4977e7bea503a4180ee149bd89dc9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172052-97541646-8e98-1.png)

成功实现弹框。

[![](assets/1701678475-29208db3f2f667614f8405de8d0194e0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172057-9ab27418-8e98-1.png)

### xss漏洞3：

进入新品上线配置模块  
添加xss的payload

[![](assets/1701678475-08d5bf86ab7ee8c53656037806875c5b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172104-9f0901c6-8e98-1.png)

成功实现弹框。

[![](assets/1701678475-ed2c176f0a088d7c7b2d1b6e92293e54.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172111-a318c03a-8e98-1.png)

## 5.垂直越权

进入/src/main/java/ltd/newbee/mall/config/NeeBeeMallWebMvcConfigurer.java中，发现针对url路径设置了不同的interceptor。addPathPatterns表示其中的路径会经过设置的拦截器，excludePathPatterns则不过该拦截器。其中两个星\**表示匹配任意字符。如果出现一个*则表示匹配单个路径

[![](assets/1701678475-07279f8394bed455d3717a64d1ec38db.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172133-b012b26e-8e98-1.png)

对请求的路由进行判断是应该使用 getServletPath() 来获取最后真正分发到路由地方的 path  
getRequestURI() 只是获取了请求的 URI。

[![](assets/1701678475-7e51d3b14c38cab30fcadc28386743d7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172145-b704e632-8e98-1.png)

使用了 getRequestURI() 来获取URI来判断URI是否以 /admin 开头，如果是 /admin 开头则校验 session，不是则不用校验。

[![](assets/1701678475-fcf74105de68c3ea59a8b8887b402670.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172159-bfc2c140-8e98-1.png)

## 漏洞复现

进入dashboard模块

[![](assets/1701678475-fea6d06f3ed2521a122a3caa154e41c2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172207-c4640e20-8e98-1.png)

然后输入//admin 或 /index/..;/admin也可以成功访问到页面。

[![](assets/1701678475-ecdffcee3a62f15ef93314f2e9d83986.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172215-c96196ae-8e98-1.png)

成功绕过了目录访问字符限制。

[![](assets/1701678475-d601d0257bc5970c424ce36594a7548f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172223-ce19e3c2-8e98-1.png)

## 6.水平越权漏洞1：

定位到源码：ltd/newbee/mall/controller/mall/PersonalController.java:114

[![](assets/1701678475-ba20e34b26fbddb51e56928930c3792c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172238-d68fe5ce-8e98-1.png)

接着看 updateUserInfo() 的实现，

[![](assets/1701678475-10c23c9c8150cfa3b7bedd6e31287e1d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172245-db366a9e-8e98-1.png)

发现这里从数据库查找用户并未用到 session ，而是直接以传递过来的 userId 为参数来查找并修改数据的，所以这里存在水平越权漏洞，修改 userId 便可修改其他用户的信息。

## 漏洞复现1：

注册一个用户，然后查看个人信息。

[![](assets/1701678475-f98417e6c02cd2b02d1b6f0678cfa4a0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172304-e661eb14-8e98-1.png)

使用burp抓包，用户 userId 为 9

[![](assets/1701678475-a7be9b3a7c8bfbf42e1fb601aaa15e36.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172313-eb766e72-8e98-1.png)

然后修改userid，成功修改其它用户信息。

[![](assets/1701678475-1884b37cdb74e66512f55a23116f7d38.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172319-ef0a8104-8e98-1.png)

[![](assets/1701678475-b5ccc293c420d8882474ed9a087523b2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172327-f439dcf6-8e98-1.png)

## 水平越权漏洞2

进入查询订单的源码：td/newbee/mall/controller/mall/OrderController.java:36  
[![](assets/1701678475-2dd15a8aa3ef59663111747c9968232c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172335-f8c43492-8e98-1.png)  
跟进getOrderDetailByOrderNo() 函数

[![](assets/1701678475-ac46ffbf20dfa9e3d77621136b087e7e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172348-004c5f6e-8e99-1.png)

## 漏洞复现：

这里用户 userId 为9的用户下的单

[![](assets/1701678475-5c503a7cecd9fa6d5e457fe1893dcf1a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172401-080998b6-8e99-1.png)

替换为其它用户cookie，也可以看到订单信息。

[![](assets/1701678475-10153253f4c9988e591b7c4481f8a250.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172407-0bfbfd6a-8e99-1.png)

## 7.Csrf漏洞

我们使用添加购物车功能为例，请求内容为下，没有任何token值来进行校验。

[![](assets/1701678475-e470c207e193b32da5241f13010812e8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172417-1194f04c-8e99-1.png)

由于是json格式的请求，不能直接使用burp Generate CSRF PoC，因为burp生成的PoC无法伪造Content-Type。burp生成的CSRF PoC请求内容如下，可以看到Content-Type: text/plain，并且post数据多出一个等号。

[![](assets/1701678475-88a620d088994473778971768e03550c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172425-168934a0-8e99-1.png)

## 漏洞复现：

未授权访问商品 [http://localhost:8089/index/..;/admin/goods/edit/10896](http://localhost:8089/index/..;/admin/goods/edit/10896)

[![](assets/1701678475-f8aebd0c28b191ae79ccef4ee43fcda4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172433-1b1c57a4-8e99-1.png)

然后生成csrf的poc。进行抓包。

[![](assets/1701678475-f070d9f05ecb685e6991fae729114404.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172440-1fc4e5e6-8e99-1.png)

然后成功写入xss的payload。

[![](assets/1701678475-352dbf9de10a600c6f849d10600ba3dc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172447-23f90246-8e99-1.png)

成功添加商品到购物车当中。

[![](assets/1701678475-6c9b50a8bbab7f851debfec068bd4eda.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172454-27fa124a-8e99-1.png)

## 8.逻辑漏洞

下订单但未支付时，访问/orders/{orderNo}/finish可直接完成交易。

[![](assets/1701678475-7378617208a6aa7691fdb9f93515e8c2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172503-2d54cb9a-8e99-1.png)

从代码中发现直接调用newBeeMallOrderService.finishOrder(orderNo, user.getUserId())，对于该订单是否支付，是否出库等过程都没有校验。

[![](assets/1701678475-7c3faa61ca698cc59c3c9938f5724621.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172510-319e048c-8e99-1.png)

因为代码使用的是@PutMapping，使用PUT方法访问，其他请求方法不会被执行。

[![](assets/1701678475-caf9f2c7846cda13f42d365e3a896442.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172516-351b11b8-8e99-1.png)

[![](assets/1701678475-d2520d544a52d367eef376289e3b968d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172523-38e874e8-8e99-1.png)

## 漏洞复现：

添加一件物品到购物车，然后提交订单。

[![](assets/1701678475-8f2f77fb4394091851ab4d208f727e03.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172531-3db92dc8-8e99-1.png)

然后点击去支付，选择支付宝支付，一系列流程下来可以购买商品。

[![](assets/1701678475-5c23ace47c1f2e34afb1591b40afb6fb.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172540-432eeec8-8e99-1.png)

我们进入商品后台，订单一开始是未支付。

[![](assets/1701678475-bfbc42909f05b62fbf62fe4a2ce59068.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172547-4737898a-8e99-1.png)

我们使用put方式去请求。

[![](assets/1701678475-d27d7bb8b1b3eefd4411629ac75ac576.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172556-4c952e1e-8e99-1.png)

成功支付商品。

[![](assets/1701678475-58302735568c11fac08e2c41f33876b3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129172604-5170ea9a-8e99-1.png)

REF：  
[https://cloud.tencent.com/developer/article/2169674](https://cloud.tencent.com/developer/article/2169674)  
[https://s31k31.github.io/2020/04/25/JavaSpringBootCodeAudit-1-Preparation/](https://s31k31.github.io/2020/04/25/JavaSpringBootCodeAudit-1-Preparation/)
