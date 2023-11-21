

# 奇安信攻防社区-【Web实战】浅谈reactor netty httpclient请求解析过程

### 【Web实战】浅谈reactor netty httpclient请求解析过程

Reactor Netty HttpClient 是 Reactor Netty 框架提供的一个用于进行异步 HTTP 请求的客户端库。它基于 Reactor 框架，采用响应式编程模型，允许以非阻塞的方式执行 HTTP 请求和处理响应。浅谈其HTTP请求解析过程。

# 0x00 前言

Reactor Netty HttpClient 是 Reactor Netty 框架提供的一个用于进行异步 HTTP 请求的客户端库。它基于 Reactor 框架，采用响应式编程模型，允许以非阻塞的方式执行 HTTP 请求和处理响应。

![image.png](assets/1700544949-750d11d30cc9ad6605b46b64974390c2.png)

通过引入对应的依赖，即可通过使用Reactor Netty从HttpClient获取目标的响应报文：

![image.png](assets/1700544949-188c53c4ef34aaa373b808e414090d52.png)

下面是一个具体的例子,首先创建了一个 HttpClient 对象，通过Reactor Netty 的链式调用 API 来构建我们的请求，发起了一个 GET 请求访问了target并打印对应响应的内容，完成了整个请求与响应处理过程：

```Java
HttpClient httpClient = HttpClient.create().wiretap(true);
httpClient.get().uri(target).responseContent().aggregate().asString().doOnSuccess(s -> {
    System.out.println("s1=" + s);
}).block();
```

上述代码串联了多个Reactor Netty的方法，下面是简单的说明：

-   `httpClient.get().uri(target)`：通过httpClient创建了一个HTTP GET请求，并指定了请访问的目标URL。
-   `.responseContent()`:调用.responseContent()方法，会获取到一个表示HTTP响应内容（响应体）的Flux\\<ByteBuf>，其中Flux是Reactor中的一种反应式数据类型，表示异步流。异步处理响应体的数据信息。
-   `.aggregate()`:因为HTTP响应的内容通常会被分成多个字节块，该方法用于将它们进行整合。
-   `.asString()`:调用该方法将`ByteBuf`内容解码为字符串方便后续的处理。
-   `doOnSuccess(s -> {` `System.out.println("s1=" + s);})`:使用.doOnSuccess()方法注册一个回调函数，当HTTP响应成功完成时，执行这个函数将HTTP响应的内容打印到控制台中。
-   `.block()`:阻塞当前线程以等待HTTP响应的完成。.block()方法会触发实际的HTTP请求发送和响应处理，然后等待直到HTTP请求完成，并且只有在响应成功时才会解除阻塞。

当然除了block以外，还可以通过类似subscribe获取响应报文。

# 0x01 "畸形scheme"HTTP请求

以GET请求为例，下面对reactor netty httpclient请求解析过程进行简单的分析：

在 Reactor Netty 框架中，MonoHttpConnect是一个用于表示 HTTP 连接的 Mono 类型。它代表了一个异步的 HTTP 请求，并返回一个 Mono 类型的结果。通过调用 subscribe 方法，可以触发实际的 HTTP 请求，并通过订阅者来处理响应结果：

![image.png](assets/1700544949-4f85509f354ff7aef8a91ae4d95ed27a.png)

首先这里会实例化HttpClientConnect，这里会调用`uriEndpointFactory.createUriEndpoint`创建 UriEndpoint，UriEndpoint是一个用于表示网络请求的目标地址的类。它封装了 URI 的相关信息，包括协议、主机名、端口号、路径等。reactor.netty.http.client.UriEndpointFactory#createUriEndpoint方法根据传入的参数，创建一个 UriEndpoint 对象，并返回该对象：

![image.png](assets/1700544949-efafaca0c7dfe76d74bb532d4e81e410.png)

可以看到，在createUriEndpoint方法中，主要是通过正则匹配的方式获取URI 的相关信息：

![image.png](assets/1700544949-e321a5c201899aa292c98eca80d8ff28.png)

创建完HttpClientHandler后，会通过配置对象（\_config）来设置一些参数：

![image.png](assets/1700544949-9d0d75938aa18575d79e63ba426e0a81.png)

这里会调用resolverInternal方法用于获取地址解析器组。它负责将主机名解析为一个或多个 IP 地址，以便 HttpClient 可以与目标服务器建立连接：

![image.png](assets/1700544949-f592df180f8e75bece57259daec0fbcc.png)

实际调用的是其父类ClientTransportConfig的方法：

![image.png](assets/1700544949-e2653bf16aab3e337b59d05d2c7fc069.png)

这里会create一系列的组件：

![image.png](assets/1700544949-33f9f57e6477bc4cb2289a3cc7747132.png)

例如创建ConnectionProvider用来管理连接池，Builer这里硬编码传入对应的name为http，后续会创建一组连接并存储在连接池中。 当需要进行网络通信时，可以从连接池中获取一个连接并使用它来发送请求：

![image.png](assets/1700544949-945396e91a7f3f628b6735b5daeaa373.png)

又例如PooledConnectionProvider，这个在后面会用到：

![image.png](assets/1700544949-657dc843dc8d74ffd67f0846a3c6177a.png)

调用完后，此时会调用`_config.httpConnectionProvider().acquire`从 HTTP 连接提供者中获取一个可用的连接。以便进行 HTTP 请求：

