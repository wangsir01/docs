

# SSD Advisory - QNAP QTS5 - /usr/lib/libqcloud.so JSON parsing leads to RCE - SSD Secure Disclosure

**Summary 总结**

QTS’s JSON parsing functionality is vulnerable to type confusion due to a failure to properly check the type of the `json-object->data` field. The bug allows an attacker to hijack control flow, and is accessible via the `/cgi-bin/qid/qidRequestV2.cgi` binary.  
QTS的JSON解析功能很容易受到类型混淆的影响，因为无法正确检查 `json-object->data` 字段的类型。该漏洞允许攻击者劫持控制流，并且可以通过 `/cgi-bin/qid/qidRequestV2.cgi` 二进制文件访问。

Successful exploitation would allow an unauthenticated attacker to execute arbitrary code as the `admin` user (equivalent to root in the QTS operating system). Under the default configuration the bug can be triggered by a network adjacent attacker, but if the HTTP server is configured for remote access it is fully remote.  
成功利用此漏洞将允许未经身份验证的攻击者以 `admin` 用户（相当于QTS操作系统中的root用户）身份执行任意代码。在默认配置下，该漏洞可以由网络相邻的攻击者触发，但如果HTTP服务器配置为远程访问，则它是完全远程的。

**Credit 信用**

An independent security researcher, dcs, working with SSD Secure Disclosure.  
一个独立的安全研究员，dcs，与SSD安全披露工作。

**CVE**

CVE-2023-39296 电话：+86-20 - 6666666

**Affected Versions 影响版本**

QNAP TS-494 NAS running QTS operating system 5.1.0.2466 build 20230721  
QNAP TS-494 NAS QTS 5.1.0.2466 build 20230721

The bug is present across QNAP NAS devices running QTS, and exists at least as far back as 5.1.0.2348 build 20230325 (oldest build publicly available for download).  
该漏洞存在于运行QTS的QNAP NAS设备中，并且至少存在于5.1.0.2348 build 20230325（可公开下载的最早版本）。

**Vendor Response 销售商应答**

The vendor has issued a fix for the vulnerability, information about the fix is available at: https://www.qnap.com/en-me/security-advisories  
供应商已经发布了针对该漏洞的修复程序，有关修复程序的信息可在以下网站获得：https://www.qnap.com/en-me/security-advisories

**Technical Analysis 技术分析**

QTS’s JSON functionality is based on the MIT-licensed `json-c` project and is implemented in `/usr/lib/libqcloud.so`. The function `json_tokener_parse_verbose` iterates through a provided JSON string, and constructs a JSON object. The `json-object` structure is defined as follows:  
QTS的JSON功能基于MIT许可的 `json-c` 项目，并在 `/usr/lib/libqcloud.so` 中实现。函数 `json_tokener_parse_verbose` 遍历提供的JSON字符串，并构造JSON对象。 `json-object` 结构定义如下：

