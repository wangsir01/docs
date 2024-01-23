

# 从日志文件泄露Dingtalk API秘钥到利用 - 先知社区

从日志文件泄露Dingtalk API秘钥到利用

- - -

### 发现 Dingtalk API 秘钥

今天遇到个日志文件泄露

里面有钉钉的appkey和appsecret

第一次见感觉挺新奇的就写个文章记录下

访问 [http://xxx.edu.cn/Login.aspx](http://xxx.edu.cn/Login.aspx) 如下图所示

[![](assets/1705975182-46efcc1156f7d3820681664209990c31.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121202904-a9f0fbfe-b858-1.png)

稍稍测了一下没弱口令也没啥裸的接口

扫了一下目录吧...

[![](assets/1705975182-38e520403cdfc2a209e9e231d51592ee.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121202924-b5db7dcc-b858-1.png)

发现有个日志文件

其中存在 dingtalk 的 appkey 和 appsecret

[![](assets/1705975182-9c486c38b5447e12999e679e7560cdfe.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121202950-c5abc5fe-b858-1.png)

拿着 appkey 和 appscret 到以下钉钉的开放 Api 去拿 access\_token

[https://open-dev.dingtalk.com/apiExplorer#/?devType=org&api=oauth2\_1.0%23GetAccessToken](https://open-dev.dingtalk.com/apiExplorer#/?devType=org&api=oauth2_1.0%23GetAccessToken)

[![](assets/1705975182-3e3b5f72427dc85ef207803576562655.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121203012-d24e1d7a-b858-1.png)

拿到 access\_token 后，在浏览器上直接访问接口去测试是否可用

（注意：不要直接在钉钉调，会说不是所属企业，但实际上是可以调的）

### 利用 Dingtalk API 秘钥

#### 获取所有角色

[https://oapi.dingtalk.com/topapi/role/list](https://oapi.dingtalk.com/topapi/role/list)

POST：access\_token=xxxxxxxx&dept\_id=1

（PS：这里面的dept\_id是指部门编号，1就是根部门编号，由于是必要参数所以就带上了）

[![](assets/1705975182-af3b727fbb315cf387648790b478a39e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121203137-05726daa-b859-1.png)

#### 获取某角色组下所有成员

[https://oapi.dingtalk.com/topapi/role/simplelist](https://oapi.dingtalk.com/topapi/role/simplelist)

POST：access\_token=xxxxxxxxxxx&role\_id=1054994944

[![](assets/1705975182-0d8fd1a3bf6b34cbf14af762d162d52a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121203243-2c6b1eac-b859-1.png)

#### 获取特定成员的详细信息

[https://oapi.dingtalk.com/topapi/v2/user/get](https://oapi.dingtalk.com/topapi/v2/user/get)

POST：access\_token=xxxxxxxxxxxxxx&userid=xxxxxxxxxxxxxxxx

[![](assets/1705975182-6cabe6e912c195f3e12d77fad3ebc0e9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121203317-40cedf0a-b859-1.png)

因为之前没见过钉钉的秘钥泄露，所以不清楚是啥危害

于是上群问了一下，有个师傅说 dingtalk 是有个接口可以上传文件的

然后私发了我张截图

[![](assets/1705975182-063f63a64d871ba504acff67102f82fd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121203335-4bbcb068-b859-1.png)

简单尝试了下不行，给师傅也试了下，也不行

虽然没利用成功，但这也不妨碍我的大胆幻想

如果能够利用成功上传文件呢？

[![](assets/1705975182-3e7e9bf61f57aefa961838e80ff4081a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121203354-56c6e352-b859-1.png)

哈哈哈结束了

[![](assets/1705975182-0a05c9fdf38f9711ea03c8380bb1d760.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240121203410-603c07e6-b859-1.png)

最后参考了下湘南第一深情师傅的文章

就当这个洞是中危吧

（PS：因为打歪了这个资产不属于目标资产的所以被拒了呜呜呜呜呜）
