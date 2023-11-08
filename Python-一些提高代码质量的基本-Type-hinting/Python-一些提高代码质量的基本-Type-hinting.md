
# Python：一些提高代码质量的基本 Type hinting

Published at 2023/11/5 14:50 , ... Views

Hi，我是 Pluveto，一个好吃懒做，屎上挖坑的 UP 主。这个视频会示范怎么借助 Python 的 Type Hints 写出工业级的 Python 代码。

不多废话直接进入正题。

有一天，程序员 Alice 提交了代码。我们来看看他的代码好不好维护？

Path[](https://www.less-bug.com/posts/python-type-hinting-basics/code/s1.py)

```python
1
def get_authors_names(posts):
2
    authors_names = []
3
    for post in posts:
4
        author = post["author"]
5
        author_name = author["name"]
6
        authors_names.append(author_name)
7
    return authors_names
```

在 2023 年，答案是确定的，这就是一坨大便。现在已经有了类型标注特性，如果不是为了兼容性考虑，不写类型的行为比不写注释更加恶劣！

味道指数：★★（鉴定为：臭味）

首先，posts 属于 Any 数据类型，但是代码里强假设了它是一个列表，且列表元素每个都具有 author 字段，每个 author 字段的值都有 name 字段。这种假设没有任何东西来保证。导致拉屎一时爽，维护火葬场。

打回去重写！

五分钟之后，Alice 给出了新的代码。

```python
1
def get_authors_names(posts):
2
    authors_names = []
3
    for post in posts:
4
        author = post.get("author")  # 使用字典的get方法获取值，如果键不存在则返回None
5
        if author is not None:
6
            author_name = author.get("name")  # 使用字典的get方法获取值，如果键不存在则返回None
7
            if author_name is not None:
8
                authors_names.append(author_name)
9
    return authors_names
```

Alice 想：哈哈，我检查了空值，这样代码质量大大提高！

恰恰相反，这种代码是真正的屎山。

味道指数：三颗星（鉴定为：强烈的臭味）

- - -

这是我工作中遇到同事最喜欢写的代码。这些同事喜欢在代码的左边画三角形，三角形越大，缩进越多，就越能促进游标卡尺的销量，帮助我国走出经济危机。

Alice，你不用写了，还是我来！

```python
 1
from typing import List, TypedDict
 2

 3
class Author(TypedDict):
 4
    name: str
 5
    email: str
 6
    bio: str
 7
    website: str
 8

 9
class Post(TypedDict):
10
    title: str
11
    author: Author
12
    publication_date: str
13
    content: str
14

15
def get_authors_names(posts: List[Post]) -> List[str]:
16
    return [post["author"]["name"] for post in posts]
```

味道指数：?（请网友自行鉴定）

这里我们利用了 Python 的 typing 特性，为参数标记了类型。这样，我们就可以在编译时期发现错误，而不是在运行时期。

之后如果要新增功能，用到了新的字段，也可以直接利用类型提示编码，不用你重新复现出数据的来源，然后打印出来一个个看。

为了告诉大家有多香，我简单演示一下。

这是第一种情况，我们要统计所有文章的长度之和。

[](https://www.less-bug.com/posts/python-type-hinting-basics/code/s2.py)

```python
1
def get_total_content_length(posts: List[Post]):
2
    total_length = 0
3
    for post in posts:
4
        content = post["content"]
5
        total_length += len(content)
6
    return total_length
```

可以看到当我们输入 `[` 的时候，编辑器就会提示可以输入什么。

第二种情况，假设我不小心把字段名打错了：

```python
1
posts[0]['authro']
```

可以看到编辑器直接就报错了。这种小毛病如果运行时才发现，而且是在生产环境，那就是灾难了。

## 常见的 typing

下面我们介绍一下 Python 的常用的 typing。介绍完之后我们继续攻占下一个屎山！

[](https://www.less-bug.com/posts/python-type-hinting-basics/code/s3.py)

```python
 1

 2

 3

 4

 5
import typing as t
 6

 7
# 字符串
 8
greet: str = "hello"
 9

10
# 浮点数
11
radius: float = 0.1
12

13
# 整数
14
num_children: int = 10
15

16
# 布尔值
17
is_cool: bool = True
18

19
# 字节串
20
data: bytes = b"hello"
21

22
# 列表
23
numbers: list[int] = [1, 2, 3, 4, 5]
24

25
# 元组
26
coordinates: tuple[float, float] = (3.5, 2.7)
27

28
# 字典
29
person: dict[str, t.Union[str, int]] = {
30
    "name": "Alice",
31
    "age": 25,
32
    "city": "New York"
33
}
34

35
# 集合
36
fruits: set[str] = {"apple", "banana", "orange"}
37

38
# 自定义类型
39
class Point:
40
    def __init__(self, x: float, y: float):
41
        self.x = x
42
        self.y = y
43

44
# 使用自定义类型
45
p1: Point = Point(2.0, 3.5)
46
p2: Point = Point(1.0, -4.5)
47

48
# 函数类型注解
49
def add(x: int, y: int) -> int:
50
    return x + y
51

52
# 使用函数类型注解
53
result: int = add(5, 10)
54

55
# 类型别名
56
Vector = t.Tuple[float, float]
57

58
# 使用类型别名
59
vector: Vector = (2.5, 1.8)
60

61
# 可选类型
62
name: t.Optional[str] = None
63

64
# 默认参数
65
def greet_person(name: str = "John") -> None:
66
    print(f"Hello, {name}!")
67

68
# 使用默认参数
69
greet_person()  # 输出: Hello, John!
70
greet_person("Alice")  # 输出: Hello, Alice!
```

## 屎山重构之简单工厂

好，现在 Bob 登场，他写了一个 create\_storage() 函数。实现了根据 storage\_type 生成不同的 StorageClient 对象。

[](https://www.less-bug.com/posts/python-type-hinting-basics/code/s4.py)

```python
 1
class S3StorageClient:
 2
    def __init__(self):
 3
        ...
 4

 5
    def sync(self, src, dest):
 6
        ...
 7

 8

 9
class AzureCloudStorageClient:
10
    def __init__(self):
11
        ...
12

13
    def sync(self, src, dest):
14
        ...
15

16

17
def create_storage(storage_type: Literal["s3", "azure"]):
18
    if storage_type == "s3":
19
        return S3StorageClient()
20
    elif storage_type == "azure":
21
        return AzureCloudStorageClient()
```

还是那句话，在 Python3.5 之前这么写没问题，但是现在这么写就是给自己挖坑。

我们先不改代码，大家看能在这个代码找到几个问题？

1.  sync 函数，能理解 src 和 dest 代表什么吗？是从本地的 src 路径复制到远程的 dest 路径吗？还是反过来？还是两边都是远程路径？还是说都可以？传入的是相对路径还是绝对路径？
    
2.  万一增加新的 StorageClient，怎么保证实现者能够实现所需要的函数（sync）
    
3.  sync 的返回值是什么类型？
    
4.  每次使用者都需要手动输入 storage\_type，万一输错了怎么办？那外面每次都需要套个 try catch?
    

我们现在一步步修改。第一步是定义一个抽象基类叫做 StorageClient，抽象基类的话，相当于其他语言中的接口，用来限定它的子类型必须实现哪些方法。

[](https://www.less-bug.com/posts/python-type-hinting-basics/code/s4_2.py)

```python
 1
from abc import ABCMeta, abstractmethod
 2
from urllib.parse import ParseResult
 3
import typing as t
 4

 5
URI = ParseResult
 6

 7

 8
class StorageClient(metaclass=ABCMeta):
 9
    @abstractmethod
10
    def sync(self, src: URI, dest: URI) -> None:
11
        """
12
        Sync files from a source URI to a destination URI.
13

14
        Args:
15
            src: The source URI.
16
                For example, s3://bucket/path/to/file or file://path/to/file.
17
            dest: The destination URI.
18
                For example, s3://bucket/path/to/file or file://path/to/file.
19

20
        Returns:
21
            None
22

23
        Raises:
24
            ValueError: If the source or destination URI is invalid.
25
            IOError: If the source or destination URI is not accessible.
26
        """
27
        return NotImplemented
```

我们还增加了注释，告诉调用者每个参数的含义。并且我们用 URI 作为参数类型，这样用户就知道，传入的 URI schema 不同，执行同步的来源和目标就会对应变化。

注释中还告诉用户什么情况下这个函数会抛出什么异常。这样调用方可以精细处理异常。

我们可以尝试增加一个新的 StorageClient，比如 WebDavStorageClient，然后故意不实现 sync，可以看到编辑器直接报错了。

下面我们再来解决 create\_storage 工厂函数。这里你可以选择用 Literal 或者枚举。

```python
 1
def create_storage(
 2
    storage_type: t.Literal["s3", "azure"]
 3
) -> StorageClient:
 4
    match storage_type:
 5
        case "s3":
 6
            return S3StorageClient()
 7
        case "azure":
 8
            return AzureCloudStorageClient()
 9
        case _ as unreachable:
10
            t.assert_never(unreachable)
```

实际上最后两行都可以去掉。

我们来看最终的代码：

怎么样，是不是屎味大减？

有关所有的 Typing 特性，请参考：[typing — Support for type hints — Python 3.12.0 documentation](https://docs.python.org/3/library/typing.html)

- - -

This work is licensed under [CC BY 4.0![](assets/1699407256-ee0d4e4e7f4a9a9264b9d9555c2cbf13.svg)![](assets/1699407256-06b1d0fa348a6372aa5bd192527bfe9b.svg)](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1) except those created with the assistance of AI.

  

表情图片预览

发送评论

0 条评论

Powered By [Artalk](https://artalk.js.org/ "Artalk v2.4.4")

Artalk ErrorTypeError: NetworkError when attempting to fetch resource.，无法获取评论列表数据  
点击重新获取