struct json\_object { json\_object {

enum json\_type o\_type; \[1\]

json\_func \*\_delete;

json\_func \*\_to\_json\_string;

int ref\_count;

struct printbuf \*pb;  
struct print \*pb;

union data {  
联合数据{

boolean c\_boolean;

double c\_double;

int c\_int;  
int n = 0;

struct lh\_table \*c\_object;

struct array\_list \*c\_array;

char \*c\_string;

} o;

};

The `json_object->o` union field allows a `json_object` to contain a variety of different data types. The data type held by each `json_object` is indicated in the `o_type` \[1\] field. While processing a JSON string, `json_tokener_parse_verbose` will read the first few characters of the JSON string, and set the `o` and `o_type` fields. For example the following string: `string {}` will return a `json_object` with `o_type` set to `json_type_string` and `o` set to a pointer to `string`, while the string `1234 {}` will return a `json_object` with `o_type` `json_type_int` and `o` set to the integer value 1234.  
`json_object->o` union字段允许 `json_object` 包含各种不同的数据类型。由每个 `json_object` 保持的数据类型在 `o_type` \[1\]字段中指示。在处理JSON字符串时， `json_tokener_parse_verbose` 将读取JSON字符串的前几个字符，并设置 `o` 和 `o_type` 字段。例如，以下字符串： `string {}` 将返回一个 `json_object` ，其中 `o_type` 设置为 `json_type_string` ， `o` 设置为指向 `string` 的指针，而字符串 `1234 {}` 将返回一个 `json_object` ，其中 `o_type` 、 `json_type_int` 和 `o` 设置为整数值1234。

When parsing an attacker-provided JSON string, the `/home/httpd/cgi-bin/qid/qidRequestV2.cgi` binary does not properly check the `o_type` field before attempting to add values to a `json_object`. Instead, it assumes that `json_tokener_parse_verbose` returns a `json_object` with `o_type` `json_type_object`. This is only true for strings that begin with `{`. A highly condensed summary of how `qidRequestV2.cgi` parses JSON data is as follows:  
解析攻击者提供的JSON字符串时， `/home/httpd/cgi-bin/qid/qidRequestV2.cgi` 二进制文件在尝试向 `json_object` 添加值之前没有正确检查 `o_type` 字段。相反，它假设 `json_tokener_parse_verbose` 返回一个带有 `o_type` `json_type_object` 的 `json_object` 。这只适用于开始为#7 #的字符串。以下是 `qidRequestV2.cgi` 如何解析JSON数据的高度浓缩摘要：

json\_obj = json\_tokener\_parse\_verbose(json\_string);  
json\_obj = json\_tokener\_parse\_verbose（json\_string）;

…

json\_string = json\_object\_new\_string(cgi\_value);  
json\_string = json\_object\_new\_string（cgi\_value）;

json\_object\_object\_add(json\_object, cgi\_param, json\_string); \[2\]  
json\_object\_object\_add（json\_object，cgi\_param，json\_string）; \[2\]

The call to `json_object_object_add` at \[2\] assumes that `json_object->o_type` is `json_type_object`. However that type is controlled by an attacker. By sending a specifically crafted JSON string, an attacker can get `qidRequestV2.cgi` to treat a provided string or integer value as a `struct lh_table`. This is especially dangerous since `json_object_object_add` attempts to call a function pointer in `lh_table` (`json_object->o->hash_fn()`). The JSON string “`702111234474983745 {}` will cause `json_object_object_add` to attempt to dereference an `lh_table` at address `0x4141414141414141`.  
在\[2\]中对 `json_object_object_add` 的调用假定 `json_object->o_type` 是 `json_type_object` 。然而，这种类型是由攻击者控制的。通过发送一个特制的JSON字符串，攻击者可以获得 `qidRequestV2.cgi` ，将提供的字符串或整数值视为 `struct lh_table` 。这是特别危险的，因为 `json_object_object_add` 试图调用 `lh_table` （ `json_object->o->hash_fn()` ）中的函数指针。JSON字符串“ `702111234474983745 {}` 将导致 `json_object_object_add` 尝试取消引用地址 `0x4141414141414141` 的 `lh_table` 。

## Steps to reproduce/proof of concept  
复制/概念验证的步骤

To reproduce the crash simply issue the following curl request to the NAS:  
要重现崩溃，只需向NAS发出以下curl请求：

curl -X POST -H "Content-Type: application/json" -d "4702111234474983745 {}" "{NAS\_IP}:8080/cgi-bin/qid/qidRequestV2.cgi?param=value"  
curl -X POST -H“Content-Type：application/json”-d“4702111234474983745 {}””{NAS\_IP}：8080/cgi-bin/qid/qidRequestV2.cgi？param=value”

This will cause the program to crash attempting to dereference a `lh_table` structure at `0x4141414141414141`.  
这将导致程序在尝试取消引用 `0x4141414141414141` 处的 `lh_table` 结构时崩溃。
