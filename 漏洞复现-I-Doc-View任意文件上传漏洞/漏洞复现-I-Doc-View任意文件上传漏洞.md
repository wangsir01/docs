
# 【漏洞复现】I Doc View任意文件上传漏洞

原创 CVES实验室

[↓↓↓](javascript:)  
  
山海之关  
  
[↑↑↑](javascript:)

*2023-11-23 15:53* *发表于马来西亚*

收录于合集

#漏洞复现 5 个

#poc 14 个

![图片](assets/1700820015-9bf2e3c7539661a8fb23381a373e2adf.jpg)

**免责声明**

**1\. 本文仅用于技术交流，目的是向相关安全人员展示漏洞的存在和利用方式，以便更好地提高网络安全意识和技术水平。**

**2\. 任何人不得利用本文中的技术手段进行非法攻击和侵犯他人的隐私和财产权利。一旦发生任何违法行为，责任自负。**

**3\. 本文中提到的漏洞验证 poc 仅用于授权测试，任何未经授权的测试均属于非法行为。请在法律许可范围内使用此 poc。**

**4\. CVES实验室对使用此 poc 导致的任何直接或间接损失不承担任何责任。使用此 poc 的风险由使用者自行承担。**

**前言**

**练习挖掘1day  
**

**情报来源：**  

```plain
https://loudongyun.360.net/leakDetail/KgndYhsjd%2Fk%3D
```

**信息收集**

**1\. 通过观察漏洞描述，都提到了远程下载恶意文件到本地，所以涉及远程访问、文件操作等函数，防护规则“html/2word”。**

**2\. github搜索源码，通过搜索"I DOC view" 关键字，找到源码，但是版本过低  
**

```plain
https://github.com/appzk/docview_win
```

**代码审计**

**controller很少，一个一个看很快发现一个问题的控制器**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**HtmlController.java，提供url参数，然后调用 \`GrabWebPageUtil.downloadHtml\` 其中参数 url可控，htmlDir不可控**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**跟进，\`GrabWebPageUtil.getWebPage\` 很明显是重点，传入了URL对象，传参情况：(可控，不可控，'index.html')**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**仔细分析\`GrabWebPageUtil.getWebPage\` 函数，如果第三个参数不可控，那么将来写入的文件名就不可控，所以这里如果为空或可控，就有可能远程获取文件内容后，写入的文件后缀改为.jsp。可惜这里不可控，强制修改filename为index.html。**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**如果filename后缀如图示，通过远程获取文件内容后写入到index.html。其中调用了 \`GrabUtility.searchForNewFilesToGrab\` 根据函数名与入参，有没有可能存在比如解析漏洞？所以跟进。**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**如果filename不是上面所示，最后写入的文件名由outFile控制**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**outFile完全可控，这里就可以利用目录穿越，拼接后就能将shell文件写入到web目录**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**\`GrabUtility.searchForNewFilesToGrab\` 按照html进行解析，提取其中的元素属性，这里有link\[href\] 、script\[src\]、img\[src\]，这里面提取的一定也是某个url或者资源地址，所以接着看 \`addLinkToFrontier\`**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**看代码这里引入了一个重要变量filesToGrab，是个数组，简单来说把src,href中的url放到数组中。**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**然后就是返回返回返回到 \`GrabWebPageUtil.downloadHtml\` ，在遍历时，再次调用getWebPage去获取文件，而且这次第三个参数为空，文件后缀完全可控了。**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**POC构造**

**流程：携带恶意link\[href\]的html -> 远程获取  -> 解析出href -> 远程获取恶意文件**

**poc.html**

```plain
<!DOCTYPE html>
<html lang="en">
<head>
    <title>test</title>
</head>
<body>
  <link href="/..\..\..\docview\poc.jsp">
</body>
</html>
```

**然后构造 \`..\\..\\..\\docview\\poc.jsp\`**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)

**广告**

**目前团队运营了两个知识星球分别为“追洞学苑”与“挖洞学苑”：**  

**追洞学苑】****会分享最新的漏洞POC，1day0day挖掘文章。**

**挖洞学苑】****会分享国内/外原创漏洞赏金项目报告，各种漏洞挖掘小技巧。**

![图片](assets/1700820015-37d80127b73f829661c0d17b431e0b18.svg)
