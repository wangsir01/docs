
# GPTs攻击面研究与分析

原创 天元实验室

[↓↓↓](javascript:)  
  
M01N Team  
  
[↑↑↑](javascript:)

*2023-12-11 18:04* *发表于北京*

![图片](assets/1703487496-6dd7d70bf683fe12d6039c5ab9c8f6a0.gif)

**引言**

在11月OpenAI的发布会之后，GPT-4的能力迎来了巨大的提升，支持用户基于初始提示词、自定义的知识库以及Actions API来构建特定任务或者主题的GPTs应用，并且引入了包括内嵌的Python代码解释器、网络内容浏览，以及图像生成在内的Agents，让模型的能力不只是局限于通用智能聊天框，通过增强模型与现实世界的交互性和多功能性，进一步扩展了模型的应用范围。

  

随着社区公开发布的GPTs数量已经过万，在深入探讨GPTs的功能、基于云化架构的重要性以及未来的发展趋势的同时，我们必须认识到，尽管这些创新是突破性的，但它们也带来了对于自身的安全挑战。在之前的文章中，我们已经研究分析了针对Python代码解释器的代码执行逃逸问题，本文将对GPTs的特性及其相应的攻击面进一步分析，探索更多关于LLMs安全风险的理解与思考。

  

**01 GPTs工作架构 && 特性**

如图所示，将GPTs带入由“LLMs + 规划 + 记忆 +工具”组成的Agent框架中，GPTs作为自主代理的核心控制器，其潜力远不止于生成优秀的文本，而是可以成为一个强大的通用问题智能化解决方案。其中Agents由几个关键组件构成，包括目标拆分与规划、记忆以及外部工具的使用。它们能够分解复杂任务为更小的子目标，并进行自我反思和优化，通过调用外部API获取所需的数据信息。此外，GPTs能够通过记忆和规划进行更深层次的任务处理，增强了与环境的交互能力。LLMs应用也在趋于在云化基座架构之上，发展为由LLMs模型作为决策引擎 + Agents机制作为调度能力的应用形态，这些特性使得GPTs不仅可以应用于日常任务的自动化，还能在科学发现、数据分析等领域展现其强大功能，成为在多领域下的高效能智能应用系统。

![图片](assets/1703487496-08a685bfbfc87e0c159948b2de22af95.png)

  

**02 GPTs攻击面分析**

**GPTs Actions 攻击面**

GPTs Actions将LLMs的功能扩展到更广泛的应用范围，Actions允许模型不仅仅是进行文本的生成响应，而是能够执行一系列更为复杂和动态的任务，例如：GPTs可以通过Actions处理分析数据、检索外部的数据信息以及外部工具调用等。在构建GPTs阶段，通过定义外部API的地址、路由、请求方式、参数信息、认证方式等关键信息，让LLMs大脑获得特定任务的解析与执行能力。

![图片](assets/1703487496-664320ecafc7f0872d583b10b25217a8.png)

  

以天气查询类GPTs为例，当用户想要查看指定城市在某一天的天气情况时，模型内部本身是不具备相关天气数据信息的，LLMs在任务规划阶段会先调用对应的天气信息检索Actions，再结合获取到执行结果并向用户提供回答。在调度Actions的过程中，LLMs会根据提前定义好的接口格式信息，构建特定的天气数据查询请求任务，并完成相应的请求发送。

![图片](assets/1703487496-a118a20ae1b46003b71f017badef3425.png)

  

由于在GPTs的构建阶段已经将相关的接口调用信息加入到了模型中，因此通过提示词注入的方式可以实现对目标GPTs应用中API接口列表的获取，以我们构建的Weather Assistant为例，成功以表格的形式输出了完整的接口数据信息。GPTs Actions功能作为模型获取外部能力的主要方式，未来会出现在各种业务应用场景中，企业和开发者会通过API调度的方式将一些业务数据或者调度功能集成到模型当中，通过这种攻击方式可以直接获取到完整的API列表信息，攻击者可能会利用企业公开的GPTs应用测绘获取目标的资产信息，进一步利用传统API中存在的未授权访问、代码执行等漏洞，实现从“AI云端”到目标企业的攻击。

