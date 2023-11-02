

# 打造高度自定义的渗透工具-Burp插件开发（一） - 先知社区

打造高度自定义的渗透工具-Burp插件开发（一）

- - -

Burp提供了高度可拓展性，很多我们想实现的功能都可以以插件的形式实现，之前也是因为不懂写插件很多自己的想法无法自动化实现，所以学了一波Burp插件开发，此系列有几篇我也不清楚，**随缘**写吧。

# Burp Extenstion API

## 前言

**本文会略过一些简单步骤如安装插件，安装Jython环境等。**

Burp插件提供了几种语言的开发方式：Python、Java、Ruby等，以下文中我会以Python为例子来讲解某个插件该如何使用。

Burp提供了API的介绍文档：[Generated Documentation](https://portswigger.net/burp/extender/api/index.html)。

并且在官方中也有提供例子供我们学习：[Burp Suite Extensibility - PortSwigger](https://portswigger.net/burp/extender/)

[![](assets/1698897659-ea988c7ad314c2f5956714a18abbc61c.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxd8gsp2j31hd0u0n9o.jpg)

此例中提供了我们几个样例，并且给了三种语言的对应版本，我的个人建议是想实现什么功能，就使用某个案例，通过阅读其代码也能慢慢的了解Burp插件的API是如何实现其功能的，如果这些例子中找不到你想实现的功能，不妨去github搜搜别人写好的插件，通过阅读对应的代码也可以了解其某些功能的实现。

## 介绍

Burp的接口集合：

[![](assets/1698897659-67ffe952c9e1b1f63447d83abbc5e189.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxd9ieblj30fs0zijxk.jpg)

每个接口都会实现特定的功能，我通过阅读其使用案例的方式来学习每个接口的作用。

### IBurpCollaboratorClientContext

在了解此接口之前，我们可以先了解一下Burp的CollaboratorClient这个功能，相当于一个dnslog，我们可以生成某个地址，当我们访问这个地址时，Burp就会将对应请求输出给我们。

[![](assets/1698897659-2427f939e3336ef379eb4e7f668b3e09.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdamcoyj31fz0u0qc7.jpg)

[![](assets/1698897659-ae54ca46dd26739d81bc431c54cf13d9.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdbxiboj313k0u0wht.jpg)

当我们点击Copy to clipboard后，就可以拿到一个burp生成的请求地址，当我们访问他之后会输出一个字符串，并且会Burp会收到请求，此时我们如果点击Poll now就可以看到请求了：

[![](assets/1698897659-e0ceb0432cb97a17792e8c070c7e4054.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdcqt5aj31ks0qstb6.jpg)

Burp收到的请求，会返回响应以及返回包。

[![](assets/1698897659-3d8582f7a8308b30d24c96220ce252f6.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdd722nj314w0j6q57.jpg)

接下来了解一下实现这个功能的接口吧，此接口可实现如下方法：

[![](assets/1698897659-efd0ac6146e524d9df0bfe5e6492e5ae.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxde68qsj326w0t0dpv.jpg)

并且由`IBurpExtenderCallbacks.createBurpCollaboratorClientContext()`创建。

看到这是不是很懵逼？问题不大，我们一个个使用对应的方法，走一遍对应的流程就可以了。

-   generatePayload(boolean includeCollaboratorServerLocation)

[![](assets/1698897659-203add8aa99546635dbc2466a7bfe7be.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdf24fyj31940ggtbe.jpg)

IBurpCollaboratorClientContext.py

```plain
from burp import IBurpExtender
from burp import IBurpCollaboratorClientContext

class BurpExtender(IBurpExtender,IBurpCollaboratorClientContext):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName('IBurpCollaboratorClientContext')
        collaboratorContext = callbacks.createBurpCollaboratorClientContext()
        print(collaboratorContext.generatePayload(True))
        print(collaboratorContext.generatePayload(True))
```

此方法需要传递一个布尔值，由你传递的值为True或False决定了返回的payload是否带有CollaboratorServerLocation。

我们先看一下上述代码在Output中的输出结果：

[![](assets/1698897659-f7d432c52f28d8a30baf65301b913540.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdg0lo5j31de0jkgn4.jpg)

再看看当传递的布尔值为False时的输出结果：

[![](assets/1698897659-a7c75af33fe5cd70526c5ad4c1bf3ecd.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdgyj6nj31q60qqmz4.jpg)

可以看到，结果只是是否返回`.burpcollaborator.net`的区别而已。

-   getCollaboratorServerLocation()

[![](assets/1698897659-cb584249ace93da7a7ce0e078070f2b7.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdhvxozj30x20dsq4p.jpg)

返回Collaborator server的hostname或ip。

一样的，输出出来看看结果：

```plain
from burp import IBurpExtender
from burp import IBurpCollaboratorClientContext

class BurpExtender(IBurpExtender,IBurpCollaboratorClientContext):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName('IBurpCollaboratorClientContext')
        collaboratorContext = callbacks.createBurpCollaboratorClientContext()
        print(collaboratorContext.getCollaboratorServerLocation())
```

[![](assets/1698897659-bfd14e78d320e300d1658120868be171.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxditev2j30xc0d4wfc.jpg)

-   fetchAllCollaboratorInteractions()

```plain
from burp import IBurpExtender
from burp import IBurpCollaboratorClientContext
import os

class BurpExtender(IBurpExtender,IBurpCollaboratorClientContext):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName('IBurpCollaboratorClientContext')
        collaboratorContext = callbacks.createBurpCollaboratorClientContext()
        payload = collaboratorContext.generatePayload(True)
        print(payload)
        while True:
            print(collaboratorContext.fetchAllCollaboratorInteractions())
```

此时我为了保证能收到我手动访问的请求，使用了While循环来输出结果：

[![](assets/1698897659-5e63edbf277015a2fb1da6e10a0c779b.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdjfrgsj323605sq3q.jpg)

我使用generatePayload方法生成了一个payload，并在浏览器中手动访问他，过了一会儿之后就可以收到请求了，而此时我们可以使用fetchAllCollaboratorInteractions方法来获取所有payload的请求结果。

-   fetchCollaboratorInteractionsFor(payload)

此方法需要传递某个payload，而这个payload正是我们上文中利用generatePayload方法生成的payload，服务器将检索该payload所处的dns服务器是否收到请求，并将结果返回给我们。

```plain
from burp import IBurpExtender
from burp import IBurpCollaboratorClientContext
import os

class BurpExtender(IBurpExtender,IBurpCollaboratorClientContext):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName('IBurpCollaboratorClientContext')
        collaboratorContext = callbacks.createBurpCollaboratorClientContext()
        payload = collaboratorContext.generatePayload(True)
        print(payload)
        while True:
            print(collaboratorContext.fetchCollaboratorInteractionsFor(payload))
```

当我手动访问其生成的payload之后，就可以获取到请求结果：

[![](assets/1698897659-75e101cefca461b6f20eecd345a5c0b3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdk53iyj31qu0g0409.jpg)

可以看到此方法与上述方法的区别吗？其区别在于一个是检索单个payload，另外一个是检索在插件运行中生成的所有payload是否被请求。

**fetchInfiltratorInteractionsFor与fetchAllInfiltratorInteractions不常用，不予介绍。**

学习完了三个主要方法之后，我们就可以开始了解一下使用这些方法可以做什么了。我们需要先想想，Burp的CollaboratorClient相当于一个dnslog，我们一般都用dnslog来测试什么呢？

**BLIND XXE、BLIND SSRF、SQL外带、Blind OS INJECTION等。**

接下来以github的某个XXE扫描插件来介绍如何使用此api的三个方法实现一个Blind XXE Scanner。

插件地址：[XXEPlugin.java](https://github.com/yandex/burp-molly-pack/blob/8c9aa5766dcd4b49d3258bf7f3790bd318fe9b7f/src/main/java/com/yandex/burp/extensions/plugins/audit/XXEPlugin.java)

重点关注以下代码：

```plain
public void initXXEPayloads() {
        XXEPayloads.add("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<!DOCTYPE test [\n<!ENTITY % remote SYSTEM \"http://{collaboratorPayload}/\">\n%remote;\n]><test>test</test>");
        XXEPayloads.add("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><!DOCTYPE root PUBLIC \"-//B/A/EN\" \"http://{collaboratorPayload}/\"><root>a0e5c</root>");
        XXEPayloads.add("<?xml version=\"1.0\"?><!DOCTYPE foo [<!ENTITY xxe1 \"dryat\"><!ENTITY xxe2 \"0Uct\"><!ENTITY xxe3 \"333\"><!ENTITY xxe \"&xxe1;&xxe3;&xxe2;\">]><methodCall><methodName>BalanceSimple.CreateOrderOrSubscription</methodName><params><param><value><string>&xxe;test</string></value></param><param>x</params></methodCall>");
        XXEPayloads.add("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE tst SYSTEM \"http://{collaboratorPayload}\">\n<tst></tst>");
    }

    @Override
    public List<IScanIssue> doScan(IHttpRequestResponse baseRequestResponse, IScannerInsertionPoint insertionPoint) {
        IResponseInfo resp = helpers.analyzeResponse(baseRequestResponse.getResponse());
        IRequestInfo req = helpers.analyzeRequest(baseRequestResponse.getRequest());
        if (resp == null | req == null) return null;

        URL url = helpers.analyzeRequest(baseRequestResponse).getUrl();
        if (flags.contains(url.toString())) return null;
        else flags.add(url.toString());

        IBurpCollaboratorClientContext collaboratorContext = callbacks.createBurpCollaboratorClientContext();
        String collaboratorPayload = collaboratorContext.generatePayload(true);
        List<IScanIssue> issues = new ArrayList<>();

        for (String xxe : XXEPayloads) {
            xxe = xxe.replace("{collaboratorPayload}", collaboratorPayload);
            List<String> headers = helpers.analyzeRequest(baseRequestResponse).getHeaders();
            headers.set(0, headers.get(0).replace("GET", "POST"));
            headers.removeIf(header -> header != null && header.toLowerCase().startsWith("content-type:"));
            headers.add("Content-type: application/xml");

            byte[] attackBody = helpers.buildHttpMessage(headers, helpers.stringToBytes(xxe));
            IHttpRequestResponse attackRequestResponse = callbacks.makeHttpRequest(baseRequestResponse.getHttpService(), attackBody);
            List<IBurpCollaboratorInteraction> collaboratorInteractions = collaboratorContext.fetchCollaboratorInteractionsFor(collaboratorPayload);

            if (attackRequestResponse != null && attackRequestResponse.getResponse() != null
                    && collaboratorInteractions != null
                    && (!collaboratorInteractions.isEmpty() || helpers.bytesToString(attackRequestResponse.getResponse()).contains("dryat0Uct333"))) {
                String attackDetails = "XXE processing is enabled at: \n" + helpers.analyzeRequest(attackRequestResponse).getUrl().toString();

                issues.add(new CustomScanIssue(attackRequestResponse.getHttpService(),
                        helpers.analyzeRequest(attackRequestResponse).getUrl(),
                        new IHttpRequestResponse[]{callbacks.applyMarkers(attackRequestResponse, null, null)},
                        attackDetails, ISSUE_TYPE, ISSUE_NAME, SEVERITY, CONFIDENCE,
                        "", "", ""));
            }
        }
        return issues.isEmpty() ? null : issues;
    }
}
```

52-53行代码实现此接口并使用了generatePayload方法来获取一个payload：

```plain
IBurpCollaboratorClientContext collaboratorContext = callbacks.createBurpCollaboratorClientContext();
String collaboratorPayload = collaboratorContext.generatePayload(true);
```

56-65行为使用生成的payload替换xxe中的标志位后发起请求：

```plain
for (String xxe : XXEPayloads) {
            xxe = xxe.replace("{collaboratorPayload}", collaboratorPayload);
            List<String> headers = helpers.analyzeRequest(baseRequestResponse).getHeaders();
            headers.set(0, headers.get(0).replace("GET", "POST"));
            headers.removeIf(header -> header != null && header.toLowerCase().startsWith("content-type:"));
            headers.add("Content-type: application/xml");

            byte[] attackBody = helpers.buildHttpMessage(headers, helpers.stringToBytes(xxe));
            IHttpRequestResponse attackRequestResponse = callbacks.makeHttpRequest(baseRequestResponse.getHttpService(), attackBody);
            List<IBurpCollaboratorInteraction> collaboratorInteractions = collaboratorContext.fetchCollaboratorInteractionsFor(collaboratorPayload);
```

最后一行获取了解析结果，即是否有服务器向payload所处地址发起请求。

并在67-69行代码处判断了是否存在xxe漏洞：

```plain
if (attackRequestResponse != null && attackRequestResponse.getResponse() != null
                    && collaboratorInteractions != null
                    && (!collaboratorInteractions.isEmpty())
```

重点：`collaboratorInteractions!=null&&(!collaboratorInteractions.isEmpty())`。

此行代码用于判断是否存在请求。

通过以上三个步骤即实现了一个简单的blind xxe scanner。

梳理一下具体步骤：

-   生成payload
-   替换payload并发起请求
-   判断是否有服务器向payload所处地址发起请求，如果有则代表漏洞存在

通过此接口，我们实现了一个Blind XXE漏洞扫描器的功能，当然同理也可以实现Blind SSRF等各种**Blind**漏洞。

### IBurpCollaboratorInteraction

留坑...没看懂这玩意干啥用的。

### IBurpExtender

[![](assets/1698897659-73c1a2781ffd3790a05f97280dece983.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdl8km4j31zb0u0n2x.jpg)

Burp明确定义了：**所有插件都必须实现这个接口**，就已经说明了这个接口的重要性。

-   registerExtenderCallbacks(IBurpExtenderCallbacks callbacks)

当我们在加载插件时，默认会调用IBurpExtender类下的registerExtenderCallbacks方法，并传递一个IBurpExtenderCallbacks对象，此对象在编写插件时会经常用到。

官方描述该方法的功能：**它注册该IBurpExtenderCallbacks接口的一个实例 ，提供可由扩展调用的方法以执行各种操作。**

IBurpExtender.py：

```plain
class BurpExtender(IBurpExtender,IBurpCollaboratorInteraction):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName('IBurpExtender')
```

上述代码中的callbacks是加载插件时默认传递的，其为IBurpExtenderCallbacks的实例，这个在后续会讲到。

### IBurpExtenderCallbacks

在上面讲到了，加载插件时默认会调用registerExtenderCallbacks方法并传递一个实例，而这个实例就是IBurpExtenderCallbacks对象的实例。

这个接口就非常之牛逼了，其内置了许多成员属性以及方法，在后续我们都会经常用到。

先看看其内置的属性吧：

[![](assets/1698897659-791eab93d2d7e54dde2b17a5a2a9efce.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdm3egrj31qc0segrr.jpg)

```plain
public static final int TOOL_COMPARER   512
public static final int TOOL_DECODER    256
public static final int TOOL_EXTENDER   1024
public static final int TOOL_INTRUDER   32
public static final int TOOL_PROXY  4
public static final int TOOL_REPEATER   64
public static final int TOOL_SCANNER    16
public static final int TOOL_SEQUENCER  128
public static final int TOOL_SPIDER 8
public static final int TOOL_SUITE  1
public static final int TOOL_TARGET 2
```

这一块属性其实都是一些标志位，当我们在处理Burp传递过来的http请求时，需要判断这些请求是在哪里传递的，比如PROXY、SCANNER、TARGET、REPEATER等，简单的来说，这些属性的功能就是用来判断我们想要处理的请求能不能正确的处理，比如我们想要处理的是REPEATER的请求，此时其余无关请求就可以抛掉，比如PROXY的请求，下面以一个代码来演示一下吧。

IBurpExtenderCallbacks.py：

```plain
from burp import IBurpExtender
from burp import IHttpListener

class BurpExtender(IBurpExtender,IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName('IBurpExtenderCallbacks')
        callbacks.registerHttpListener(self)

    def processHttpMessage(self, toolFlag, messageIsRequest, messageinfo):
        if toolFlag == self._callbacks.TOOL_REPEATER :
            print("you are using repeater")
```

此时当我们在repeater中发出请求时，就可以在output下看到如下输出：

[![](assets/1698897659-d8f4ba54bdd8fe63e56cfa36afb12ceb.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdn6qshj30vm0bwwfe.jpg)

接下来开始介绍一下该接口下的方法，其方法有点多，我就不截图了，可以在以下地址中查看：

[Interface IBurpExtenderCallbacks](https://portswigger.net/burp/extender/api/burp/IBurpExtenderCallbacks.html#TOOL_PROXY)

### addScanIssue(IScanIssue issue)

[![](assets/1698897659-5039e6f2fc63dec64774b458fab40db2.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdo0h4hj324g08wjtx.jpg)

此方法要求我们传入IScanIssue的实例化，用于生成自定义的扫描问题，就像是我们在主页中看到的各种漏洞一样，直接演示一下：

```plain
from burp import IBurpExtender
from burp import IHttpListener
from burp import IScanIssue

class CustomIssue(IScanIssue):
    def __init__(self, BasePair, Confidence='Certain', IssueBackground=None, IssueDetail=None, IssueName='Python Scripter generated issue', RemediationBackground=None, RemediationDetail=None, Severity='High'):
        self.HttpMessages=[BasePair]
        self.HttpService=BasePair.getHttpService()
        self.Url=BasePair.getUrl() 
        self.Confidence = Confidence
        self.IssueBackground = IssueBackground 
        self.IssueDetail = IssueDetail
        self.IssueName = IssueName
        self.IssueType = 134217728 
        self.RemediationBackground = RemediationBackground 
        self.RemediationDetail = RemediationDetail 
        self.Severity = Severity 

    def getHttpMessages(self):
        return self.HttpMessages

    def getHttpService(self):
        return self.HttpService

    def getUrl(self):
        return self.Url

    def getConfidence(self):
        return self.Confidence

    def getIssueBackground(self):
        return self.IssueBackground

    def getIssueDetail(self):
        return self.IssueDetail

    def getIssueName(self):
        return self.IssueName

    def getIssueType(self):
        return self.IssueType

    def getRemediationBackground(self):
        return self.RemediationBackground

    def getRemediationDetail(self):
        return self.RemediationDetail

    def getSeverity(self):
        return self.Severity

class BurpExtender(IBurpExtender,IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName('IBurpExtenderCallbacks')
        callbacks.registerHttpListener(self)

    def processHttpMessage(self, toolFlag, messageIsRequest, messageinfo):
        if toolFlag == self._callbacks.TOOL_REPEATER :
            if messageIsRequest: 
                issue = CustomIssue(
                    BasePair=messageinfo,
                    IssueName='HTTP REQUESTS',
                    IssueDetail='addScanIssue Testing',
                    Severity='High',
                    Confidence='Certain'
                )
                self._callbacks.addScanIssue(issue)
        return
```

此时当我们在repeater中发出请求时，主页便会多了一个我们自定义的扫描问题：

[![](assets/1698897659-533162eab6d6805d47ce301254a86f9e.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdr9l59j30zs0u0791.jpg)

漏洞详情以及危害等级都是我们可以自定义的，此方法多用于在测试漏洞时，如果不想添加tab来显示存在漏洞的地址，则使用addScanIssue方法来添加一个自定义问题。

-   addSuiteTab

[![](assets/1698897659-cedbb9ecc9027a778168986a0c530572.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdt3davj310608ct9u.jpg)

该接口实现创建一个自定义选项卡到Burp的选项栏中，默认我们的输出只会在插件的output处输出，如果想输出在界面中，就需要实现此接口。

这方面涉及到java的图形化开发，其实和burp就没多大关系了，不懂也没关系，我们照葫芦画瓢就可以了。

在实现这块之前，请读者先思考一下，我们实现一个图形化的界面有几种目的，在这里我先说一下我的个人观点。

1.实现插件与用户交互  
2.更好的显示漏洞细节

其实实现图形化无非就这两点，所以我们现在来尝试实现这两个功能。

以Burp的官方案例CustomLogger为例：[custom-logger](https://github.com/PortSwigger/custom-logger/blob/master/python/CustomLogger.py)

整个插件实现起来的效果如下：

[![](assets/1698897659-0033d5c8df1de3d8a68829c8592c1a9e.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdu7nenj31fz0u0dtu.jpg)

其实就是展示了我们的数据包是从burp的哪个模块发出去的，并且显示出数据包的详细内容。

如果我们想改改，将此处整成展示漏洞详情的页面，需要怎么改呢？

要实现这个功能，我们需要修改几个地方。

1.将Tool修改为param(即存在漏洞的参数)  
2.只将存在漏洞的页面显示在这里，其他的不显示。

通过全局搜索的方式，我们可以找到定义Tool的地方：

[![](assets/1698897659-127539d761feb117f083654055e90d8d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdvcyxtj30n206sjrz.jpg)

此时我们将TOOL修改为PARAM，就算简单完成了第一步：

```plain
def getColumnName(self, columnIndex):
    if columnIndex == 0:
        return "PARAM"
    if columnIndex == 1:
        return "URL"
    return ""
```

但是我们要注意的是，现在只是修改了其对应的标签名，并没有修改其对应输出的内容，此处输出的内容依旧是toolflag对应的burp组件(如果不知道toolflag是什么，请仔细阅读前文)：

[![](assets/1698897659-4f7b2a5e301c93add7fe3f087b523f9a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdvtq0aj30z60ie3zr.jpg)

如果此处我们想显示为当前url的query，如何做到呢？将想法分割为多个小步，是我实现一个目的的基本办法，所以我们将`显示为当前url的query`分成如下小步来实现：

1.找到显示此处的位置  
2.修改显示内容

第一个问题和第二个问题都很容易解决，我们只需要找到输出此处内容的方法即可：

[![](assets/1698897659-2599023aad9da4408e4b27c11a444e53.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdwdc59j30sg076jsj.jpg)

columnIndex=0对应着PARAM，而columnIndex=1对应着URL，此处稍微修改一下：

```plain
def getValueAt(self, rowIndex, columnIndex):
    logEntry = self._log.get(rowIndex)
    url = logEntry._url.toString()
    if urlparse(url).query =='':
        return
    if columnIndex == 0:
        return urlparse(url).query
    if columnIndex == 1:
        return logEntry._url.toString()
    return ""
```

实现效果：

[![](assets/1698897659-79c8ed01163cf987038391c4dd77cb21.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdxukw2j31fz0u0tox.jpg)

此时虽然只显示出了带有参数的URL，但是却多了很多空白行，这样看起来很丑，所以我们需要找到是哪个方法调用了getValueAt方法，并修改对应点。

通过全局搜索getValueAt这个关键字，我发现并没有任何地方显式的调用了getValueAt方法：

[![](assets/1698897659-a46484b815bf286388d3c0c51557bd73.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxdzk5mfj30ie01mgll.jpg)

那么很明显了，此处就是隐式的调用了getValueAt方法：

[![](assets/1698897659-92197109d7c10e54109677faba69b25e.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe029tfj31nu0bwmzs.jpg)

此处为burp处理请求的方法，而使用者也已经注释的很清楚了，这里就是添加log的地方，由于此处只有一个图形化界面的操作fireTableRowsInserted，所以推测就是此处对表格进行插入的，所以我们只需要在插入之前判断一下url是否带有query即可：

[![](assets/1698897659-fd9971db2bb860142e18283ab5ef1f89.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe2c0ctj31p2078ac4.jpg)

此时重新加载一次插件，就可以看到我们想要的效果了：

[![](assets/1698897659-5ea928d0f4af2880687896421389c53d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe3iqtyj31fz0u0nc8.jpg)

以上只是简单的以一个不懂任何图形化界面的新手来完成这些操作，通过此例，我们可以知道即使不会任何图形化界面的开发也不必要，照葫芦画瓢即可，实在不行直接看官方文档，一样是可以实现我们想实现的功能的。

通过以上案例，我们实现了`更好的显示漏洞细节`，那么如何与用户交互呢，一样的，让我们来照葫芦画瓢。

先思考与用户交互需要什么，无非就是一个输入框，一个确认按钮，程序通过监听按钮来获取用户输入，代入到程序的执行过程中。

以lufe1师傅的xxe检测插件为例：[burp插件LFI scanner第二版](https://lufe1.cn/2018/05/18/Burp%20XXE%20Scanner%20%E6%8F%92%E4%BB%B6/)

先看看图形化实现效果：

[![](assets/1698897659-8afcadb110f3063e14cd769cbc368cde.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe57ed6j314s0hqjta.jpg)

此处只说明图形化相关的配置：

```plain
public class XxeOption implements ITab, ActionListener {
    JPanel jp;
    JTextField jtfId,jtfToken;
    JButton jb;
    JLabel jlId,jlToken;
    private final IBurpExtenderCallbacks callbacks;


    public XxeOption(final IBurpExtenderCallbacks callbacks) {
        this.callbacks = callbacks;


        jp = new JPanel();


        jlId = new JLabel("Identifier:");
        jlToken = new JLabel("API Token:");
        jtfId = new JTextField(10);
        jtfToken = new JTextField(20);


        //设置Id,Token文本框
        File file = new File("xxe.config");
        if(file.exists()){
            String info = ReadConfig();
            if(info.contains("|"))
            {
                jtfId.setText(info.split("\\|")[0]);
                jtfToken.setText(info.split("\\|")[1]);
            }

        }

        jb = new JButton("保存");
        jb.addActionListener(this);

        jp.add(jlId);
        jp.add(jtfId);
        jp.add(jlToken);
        jp.add(jtfToken);
        jp.add(jb);


        callbacks.customizeUiComponent(jtfToken);
        callbacks.addSuiteTab(XxeOption.this);
    }

    //写入配置
    public void WriteConfig(String data)
    {
        try{

            File file = new File("xxe.config");

            //if file doesnt exists, then create it
            if(!file.exists()){
                file.createNewFile();
            }

            //true = append file
            FileWriter fileWritter = new FileWriter(file.getName(),false);
            BufferedWriter bufferWritter = new BufferedWriter(fileWritter);
            bufferWritter.write(data);
            bufferWritter.close();

        }catch(IOException e){

            e.printStackTrace();
        }

    }

    //读取配置
    public String ReadConfig()
    {
        StringBuilder result = new StringBuilder();
        try{
            BufferedReader br = new BufferedReader(new FileReader("xxe.config"));//构造一个BufferedReader类来读取文件
            String s = null;
            while((s = br.readLine())!=null){//使用readLine方法，一次读一行
                result.append(s);
            }
            br.close();
        }catch(Exception e){
            e.printStackTrace();
        }
        return result.toString();
    }



    @Override
    public String getTabCaption() {
        return "XXEScanner";
    }

    @Override
    public Component getUiComponent() {
        return jp;
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        if((jtfId.getText() != "") && (jtfToken.getText() != ""))
        {
            String path = "";
            File directory  = new File(".");
            try {
                path = directory.getCanonicalPath() + "\\xxe.config";
            } catch (IOException e1) {
                e1.printStackTrace();
            }
            WriteConfig(jtfId.getText() + "|" +jtfToken.getText());
        }else {
            JOptionPane.showMessageDialog(jp, "ID 和 Token不能为空", "提示",JOptionPane.WARNING_MESSAGE);
        }


    }
}
```

此处实现了两个接口：ITab, ActionListener

重点在XxeOption这个方法：

```plain
public XxeOption(final IBurpExtenderCallbacks callbacks) {
        this.callbacks = callbacks;


        jp = new JPanel();


        jlId = new JLabel("Identifier:");
        jlToken = new JLabel("API Token:");
        jtfId = new JTextField(10);
        jtfToken = new JTextField(20);


        //设置Id,Token文本框
        File file = new File("xxe.config");
        if(file.exists()){
            String info = ReadConfig();
            if(info.contains("|"))
            {
                jtfId.setText(info.split("\\|")[0]);
                jtfToken.setText(info.split("\\|")[1]);
            }

        }

        jb = new JButton("保存");
        jb.addActionListener(this);

        jp.add(jlId);
        jp.add(jtfId);
        jp.add(jlToken);
        jp.add(jtfToken);
        jp.add(jb);


        callbacks.customizeUiComponent(jtfToken);
        callbacks.addSuiteTab(XxeOption.this);
    }

    //写入配置
    public void WriteConfig(String data)
    {
        try{

            File file = new File("xxe.config");

            //if file doesnt exists, then create it
            if(!file.exists()){
                file.createNewFile();
            }

            //true = append file
            FileWriter fileWritter = new FileWriter(file.getName(),false);
            BufferedWriter bufferWritter = new BufferedWriter(fileWritter);
            bufferWritter.write(data);
            bufferWritter.close();

        }catch(IOException e){

            e.printStackTrace();
        }

    }
```

先是new了一个JPanel类，24-27行设置了文本内容以及文本框长度：

```plain
jlId = new JLabel("Identifier:");
jlToken = new JLabel("API Token:");
jtfId = new JTextField(10);
jtfToken = new JTextField(20);
```

JLabel传入一个字符串代表创建一个标签，标签的名称为传入的字符串，JTextField(10)代表长度为10的文本框。

31-40行用于判断有无历史配置文件，如果有则自动载入配置文件中的内容到文本框中：

```plain
File file = new File("xxe.config");
if(file.exists()){
    String info = ReadConfig();
    if(info.contains("|"))
    {
        jtfId.setText(info.split("\\|")[0]);
        jtfToken.setText(info.split("\\|")[1]);
    }

}
```

42-43行用于创建一个按钮，并监听此按钮的事件：

```plain
jb = new JButton("保存");
jb.addActionListener(this);
```

当点击此按钮后，会触发actionPerformed方法，在110-128行重写了此方法：

```plain
@Override
    public void actionPerformed(ActionEvent e) {
        if((jtfId.getText() != "") && (jtfToken.getText() != ""))
        {
            String path = "";
            File directory  = new File(".");
            try {
                path = directory.getCanonicalPath() + "\\xxe.config";
            } catch (IOException e1) {
                e1.printStackTrace();
            }
            WriteConfig(jtfId.getText() + "|" +jtfToken.getText());
        }else {
            JOptionPane.showMessageDialog(jp, "ID 和 Token不能为空", "提示",JOptionPane.WARNING_MESSAGE);
        }


    }
}
```

45-47行添加了组件：

```plain
jp.add(jlId);
jp.add(jtfId);
jp.add(jlToken);
jp.add(jtfToken);
jp.add(jb);
```

53行代码在burp中创建了一个自定义选项卡：

```plain
callbacks.addSuiteTab(XxeOption.this);
```

以上代码实现了所有图形化的界面，那么我们在插件代码中如何与用户交互？

来到插件入口处：[BurpExtender.java](https://github.com/lufeirider/Project/blob/bccb10837f4075508c4af616e2d619411b64078c/LXXEScanner/src/burp/BurpExtender.java)

在43行代码中实例化了XxeOption这个类：

```plain
xxeOption = new XxeOption(callbacks);
```

并在被动扫描插件处调用了他：

```plain
byte[] xxePayload = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                "<!DOCTYPE root [\n" +
                "<!ENTITY % remote SYSTEM \"http://" + xxeOption.jtfId.getText() + "/" + flag + "\">\n" +
                "%remote;]>\n" +
                "<root/>").getBytes();
```

以上代码实现了与用户传递进行交互的功能。

-   removeSuiteTab

[![](assets/1698897659-922c225409cbf0a9cd356841c5b79670.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe5lizsj314m08at9y.jpg)

从字面意思理解，addSuiterTab用于添加自定义选项卡，那么removeSuiteTab就是用于删除自定义选项卡了，这功能基本用不到，不作讲解。

大概到用途就是给一个按钮，比如一个关闭选项卡的按钮，点击后触发removeSuiteTab方法并传日当前的ITab实例化对象。

-   customizeUiComponent

这个方法不需要实现，可以用ITab.getUiComponent来代替，没怎么用过emmm。

-   addToSiteMap

[![](assets/1698897659-36fc5d4a7865786f40725491a95102c5.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe6ly0sj31zq08agnb.jpg)

简而言之，此方法就是用于将某个数据包添加到burp的sitemap中的。

参考代码：

```plain
from burp import IBurpExtender
from burp import IHttpListener
from burp import IBurpExtenderCallbacks

class BurpExtender(IBurpExtender, IHttpListener, IBurpExtenderCallbacks):

    def registerExtenderCallbacks( self, callbacks):
        self._helpers = callbacks.getHelpers()

        self._callbacks = callbacks

        # set our extension name
        callbacks.setExtensionName("Repeater to Sitemap")
        callbacks.registerHttpListener(self)
        return

    def  processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if toolFlag == 64: #Repeater
            if messageIsRequest == False:
                self._callbacks.addToSiteMap(messageInfo)
```

上述代码的功能是将repeater中的数据包添加到sitemap中：

[![](assets/1698897659-1e2ae5db4ce06aa1c64527487030703f.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe77i5ij31fz0u0qhc.jpg)

当我们在repeater中发送一个数据包后，就可以在sitemap中看到：

[![](assets/1698897659-de97786bc44007176933cc970ec104e0.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe7kzt8j31fz0u0n3g.jpg)

-   applyMarkers

[![](assets/1698897659-c230e2ad3c83eb8dd8a209342c095522.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe85cu2j323q0hk0z0.jpg)

这个方法是用来标记返回包中敏感信息的，一般搭配IScanIssue使用。

给个demo来理解一下：

```plain
from burp import IBurpExtender
from burp import IHttpListener
from burp import IBurpExtenderCallbacks
from burp import IScanIssue,IScannerCheck,IScannerInsertionPoint
from array import array

class BurpExtender(IBurpExtender, IHttpListener, IBurpExtenderCallbacks,IScannerCheck,IScannerInsertionPoint):

    def registerExtenderCallbacks( self, callbacks):
        self._helpers = callbacks.getHelpers()

        self._callbacks = callbacks

        # set our extension name
        callbacks.setExtensionName("Repeater to Sitemap")
        callbacks.registerScannerCheck(self)
        return

    def getMatches(self, response, match):
      '''This finds our pattern match in the request/response and returns an int array'''
      start = 0
      count = 0
      matches = [array('i')]
      while start < len(response):
        start=self._helpers.indexOf(response, match, True, start, len(response))
        if start == -1:
          break
        try:
          matches[count]
        except:
          matches.append(array('i'))
        matches[count].append(start)
        matches[count].append(start+len(match))
        start += len(match)
        count += 1

      return matches

    def doPassiveScan(self, baseRequestResponse):
        PATTERN="phpinfo"
        ISSUE_NAME="phpinfo found in HTTP Response"
        ISSUE_DETAIL="HTTP Response contains this pattern: " + PATTERN
        ISSUE_BACKGROUND="The web site has exposed sensitive information"
        REMEDIATION_BACKGROUND="Sensitive information"
        REMEDIATION_DETAIL="Ensure sensitive information is only shown to authorized users"
        SEVERITY="Information"
        CONFIDENCE="Certain"
        issue = list()
        match = self.getMatches(baseRequestResponse.getResponse(), PATTERN)
        if len(match) > 0:
            httpmsgs = [self._callbacks.applyMarkers(baseRequestResponse,None,match)]
            issue.append(ScanIssue(baseRequestResponse.getHttpService(), self._helpers.analyzeRequest(baseRequestResponse).getUrl(), httpmsgs, ISSUE_NAME, ISSUE_DETAIL, SEVERITY, CONFIDENCE, REMEDIATION_DETAIL, ISSUE_BACKGROUND, REMEDIATION_BACKGROUND))
        return issue
    def doActiveScan(self, baseRequestResponse, insertionPoint):
        pass

class ScanIssue(IScanIssue):
  '''This is our custom IScanIssue class implementation.'''
  def __init__(self, httpService, url, httpMessages, issueName, issueDetail, severity, confidence, remediationDetail, issueBackground, remediationBackground):
      self._issueName = issueName
      self._httpService = httpService
      self._url = url
      self._httpMessages = httpMessages
      self._issueDetail = issueDetail
      self._severity = severity
      self._confidence = confidence
      self._remediationDetail = remediationDetail
      self._issueBackground = issueBackground
      self._remediationBackground = remediationBackground


  def getConfidence(self):
      return self._confidence

  def getHttpMessages(self):
      return self._httpMessages
      #return None

  def getHttpService(self):
      return self._httpService

  def getIssueBackground(self):
      return self._issueBackground

  def getIssueDetail(self):
      return self._issueDetail

  def getIssueName(self):
      return self._issueName

  def getIssueType(self):
      return 0

  def getRemediationBackground(self):
      return self._remediationBackground

  def getRemediationDetail(self):
      return self._remediationDetail

  def getSeverity(self):
      return self._severity

  def getUrl(self):
      return self._url

  def getHost(self):
      return 'localhost'

  def getPort(self):
      return int(80)
```

参考：[CustomScanner.py](https://github.com/luxcupitor/burpsuite-extensions/blob/505f0821d0ac215e57ba8cebf4b674fdc2d203c6/CustomScanner.py#L154)

该插件的功能是当返回包中含有phpinfo这个字符串时，添加一个Issue并高亮返回包中的phpinfo字符串，效果如下：

[![](assets/1698897659-c997348cc7880d0e25e8ebbe670c88d9.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe8lyqnj30wm0u00zx.jpg)

当然也可以高亮request中的字符串，参考：

[![](assets/1698897659-672a77fb768f52e145b24264b65b17fb.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxe9potrj31dk0hmdli.jpg)

用法：

```plain
self._callbacks.applyMarkers(baseRequestResponse,match,None)
```

当然也可以两个都高亮：

```plain
self._callbacks.applyMarkers(baseRequestResponse,match1,match2)
```

-   createBurpCollaboratorClientContext

[![](assets/1698897659-e87c6fae74873e2f203492ef10c885c6.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxead6k6j31yc088wgs.jpg)

这个方法之前介绍过了，用来创建IBurpCollaboratorClientContext实例并生成payload的。

-   createMessageEditor

[![](assets/1698897659-332b47d3ec307a8d26fbdc1fa7cbd4c3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxebg0y3j32420emwj6.jpg)

此方法返回实现了IMessageEditor接口的对象，方便在自己插件的UI中使用，具体使用方法参考上面的图形化界面相关(addSuiteTab)。

-   createTextEditor

[![](assets/1698897659-f942b5b146fa1804d6924d5f9f7b055d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxec75rmj31dy08aabg.jpg)

和上边那个作用是一样的，只是返回的对象实现的接口不同，所以可调用的方法也有几个不同。

参考：[HelloWorldBurpTabExtender.py](https://github.com/cvantet/basic-burp-jython-plugin/blob/143259462618dae954fefb88fc984d9078df7ef1/HelloWorldBurpTabExtender.py)

-   customizeUiComponent

[![](assets/1698897659-1dcba500f621d3bfbb7dbb8c58c9e3f3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxecostzj3228088myx.jpg)

我的理解是这个插件是用来对自定义组件传入其他任意的自定义子组件，也是用来对UI进行操作的。

相当于一个input标签里还可以定义name属性value属性等这个意思。

-   doActiveScan

[![](assets/1698897659-cea74a630c13f53a7a729e4e4a85549b.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxedbcpqj314o0h0q5q.jpg)

此方法用于对传入的数据包进行主动扫描，并返回当前正在扫描的队列。

参考：[AutoScanWithBurp.py](https://github.com/rasinfosec/Burp_Automator/blob/7fbcc7af8b18123e49c07bb5269c61c2e40a8c8a/AutoScanWithBurp.py)

该插件的功能是将爬虫的数据包丢到主动扫描模块进行扫描。

-   doPassiveScan

[![](assets/1698897659-a8dd2fd338f7721ba79d13b2f62f4ca0.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxefit72j31bo0gwwhe.jpg)

没怎么用过这个方法，不太了解，大概看了一些网上的demo，推测是使用burp来进行转发，将burp代理的流量转发到扫描器上进行被动扫描。

-   excludeFromScope

[![](assets/1698897659-16b49e2b472ec52b604b259258652489.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxehejo5j318c088gmt.jpg)

从burp的scope中排除指定的url。

-   exitSuite

[![](assets/1698897659-139df5458c2096983b89d1b1129cde6a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxek9jqyj31j008875q.jpg)

以编程形式关闭burp，传入参数为0和1，代表用户是否选择关闭burp的布尔标志。

-   generateScanReport

[![](assets/1698897659-eef1069054079c7cf120fe00e967d209.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxel3kbij31vk0c6ju4.jpg)

将issues以某种格式导出到某个文件，issues是个列表，里边可以存放多个issue。

此方法一般用于导出漏洞扫描报告或问题集合。

-   getCookieJarContents

[![](assets/1698897659-8b9492e6e31ad8a4481ea0a5fb4f8852.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxeljaoaj321o0880ur.jpg)

官方说明是为了处理会话异常，没找到实用的demo，本地测试了一下：

```plain
from burp import IBurpExtender,ICookie




class BurpExtender(IBurpExtender,ICookie):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        cookies = self.callbacks.getCookieJarContents()
        for cookie in cookies:
            print(cookie.value)
```

[![](assets/1698897659-ece21c72b670d2cf034e4479c8f78e15.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxelzjq4j30ms05074j.jpg)

当然也可以获取cookie所在域，使用cookie.domain即可。

-   getBurpVersion

[![](assets/1698897659-779e31bcba4e381fba32352716287dbe.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxemkkyzj31z4084gnk.jpg)

此方法用于返回Burp相关的信息集合：

[![](assets/1698897659-91870d9f8b1101f56bc780d282f025a3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxeni96vj31a00gagmm.jpg)

-   getCommandLineArguments

[![](assets/1698897659-9e426967ed877d2632fa0588f05397e1.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxeof2xfj31co086abc.jpg)

此方法返回启动burp时使用的参数列表。

这玩意基本不会用。。

-   getContextMenuFactories

[![](assets/1698897659-37c744ebbfb584588dfc9866d8cd6b21.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxeousk7j319m088q4h.jpg)

没用过，不予以介绍。

-   getExtensionFilename

[![](assets/1698897659-d72416e0f21667312a1c7150907f8369.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxepapmbj31c808agmw.jpg)

此方法返回插件所处的绝对路径：

```plain
from burp import IBurpExtender,ICookie




class BurpExtender(IBurpExtender,ICookie):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        print(self.callbacks.getExtensionFilename())
```

[![](assets/1698897659-15dcb95338c2d9ef60fea513dd5e331e.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxeptdt1j31gs0cg0to.jpg)

-   getExtensionStateListeners

[![](assets/1698897659-aac563b8e4e320793a323aacd15c02a7.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxeqao4oj314g086abh.jpg)

此方法返回该拓展注册的监听器，什么是监听器一会会讲到，比如上文有一个`callbacks.registerHttpListener`，这就注册了一个请求&响应监听器。

-   getHelpers

[![](assets/1698897659-9d6480cfb0136fa86a1292355452fbd7.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxet40e7j31mg086gn4.jpg)

此方法用于获取IExtensionHelpers对象的实例，这个实例很有用，之后对数据包的很多处理都会用到他。

具体的IExtensionHelpers对象可使用的方法可以看这里：[Interface IExtensionHelpers](https://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html)。

-   getHttpListeners

[![](assets/1698897659-96f6ad54fc142bb8df60fea0018c1817.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxetz3duj30x8084ab7.jpg)

此方法返回当前注册的HTTP监听器列表。

示例代码；

```plain
from burp import IBurpExtender,ICookie,IScannerCheck,IHttpListener




class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerScannerCheck(self)
        callbacks.registerHttpListener(self)
        print(callbacks.getHttpListeners())

    def processHttpMessage(self, toolFlag, messageIsRequest, messageinfo):
        if toolFlag == 4 :
            if messageIsRequest:
                return

    def doActiveScan(self, baseRequestResponse, insertionPoint):
        pass

    def doPassiveScan(self, baseRequestResponse):
        pass
```

输出：

[![](assets/1698897659-5c5030d9ca82dbb8072fdb3aa5f4551b.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxexe44uj315a0j6jsm.jpg)

PS：以下几个方法都是一个意思，不再重复叙述。

[![](assets/1698897659-5e2d85d772cc103d1653f17b66951fdc.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxezaq9lj317w088gnz.jpg)

[![](assets/1698897659-b81cb6ef7801234268c7a2524ba0496f.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxezmgvsj31340acq5s.jpg)

添加上一个getProxyListeners()方法。

-   getProxyHistory

[![](assets/1698897659-837aa9e799970fd0273d1584a9a2f5d2.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxf12dbgj31eg088dgy.jpg)

此方法返回history中的数据包列表，返回的是IHttpRequestResponse的实例，可调用其中的方法。

-   getScanIssues

[![](assets/1698897659-b58b6437b3b420fd91af0a9dcb05c288.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxf21puej323y0bmtba.jpg)

此方法返回某个url的issus列表，列表中的每一项为IScanIssue的实例，可调用其中的方法。

示例：

```plain
class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerScannerCheck(self)
        callbacks.registerHttpListener(self)
        issue_list = callbacks.getScanIssues('http://ctf.localhost.com')
        for issue in issue_list:
            print(issue.getIssueName())
```

输出：

[![](assets/1698897659-0cfcdb3dbcb426046b3fd0bbcb222ff0.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxf2zyphj31ig0gmabj.jpg)

其中的issueName是在issue列表中获得的：

[![](assets/1698897659-935b8d12e36d65d4536219e4cbbc9814.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxf3tmtvj313w0bm0tz.jpg)

-   getSiteMap

[![](assets/1698897659-07d9f16380bc831687a52ebc28e9d772.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxf5a3jjj32440bimzq.jpg)

此方法用于从sitemap中提取指定url的sitemap子集，官方描述是可以匹配以某个特定字符开头的站点，意思就是可以用正则这样子。

返回是IHttpRequestResponse的实例，可以调用其中的方法。

示例：

```plain
class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerScannerCheck(self)
        callbacks.registerHttpListener(self)
        site_requests = callbacks.getSiteMap("http://ctf.localhost.com")
        for request in site_requests:
            print(request.getHttpService())
```

输出：

[![](assets/1698897659-88bba3a859790007b42aaced4ed0bbd0.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxf6c7shj316y0bqabh.jpg)

-   四个不懂用的方法

[![](assets/1698897659-94fd015fe2fc590ae2b2840549bf5375.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxf9ym3cj31du048t9s.jpg)

[![](assets/1698897659-4f76931d183cc03dd1838622d94ce4f7.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfauv3ij31z604cabu.jpg)

这四个方法是我不知道干啥用的，不予介绍。

-   getToolName

[![](assets/1698897659-0c7c93c7843214cee6d93268369c6b11.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfbtnnwj31dw0aqq4u.jpg)

此方法返回toolflag对应的toolname，如果不知道toolflag是啥的回头仔细看看就知道了。

示例：

```plain
from burp import IBurpExtender,ICookie,IScannerCheck,IHttpListener




class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerScannerCheck(self)
        callbacks.registerHttpListener(self)
        print(callbacks.getToolName(4))
```

输出：

[![](assets/1698897659-a9e81ae3a49247b5d98664ae68bd43ac.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfcperzj314a07sq3n.jpg)

-   includeInScope

[![](assets/1698897659-43d9700c6ceafc2a505137f9230ded74.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfdnm7gj323w084wft.jpg)

我的理解是将某个匹配规则添加进scope中。

-   isExtensionBapp

[![](assets/1698897659-50f9907f756caf41bd75c45e6dbf71ed.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfer47dj31is08675m.jpg)

判断当前插件是否已经上架到burp的bapp store里了，如果上架了则返回true，反之返回false。

-   isInScope

[![](assets/1698897659-398d7e8c45d3abac528c84d179fbf0bf.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxffplh8j31ci0awmyo.jpg)

查询指定的url规则是否在scope中，一般和includeInScope配套使用。

-   issueAlert

[![](assets/1698897659-dfe371b19672e3553ebebbcc4ab804fa.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfgfyo4j31440823zm.jpg)

用于在burp的选项卡中输出消息。

示例：

```plain
from burp import IBurpExtender,ICookie,IScannerCheck,IHttpListener




class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerScannerCheck(self)
        callbacks.registerHttpListener(self)
        callbacks.issueAlert("test")
```

输出：

[![](assets/1698897659-6bfb0903766f14e0de34bf26d2f24556.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfgzmrdj313q0eidhy.jpg)

-   makeHttpRequest

[![](assets/1698897659-a89f48ac214c101fe396bc3f25542c5f.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfhdy3kj316o04a0u5.jpg)

这个方法还挺常用的，简单一点来说就是修改数据包了之后本地重新再发一次，一般用在漏洞检测这块。

从上面第一个图也看到了，这个方法有两种用法：

[![](assets/1698897659-17204bf9fac4a942776f23fefc13972c.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfjegy6j31dt0u0q8m.jpg)

两种方法都是用来重新发包的，只是返回值不同，第一种返回的是IHttpRequestResponse的实例，可以使用getResponse()方法直接获取响应结果，而第二种返回的数据类型为bytes，一般使用该方法获取响应结果：

```plain
againRes = self._callbacks.makeHttpRequest(host, port, ishttps, againReq)
link = againReqHeaders[0].split(' ')[1]
host = againReqHeaders[1].split(' ')[1]
analyzedrep = self._helpers.analyzeResponse(againRes)
againResBodys = againRes[analyzedrep.getBodyOffset():].tostring()
```

这个方法是很重要的，以后会经常用到，不懂的可以多去搜下demo。

-   printError

[![](assets/1698897659-23139466e8b83456c328589ed987d209.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfjqymnj317s088759.jpg)

不怎么用这个方法，感觉就和抛出一个自定义错误一样的。

示例：

```plain
from burp import IBurpExtender,ICookie,IScannerCheck,IHttpListener




class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerScannerCheck(self)
        callbacks.registerHttpListener(self)
        callbacks.printError("123")
```

输出：

[![](assets/1698897659-af2b9e148669437e62ea7ffb03d0d287.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfkbdpuj312w0r8gnl.jpg)

-   printOutput

[![](assets/1698897659-e8c07b6dbba79eb5b40ac69f2cb547fe.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfknf20j30tw08cdgr.jpg)

emm，感觉这个方法就是为了代替使用print？

示例：

```plain
class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerScannerCheck(self)
        callbacks.registerHttpListener(self)
        callbacks.printOutput("123")
```

输出：

[![](assets/1698897659-fa5da05a6e26100be45ae76b4b3b11f9.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfl4twoj31hk0og0u5.jpg)

-   一系列register

[![](assets/1698897659-9c7dfcaefee6600aff1c710f62a23c43.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfnin1cj318s0rugve.jpg)

这些registerxxx的方法，我的个人理解就是你注册了某个类，你就可以重写某个类的方法，这些类的方法在使用burp进行某些特定操作时会自动调用。

以registerHttpListener为例：

[![](assets/1698897659-4b5c66778ead067d5b057c0acae0e316.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfpu67dj3200086jt9.jpg)

从上图中可以看出，其注册的实际是IHttpListener这个接口，让我们来看看此接口下的方法：

[![](assets/1698897659-a2c8f48903143d09e8bc5fedfcd7c409.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfrdw3wj327y0j00ww.jpg)

官方描述是，任何Burp收到或发出的请求以及响应都将触发此方法，所以这个方法也同样可以用来当漏扫，只不过一般没人这么干，因为只有此方法执行完后，浏览器的页面才会返回结果。

示例：

```plain
from burp import IBurpExtender,ICookie,IScannerCheck,IHttpListener




class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerHttpListener(self)


    def processHttpMessage(self, toolFlag, messageIsRequest, messageinfo):
        if toolFlag == 4 :
            if messageIsRequest:
                return
            else:
                print("you are loading:  " + messageinfo.getHttpService().toString())
```

此时当我们用burp代理发出请求时，就会自动调用该方法，输出如下：

[![](assets/1698897659-48c7a0cac9d6dae1ca98603641f301dc.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfs5un6j30y40ik0uf.jpg)

-   一系列remove

[![](assets/1698897659-629219a0552a9a41d2f42acd81657c99.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxftp35yj31ty0r0n85.jpg)

这些方法对应着上面的register，即删除插件所注册的某些接口。

字面翻译就可以啦。

-   saveBuffersToTempFiles

将IHttpRequestResponse对象的请求以及响应存储到临时文件中，确保其不存在于内存中。emmm不知道这个的作用是什么。

返回实现了IHttpRequestResponse接口的对象，我们可以调用如下方法：

[![](assets/1698897659-ae78c0e2abd0495b82c21f17e0dc559b.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfwkprzj326c0cymzj.jpg)

-   saveConfigAsJson&&loadConfigFromJson

[![](assets/1698897659-44d8eb1b462e9e1cd3ea1bbb398c0759.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxfxbt98j32400m0teh.jpg)

官方描述如上，我也不清楚是怎么使用的，不予介绍。

-   一系列send

[![](assets/1698897659-694130779dbacfaa929b1cceb14cb99f.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxg0nsruj321q0a6djy.jpg)

字面意思，就是把某个数据包发送到burp的某个模块里，这里以sendToRepeater为例：

```plain
from burp import IBurpExtender,ICookie,IScannerCheck,IHttpListener




class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
        callbacks.registerHttpListener(self)


    def processHttpMessage(self, toolFlag, messageIsRequest, messageinfo):
        if messageinfo.getHttpService().getProtocol() == 'https://':
            is_https = 1
        else:
            is_https = 0
        headers = list(self.helpers.analyzeRequest(messageinfo).getHeaders())
        newMessage = self.helpers.buildHttpMessage(headers, None)
        self.callbacks.sendToRepeater(messageinfo.getHttpService().getHost(),messageinfo.getHttpService().getPort(),is_https,newMessage,None)
```

此时当burp代理发出请求或收到响应时，都会调用processHttpMessage，我在里边实现了一个简单的sendToRepeater方法，此时可以看到我的repeater里有巨多请求：

[![](assets/1698897659-00ddbfec57a6f345a178e4f3df59459a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxg4jirgj31fz0u046s.jpg)

感觉这几个sendtoxxx的方法都需要配合button这样的监听事件来实现。

-   setExtensionName

[![](assets/1698897659-f3b9bd1d6236d2974ef0fc2b7ff12706.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxg62bsdj31c80840tz.jpg)

顾名思义，就是用来设置插件名称的。

示例：

```plain
class BurpExtender(IBurpExtender,ICookie,IScannerCheck,IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('IBurp')
```

此时插件的名称会展示在extender-extensions中：

[![](assets/1698897659-e8e410a8a45a2e4ef6a88b7059a17db3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxg6qywpj30x400yjrb.jpg)

-   setProxyInterceptionEnabled

[![](assets/1698897659-eda56c78f706bb3873f90b570a71cfe6.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxg76w6rj316a08aabf.jpg)

没用过，不清楚如何使用，本地测试了一下也没搞明白。

-   unloadExtension

[![](assets/1698897659-177ef7c1f7b7f39a5ddd8683d02fbbec.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxg7m9fqj316204wjry.jpg)

此方法用于从拓展中去除当前使用的拓展，即不使用该拓展，也是要配合button使用才有意义的。

-   updateCookieJar

[![](assets/1698897659-abca24f0fdc9ea1536d71007316a008a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxg88qoij323y0900vm.jpg)

没使用过。

- - -

以上即为IBurpExtenderCallbacks接口中实现的所有方法，在写这篇文章的时候，有的方法我也没使用过，写起来很费事，不过如果真的想了解burp插件的一套调用流程，这个接口是你必须要认真去阅读的。

参考：[Interface IBurpExtenderCallbacks](https://portswigger.net/burp/extender/api/burp/IBurpExtenderCallbacks.html#updateCookieJar%28burp.ICookie%29)

### IContextMenuFactory

[![](assets/1698897659-9aba6ba8e021c1502ace41d527f34bf7.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx9z07x4j31xi0u0gt9.jpg)

此接口由`IBurpExtenderCallbacks.registerContextMenuFactory()`注册，其需要实现的方法只有一个，返回的是IContextMenuInvocation的实例，可以调用其中的方法。

这个接口是用来实现菜单与一系列操作联合起来的，具体看个demo：

示例：

```plain
class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self,invocation):
        menu= []
        menu.append(JMenuItem("Test Menu", None, actionPerformed=self.testmenu()))
        print(invocation.getSelectedMessages())
        return menu

    def testmenu(self):
        return 1
```

此时我在Burp的上下文菜单中创建了一个名为Test Menu的菜单，我重写他的 createMenuItems方法，此时在Burp的任意地方调用上下文菜单都会触发此方法。

实例效果：

[![](assets/1698897659-2c0b90258d4979c779de97267cfa873a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx9zcwbhj30ny0m4dib.jpg)

可以看到这里出现了一个我们自定义的菜单选项，一般这个选项是要配合其他的操作来进行的，下面以sahildhar师傅的shodan信息探测插件来讲一下这个api要怎么用。

项目地址：[shodanapi.py](https://github.com/sahildhar/BurpExtenderPractise/blob/master/shodanapi.py)

在23行注册了此接口：`self.callbacks.registerContextMenuFactory(self)`

26-29行重写了此方法：

```plain
def createMenuItems(self,invocation):
        menu_list = []
        menu_list.append(JMenuItem("Scan with Shodan",None,actionPerformed= lambda x, inv=invocation:self.startThreaded(self.start_scan,inv)))
        return menu_list
```

此时创建了一个菜单选项名为Scan with Shodan，而actionPerformed是用来指定点击了这个选项后会触发的方法。

此时点击这个菜单选项后会触发start\_scan方法并传递invocation为参数进去。

35-48行是核心代码，也就是从shodan获取信息的方法：

```plain
def start_scan(self,invocation):
        http_traffic = invocation.getSelectedMessages()
        if len(http_traffic) !=0:
                service = http_traffic[0].getHttpService()
                hostname = service.getHost()
                ip = socket.gethostbyname(hostname)
                req = urllib2.Request("https://api.shodan.io/shodan/host/"+ip+"?key=<api_key>")
                response = json.loads(urllib2.urlopen(req).read())
                print "This report is last updated on  %s" % str(response['last_update'])
                print "IP - %s" %str(response['ip_str'])
                print "ISP - %s" %str(response['isp'])
                print "City - %s" %str(response['city'])
                print "Possible Vulns - %s" %str(response['vulns'])
                print "Open Ports -  %s" % str(response['ports'])
```

我们知道invocation是IContextMenuInvocation的实例，所以我们可以调用其中的任何方法，让我们看看有哪些方法：

[![](assets/1698897659-cbc1e02ac4b976b6e24587df4feaa8a3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa02jtxj325u0iwn2l.jpg)

在代码中作者调用了getSelectedMessages方法，此方法返回调用上下文菜单时用户所选择的请求或响应的详细数据包，返回IHttpRequestResponse对象的实例。

有了IHttpRequestResponse的实例，我们就可以调用其中的方法，作者只是调用了getHttpService这个方法。

后面一系列操作就是取hostname，取ip，传给shodan，解析请求结果了。

如果细心看过前面内容的同学，就可以知道burp的菜单实际上都是可以用此方法进行创建的：

[![](assets/1698897659-981eaaa4ee76d4bcbe7303a7f947a8ae.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa1deshj30o40m4q57.jpg)

下面来演示一个Send to Repeater beta。

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self,invocation):
        menu_list = ArrayList()
        inv = invocation.getSelectedMessages()
        self.inv = inv
        menu_list.add(JMenuItem("send to repeater beta", actionPerformed=self.sendtorepeater))
        return menu_list

    def sendtorepeater(self,event):

        inv = self.inv[0]
        service = inv.getHttpService()
        host = service.getHost()
        port = service.getPort()
        protocol = service.getProtocol()
        if protocol == 'https':
            is_https = 1
        else:
            is_https = 0
        req = inv.getRequest()
        self._callbacks.sendToRepeater(host,port,is_https,req,None)
```

我首先注册了该接口并重写了createMenuItems方法，通过JMenuItem实现了一个按钮，当用户在按钮处释放光标后会触发actionPerformed指定的方法并传递给其event参数。

这个参数不需要管，我们只需要处理invocation就好，我通过getSelectedMessages来获取菜单所处的请求以及响应的详细信息，并通过数组取值的方式仅取出请求。后续实际上就是在利用IHttpRequestResponse接口以及IHttpService接口来获取一些我们需要的参数而已了。

最后使用`self._callbacks.sendToRepeater`方法将请求传递到repeater中。

实现效果：

[![](assets/1698897659-b603de26cc4c1c8cea1929279acd62aa.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa2bt6yj327y0n40zv.jpg)

点击后repeater就多了一项：

[![](assets/1698897659-7f6ddfeccba9e18e28e846593406c516.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa3dshyj31y70u0jw7.jpg)

可以点击go来获取响应数据包：

[![](assets/1698897659-c7a01e5c58e1328146db793ca2e4d015.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa46n8jj313o0tmjvg.jpg)

### IContextMenuInvocation

这个接口在上文中其实已经介绍过了，当Burp在调用IContextMenuInvocation接口时，就会使用此到此接口，我们上文中一直用的invocation，其实就是IContextMenuInvocation的实例。

在这里我会详细的解释这个接口的每个参数是如何作用的。

首先看看此接口中定义的一些属性：

[![](assets/1698897659-7918ddce9a555ee479f6deac6aba69cb.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa55oshj325m0taajc.jpg)

emmm其实这些都是类似toolflag一样的标志位，没什么好讲的，一般用于判断你想处理的请求是否是你想处理的请求。

这么说可能有点抽象，比如你想处理的是proxy的请求，却处理了response的请求，差不多就是这么个意思。

接着看看他的方法吧：

[![](assets/1698897659-6f3fa087ab0aa39362b5f608290e05f3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa5yimnj325o0iu79p.jpg)

-   getInputEvent

[![](assets/1698897659-078a48ad7861cbfc5737a84207489a3c.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa6hw1sj3244084abk.jpg)

这个一般不会用到，用来获取鼠标事件的一些详细信息，打印出来看看就知道了。

示例：

```plain
class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self,invocation):
        menu_list = ArrayList()
        print(invocation.getInputEvent())
```

输出：

[![](assets/1698897659-57edfc64e3695d092817b93c92c1c32f.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa6ulztj327w0fcjub.jpg)

-   getInvocationContext

[![](assets/1698897659-2524a40d207a42573890e4cc94911bd3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa7ag6wj323y082jsv.jpg)

用来获取调用该菜单时的上下文，给个demo你就清楚啦：

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self,invocation):
        menu_list = ArrayList()
        print(invocation.getInvocationContext())
```

此时如果我在proxy\_history中调用，打印出来的结果是6，其值实际上是对应着这里的：

[![](assets/1698897659-3a151f8a50aac6b23c47dbfdd30695c8.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa88agcj325u010wep.jpg)

同样的，也是相当于toolflag一样的作用。

-   getToolFlag

[![](assets/1698897659-98009bc1d152e262da79b92df216db2d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxa998wlj323w086q4j.jpg)

顾名思义，返回的是调用菜单时所处的工具的toolflag。

demo：

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList


class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self,invocation):
        menu_list = ArrayList()
        print(invocation.getToolFlag())
```

如果我在proxy\_history中调用，打印出来的结果是4，对应着这块：

[![](assets/1698897659-b379c09617bc6df22394349f60a29423.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaa9p88j325u016t8t.jpg)

-   getSelectedIssues

[![](assets/1698897659-a3f55eb02c9a4954fca9bfc2f71f4bf1.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxab5dmgj32400agwj6.jpg)

此方法用于返回菜单中所选项的详细issue信息，一般在下图这个位置调用：

[![](assets/1698897659-bed0e385dab2565901e9673a999b8aa1.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxac7ub0j31fz0u04fr.jpg)

返回的是IScanIssue的实例，我们可以调用其中的方法来获取issue的详细信息比如名字啊啥的。

-   getSelectedMessages

[![](assets/1698897659-e6dce5f256f967518bd658643b03fde9.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxacylsbj323w0aejw2.jpg)

此方法返回当前菜单所选项对应的HTTP请求以及响应的详细信息，返回的IHttpRequestResponse的实例，我们可以使用其中的方法来获取当前数据包中的详细信息，这个其实我在上面已经用过了，不了解的可以去看看。

-   getSelectionBounds

[![](assets/1698897659-bb6eea08c6c58cf9e1926448b7e2cf20.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxadgu0dj323u08wmz9.jpg)

不常用，不做介绍。

### ICookie

留坑。

### IExtensionHelpers

这个接口很重要，会经常用到，如果仔细留意我上边的代码，就会发现我会在每个插件里写上一句：

```plain
self._helpers   = callbacks.getHelpers()
```

getHelpers方法实际上就是获取此接口的实例，此接口中可使用的方法比较多，截不完，可以来这看：[Interface IExtensionHelpers](https://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html)

下面开始逐个介绍此接口中的每个方法。

-   analyzeRequest

[![](assets/1698897659-2d0c6b9b7f5093aa4c26b79a4c59adc8.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxae2xhqj31nh0u0aiq.jpg)

此方法可传递三种形式的参数，返回的是IRequestInfo的实例，我们通常使用此方法来分析请求数据包。

示例：

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from burp import IHttpListener


class BurpExtender(IBurpExtender,IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerHttpListener(self)

    def processHttpMessage(self,toolflag,messageIsRequest,messageInfo):
        service = messageInfo.getHttpService()
        request = messageInfo.getRequest()
        analyze_req = self._helpers.analyzeRequest(service,request)
        params = analyze_req.getParameters()
        new_params = ''
        for param in params:
            k = param.getName().encode("utf-8")
            v = param.getValue().encode("utf-8")
            new_params += k + '=' + v +'&'
        new_params = new_params[:-1]
        print('Params is '+ new_params)
```

输出：

[![](assets/1698897659-6bfdaa9fcf68056b218fcdb8bde80c2d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaf2x59j31fz0u0asy.jpg)

上述代码用于获取请求中的参数列表，包括cookie的以及query，如果不想要cookie的参数，可以使用一个判断：

```plain
if param.getType() == IParameter.PARAM_COOKIE:
                continue
```

参考：

[![](assets/1698897659-71e4ac465ea909778debb73c8a60fc3a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxafq7wxj325s0acacw.jpg)

-   analyzeResponse

[![](assets/1698897659-7e2102d231e4d90ffc7da24b472068d0.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxagoe8tj32400ao76g.jpg)

此方法返回一个IResponseInfo实例，我们可以使用此实例来分析响应数据包。

示例：

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from burp import IHttpListener


class BurpExtender(IBurpExtender,IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerHttpListener(self)

    def processHttpMessage(self,toolflag,messageIsRequest,messageInfo):
        response = messageInfo.getResponse()
        analyze_response = self._helpers.analyzeResponse(response)
        print("status code:"+str(analyze_response.getStatusCode()))
```

输出：

[![](assets/1698897659-f5ca303af9adbfb8f702dc047f17221a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxahon33j31700keju6.jpg)

-   getRequestParameter

[![](assets/1698897659-6d4b20ce57b34dcd3c9beaee781c2872.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxai2rc8j323w0d0whm.jpg)

此方法用于获取request中特定参数的详细信息，返回IParameter实例。

示例：

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from burp import IHttpListener


class BurpExtender(IBurpExtender,IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerHttpListener(self)

    def processHttpMessage(self,toolflag,messageIsRequest,messageInfo):
        request = messageInfo.getRequest()
        analyze_param = self._helpers.getRequestParameter(request,"v")
```

-   urlDecode

[![](assets/1698897659-db01d7638eebdb6e6b3464da7c0eb6ef.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaintj9j31uc0ayta5.jpg)

顾名思义，传入一个字符串，返回url解码后的字符串，同样也可以传入bytes的数据，返回被解码后的数据。

-   urlEncode

[![](assets/1698897659-91c85ea86265e165eae0fb6139f2c14f.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxajiwtsj31em0awjsv.jpg)

一样的，传入一个字符串，返回被url编码后的字符串，同上，也可以传入bytes的数据，返回被编码的字符串。

-   base64Decode&base64Encode&stringToBytes&bytesToString

[![](assets/1698897659-20e443c13236a6025832ab901210c813.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaln1q1j323y0ng0w8.jpg)

[![](assets/1698897659-92f9af987812f1d317a8723026d240d4.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxan0qh8j323w0q4dmd.jpg)

这几个编码解码都是一样的，不重复赘述了。

-   indexOf

[![](assets/1698897659-9766bff7ec0ac51ed3aec8f9aa42361b.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxanzoitj31zu0jmtct.jpg)

直接看图吧，这个方法和Python中的index的使用方式是一样的。

-   buildHttpMessage

[![](assets/1698897659-680b0d245ec3c5c78585e2da1efd0a28.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaonnqbj31rc0d8acp.jpg)

这个方法挺重要的，在更新请求的时候会经常用到。

以github上的某个插件为例介绍此方法：[CaidaoExt.py](https://github.com/ekgg/Caidao-AES-Version/blob/8f52ef82f9cdbe84863b8c6f82c1ac3150159940/BurpSuite-Caidao-Extender/CaidaoExt.py)

在57-66行获取了请求的详细信息并使用buildHttpMessage方法创建一个更新后的请求：

```plain
info = getInfo(messageInfo, messageIsRequest, self._helpers)
            headers = info.getHeaders()

            # get the body
            body = getBody(messageInfo.getRequest(), messageIsRequest, self._helpers)

            # encrypt the caidao post body
            encryptedBody = encryptJython(body, key, iv)

            newMSG = self._helpers.buildHttpMessage(headers, encryptedBody)
```

67行使用messageInfo.setRequest更新了请求消息主体，此时发出去的请求即为加密后的请求。

由于buildHttpMessage返回的是byte的数据类型，所以同样也可以用于漏扫时的重新发包：

```plain
againReq = self._helpers.buildHttpMessage(againReqHeaders, reqBodys)
ishttps = False
if protocol == 'https':
ishttps = True
againRes = self._callbacks.makeHttpRequest(host, port, ishttps, againReq)
```

-   buildHttpRequest

[![](assets/1698897659-d8c4d488c31fa3694ca67cecfc35ebdf.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxap45e2j31u60aswge.jpg)

同样的，此方法也可以用来使用于当漏扫时重新发包：

```plain
java_URL = URL(http_url)
port = 443 if java_URL.protocol == 'https' else 80
port = java_URL.port if java_URL.port != -1 else port
httpService = self.helpers.buildHttpService(java_URL.host, port, java_URL.protocol)
httpRequest = self.helpers.buildHttpRequest(URL(http_url))
self.callbacks.makeHttpRequest(httpService, httpRequest))
```

-   addParameter

[![](assets/1698897659-2ecaaa3ae2d455a2a43996b0e39ec0a4.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxapnjz9j31zu0jmtct.jpg)

看官方描述就清楚了，此方法是用于添加request中的参数的，需要传入一个byte的数据包以及IParameter实例的参数或参数集合。

返回一个完整的数据包，数据类型为byte。

-   removeParameter

[![](assets/1698897659-0598416adcd08e19d5b0fe2d687c08e4.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaq4xslj31r80da41a.jpg)

同上，传递的参数都是一样的，只不过会移除指定的参数或参数集。

返回一个完整的数据包，数据类型为byte。

-   updateParameter

[![](assets/1698897659-ca543db9d15d928461dea3232ceeef14.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaqkr8bj323y0dswie.jpg)

同上，用于更新请求中的参数，目前支持更新cookie，postdata，url中的参数。

返回更新后的完整数据包，数据类型为byte。

-   toggleRequestMethod

[![](assets/1698897659-7023f2872585457446dac6cd28d5447a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxatw5v9j32400awdi7.jpg)

此方法用于切换GET/POST请求，类似以下这个按钮：

[![](assets/1698897659-109109cf246ef65ef588adac0f8f893a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaum96bj31fz0u07g7.jpg)

返回切换方法后的完整数据包，数据类型为byte。

-   buildHttpService

[![](assets/1698897659-65d3fab90697cf15777f31579216b206.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaypqdaj31zu0u0jxd.jpg)

这个方法在官方案例中有提到：[TrafficRedirector.py](https://github.com/PortSwigger/example-traffic-redirector/blob/master/python/TrafficRedirector.py)

个人理解是用来更新httpservice的，一般搭配setHttpService来使用。

-   buildParameter

[![](assets/1698897659-ddc51d27ab407200b7768d3c274c2194.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxaze42uj323w0fcdio.jpg)

传入param的name以及value，最后一个type实际上就是IParameter内置的几个type：

[![](assets/1698897659-e6da81f38e86b6d039832743101efe3d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxb0zc6wj324k0jugqk.jpg)

返回一个IParameter实例，配合前面的updateParameter或addParameter使用。

-   makeScannerInsertionPoint&analyzeResponseVariations&analyzeResponseKeywords

[![](assets/1698897659-83e2803248fdeda18e5eeeffd8679372.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxb1aw80j31us0hadjt.jpg)

[![](assets/1698897659-9339c24e8f90b4097a628bf378d3cb8d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxb2ci5uj323c0pe0z7.jpg)

留个坑，这几个方法没用过，不清楚细节，不在这儿班门弄斧了。

### IExtensionStateListener

[![](assets/1698897659-5d7aeb7638cc3c72115032c15ea44ccd.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galxb36rmmj327y0tu79n.jpg)

此接口通过调用`IBurpExtenderCallbacks.registerExtensionStateListener()`来实现。

需要实现的方法只有一个：extensionUnloaded

当插件被取消使用或者被卸载时，都将触发此方法。

### IHttpListener

[![](assets/1698897659-a410cd11695e227fc9974a7c5c9c1c0d.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzs0vyaj327y0iu78f.jpg)

这个接口挺重要的，可以通过调用`IBurpExtenderCallbacks.registerHttpListener()`来实现此接口。

-   processHttpMessage

[![](assets/1698897659-0b4f9f31a5befa0ec53415504f590900.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzt530tj32160h40wr.jpg)

这是此接口中唯一一个需要实现的方法，当通过`IBurpExtenderCallbacks.registerHttpListener()`注册了HTTP监听器后，所有的流量都会先传入processHttpMessage方法中进行处理。

传递进来的值有这么几个：

1.toolFlag (标志位)  
2.messageIsRequest (标记处理的数据包是request还是response)  
3.messageInfo (一个IHttpRequestResponse实例，包含当前请求的详细信息)

需要注意的是，浏览器访问某个页面时，流量会先经过此方法，当此方法运行结束后，浏览器才会返回页面，所以如果我们的漏扫是需要发很多次包的，就不要使用这个接口，或者进行某些判断后才触发漏扫的流程。

我们一般使用这个方法来进行如下几个操作：

1.替换请求or响应主体内容  
2.进行一次性漏洞扫描 (如xxe这种只需要发一次包的)

### IHttpRequestResponse

[![](assets/1698897659-93bff2697a7f4ee8f9a3a005202561ff.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwztv5d0j327y0auq5d.jpg)

此接口用于检索和更新有关数据包详细信息，具体可使用的方法如下：

[![](assets/1698897659-b46067c59304d30f8f4837a9c5202df3.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzvajm2j31to0r0ah6.jpg)

PS：getxxx的方法只能在响应结束后使用，而setxxx的方法也只能在响应前使用。

下面挑几个经常用的来介绍。

-   getHttpService

[![](assets/1698897659-f614bcab094ca1629d5857557ff19ef9.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzw35otj31sq08875m.jpg)

返回IHttpService的实例，通过此方法我们可以获得一些请求中的信息，包括域名、端口、协议等。

示例：

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from burp import IHttpListener


class BurpExtender(IBurpExtender,IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerHttpListener(self)

    def processHttpMessage(self,toolflag,messageIsRequest,messageInfo):
        service = messageInfo.getHttpService()
        host = service.getHost()
        port = service.getPort()
        protocol = service.getProtocol()
        complete_url = str(protocol) + '://' + str(host) + ':' + str(port)
        print("You are loading: " + complete_url)
```

输出：

[![](assets/1698897659-96950fc12af730ea54ca13fb1dff3ea0.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzwyqfqj316y0n0dl6.jpg)

-   getRequest&getResponse

[![](assets/1698897659-09db4c394042f328e789ddfc3cd1b9e8.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzxfq61j31vi08ct9n.jpg)

[![](assets/1698897659-df0185ff42fb8a3bc9916e14fce9cbf0.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzy267qj3108088mxy.jpg)

这两个方法用于获取请求主体或响应主体，返回的数据类型为bytes，一般配合analyzeRequest以及analyzeResponse来解析请求或响应主体中的信息。

-   setHighlight

[![](assets/1698897659-c34ddd417633552e8a59bec2e21c8a21.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzyfdfuj31o808awg4.jpg)

高亮某个请求信息，color可以自定义，一般用于高亮存在敏感信息的数据包等。

示例：

```plain
from burp import IBurpExtender 
from burp import IContextMenuFactory

from burp import IHttpListener


class BurpExtender(IBurpExtender,IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self._context   = None

        # set up the extension
        callbacks.setExtensionName('IBurp')
        callbacks.registerHttpListener(self)

    def processHttpMessage(self,toolflag,messageIsRequest,messageInfo):
        messageInfo.setHighlight('red')
```

此时我们在history中就可以看到被高亮的请求了，效果如下：

[![](assets/1698897659-79670a51b1fc82464586582d7b676ba6.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galwzzjqz1j31fz0u0dsb.jpg)

-   setRequest&setResponse

[![](assets/1698897659-e1f31f4fd0589a361922729d9e8f6317.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx00ccroj31dk04a0to.jpg)

两个set的作用都是一样的，一个是用来替换请求主体的信息，一个是用来替换响应主体的信息，拿一个做介绍，以一个解析unicode编码的插件为例：[changeu.py](https://github.com/stayliv3/burpsuite-changeU/blob/master/changeu.py)

29行开始处理数据包，使用`if not messageIsRequest`来确保处理的只是response。

42-50行处理header中的content-type：

```plain
for header in headers:
                    # Look for Content-Type Header)
                    if header.startswith("Content-Type:"):
                        # Look for HTML response
                        # header.replace('iso-8859-1', 'utf-8')
                        # print header
                        new_headers.append(header.replace('iso-8859-1', 'utf-8'))
                    else:
                        new_headers.append(header)
```

将编码替换为utf-8。

54-62行处理response中的body：

```plain
body = response[analyzedResponse.getBodyOffset():]
                body_string = body.tostring()
                # print body_string
                u_char_escape = re.search( r'(?:\\u[\d\w]{4})+', body_string)
                if u_char_escape:
                    # print u_char_escape.group()
                    u_char = u_char_escape.group().decode('unicode_escape').encode('utf8')
                    new_body_string = body_string.replace(u_char_escape.group(),'--u--'+u_char+'--u--')
                    new_body = self._helpers.bytesToString(new_body_string)
```

将unicode解码后替换为原响应body，在64行更新了响应结果：

```plain
messageInfo.setResponse(self._helpers.buildHttpMessage(new_headers, new_body))
```

实现效果：

[![](assets/1698897659-d4dcad7ab8203172d3c50bd59314f059.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx01a4ipj31fg0n443x.jpg)

### IHttpService

[![](assets/1698897659-18d93ce8147586b2d58e46a7b8107a93.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx026jryj31fw0k4n13.jpg)

这个之前讲其他接口的时候用到了，这里不赘述了，一般是要配合其他接口来使用的，获取详细的请求地址。

### IInterceptedProxyMessage&IProxyListener

IInterceptedProxyMessage这个接口是由注册IProxyListener来实现获取数据包的详细信息的。

先看看IProxyListener吧，这个其实和IHttpListener有点像，只不过IHttpListener是获取burp所有模块的数据包，而IProxyListener仅获取proxy模块的数据包。

接口描述如下：

[![](assets/1698897659-bb0a9b00b754e7902803dbb954b363b4.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx03n3dzj326w0iytcy.jpg)

传入的message就是IInterceptedProxyMessage的实例，其他的都和IHttpListener是一样的。

接着转回来看IInterceptedProxyMessage实例，其可以使用的方法如下：

[![](assets/1698897659-39be0c506849905c31ec92237362912a.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx04lrxij324s0hydkp.jpg)

这里的getMessageInfo方法，最终得到的就是IHttpListener中传入的message。

-   getClientIpAddress

[![](assets/1698897659-81822a4282bcb713096c6c6d2b5fa433.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx05g1bij318q0860u2.jpg)

此方法返回客户端的请求地址，一般是127.0.0.1。

-   getListenerInterface

[![](assets/1698897659-f16ffc19acb4d81cb6397ee45d185486.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx05txwdj31qu088q4j.jpg)

此方法返回代理地址，默认为127.0.0.1:8080。

-   getMessageInfo

[![](assets/1698897659-eb0d2fed7182c05f6e3a470e497571af.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx06gqiuj319o088myh.jpg)

此方法返回一个IHttpRequestResponse实例，相当于IHttpListener中传入的message，可以调用其实例中存在的方法。

### IIntruderxxx

[![](assets/1698897659-46501839c16fc14684db24017646ce21.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx07cdwtj30fa03ajrx.jpg)

这几个接口留个坑，下次讲吧，没用到过。

### registerMenuItem

[![](assets/1698897659-c65863b52004c09d2d62354bac970a2f.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx08c6kbj31cs0u0gt2.jpg)

此接口用于实现自定义菜单上下文，并通过重写menuItemClicked方法来实现一些自定义操作。

通过`Callbacks.registerMenuItem()`来重写。

示例：

```plain
#! /usr/bin/python
# A sample burp extention in python (needs jython) which extracts hostname from the request (Target Tab).
from burp import IBurpExtender
from burp import IMenuItemHandler
import re
import urllib2
class BurpExtender(IBurpExtender):
    def registerExtenderCallbacks(self, callbacks):
        self.mCallBacks = callbacks
        self.mCallBacks.registerMenuItem("Sample Extention", hostnamefunc())

class hostnamefunc(IMenuItemHandler):
    def menuItemClicked(self, menuItemCaption, messageInfo):
        print "--- Hostname Extract ---"

        if messageInfo:

            request1=HttpRequest(messageInfo[0].getRequest())
            req=request1.request
            host=req[1]    
            print host
            print "DONE"
class HttpRequest:
    def __init__(self, request):
        self.request=request.tostring().splitlines()
```

加载此插件后可以看到在右键菜单中多了一个选项：

[![](assets/1698897659-112ecf4eca55a97a421cc82b4b52719b.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx09d1coj31fz0u0h70.jpg)

通过点击就可以触发menuItemClicked方法，实现对应的功能，这里实现的功能是gethostname。

输出：

[![](assets/1698897659-96974b002caeca8f53594c32f5e70c63.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx0a2598j310m0coq3x.jpg)

### Another

[![](assets/1698897659-1610d28e92e456c40e329ccd5f7c1fe2.jpg)](https://tva1.sinaimg.cn/large/006tNbRwgy1galx0bjehxj30d60iadic.jpg)

剩下的就是上图中的接口了，基本上是之前接口的方法中引入的实例或对象等。想了解这些方法的话，对应方法对应去看即可。

## 学习方法

个人建议是对着别人写过的工具理解其中的代码，哪里不理解的可以去看官方接口，或者去github搜某些接口的用法，本地多改改就能理解代码的含义了，**Burp写插件其实就是在实现Burp自带的接口，重写其中的一些方法以达成某些想法。**

## 总结

在写这篇文章的过程中，很多方法我是一边实现一边写的，导致有的地方可能写的不正确(因为是按照个人理解写的)，如果有错误的地方，希望师傅们能指出来，我会及时更正文中的错误点
