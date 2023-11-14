

# Finding A RCE Gadget Chain In WordPress Core | WPScan --- 在 WordPress 核心中寻找 RCE 小工具链 |WPS扫描

October 13, 2023 10月 13， 2023

# Finding A RCE Gadget Chain In WordPress Core  
在 WordPress Core 中寻找 RCE 小工具链

During a recent team gathering in Belgium, we had an impromptu [Capture The Flag](https://en.wikipedia.org/wiki/Capture_the_flag_(cybersecurity)) game that included a challenge with an SQL Injection vulnerability occurring inside an `INSERT` statement, meaning attackers could inject random stuff into the targeted table’s columns, and query information from the database, the intended “flag” being the credentials of a user on the affected blog.  
在最近在比利时举行的一次团队聚会中，我们进行了一次即兴的 Capture The Flag 游戏，其中包括 `INSERT` 一个在语句中发生的 SQL 注入漏洞的挑战，这意味着攻击者可以将随机内容注入目标表的列中，并从数据库中查询信息，预期的“标志”是受影响博客上用户的凭据。

The vulnerable SQL query inserted new rows into the `wp_termmeta` table, which while we knew it could potentially lead to [Object Injection attacks](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection) due to the inserted [metadata being passed through maybe\_unserialize upon retrieval](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/meta.php#L657), we didn’t think too much about it since the common thought on the matter was that there was no known current RCE gadget chain in WordPress Core, and thus the challenge was “safe” since it didn’t use any other external plugins.  
易受攻击的 SQL 查询在表中 `wp_termmeta` 插入了新行，虽然我们知道它可能会导致对象注入攻击，因为插入的元数据在检索时会通过maybe\_unserialize传递，但我们并没有想太多，因为关于此事的普遍想法是 WordPress Core 中没有已知的当前 RCE 小工具链， 因此，挑战是“安全的”，因为它没有使用任何其他外部插件。

This proved to be enough to win that flag, however, the thought that there might be an alternative solution to the challenge piqued our curiosity. What if *there was* a working RCE gadget chain in Core waiting to be found?  
事实证明，这足以赢得这面旗帜，然而，一想到可能有替代解决方案来应对这一挑战，就激起了我们的好奇心。如果 Core 中有一个有效的 RCE 小工具链等待被发现怎么办？

Turns out, there *was* a way, which the [WordPress Security Team fixed on version 6.3.2](https://wordpress.org/news/2023/10/wordpress-6-3-2-maintenance-and-security-release/) by preventing several classes used in the final chain from either being unserialized at all, or restricting what some of their unserialized properties may contain.  
事实证明，有一种方法可以，WordPress 安全团队在 6.3.2 版上修复了这种方法，它阻止了最终链中使用的几个类完全被反序列化，或者限制了它们的一些未序列化属性可能包含的内容。

## Building An RCE Gadget Chain For WordPress Core  
为 WordPress 核心构建 RCE 小工具链

There are many ways to initiate this POP chain, but we elected to use one that is very flexible: triggering [the \_\_toString magic method](https://www.php.net/manual/en/language.oop5.magic.php#object.tostring) when whatever is being unserialized (or one of its internal components) is used like a string. To do so, we flagged [WordPress’ WP\_Theme class](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/class-wp-theme.php#L503) as a potentially good starting point for our chain:  
有很多方法可以启动这个 POP 链，但我们选择使用一种非常灵活的方法：当任何被反序列化的东西（或其内部组件之一）像字符串一样使用时，触发 \_\_toString 魔术方法。为此，我们将 WordPress 的 WP\_Theme 类标记为我们链的潜在良好起点：

```php
 /**
  * When converting the object to a string, the theme name is returned.
  *
  * @since 3.4.0
  *
  * @return string Theme name, ready for display (translated)
  */
public function __toString() {
  return (string) $this->display( 'Name' );
}
```

When used as a string, it calls `$this‑>display( 'Name' );`, which itself calls `$this‑>get( 'Name' );`:  
当用作字符串时，它调用 ，它本身调用 `$this‑>display( 'Name' );` `$this‑>get( 'Name' );` ：

```php
public function get( $header ) {
  if ( ! isset( $this->headers[ $header ] ) ) {
   return false;
  }

  if ( ! isset( $this->headers_sanitized ) ) {
   $this->headers_sanitized = $this->cache_get( 'headers' );
   if ( ! is_array( $this->headers_sanitized ) ) {
    $this->headers_sanitized = array();
   }
  }

  if ( isset( $this->headers_sanitized[ $header ] ) ) {
   return $this->headers_sanitized[ $header ];
  }

  // If themes are a persistent group, sanitize everything and cache it. One cache add is better than many cache sets.
  if ( self::$persistently_cache ) {
   foreach ( array_keys( $this->headers ) as $_header ) {
    $this->headers_sanitized[ $_header ] = $this->sanitize_header( $_header, $this->headers[ $_header ] );
   }
   $this->cache_add( 'headers', $this->headers_sanitized );
  } else {
   $this->headers_sanitized[ $header ] = $this->sanitize_header( $header, $this->headers[ $header ] );
  }

  return $this->headers_sanitized[ $header ];
}
```

`WP_Theme::get( $header )` accesses a lot of internal properties assuming they are arrays, a reasonable assumption to make in normal times. However, since we fully control the instance (we serialized it ourselves!), we can make those properties contain anything, including other classes that implement [the ArrayAccess interface](https://www.php.net/manual/en/class.arrayaccess.php).  
`WP_Theme::get( $header )` 访问许多内部属性，假设它们是数组，这在正常情况下是一个合理的假设。但是，由于我们完全控制了实例（我们自己序列化了它！），我们可以使这些属性包含任何内容，包括实现 ArrayAccess 接口的其他类。

These types of classes behave roughly like arrays, implementing their “array‑like” functionality by putting their logic in the `offsetGet`, `offsetSet`, `offsetExists`, and `offsetUnset` methods.  
这些类型的类的行为大致类似于数组，通过将它们的逻辑放在 `offsetGet` 、 、 `offsetSet` `offsetExists` 和 `offsetUnset` 方法中来实现它们的“类数组”功能。

## Pivoting, And Pivoting Again  
旋转，再次旋转

This is where this POP chain code logic becomes kind of convoluted.  
这就是这个POP链码逻辑变得有点复杂的地方。

Scavenging for classes that use the ArrayAccess interface in interesting ways led us to [the WP\_Block\_List class](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/class-wp-block-list.php#L81):  
通过搜索以有趣的方式使用 ArrayAccess 接口的类，我们找到了 WP\_Block\_List 类：

```php
public function offsetGet( $index ) {
  $block = $this->blocks[ $index ];

  if ( isset( $block ) && is_array( $block ) ) {
   $block                  = new WP_Block( $block, $this->available_context, $this->registry );
   $this->blocks[ $index ] = $block;
  }

  return $block;
}
```

The `$index` parameter contains `'Name'`, and we can set `$this‑>blocks` to whatever we want, which means we have full control over what `$block` contains. This is handy because the code instantiates a `WP_Block` class using three parameters we have full control over.  
`$index` 参数包含 ，我们可以设置为 `$this‑>blocks` 任何我们想要的东西，这意味着我们可以完全控制包含 `'Name'` 的内容 `$block` 。这很方便，因为代码使用我们可以完全控制的三个参数实例化一个 `WP_Block` 类。

```php
public function __construct( $block, $available_context = array(), $registry = null ) {
  $this->parsed_block = $block;
  $this->name         = $block['blockName'];

  if ( is_null( $registry ) ) {
   $registry = WP_Block_Type_Registry::get_instance();
  }

  $this->registry = $registry;

  $this->block_type = $registry->get_registered( $this->name );
```

The `WP_Block` class’ constructor uses the `$registry` parameter, which it expects to be an instance of a class that extends `WP_Block_Type_Registry`, to get registered block types via [its get\_registered() method](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/class-wp-block-type-registry.php#L132). Note that we control both `$registry` *and* `$this‑>name` here.  
`WP_Block` 类的构造函数使用参数 `$registry` ，它期望该参数是扩展 `WP_Block_Type_Registry` 类的实例，通过其 get\_registered（） 方法获取已注册的块类型。请注意，我们控制两者 `$registry` 和 `$this‑>name` 这里。

```php
public function get_registered( $name ) {
  if ( ! $this->is_registered( $name ) ) {
   return null;
  }

  return $this->registered_block_types[ $name ];
}
```

As you can see again, we have *another* interesting POP chain primitive right there. The `$this‑>registered_block_types[ $name ]` snippet allows us to do the `offsetGet` trick again, with the important difference that this time around, we actually decide which array index we’re retrieving!  
正如你所看到的，我们还有另一个有趣的POP链原语。该 `$this‑>registered_block_types[ $name ]` 代码片段允许我们再次执行该 `offsetGet` 操作，但重要的区别在于，这一次，我们实际上决定了要检索的数组索引！

Knowing that, let’s pivot back to [the WP\_Theme class](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/class-wp-theme.php#L643), which *also* implements the `ArrayAccess` interface.  
知道了这一点，让我们回到 WP\_Theme 类，它也实现了 `ArrayAccess` 接口。

```php
public function offsetGet( $offset ) {
  switch ( $offset ) {
   // (... Bunch of less interesting offset to choose from ...)
   case 'Parent Theme':
    return $this->parent() ? $this->parent()->get( 'Name' ) : '';
```

The point of interest here is what happens when we try to grab the `Parent Theme` offset. The method calls [$this‑>parent()](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/class-wp-theme.php#L731), which essentially just returns `$this‑>parent` if it is set, and calls that object’s `get()` method.  
这里的兴趣点是当我们试图抓住 `Parent Theme` 偏移量时会发生什么。该方法调用 $this->parent（），它本质上只返回 `$this‑>parent` （如果它被设置），并调用该对象 `get()` 的方法。

Now, `get()` is a very common method name, so surely we might be able to have `$this‑>parent` contain an instance of a class other than `WP_Theme`, which also happens to contain a method with the same name?  
现在，是一个非常常见的方法名称，那么我们肯定可以包含一个类的实例，而不是 `WP_Theme` ， `get()` 它恰好也 `$this‑>parent` 包含一个同名的方法？

## Will It Get() Better? 它会变得更好吗？

The [WpOrg\\Requests\\Session class](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/Requests/src/Session.php#L148) (formerly known as [Requests\_Session](https://developer.wordpress.org/reference/classes/requests_session/) before WordPress introduced more namespaces in Core) has what we’re looking for:  
WpOrg\\Requests\\Session 类（在 WordPress 在 Core 中引入更多命名空间之前称为 Requests\_Session）具有我们正在寻找的内容：

```php
public function get($url, $headers = [], $options = []) {
  return $this->request($url, $headers, null, Requests::GET, $options);
}
```

Note that we only know the first parameter (`$url`), and can’t change it because it’s hardcoded. The method is almost just an alias for the [WpOrg\\Requests\\Session::request() method](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/Requests/src/Session.php#L210), it only hardcodes the HTTP method to be used (not that it matters to us):  
请注意，我们只知道第一个参数 （ `$url` ），并且无法更改它，因为它是硬编码的。该方法几乎只是 WpOrg\\Requests\\Session：：request（） 方法的别名，它只对要使用的 HTTP 方法进行硬编码（对我们来说并不重要）：

```php
public function request($url, $headers = [], $data = [], $type = Requests::GET, $options = []) {
  $request = $this->merge_request(compact('url', 'headers', 'data', 'options'));

  return Requests::request($request['url'], $request['headers'], $request['data'], $type, $request['options']);
}
```

The `request` method is relatively straightforward, it does some processing with the parameters it received before handing off the actual request process to `Requests::request()`.  
该 `request` 方法相对简单，在将实际的请求过程移交给之前，它会对收到的参数进行一些处理 `Requests::request()` 。

Let’s have a look at what [the $this‑>merge\_request() method](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/Requests/src/Session.php#L268) does:  
让我们看一下 $this->merge\_request（） 方法的作用：

```php
protected function merge_request($request, $merge_options = true) {
  if ($this->url !== null) {
   $request['url'] = Iri::absolutize($this->url, $request['url']);
   $request['url'] = $request['url']->uri;
  }

  if (empty($request['headers'])) {
   $request['headers'] = [];
  }

  $request['headers'] = array_merge($this->headers, $request['headers']);

  if (empty($request['data'])) {
   if (is_array($this->data)) {
    $request['data'] = $this->data;
   }
  } elseif (is_array($request['data']) && is_array($this->data)) {
   $request['data'] = array_merge($this->data, $request['data']);
  }

  if ($merge_options === true) {
   $request['options'] = array_merge($this->options, $request['options']);

   // Disallow forcing the type, as that's a per request setting
   unset($request['options']['type']);
  }

  return $request;
}
}
```

TL;DR: This method merges the parameters it received with some of its internal properties (`$this‑>url`, `$this‑>headers`, `$this‑>options`, etc.)… which we happen to control too since we created that instance from scratch! 🙂  
TL;DR：此方法将它收到的参数与其一些内部属性（ 、 `$this‑>url` 、 `$this‑>headers` `$this‑>options` 等）合并...由于我们从头开始创建了该实例，因此我们碰巧也控制了它！🙂

As such, we have *very* high control of whatever requests we’re about to launch, which could be useful in SSRF attack scenarios. With the exception of the request’s type (aka. method) and path, we can basically control everything. However, we promised we’d get code execution, and we will.  
因此，我们对即将启动的任何请求都有非常高的控制权，这在 SSRF 攻击场景中可能很有用。除了请求的类型（又名方法）和路径之外，我们基本上可以控制一切。但是，我们承诺我们会执行代码，我们会的。

We’ll leave SSRF as an exercise for the reader, but getting to this point is a pretty good way to better grasp what comes next.  
我们将把 SSRF 作为读者的练习，但达到这一点是更好地掌握接下来会发生什么的好方法。

## Popping Shells With Captain Hook  
用胡克船长爆破炮弹

```php
public static function request($url, $headers = [], $data = [], $type = self::GET, $options = []) {

        // (...) Uninteresting code (...)

  $options['hooks']->dispatch('requests.before_request', [&$url, &$headers, &$data, &$type, &$options]);
```

The [WpOrg\\Requests\\Requests::request() method](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/Requests/src/Requests.php#L429) has *at least* one thing that catches the eye of anyone who’s remotely familiar with WordPress’ fondness for dynamic function callbacks (like it uses for making actions and filters work). One of them is a line where it grabs `$options['hooks']`, which is presumably meant to contain a [WpOrg\\Requests\\Hooks](https://core.trac.wordpress.org/browser/tags/6.2/src/wp-includes/Requests/src/Hooks.php) instance.  
WpOrg\\Requests\\Requests：：request（） 方法至少有一件事可以吸引任何熟悉 WordPress 对动态函数回调的喜爱的人的眼球（就像它用于使操作和过滤器工作一样）。其中之一是它抓取的一行，据推测 `$options['hooks']` ，该行可能包含一个 WpOrg\\Requests\\Hooks 实例。

If you recall (or might actually just guess at this point, we control everything!), we actually have a say in what instance should go in `$options['hooks']`! Except now, we’ll give it exactly what it expects, perhaps with a couple personalized hooks and tricks to have it call functions and methods of our choice.  
如果你还记得（或者实际上可能只是在这一点上猜测，我们控制着一切！），我们实际上对应该进入 `$options['hooks']` 什么情况有发言权！除了现在，我们将完全按照它的期望，也许会有一些个性化的钩子和技巧，让它调用我们选择的函数和方法。

The Hooks::dispatch method is defined as the following:  
Hooks：:d ispatch 方法定义如下：

```php
public function dispatch($hook, $parameters = []) {
  if (is_string($hook) === false) {
   throw InvalidArgument::create(1, '$hook', 'string', gettype($hook));
  }

  // Check strictly against array, as Array* objects don't work in combination with `call_user_func_array()`.
  if (is_array($parameters) === false) {
   throw InvalidArgument::create(2, '$parameters', 'array', gettype($parameters));
  }

  if (empty($this->hooks[$hook])) {
   return false;
  }

  if (!empty($parameters)) {
   // Strip potential keys from the array to prevent them being interpreted as parameter names in PHP 8.0.
   $parameters = array_values($parameters);
  }

  ksort($this->hooks[$hook]);

  foreach ($this->hooks[$hook] as $priority => $hooked) {
   foreach ($hooked as $callback) {
    $callback(...$parameters);
   }
  }

  return true;
}
```

As expected, this is very reminiscent of how add\_action() and add\_filter() work. We can define `$this‑>hooks` to whatever we want, and have the method call it. Still, we’re facing two relatively important issues:  
不出所料，这很容易让人想起 add\_action（） 和 add\_filter（） 的工作方式。我们可以定义 `$this‑>hooks` 任何我们想要的东西，并让方法调用它。尽管如此，我们仍然面临着两个相对重要的问题：

-   The first parameter we control *has* to be a URL due to the `Session::merge_request()` from earlier  
    我们控制的第一个参数必须是 URL，因为 `Session::merge_request()`
-   We’re sending a total of 5 parameters, which can be a problem if our goal is to call PHP functions, like `system()`, because they’re stricter about parameter types, and count.  
    我们总共发送了 5 个参数，如果我们的目标是调用 PHP 函数，这可能是一个问题，例如 `system()` ，因为它们对参数类型和计数更严格。

Since user‑defined functions and methods do *not* share that latter constraint, what we can do to make it easier on us is to recurse once by having the method call itself with the parameters we provided, which will effectively shift all the variables we control to the left.  
由于用户定义的函数和方法不共享后一个约束，因此我们可以做的是让方法使用我们提供的参数调用自身来递归一次，这将有效地将我们控制的所有变量向左移动。

In other words, the first Hooks::dispatch() call we did used the following parameters:  
换句话说，我们所做的第一个 Hooks：:d ispatch（） 调用使用了以下参数：

```php
$options['hooks']->dispatch('requests.before_request', [&$url, &$headers, &$data, &$type, &$options])
```

and recursing into the method once is functionally equivalent to letting us do:  
并且递归到方法中一次在功能上等同于让我们这样做：

```php
$options['hooks']->dispatch($url, $headers, &$data, &$type, &$options])
```

As mentioned before: user‑defined methods ignore additional, undefined parameters. Since the `Hooks::dispatch()` method only uses two, the `$data`, `$type`, and `$options` variable will simply not be used at all, while the `$url` variable will be used as the hook’s name instead of a parameter.  
如前所述：用户定义的方法会忽略其他未定义的参数。由于该 `Hooks::dispatch()` 方法仅使用两个，因此根本不会使用 ， 和 `$options` 变量 `$data` ， `$type` 而变量 `$url` 将用作钩子的名称而不是参数。

### How Do You Build The Payload?  
如何构建有效载荷？

Putting all the necessary pieces in the right order for everything to work is relatively tricky since we have to make sure a number of things align properly. However, the resulting code allows to run any PHP commands, including [system()](https://www.php.net/manual/en/function.system.php), allowing an attacker to execute arbitrary commands on the server. For obvious reasons, we will not be sharing the actual proof of concept publicly.  
将所有必要的部分按正确的顺序排列以使一切正常工作是相对棘手的，因为我们必须确保许多事情正确对齐。但是，生成的代码允许运行任何 PHP 命令，包括 system（），从而允许攻击者在服务器上执行任意命令。出于显而易见的原因，我们不会公开分享实际的概念验证。

### Share this: 分享此页：

-   [Twitter](https://wpscan.com/blog/finding-a-rce-gadget-chain-in-wordpress-core/?share=twitter&nb=1 "Click to share on Twitter")
-   [Facebook](https://wpscan.com/blog/finding-a-rce-gadget-chain-in-wordpress-core/?share=facebook&nb=1 "Click to share on Facebook")
 推特脸书

[↓↓↓](# "2 bloggers like this.")  
  
Like  
  
[↑↑↑](# "2 bloggers like this.")

-   [↓↓↓](https://gravatar.com/alexsanford1 "Alex Sanford")  
      
    ![Alex Sanford](assets/1699429224-004c4d3ccc33b8feadab150a7abd7167.png)  
      
    [↑↑↑](https://gravatar.com/alexsanford1 "Alex Sanford")
    
-   [↓↓↓](https://gravatar.com/minikaka "minikaka")  
      
    ![minikaka](assets/1699429224-dfad7ed0ad7ad35509471543c09ba9fc.png)  
      
    [↑↑↑](https://gravatar.com/minikaka "minikaka")
    

[2 bloggers](#) like this.

## Posted by 发布者

[↓↓↓](https://wpscan.com/blog/author/marcs0h/)  
  
Marc Montpas 马克·蒙帕斯  
  
[↑↑↑](https://wpscan.com/blog/author/marcs0h/)

### Leave a Reply  留言

Write a reply... 写回复...

Log in or provide your name and email to leave a reply.

Email me new posts

InstantlyDailyWeekly

Email me new comments

Reply

  

## Get News and Tips From WPScan  
从WPScan获取新闻和提示

Type your email… 

      Subscribe
