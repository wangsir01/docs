

# ebpf hello-world

-   资料来源:
    
    > <>
    
-   更新
    
    |     |     |
    | --- | --- |
    | ```plain<br>1<br>``` | ```plain<br>2023.10.30 初始<br>``` |
    

## [](#%E5%AF%BC%E8%AF%AD "导语")导语

最近需要搞点程序运行时监控, 于是早就想试试 ebpf 了, 无奈用户态/内核态切换的代价,评估后还是还得想别的思路. 仅水一篇.

## [](#%E6%A6%82%E5%BF%B5 "概念")概念

ebpf 安全的内核虚拟机, bpf 是其早期版本.

bpftrace / bcc: 基于 ebpf 封装,降低 ebpf 使用难度.

-   bpftrace: ebpf 高级跟踪语言. 开发快速 ++,快速原型开发;
-   bbc: bbc 库以及一系列工具集合. 适合更复杂的程序.

用户空间探针: `uprobes` / `uretprobes`

-   uprobes(user-level probes): 埋点函数入口调用
-   uretprobes: 埋点函数运行后调用,还能获取返回值.
-   相比之下 uprobes 性能代价小一点点

内核空间探针: `kprobes` / `kretprobe` 功能类似, 在内核程序埋点.

用户空间探针也只是另一种类型的内核探针, 不过陷阱在 用户态程序 而已,执行回调 还是切换到内核态.

探针与 ebpf 没有直接关系, 没有 epbf 挂个 ko 也能运行, 但一般会协同使用. uprobes 埋点, 跳转到 ebpf 执行 (内核态,能执行更复杂任务). ebpf 程序编写就交给 bpftrace / bcc.

## [](#Helloworld-Ebpf-Uprobes "Helloworld: Ebpf + Uprobes")Helloworld: Ebpf + Uprobes

ebpf + uprobes

-   bcc 编写 epbf

目标: set\_value 函数执行时,捕获 传入的参数 `new_value`

|     |     |
| --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>``` | ```plain<br>#include <stdio.h><br>#include <time.h><br><br>int value;<br><br>void set_value(int new_value)<br>{<br>    value = new_value;<br>}<br><br>int main()<br>{<br>    int iterations = 1000000;<br><br>    for (int i = 0; i < iterations; i++)<br>    {<br>        set_value(i);<br>    }<br>    return 0;<br>}<br>``` |

编译: `gcc -o helloworld helloworld.c`

先来看看 epbf 的定义 `trace_set_value.bpf.c`

|     |     |
| --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>``` | ```plain<br>#include <uapi/linux/ptrace.h><br>#include <linux/limits.h><br><br>int trace_set_value(struct pt_regs *ctx) {<br>  int v = PT_REGS_RC(ctx); // get new_value<br>  bpf_trace_printk("set value to %d\\n", v); // print value // 输出要用 bpf_trace_printk<br><br>  return 0;<br>};<br>``` |

bcc 支持 python go 等初始化 ebpf ,反正是个 demo ,就 python 了:

|     |     |
| --- | --- |
| ```plain<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>``` | ```plain<br>from bcc import BPF, USDT<br><br># 读取 BPF 程序<br>with open("trace_set_value.bpf.c", "r") as f:<br>    program = f.read()<br><br># 加载 BPF 程序<br>bpf = BPF(text=program)<br># 加载 uprobe<br>bpf.attach_uprobe(name="./helloworld", sym="set_value", fn_name="trace_set_value")<br><br># 持续打印输出<br>while True:<br>    try:<br>        msg = bpf.trace_fields()<br>        msg = msg[-1]<br>        print(msg)<br>    except KeyboardInterrupt:<br>        exit()<br>``` |

运行 `python3 trace_set_value.py` 然后其他 shell `./helloworld` 就能看到输出了.

## [](#%E7%BB%93%E8%AF%AD "结语")结语

BCC 真的简化了 N 多工作, 期待后面再能用上 ebpf 吧.
