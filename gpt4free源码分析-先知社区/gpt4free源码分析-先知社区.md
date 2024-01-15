

# gpt4free源码分析 - 先知社区

gpt4free源码分析

- - -

## 简介

项目地址 [https://github.com/xtekky/gpt4free](https://github.com/xtekky/gpt4free)  
该项目能够让用户免费试用GPT，具体的实现是针对公网GPT存在的各种安全问题进行了认证的绕过  
截止写这篇文章的时候 gpt4free使用的GPT3.5的接口有  
[![](assets/1705301720-322e643de8a671dde0b3edf163345c9b.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1702892484031-cc23f5e5-e7bd-4138-afb3-77664dc2715f.png#averageHue=%238cd064&clientId=u80e6ca59-eb0b-4&from=paste&height=514&id=pqjmj&originHeight=771&originWidth=761&originalType=binary&ratio=1&rotation=0&showTitle=false&size=105077&status=done&style=none&taskId=u6d064d7d-3a36-4c22-b525-9bf875f4742&title=&width=507.3333333333333)

另外还有一个很多用户自行搭建的GPT站点 对应的源码是 [https://github.com/Chanzhaoyu/chatgpt-web](https://github.com/Chanzhaoyu/chatgpt-web)

但是老版本存在未授权访问的问题，可以通过未授权直接使用，使用FOFA搜索  
[![](assets/1705301720-de75781d3bf07ac6342f713d6e37ce92.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1702892585883-d6b6112d-d9c6-483a-8b19-394636f44a67.png#averageHue=%230b1527&clientId=u5a2e958e-9ace-4&from=paste&height=491&id=mB9nh&originHeight=736&originWidth=1337&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=102103&status=done&style=none&taskId=u549b8bb1-d876-4cce-a2ec-6486f1cc69f&title=&width=891.3333333333334)  
多尝试几个就可以找到可用的  
[![](assets/1705301720-c4fe33a997a3f378447bdc9bf33ff476.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1702892655948-7fddede3-ff7b-45e5-b70e-6593fb2be648.png#averageHue=%23debe89&clientId=u5a2e958e-9ace-4&from=paste&height=329&id=fNYpM&originHeight=493&originWidth=1753&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=64591&status=done&style=none&taskId=u30517cca-24b0-49e6-a5c2-c06117723ad&title=&width=1168.6666666666667)  
gpt4free使用的GPT4的接口有  
[![](assets/1705301720-faf901b3cce5f5de41d6577f2c4fce91.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1702892807633-3e75136f-e76d-4677-87f4-24f1e9921dc4.png#averageHue=%23c9c280&clientId=u5a2e958e-9ace-4&from=paste&height=247&id=tqNqe&originHeight=371&originWidth=739&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=40326&status=done&style=none&taskId=ub0eb661c-5b89-4bba-aa1d-8fe0db17d4a&title=&width=492.6666666666667)

## 安装运行

运行web版本的

> python .\\g4f\\gui\\run.py

[![](assets/1705301720-717afc621c54bb31827cf4f686b3e56d.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704553567868-cfad4f44-82a0-441c-8c6e-0c70c5f4e190.png#averageHue=%23181817&clientId=u59b017dd-cbbc-4&from=paste&height=314&id=ue01bca5d&originHeight=471&originWidth=1742&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=83104&status=done&style=none&taskId=u167b4bd4-93ed-412d-98be-50c6d572c26&title=&width=1161.3333333333333)  
默认的模型是3.5  
[![](assets/1705301720-72dddd87512e4ddca3171c5b948ab72f.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704553529134-bde34841-115f-409d-bb88-587dcd893989.png#averageHue=%23160e20&clientId=u59b017dd-cbbc-4&from=paste&height=553&id=u0a5cb969&originHeight=830&originWidth=1920&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=221883&status=done&style=none&taskId=uc3364746-52cf-4ec4-9266-4f54e875f10&title=&width=1280)  
切换到gpt4之后就不行了  
[![](assets/1705301720-bd3cc757e8f246dfe00540e3a104cf39.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704554237868-26109578-5cb7-4276-808b-d098135fd8c8.png#averageHue=%23160e20&clientId=u59b017dd-cbbc-4&from=paste&height=549&id=u04f24c77&originHeight=823&originWidth=1920&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=229834&status=done&style=none&taskId=u4aef6ca8-450c-4550-9a1b-9bba3c6a087&title=&width=1280)

也可以使用python包的方式

```plain
import g4f

g4f.debug.logging = False  # Enable debug logging
g4f.debug.check_version = False  # Disable automatic version checking
# print(g4f.Provider.Bing.params)  # Print supported args for Bing

# Using automatic a provider for the given model
## Streamed completion
response = g4f.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "昨天的当天是明天的什么"}],
    stream=True,
)
for message in response:
    print(message, flush=True, end='')
```

输出答案为（实际测试的时候这部分输出等待的时间挺长的）  
[![](assets/1705301720-5b759a1e510a0a064023c5643ec24d69.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1703507397276-3b11795f-92c3-41ca-84ee-13ea3cf0dd12.png#averageHue=%232e2e2d&clientId=u2290c72c-00e3-4&from=paste&height=143&id=rt7MY&originHeight=143&originWidth=563&originalType=binary&ratio=1&rotation=0&showTitle=false&size=9121&status=done&style=none&taskId=u30e6ec89-1fac-4b55-b05f-fadf1c5653c&title=&width=563)  
如果使用GPT4的API

```plain
import g4f

g4f.debug.logging = True  # Enable debug logging
g4f.debug.check_version = False  # Disable automatic version checking

## Normal response
response = g4f.ChatCompletion.create(
    model=g4f.models.gpt_4,
    messages=[{"role": "user", "content": "昨天的当天是明天的什么"}],
)  # Alternative model setting

print(response)
```

在国内IP的情况下 运行结果如下  
[![](assets/1705301720-90c0018752de7b22a5e76a1ba92bcc28.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1703508056531-eefd6a4b-c90a-4452-8e1d-c9318a52cfd9.png#averageHue=%23302c2c&clientId=u2290c72c-00e3-4&from=paste&height=427&id=Y8VUs&originHeight=427&originWidth=1050&originalType=binary&ratio=1&rotation=0&showTitle=false&size=86679&status=done&style=none&taskId=u4499538c-5125-4bc6-8e97-84fcb94cd8e&title=&width=1050)

## 运行流程

从web入口run.py跟进查看

```plain
def run_gui_args(args):
    host = args.host
    port = args.port
    debug = args.debug
    run_gui(host, port, debug)
```

web后端是使用的flask框架，对话的API接口是 /backend-api/v2/conversation  
前端收到了用户的输入之后传递给对应接口  
[![](assets/1705301720-6fe46af4900593e4c495f6d0cf09663c.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704556068391-8a68af77-d345-4078-8573-5c162a0968c2.png#averageHue=%232f2c2b&clientId=u59b017dd-cbbc-4&from=paste&height=407&id=u67b69821&originHeight=611&originWidth=1148&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=86834&status=done&style=none&taskId=ucea0f3ce-8cae-4264-8aa0-51df7472bd0&title=&width=765.3333333333334)  
后台python解析参数并且传递给选择的模型，最后返回结果

```plain
def _conversation(self):
    ......
    messages = request.json['meta']['content']['parts']
    model = model if model else g4f.models.default
    ......
    for chunk in g4f.ChatCompletion.create(
        model=model,
        provider=provider,
        messages=messages,
        stream=True,
        ignore_stream_and_auth=True
    ):
        yield ......
```

默认的模型跟进查看

```plain
default = Model(
    name          = "",
    base_provider = "",
    best_provider = RetryProvider([
        Bing,
        ChatgptAi, GptGo, GeekGpt,
        You,
        Chatgpt4Online
    ])
)
```

这也是相对来说比较稳定的，我们就从这些模型里面学习是如何《偷走》GPT资源的

## 机制绕过

在Provider文件夹下面可以看到所有的模型，下面的部分网址需要使用魔法

### Bing

使用谷歌浏览器访问 [https://bing.com/chat](https://bing.com/chat) ， 进入聊天界面  
[![](assets/1705301720-6c05ca2fa45c416e39adc941f5bc008d.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704962528621-2ca2350e-e540-4a27-8f53-fa5ae2a664da.png#averageHue=%23e2e9f7&clientId=u564ef7ad-5412-4&from=paste&height=414&id=uf20000fc&originHeight=621&originWidth=1800&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=321418&status=done&style=none&taskId=u123b7f87-2290-47cf-aed9-33b9cfe1957&title=&width=1200)  
测试之后可以发现最后返回的数据接口是 wss://sydney.bing.com/sydney/ChatHub  
[![](assets/1705301720-9fd8d3049a912e2d250709f16796c0fa.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704964027637-a0ae7666-58da-49a8-85eb-dc6538ed97a3.png#averageHue=%2383ba5d&clientId=u564ef7ad-5412-4&from=paste&height=213&id=u97cc00da&originHeight=320&originWidth=1902&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=69622&status=done&style=none&taskId=u12e8faf6-4dac-4fcb-95f2-299125e7c05&title=&width=1268)  
需要带上一个 sec\_access\_token  
[![](assets/1705301720-ccd04cf8eebdce23ba6c0da14c9d641a.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704964101367-1dd85ee4-3ec2-4832-acbd-f3cb3476cca9.png#averageHue=%23ededef&clientId=u564ef7ad-5412-4&from=paste&height=217&id=uc44ae5df&originHeight=326&originWidth=1267&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=62887&status=done&style=none&taskId=u57decba7-96f6-4bbe-ac29-847b8a6532e&title=&width=844.6666666666666)  
而sec\_access\_token又在访问/turing/conversation/create?bundleVersion=时会返回在响应头里面作为X-Sydney-Encryptedconversationsignature  
[![](assets/1705301720-14c88e5b1ca40798a12e760276466689.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704964428920-9b558f0d-d249-48d1-bb6f-f00f5e12f181.png#averageHue=%23eb9f78&clientId=u564ef7ad-5412-4&from=paste&height=215&id=u3ba1274f&originHeight=323&originWidth=1903&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=103834&status=done&style=none&taskId=uf64af1a6-9a81-4b4d-8e35-c71df4c520f&title=&width=1268.6666666666667)  
但是好像没有提到我们怎么把prompt传过去的，因为这个是websocket建立链接后进行的，直接在F12里面看不到  
使用burpsuite查看websockets history，这个是我们发过去的数据  
[![](assets/1705301720-77e0d3649c5487d09079566b24115259.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704965622608-d1ea1ad9-7ab6-41fd-a672-dc868390af1a.png#averageHue=%23b3b497&clientId=u564ef7ad-5412-4&from=paste&height=647&id=ub8fa04c4&originHeight=971&originWidth=1920&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=199228&status=done&style=none&taskId=u082dca66-b542-4973-89e0-51a82e2192b&title=&width=1280)  
回复的响应为  
[![](assets/1705301720-0ec68fd5151c97761cfeec350a993bff.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704965751192-1b55082d-6270-4e3f-ba28-122253d52515.png#averageHue=%2391a695&clientId=u564ef7ad-5412-4&from=paste&height=501&id=u23b630e5&originHeight=752&originWidth=1876&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=153586&status=done&style=none&taskId=ua15b2d96-b9c5-4c18-9b5f-b975126d64d&title=&width=1250.6666666666667)  
可以看到是一致的  
[![](assets/1705301720-98c42e7165b17ed3fb1fd2f3b9d1a684.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704965776918-c3969b64-6a42-4049-ad62-404ded989b56.png#averageHue=%23e2eaf7&clientId=u564ef7ad-5412-4&from=paste&height=452&id=u9bdc5a4a&originHeight=678&originWidth=1904&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=104310&status=done&style=none&taskId=u697a44d5-52ef-44eb-b4d3-560805ac7f7&title=&width=1269.3333333333333)  
所以整体步骤就是先获取sec\_access\_token，再组装websocket内容发送出去

#### 获取sec\_access\_token和其他参数

```plain
if __name__ == '__main__':
    url = "https://bing.com/chat"
    url1 = 'https://www.bing.com/turing/conversation/create?bundleVersion=1.1467.3'

    working = True
    supports_message_history = True
    supports_gpt_4 = True
    prompt = "hi"
    context = None
    ip_address = f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"110.0.1587.69"',
        'sec-ch-ua-full-version-list': '"Chromium";v="110.0.5481.192", "Not A(Brand";v="24.0.0.0", "Microsoft Edge";v="110.0.1587.69"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69',
        'x-edge-shopping-flag': '1',
        'x-forwarded-for': ip_address,
    }
    cookies = {
        'SRCHD': 'AF=NOFORM',
        'PPLState': '1',
        'KievRPSSecAuth': '',
        'SUID': '',
        'SRCHUSR': '',
        'SRCHHPGUSR': f'HV={int(time.time())}',
    }
    headers = headers if not cookies else {**headers, "Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items())}

    session = requests.session()
    response = session.get(url1,headers=headers)
    data = json.loads(response.text)
    conversationId = data.get('conversationId')
    clientId = data.get('clientId')
    conversationSignature = response.headers.get('X-Sydney-Encryptedconversationsignature')
    print(f"conversationId:{conversationId}\nclientId:{clientId}\nconversationSignature:{conversationSignature}")
```

可以得到  
[![](assets/1705301720-fa95b3885a9832154a4f673da0a61219.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704967687763-07140a4b-4c20-4b3d-b1b7-e1265be406c7.png#averageHue=%2331302f&clientId=u564ef7ad-5412-4&from=paste&height=164&id=u53745056&originHeight=246&originWidth=1428&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=48342&status=done&style=none&taskId=u05d1ad50-70eb-491b-aff9-e9b89faa615&title=&width=952)

#### 建立websocket连接

源码中使用ClientSession建立websocket连接

```plain
async with ClientSession(
        timeout=ClientTimeout(total=900),
        headers=Defaults.headers if not cookies else {**Defaults.headers, "Cookie": "; ".join(f"{k}={v}" for k, v in cookies.items())},
    ) as session:
    conversation = await create_conversation(session, tone, image, proxy)
    try:
        async with session.ws_connect('wss://sydney.bing.com/sydney/ChatHub', autoping=False, params={'sec_access_token': conversation.conversationSignature}, proxy=proxy) as wss:

            await wss.send_str(format_message({'protocol': 'json', 'version': 1}))
            await wss.receive(timeout=900)
            await wss.send_str(create_message(conversation, prompt, tone, context, web_search, gpt4_turbo))
        ......
```

create\_message用来构建发送的数据，结构如下

```plain
struct = {
    'arguments': [
        {
            'source': 'cib',
            'optionsSets': optionsSets,
            'allowedMessageTypes': allowedMessageTypes,
            'sliceIds': sliceIds,
            'traceId': os.urandom(16).hex(),
            'isStartOfSession': True,
            'requestId': request_id,
            'message': {**location, **{
                'author': 'user',
                'inputMethod': 'Keyboard',
                'text': prompt,
                'messageType': 'Chat',
                'requestId': request_id,
                'messageId': request_id,
            }},
            "scenario": "SERP",
            'tone': tone,
            'spokenTextMode': 'None',
            'conversationId': conversationId,
            'participant': {
                'id': clientId
            },
        }
    ],
    'invocationId': '1',
    'target': 'chat',
    'type': 4
}
```

### Chatgpt4Online

先在网页上找到入口 [https://chatgpt4online.org](https://chatgpt4online.org/)  
[![](assets/1705301720-81bb534188c3468c89e461439d54b197.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704954243938-050dfde1-c948-4c25-baee-c323edd20c19.png#averageHue=%2346c07b&clientId=u564ef7ad-5412-4&from=paste&height=551&id=c9lGi&originHeight=826&originWidth=1899&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=639181&status=done&style=none&taskId=ufb968324-6ded-4a97-aad1-9ef6227a394&title=&width=1266)  
在这个位置可以输入我们的问题 并且获得回复  
具体的接口为 /wp-json/mwai-ui/v1/chats/submit  
header为

> Content-Type:application/json  
> Referer:[https://chatgpt4online.org/](https://chatgpt4online.org/)  
> Sec-Ch-Ua:"Not\_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"  
> Sec-Ch-Ua-Mobile:?0  
> Sec-Ch-Ua-Platform:"Windows"  
> User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36  
> X-Wp-Nonce:03b66db665

X-Wp-Nonce这个值是我们第一次访问该网页会给我们的一个值，这个值在跟GPT对话的时候需要带到header里面去

尝试使用requests库来进行获取

```plain
if __name__ == '__main__':
    url = "https://chatgpt4online.org"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US",
        "content-type": "application/json",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://chatgpt4online.org/",
        "referrer-policy": "strict-origin-when-cross-origin",
    }
    response = requests.get(f"{url}/",headers=headers)
    print(response.text)
    result = re.search(r'restNonce&quot;:&quot;(.*?)&quot;', response.text)
    _wpnonce = ""
    if result:
        _wpnonce = result.group(1)
        print(_wpnonce)
```

可以获取到\_wpnonce  
[![](assets/1705301720-1fb83d446734525120f70478db57e5cd.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704955334809-0470441c-4745-4f02-b43d-0b0512558c6d.png#averageHue=%23302d2d&clientId=u564ef7ad-5412-4&from=paste&height=244&id=KYKZk&originHeight=366&originWidth=1160&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=45678&status=done&style=none&taskId=u69e43411-8610-48d8-b2f3-e0868eda1a6&title=&width=773.3333333333334)  
尝试问个问题

```plain
if __name__ == '__main__':
    url = "https://chatgpt4online.org"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US",
        "content-type": "application/json",
        "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "referer": "https://chatgpt4online.org/",
        "referrer-policy": "strict-origin-when-cross-origin",
    }
    response = requests.get(f"{url}/",headers=headers)
    print(response.text)
    result = re.search(r'restNonce&quot;:&quot;(.*?)&quot;', response.text)
    _wpnonce = ""
    if result:
        _wpnonce = result.group(1)
        print(_wpnonce)

    data = {
        "botId": "default",
        "customId": None,
        "session": "N/A",
        "chatId": get_random_string(11),
        "contextId": 58,
        "messages": [{
            "id": "n1r8ruarf4c",
            "role": "assistant",
            "content": "Hi, How can I help you?",
            "who": "AI: ",
            "timestamp": 1704953575128
        }],
        "newMessage": '你是谁',
        "newImageId": None,
        "stream": True
    }
    print(data)
    response = requests.post(
        f"https://chatgpt4online.org/wp-json/mwai-ui/v1/chats/submit",
        json=data,
        headers={
            "Content-Type":"application/json",
            "Referer":"https://chatgpt4online.org/",
            "Sec-Ch-Ua":'"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile":"?0",
            "Sec-Ch-Ua-Platform":"Windows",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-wp-nonce": _wpnonce
        }
    )
    print(response.text)
```

看来没有问题  
[![](assets/1705301720-b92739a5a6437475b013114308d4591d.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704956518441-410a5931-8fb6-434e-b904-52027c110718.png#averageHue=%232f2e2d&clientId=u564ef7ad-5412-4&from=paste&height=240&id=U8lYl&originHeight=360&originWidth=1777&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=55401&status=done&style=none&taskId=u9d1615a1-5fa3-4b29-b85a-77d5fdbe7b6&title=&width=1184.6666666666667)  
但是在实际测试的过程中 有的时候会被Cloudflare人机验证拦截，所以这个接口也不稳定

### ChatgptAi

网址为 [https://chatgpt.ai](https://chatgpt.ai/)  
这里的实现方式跟Chatgpt4Online是类似的 ，就不再对ChatgptAi进行赘述了  
[![](assets/1705301720-f2728fae3df62b28921b0bdd462297d2.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704960827364-5517d28a-cfcf-4357-8518-908789ff869d.png#averageHue=%23312c2b&clientId=u564ef7ad-5412-4&from=paste&height=316&id=u4e7bc24a&originHeight=474&originWidth=1133&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=63806&status=done&style=none&taskId=ubf83ac26-4d4d-493c-927e-40e560a3cf1&title=&width=755.3333333333334)

### GptGo

查看gpt4free里面的代码 可以知道我们需要先获取到token，然后再带着token去查询答案  
[![](assets/1705301720-4b924f96b4fd64ab3c53679c34a7fcfe.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704959902495-79201bba-8b1c-41e1-b8f5-bfb68d4e9d2f.png#averageHue=%23e0b37c&clientId=u564ef7ad-5412-4&from=paste&height=357&id=u1a3eaf40&originHeight=535&originWidth=1901&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=85814&status=done&style=none&taskId=u329c46cf-e319-4c65-95f7-6c04404c59c&title=&width=1267.3333333333333)  
token在这个里面  
[![](assets/1705301720-0f4743803c4ae5536180f434470f3c9f.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704959790612-b7100803-9229-4806-bdf2-a9795e065f8c.png#averageHue=%23f2af8b&clientId=u564ef7ad-5412-4&from=paste&height=153&id=u9c3b2348&originHeight=229&originWidth=1905&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=36678&status=done&style=none&taskId=u5f4d0894-3214-413d-9c79-c189307bab1&title=&width=1270)  
获取token的python代码

```plain
if __name__ == '__main__':

    url = "https://gptgo.ai"
    message = "hi"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-language": "en-US",
        "Origin": url,
        "Referer": f"{url}/",
        "sec-ch-ua": '"Google Chrome";v="116", "Chromium";v="116", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = requests.session()
    response = session.post(
            "https://gptgo.ai/get_token.php",
            data={"ask": message},
            headers=headers
    )
    token = response.text
    token = base64.b64decode(token[10:-20]).decode()
    print(token)
```

拿到token之后 去访问 web.php 页面  
[![](assets/1705301720-4d77c28679afd4cc59af582e425b5541.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704960585067-bf3f50c7-7bcb-4093-bfa1-e1d646210b92.png#averageHue=%23d8dad8&clientId=u564ef7ad-5412-4&from=paste&height=173&id=u9061a034&originHeight=259&originWidth=1904&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=71000&status=done&style=none&taskId=u285b0dbd-4848-4e0c-8a05-7f542722498&title=&width=1269.3333333333333)  
就可以获取到结果  
[![](assets/1705301720-abfd02a3e95033beebf195f093a07ee5.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704960613622-501681be-b076-4bbf-b770-69310ac4aa01.png#averageHue=%23d8dad8&clientId=u564ef7ad-5412-4&from=paste&height=175&id=u319880aa&originHeight=262&originWidth=1896&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=75175&status=done&style=none&taskId=u789200de-138e-4f58-b65f-d12ca69549a&title=&width=1264)  
所以同步的代码为

```plain
if __name__ == '__main__':

    url = "https://gptgo.ai"
    message = "hi"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-language": "en-US",
        "Origin": url,
        "Referer": f"{url}/",
        "sec-ch-ua": '"Google Chrome";v="116", "Chromium";v="116", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = requests.session()
    response = session.post(
            "https://gptgo.ai/get_token.php",
            data={"ask": message},
            headers=headers
    )
    token = response.text
    token = base64.b64decode(token[10:-20]).decode()
    print(token)

    response = session.get(
            "https://api.gptgo.ai/web.php",
            params={"array_chat": token},
            headers=headers
    )
    print(response.text)
```

输出结果  
[![](assets/1705301720-7c2bf904d2589eb08915a9fb07857b91.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704960672959-01178cf8-72a3-4063-baa4-1a24fefa9621.png#averageHue=%2331302f&clientId=u564ef7ad-5412-4&from=paste&height=349&id=u9ab7f70d&originHeight=524&originWidth=1851&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=125219&status=done&style=none&taskId=u7ab885a8-446a-45f6-9fb7-b67115ad552&title=&width=1234)

### GeekGpt

这里的网址是 [https://chat.geekgpt.org/](https://chat.geekgpt.org/)

[![](assets/1705301720-6bd8da65192cf5b1de83620577961de9.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1703508800248-e2a060e8-c2bc-4451-a772-5c87a02ee82e.png#averageHue=%23373742&clientId=u2290c72c-00e3-4&from=paste&height=959&id=Co4Vu&originHeight=959&originWidth=1917&originalType=binary&ratio=1&rotation=0&showTitle=false&size=60304&status=done&style=none&taskId=u28213d57-ca9d-4952-bae6-3f63776b1ea&title=&width=1917)  
这里就是剩余的余额，也就是说每个用户都会有一定初始额度  
[![](assets/1705301720-1b9f506190b96afb67d79e07e3a9ed65.png)](https://cdn.nlark.com/yuque/0/2023/png/21398751/1703508838548-5928aab0-f65e-4078-bcf6-8aedf2c492e7.png#averageHue=%233c3c49&clientId=u2290c72c-00e3-4&from=paste&height=453&id=kOz2s&originHeight=453&originWidth=884&originalType=binary&ratio=1&rotation=0&showTitle=false&size=21924&status=done&style=none&taskId=u1db1a2d0-6648-45f0-a889-ec2bfbae6cb&title=&width=884)  
根据源码找接口  
[![](assets/1705301720-2354361c63619c7066551e736deb7831.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704957859877-1ba7cf00-dfe3-4c08-be98-98677d883c08.png#averageHue=%23dde0dd&clientId=u564ef7ad-5412-4&from=paste&height=167&id=u5e510ada&originHeight=251&originWidth=1753&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=34873&status=done&style=none&taskId=u77f2fc8a-2bfd-4947-b1e7-6d5159f6e17&title=&width=1168.6666666666667)  
带上payload来进行访问

```plain
if __name__ == '__main__':
    messages = [
        {
            "content": "You are ChatGPT, a large language model trained by OpenAI.\nCarefully heed the user's instructions. \nRespond using Markdown.",
            "role": "system"
        },
        {
            "content": "who are you",
            "role": "user"
        }
    ]
    model = "gpt-3.5-turbo"
    json_data = {
        'messages': messages,
        'model': model,
        'temperature':  1,
        'presence_penalty': 0,
        'top_p': 1,
        'frequency_penalty':  0,
        'stream': True
    }

    data = json.dumps(json_data, separators=(',', ':'))

    headers = {
        'authority': 'Bearer pk-this-is-a-real-free-pool-token-for-everyone',
        # 'authority': 'ai.fakeopen.com',
        'accept': '*/*',
        'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
        'authorization': 'Bearer pk-this-is-a-real-free-pool-token-for-everyone',
        'content-type': 'application/json',
        'origin': 'https://chat.geekgpt.org',
        'referer': 'https://chat.geekgpt.org/',
        'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }

    response = requests.post("https://ai.fakeopen.com/v1/chat/completions",
                             headers=headers, data=data, stream=True)
    print(response.text)
    response.raise_for_status()

    for chunk in response.iter_lines():
        if b'content' in chunk:
            json_data = chunk.decode().replace("data: ", "")

            if json_data == "[DONE]":
                break

            try:
                content = json.loads(json_data)["choices"][0]["delta"].get("content")
            except Exception as e:
                raise RuntimeError(f'error | {e} :', json_data)

            if content:
                print(content)
```

实际测试的过程中发现authority是Bearer pk-this-is-a-real-free-pool-token-for-everyone  
[![](assets/1705301720-ee1bfa25e9c51d6976af737c45364c36.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704959355214-e90878fc-e54c-4b28-8de2-9fae999295be.png#averageHue=%23f5eeee&clientId=u564ef7ad-5412-4&from=paste&height=168&id=ufc1958aa&originHeight=252&originWidth=1215&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=25665&status=done&style=none&taskId=u01089ac5-32ee-435d-be17-820b8cb020f&title=&width=810)  
[![](assets/1705301720-21e419a0c0c52d1a2baf080ffea4d220.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704959406533-58050036-a829-4e5c-a66f-018daccef563.png#averageHue=%232c2c2b&clientId=u564ef7ad-5412-4&from=paste&height=395&id=u37dd95d5&originHeight=592&originWidth=739&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=16746&status=done&style=none&taskId=u662879bf-e3d3-4307-99d5-4fd6e9e15a8&title=&width=492.6666666666667)  
不过使用 ai.fakeopen.com 也有返回结果，还挺奇怪的

### You

网址是 [https://you.com](https://you.com")，谷歌F12打开查看网络流，观察可知接口是 [/api/streamingSearch](https://you.com/api/streamingSearch)  
[![](assets/1705301720-a3ef028ecde59cba043318600e4c5ed5.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704557824082-117d5b1c-a277-424e-87e5-6db7177cdce8.png#averageHue=%23e2b57f&clientId=u59b017dd-cbbc-4&from=paste&height=362&id=u5ee4bb2f&originHeight=543&originWidth=1910&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=110004&status=done&style=none&taskId=ub852334e-997c-465c-a0ca-73a5c1a3f30&title=&width=1273.3333333333333)  
不过代码里面将部分冗余的参数进行了省略  
手动在浏览器里面访问 [https://you.com/api/streamingSearch?q=hi&domain=youchat&chat=](https://you.com/api/streamingSearch?q=hi&domain=youchat&chat=)  
可以看到后面返回的内容也就是GPT返回的答案  
[![](assets/1705301720-a8c93d9f64cce758fe1429bc452023e7.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704560051348-82dc9c51-a2fa-46cc-971d-1eafe49d6815.png#averageHue=%23fdfcf0&clientId=u59b017dd-cbbc-4&from=paste&height=547&id=ue044718d&originHeight=821&originWidth=916&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=86432&status=done&style=none&taskId=ud63c4363-ea49-458f-88f0-d1a983f89f6&title=&width=610.6666666666666)  
然而如果把You的代码改为同步

```plain
import requests

def fetch_chat_data():
    url = "https://you.com"
    messages = "hi"
    headers = {
        "Accept": "text/event-stream",
        "Referer": f"{url}/search?fromSearchBar=true&tbm=youchat",
    }
    data = {"q": messages, "domain": "youchat", "chat": ""}
    response = requests.get(
        f"{url}/api/streamingSearch",
        params=data,
        headers=headers,
        timeout= 120
    )
    print(response.text)


if __name__ == '__main__':
    fetch_chat_data()
```

直接使用不太稳定，因为目标存在检测  
[![](assets/1705301720-7615ade7afac555f62222017803415f1.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704788815964-670f0f24-3555-46f5-85f9-a0a59d16639f.png#averageHue=%232d2b2b&clientId=u7dc511ac-f8af-4&from=paste&height=244&id=ub2d0186b&originHeight=366&originWidth=1461&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=24580&status=done&style=none&taskId=u2f80bed8-c9c9-45e5-9eff-c18f34f3016&title=&width=974)

[![](assets/1705301720-5589eec88e1a3a13218a3cddbbcea783.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704788729484-78f10a1c-1e44-440a-99bc-bfb4c94609bf.png#averageHue=%23fcfcfc&clientId=u7dc511ac-f8af-4&from=paste&height=471&id=u42d19898&originHeight=706&originWidth=1116&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=39858&status=done&style=none&taskId=u9d20f4f2-f1f9-4c99-b5c5-1325e9bd2fc&title=&width=744)  
为了规避特征检测，原代码里面使用了curl\_cffi impersonate进行绕过

```plain
async with StreamSession(proxies={"https": proxy}, impersonate="chrome107", timeout=timeout) as session:
```

这里我们简单测试一下  
使用浏览器访问 [https://tls.browserleaks.com/json](https://tls.browserleaks.com/json)  
[![](assets/1705301720-e4458e371b05f1ab6638340b33b10e3a.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704790013368-6d1c19eb-9df0-4485-8a89-7efbb86e998a.png#averageHue=%23fcfbfa&clientId=u7dc511ac-f8af-4&from=paste&height=220&id=uad1c7361&originHeight=330&originWidth=1697&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=68944&status=done&style=none&taskId=u60d41c77-fd5d-4fe4-ab80-f888862fe82&title=&width=1131.3333333333333)  
可以看到akamai\_hash akamai\_text两个字段都是有值的  
但是用下面的代码进行requests访问

```plain
import json
import requests
def test():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46',
    }

    response = requests.get('https://tls.browserleaks.com/json', headers=headers)
    data = response.json()

    formatted_data = json.dumps(data, indent=4)
    print(formatted_data)

if __name__ == '__main__':
    test()
```

[![](assets/1705301720-712e452b8ddcd06cada1b5e6d4b5c891.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704790101795-83191b8f-7569-4b65-851b-1941aa3f3187.png#averageHue=%232f2d2c&clientId=u7dc511ac-f8af-4&from=paste&height=298&id=u7d8e3911&originHeight=447&originWidth=1140&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=57101&status=done&style=none&taskId=uecf9f454-4924-4b5b-99ce-f6b8672613e&title=&width=760)  
现在就为空了

> 这里的akamai是一家提供内容传输网络（Content Delivery Network，CDN）和网络安全解决方案的公司  
> 在签名防爬虫方面，Akamai 提供了一种称为 "EdgeScape Threat Intelligence" 的功能。这个功能可以根据客户端请求的特征生成一个加密签名（通常是一个短字符串），将该签名添加到请求中的 HTTP 头部或参数中。然后，目标网站可以使用 Akamai 提供的 SDK 或 API 验证并解析该签名，以确认请求是否来自合法的 Akamai 代理，而不是恶意机器人直接访问。

针对You网站的反爬使用curl\_cffi来生成对应浏览器版本的指纹信息，在一定程度上防止被检测到

```plain
import json
from curl_cffi import requests

def test():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46',
    }

    response = requests.get('https://tls.browserleaks.com/json', headers=headers
                            ,impersonate="chrome110")
    data = response.json()

    formatted_data = json.dumps(data, indent=4)
    print(formatted_data)

if __name__ == '__main__':
    test()
```

[![](assets/1705301720-36d7dcad355242caa7ea86d904797b49.png)](https://cdn.nlark.com/yuque/0/2024/png/21398751/1704790395650-6110e515-a259-4df4-a7d1-4c3cf252a362.png#averageHue=%23302e2d&clientId=u7dc511ac-f8af-4&from=paste&height=247&id=u1ba2a4e4&originHeight=370&originWidth=1107&originalType=binary&ratio=1.5&rotation=0&showTitle=false&size=60841&status=done&style=none&taskId=ua69e5df8-8b0f-48b3-b38e-9d64a666143&title=&width=738)  
现在就会自带浏览器的指纹信息了

## 参考链接

-   [https://github.com/xtekky/gpt4free](https://github.com/xtekky/gpt4free)
-   [https://github.com/Cl0udG0d/Fofa-hack](https://github.com/Cl0udG0d/Fofa-hack)
-   [https://cloud.tencent.com/developer/article/2278728](https://cloud.tencent.com/developer/article/2278728)
-   [https://blog.csdn.net/resphina/article/details/132507212](https://blog.csdn.net/resphina/article/details/132507212)
-   [https://www.kingname.info/2023/10/17/curl-cffi/](https://www.kingname.info/2023/10/17/curl-cffi/)
-   [https://linweiyuan.github.io/2023/03/14/%E4%B8%80%E7%A7%8D%E5%8F%96%E5%B7%A7%E7%9A%84%E6%96%B9%E5%BC%8F%E7%BB%95%E8%BF%87-Cloudflare-v2-%E9%AA%8C%E8%AF%81.html](https://linweiyuan.github.io/2023/03/14/%E4%B8%80%E7%A7%8D%E5%8F%96%E5%B7%A7%E7%9A%84%E6%96%B9%E5%BC%8F%E7%BB%95%E8%BF%87-Cloudflare-v2-%E9%AA%8C%E8%AF%81.html)
-   [https://mp.weixin.qq.com/s/efloBirboVfH2hK3cNoU5A](https://mp.weixin.qq.com/s/efloBirboVfH2hK3cNoU5A)