![图片](assets/1703487496-a0ca39a5c9d60d7fb0260b1058840985.png)

  

  

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
| Plugin | URL | Path | Request Method | Description | Operation ID | Parameters |
| petstore\_swagger\_io\_\_jit\_plugin | petstore.swagger.io | /pets | GET | List all pets | listPets | limit: number |
| petstore\_swagger\_io\_\_jit\_plugin | petstore.swagger.io | /pets | POST | Create a pet | createPets |     |
| petstore\_swagger\_io\_\_jit\_plugin | petstore.swagger.io | /pets/{petId} | GET | Info for a specific pet | showPetById | petId: string |
| weather\_example\_com\_\_jit\_plugin | weather.example.com | /location | GET | Get temperature for a specific location | GetCurrentWeather | location: string, date: string |

  

**GPTs 初始提示词泄露**

初始提示词Instructions作为GPTs构建时的关键信息，用于设定GPTs目标与角色、思维链运行模版、Tools工具集调用方式等，实现对GPTs的工作方向以及应用范围的引导。GPTs Instructions支持使用GPT Builder生成和自定义Configure编写两种方式进行设定，其中GPT Builder会一步步的引导用户来构建符合自己需求的Instructions信息，以下是通过GPT Builder生成初始提示词的基本结构：

```plain
Role and Goal:  This GPT is designed as a weather query assistant. It responds to user queries about weather conditions based on a specified location and date ... it uses the "GetCurrentWeather" operation to get the accurate and up-to-date weather information.

Constraints: The GPT should not provide weather forecasts beyond its capability or the data available through the 'GetCurrentWeather' action. It should avoid making predictions or assumptions about weather conditions beyond the provided data.

Guidelines: The GPT should be clear and precise in conveying weather data. It should understand and correctly interpret the location and date information provided by the user. It should also ensure that the weather information is presented in a user-friendly manner.

Clarification: If there is ambiguity in the user's request (e.g., unclear location or date), the GPT should ask for clarification to provide accurate weather data.

Personalization: The GPT should maintain a helpful and informative tone, focusing on delivering weather information efficiently.
```

  

如下图所示，我们研究利用攻击性的提示词Payload，获取到了Weather Assistant的初始提示词。

![图片](assets/1703487496-cc0512ad9a58655947cd622f6f75d57a.png)

  

其中获取到的GPTs Instructions结构如下所示，包含了GPTs Actions API插件、Python解释器、网络浏览器等关键Tools工具集的设定。

```plain
You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture.
Knowledge cutoff: 2023-04
Current date: 2023-12-07

Image input capabilities: Enabled

# Tools

## weather_example_com__jit_plugin - Actions API插件定义

This typescript tool allows you to call external API endpoints on weather.example.com over the internet.
...

## browser - 外部网络内容浏览Tool定义

You have the tool `browser` with these functions:
`search(query: str, recency_days: int)` Issues a query to a search engine and displays the results.
...

## python - Python代码执行以及数据访问Tool定义

When you send a message containing Python code to python, it will be executed in a
stateful Jupyter notebook environment. Python will respond with the output of the execution or time out after 60.0
seconds. The drive at '/mnt/data' can be used to save and persist user files. Internet access for this session is disabled. Do not make external web requests or API calls as they will fail.
...

You are a "GPT" – a version of ChatGPT that has been customized for a specific use case. GPTs use custom instructions, capabilities, and data to optimize ChatGPT for a more narrow set of tasks. You yourself are a GPT created by a user, and your name is Weather Assistant. Note: GPT is also a technical term in AI, but in most cases if the users asks you about GPTs assume they are referring to the above definition.
...

Role and Goal:  This GPT is designed as a weather query assistant. It responds to user queries about weather conditions based on a specified location and date ... it uses the "GetCurrentWeather" operation to get the accurate and up-to-date weather information.

Constraints:

...
```

  

值得关注的是，GPT Builder生成提示词中包含针对当前应用使用限制条件的一些定义，但主要还是在确保模型响应天气结果的准确性，缺乏在LLMs安全性方面的限制与防御，因此在GPTs应用实际的对外开放使用过程当中，攻击者可轻易获取到完整Instructions提示词内容。随着GPTs应用数量的飞速提升，越来越多的应用将会面临这一安全问题，目前在Github上已经有多个项目开源了GPTs应用的Instructions提示词设定集合。  
  
