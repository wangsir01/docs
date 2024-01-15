
# 

[↓↓↓](https://www.cnblogs.com/Arthemis-z/p/17717859.html)  
  
Linux环境下sentence-transformers 之 all-MiniLM-L6-v2模型安装与使用  
  
[↑↑↑](https://www.cnblogs.com/Arthemis-z/p/17717859.html)

好记性不如烂笔头系列

一、背景：

1、之前使用chatgpt接口生成embeddings的向量维度为1536维，数据库中占用较大，所以找寻低维度的向量生成方法，减少数据占用

2、在[huggingface](https://huggingface.co/)上发现[all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2 "all-mpnet-base-v2")及[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 "all-MiniLM-L6-v2")两个模型不错，前者会生成768维的向量，后者会生成384维的向量

二、介绍：

　　1、huggingface下的[Sentence Transformers](https://huggingface.co/sentence-transformers?sort_models=downloads#models "sentence-transformers")是一个Python框架，用于最先进的句子，文本和图像嵌入。all-mpnet-base-v2、all-MiniLM-L6-v2则是该框架下下载量最多的两个模型

2、模型并不能直接使用，使用这些模型需要提前安装好环境

三、环境安装：

1、因为要使用python环境，所以我们使用[Anaconda（官网）](https://www.anaconda.com/download/#macos)来对环境进行统一管理，具体介绍可看这篇文章：[Anaconda介绍、安装及使用教程](https://zhuanlan.zhihu.com/p/32925500)

2、官网下载Anaconda linux环境安装包，并传到linux下

![](assets/1705301789-aa144d9e74ca3bae981090463c6a2509.png)

![](assets/1705301789-1cc927e101e11d43f3c801aebae81944.png)

![](assets/1705301789-c1fe8d597c53f04e9fe73528996f24aa.png)

 3、执行安装Anaconda

```plain
1 bash Anaconda3-2023.07-2-Linux-x86_64.sh
```

按照说明一路向下回车，直到显示：Do you accept the license terms? \[yes|no\]，输入yes，回车，等待安装

![](assets/1705301789-7b928fec3c3b3cecb84810a70a87e397.png)

![](assets/1705301789-e343cfcd410c50895e58e942ce6859aa.png)

**此时记得断开终端，重新连接，使安装后的Anaconda生效！**

 之后执行指令，来验证是否安装成功，成功会显示版本号

```plain
conda --version
```

执行指令，来更新conda，等待跳出更新列表，输入y，进行更新

```plain
conda update conda
```

![](assets/1705301789-fda7cdc29a88db7481411ea66548da6e.png)

4、创建python环境（此处看文章 [Anaconda介绍、安装及使用教程](https://zhuanlan.zhihu.com/p/32925500) 即可）

通过[Sentence Transformers github](https://github.com/UKPLab/sentence-transformers)页面可知，安装条件，在条件[transformers v4.6.0](https://github.com/huggingface/transformers/blob/main/README_zh-hans.md)中看到在python3.8+得到测试，为了稳妥起见，我这边使用了python3.9

![](assets/1705301789-04a1470b5773b656489742f7a0f4d022.png)

![](assets/1705301789-d67faae973e312936e1028b8d43ad978.png)

 创建python3.9环境，输入y回车，开始创建

```plain
conda create --name python3.9 python=3.9
```

![](assets/1705301789-4924ce159c07cb86944a1ee0df0488ef.png)

查看环境

```plain
conda info --envs
```

![](assets/1705301789-f83dd00eae917ec3db7f500ce8ba8b47.png)

 切换到环境python3.9

```plain
source activate python3.9
```

![](assets/1705301789-dad40d34770fc61deef8f91c5eb58d08.png)

 5、安装PyTorch

进入[pyTorch官网](https://pytorch.org/get-started/locally/)，获取安装pyTouch命令，根据自身情况选择

![](assets/1705301789-7f948e374446cd3379325daa17d9237d.png)

 回到python3.9环境下，执行命令，安装pyTorch

```plain
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

![](assets/1705301789-1bd5da12bff6b6bda5518220452aea30.png)

 6、安装[transformers](https://github.com/huggingface/transformers/blob/main/README_zh-hans.md)

 因为上面已经安装了pyTorch，所以此时可以安装transformers了

```plain
pip install transformers
```

![](assets/1705301789-ec70c59da8c1347db06562f50157bfe3.png)

7、上述依赖环境安装完成，开始安装`sentence-transformers`

建议使用conda安装，使用pip安装不知道会有何问题

```plain
conda install -c conda-forge sentence-transformers
```

![](assets/1705301789-f5ea26b2a19e53329cc375010af7f1af.png)

 此时已全部安装完成，环境配置完成

8、下载模型

此处建议手动下载模型，否则执行python脚本时再下载会很耽误时间

模型地址上述提过：[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 "all-MiniLM-L6-v2")，按照图中所示下载全部文件，再放到linux指定目录

![](assets/1705301789-8e1abf6b645ce33431eff5c367588b72.png)

![](assets/1705301789-63284d218ae421c7cac8e454b1a1b56c.png)

9、执行测试python脚本

```plain
from sentence_transformers import SentenceTransformer

sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('/usr/local/zxx/huggingface_model/all-MiniLM-L6-v2')
embeddings = model.encode(sentences)
print(embeddings)
```

![](assets/1705301789-2da0afa4867ee1dc10cd60983bbc7325.png)

 完结撒花~（实测，384维的向量![](assets/1705301789-5353d4250f929d8c4e67db7300c50047.png)）
