

# 如何在 Linux 下限制端口仅对指定 IP 开放访问

## [](#1)1\. 主机服务端口

```plain
$ iptables -I INPUT -p tcp --dport 80 -j DROP
$ iptables -I INPUT -p tcp -s 1.2.3.4 --dport 80 -j ACCEPT
```

这里仅允许 `1.2.3.4` 访问本地主机的 80 端口。

## [](#2-docker)2\. Docker 服务端口

对于类似 `docker run -d -p 80:80 shaowenchen/demo-whoami` 运行的服务，上面的方法无效，需要在 DOCKER-USER 链中添加规则。

Docker 会将 iptables 规则添加到 DOCKER 链中，如果需要在 Docker 之前添加规则需要添加到 DOCKER-USER 链中

```plain
$ iptables -I DOCKER-USER -i ens192 ! -s 1.2.3.4 -p tcp --dport 80 -j DROP
```

ens192 是本地的网卡，这里仅允许 `1.2.3.4` 访问本地主机的 80 端口。

## [](#3)3\. 清理环境

```plain
$ yum install -y iptables-services
$ systemctl restart iptables.service
```

如果需要在主机重启之后 iptables 设置，依然有效，需要安装 `iptables-services` 并保存

```plain
$ yum install -y iptables-services
$ service iptables save
```

## [](#4)4\. 参考

-   [https://docs.docker.com/network/iptables/](https://docs.docker.com/network/iptables/)

> 本文转载自：「 陈少文的博客 」，原文：[https://url.hi-linux.com/SrAYO](https://url.hi-linux.com/SrAYO) ，版权归原作者所有。欢迎投稿，投稿邮箱: [editor@hi-linux.com](mailto:editor@hi-linux.com)。
