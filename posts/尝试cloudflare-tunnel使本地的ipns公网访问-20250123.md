---
title: 尝试Cloudflare Tunnel使本地的IPNS公网访问
date: 2025-01-23
created_at: 2025-01-23 18:03:48
tags: [Cloudflare Tunnel,内网穿透]
---
### 安装cloudflared: 
```
brew install cloudflare/cloudflare/cloudflared
```
### 验证登录并授权一个域名(先在浏览器上登录Cloudflare，再运行命令): 
```
cloudflared login
```

### 绑定自己域名 (可选)
1. 创建隧道 (前提已经登录并授权一个域名) 
```
cloudflared tunnel create
```
你的家目录中会出现 `~/.cloudflared/[一长串UUID].json`，里面保存这运行这条隧道所需要的授权信息。

2. 配置路由
创建了隧道之后，我们还需要让它可以被访问。Cloudflare 支持将其部署到负载均衡器后端，或者通过 DNS 直接访问。这里只介绍后者的使用方法。
```
cloudflared tunnel route dns [名字或者 UUID] [想要绑定到的域名或其二级域名]

# 例如：
 cloudflare tunnel route dns my-tunnel domain.example.com
# 目标域名必须没有设定相关DNS解析记录
```

### 使用Cloudflare随机域名启动
修改为自己的端口，运行命令之后出现一个随记域名`https://random-name.trycloudflare.com`: 
```
cloudflared tunnel --url http://localhost:8080
```

### 使用自己配置好的域名启动
```
cloudflared tunnel --name [隧道名称] --url http://[站点地址]

# 例如:
cloudflared tunnel --name my-tunnel --url http://127.0.0.1:18181
```

---
参考: 
- [用 Cloudflare Tunnel 进行内网穿透](https://blog.outv.im/2021/cloudflared-tunnel)
- [無痛本地調試：使用 Cloudflare Tunnel 實現 HTTPS 和自定義主機名](https://blog.logto.io/zh-TW/painless-local-debugging)
- [CloudFlare Tunnel 免费内网穿透的简明教程](https://sspai.com/post/79278)
