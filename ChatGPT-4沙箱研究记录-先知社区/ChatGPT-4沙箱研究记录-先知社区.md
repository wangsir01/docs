

# ChatGPT-4沙箱研究记录 - 先知社区

ChatGPT-4沙箱研究记录

- - -

## 一、环境介绍

使用的环境是OpenAI公司的gpt-4-gizmo模型。

## 二、过程记录

本来这个模型会员才可以使用，刚好前两天这个模型存在越权访问，借此来对其进行测试。

[![](assets/1704762175-f0207573c97f63662015d954382aaea7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163135-55bb91fa-ae00-1.png)

chatgpt4增加了代码解释器功能，代码类型是python。

[![](assets/1704762175-06f7f90124a3fc1de7d74f59fe3ee47f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163150-5e50f602-ae00-1.png)

随后告诉chatgpt，把我的输入当作命令，直接执行

[![](assets/1704762175-ac14b8288327c3bc91f7c9bde5c131f2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163207-68e6c0f6-ae00-1.png)

先查看一下当前目录，是在一个沙箱目录

[![](assets/1704762175-9aba41b7620627a2523c183f41f994b5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163216-6e21d15a-ae00-1.png)

查询网络情况，发现不行，猜测是被禁止了。也尝试了其他查询网络的方法，比如：`ip a`、`netstat`命令，也都不行。

[![](assets/1704762175-269d7453b832e6f6bb7630a81ba8162c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163233-77fa8852-ae00-1.png)

也尝试编写代码，直接调用系统函数进行网络查询。编写好代码，先在本地编译测试，可以执行

[![](assets/1704762175-33c7541ea52cb798a94a662b108733f6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163246-7fc347cc-ae00-1.png)

随后把程序上传到模型中

[![](assets/1704762175-42f810aed7d8d4735a6dfff20bd37e73.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163254-8471352c-ae00-1.png)

用户上传的文件在`/mnt/data`目录，这个目录是挂在的硬盘，移动到当前目录执行

[![](assets/1704762175-f25a817876991a7193db5c78716c803f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163309-8db0dc0a-ae00-1.png)

告诉我不能执行，可能是只能执行白名单程序命令

[![](assets/1704762175-7c82318e330e2c8a9443e970c4e57dac.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163324-9651ef98-ae00-1.png)

接下来看看系统上都有哪些文件，`.openai_internal`目录引起了我的注意。

[![](assets/1704762175-30ad24a222b2736b3dc3e39b3baf14c3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163334-9c9684ae-ae00-1.png)

通过目录遍历，看到这个目录下是一个python写的项目

[![](assets/1704762175-5ea0d7888437fc2a4bddf3580421c31f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163350-a5e97e58-ae00-1.png)

通过`cat`命令，获取文件源码

[![](assets/1704762175-ac5053495aae6808ca157f721c6abae5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163400-ac1f7250-ae00-1.png)

通过对下载下来的源码进行分析，发现这些源码是当前解释器的源码。python的web路由对应着页面上的功能。比如上传文件功能：

[![](assets/1704762175-381a4a75930ffee40f4c1dfa85ba99fe.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163414-b471ac3e-ae00-1.png)

后续未进一步测试，越权漏洞修复了，自动降为了3.5模型。

[![](assets/1704762175-d48b281baa2711dc92195c550cdc9ec8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240108163423-b9c99ea8-ae00-1.png)
