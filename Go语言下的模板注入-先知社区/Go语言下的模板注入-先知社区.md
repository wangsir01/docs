

# Go语言下的模板注入 - 先知社区

Go语言下的模板注入

* * *

# Go语言下的模板注入：

这差不多应该是模板注入系列的最后一篇文章了，最近去打了华东北赛区的线下，结果被打爆了，java和go让不会的孩子太坐牢了，于是就想到了，最后一篇有关模板注入的系列就以go语言结尾吧，同样也是开头，暑假开始学java和go。

## go语言基础：

首先还是结合菜鸟教程先来学习一下go语言的基本语法，简单熟悉一下go的语言：

```plain
package main
import "fmt"
func main(){//需要注意的是 { 不能单独放在一行，所以以下代码在运行时会产生错误：
  /* 这是我的第一个简单的程序 */
  fmt.Println("Hello,World!")
}
```

```plain
- 第一行代码 package main 定义了包名。你必须在源文件中非注释的第一行指明这个文件属于哪个包，如：package main。package main表示一个可独立执行的程序，每个 Go 应用程序都包含一个名为 main 的包。
- 下一行 import "fmt" 告诉 Go 编译器这个程序需要使用 fmt 包（的函数，或其他元素），fmt 包实现了格式化 IO（输入/输出）的函数。
- 下一行 func main() 是程序开始执行的函数。main 函数是每一个可执行程序所必须包含的，一般来说都是在启动后第一个执行的函数（如果有 init() 函数则会先执行该函数）。
- 下一行 fmt.Println(...) 可以将字符串输出到控制台，并在最后自动增加换行字符 \n。使用 fmt.Print("hello, world\n") 可以得到相同的结果。
- Print 和 Println 这两个函数也支持使用变量，如：fmt.Println(arr)。如果没有特别指定，它们会以默认的打印格式将变量 arr 输出到控制台。
```

当标识符（包括常量、变量、类型、函数名、结构字段等等）以一个大写字母开头，如：Group1，那么使用这种形式的标识符的对象就可以被外部包的代码所使用（客户端程序需要先导入这个包），这被称为导出（像面向对象语言中的 public）；标识符如果以小写字母开头，则对包外是不可见的，但是他们在整个包的内部是可见并且可用的（像面向对象语言中的 protected ）。

### Go 标记：

Go 程序可以由多个标记组成，可以是关键字，标识符，常量，字符串，符号。如以下 GO 语句由 6 个标记组成：

```plain
fmt.Println("Hello, World!")
```

6 个标记是(每行一个)：

```plain
1. fmt
2. .
3. Println
4. (
5. "Hello, World!"
6. )
```

### 格式化字符串

Go 语言中使用 **fmt.Sprintf** 或 **fmt.Printf** 格式化字符串并赋值给新串：

*   **Sprintf** 根据**格式化参数生成格式化的字符串**并返回该字符串。
*   **Printf** 根据**格式化参数生成格式化的字符串**并写入标准输出。

#### Sprintf 实例

```plain
package main

import (
  "fmt"
)

func main() {
  // %d 表示整型数字，%s 表示字符串
  var stockcode=123
  var enddate="2020-12-31"
  var url="Code=%d&endDate=%s"
  var target_url=fmt.Sprintf(url,stockcode,enddate)
  fmt.Println(target_url)
}
```

输出结果为：

```plain
Code=123&endDate=2020-12-31
```

#### Printf 实例

```plain
package main

import (
  "fmt"
)

func main() {
  // %d 表示整型数字，%s 表示字符串
  var stockcode=123
  var enddate="2020-12-31"
  var url="Code=%d&endDate=%s"
  fmt.Printf(url,stockcode,enddate)
}
```

输出结果为：

```plain
Code=123&endDate=2020-12-31
```

### 变量声明：

1.  第一种，指定变量类型，如果没有初始化，则变量默认为零值。

```plain
var v_name v_type
v_name = value
```

1.  第二种，根据值自行判定变量类型。

```plain
var v_name = value
```

1.  第三种，如果变量已经使用 var 声明过了，再使用 :=\\ 声明变量，就产生编译错误，格式：

