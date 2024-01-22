

# 技术文档 | 将OpenSCA接入GitHub Action，从软件供应链入口控制风险面 - 先知社区

技术文档 | 将OpenSCA接入GitHub Action，从软件供应链入口控制风险面

- - -

继Jenkins和Gitlab CI之后，GitHub Action的集成也安排上啦~

若您解锁了其他OpenSCA的用法，也欢迎向项目组来稿，将经验分享给社区的小伙伴们~

### 参数说明

| 参数  | 是否必须 | 描述  |
| --- | --- | --- |
| token | ✔   | OpenSCA云漏洞库服务token，可在OpenSCA官网获得 |
| proj | ✖   | 用于同步检测结果至OpenSCA SaaS指定项目 |
| need-artifact | ✖   | "是否上传日志/结果文件至workflow run（默认：否） |
| out | ✖   | 指定上传的结果文件格式（文件间使用“,”分隔；仅outputs目录下的结果文件会被上传） |

### 使用样例

workflow 示例

```plain
on:
  push:
    branches:
        - master
        - main
  pull_request:
    branches:
        - master
        - main

jobs:
  opensca-scan:
    runs-on: ubuntu-latest
    name: OpenSCA Scan
    steps:
      - name: Checkout your code
        uses: actions/checkout@v4
      - name: Run OpenSCA Scan
        uses: XmirrorSecurity/opensca-scan-action@v1
        with:
          token: ${{ secrets.OPENSCA_TOKEN }}
```

\*需要先基于OpenSCA云漏洞库服务token创建秘钥，详细信息请见[https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#about-secrets)

扫描结束后，可在仓库的Security/Code scanning里找到结果  
[![](assets/1705890854-e67ddcf6e5afb74837fa7c31e272e41b.jpg)](https://xzfile.aliyuncs.com/media/upload/picture/20240118111154-55131596-b5af-1.jpg)

也可直接跳转至OpenSCA SaaS查看更多详细信息；跳转链接可在Action日志中找到  
[![](assets/1705890854-486bf810708b15e88e106c2b619b6879.jpg)](https://xzfile.aliyuncs.com/media/upload/picture/20240118111206-5c0827f6-b5af-1.jpg)

### 更多场景

#### 同步检测结果至OpenSCA SaaS指定项目

使用proj参数将检测任务绑定至指定项目下；ProjectID可在SaaS平台获取

```plain
- name: Run OpenSCA Scan
  uses: XmirrorSecurity/opensca-scan-action@v1
  with:
    token: ${{ secrets.OPENSCA_TOKEN }}
    proj: ${{ secrets.OPENSCA_PROJECT_ID }}
```

#### 保留日志用于问题排查

```plain
- name: Run OpenSCA Scan
  uses: XmirrorSecurity/opensca-scan-action@v1
  with:
    token: ${{ secrets.OPENSCA_TOKEN }}
    need-artifact: "true"
```

#### 上传日志及检测报告至workflow run

```plain
- name: Run OpenSCA Scan
  uses: XmirrorSecurity/opensca-scan-action@v1
  with:
    token: ${{ secrets.OPENSCA_TOKEN }}
    out: "outputs/result.json,outputs/result.html"
    need-artifact: "true"
```

\*仅outputs目录下的结果文件会被上传

### 常见问题

#### Permission denied

若遇permission denied报错，可前往`Settings` -> `Actions` -> `General`，在`Workflow permissions`里选中 "Read and write permissions"并保存

#### 找不到artifact?

在workflow summary页面底部区域，截图示意如下：  
[![](assets/1705890854-ba7c35052cfda1bfda192f23f90b5e33.jpg)](https://xzfile.aliyuncs.com/media/upload/picture/20240118111225-6758eca8-b5af-1.jpg)

如有其他问题或反馈，欢迎向我们提交ISSUE~

[https://github.com/XmirrorSecurity/opensca-scan-action](https://github.com/XmirrorSecurity/opensca-scan-action)
