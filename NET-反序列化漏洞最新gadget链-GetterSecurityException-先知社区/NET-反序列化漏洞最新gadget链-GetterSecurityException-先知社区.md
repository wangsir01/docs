

# .NET 反序列化漏洞最新gadget链 GetterSecurityException - 先知社区

.NET 反序列化漏洞最新gadget链 GetterSecurityException

- - -

# GetterSecurityException gadget

> 细致解读2023年Hexacon会议上发表的 .NET 反序列化最新链路的白皮书，本次介绍 GetterSecurityException gadget，System.Security.SecurityException位于mscorlib.dll程序集，用于应用程序尝试执行需要特定权限的操作时，因权限不足或与CAS策略冲突时导致的异常错误信息。

- - -

## 链路1 SecurityException

SecurityException类的Method成员，对象访问器Getter调用了内部方法this.getMethod()，修改器Setter通过ObjectToByteArray方法转换为字节，如下图所示  
[![](assets/1699250170-0493c1472674eb226758c384dede44d1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102105614-62ac1ea2-792b-1.png)  
通过反编译ObjectToByteArray得知，内部使用BinaryFormatter.Serialize将对象序列化成一个MemoryStream，并通过ToArray方法返回byte\[\]类型，如下图所示  
[![](assets/1699250170-21187a49ded8050d34b3fac84df5554e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102105625-694f45a4-792b-1.png)  
因此访问SecurityException对象的Method属性时触发的getMethod()方法，一定是通过BinaryFormatter格式化器反序列化对象，打开后发现调用了ByteArrayToObject，如下图所示  
[![](assets/1699250170-49b53c6854f606d38027f53f6406f66b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102105649-77abda68-792b-1.png)  
从方法名知道ByteArrayToObject正好与Setter里的ObjectToByteArray相反，用于反序列化操作，如下图所示  
[![](assets/1699250170-a8913aac90a32c859f7b59356456ca64.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102105705-81772a2a-792b-1.png)  
因此攻击者控制Method属性通过setter赋值的方式添加BinaryFormatter攻击载荷，便能在调用getter时触发反序列化漏洞。

## 链路2 PropertyGrid

System.Windows.Forms.PropertyGrid 是Windows Forms中的一个控件，通常用于创建属性窗格，便于用户直观地查看和编辑对象的属性值。这个gadget是通过修改器setter设置SelectedObjects属性时触发的，该setter很复杂并且包含大量代码，重要的是Refresh()方法，Refresh方法触发RefreshProperties、UpdateSelection、CreateChildren这一系列的多个方法的调用，然后进入GridEntry.GetPropEntries，如下图所示  
[![](assets/1699250170-76c37930293c6abdcfe565bdb281fbaf.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102105757-a08f2cd2-792b-1.png)  
该方法内部迭代对象的成员，并通过PropertyDescriptor2.GetValue方法获取每个成员值，这个过程会调用每个成员的访问器getter，如下图所示  
[![](assets/1699250170-6431ec659b702b77b37ce0cb042f2c32.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102105813-a9f0292a-792b-1.png)

## 编码实践

根据上述两条链路的原理性分析，我们可以尝试着构造用于恶意反序列化的攻击代码，结合Ysoserial.Net的代码实现如下

```plain
payload = @"{
    '$type':'System.Windows.Forms.PropertyGrid, System.Windows.Forms, Version = 4.0.0.0, Culture = neutral, PublicKeyToken = b77a5c561934e089',
    'SelectedObjects':[" + sePayload + @"]}";
```

PropertyGrid类 的SelectedObjects属性是一个数组，由包含了攻击载荷的变量sePayload 构建的，sePayload变量定义的代码如下

```plain
string sePayload = @"{
    '$type':'System.Security.SecurityException',
    'ClassName':'System.Security.SecurityException',
    'Message':'Security error.',
    'InnerException':null,
    'HelpURL':null,
    'StackTraceString':null,
    'RemoteStackTraceString':null,
    'RemoteStackIndex':0,
    'ExceptionMethod':null,
    'HResult':-2146233078,
    'Source':null,
    'Action':0,
    'Method':'" + b64encoded + @"',
    'Zone':0
}";
```

Method是一组进行Base64编码后基于BinaryFormatter生成的攻击载荷，原理前文已经分析过，此处不再赘述，调试时打印出完整的Payload，如下贴图所示  
[![](assets/1699250170-05058ce492ea3db42dedbf481790133a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102110050-0794842c-792c-1.png)  
最后通过上面这段JSON.NET代码完成整条攻击链路的反序列化，成功启动本地计算器进程，如下图所示  
[![](assets/1699250170-b2b14342c30f20ec73821f995a2575a4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231102110114-15e159c4-792c-1.png)

打赏