```plain
v_name := value

var intVal int 
intVal :=1 // 这时候会产生编译错误，因为 intVal 已经声明，不需要重新声明

intVal := 1 // 此时不会产生编译错误，因为有声明新的变量，因为 := 是一个声明语句
相当于：
var intVal int 
intVal =1
```

例：

```plain
可以将 var f string = "Runoob" 简写为 f := "Runoob"
```

### Go 语言常量

常量是一个简单值的标识符，在程序运行时，不会被修改的量。

常量中的数据类型只可以是布尔型、数字型（整数型、浮点型和复数）和字符串型。

常量的定义格式：

```plain
const identifier [type] = value
```

你可以省略类型说明符 \[type\]，因为编译器可以根据变量的值来推断其类型。

*   显式类型定义： `const b string = "abc"`
*   隐式类型定义： `const b = "abc"`

多个相同类型的声明可以简写为：

```plain
const c_name1, c_name2 = value1, value2
```

### 循环语句：

#### 语法:

Go 语言的 For 循环有 3 种形式，只有其中的一种使用分号。

和 C 语言的 for 一样：

```plain
for init; condition; post { }
```

和 C 的 while 一样：

```plain
for condition { }
```

和 C 的 for(;;) 一样：

```plain
for { }
```

*   init： 一般为赋值表达式，给控制变量赋初值；
*   condition： 关系表达式或逻辑表达式，循环控制条件；
*   post： 一般为赋值表达式，给控制变量增量或减量。

for语句执行过程如下：

*   1、先对表达式 1 赋初值；
*   2、判别赋值表达式 init 是否满足给定条件，若其值为真，满足循环条件，则执行循环体内语句，然后执行 post，进入第二次循环，再判别 condition；否则判断 condition 的值为假，不满足条件，就终止for循环，执行循环体外语句。

for 循环的 range 格式可以对 slice、map、数组、字符串等进行迭代循环。格式如下：

```plain
for key, value := range oldMap {
    newMap[key] = value
}
```

以上代码中的 key 和 value 是可以省略。

如果只想读取 key，格式如下：

```plain
for key := range oldMap
```

或者这样：

```plain
for key, _ := range oldMap
```

如果只想读取 value，格式如下：

```plain
for _, value := range oldMap
```

```plain
package main
import "fmt"

func main() {
  strings := []string{"google", "runoob"}
  for i, s := range strings {
   fmt.Println(i, s)
  }


  numbers := [6]int{1, 2, 3, 5}
  for i,x:= range numbers {
   fmt.Printf("第 %d 位 x 的值 = %d\n", i,x)
  } 
}
```

以上实例运行输出结果为:

```plain
0 google
1 runoob
第 0 位 x 的值 = 1
第 1 位 x 的值 = 2
第 2 位 x 的值 = 3
第 3 位 x 的值 = 5
第 4 位 x 的值 = 0
第 5 位 x 的值 = 0
```

#### 实例:

```plain
package main
import "fmt"

func main() {
  map1 := make(map[int]float32)
  map1[1] = 1.0
  map1[2] = 2.0
  map1[3] = 3.0
  map1[4] = 4.0

  // 读取 key 和 value
  for key, value := range map1 {
   fmt.Printf("key is: %d - value is: %f\n", key, value)
  }

  // 读取 key
  for key := range map1 {
   fmt.Printf("key is: %d\n", key)
  }

  // 读取 value
  for _, value := range map1 {
   fmt.Printf("value is: %f\n", value)
  }
}
```

```plain
key is: 4 - value is: 4.000000
key is: 1 - value is: 1.000000
key is: 2 - value is: 2.000000
key is: 3 - value is: 3.000000
key is: 1
key is: 2
key is: 3
key is: 4
value is: 1.000000
value is: 2.000000
value is: 3.000000
value is: 4.000000
```

## 漏洞成因：

在我们已经知道了Python中例如Flask，Mako以及php中的Smarty等等，都是没有正常使用渲染模板从而导致的能执行相应格式的代码而造成的注入，所以go也是同样的一种逻辑，也是因为没能够规范使用模板渲染，而导致代码能够被直接执行。

