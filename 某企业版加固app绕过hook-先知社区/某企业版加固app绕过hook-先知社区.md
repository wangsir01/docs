

# 某企业版加固app绕过hook - 先知社区

某企业版加固app绕过hook

- - -

# 1、环境及背景

pixel 2  
某app （\*\*\*企业版加固）  
frida 15.1.28

# 2、hook绕过

启用frida并更改端口没有发现检测行为但是直接hook会闪退

[![](assets/1704273649-1682f4875d2b03bffdf91439e707b757.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240102095217-8f4ce638-a911-1.png)

打印so 调用堆栈

```plain
function hook_pthread(){
        var pthread_create_addr = Module.findExportByName(null, 'pthread_create
    var pthread_create = new NativeFunction(pthread_create_addr, "int", ["pointer", "pointer", "pointer", "pointer"]);

    Interceptor.replace(pthread_create_addr, new NativeCallback(function (parg0, parg1, parg2, parg3) {
        var so_name = Process.findModuleByAddress(parg2).name;
        var so_path = Process.findModuleByAddress(parg2).path;
        var so_base = Module.getBaseAddress(so_name);
        var offset = parg2 - so_base;
        var PC = 0;
        if ((so_name.indexOf("libexec.so") > -1)) {
            console.log("find thread func offset", so_name, offset);
        } else {
            PC = pthread_create(parg0, parg1, parg2, parg3);
        }
        return PC;
    }, "int", ["pointer", "pointer", "pointer", "pointer"]))
}
hook_pthread();
```

[![](assets/1704273649-c8712bb5474d7d2d45339357fe9c40b6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240102095252-a3edb824-a911-1.png)

找到了libexec.so开启pthread\_create的偏移量，对其进行bypass，即

```plain
function hook_pthread() {

    var pthread_create_addr = Module.findExportByName(null, 'pthread_create');

    var pthread_create = new NativeFunction(pthread_create_addr, "int", ["pointer", "pointer", "pointer", "pointer"]);
    Interceptor.replace(pthread_create_addr, new NativeCallback(function (parg0, parg1, parg2, parg3) {
        var so_name = Process.findModuleByAddress(parg2).name;
        var so_path = Process.findModuleByAddress(parg2).path;
        var so_base = Module.getBaseAddress(so_name);
        var offset = parg2 - so_base;
        var PC = 0;
        if ((so_name.indexOf("libexec.so") > -1)) {
            console.log("find thread func offset", so_name, offset);
            if ((207076 === offset)) {
                console.log("anti bypass");
            } else if (207308 === offset) {
                console.log("anti bypass");
            } else if (283820 === offset) {
                console.log("anti bypass");
            } else if (286488 === offset) {
                console.log("anti bypass");
            } else if (292416 === offset) {
                console.log("anti bypass");
            } else if (78136 === offset) {
                console.log("anti bypass");
            } else if (293768 === offset) {
                console.log("anti bypass");
            } else {
                PC = pthread_create(parg0, parg1, parg2, parg3);
            }
        } else {
            PC = pthread_create(parg0, parg1, parg2, parg3);
        }
        return PC;
    }, "int", ["pointer", "pointer", "pointer", "pointer"]))
}
hook_pthread();
```

[![](assets/1704273649-a087844293e3cb09628dff7c170c2c10.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240102095314-b129f6ba-a911-1.png)

已经对其进行绕过frida的检测。

# 3、class的遍历和hook

绕过frida的检测之后，开始对其加载的class以及class中的函数进行遍历

```plain
Java.enumerateLoadedClasses({
        onMatch: function(className) {
        console.log("found class >> " + className);
        //遍历类中所有的方法和属性
        var jClass = Java.use(className);
             console.log(JSON.stringify({
                    _name: className,
                    _methods: Object.getOwnPropertyNames(jClass.__proto__).filter(function(m) {
                    return !m.startsWith('$') // filter out Frida related special properties
                    || m == 'class' || m == 'constructor' // optional
                }), 
                     _fields: jClass.class.getFields().map(function(f) {
                     return f.toString()
                    })
              }, null, 2));
               //遍历类中所有的方法和属性
          },
        onComplete: function() {
              console.log("[*] class enuemration complete");
           }
    });
```

[![](assets/1704273649-9cba9ddd3e1660fe1133423d9536f6b1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240102095513-f82c9504-a911-1.png)

class和函数大部分已经被遍历出来了，但是由于是加固的，部分函数并没有被加载出来(意料之中)，利用常规的框架尝试去执行

```plain
//框架为
if(Java.available) {
    Java.perform(function(){
        var application = Java.use("android.app.Application");

        application.attach.overload('android.content.Context').implementation = function(context) {
            var result = this.attach(context); // 先执行原来的attach方法
            var classloader = context.getClassLoader(); // 获取classloader
            Java.classFactory.loader = classloader;
            var Hook_class = Java.classFactory.use("com.xxx.xxx");  // app的类
            console.log("Hook_class: " + Hook_class);
            // 下面代码和写正常的hook一样
            Hook_class.函数.implementation = function()  // 有参数填参数
            {
            }

            return result;
        }
    });
}
```

发现会执行不成功，说明加固后的app没有用常规的classloader去加载函数。因此需要去遍历在加载app的时候，是哪些classloader被加载  
1、可以通过重加载指定classloader去使得脱壳后的源码能在内存中被找到  
2、可以一次性重加载所有调用的classloader去执行

```plain
//获取加固的classloader并hook函数
Java.enumerateClassLoaders({
        onMatch: function(loader){
            // 每次匹配到，都要把匹配到的赋值给java默认的loader
            Java.classFactory.loader = loader;
            var TryClass;
            // console.log(loader); // 输出被加载的classloader
            // 没报错就hook到了，报错了就hook下一个，如果全都报错了，没打印东西，那可能就是hook错了。
            try{ // 每一次加载尝试是否可以找到想要的class
                TryClass = Java.use("cn.xxx"); // 需要被加载之后查询的类
                TryClass.xx.implementation = function(p1,p2){ // 类的函数
                    console.log('p1:'+p1)
                    console.log('p2:'+p2)
                    return this.xx(p1,p2)
                }
            }catch(error){
                if(error.message.includes("ClassNotFoundException")){
                    console.log(" You are trying to load encrypted class, trying next loader");
                }
                else{
                    console.log(error.message);
               }
            }
        },
        onComplete: function(){
        }
})
```

[![](assets/1704273649-86af9551860fecd2e37c6c6931118932.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240102095531-02ee8f06-a912-1.png)

用2的方法被加载成功。

# 4、最后

最终成功实现在\*\*\*企业版中去hook数据，当然这需要成功的脱壳之后查看原app存在哪些函数才行。依靠遍历出来的class  
[![](assets/1704273649-cd18ef8ec8a09d36adea414c987a3b8c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240102095540-08117e3a-a912-1.png)
