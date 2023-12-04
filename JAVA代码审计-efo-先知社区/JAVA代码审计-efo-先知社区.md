

# JAVA代码审计-efo - 先知社区

JAVA代码审计-efo

- - -

# 环境搭建：

首先去修改源码中的配置文件，修改为你本地的用户名和密码。

[![](assets/1701678538-fc6fbf5f57e91bfd306c1979e32091fd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144703-1ab7f9f0-8e83-1.png)

然后启动环境之后，就进入了登录界面。

[![](assets/1701678538-8fb1a0f7d5b688858af3d5755c426ec2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144713-209e8866-8e83-1.png)

# 代码审计：

## 1.SQL注入漏洞

全局搜索关键字，然后去找到DAO⽂件，发现存在search用法。

[![](assets/1701678538-ec4e1b4662fe655ff93cfb3248c52f7f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144726-28936bae-8e83-1.png)

跟进它。

[![](assets/1701678538-642db5cca3f32ac90ee2cb447be6a994.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144735-2d88eaf8-8e83-1.png)

然后再跟进listUserUploaded⽅法

[![](assets/1701678538-f999d88d8d2a4aeebd8b2a8233cbea6b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144742-32069e18-8e83-1.png)

但fileDAO接⼝只有三个参数，主要查询代码，映射FileSqlProvider这个类的getUserUploaded⽅法。

[![](assets/1701678538-e48fffeb78af6581decfe80e2649115d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144755-39df909a-8e83-1.png)

接着调⽤了getSqlEnds⽅法

[![](assets/1701678538-3425f76409a74a4433f1f4862f68b585.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144808-4156eb0c-8e83-1.png)

最后调⽤getSearch⽅法，然后结束流程。

[![](assets/1701678538-2a5b1a764aec24a05ff41cb15b13f4dc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144817-46987248-8e83-1.png)

## 漏洞复现：

进入我的资源功能处，然后点击获取更多。

[![](assets/1701678538-05aab8f8f2dc5b1e186d21faed4d4401.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144839-5415914e-8e83-1.png)

然后输入单引号，出现报错注入，证明此处确实存在SQL注入漏洞。

[![](assets/1701678538-7ced05a164a63ef29908cbe4ce02db04.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144847-586f791c-8e83-1.png)

输入"进行验证。

[![](assets/1701678538-7c2a0c7fdfc20407625ae74ac5170a87.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144855-5d3a39aa-8e83-1.png)

成功看到报错注入。

[![](assets/1701678538-ddef9e22b7f566e719b925601c5367f8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144902-61678c12-8e83-1.png)

使用sqlmap进行验证。

[![](assets/1701678538-52345c8096e772ac2e55457412714097.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144908-6540c84e-8e83-1.png)

## 2.sql注入漏洞2

全局搜索关键字，然后定位到更新用户权限功能处。

[![](assets/1701678538-eab93c9b94ea5ccf270ffa66486829b3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144949-7dd2bb56-8e83-1.png)

然后跟进upadtePermission这个函数。

[![](assets/1701678538-7ef70c966f979e8dcc7019eba94c2fb7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129144957-8279f84a-8e83-1.png)

然后进入UserDAO层。

[![](assets/1701678538-42520cba545441e499bbf764deeb9c27.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145004-86c24650-8e83-1.png)

发现其未对用户的输入进行过滤，直接进行SQL查询。

[![](assets/1701678538-6e6a21ec3d8978eda9d06d9ff972765d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145048-a0be909a-8e83-1.png)

## 漏洞复现：

进入系统设置功能处，然后点击获取更多。

[![](assets/1701678538-052e443aec31b5e2ac78840f2ada47bf.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145057-a655f872-8e83-1.png)

发现该处存在时间盲注

[![](assets/1701678538-e64f976f3c30f37ee67e96cf8860807e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145104-aa8e39ae-8e83-1.png)

也存在报错注入。

[![](assets/1701678538-efa2a771b2dfdb8dc41272d6ef120cda.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145113-afab10e2-8e83-1.png)

## 3.sql注入漏洞3

全局搜索关键字，接着进入AuthDAO层，

[![](assets/1701678538-dfd9e50bb16b69c972eb0d9b4efa29f2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145119-b374daa0-8e83-1.png)

跟进它。

[![](assets/1701678538-5b8439a27f992656122d4dfa82024458.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145126-b7555564-8e83-1.png)

然后继续往下走。

[![](assets/1701678538-4b26dca386ec43ec5b6ee113842e6534.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145133-bb79e84e-8e83-1.png)

发现未对用户输入进行处理，导致其存在SQL注入漏洞。

[![](assets/1701678538-966cf2aa67ce8cef4a5bf0c2bc3f0647.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145142-c0fbd174-8e83-1.png)

## 漏洞复现：

进入权限管理功能处，然后点击新增，然后使用burp抓包。

[![](assets/1701678538-2fa4185e695b80465b7ffaa71470f5f9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145148-c44ed8c6-8e83-1.png)

然后进行报错注入尝试，发现其存在报错注入。

[![](assets/1701678538-a5c9baaed227cc7356e4e78915122c9e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145154-c84ff6a8-8e83-1.png)

也可以使用SQLMAP进行验证的。

[![](assets/1701678538-42a5cee6314f15b0791488aa0b15655f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145202-cceaac1c-8e83-1.png)

## 4.sql注入漏洞4：

进入/file/all，在列出所有文件的地方传入参数 order by，并且没有做过滤，导致产生SQL注入漏洞，接口信息如下

[![](assets/1701678538-4bfb5b6beed70028016b8ceb24647d49.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145216-d54379b6-8e83-1.png)

发现orderBy 参数都是字符串，无过滤且是通过字符串拼接方式进行的传参

[![](assets/1701678538-d921c3404a8e58cb71a4b1ccd469f41c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145223-d9606bda-8e83-1.png)

## 漏洞复现：

访问url地址。

[![](assets/1701678538-72923bbeda9a4e785581165d638bef7b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145234-e030b74e-8e83-1.png)

发现其存在报错注入。

[![](assets/1701678538-4b23b7446cfe595bb1e76e3a39cd140e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145241-e452af58-8e83-1.png)

使用SQLMAP进行验证。

[![](assets/1701678538-7fe1dcc6ca2ca3d718607ec7cdf9bb4f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145250-e977bf50-8e83-1.png)

## 5、敏感信息泄露泄露

发现多个类中的 jsonObject 对象(一个用来按照json格式保存结果的变量)是共用的，导致认证后的 token 会在访问返回该对象的 未认证接口时泄露，就会成功进行返回。

[![](assets/1701678538-354f5b92ff8811f510c9d61366cc8bbe.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145259-ef205f34-8e83-1.png)

## 漏洞复现：

成功获取随机生成的cookie。

[![](assets/1701678538-012302f5a6f1c35df12e9d023539455c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145309-f4f5e1e0-8e83-1.png)

## 6.未认证任意密码重置

进入重置密码验证码的接口 /common/{email}/code  
然后测试功能需要先修改下配置中的邮箱数据， 邮箱的 smtp 服务器是 smtp.qq.com  
这里向对应邮箱发送了一个验证码，并将其设置发送到对应的session中

[![](assets/1701678538-6b8f9d2e6a8686dbcaf3b745c44333c6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145317-f9ac5930-8e83-1.png)

## 漏洞复现

进入重置密码处。  
然后获取cookie  
[![](assets/1701678538-1f42431b3f6f2c51e090bb3fdd33e49b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145327-ffa91a58-8e83-1.png)

然后利用返回的jessionid配合之前的SQL注入漏洞来修改密码。

[![](assets/1701678538-4917b4b49814d15a49f22df4a1aa45db.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231129145336-04fe5ed2-8e84-1.png)