## Go的模板引擎：

所以我们先来看一下对应的模板引擎：

GO语言提供了两个模板包，一个是 html/template，另一个是 text/template 模块：

### html/template模块：

[https://pkg.go.dev/html/template](https://pkg.go.dev/html/template)

在html模块中是这样介绍的，这个模板包用于处理安全的HTML输出，防止XSS这样的代码注入，也就是说，HTML 模板将数据值视为纯文本，应对其进行编码，以便可以安全地嵌入 HTML 文档中。当用户输入的是html形式的时候，就应该以html/template来进行处理而不是text/template，举个例子来说：

```plain
import "text/template" 
... 
t, err := template.New("foo").Parse(`{{define "T"}}你好，{{.}}！{{end}}`) 
err = t.ExecuteTemplate(out, "T", "<script>alert('你已被攻击')</script>")
```

*   重点代码在两个地方：

```plain
{{define "T"}}你好，{{.}}！{{end}}
```

*   这里define了一个T，和两个模板处理的方式一样，将输入的数据值定义为一个纯文本，然后{{.}}是我们用户进行输入的东西：

```plain
err = t.ExecuteTemplate(out, "T", "<script>alert('你已被攻击')</script>")
```

*   这里就让用户输入一个纯文本信息

```plain
<script>alert('你已被攻击')</script>
```

*   但是因为使用的是text类型的模板包，他会直接输出：

```plain
Hello, <script>alert('you have been pwned')</script>!
```

*   然而当我们import引用的是html形式的时候，他就会输出：从而防止恶意的代码进行注入：

```plain
Hello, &lt;script&gt;alert(&#39;you have been pwned&#39;)&lt;/script&gt;!
```

*   而之所以html包能够实现这样的操作，是这个原因：
    
*   该包理解 HTML、CSS、JavaScript 和 URI。它为每个简单的操作管道添加了清理功能，因此给出了摘录
    

```plain
<a href="/search?q={{.}}">{{.}}</a>
```

*   在解析时，每个 {{.}} 都会被覆盖，以根据需要添加转义函数。在这种情况下就变成了

```plain
<a href="/search?q={{.| urlescaper | attrescaper}}">{{. | htmlescaper}}</a>
```

*   其中 urlescaper、attrescaper 和 htmlescaper 是内部转义函数的别名。对于这些内部转义函数，如果操作管道计算结果为 nil 接口值，则会将其视为空字符串。

## 漏洞利用的方法：

我们看一个代码示例，代码的解释为了方便观看我以注释的形式写在里面了，刚开始熟悉go，顺便连着读代码……:(

```plain
package main
//这里引用了包，里面包括我们一开始学习到的fmt，以及用于网络服务的http，最重要的就是text/template模板包是这个代码存在漏洞点的关键。
import (
    "fmt"
    "net/http"
    "strings"
    "text/template"//这里就采用了text模板包
)
//进行了全局定义
type User struct {
    Id     int
    Name   string
    Passwd string
}

func StringTplExam(w http.ResponseWriter, r *http.Request) {
    user := &User{1, "admin", "123456"}
    r.ParseForm()//这里通过r.ParseForm()方法用户提交的表单，将其解析为一个键值对的形式，存储在r.PostForm 中。
    arg := strings.Join(r.PostForm["name"], "")//用户输入的地方，进行post传参
    tpl1 := fmt.Sprintf(`<h1>Hi, ` + arg + `</h1> Your name is ` + arg + `!`)//使用Sprintf，将数据进行拼接以后返回纯文本再赋值给tpl1；
    html, err := template.New("login").Parse(tpl1)//进行模板渲染
    //这里创建一个名为 "login" 的模板，并将模板字符串 tpl1 解析到该模板中。template.New()函数作用是创建一个新的模板，Parse()是用于解析模板字符串。
    html = template.Must(html, err)
    html.Execute(w, user)
}

func main() {
    server := http.Server{
        Addr: "127.0.0.1:8080",
    }
    http.HandleFunc("/login", StringTplExam)
    server.ListenAndServe()
}
```

### 漏洞点1：

因为我们在这里使用了模板&User，所以会通过`{{.Passwd}}`模板使用 user 的 属性，就会导致信息泄露

```plain
type User struct {
    Id     int
    Name   string
    Passwd string
}
```

[![](assets/1701612401-8a430670202e85377d56014eacf02293.png)](https://xzfile.aliyuncs.com/media/upload/picture/20230628114240-d50e2a8c-1565-1.png)

[![](assets/1701612401-bc2e151762fd43a51e37a67635d32d5f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20230628114248-d9ccd37a-1565-1.png)

### 漏洞点2：

go语言中ssti的rce执行其实也是其他语言ssti一样，都是通过危险方法的调用，来实现rce：

比如，我们在代码中引入`"os/exec"`并添加一个危险函数：

```plain
func (u User) Secret(test string) string {
    out, _ := exec.Command(test).CombinedOutput()
    return string(out)
}
```

[![](assets/1701612401-2b542f690347ab996d49f2c8770f00f2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20230628114328-f1c4c7bc-1565-1.png)

这些危险函数的利用其实就是在审计的过程中发现了一个可以进行任意文件读取的方法，并且存在模板注入的点，导致了文件信息的泄露，我们简化一下，引入`"io/ioutil"`包

```plain
import("io/ioutil")
func (u *User)FileRead(File string) string i
    data,err := ioutil.ReadFile(File)
    if err != nil {
        fmt.Print( "File read" )
    }
    return string(data)
```

### 漏洞点3：

我们在刚才熟悉html模板包的时候就知道，可以对XSS进行防御，那么我们不使用的时候我们就来尝试一下能不能进行XSS攻击：

借助Go模板提供的字符串打印功能，可以直接输出XSS语句，上面修改的的防御方法也无法阻挡弹窗的脚步

```plain
{{"<script>alert(/xss/)</script>"}}
{{print "<script>alert(/xss/)</script>"}}
```

[![](assets/1701612401-b555b9d013ef6dca0b6c7f85232f1228.png)](https://xzfile.aliyuncs.com/media/upload/picture/20230628114337-f6bc45c4-1565-1.png)

## 防御：

### 防御1：

```plain
func StringTpl2Exam(w http.ResponseWriter, r *http.Request) {
    user := &User{1, "tyskill", "tyskill"}
    r.ParseForm()
    arg := strings.Join(r.PostForm["name"], "")
    tpl := `<h1>Hi, {{ .arg }}</h1><br>Your name is {{ .Name }}`
    data := map[string]string{
        "arg":  arg,
        "Name": user.Name,
    }
    html := template.Must(template.New("login").Parse(tpl))
    html.Execute(w, data)
}
```

这里是根据`sp4`师傅借鉴的tyskill师傅文章对应的防御代码，打完国赛，patch的分简直是不能忽视，平常就应该培养这样的攻防思维：

防御点解析:

1.  模板中使用 `{{ .arg }}` 和 `{{ .Name }}` 来引用变量。可以防止直接将用户输入的内容作为字符串插入到模板中，模板引擎会对这些变量进行合适的转义。
2.  创建了一个名为 `data` 的 `map`，用于存储模板中需要的数据。在这个 `map` 中，键名与模板中的变量名相对应，键值则为相应的数据。这样可以避免直接将用户输入的值作为变量名，减少了可能的安全风险。

[![](assets/1701612401-8fad632aac00a227b56ca4d594fa80f5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20230628114407-08e18fb6-1566-1.png)

### 防御2：

1、Go模板包`text/template`提供内置函数html来进行转义，除此之外还提供了js函数转义js代码。

```plain
{{html "<script>alert(/xss/)</script>"}}
{{js "js代码"}}
```

2、`text/template`在模板处理阶段还定义`template.HTMLEscapeString`等转义函数

3、使用另一个模板包`html/template`，自带转义效果

参考文章：  
主要还是学的大师傅sp4的文章：[https://forum.butian.net/share/1286](https://forum.butian.net/share/1286)  
[https://tyskill.github.io/posts/gossti/](https://tyskill.github.io/posts/gossti/)
