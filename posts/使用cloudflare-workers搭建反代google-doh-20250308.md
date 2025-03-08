---
title: 使用Cloudflare Workers搭建反代Google DoH
date: 2025-03-08
created_at: 2025-03-08 11:47:05
tags: [Cloudflare Workers,DoH]
---

### 转自[Nodeseek--使用Workers搭建反代加密DNS](https://www.nodeseek.com/post-282877-1)，仅作备份

代码如下
```
export default {
  async fetch(request) {
    let url = new URL(request.url);

    // 仅允许 /doh, /dns-query特征明显，换成别的
    if (url.pathname !== "/doh") {
      return new Response("Not Found", { status: 404 });
    }

    // 目标 DoH 服务器
    let targetURL = "https://dns.google/dns-query" + url.search;

    let modifiedRequest = new Request(targetURL, {
      method: request.method,
      headers: new Headers(request.headers),
      body: request.body,
      redirect: "follow"
    });

    // 设置正确的 Host 头，避免 Google 拒绝请求
    modifiedRequest.headers.set("Host", "dns.google");
    modifiedRequest.headers.set("Accept", "application/dns-message");

    let response = await fetch(modifiedRequest);

    let newHeaders = new Headers(response.headers);
    newHeaders.set("Access-Control-Allow-Origin", "*"); // 允许 CORS

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders
    });
  }
}

```

最好将默认路径`/dns-query`换成别的，或许更不容易被阻断

部署之后绑定自定域名，使用`https://your.domain/doh`即可进行加密DNS查询



