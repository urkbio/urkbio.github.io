import os
import shutil
import frontmatter
import markdown2
from jinja2 import Environment, FileSystemLoader
import click
from datetime import datetime
import subprocess

class BlogGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.ensure_directories()

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

    def generate_index(self, posts):
        """生成博客索引页面"""
        template = self.env.get_template('index.html')
        output = template.render(posts=posts)
        
        with open('output/index.html', 'w', encoding='utf-8') as f:
            f.write(output)

    def copy_static_files(self):
        """复制静态文件到输出目录"""
        if os.path.exists('static'):
            if os.path.exists('output/static'):
                shutil.rmtree('output/static')
            shutil.copytree('static', 'output/static')

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
    
    # 清理输出目录
    if os.path.exists('output'):
        shutil.rmtree('output')
    os.makedirs('output')
    
    # 生成所有文章
    posts = []
    for filename in os.listdir('posts'):
        if filename.endswith('.md'):
            metadata = generator.generate_post(filename)
            posts.append({
                'title': metadata['title'],
                'date': metadata['date'],
                'tags': metadata['tags'],
                'url': os.path.splitext(filename)[0] + '.html'
            })
    
    # 按日期排序文章
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    # 生成索引页
    generator.generate_index(posts)
    
    # 复制静态文件
    generator.copy_static_files()
    
    print("Blog built successfully!")

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

if __name__ == '__main__':
    cli()
