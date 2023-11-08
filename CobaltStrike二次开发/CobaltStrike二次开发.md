

# CobaltStrike二次开发

# [](#cs-%E4%BA%8C%E6%AC%A1%E5%BC%80%E5%8F%91)CS 二次开发

> 工具：
> 
> IDEA 自带的 java-decompiler.jar

## [](#1-cs-%E5%8F%8D%E7%BC%96%E8%AF%91)1 CS 反编译

以 MAC 为例，IDEA 自带的 java-decompiler.jar 地址为：

`/Applications/IntelliJ IDEA.app/Contents/plugins/java-decompiler/lib/java-decompiler.jar`

因为 `MANIFEST.MF` 中没有 `main class` 属性，没有指定主类，因此不能直接使用 `java -jar`，如果想要执行 `java` 包中具体的类，要使用 `java -cp` 输入如下命令：

使用方法：

|     |     |     |
| --- | --- | --- |
| ```plain<br>1<br>``` | ```bash<br>java -cp java-decompiler.jar org.jetbrains.java.decompiler.main.decompiler.ConsoleDecompiler -dgs=true cs_bin/cobaltstrike.jar cs_src<br>``` |

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221164315.png-water_print](assets/1699411769-73e0b8586b1b1ea974a5c2f887a66690 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221164315.png-water_print")

反编译后，会自动打包成 `jar` 包，右键解压后打开可以看到都是 `.java` 了，使用这个方法会非常方便，就不需要第三方工具,这个反编译出来的就可以直接放入 `IntelliJ IDEA` 中，可直接实现代码搜索，相关的交叉引用。

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221164914.png-water_print](assets/1699411769-76e130d9c77f41f42f800ec2dccdc744 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221164914.png-water_print")

## [](#2-cs-%E4%BA%8C%E6%AC%A1%E5%BC%80%E5%8F%91%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C)2 CS 二次开发准备工作

### [](#21-%E5%88%9B%E5%BB%BA%E5%B7%A5%E7%A8%8B)2.1 创建工程

打开 `IntelliJ IDEA` 选择 `Create New Project` 一直选择 Next。

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165123.png-water_print](assets/1699411769-91f4ae246af0f42e5bb225ee16849d8c "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165123.png-water_print")

创建工程目录：

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165131.png-water_print](assets/1699411769-2b2c92e1c43c65595324cf5d5f77aeda "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165131.png-water_print")

创建好后需要先建立两个文件夹，右击选择 `New Directory` 建立一个 `decompiled_src` 文件夹，之后再建立一个 `lib` 文件夹。

### [](#22-%E9%85%8D%E7%BD%AE%E4%BE%9D%E8%B5%96%E5%85%B3%E7%B3%BB)2.2 配置依赖关系

把刚刚反编译好的 `CobaltStrike` 复制到 `decompiled_src` 中，然后把它解压出来，可看到一个完整的反编译后的目录。

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165416.png-water_print](assets/1699411769-0bff598b85b090b53b131d61fb4c84a0 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165416.png-water_print")

随后把原始的未编译的 `CobaltStrike` 放到刚刚新建的 `lib` 中去。

接下来需要对这个项目进行设置，点击 `File` 中的 `Project Structure` 在 `Modules` 对 `Dependencies` 进行设置。

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165747.png-water_print](assets/1699411769-4571ea39c3a348183a560a45ad493a15 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221165747.png-water_print")

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172053.png-water_print](assets/1699411769-540cae6df899aa9d383c5a85b3a0cc7c "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172053.png-water_print")

点击添加 `Jar or Directories`，添加 `./lib` 下的原始 JAR 包，并勾选 `Export`：

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172115.png-water_print](assets/1699411769-8691f63c638b2937c33b9e24af7419b7 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172115.png-water_print")

### [](#23-%E5%AF%BB%E6%89%BE-main-class)2.3 寻找 Main Class

点击 `./lib/META_INF/MANIFEST.MF` ，复制 `Main-Class`：

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172643.png-water_print](assets/1699411769-f917a1695d100bc65889264d2e9bf5e3 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172643.png-water_print")

将原始包中 `MANIFEST.MF` 的内容复制到项目中的 `MANIFEST.MF`

### [](#24-%E9%85%8D%E7%BD%AE-artifacts)2.4 配置 Artifacts

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172836.png-water_print](assets/1699411769-ebe35dad0c738c328cb310a04af1a05d "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172836.png-water_print")

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172843.png-water_print](assets/1699411769-b88066fa2e218741b5e631d4bdf8c114 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221172843.png-water_print")

接下来在 `decompiled_src` 目录中找到已经反编译完的 `aggressor` 主类，右击选择 `Refactor ——Copy File` 到 `src` 下的相同目录：

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221173302.png-water_print](assets/1699411769-f76a5a2601fae620514afe6f8de9f0b8 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221173302.png-water_print")

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221173311.png-water_print](assets/1699411769-45c4410d743245b7384130c3501561e8 "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201221173311.png-water_print")

### [](#25-%E4%BF%AE%E6%94%B9%E5%90%8E%E7%BC%96%E8%AF%91)2.5 修改后编译

点击 `Build` -> `Build Artifacts` -> `build`

## [](#3-idea-%E5%85%B6%E5%AE%83-tips)3 IDEA 其它 Tips

### [](#31-%E6%AF%94%E5%AF%B9-jar-%E5%8C%85)3.1 比对 JAR 包

在进行 bin 文件对比时，自动进行反编译

命令行形式：

|     |     |     |
| --- | --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>``` | ```bash<br>windows:<br>/path/to/idea/bin/idea64.exe diff absolute/path/to/file1 absolute/path/to/file2<br><br>mac:<br>/Applications/IntelliJ IDEA.app/Contents/MacOS/idea absolute/path/to/file1 absolute/path/to/file2<br>``` |

![https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201222093453.png-water_print](assets/1699411769-1f336582e09cda857afc950b63c597da "https://geekby.oss-cn-beijing.aliyuncs.com/MarkDown/20201222093453.png-water_print")

在 IDEA 中：

选中要比对的两个文件，`Command + D` 进行比对
