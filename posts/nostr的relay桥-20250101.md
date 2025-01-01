---
title: Nostr的Relay桥
date: 2025-01-01
created_at: 2025-01-01 14:31:49
tags: [Nostr,server]
---

- 项目：[NostrBridge](https://github.com/duozhutuan/NostrBridge)

1. 修改`server.js`中的监听端口

2. 可以修改`server.js`自定义端口

3. 用Nginx或其他反向代理该端口



启动命令：
```
# 进入目录
cd /opt/NostrBridge

# 用forever启动，设定日志到/dev/null 避免占用磁盘空间
forever start \
  -a \
  -l /dev/null \
  --minUptime 5000 \
  --spinSleepTime 2000 \
  src/server.js
```

---

也可以使用项目中的`cli.js`实现本地relay桥

修改`config.js`中的localserver部分，改为自己的内网IP加端口，使用`ws://`

在`cli.js`中添加需要桥接的远端relay

在本地启动`node src/cli.js`
