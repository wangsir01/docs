
# Python：简单文本过滤自动机的实现

Published at 2023/11/7 07:57 , ... Views

## 引言

假设给你一串这样的文本:

```text
1
Stellar是一个基于区块链的去中心化支付系统，旨在实现快速、低成本的跨境支付和资产转移[1](http://fourweekmba.com/)。它建立在Stellar区块链上，是一个开放源代码的网络，可以用于转移和存储资金的开放支付网络[2](https://www.oanda.com/)。Stellar的原生加密货币称为流明（Lumens），简称XLM，可以作为媒介用于转换各种货币和支付手续费[2](https://www.oanda.com/)。
```

怎么把里面的这种东西过滤掉？

这些东西我们称为 Markdown 链接。我们例子里的链接更加特殊：就是方括号里一个整数, 后面紧跟着一个圆括号, 圆括号里是一个链接. 这个格式可以表示这样的规则:

`[[数字]](任意文本)`

我们的目标的话, 是过滤掉符合这个规则的子字符串. 也就是得到:

```text
1
Stellar是一个基于区块链的去中心化支付系统，旨在实现快速、低成本的跨境支付和资产转移。它建立在Stellar区块链上，是一个开放源代码的网络，可以用于转移和存储资金的开放支付网络。Stellar的原生加密货币称为流明（Lumens），简称XLM，可以作为媒介用于转换各种货币和支付手续费。
```

同时, 我们不打算使用现成的工具, 而是使用有限自动机来实现.

来想想思路

1.  首先, 设计一个通用的有限自动机, 能够实现状态的定义, 转换和判断.
    
2.  然后我们使用一个叫做 TextFilter 的自动机, 专门用于我们链接过滤的任务.
    
3.  最后，测试当然不能少
    

## 通用的有限自动机

自动机可以分为有限状态和无限状态两种。常见情况下，如果需要匹配无限可嵌套的文本，比如

`((...))`

就需要无限状态。其余多数情况下有限状态能解决问题。

有限状态自动机可以分为确定性和不确定性两种。

确定性自动机，简称 DFA 就是说一个时刻只能处于一个状态，走到终止状态算匹配。

不确定性状态机的话，也叫 NFA，允许同时处于多个状态，只要其中一个走到了终止状态（也叫接受状态）就算匹配。

DFA 和 NFA、正则表达式三者等价，可以通过一些算法相互转化。

感兴趣的同学可以看我的形式语言与自动机笔记，或者搜哈工大的课程，这里不赘述了。

维基百科对 DFA 的标准定义如下：

