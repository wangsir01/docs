
uC-HTTP漏洞分析( CVE-2023-28379 CVE-2023-25181......)

- - -

# uC-HTTP漏洞分析

## 描述

uC-HTTP 服务器实现设计用于运行 µC/OS II 或 µC/OS III RTOS 内核的嵌入式系统。该 HTTP 服务器支持许多功能，包括持久连接、表单处理、分块传输编码、HTTP 标头字段处理、HTTP 查询字符串处理和动态内容

uC-HTTP v3.01.01中存在多个漏洞

下载链接：[https://github.com/weston-embedded/uC-HTTP/archive/refs/tags/v3.01.01.zip](https://github.com/weston-embedded/uC-HTTP/archive/refs/tags/v3.01.01.zip)

uC-LIB下载：[https://github.com/weston-embedded/uC-LIB.git](https://github.com/weston-embedded/uC-LIB.git)

## 漏洞分析

首先分析一下http-s\_req.c中的HTTPsReq\_Handle函数

这个函数就是一个http的请求处理

通过一个循环，如果对应的State正确则会对对应的请求字段进行解析

字段正常解析之后会依次循环解析下一个字段

```plain
void  HTTPsReq_Handle (HTTPs_INSTANCE  *p_instance,
                       HTTPs_CONN      *p_conn)
{
......

    done = DEF_NO;
    while (done != DEF_YES) {
        switch (p_conn->State) {

            case HTTPs_CONN_STATE_REQ_INIT:
                 HTTPs_STATS_INC(p_ctr_stats->Req_StatRxdCtr);
#if (HTTPs_CFG_HDR_RX_EN == DEF_ENABLED)
                 p_conn->HdrType = HTTPs_HDR_TYPE_REQ;
#endif
                 p_conn->State   = HTTPs_CONN_STATE_REQ_PARSE_METHOD;
                 break;

                                                                /* ---------------- PARSE REQ METHOD ------------------ */
            case HTTPs_CONN_STATE_REQ_PARSE_METHOD:
                 HTTPsReq_MethodParse(p_instance, p_conn, &err);
                 switch (err) {
                     case HTTPs_ERR_NONE:                                    /* If the Method parsing is successful...   */
                          p_conn->State = HTTPs_CONN_STATE_REQ_PARSE_URI;    /* ...go to the next step.                  */
                          break;

                     default:                                                /* If the Method parsing has failed...      */
                          HTTPs_ERR_INC(p_ctr_err->Req_ErrInvalidCtr);       /* ...generate an error...                  */
                          p_conn->ErrCode   = err;
                          p_conn->State     = HTTPs_CONN_STATE_ERR_INTERNAL;
                          p_conn->SockState = HTTPs_SOCK_STATE_NONE;
                          done              = DEF_YES;                       /* ...and exit the state machine.           */
                          break;
                 }
                 break;

                                                                /* ------------------ PARSE REQ URI ------------------- */
            case HTTPs_CONN_STATE_REQ_PARSE_URI:
                 is_query_str_found = HTTPsReq_URI_Parse(p_instance, p_conn, &err);
                 switch (err) {
                     case HTTPs_ERR_NONE:                            /* If the URI parsing is successful...              */
                          if (is_query_str_found == DEF_YES) {       /* ...check if query string need to be parse.       */
                              p_conn->State = HTTPs_CONN_STATE_REQ_PARSE_QUERY_STRING;
                          } else {
                              p_conn->State = HTTPs_CONN_STATE_REQ_PARSE_PROTOCOL_VERSION;
                          }
                          break;

                     case HTTPs_ERR_REQ_MORE_DATA_REQUIRED:          /* If more data is required to complete the...      */
                          p_conn->SockState = HTTPs_SOCK_STATE_RX;   /* ...URI Parsing, exit the state machine.          */
                          done                = DEF_YES;
                          break;

                     default:                                        /* If the URI parsing has failed...                 */
                          HTTPs_ERR_INC(p_ctr_err->Req_ErrInvalidCtr); /* ...generate an error...                        */
                          p_conn->SockState = HTTPs_SOCK_STATE_NONE;
                          p_conn->ErrCode   = err;
                          p_conn->State     = HTTPs_CONN_STATE_ERR_INTERNAL;
                          done              = DEF_YES;               /* ...and exit the state machine.                   */
                          break;
                 }
                 break;

                                                                /* --------------- PARSE REQ QUERY STR ---------------- */
            case HTTPs_CONN_STATE_REQ_PARSE_QUERY_STRING:
                 HTTPsReq_QueryStrParse(p_instance, p_conn, &err);
                 switch (err) {
                     case HTTPs_ERR_NONE:                            /* If the Query Str parsing is successful...        */
                                                                     /* ...go to the next step.                          */
                          p_conn->State = HTTPs_CONN_STATE_REQ_PARSE_PROTOCOL_VERSION;
                          break;

                     case HTTPs_ERR_REQ_MORE_DATA_REQUIRED:          /* If more data is required to complete the...      */
                          p_conn->SockState = HTTPs_SOCK_STATE_RX;   /* ...Query Str Parsing, exit the state machine.    */
                          done              = DEF_YES;
                          break;

                     default:                                        /* If the Query Str parsing has failed...           */
                          HTTPs_ERR_INC(p_ctr_err->Req_ErrInvalidCtr); /* ...generate an error...                        */
                          p_conn->SockState = HTTPs_SOCK_STATE_NONE;
                          p_conn->ErrCode   = err;
                          p_conn->State     = HTTPs_CONN_STATE_ERR_INTERNAL;
                          done              = DEF_YES;               /* ...and exit the state machine.                   */
                          break;
                 }
                 break;

                                                                /* -------------- PARSE REQ PROTOCOL VER -------------- */
            case HTTPs_CONN_STATE_REQ_PARSE_PROTOCOL_VERSION:
                 HTTPsReq_ProtocolVerParse(p_instance, p_conn, &err);
                    switch (err) {
                        case HTTPs_ERR_NONE:                            /* If the Protocol Ver parsing is successful... */
                                                                        /* ...go to the next step.                      */
                             p_conn->State        = HTTPs_CONN_STATE_REQ_PARSE_HDR;
                             p_conn->SockState    = HTTPs_SOCK_STATE_NONE;
                             DEF_BIT_CLR(p_conn->Flags, HTTPs_FLAG_RESP_LOCATION);
                             break;

                        case HTTPs_ERR_REQ_MORE_DATA_REQUIRED:          /* If more data is required to complete the...  */
                             p_conn->SockState = HTTPs_SOCK_STATE_RX;   /* ...Protocol Ver parsing, exit the state...   */
                             done              = DEF_YES;               /* ...machine.                                  */
                             break;

                        default:                                      /* If the Protocol Ver parsing has failed...      */
                             HTTPs_ERR_INC(p_ctr_err->Req_ErrInvalidCtr); /* ...generate an error...                    */
                             p_conn->SockState = HTTPs_SOCK_STATE_NONE;
                             p_conn->ErrCode   = err;
                             p_conn->State     = HTTPs_CONN_STATE_ERR_INTERNAL;
                             done                = DEF_YES;             /* ...and exit the state machine.               */
                             break;
                    }
                    break;

                                                                /* ------------------ PARSE REQ HDR ------------------- */
            case HTTPs_CONN_STATE_REQ_PARSE_HDR:
                 HTTPsReq_HdrParse(p_instance, p_conn, &err);   /* See Note #2.                                         */
                 switch (err) {
                     case HTTPs_ERR_NONE:                       /* If the Protocol Ver parsing is successful...         */
                                                                /* ...go to the next step.                              */
                          p_conn->State     = HTTPs_CONN_STATE_REQ_LINE_HDR_HOOK;
                          p_conn->SockState = HTTPs_SOCK_STATE_NONE;
                          HTTPs_STATS_INC(p_ctr_stats->Req_StatProcessedCtr);
                          break;

                     case HTTPs_ERR_REQ_MORE_DATA_REQUIRED:     /* If more data is required to complete the...          */
                          p_conn->SockState = HTTPs_SOCK_STATE_RX; /* ...Protocol Ver parsing, exit the state...        */
                          done              = DEF_YES;          /* ...machine.                                          */
                          break;

                     default:                                    /* If the Header parsing has failed...                  */
                         HTTPs_ERR_INC(p_ctr_err->Req_ErrInvalidCtr); /* ...generate an error...                         */
                         p_conn->ErrCode = err;
                         p_conn->State   = HTTPs_CONN_STATE_ERR_INTERNAL;
                         done            = DEF_YES;              /* ...and exit the state machine.                       */
                         break;
                 }
                 break;

                                                                /* --------------- CONN REQ EXT PROCESS --------------- */
            case HTTPs_CONN_STATE_REQ_LINE_HDR_HOOK:
                 hook_def = HTTPs_HOOK_DEFINED(p_cfg->HooksPtr, OnReqHook);
                 if (hook_def == DEF_YES) {
                     accepted = p_cfg->HooksPtr->OnReqHook(p_instance,
                                                           p_conn,
                                                           p_cfg->Hooks_CfgPtr);
                     if (accepted != DEF_YES) {
                                                                /* If the connection is not authorized ...              */
                         if (p_conn->StatusCode == HTTP_STATUS_OK) {
                             p_conn->StatusCode = HTTP_STATUS_UNAUTHORIZED;
                         }
                         DEF_BIT_SET(p_conn->Flags, HTTPs_FLAG_REQ_FLUSH);
                         p_conn->State = HTTPs_CONN_STATE_REQ_BODY_FLUSH_DATA;
                     }
                 }
                                                                /* Otherwise, receive the body.                         */
                 p_conn->State     = HTTPs_CONN_STATE_REQ_BODY_INIT;
                 done              = DEF_YES;                   /* ... exit the state machine.                          */
                 break;


            default:
                HTTPs_ERR_INC(p_ctr_err->Req_ErrStateUnkownCtr);
                p_conn->ErrCode = HTTPs_ERR_STATE_UNKNOWN;
                p_conn->State   = HTTPs_CONN_STATE_ERR_INTERNAL;
                done            = DEF_YES;
                break;
        }
    }
}
```

此次漏洞分析的主要漏洞都在字段解析中

### oob write vulnerability

Method解析中存在长度重置错误引起后续的out-of-bounds write vulnerability

-   首先在\[1\]中，p\_request\_method\_start会获取整个数据包的第一个有效字符
-   计算长度，将第一个有效字符之前的无效字符长度给去掉\[2\]
-   接着利用`Str_Char_N`函数截取空格，此时将位置返回给`p_request_method_end`\[3\]
-   然后取得`p_request_method_end - p_request_method_start`的长度，也就是method的长度\[4\]
-   `p_conn->RxBufLenRem`会减去上面的method长度\[5\]

漏洞点出在了\[4\]这里，这里的len直接被赋值成了method的长度，没有考虑到前面无效字符，导致`p_conn->RxBufLenRem -= len`这里多出了无效字符的长度，也就是有多少个无效字符，长度就多出多少

而\[6\]这里就是正确的计算

```plain
static  void  HTTPsReq_MethodParse (HTTPs_INSTANCE  *p_instance,
                                HTTPs_CONN      *p_conn,
                                HTTPs_ERR       *p_err)
{
...
    len = p_conn->RxBufLenRem;
...
                                                                /* Move the start ptr to the first meanningful char.    */
    p_request_method_start = HTTP_StrGraphSrchFirst(p_conn->RxBufPtr, len);             /* [1] p_request_method_start advances to the 
                                                                                            first character between 0x21 - 0x7e*/
    if (p_request_method_start == DEF_NULL) {
    *p_err = HTTPs_ERR_REQ_FORMAT_INVALID;
        return;
    }
    len -= p_request_method_start - p_conn->RxBufPtr ;                                  /* [2] len is correctly calculated */
                                                                /* Find the end of method string.                       */
    p_request_method_end =  Str_Char_N(p_request_method_start, len, ASCII_CHAR_SPACE);  /* [3] */
    if (p_request_method_end == DEF_NULL) {
    *p_err = HTTPs_ERR_REQ_FORMAT_INVALID;
        return;
    }
    len = p_request_method_end - p_request_method_start;                                /* [4] This is the bug */
...
    p_conn->RxBufLenRem -= len;                                                         /* [5] */
    p_conn->RxBufPtr     = p_request_method_end;                                        /* [6] */
}
```

在处理BodyForm的时候会将上面这个计算错误的长度赋值到len\_str

然后`HTTPsReq_BodyFormAppKeyValBlkAdd`函数调用这个长度

```plain
static  CPU_BOOLEAN  HTTPsReq_BodyFormAppParse (HTTPs_INSTANCE  *p_instance,
                                                HTTPs_CONN      *p_conn,
                                                HTTPs_ERR       *p_err)
{
...
    while (done != DEF_YES) {
                                                                /* ----------- VALIDATE CUR KEY/VAL PAIRS ------------- */
        p_key_next = Str_Char_N(p_key_name,                     /* Srch beginning of next key/val pairs.                */
                                p_conn->RxBufLenRem,
                                ASCII_CHAR_AMPERSAND);

        if (p_key_next == DEF_NULL) {                           /* If next key/val pairs not found ...                  */
                                                                /* ... determine if all data are received or next ...   */
                                                                /* ... key/val pairs are missing.                       */
            len_content_rxd = p_conn->ReqContentLenRxd
                            + p_conn->RxBufLenRem;

            if (len_content_rxd < p_conn->ReqContentLen) {      /* If data are missing ...                              */
            *p_err = HTTPs_ERR_REQ_MORE_DATA_REQUIRED;       /* ... receive more data.                               */
                goto exit;

            } else {                                            /* If all data received ...                             */
                len_str = p_conn->RxBufLenRem;                  /* [1] 
                                                                /* ... last key/val pairs to parse.                     */
            }

        } else {                                                /* Next key/val pairs found ...                         */
            len_str = (p_key_next - p_key_name);                /* ... parse key/val pairs.                             */
        }

                                                                /* Add key-Value block to list.                         */
        result = HTTPsReq_BodyFormAppKeyValBlkAdd(p_instance,
                                                p_conn,
                                                p_key_name,
                                                len_str,
                                                p_err);         /* [2] */
...
}
```

在`HTTPsReq_BodyFormAppKeyValBlkAdd`中调用了`HTTPsReq_URL_EncodeStrParse`函数，str\_len是一个用户控制的长度，在\[1\]这里导致oob write null

```plain
static  CPU_BOOLEAN  HTTPsReq_URL_EncodeStrParse (HTTPs_INSTANCE  *p_instance,
                                                HTTPs_CONN      *p_conn,
                                                HTTPs_KEY_VAL   *p_key_val,
                                                CPU_BOOLEAN      from_query,
                                                CPU_CHAR        *p_str,
                                                CPU_SIZE_T       str_len)
{
...
                                                                /* Find separator "=".                                  */
    p_str_sep = Str_Char_N(p_str, str_len, ASCII_CHAR_EQUALS_SIGN);

    p_str[str_len] = ASCII_CHAR_NULL;                           /* [1] */
...
}
```

### off by null vulnerability

header解析异常后引起的单字节NULL溢出

-   如果上面的header解析没有符合要求的，则会进入default
-   在\[1\]中得到解析失败的header长度len
-   在\[2\]中header长度len会与`p_cfg->HdrRxCfgPtr->DataLenMax`最大长度进行比较，如果超出则return
-   接着在最后补上一个NULL\[4\]

漏洞点出在了\[2\]这里，这里的len缺少了验证len等于`p_cfg->HdrRxCfgPtr->DataLenMax`长度的情况

如果len等于`p_cfg->HdrRxCfgPtr->DataLenMax`，则\[3\]这里会指向现有标准长度的最后一位，而\[4\]这里又会继续添加一个NULL，所以造成了一个单字节NULL溢出

```plain
File: http-s_req.c
1759:                     default:
1760: #if (HTTPs_CFG_HDR_RX_EN == DEF_ENABLED)
1761:                          if ((p_cfg->HdrRxCfgPtr != DEF_NULL) &&
1762:                              (p_cfg->HooksPtr    != DEF_NULL)) {
1763:                              keep = p_cfg->HooksPtr->OnReqHdrRxHook(p_instance,                       /* [0] */
1764:                                                                     p_conn,
1765:                                                                     p_cfg->Hooks_CfgPtr,
1766:                                                                     field);
...
1776:                              if (keep == DEF_YES) {
...
1789:                                 p_val = HTTPsReq_HdrParseValGet(p_field,
1790:                                                                 p_field_dict_entry->StrLen,
1791:                                                                 p_field_end,
1792:                                                                &len);                                 /* [1] */
...
1796:                                     if (len > p_cfg->HdrRxCfgPtr->DataLenMax) {                       /* [2] */
1797:                                         HTTPs_ERR_INC(p_ctr_errs->Req_ErrHdrDataLenInv);
1798:                                        *p_err = HTTPS_ERR_REQ_HDR_INVALID_VAL_LEN;
1799:                                         return;
1800:                                     }
...
1807:                                     p_str                 = (CPU_CHAR *)p_req_hdr_blk->ValPtr + len;  /* [3] */
1808:                                    *p_str                 =  ASCII_CHAR_NULL;                         /* [4] */
1809:                                     p_req_hdr_blk->ValLen =  len + 1;
```

### off by null vulnerability

host解析后引起的单字节NULL溢出

-   \[1\]中确定HOST长度
-   \[2\]这里检查长度，最长为`p_cfg->HostNameLenMax`
-   利用`Str_Copy_N`将HOST拷贝到`p_conn->HostPtr`中
-   最后补上一个NULL截断

如果\[2\]这里的长度刚好等于`p_cfg->HostNameLenMax`，此时\[3\]这里就会溢出一个单字节NULL

```plain
File: http-s_req.c
1713:                                                                 /* Find beginning of host string val.                   */
1714:                          p_val = HTTPsReq_HdrParseValGet(p_field,
1715:                                                          HTTP_STR_HDR_FIELD_HOST_LEN,
1716:                                                          p_field_end,
1717:                                                         &len);                        /* [1] */
1718: 
1719:                          len   = DEF_MIN(len, p_cfg->HostNameLenMax);                 /* [2] */
1720: 
1721:                                                                 /* Copy host name val in Conn struct.                   */
1722:                          (void)Str_Copy_N(p_conn->HostPtr, p_val, len);
1723:                                                                 /* Make sure to create a string.                        */
1724:                          p_conn->HostPtr[len] = ASCII_CHAR_NULL;                      /* [3] */
```

### Heap Overflow Vulnerability

boundary解析后引起的堆溢出

在解析之后，可以看到len并没有进行任何的限制，直接利用\[0\]进行了`Str_Copy_N`到了`p_conn->FormBoundaryPtr`中，导致了堆溢出

```plain
File: http-s_req.c
1661:                                               p_val++;          /* Remove space before boundary val.                    */
1662:                                               p_val = HTTP_StrGraphSrchFirst(p_val,
1663:                                                                              len);
1664:                                               len   = p_field_end - p_val;
1665: 
1666:                                                                 /* Copy boundary val to Conn struct.                    */
1667:                                               Str_Copy_N(p_conn->FormBoundaryPtr,                         /* [0] */
1668:                                                          p_val,
1669:                                                          len);
```

### Buffer Overflow Vulnerability

在解析Protocol时引起的整数下溢，最后导致Buffer Overflow Vulnerability

-   \[1\]这里会得到第一个有效字符
-   \[2\]这里找到\\r\\n判断最后一个字符，这样就得到了一个Protocol字段
-   然后\[3\]这里会更新长度、位置

最终的漏洞点发生在\[3\]这里，整数下溢。如果前面存在无效字符，\[1\]这里跳过无效字符之后，len并没有更新长度，还是原始的`RxBufLenRem`

而后面搜索`\r\n`时使用这个len值就会越界访问，在缓冲区之外搜索，由于`p_protocol_ver_end`可能位于原始缓冲区之外，在更新`RxBufLenRem`时这个`p_protocol_ver_end - p_conn->RxBufPtr + 2`可能是一个负数，\[3\]这里减去这个负数后，`RxBufLenRem`发生整数下溢

```plain
/* HTTPsReq_ProtocolVerParse */
static  void  HTTPsReq_ProtocolVerParse (HTTPs_INSTANCE  *p_instance,
                                     HTTPs_CONN      *p_conn,
                                     HTTPs_ERR       *p_err)
{
...
    len = p_conn->RxBufLenRem;
...
                                                                /* Move the pointer to the next meaningful char.        */
    p_protocol_ver_start = HTTP_StrGraphSrchFirst(p_conn->RxBufPtr, len);       /* [1] p_protocol_ver_start advances to the first character 
                                                                                    between 0x21 - 0x7e */
    if (p_protocol_ver_start == DEF_NULL) {
    *p_err               = HTTPs_ERR_REQ_FORMAT_INVALID;
        return;
    }
                                                                /* Find the end of the request line.                    */
    p_protocol_ver_end = Str_Str_N(p_protocol_ver_start, STR_CR_LF, len);       /* [2] this will search outside of the buffer since len 
                                                                                    does not account for the previously skipped characters in [1] */
    if (p_protocol_ver_end == DEF_NULL) {                       /* If not found, check to get more data.                */
        if (p_conn->RxBufPtr != p_conn->BufPtr) {
        *p_err = HTTPs_ERR_REQ_MORE_DATA_REQUIRED;
        } else {
        *p_err = HTTPs_ERR_REQ_FORMAT_INVALID;
        }
        return;
    }
...
                                                                /* Update the RxBuf ptr.                                */
    p_conn->RxBufLenRem      -= (p_protocol_ver_end - p_conn->RxBufPtr) + 2;    /* [3] Since p_protocol_ver_end can be outside of the 
                                                                                    original buffer, this could lead to an integer underflow */
    p_conn->RxBufPtr          =  p_protocol_ver_end + 2;
...
}
```

发生整数下溢后，下溢的长度值`p_conn->RxBufLenRem`会变得很大，于Mem\_Copy发生溢出，接下来，下溢的长度值再次用于计算将在后续调用接收\[2\] 时使用的指针，这会导致攻击者控制的数据被写入接收缓冲区的边界之外

```plain
CPU_BOOLEAN  HTTPsSock_ConnDataRx (HTTPs_INSTANCE  *p_instance,
                               HTTPs_CONN      *p_conn)
{
...
    if ((p_conn->RxBufLenRem > 0) &&
        (p_conn->RxBufPtr   != p_conn->BufPtr)) {               /* If data is still present in the rx buf.              */
                                                                /* Move rem data to the beginning of the rx buf.        */
            Mem_Copy(p_conn->BufPtr, p_conn->RxBufPtr, p_conn->RxBufLenRem);        //[1] the length used here is very large because of the underflow
    }
    p_buf   = p_conn->BufPtr + p_conn->RxBufLenRem;                             //[2] p_buf now points very far outside of the original buffer
    buf_len = p_conn->BufLen - p_conn->RxBufLenRem;
...
    rx_len = (CPU_INT16U)NetSock_RxDataFrom(        p_conn->SockID,
                                            (void *)p_buf,
                                                    buf_len,
                                                    NET_SOCK_FLAG_NO_BLOCK,
                                                &p_conn->ClientAddr,
                                                &addr_len_client,
                                                    DEF_NULL,
                                                    DEF_NULL,
                                                    DEF_NULL,
                                                &err);
...
}
```

至此漏洞分析完成，还有漏洞验证写poc，但是由于时间原因这里只写了漏洞分析

## Reference

[https://talosintelligence.com/vulnerability\_reports/TALOS-2023-1725](https://talosintelligence.com/vulnerability_reports/TALOS-2023-1725)