Instructions提示词作为GPTs应用的核心，企业与开发者应当注重对其的保护，以确保应用在可控的范围之内为用户提供服务，关于如何对Instructions提示词实现保护，可以参考我们之前发布的文章[《LLMs安全：针对业务模型应用场景下提示词攻击的防御检测方案》](http://mp.weixin.qq.com/s?__biz=MzkyMTI0NjA3OA==&mid=2247492874&idx=1&sn=808e00c6c48f93039ba6c795eb193a0d&chksm=c184251bf6f3ac0dab341476bccbcdfd723e836678b3bcb25be979e76d001c45584a07c191d2&scene=21#wechat_redirect)，其中详细介绍了从业务模型侧Prompt防御和应用平台侧防御守卫两个方面，体系化实现对大模型应用中的提示词攻击开展防御保护。

  

**GPTs 训练数据 && 知识库文件泄露**

GPTs 在创建时支持用户自行上传自定义的知识库文件，包括：PDF、Json等多种形态的文件内容，这些知识库文件将在应用提供服务期间，为模型提供专业的知识内容，帮助开发者基于通用的GPT-4大模型快速实现垂直业务应用模型的训练与开发。我们在构建的Weather Assistant应用中上传了一个weather\_info.json文件，用于为该应用提供一些模型外部的天气数据信息。

![图片](assets/1703487496-dae054987da8bd7085ee3a9fcce9701d.png)

  

通过提示词注入可以让对外发布的GPTs应用告诉用户，其在构建阶段上传了哪些知识库文件。

![图片](assets/1703487496-5828827b3fb85b9b26b8a82070cb6a67.png)

  

通过进一步的利用，成功使得GPTs应用调度Python解释器组件，从/mnt/data目录中将我们上传的天气数据文件打包并生成了下载链接，实现了对目标GPTs训练数据 && 知识库文件内容的获取。

![图片](assets/1703487496-b48e3dd9c346e0be4c6371cc57030825.png)

  

实际验证文件内容，也可以看到其中的json结构以及具体的键值对都是完全一致的。

![图片](assets/1703487496-fc9d2d26dc529c175a755f2b7bc61326.png)

  

值得关注的是在GPTs应用构建阶段，用户上传知识库文件后，GPTs开发面板会主动提示该文件的内容将会被包含到GPTs对话中去，并且当应用开启Python代码解释器功能时，存在被下载的风险。**存在这一安全问题，正是因为Python解释器执行代码的过程是在K8S Pod中完成的，并且从泄露的初始提示词中也可以看到在Python Tool定义过程中，明确说明 /mnt/data目录可用于保存和持续运行用户文件。OpenAI为了让用户更方便的在GPTs应用中使用自己上传的知识库文件，在启动Python K8S Pod的过程中将相关文件挂载到了容器中，并结合Python解释器实现更复杂的工作内容。**这一发现也进一步验证了我们在[《从ChatGPT代码执行逃逸到LLMs应用安全思考》](http://mp.weixin.qq.com/s?__biz=MzkyMTI0NjA3OA==&mid=2247492812&idx=1&sn=d653b00419d2b7e65d672540d9a2adaf&chksm=c18424ddf6f3adcb1b023393f4ccc7128cfbed6bb7bb45acbfe285909ab7704c875e39018296&scene=21#wechat_redirect)中实现的Python代码执行逃逸是真实存在的，而非是模型幻觉输出的虚假内容。

![图片](assets/1703487496-bcefff6189c5d3822ff2b168c65d0ddf.png)

  

**GPTs 私有性访问**

 GPTs 目前支持三种不同的应用发布范围：

  

-   Only me：仅开发者自身使用
    
      
    
-   Only people with a link：仅获取到GPTs Link的用户使用
    
      
    
-    Public：完全公开
    
      
    

其中值得关注的是第二种发布范围，访问链接的泄露可能会导致，原本开发者仅想一定范围内发布的GPTs应用，被完全公开出来，进一步通过上述的GPTs Actions、初始提示词泄露、知识库文件泄露的攻击方式获取到应用内的未授权的模型能力以及隐私数据。

![图片](assets/1703487496-b02af2dde72e6caa708d43c1dcb54d99.png)

  

目前Github上的开源项目已经收集了不少GPTs应用，这些应用未必是所有作者都希望公开。

  

参考链接：

  

-   https://www.gptshunter.com/
    
      
    
-   https://github.com/ai-boost/Awesome-GPTs
    

  

**Python 解释器滥用**

在[《从ChatGPT代码执行逃逸到LLMs应用安全思考》](http://mp.weixin.qq.com/s?__biz=MzkyMTI0NjA3OA==&mid=2247492812&idx=1&sn=d653b00419d2b7e65d672540d9a2adaf&chksm=c18424ddf6f3adcb1b023393f4ccc7128cfbed6bb7bb45acbfe285909ab7704c875e39018296&scene=21#wechat_redirect)一文中，我们已经重点分析了该功能的特性以及相关攻击面和代码执行逃逸问题，虽然OpenAI已经在底层的运行环境中进行了多种加固方式，但是该场景下依然存在部分安全风险，包括代码执行和资源滥用、数据安全问题甚至容器逃逸风险等。

  

**为了再次验证该代码执行逃逸漏洞并非是模型幻觉问题所致**，我们利用该代码执行实现了非/mnt/data目录的其他文件下载，通过将/etc/passwd文件重命名为w，成功实现了该系统文件的下载（直接下载该文件会被提示是系统文件，无法下载）。

![图片](assets/1703487496-86ff2659559ccceb0b17e5fe9d1194b8.png)

![图片](assets/1703487496-eb987631e4e294f83fdeddd2ee691ff1.png)

![图片](assets/1703487496-43c49d58f8ba90dbf00249a77863cb25.png)

  

从/etc/passwd文件中可以看到，当前容器中存在sandbox的用户，与直接执行env命令展示的环境变量信息一致。

![图片](assets/1703487496-4f8987b29b3f61fad70f12d804d2c3f3.png)

  

**03 总结**

对上述提到的各种功能以及相应的攻击面，我们总结了以下几种主要的攻击场景：

  

-   **自定义GPTs提示词泄露：**在模型应用时代，提示词是GPTs应用的核心组件之一，自定义提示词的泄露会导致对外发布的应用，轻易被其他人复刻，并且泄露的提示词当中暴露关键数据信息，也会给企业带来一些安全风险；
    
      
    
-   **敏感文件泄露：**GPTs的开发者，可能使用一些敏感文件，丰富GPTs的能力，比如访问API的key、用于绘制统计图表的薪资数据文件，通过存放在/mnt/data路径中进行持久化使用，利用代码执行、网页下载等方式，可能导致敏感文件泄露；
    
      
    
-   **计算资源滥用：**通过逃逸ChatGPT的安全限制，可以通过代码执行能力实现Python代码的解析，进而使用底层容器的计算资源，实现资源滥用；
    
      
    
-   **API信息泄露：**API是让模型获取外部能力的关键组件，而API的泄露让模型的外部能力直接泄露，既可以让攻击者从针对模型应用的攻击转到针对所属企业的攻击，也可能会在未来发展为测绘网络资产的一种新方式；
    
      
    
-   **间接提示词注入：**浏览器功能结合GPTs外部数据分析的功能，在一定的使用场景下会造成间接提示词注入风险，导致用户对话、数据等敏感数据信息被外传到攻击者的服务器；
    

  

本文从新发布GPTs应用的各项功能特性出发，分析了其中潜在的攻击面以及相关的研究成果，随着LLMs技术的快速发展，未来可能还会出现更多有趣的攻击方式，我们团队也会持续跟进各类LLMs技术发展以及相关安全问题。

  

![图片](assets/1703487496-37d80127b73f829661c0d17b431e0b18.svg)

**绿盟科技天元实验室**专注于新型实战化攻防对抗技术研究。

研究目标包括：漏洞利用技术、防御绕过技术、攻击隐匿技术、攻击持久化技术等蓝军技术，以及攻击技战术、攻击框架的研究。涵盖Web安全、终端安全、AD安全、云安全等多个技术领域的攻击技术研究，以及工业互联网、车联网等业务场景的攻击技术研究。通过研究攻击对抗技术，从攻击视角提供识别风险的方法和手段，为威胁对抗提供决策支撑。

  

![图片](assets/1703487496-37d80127b73f829661c0d17b431e0b18.svg)

**M01N Team公众号**

聚焦高级攻防对抗热点技术

绿盟科技蓝军技术研究战队

![图片](assets/1703487496-37d80127b73f829661c0d17b431e0b18.svg)

**官方攻防交流群**

网络安全一手资讯

攻防技术答疑解惑

扫码加好友即可拉群
