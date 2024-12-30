---
title: Cloudflare回源绕过备案
date: 2024-12-30
created_at: 2024-12-30 13:24:04
tags: [技巧]
---
### 针对国内云服务器又没有备案的解决方法，当然可以使用其他端口，比如直接使用8443也是可以开启HTTPS的，可是不够优雅。如果你能接受Cloudflare的延迟，可以通过建立Origin Rules实现重定向。


- 反代服务端口设为 HTTP 8080；HTTPS 8443
- 在cf中解析好对应域名、开启CDN
- 在Cloudflare规则-Origin Rules中创建规则
- 自定义筛选表达式—>主机名 等于 你的域名
- 目标端口重写到8443