[https://zh.wikipedia.org/zh-hans/%E7%A1%AE%E5%AE%9A%E6%9C%89%E9%99%90%E7%8A%B6%E6%80%81%E8%87%AA%E5%8A%A8%E6%9C%BA](https://zh.wikipedia.org/zh-hans/%E7%A1%AE%E5%AE%9A%E6%9C%89%E9%99%90%E7%8A%B6%E6%80%81%E8%87%AA%E5%8A%A8%E6%9C%BA)

看上去稍显复杂, 但请忽略掉上面这些晦涩的数学定义, 让我们直接动手!

为了设计一个通用的有限自动机，我们需要定义以下几个要素：

1.  状态（States）：有限自动机中的每个状态表示一个特定的条件。在通用有限自动机中，我们可以使用整数来表示状态。
    
2.  转换（Transitions）：转换是有限自动机从一个状态转移到另一个状态的过程。转换是有条件的，只有在满足特定条件时，才会发生状态转换。我们可以用一个包含当前状态、条件和下一个状态的元组来表示转换。
    
3.  开始状态（Start State）：有限自动机的初始状态。
    
4.  接受状态（Accept States）：当有限自动机达到接受状态时，表示已经识别到了一个有效的模式。
    
5.  输入字符表理论上需要定义, 但我们使用整个 Python int 整数空间来表示. 所以不需要写出来.
    

有了这些概念，我们可以开始设计通用有限自动机的类。为了简化实现，我们可以使用Python的`dataclasses`库来定义转换类，使用`enum`库来定义状态和条件的枚举类型。

```python
 1
from dataclasses import dataclass
 2
from enum import IntEnum, auto
 3
from typing import List, Dict, Set, Tuple
 4

 5

 6
@dataclass
 7
class Transition:
 8
    present: int
 9
    condition: int
10
    next: int
11

12

13
class FSM:
14
    def __init__(
15
        self,
16
        states: List[int],
17
        transitions: List[Transition],
18
        start_state: int,
19
        accept_states: List[int],
20
    ):
21
        self._states: Set[int] = set(states)
22
        self._transitions: Dict[Tuple[int, int], int] = {}
23
        self._start_state: int = start_state
24
        self._accept_states: List[int] = accept_states
25
        self._current_state: int = start_state
26

27
        for transition in transitions:
28
            self._validate_and_add_transition(transition)
29

30
    def _validate_and_add_transition(self, transition: Transition):
31
        present = transition.present
32
        condition = transition.condition
33
        next_state = transition.next
34

35
        if present not in self._states:
36
            raise ValueError(f"Invalid present state: {present}")
37
        if next_state not in self._states:
38
            raise ValueError(f"Invalid next state: {next_state}")
39
        if (present, condition) in self._transitions:
40
            raise ValueError(
41
                f"Duplicate transition: {(present, condition)} -> {next_state}"
42
            )
43

44
        self._transitions[(present, condition)] = next_state
```

其中 state 是一个状态列表，表示所有可能的状态。

transitions 包含所有可能的状态转换。如果遇到的输入不在里面，就不转换状态。 start\_state 表示初始状态。 accept\_states 表示接受状态的列表。

接下来，我们需要实现有限自动机的一些基本操作：

```python
 1
class FSM:
 2
    # ...之前的代码...
 3

 4
    def is_accept_state(self) -> bool:
 5
        return self._current_state in self._accept_states
 6

 7
    def is_start_state(self) -> bool:
 8
        return self._current_state == self._start_state
 9

10
    def reset(self) -> None:
11
        self._current_state = self._start_state
12

13
    def process(self, condition: int) -> None:
14
        if (self._current_state, condition) in self._transitions:
15
            self._current_state = self._transitions[(self._current_state, condition)]
```

前两个就不说了，就是判断当前状态是不是接受状态和初始状态。

reset 函数用于重置有限自动机。它将当前状态设置为初始状态。

process 函数用于处理输入。它接受一个输入，条件，如果条件匹配到，就将当前状态设置为下一个状态。

其实这里输入应该叫 input，奈何 Python 里有个 input 函数，用了的话不符合规范，所以就用 condition 代替了。

这样我们实现了一个比较通用的有限自动机类。测它！

我们的测试计划是：创建一个简单的有限自动机，它可以识别连续的两个`A`字符。然后这个自动机有三个状态：初始状态、遇到一个 A 的状态和遇到两个连续 A 的状态（也就是接受状态）。

```python
 1
import unittest
 2

 3
from program import FSM, Transition
 4

 5

 6
class TestFSM(unittest.TestCase):
 7
    def setUp(self):
 8
        self.fsm = FSM(
 9
            states=[0, 1, 2],
10
            transitions=[
11
                Transition(present=0, condition=ord("A"), next=1),
12
                Transition(present=1, condition=ord("B"), next=0),
13
                Transition(present=1, condition=ord("A"), next=2),
14
            ],
15
            start_state=0,
16
            accept_states=[2],
17
        )
```

然后，我们编写测试用例。

```python
 1

 2
    def test_fsm(self):
 3
        # 测试初始状态
 4
        self.assertTrue(self.fsm.is_start_state())
 5

 6
        # 处理第一个A
 7
        self.fsm.process(ord("A"))
 8
        self.assertFalse(self.fsm.is_start_state())
 9
        self.assertFalse(self.fsm.is_accept_state())
10

11
        # 处理第二个A
12
        self.fsm.process(ord("A"))
13
        self.assertFalse(self.fsm.is_start_state())
14
        self.assertTrue(self.fsm.is_accept_state())
15

16
        # 重置自动机
17
        self.fsm.reset()
18
        self.assertTrue(self.fsm.is_start_state())
19
        self.assertFalse(self.fsm.is_accept_state())
20

21

22
if __name__ == "__main__":
23
    unittest.main()
```

我们运行看看。

好的，测试通过。终于到了实现文本过滤的环节！

## 3\. 实现具体文本过滤功能

首先，让我们看一下目标是啥：输入是字符串，输出是过滤后的字符串。功能是希望过滤掉文本中特定格式的字符串，这个字符串的格式是：一个左方括号，紧接着一个数字，然后是一个右方括号，再接着是一个左圆括号，然后是一些内容，最后是一个右圆括号。

那我们梳理一下思路。这个匹配过程会有哪些状态呢？

1.  是初始状态，也就是还没开始匹配的状态。
    
2.  是遇到左方括号的状态。
    
3.  是遇到数字的状态。
    
4.  是遇到右方括号的状态。
    
5.  是遇到左圆括号的状态。
    
6.  是接受状态，也就是匹配成功的状态。因为，如果我们遇到了右圆括号，就表示匹配成功了。
    

为什么不定义一个匹配除了有括号的任意字符的中间状态呢？因为这样就得添加一堆规则，让非右括号的输入都匹配到这个中间状态。这样做很麻烦，我们只要直接不匹配，然后让游标往前移动，就能涵盖这种状况。看了代码就懂了。

首先，我们需要定义两个枚举类：`TokenType` 和 `TextFilterState`。`TokenType` 用于表示文本中字符的类型，包括普通字符、数字、左/右方括号和左/右圆括号。`TextFilterState` 用于表示文本过滤器的状态，包括初始状态、左方括号状态、数字状态、右方括号状态、圆括号状态和接受状态。

接下来，我们创建一个名为 `TextFilterFSM` 的类，它将包含我们的文本过滤器。我们希望这个类除了内部的“当前状态”外，其它状态都是固定的。所以我们直接用依赖注入的方式，把各个要素设计为参数的形式。

现在，我们需要定义状态之间的转换。我们创建一个名为 `transition_table` 的列表，其中包含五个 `Transition` 对象。每个 `Transition` 对象都包含当前状态、条件（即输入的字符类型）和下一个状态。我们按照之前描述的字符串格式定义转换规则。

首先是 states，直接遍历 TextFilterState 生成。

然后是 transitions，一个一个分析。

如果当前状态是初始状态，那么只有遇到左方括号才会转换到左方括号状态。

如果当前状态是左方括号状态，那么只有遇到数字才会转换到数字状态。

如果当前状态是数字状态，那么只有遇到右方括号才会转换到右方括号状态。

如果当前状态是右方括号状态，那么只有遇到左圆括号才会转换到左圆括号状态。

如果当前状态是左圆括号状态，那么只有遇到右圆括号才会转换到接受状态。

最后，定义开始状态和接受状态。构造出 fsm 对象。

由于输入的是字符串，字符串由字符构成，我们需要把字符转换为 condition，也就是 TokenType。

```python
 1
    def _match_token(self, char: str) -> int:
 2
        match char:
 3
            case "[":
 4
                return TokenType.OPEN_BRACKET
 5
            case "]":
 6
                return TokenType.CLOSE_BRACKET
 7
            case "(":
 8
                return TokenType.OPEN_PARENTHESIS
 9
            case ")":
10
                return TokenType.CLOSE_PARENTHESIS
11
            case _ if char.isdigit():
12
                return TokenType.DIGIT
13
            case _:
14
                return TokenType.NORMAL
```

最后，我们编写 `do_filter` 函数，我们创建一个名为 `filtered_text` 的空字符串，用于存储过滤后的文本，也是返回值。我们还创建一个名为 `buffer` 的空字符串，用于存储当前处理的字符串。

然后，我们遍历输入的文本中的每个字符。对于每个字符，我们首先使用 `_match_token` 函数获取相应的 `TokenType`。然后，我们将这个 `TokenType` 传递给自动机的 `process` 函数。接着，我们将字符添加到 `buffer` 中。

我们检查自动机是否处于接受状态。如果是，则重置自动机并清空 `buffer`。如果自动机处于开始状态，我们将 `buffer` 中的内容添加到 `filtered_text` 中，并清空 `buffer`。

在遍历完文本后，我们将 `buffer` 中的剩余内容添加到 `filtered_text` 中，并返回 `filtered_text`。

以上就是本期视频的内容，求三连，谢谢。有什么感兴趣的内容可以告诉我。看大家对屎山比较感兴趣，下期我们可能会聊一聊怎么重构各种屎山？

## 代码（主体）

```python
  1
from dataclasses import dataclass
  2
from enum import IntEnum, auto
  3
from typing import List, Dict, Set, Tuple
  4

  5

  6
@dataclass
  7
class Transition:
  8
    present: int
  9
    condition: int
 10
    next: int
 11

 12

 13
class FSM:
 14
    def __init__(
 15
        self,
 16
        states: List[int],
 17
        transitions: List[Transition],
 18
        start_state: int,
 19
        accept_states: List[int],
 20
    ):
 21
        self._states: Set[int] = set(states)
 22
        self._transitions: Dict[Tuple[int, int], int] = {}
 23
        self._start_state: int = start_state
 24
        self._accept_states: Set[int] = set(accept_states)
 25
        self._current_state: int = start_state
 26

 27
        for transition in transitions:
 28
            self._validate_and_add_transition(transition)
 29

 30
    def _validate_and_add_transition(self, transition: Transition):
 31
        present = transition.present
 32
        condition = transition.condition
 33
        next_state = transition.next
 34

 35
        if present not in self._states:
 36
            raise ValueError(f"Invalid present state: {present}")
 37
        if next_state not in self._states:
 38
            raise ValueError(f"Invalid next state: {next_state}")
 39
        if (present, condition) in self._transitions:
 40
            raise ValueError(
 41
                f"Duplicate transition: {(present, condition)} -> {next_state}"
 42
            )
 43

 44
        self._transitions[(present, condition)] = next_state
 45

 46
    def is_accept_state(self) -> bool:
 47
        return self._current_state in self._accept_states
 48

 49
    def is_start_state(self) -> bool:
 50
        return self._current_state == self._start_state
 51

 52
    def reset(self) -> None:
 53
        self._current_state = self._start_state
 54

 55
    def process(self, condition: int) -> None:
 56
        if (self._current_state, condition) in self._transitions:
 57
            self._current_state = self._transitions[(self._current_state, condition)]
 58

 59

 60
class TokenType(IntEnum):
 61
    NORMAL = auto()
 62
    DIGIT = auto()
 63
    OPEN_BRACKET = auto()
 64
    CLOSE_BRACKET = auto()
 65
    OPEN_PAREN = auto()
 66
    CLOSE_PAREN = auto()
 67

 68

 69
class TextFilterState(IntEnum):
 70
    INITIAL = auto()
 71
    OPEN_BRACKET = auto()
 72
    DIGIT = auto()
 73
    CLOSE_BRACKET = auto()
 74
    OPEN_PAREN = auto()
 75
    ACCEPT = auto()
 76

 77

 78
class TextFilterFSM:
 79
    def __init__(self):
 80
        states = [int(state) for state in TextFilterState]
 81

 82
        transition_table = [
 83
            Transition(
 84
                present=TextFilterState.INITIAL,
 85
                condition=TokenType.OPEN_BRACKET,
 86
                next=TextFilterState.OPEN_BRACKET,
 87
            ),
 88
            Transition(
 89
                present=TextFilterState.OPEN_BRACKET,
 90
                condition=TokenType.DIGIT,
 91
                next=TextFilterState.DIGIT,
 92
            ),
 93
            Transition(
 94
                present=TextFilterState.DIGIT,
 95
                condition=TokenType.CLOSE_BRACKET,
 96
                next=TextFilterState.CLOSE_BRACKET,
 97
            ),
 98
            Transition(
 99
                present=TextFilterState.CLOSE_BRACKET,
100
                condition=TokenType.OPEN_PAREN,
101
                next=TextFilterState.OPEN_PAREN,
102
            ),
103
            Transition(
104
                present=TextFilterState.OPEN_PAREN,
105
                condition=TokenType.CLOSE_PAREN,
106
                next=TextFilterState.ACCEPT,
107
            ),
108
        ]
109

110
        # 设置开始和接受状态
111
        start_state = TextFilterState.INITIAL
112
        accept_states = [TextFilterState.ACCEPT.value]
113

114
        self._fsm = FSM(states, transition_table, start_state, accept_states)
115

116
    def _match_token(self, char: str) -> int:
117
        match char:
118
            case "[":
119
                return TokenType.OPEN_BRACKET
120
            case "]":
121
                return TokenType.CLOSE_BRACKET
122
            case "(":
123
                return TokenType.OPEN_PAREN
124
            case ")":
125
                return TokenType.CLOSE_PAREN
126
            case _ if char.isdigit():
127
                return TokenType.DIGIT
128
            case _:
129
                return TokenType.NORMAL
130

131
    def do_filter(self, text: str) -> str:
132
        filtered_text = ""
133
        buffer = ""
134

135
        for char in text:
136
            token = self._match_token(char)
137
            self._fsm.process(token)
138
            buffer += char
139

140
            if self._fsm.is_accept_state():
141
                self._fsm.reset()
142
                buffer = ""
143
            elif self._fsm.is_start_state():
144
                filtered_text += buffer
145
                buffer = ""
146

147
        filtered_text += buffer
148
        return filtered_text
149

150

151
if __name__ == "__main__":
152
    sample_text = (
153
        "Stellar是一个基于区块链的去中心化支付系统，旨在实现快速、低成本的跨境支付和资产转移"
154
        "[1](http://fourweekmba.com/zh-CN/%E6%81%92%E6%98%9F%E5%8C%BA%E5%9D%97%E9%93%BE/)。"
155
        "它建立在Stellar区块链上，是一个开放源代码的网络，可以用于转移和存储资金的开放支付网络"
156
        "[2](https://www.oanda.com/bvi-ft/lab-education/cryptocurrency/stellar/)。"
157
        "Stellar的原生加密货币称为流明（Lumens），简称XLM，可以作为媒介用于转换各种货币和支付手"
158
        "续费[2](https://www.oanda.com/bvi-ft/lab-education/cryptocurrency/stellar/)。"
159
    )
160

161
    fsm = TextFilterFSM()
162
    print(fsm.do_filter(sample_text))
```

## 代码（测试）

```python
 1
import time
 2
import unittest
 3
import re
 4

 5
from program import TextFilterFSM
 6

 7

 8
def filter_fn_re(text: str):
 9
    pattern = r"\[\d+\]\([^)]*\)"
10
    return re.sub(pattern, "", text)
11

12

13
filter_fn = TextFilterFSM().do_filter
14

15

16
class TestFilterFn(unittest.TestCase):
17
    def test_normal_case(self):
18
        input_text = "Hello, this is a test [1](example)"
19
        expected_output = "Hello, this is a test "
20
        self.assertEqual(filter_fn(input_text), expected_output)
21

22
    def test_no_match(self):
23
        input_text = "Hello, this is a test"
24
        expected_output = input_text
25
        self.assertEqual(filter_fn(input_text), expected_output)
26

27
    def test_multiple_matches(self):
28
        input_text = "Hello, this is a test [1](example). And another one [2](example2)"
29
        expected_output = "Hello, this is a test . And another one "
30
        self.assertEqual(filter_fn(input_text), expected_output)
31

32
    def test_nested_matches(self):
33
        input_text = "Hello, this is a test [1](example [2](example2))"
34
        expected_output = "Hello, this is a test )"
35
        self.assertEqual(filter_fn(input_text), expected_output)
36

37
    def test_empty_text(self):
38
        input_text = ""
39
        expected_output = ""
40
        self.assertEqual(filter_fn(input_text), expected_output)
41

42
    def test_only_numbers_and_brackets(self):
43
        input_text = "[1]()"
44
        expected_output = ""
45
        self.assertEqual(filter_fn(input_text), expected_output)
46

47
    def test_only_brackets_and_text(self):
48
        input_text = "[](example)"
49
        expected_output = input_text
50
        self.assertEqual(filter_fn(input_text), expected_output)
51

52
    def test_only_numbers_and_text(self):
53
        input_text = "1example"
54
        expected_output = input_text
55
        self.assertEqual(filter_fn(input_text), expected_output)
56

57
    def test_performance(self):
58
        t = time.perf_counter()
59
        input_text = "Hello, this is a test [1](example). And another one [2](example2)"
60
        for _ in range(1000):
61
            filter_fn(input_text)
62
        elapsed = time.perf_counter() - t
63
        print("\n")
64
        print(f"FSM: Time elapsed: {elapsed:0.4f} seconds")
65

66
        t = time.perf_counter()
67
        for _ in range(1000):
68
            filter_fn_re(input_text)
69
        elapsed = time.perf_counter() - t
70
        print(f"RE: Time elapsed: {elapsed:0.4f} seconds")
71

72

73
if __name__ == "__main__":
74
    unittest.main()
```

- - -

This work is licensed under [CC BY 4.0![](assets/1699407228-ee0d4e4e7f4a9a9264b9d9555c2cbf13.svg)![](assets/1699407228-06b1d0fa348a6372aa5bd192527bfe9b.svg)](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1) except those created with the assistance of AI.

  

表情图片预览

发送评论

0 条评论

Powered By [Artalk](https://artalk.js.org/ "Artalk v2.4.4")

Artalk ErrorTypeError: NetworkError when attempting to fetch resource.，无法获取评论列表数据  
点击重新获取