![image.png](assets/1700544949-d07c854c246baa2268cf5b331fa1a451.png)

查看具体的过程，这里最终会调用PooledConnectionProvider的acquire方法：

![image.png](assets/1700544949-b6e804513c181d54802ef460174a5e6c.png)

![image.png](assets/1700544949-276fd73e2c77334a5b723d5aaf7440ef.png)

reactor.netty.resources.PooledConnectionProvider的作用是提供连接池管理功能。在使用 Reactor Netty 进行网络通信时，可以通过 PooledConnectionProvider 来管理和复用连接，以提高性能和资源利用率，这里会调用 acquire 方法获取一个可用的连接，以便进行网络通信。获取到的连接可以用于发送请求、接收响应等操作，如果连接池中没有可用的连接，它可能会创建一个新的连接：

![image.png](assets/1700544949-c5dd8bc219ec5f9db6318c2be5aa8451.png)

从对应的调试信息可以知道，这里创建的是http client pool，结合前面解析请求target的过程，这里name的值并不是从请求target的schema获取的，是从前面Builer里硬编码获取的：

![image.png](assets/1700544949-280993d8d186e5730adc7eac131bcfc8.png)

后面是HttpClientOperations的处理，也没有对schema进行相应检查操作，那么这里有没有可能reactor netty httpclient可以以任意符合正则匹配的schema进行请求呢？

![image.png](assets/1700544949-c4b05cc67e9ff5de9d6e9465d65c6e69.png)

验证下前面的猜想：

![image.png](assets/1700544949-eb1b36d52cb5f687fe6bb612b0bdadc9.png)

正常情况下，通过reactor netty httpclient请求`http://127.0.0.1:8080/health`正常返回：

![image.png](assets/1700544949-a8e74b1c7e898d7bf470458ec46a74f8.png)

将scheme替换成任意字符，可以发现依旧能正常请求并返回：

![image.png](assets/1700544949-3091a528295c76bb83b501e020f6f4e4.png)

查看reactor netty httpclient的日志，确实没有考虑用户输入的协议，在PooledConnectionProvider创建了新的http client pool，同时也没有发现关于schema的检查：

![image.png](assets/1700544949-5123538a2a6f1248bfcdf4c9d993065d.png)

![image.png](assets/1700544949-2ac817c6fb7fee171cc7f5e6490c8427.png)

结合前面请求target解析的正则：

![image.png](assets/1700544949-6fd07196bd3665d9dfea76e3f2d05313.png)

![image.png](assets/1700544949-29c28610ab0faa5a2cad29a1693a70ba.png)

scheme还支持下划线匹配，所以类似`anyt____hing`的schema同样能正常请求：

![image.png](assets/1700544949-7977ffd3cea2ad8ba4335af1d8ac5ccb.png)

# 0x02 其他

WebClient是从Spring WebFlux 5.0版本开始提供的一个非阻塞的基于响应式编程的进行Http请求的客户端工具。 它的响应式编程的基于Reactor的。 WebClient中提供了标准Http请求方式对应的get、post、put、delete等方法，可以用来发起相应的请求。

通过引入如下依赖即可使用WebClient:

![image.png](assets/1700544949-685843b99fe7909f38f6b8f86d7bffb3.png)

从依赖关系可以看到，实际上spring-boot-starter-webflux也是基于reactor-netty-http来发起相应的请求的：

![image.png](assets/1700544949-81c28c9ce15f187fa0ff379d4d7ad24d.png)

下面的代码是一个简单的WebClient请求示例。可以通过`WebClient.create()`创建一个WebClient的实例，然后选择调用方式get，在`uri()`指定需要请求的路径，然后调用`retrieve()`发起请求并获得响应，`bodyToMono(String.class)`用来指定请求结果需要处理为String:

```Java
WebClient webClient = WebClient.builder().build();
String response = webClient.get().uri(url).retrieve().bodyToMono(String.class).block();
return response;
```

简单看下WebClient的处理过程，首先会在org.springframework.web.util.UriComponentsBuilder#fromUriString方法处理需要请求的目标：

![image.png](assets/1700544949-50c1bb52661ac8006e4658c0bab72ab9.png)

可以看到这里也是通过正则的方式进行匹配：

![image.png](assets/1700544949-afeeb5426bceae958eb3f37fbd4e35dd.png)

若未匹配相关信息，会抛出`throw new IllegalArgumentException("[" + uri + "] is not a valid URI");`异常，否则进行进一步的封装，同时这里对scheme和host进行了一定的合法性检查：

![image.png](assets/1700544949-62eea9a912b6974b3eefa0f5d5cc99cf.png)

但是并没有强制校验scheme是否是http/https，所以同样的当尝试请求`anything://127.0.0.1:8080/health`，WebClient同样也是能正常解析并正常返回：

![image.png](assets/1700544949-9b9d03f98fe79b2445aecc9623a37d91.png)

可以看到结合reactor netty httpclient解析过程中的一些处理方式，可以构造类似上述任意协议的“畸形”的请求样式，在某种情况下可以绕过现有ssrf的一些安全防护措施。开发人员应该避免将不受信任且未经验证的数据从 HTTP 请求传递给reactor netty httpclient，避免不必要的绕过导致ssrf风险。
