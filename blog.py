import os
import shutil
import frontmatter
import markdown2
from jinja2 import Environment, FileSystemLoader
import click
from datetime import datetime
import subprocess
from xml.etree import ElementTree as ET
from email.utils import formatdate
import urllib.parse

class BlogGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.ensure_directories()
        self.site_url = self._get_site_url()

    def _get_site_url(self):
        """从 CNAME 文件获取网站 URL"""
        cname_path = os.path.join('templates', 'CNAME')
        if os.path.exists(cname_path):
            with open(cname_path, 'r') as f:
                return f"https://{f.read().strip()}"
        return "http://localhost:8000"  # 默认本地地址

    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = ['posts', 'templates', 'static', 'output']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def read_post(self, filename):
        """读取并解析markdown文件"""
        with open(os.path.join('posts', filename), 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            
        # 设置默认元数据
        metadata = post.metadata
        metadata.setdefault('title', os.path.splitext(filename)[0])
        metadata.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
        metadata.setdefault('tags', [])
        
        # 转换内容
        content = markdown2.markdown(post.content, extras=['fenced-code-blocks', 'tables'])
        return metadata, content

    def generate_post(self, filename):
        """生成单篇文章的HTML"""
        metadata, content = self.read_post(filename)
        template = self.env.get_template('post.html')
        output = template.render(
            title=metadata['title'],
            date=metadata['date'],
            tags=metadata['tags'],
            content=content
        )
        
        # 创建输出文件
        output_path = os.path.join('output', os.path.splitext(filename)[0] + '.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        
        return metadata

    def generate_index(self, posts, tags):
        """生成博客索引页面"""
        template = self.env.get_template('index.html')
        output = template.render(posts=posts, tags=tags)
        
        with open('output/index.html', 'w', encoding='utf-8') as f:
            f.write(output)

    def generate_tag_pages(self, posts):
        """为每个标签生成单独的页面"""
        # 收集每个标签的文章
        tag_posts = {}
        for post in posts:
            for tag in post.get('tags', []):
                if tag not in tag_posts:
                    tag_posts[tag] = []
                tag_posts[tag].append(post)
        
        # 为每个标签生成页面
        template = self.env.get_template('tag.html')
        os.makedirs('output/tags', exist_ok=True)
        
        for tag, tag_posts_list in tag_posts.items():
            output = template.render(
                tag=tag,
                posts=sorted(tag_posts_list, key=lambda x: x['date'], reverse=True)
            )
            
            # 使用 URL 安全的文件名
            safe_tag = tag.lower().replace(' ', '-')
            with open(f'output/tags/{safe_tag}.html', 'w', encoding='utf-8') as f:
                f.write(output)
            
        return tag_posts

    def generate_rss(self, posts):
        """生成 RSS feed"""
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        # 添加频道基本信息
        title = ET.SubElement(channel, 'title')
        title.text = 'CHIU BLOG'
        
        link = ET.SubElement(channel, 'link')
        link.text = self.site_url
        
        description = ET.SubElement(channel, 'description')
        description.text = 'Sharing Technology and Life'
        
        language = ET.SubElement(channel, 'language')
        language.text = 'zh-CN'
        
        lastBuildDate = ET.SubElement(channel, 'lastBuildDate')
        lastBuildDate.text = formatdate(localtime=True)
        
        # 添加文章
        for post in posts:
            item = ET.SubElement(channel, 'item')
            
            item_title = ET.SubElement(item, 'title')
            item_title.text = post['title']
            
            item_link = ET.SubElement(item, 'link')
            item_link.text = f"{self.site_url}/{post['url']}"
            
            item_guid = ET.SubElement(item, 'guid')
            item_guid.text = f"{self.site_url}/{post['url']}"
            
            item_pubDate = ET.SubElement(item, 'pubDate')
            # 处理日期可能是字符串或datetime.date的情况
            if isinstance(post['date'], str):
                pub_date = datetime.strptime(post['date'], '%Y-%m-%d')
            else:
                pub_date = datetime.combine(post['date'], datetime.min.time())
            timestamp = pub_date.timestamp()
            item_pubDate.text = formatdate(timestamp, localtime=True)
            
            # 获取文章内容
            with open(os.path.join('posts', post['url'].replace('.html', '.md')), 'r', encoding='utf-8') as f:
                post_content = frontmatter.load(f)
                content_html = markdown2.markdown(post_content.content)
            
            item_description = ET.SubElement(item, 'description')
            item_description.text = content_html
            
            if post.get('tags'):
                for tag in post['tags']:
                    category = ET.SubElement(item, 'category')
                    category.text = tag
        
        # 生成 RSS 文件
        tree = ET.ElementTree(rss)
        tree.write('output/feed.xml', encoding='utf-8', xml_declaration=True)

    def copy_static_files(self):
        """复制静态文件到输出目录"""
        if os.path.exists('static'):
            if os.path.exists('output/static'):
                shutil.rmtree('output/static')
            shutil.copytree('static', 'output/static')
        
        # 复制 CNAME 文件
        cname_path = os.path.join('templates', 'CNAME')
        if os.path.exists(cname_path):
            shutil.copy2(cname_path, os.path.join('output', 'CNAME'))

    def deploy_to_github(self):
        """部署到GitHub Pages"""
        try:
            # 确保在output目录中
            os.chdir('output')
            
            # 初始化git仓库（如果需要）
            if not os.path.exists('.git'):
                subprocess.run(['git', 'init'])
                subprocess.run(['git', 'checkout', '-b', 'gh-pages'])
            
            # 添加所有文件并提交
            subprocess.run(['git', 'add', '.'])
            subprocess.run(['git', 'commit', '-m', f'Update blog: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            
            # 推送到远程仓库
            subprocess.run(['git', 'push', 'origin', 'gh-pages', '-f'])
            
            print("Successfully deployed to GitHub Pages!")
            
        except Exception as e:
            print(f"Error deploying to GitHub Pages: {str(e)}")
        finally:
            os.chdir('..')

    def build(self):
        """构建博客"""
        # 清理输出目录，保留.git
        if os.path.exists('output'):
            for item in os.listdir('output'):
                if item != '.git':
                    item_path = os.path.join('output', item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
        else:
            os.makedirs('output')
        
        # 生成所有文章
        posts = []
        for filename in os.listdir('posts'):
            if filename.endswith('.md'):
                metadata = self.generate_post(filename)
                posts.append({
                    'title': metadata['title'],
                    'date': metadata['date'],
                    'tags': metadata['tags'],
                    'url': os.path.splitext(filename)[0] + '.html'
                })
        
        # 按日期排序文章
        posts.sort(key=lambda x: x['date'], reverse=True)
        
        # 生成标签页面并获取标签统计
        tag_posts = self.generate_tag_pages(posts)
        
        # 准备标签云数据
        tags = []
        for tag, tag_posts_list in tag_posts.items():
            count = len(tag_posts_list)
            safe_tag = tag.lower().replace(' ', '-')
            tags.append({
                'name': tag,
                'count': count,
                'url': f'/tags/{safe_tag}.html'
            })
        
        # 按文章数量排序标签
        tags.sort(key=lambda x: (-x['count'], x['name']))
        
        # 生成索引页
        self.generate_index(posts, tags)
        
        # 生成 RSS feed
        self.generate_rss(posts)
        
        # 复制静态文件
        self.copy_static_files()
        
        print("Blog built successfully!")

@click.group()
def cli():
    """静态博客生成器命令行工具"""
    pass

@cli.command()
def init():
    """初始化博客目录结构和模板"""
    generator = BlogGenerator()
    print("Blog initialized successfully!")

@cli.command()
def build():
    """构建博客"""
    generator = BlogGenerator()
    generator.build()

@cli.command()
def deploy():
    """部署到GitHub Pages"""
    generator = BlogGenerator()
    generator.deploy_to_github()

@cli.command()
@click.argument('title')
def new(title):
    """创建新的博客文章"""
    current_time = datetime.now()
    filename = f"{title.lower().replace(' ', '-')}-{current_time.strftime('%Y%m%d')}.md"
    template = f"""---
title: {title}
date: {current_time.strftime('%Y-%m-%d')}
tags: []
---

Write your content here...
"""
    
    with open(os.path.join('posts', filename), 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"Created new post: {filename}")

@cli.command()
@click.argument('title')
def delete(title):
    """删除博客文章"""
    # 列出所有文章
    posts = []
    for filename in os.listdir('posts'):
        if filename.endswith('.md') and title.lower() in filename.lower():
            posts.append(filename)
    
    if not posts:
        print(f"没有找到包含 '{title}' 的文章")
        return
    
    if len(posts) > 1:
        print("找到多篇文章：")
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post}")
        choice = input("请选择要删除的文章编号（输入数字）：")
        try:
            index = int(choice) - 1
            if 0 <= index < len(posts):
                filename = posts[index]
            else:
                print("无效的选择")
                return
        except ValueError:
            print("请输入有效的数字")
            return
    else:
        filename = posts[0]
    
    try:
        os.remove(os.path.join('posts', filename))
        print(f"已删除文章: {filename}")
        print("请运行 'python blog.py build' 重新构建博客")
    except Exception as e:
        print(f"删除文章时出错: {str(e)}")

if __name__ == '__main__':
    cli()
