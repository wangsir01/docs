

# 改造gadgetinspector篇-自动化挖掘Fastjson gadget chain - 先知社区

改造gadgetinspector篇-自动化挖掘Fastjson gadget chain

- - -

### 0x01 前言

#### 《java反序列化利用链自动挖掘工具gadgetinspector源码浅析》

github：[改造过的gadgetinspector](https://github.com/threedr3am/gadgetinspector "改造过的gadgetinspector")  
我的上一篇文章，详细地讲述了gadgetinspector挖掘java反序列化利用链的原理，在明白了gadgetinspector的原理细节后，我们其实会发现它还存在着一部分的缺点：

1.  对于运行时确定的实现，也就是多态性，没办法做到污点分析：

gadgetinspector.PassthroughDiscovery.PassthroughDataflowMethodVisitor#visitMethodInsn

```plain
Set<Integer> passthrough = passthroughDataflow.get(new MethodReference.Handle(new ClassReference.Handle(owner), name, desc));
if (passthrough != null) {
    for (Integer passthroughDataflowArg : passthrough) {
        //判断是否和同一方法体内的其它方法返回值关联，有关联则添加到栈底，等待执行return时保存
        resultTaint.addAll(argTaint.get(passthroughDataflowArg));
    }
}
```

可以想到，如果调用的是一个接口interface中定义的方法，那么，在gadgetinspector对其扫描期间，并不在被扫描程序的Runtime，那么，就没办法取确定实际上的实现method。

我看过有文章分析，可以通过查找该方法method的实现（接口的实现类中的方法）进行污染判断，不过，这种方式还是具有缺陷性，例如，这个接口存在着两个实现类，那么，从上述代码就可以看到，只能选择其中一个实现方法的污染结果进行判断。

1.  调用链搜索不完整，还是因为多态性的原因，做不到完整的调用链搜索：

gadgetinspector.CallGraphDiscovery.ModelGeneratorMethodVisitor#visitMethodInsn

```plain
//记录参数流动关系
//argIndex：当前方法参数索引，srcArgIndex：对应上一级方法的参数索引
discoveredCalls.add(new GraphCall(
        new MethodReference.Handle(new ClassReference.Handle(this.owner), this.name, this.desc),
        new MethodReference.Handle(new ClassReference.Handle(owner), name, desc),
        srcArgIndex,
        srcArgPath,
        argIndex));
```

如果调用的是一个接口interface中定义的方法，那么，在gadgetinspector对其扫码期间，并不在被扫码程序的Runtime，那么，也就没办法取确定实际上的实现method。

不过，对于这种缺陷，我们是不是可以考虑，通过列举所有的接口实现类出来，并把他们加入到调用链中？这个办法，有好处也有坏处，好处即是能全部Runtime时不管能不能执行到的实现都加进去了。而坏处也是因为这点，会造成路径爆炸，假如接口类有几十个实现类，如果把它们都加入到调用链中（不管Runtime到底是否能走到这个实现），造成的路径爆炸问题会非常严重。

1.  对于JNDI lookup的slink并没有加入
2.  还不能挖掘Fastjson利用链
3.  等等...

而本篇文章，是围绕着第3、4点而讲，即讲述如何改造gadgetinspector，使它能够挖掘Fastjson的gadget chain

### 0x02 如何新加序列化方式

#### source

对于看过gadgetinspector，并且看懂了的小伙伴来说，能够发现，对于一种新序列化方式的gadget chain挖掘，gadgetinspector做到了很好的适配。

```plain
public interface GIConfig {

    String getName();
    SerializableDecider getSerializableDecider(Map<MethodReference.Handle, MethodReference> methodMap, InheritanceMap inheritanceMap);
    ImplementationFinder getImplementationFinder(Map<MethodReference.Handle, MethodReference> methodMap,
                                                 Map<MethodReference.Handle, Set<MethodReference.Handle>> methodImplMap,
                                                 InheritanceMap inheritanceMap);
    SourceDiscovery getSourceDiscovery();

}
```

```plain
public class JacksonDeserializationConfig implements GIConfig {

    @Override
    public String getName() {
        return "jackson";
    }

    @Override
    public SerializableDecider getSerializableDecider(Map<MethodReference.Handle, MethodReference> methodMap, InheritanceMap inheritanceMap) {
        return new JacksonSerializableDecider(methodMap);
    }

    @Override
    public ImplementationFinder getImplementationFinder(Map<MethodReference.Handle, MethodReference> methodMap,
                                                        Map<MethodReference.Handle, Set<MethodReference.Handle>> methodImplMap,
                                                        InheritanceMap inheritanceMap) {
        return new JacksonImplementationFinder(getSerializableDecider(methodMap, inheritanceMap));
    }

    @Override
    public SourceDiscovery getSourceDiscovery() {
        return new JacksonSourceDiscovery();
    }
}
```

从上述代码中，可以看到，想要增加新的反序列化类型的挖掘，需要的是实现GIConfig接口，并通过实现类构造三个组件：

1.  SerializableDecider：序列化决策者，这个决策者的作用主要围绕着apply方法的实现，通过apply方法，判断目标类class是否具备这可序列化，那么相对而言就是是否可以被反序列化
2.  ImplementationFinder：对于一个接口interface，该组件主要用于判断它的实现类，是否能被反序列化
3.  SourceDiscovery：链的起始端搜索类，类似于jackson对于json的解析，在反序列化时，会有一定条件的触发setter、getter方法，那么，这些方法即是整个gadget chain的入口点，而该组件就是用于搜索所有具备这样特征的类

我们可以看看jackson对于这三个组件的具体实现是怎么样的：

-   SerializableDecider->JacksonSerializableDecider

```plain
public class JacksonSerializableDecider implements SerializableDecider {
    ...

    @Override
    public Boolean apply(ClassReference.Handle handle) {
        Boolean cached = cache.get(handle);
        if (cached != null) {
            return cached;
        }

        Set<MethodReference.Handle> classMethods = methodsByClassMap.get(handle);
        if (classMethods != null) {
            for (MethodReference.Handle method : classMethods) {
                //该类，只要有无参构造方法，就通过决策
                if (method.getName().equals("<init>") && method.getDesc().equals("()V")) {
                    cache.put(handle, Boolean.TRUE);
                    return Boolean.TRUE;
                }
            }
        }

        cache.put(handle, Boolean.FALSE);
        return Boolean.FALSE;
    }
}
```

很明显，jackson对于是否可被反序列化的判断就是是否存在无参构造方法。

-   ImplementationFinder->JacksonImplementationFinder

```plain
public class JacksonImplementationFinder implements ImplementationFinder {

    private final SerializableDecider serializableDecider;

    public JacksonImplementationFinder(SerializableDecider serializableDecider) {
        this.serializableDecider = serializableDecider;
    }

    @Override
    public Set<MethodReference.Handle> getImplementations(MethodReference.Handle target) {
        Set<MethodReference.Handle> allImpls = new HashSet<>();

        // For jackson search, we don't get to specify the class; it uses reflection to instantiate the
        // class itself. So just add the target method if the target class is serializable.
        if (Boolean.TRUE.equals(serializableDecider.apply(target.getClassReference()))) {
            allImpls.add(target);
        }

        return allImpls;
    }
}
```

而对于判断是否有效实现类，也是借用到了JacksonSerializableDecider，通过它判断，只要具有无参构造方法，那么就是有效的实现类。

-   SourceDiscovery->JacksonSourceDiscovery

```plain
public class JacksonSourceDiscovery extends SourceDiscovery {

    @Override
    public void discover(Map<ClassReference.Handle, ClassReference> classMap,
                         Map<MethodReference.Handle, MethodReference> methodMap,
                         InheritanceMap inheritanceMap) {

        final JacksonSerializableDecider serializableDecider = new JacksonSerializableDecider(methodMap);

        for (MethodReference.Handle method : methodMap.keySet()) {
            if (serializableDecider.apply(method.getClassReference())) {
                if (method.getName().equals("<init>") && method.getDesc().equals("()V")) {
                    addDiscoveredSource(new Source(method, 0));
                }
                if (method.getName().startsWith("get") && method.getDesc().startsWith("()")) {
                    addDiscoveredSource(new Source(method, 0));
                }
                if (method.getName().startsWith("set") && method.getDesc().matches("\\(L[^;]*;\\)V")) {
                    addDiscoveredSource(new Source(method, 0));
                }
            }
        }
    }

}
```

对于source搜索组件的逻辑，jackson的处理也非常简单，就是只要有无参构造方法或getter、setter，就能被标识为source起点类

最后，在实现了这三个组件之后，还有最后的一步，需要把他们的构造放到上述所讲的JacksonDeserializationConfig，也就是GIConfig的实现类中，并最后，放到配置库中ConfigRepository：

```plain
public class ConfigRepository {
    private static final List<GIConfig> ALL_CONFIGS = Collections.unmodifiableList(Arrays.asList(
            new JavaDeserializationConfig(),
            new JacksonDeserializationConfig(),
            new XstreamDeserializationConfig()));

    public static GIConfig getConfig(String name) {
        for (GIConfig config : ALL_CONFIGS) {
            if (config.getName().equals(name)) {
                return config;
            }
        }
        return null;
    }
}
```

#### slink

除了三个组件确定节点有效性以外，最终数据流是否能触发到slink，亦是需要进行判断的。而gadgetinspector是这么做的：

gadgetinspector.GadgetChainDiscovery#isSink

```plain
private boolean isSink(MethodReference.Handle method, int argIndex, InheritanceMap inheritanceMap) {
    if (method.getClassReference().getName().equals("java/io/FileInputStream")
            && method.getName().equals("<init>")) {
        return true;
    }
    if (method.getClassReference().getName().equals("java/io/FileOutputStream")
            && method.getName().equals("<init>")) {
        return true;
    }
    if (method.getClassReference().getName().equals("java/nio/file/Files")
        && (method.getName().equals("newInputStream")
            || method.getName().equals("newOutputStream")
            || method.getName().equals("newBufferedReader")
            || method.getName().equals("newBufferedWriter"))) {
        return true;
    }

    if (method.getClassReference().getName().equals("java/lang/Runtime")
            && method.getName().equals("exec")) {
        return true;
    }
    /*
    if (method.getClassReference().getName().equals("java/lang/Class")
            && method.getName().equals("forName")) {
        return true;
    }
    if (method.getClassReference().getName().equals("java/lang/Class")
            && method.getName().equals("getMethod")) {
        return true;
    }
    */
    // If we can invoke an arbitrary method, that's probably interesting (though this doesn't assert that we
    // can control its arguments). Conversely, if we can control the arguments to an invocation but not what
    // method is being invoked, we don't mark that as interesting.
    if (method.getClassReference().getName().equals("java/lang/reflect/Method")
            && method.getName().equals("invoke") && argIndex == 0) {
        return true;
    }
    if (method.getClassReference().getName().equals("java/net/URLClassLoader")
            && method.getName().equals("newInstance")) {
        return true;
    }
    if (method.getClassReference().getName().equals("java/lang/System")
            && method.getName().equals("exit")) {
        return true;
    }
    if (method.getClassReference().getName().equals("java/lang/Shutdown")
            && method.getName().equals("exit")) {
        return true;
    }
    if (method.getClassReference().getName().equals("java/lang/Runtime")
            && method.getName().equals("exit")) {
        return true;
    }

    if (method.getClassReference().getName().equals("java/nio/file/Files")
            && method.getName().equals("newOutputStream")) {
        return true;
    }

    if (method.getClassReference().getName().equals("java/lang/ProcessBuilder")
            && method.getName().equals("<init>") && argIndex > 0) {
        return true;
    }

    if (inheritanceMap.isSubclassOf(method.getClassReference(), new ClassReference.Handle("java/lang/ClassLoader"))
            && method.getName().equals("<init>")) {
        return true;
    }

    if (method.getClassReference().getName().equals("java/net/URL") && method.getName().equals("openStream")) {
        return true;
    }

    // Some groovy-specific sinks
    if (method.getClassReference().getName().equals("org/codehaus/groovy/runtime/InvokerHelper")
            && method.getName().equals("invokeMethod") && argIndex == 1) {
        return true;
    }

    if (inheritanceMap.isSubclassOf(method.getClassReference(), new ClassReference.Handle("groovy/lang/MetaClass"))
            && Arrays.asList("invokeMethod", "invokeConstructor", "invokeStaticMethod").contains(method.getName())) {
        return true;
    }

    return false;
}
```

代码有点多，但是不难看懂，其实就是对于一条执行链最末端的判断，基本都是判断是否属于某个类的某个方法，或者是否是某个类的子类、某个接口的实现类的某个方法。只要满足判断的特征，那么就证明这条链的可用性。

### 0x03 Fastjson反序列化方式添加前的准备

在添加Fastjson前，参考jackson三个组件，我们需要去了解Fastjson的一些特性：

1.  可被反序列化的类特征
2.  反序列化可被触发执行的方法特征

#### 可被反序列化的类特征：

通过阅读Fastjson的代码，在"@type"的处理部分

com.alibaba.fastjson.parser.ParserConfig#checkAutoType(java.lang.String, java.lang.Class<?>, int)方法调用后，会返回一个class类对象

```plain
clazz = config.checkAutoType(typeName, null, lexer.getFeatures());
```

紧接着，会进行黑名单、白名单等判断，接着会创建JavaBeanInfo，进行autoType以及构造方法的判断

创建JavaBeanInfo

```plain
JavaBeanInfo beanInfo = JavaBeanInfo.build(clazz
        , type
        , propertyNamingStrategy
        ,false
        , TypeUtils.compatibleWithJavaBean
        , jacksonCompatible
);
```

在build方法中，会对构造方法进行获取并判断

```plain
Constructor[] constructors = clazz.getDeclaredConstructors();

Constructor<?> defaultConstructor = null;
if ((!kotlin) || constructors.length == 1) {
    if (builderClass == null) {
        defaultConstructor = getDefaultConstructor(clazz, constructors);
    } else {
        defaultConstructor = getDefaultConstructor(builderClass, builderClass.getDeclaredConstructors());
    }
}
```

```plain
static Constructor<?> getDefaultConstructor(Class<?> clazz, final Constructor<?>[] constructors) {
if (Modifier.isAbstract(clazz.getModifiers())) {
    return null;
}

Constructor<?> defaultConstructor = null;

for (Constructor<?> constructor : constructors) {
    if (constructor.getParameterTypes().length == 0) {
        defaultConstructor = constructor;
        break;
    }
}

if (defaultConstructor == null) {
    if (clazz.isMemberClass() && !Modifier.isStatic(clazz.getModifiers())) {
        Class<?>[] types;
        for (Constructor<?> constructor : constructors) {
            if ((types = constructor.getParameterTypes()).length == 1
                    && types[0].equals(clazz.getDeclaringClass())) {
                defaultConstructor = constructor;
                break;
            }
        }
    }
}

return defaultConstructor;
}
```

综上代码，可以清晰的得到，Fastjson对于大部分这些类的反序列化时，优先通过获取无参构造方法实例化，如果没有无参构造方法，则选择一个参数（参数类型和自身一致）的构造方法，并放到defaultConstructor中（后续会用于区分）。但如果都获取不到，那么就会走到下面的逻辑：

```plain
} else if (!isInterfaceOrAbstract) {
    String className = clazz.getName();

    String[] paramNames = null;
    if (kotlin && constructors.length > 0) {
        paramNames = TypeUtils.getKoltinConstructorParameters(clazz);
        creatorConstructor = TypeUtils.getKoltinConstructor(constructors, paramNames);
        TypeUtils.setAccessible(creatorConstructor);
    } else {

        for (Constructor constructor : constructors) {
        ...
            paramNames = lookupParameterNames;
            creatorConstructor = constructor;
        }
    }
}
```

可以看到，若是没有无参和一参（和自身class类型一致）构造方法的话，就会遍历构造方法，取最后一个，但是，构造方法会放在creatorConstructor，将会导致在com/alibaba/fastjson/parser/ParserConfig.java:1325，即：

方法com.alibaba.fastjson.parser.ParserConfig#checkAutoType(java.lang.String, java.lang.Class<?>, int)中

```plain
JavaBeanInfo beanInfo = JavaBeanInfo.build(clazz, clazz, propertyNamingStrategy);
if (beanInfo.creatorConstructor != null && autoTypeSupport) {
    throw new JSONException("autoType is not support. " + typeName);
}
```

可以看到，如果creatorConstructor不为空，并且autoTypeSupport为true，就会直接抛异常.

而不开启autoType，后续判断到没开启autoType，也会抛出异常

```plain
if (!autoTypeSupport) {
    throw new JSONException("autoType is not support. " + typeName);
}
```

但在其抛异常的判断之前，/Users/xuanyh/.ideaLibSources/fastjson-1.2.59-sources.jar!/com/alibaba/fastjson/parser/ParserConfig.java:1154，还是在方法com.alibaba.fastjson.parser.ParserConfig#checkAutoType(java.lang.String, java.lang.Class<?>, int)中

```plain
boolean autoTypeSupport = this.autoTypeSupport
        || (features & mask) != 0
        || (JSON.DEFAULT_PARSER_FEATURE & mask) != 0;

if (clazz == null && (autoTypeSupport || jsonType || expectClassFlag)) {
    boolean cacheClass = autoTypeSupport || jsonType;
    clazz = TypeUtils.loadClass(typeName, defaultClassLoader, cacheClass);
}
```

只要开启了autoType，都会调用TypeUtils.loadClass去加载class，观察其内部代码实现可以发现，会把class放到mappings缓存中

```plain
public static Class<?> loadClass(String className, ClassLoader classLoader, boolean cache) {
    if(className == null || className.length() == 0 || className.length() > 128){
        return null;
    }

    Class<?> clazz = mappings.get(className);
    if(clazz != null){
        return clazz;
    }

    if(className.charAt(0) == '['){
        Class<?> componentType = loadClass(className.substring(1), classLoader);
        return Array.newInstance(componentType, 0).getClass();
    }

    if(className.startsWith("L") && className.endsWith(";")){
        String newClassName = className.substring(1, className.length() - 1);
        return loadClass(newClassName, classLoader);
    }

    try{
        if(classLoader != null){
            clazz = classLoader.loadClass(className);
            if (cache) {
                mappings.put(className, clazz);
            }
            return clazz;
        }
    } catch(Throwable e){
        e.printStackTrace();
        // skip
    }
    try{
        ClassLoader contextClassLoader = Thread.currentThread().getContextClassLoader();
        if(contextClassLoader != null && contextClassLoader != classLoader){
            clazz = contextClassLoader.loadClass(className);
            if (cache) {
                mappings.put(className, clazz);
            }
            return clazz;
        }
    } catch(Throwable e){
        // skip
    }
    try{
        clazz = Class.forName(className);
        if (cache) {
            mappings.put(className, clazz);
        }
        return clazz;
    } catch(Throwable e){
        // skip
    }
    return clazz;
}
```

从上面的代码，得到一个非常重要的信息，通过这个缓存，我们可以得到一个构造方法判断绕过方式：一个需要反序列化的class，如果不存在上面所说的无参、一参构造方法，那么在第一次反序列化时，会通过TypeUtils.loadClass存到mappings缓存，然后再到后面的抛异常报错，但是这个时候，class已经加到mappings缓存了，那么，只要再发起一次反序列化，就能从最早最早的地方从mappings缓存加载，从而避免了后续的构造方法和autoType判断

```plain
if (clazz == null) {
    clazz = TypeUtils.getClassFromMapping(typeName);
}

if (clazz == null) {
    clazz = deserializers.findClass(typeName);
}

if (clazz == null) {
    clazz = typeMapping.get(typeName);
}

if (clazz != null) {
    if (expectClass != null
            && clazz != java.util.HashMap.class
            && !expectClass.isAssignableFrom(clazz)) {
        throw new JSONException("type not match. " + typeName + " -> " + expectClass.getName());
    }

    return clazz;
}
```

那么也就是说，对于Fastjson，不管存不存在无参或自身类型一致的一参构造方法，都能被反序列化。

PS：而关于注解部分，大部分第三方依赖都不会用到Fastjson的注解，这部分我们暂且不加入，因为gadgetinspector对于方法扫描的时候还没有做到存储注解，如果需要做这样的改造的话，需要做一部分的改造，这篇文章暂且不提。

#### 反序列化可被触发执行的方法特征

因为Fastjson反序列化时，并不是直接反射Field设值，而是智能的提取出相应的setter、getter方法等，然后通过这些方法提取得到字段名称，接着进行设值

对于反序列化时会调用哪个特征的方法，由于网络上有一部分博文已经描述总结得很详细了，故而，我这边也不再贴代码了。

setter：

1.  方法名长度大于3
2.  非静态方法
3.  返回类型为Void.TYPE
4.  返回类型为自身class类型
5.  显式入参只有一个

getter：

1.  对于提取名称（getName->name），setter未存在的
2.  方法名长度大于3，并且第4个字符为大写
3.  非静态方法
4.  没有入参
5.  返回值类型是Collection.class、Map.class、AtomicBoolean.class、AtomicInteger.class、AtomicLong.class或是其子孙类

### 0x04 编写Fastjson三件套

#### SerializableDecider->FastjsonSerializableDecider

由上一节分析得出，只要存在构造方法，就能被Fastjson反序列化，因此，对于SerializableDecider的apply方法的逻辑实现，全部返回true就可以了。

```plain
public class FastjsonSerializableDecider implements SerializableDecider {
    public FastjsonSerializableDecider(Map<MethodReference.Handle, MethodReference> methodMap) {
    }

    @Override
    public Boolean apply(ClassReference.Handle handle) {
        return Boolean.TRUE;
    }
}
```

考虑到Fastjson具有反序列化黑名单的机制，如果各位想要减少已被禁用链的输出，可以在这里加入黑名单。

#### SourceDiscovery->FastjsonSourceDiscovery

根据前面列出的规则，创建Fastjson的SourceDiscovery

```plain
public class FastjsonSourceDiscovery extends SourceDiscovery {

  @Override
  public void discover(Map<ClassReference.Handle, ClassReference> classMap,
      Map<MethodReference.Handle, MethodReference> methodMap,
      InheritanceMap inheritanceMap) {

    final FastjsonSerializableDecider serializableDecider = new FastjsonSerializableDecider(
        methodMap);

    for (MethodReference.Handle method : methodMap.keySet()) {
      if (serializableDecider.apply(method.getClassReference())) {
        if (method.getName().startsWith("get") && method.getDesc().startsWith("()")) {
          if (method.getDesc().matches("\\(L[^;]*;\\)L.+?;")) {
            String fieldName =
                method.getName().charAt(3) + method.getName().substring(4);
            String desc = method.getDesc()
                .substring(method.getDesc().indexOf(")L") + 2, method.getDesc().length() - 1);
            MethodReference.Handle handle = new MethodReference.Handle(
                method.getClassReference(), "set" + fieldName, desc);
            if (!methodMap.containsKey(handle) &&
                method.getDesc().matches("\\(L[^;]*;\\)Ljava/util/Collection;") ||
                method.getDesc().matches("\\(L[^;]*;\\)Ljava/util/Map;") ||
                method.getDesc().matches("\\(L[^;]*;\\)Ljava/util/concurrent/atomic/AtomicBoolean;") ||
                method.getDesc().matches("\\(L[^;]*;\\)Ljava/util/concurrent/atomic/AtomicInteger;") ||
                method.getDesc().matches("\\(L[^;]*;\\)Ljava/util/concurrent/atomic/AtomicLong;")){
              addDiscoveredSource(new Source(method, 0));
            }
          }
        }
        if (method.getName().startsWith("set") && method.getDesc().matches("\\(L[^;]*;\\)V")) {
          addDiscoveredSource(new Source(method, 1));
        }
      }
    }
  }

}
```

#### ImplementationFinder->FastjsonImplementationFinder

因为该Finder类，基本都是用到SerializableDecider决策者就可以了，那么这个实现就非常简单

```plain
public class FastjsonImplementationFinder implements ImplementationFinder {

    private final SerializableDecider serializableDecider;

    public FastjsonImplementationFinder(SerializableDecider serializableDecider) {
        this.serializableDecider = serializableDecider;
    }

    @Override
    public Set<MethodReference.Handle> getImplementations(MethodReference.Handle target) {
        Set<MethodReference.Handle> allImpls = new HashSet<>();

        // For jackson search, we don't get to specify the class; it uses reflection to instantiate the
        // class itself. So just add the target method if the target class is serializable.
        if (Boolean.TRUE.equals(serializableDecider.apply(target.getClassReference()))) {
            allImpls.add(target);
        }

        return allImpls;
    }
}
```

#### 配置Fastjson以及添加到配置仓库ConfigRepository

```plain
public class FastjsonDeserializationConfig implements GIConfig {

    @Override
    public String getName() {
        return "fastjson";
    }

    @Override
    public SerializableDecider getSerializableDecider(Map<MethodReference.Handle, MethodReference> methodMap, InheritanceMap inheritanceMap) {
        return new FastjsonSerializableDecider(methodMap);
    }

    @Override
    public ImplementationFinder getImplementationFinder(Map<MethodReference.Handle, MethodReference> methodMap,
                                                        Map<MethodReference.Handle, Set<MethodReference.Handle>> methodImplMap,
                                                        InheritanceMap inheritanceMap) {
        return new FastjsonImplementationFinder(getSerializableDecider(methodMap, inheritanceMap));
    }

    @Override
    public SourceDiscovery getSourceDiscovery() {
        return new FastjsonSourceDiscovery();
    }
}
```

```plain
public class ConfigRepository {
    private static final List<GIConfig> ALL_CONFIGS = Collections.unmodifiableList(Arrays.asList(
            new JavaDeserializationConfig(),
            new JacksonDeserializationConfig(),
            new XstreamDeserializationConfig(),
            new FastjsonDeserializationConfig()));

    public static GIConfig getConfig(String name) {
        for (GIConfig config : ALL_CONFIGS) {
            if (config.getName().equals(name)) {
                return config;
            }
        }
        return null;
    }
}
```

### 0x05 优化slink-加入jndi-lookup

因为Fastjson反序列化RCE很多的打法，基本都是jndi-lookup实现，但是我看到gadgetinspector中并没有该slink的判断，因此，加入该slink的判断，以对其进行优化

gadgetinspector.GadgetChainDiscovery#isSink

在该方法末尾添加jndi-lookup判断即可

```plain
if (inheritanceMap.isSubclassOf(method.getClassReference(), new ClassReference.Handle("javax/naming/Context"))
        && method.getName().equals("lookup")) {
    return true;
}
```

至此，gadgetinspector的改造就完成了，那么接下来，我们以一个已有gadget chain的jar进行扫码挖掘，测试一下效果

例：HikariCP-3.4.1.jar

扫码挖掘结果：

```plain
sun/usagetracker/UsageTrackerClient.setup(Ljava/io/File;)V (1)
  java/io/FileInputStream.<init>(Ljava/io/File;)V (1)

org/apache/log4j/jmx/LayoutDynamicMBean.setAttribute(Ljavax/management/Attribute;)V (1)
  java/lang/reflect/Method.invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object; (0)

com/sun/org/apache/xml/internal/serializer/ToStream.setOutputFormat(Ljava/util/Properties;)V (1)
  com/sun/org/apache/xml/internal/serializer/ToStream.init(Ljava/io/Writer;Ljava/util/Properties;ZZ)V (2)
  com/sun/org/apache/xml/internal/serializer/CharInfo.getCharInfo(Ljava/lang/String;Ljava/lang/String;)Lcom/sun/org/apache/xml/internal/serializer/CharInfo; (0)
  com/sun/org/apache/xml/internal/serializer/CharInfo.<init>(Ljava/lang/String;Ljava/lang/String;Z)V (1)
  java/net/URL.openStream()Ljava/io/InputStream; (0)

com/sun/management/jmx/TraceListener.setFile(Ljava/lang/String;)V (1)
  java/io/FileOutputStream.<init>(Ljava/lang/String;Z)V (1)

com/zaxxer/hikari/HikariConfig.setMetricRegistry(Ljava/lang/Object;)V (1)
  com/zaxxer/hikari/HikariConfig.getObjectOrPerformJndiLookup(Ljava/lang/Object;)Ljava/lang/Object; (1)
  javax/naming/InitialContext.lookup(Ljava/lang/String;)Ljava/lang/Object; (1)

org/apache/log4j/jmx/AppenderDynamicMBean.setAttribute(Ljavax/management/Attribute;)V (1)
  org/apache/log4j/jmx/AppenderDynamicMBean.getAttribute(Ljava/lang/String;)Ljava/lang/Object; (1)
  java/lang/reflect/Method.invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object; (0)

org/apache/log4j/varia/LevelMatchFilter.setLevelToMatch(Ljava/lang/String;)V (1)
  org/apache/log4j/helpers/OptionConverter.toLevel(Ljava/lang/String;Lorg/apache/log4j/Level;)Lorg/apache/log4j/Level; (0)
  java/lang/reflect/Method.invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object; (0)

org/apache/log4j/jmx/LayoutDynamicMBean.setAttribute(Ljavax/management/Attribute;)V (1)
  org/apache/log4j/jmx/LayoutDynamicMBean.getAttribute(Ljava/lang/String;)Ljava/lang/Object; (1)
  java/lang/reflect/Method.invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object; (0)

org/apache/log4j/jmx/AppenderDynamicMBean.setAttribute(Ljavax/management/Attribute;)V (1)
  java/lang/reflect/Method.invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object; (0)
```

可以看到，其中我们新加入的jndi-lookup的slink，顺利的挖掘到一个可用的gadget chain：

```plain
com/zaxxer/hikari/HikariConfig.setMetricRegistry(Ljava/lang/Object;)V (1)
  com/zaxxer/hikari/HikariConfig.getObjectOrPerformJndiLookup(Ljava/lang/Object;)Ljava/lang/Object; (1)
  javax/naming/InitialContext.lookup(Ljava/lang/String;)Ljava/lang/Object; (1)
```

当然，这个gadget chain早在1.2.60就被黑名单禁了，哈哈！还有就是，文章难免某个地方会搞错，希望各位dalao阅读之后可以不吝指教。

新年将至，也祝各位小伙伴能挖到好洞，过一个愉快的肥年，谢谢！
