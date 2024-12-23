# My Blog

这是一个使用 Python 构建的静态博客生成器。

## 初始设置

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **在 GitHub 上创建新仓库**
   - 登录 GitHub
   - 创建新仓库，名称可以是 `<你的用户名>.github.io` 或任意名称
   - 不要初始化仓库（不要添加 README、.gitignore 等文件）

3. **初始化本地仓库**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <你的仓库URL>
git push -u origin main
```

## 日常使用

1. **创建新文章**
```bash
python blog.py new "文章标题"
```
这会在 `posts` 目录下创建一个新的 markdown 文件，格式为：`文章标题-YYYYMMDD.md`

2. **编写文章**
在 `posts` 目录下编辑对应的 markdown 文件。文件开头的 YAML 格式元数据如下：
```yaml
---
title: 文章标题
date: YYYY-MM-DD
tags: [标签1, 标签2]
---

这里是文章内容...
```

3. **构建网站**
```bash
python blog.py build
```
这会在 `output` 目录生成所有静态文件

4. **部署到 GitHub Pages**
```bash
cd output
git init
git add .
git commit -m "Deploy blog"
git branch -M gh-pages
git remote add origin <你的仓库URL>
git push -u origin gh-pages -f
```

5. **设置 GitHub Pages**
   - 去到你的 GitHub 仓库设置
   - 找到 "Pages" 选项（在 Settings 菜单下）
   - 在 "Source" 选项中选择 "gh-pages" 分支
   - 保存设置

你的博客将在以下地址可访问：
- 如果仓库名是 `<用户名>.github.io`：`https://<用户名>.github.io`
- 如果是其他名称：`https://<用户名>.github.io/<仓库名>`

## 配置自定义域名

1. **创建 CNAME 文件**
   - 在 `templates` 目录下创建 `CNAME` 文件
   - 文件内容为你的域名，例如：`your-domain.com`

2. **DNS 设置**
   
   对于根域名（`your-domain.com`），添加这些 A 记录：
   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```

   对于子域名（如 `blog.your-domain.com`），添加 CNAME 记录：
   - 类型：`CNAME`
   - 主机记录：`blog`（或其他子域名）
   - 记录值：`<你的用户名>.github.io`

3. **等待 DNS 生效**
   - DNS 更改可能需要最多 24 小时生效
   - 可以使用 `dig` 或 `nslookup` 命令检查 DNS 是否已更新

## 后续更新博客

1. 写新文章：`python blog.py new "文章标题"`
2. 编辑文章内容（在 `posts` 目录下）
3. 构建：`python blog.py build`
4. 部署：进入 `output` 目录，执行：
```bash
git add .
git commit -m "Update blog"
git push origin gh-pages -f
```

## 目录结构

- `posts/`: 存放 Markdown 格式的博客文章
- `templates/`: HTML 模板文件
- `static/`: 样式表和其他静态资源
- `output/`: 生成的静态网站文件（已添加到 .gitignore）

## 注意事项

- 主分支（main）保存博客源码
- gh-pages 分支保存生成的静态文件
- 每次部署时都需要强制推送 gh-pages 分支（使用 `-f` 参数）
- `output` 目录已添加到 `.gitignore` 中，避免源码仓库包含生成的文件
