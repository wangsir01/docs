
# 搭建基于 qemu 与 gdb 的 Linux 内核开发环境

Published at 2023/11/1 18:59 , ... Views

## 1\. 安装所需软件

首先，我们需要安装一些必要的软件，包括编译工具，Linux 内核头文件，以及一些其他的依赖库。

```bash
1sudo apt-get install build-essential linux-headers-5.15.0-86-generic flex bison
```

`build-essential` 是一组包含了许多用于编译的软件包，如 gcc 和 make 等。`linux-headers-5.15.0-86-generic` 是 Linux 内核的头文件，用于编译内核和内核模块。

## 2\. 获取 Linux 源码

接下来，我们从 Linux 官方网站下载内核源码。

```bash
1wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.15.tar.gz
```

## 3\. 配置和编译 Linux 源码

然后，我们配置并编译下载的 Linux 源码。

首先，我们设置环境变量 `ARCH` 为 `x86`，然后使用 `make` 命令生成默认的配置文件。

```bash
1export ARCH=x86
2make x86_64_defconfig
3make menuconfig
```

在 `menuconfig` 的菜单中，我们需要启用以下选项以便调试内核：

```plain
Kernel hacking  ---> 
    [*] Kernel debugging
    Compile-time checks and compiler options  --->
        [*] Compile the kernel with debug info
        [*]   Provide GDB scripts for kernel debugging
```

关闭随机化内核地址(KASLR)选项，因为它会使得调试过程更加复杂：

```plain
Processor type and features ---->
    [] Randomize the address of the kernel image (KASLR)
```

然后使用 `make` 命令编译内核。

```bash
1make -j 20
2cp linux-5.15/arch/x86/boot/bzImage .
```

## 4\. 创建和配置模拟的文件系统

接着我们需要创建一个模拟的文件系统，并在其中安装 BusyBox。

```bash
1dd if=/dev/zero of=rootfs.img bs=1M count=10
2mkfs.ext4 rootfs.img
3mkdir fs
4sudo mount -t ext4 -o loop rootfs.img ./fs
```

我们下载并解压 BusyBox，然后将其安装到我们刚刚创建的文件系统中。

```bash
 1wget https://busybox.net/downloads/busybox-1.36.1.tar.bz2
 2tar jxVf busybox-1.36.1.tar.bz2
 3pushd busybox-1.36.1
 4	sudo make install CONFIG_PREFIX=../fs
 5popd
 6pushd ./fs
 7	sudo mkdir proc dev etc home mnt
 8popd
 9pushd busybox-1.36.1
10	sudo cp -r examples/bootfloppy/etc/* ../fs/etc/
11popd
12
13sudo umount fs
```

## 5\. 创建并配置硬盘镜像

接下来，我们需要创建并配置一个硬盘镜像。

```bash
1dd if=/dev/zero of=ext4.img bs=512 count=131072
2mkfs.ext4 ext4.img
3popd
```

## 6\. 创建并运行 qemu 脚本

现在，我们创建并运行一个 qemu 脚本来启动模拟的系统。

```bash
1vi run_qemu.sh
```

在 `run_qemu.sh` 中，我们添加以下内容：

```bash
1qemu-system-x86_64 \
2        -kernel ./bzImage  \
3        -hda ./rootfs.img  \
4        -hdb ./ext4.img \
5        -append "root=/dev/sda console=ttyS0" \
6        -nographic $@
```

然后运行脚本：

```bash
1./run_qemu.sh -s -S
```

## 7\. 使用 gdb 连接 qemu

最后，我们在一个新的终端中使用 gdb 连接 qemu，开始调试我们的内核。

```bash
1gdb
2
3> target remote localhost:1234
4
5> continue
```

OK，你已经成功搭建了一个基于 qemu 和 gdb 的 Linux 内核开发环境。你可以使用这个环境来学习和研究 Linux 内核的工作原理。

参考资源：[http://derekmolloy.ie/writing-a-linux-kernel-module-part-1-introduction/](http://derekmolloy.ie/writing-a-linux-kernel-module-part-1-introduction/)

- - -

This work is licensed under [CC BY 4.0![](assets/1698919004-ee0d4e4e7f4a9a9264b9d9555c2cbf13.svg)![](assets/1698919004-06b1d0fa348a6372aa5bd192527bfe9b.svg)](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1) except those created with the assistance of AI.

  

表情图片预览

发送评论

0 条评论

Powered By [Artalk](https://artalk.js.org/ "Artalk v2.4.4")

Artalk ErrorTypeError: NetworkError when attempting to fetch resource.，无法获取评论列表数据  
点击重新获取
