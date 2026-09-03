#!/usr/bin/env python3
"""
Static Markdown Blog Generator for Harsha Karimikonda Portfolio
Features:
- Zero-dependency: Uses Python 3 standard library
- 100% SEO-Optimized: Open Graph meta tags, Twitter Cards, Schema.org JSON-LD, sitemap.xml, robots.txt
- Obsidian & Cyan Glassmorphism UI: Fully matches web.css
- Syntax Highlighting: Built-in Highlight.js support for Python, Go, C++, CUDA, etc.
"""

import os
import re
import glob
import html
from datetime import datetime

SITE_URL = "https://harsha-karimikonda.github.io"
AUTHOR_NAME = "Harsha Karimikonda"
AUTHOR_TITLE = "Software Engineer & ML Systems Architect"
POSTS_DIR = os.path.join(os.path.dirname(__file__), "posts")
BLOG_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "blog")

def parse_frontmatter(content):
    """Extract YAML frontmatter and markdown body."""
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            for line in fm_text.strip().split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if val.startswith("[") and val.endswith("]"):
                        # Parse simple list
                        items = [x.strip().strip('"').strip("'") for x in val[1:-1].split(",")]
                        meta[key] = [i for i in items if i]
                    else:
                        meta[key] = val
    return meta, body

def markdown_to_html(md_text):
    """Convert Markdown to semantic HTML with syntax-highlighted code blocks."""
    lines = md_text.split("\n")
    html_out = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_list = False
    list_type = None

    def close_list():
        nonlocal in_list, list_type
        if in_list:
            html_out.append(f"</{list_type}>")
            in_list = False
            list_type = None

    for line in lines:
        # Fenced code block check
        if line.strip().startswith("```"):
            if in_code_block:
                close_list()
                code_content = html.escape("\n".join(code_lines))
                lang_class = f"class=\"language-{code_lang}\"" if code_lang else ""
                html_out.append(f"<div class=\"code-block-wrapper\"><pre><code {lang_class}>{code_content}</code></pre></div>")
                in_code_block = False
                code_lines = []
                code_lang = ""
            else:
                close_list()
                in_code_block = True
                code_lang = line.strip()[3:].strip()
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Blank line
        if not line.strip():
            close_list()
            continue

        # Horizontal Rule
        if re.match(r"^(\*{3,}|-{3,}|_{3,})$", line.strip()):
            close_list()
            html_out.append("<hr class=\"article-divider\" />")
            continue

        # Headings
        h_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h_match:
            close_list()
            level = len(h_match.group(1))
            heading_text = h_match.group(2).strip()
            heading_id = re.sub(r"[^a-zA-Z0-9\s-]", "", heading_text).strip().lower()
            heading_id = re.sub(r"[\s]+", "-", heading_id)
            formatted_text = inline_formatting(heading_text)
            html_out.append(f"<h{level} id=\"{heading_id}\">{formatted_text}</h{level}>")
            continue

        # Blockquotes
        if line.startswith("> "):
            close_list()
            quote_content = inline_formatting(line[2:].strip())
            html_out.append(f"<blockquote class=\"article-quote\"><p>{quote_content}</p></blockquote>")
            continue

        # Unordered list
        ul_match = re.match(r"^[-*+]\s+(.*)$", line)
        if ul_match:
            if not in_list or list_type != "ul":
                close_list()
                in_list = True
                list_type = "ul"
                html_out.append("<ul class=\"article-list\">")
            item_text = inline_formatting(ul_match.group(1).strip())
            html_out.append(f"<li>{item_text}</li>")
            continue

        # Ordered list
        ol_match = re.match(r"^\d+\.\s+(.*)$", line)
        if ol_match:
            if not in_list or list_type != "ol":
                close_list()
                in_list = True
                list_type = "ol"
                html_out.append("<ol class=\"article-list-ol\">")
            item_text = inline_formatting(ol_match.group(1).strip())
            html_out.append(f"<li>{item_text}</li>")
            continue

        # Standard Paragraph
        close_list()
        formatted_p = inline_formatting(line.strip())
        html_out.append(f"<p>{formatted_p}</p>")

    close_list()
    return "\n".join(html_out)

def inline_formatting(text):
    """Format inline code, bold, italics, images, and links."""
    # Inline code: `code`
    text = re.sub(r"`([^`]+)`", r'<code class="inline-code">\1</code>', text)
    # Images: ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" class="article-img" loading="lazy" />', text)
    # Links: [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer" class="article-link">\1</a>', text)
    # Bold: **text** or __text__
    text = re.sub(r"\*\*([^*]+)\*\*", r'<strong>\1</strong>', text)
    text = re.sub(r"__([^_]+)__", r'<strong>\1</strong>', text)
    # Italic: *text* or _text_
    text = re.sub(r"\*([^*]+)\*", r'<em>\1</em>', text)
    text = re.sub(r"_([^_]+)_", r'<em>\1</em>', text)
    return text

def calculate_reading_time(text):
    """Estimate reading time based on ~200 WPM."""
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

def generate_article_page(meta, body_html, raw_body, slug):
    """Generate independent SEO-optimized article page with OpenGraph and Schema.org JSON-LD."""
    title = meta.get("title", "Technical Article")
    summary = meta.get("summary", "Technical article by Harsha Karimikonda.")
    date = meta.get("date", "2026-09-03")
    author = meta.get("author", AUTHOR_NAME)
    tags = meta.get("tags", ["Engineering", "Systems"])
    reading_time = calculate_reading_time(raw_body)
    article_url = f"{SITE_URL}/blog/{slug}/"

    tag_pills_html = "".join([f'<span class="tag">{t}</span>' for t in tags])

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {AUTHOR_NAME}</title>
    <meta name="description" content="{summary}">
    <meta name="author" content="{author}">
    <link rel="canonical" href="{article_url}">

    <!-- Open Graph (LinkedIn, Twitter, Facebook, Slack) -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{summary}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{article_url}">
    <meta property="og:site_name" content="{AUTHOR_NAME}">
    <meta property="article:published_time" content="{date}">
    <meta property="article:author" content="{author}">

    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{summary}">

    <!-- Schema.org JSON-LD for Google Rich Snippets -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "TechArticle",
      "headline": "{title}",
      "description": "{summary}",
      "author": {{
        "@type": "Person",
        "name": "{author}",
        "url": "{SITE_URL}"
      }},
      "datePublished": "{date}",
      "mainEntityOfPage": "{article_url}"
    }}
    </script>

    <!-- Stylesheets & Fonts -->
    <link rel="stylesheet" href="../../web.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <style>
        .article-container {{
            max-width: 820px;
            margin: 0 auto;
            padding: 8rem 1.5rem 5rem 1.5rem;
        }}
        .article-header {{
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 2rem;
        }}
        .back-nav {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--cyan);
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            transition: var(--transition-smooth);
        }}
        .back-nav:hover {{
            transform: translateX(-4px);
        }}
        .article-title {{
            font-size: clamp(2rem, 4.5vw, 2.75rem);
            line-height: 1.2;
            margin-bottom: 1.25rem;
            letter-spacing: -0.02em;
        }}
        .article-meta-bar {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            color: var(--text-muted);
            font-size: 0.88rem;
            flex-wrap: wrap;
            margin-bottom: 1.25rem;
        }}
        .article-meta-bar span {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }}
        .article-content {{
            font-size: 1.08rem;
            line-height: 1.8;
            color: var(--text-secondary);
        }}
        .article-content h2 {{
            font-size: 1.75rem;
            color: var(--text-primary);
            margin: 2.5rem 0 1rem 0;
            letter-spacing: -0.01em;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 0.5rem;
        }}
        .article-content h3 {{
            font-size: 1.35rem;
            color: var(--text-primary);
            margin: 2rem 0 0.85rem 0;
        }}
        .article-content p {{
            margin-bottom: 1.5rem;
        }}
        .code-block-wrapper {{
            margin: 1.5rem 0 2rem 0;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid var(--border-subtle);
            box-shadow: var(--shadow-card);
        }}
        .code-block-wrapper pre {{
            margin: 0;
            padding: 1.25rem;
            font-family: var(--font-mono);
            font-size: 0.9rem;
            background: #090d16 !important;
            overflow-x: auto;
        }}
        .inline-code {{
            font-family: var(--font-mono);
            font-size: 0.88rem;
            padding: 0.2rem 0.45rem;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-subtle);
            color: var(--cyan);
        }}
        .article-quote {{
            border-left: 3px solid var(--cyan);
            padding: 0.75rem 1.25rem;
            background: rgba(56, 189, 248, 0.04);
            border-radius: 0 12px 12px 0;
            margin: 1.5rem 0;
            font-style: italic;
            color: var(--text-primary);
        }}
        .article-list, .article-list-ol {{
            padding-left: 1.75rem;
            margin-bottom: 1.5rem;
        }}
        .article-list li, .article-list-ol li {{
            margin-bottom: 0.5rem;
        }}
        .article-link {{
            color: var(--cyan);
            text-decoration: underline;
            text-underline-offset: 3px;
        }}
        .article-author-card {{
            margin-top: 4rem;
            padding: 2rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
            border-radius: 18px;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            backdrop-filter: blur(12px);
        }}
        .author-avatar-icon {{
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background: var(--gradient-brand);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.25rem;
            flex-shrink: 0;
        }}
    </style>
</head>
<body>

    <!-- Ambient Glowing Mesh -->
    <div class="ambient-mesh">
        <div class="mesh-orb orb-1"></div>
        <div class="mesh-orb orb-2"></div>
    </div>

    <!-- Navigation Bar -->
    <header class="navbar">
        <div class="container nav-container">
            <a href="../../#home" class="nav-logo">
                <i data-lucide="terminal"></i>
                <span>Harsha<span class="gradient-text">.dev</span></span>
            </a>

            <ul class="nav-links">
                <li><a href="../../#home" class="nav-link">Home</a></li>
                <li><a href="../../#about" class="nav-link">About</a></li>
                <li><a href="../../#projects" class="nav-link">Projects</a></li>
                <li><a href="../" class="nav-link active">Blog</a></li>
                <li><a href="../../#contact" class="nav-link">Contact</a></li>
            </ul>

            <div class="nav-actions">
                <a href="https://github.com/Harsha-Karimikonda" target="_blank" class="btn-icon" aria-label="GitHub">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-5-2-7-2"></path></svg>
                </a>
            </div>
        </div>
    </header>

    <main class="article-container">
        <a href="../" class="back-nav">
            <i data-lucide="arrow-left"></i>
            <span>Back to All Articles</span>
        </a>

        <article>
            <header class="article-header">
                <h1 class="article-title">{title}</h1>
                <div class="article-meta-bar">
                    <span><i data-lucide="calendar"></i> {date}</span>
                    <span><i data-lucide="clock"></i> {reading_time}</span>
                    <span><i data-lucide="user"></i> {author}</span>
                </div>
                <div class="project-tags">
                    {tag_pills_html}
                </div>
            </header>

            <div class="article-content">
                {body_html}
            </div>

            <div class="article-author-card">
                <div class="author-avatar-icon">HK</div>
                <div>
                    <h4>{author}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.92rem; margin-top: 0.25rem;">
                        MS CS student at the University of Florida & former Associate Data Scientist at Gramener (Straive). Writing about high-throughput ML systems, continuous batching, and scalable distributed architectures.
                    </p>
                    <div style="display: flex; gap: 1rem; margin-top: 0.75rem;">
                        <a href="https://in.linkedin.com/in/harsha-karimikonda-602a47214" target="_blank" class="article-link">LinkedIn</a>
                        <a href="https://github.com/Harsha-Karimikonda" target="_blank" class="article-link">GitHub</a>
                        <a href="https://mlthings.beehiiv.com" target="_blank" class="article-link">Newsletter</a>
                    </div>
                </div>
            </div>
        </article>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container footer-content">
            <div class="footer-copy">
                &copy; 2026 {AUTHOR_NAME}. Published under open engineering research.
            </div>
            <div class="footer-socials">
                <a href="https://github.com/Harsha-Karimikonda" target="_blank" class="btn-icon" aria-label="GitHub">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-5-2-7-2"></path></svg>
                </a>
                <a href="https://in.linkedin.com/in/harsha-karimikonda-602a47214" target="_blank" class="btn-icon" aria-label="LinkedIn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
                </a>
            </div>
        </div>
    </footer>

    <!-- Scripts: Lucide Icons & Highlight.js -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            if (typeof lucide !== 'undefined') lucide.createIcons();
            if (typeof hljs !== 'undefined') hljs.highlightAll();
        }});
    </script>
</body>
</html>
"""

def generate_blog_index(posts):
    """Generate main Blog listing page (/blog/index.html)."""
    cards_html = []
    for post in posts:
        slug = post["slug"]
        meta = post["meta"]
        title = meta.get("title", "Article")
        summary = meta.get("summary", "")
        date = meta.get("date", "2026-09-03")
        reading_time = post["reading_time"]
        tags = meta.get("tags", [])
        tag_pills = "".join([f'<span class="tag">{t}</span>' for t in tags])

        cards_html.append(f"""
        <article class="spotlight-card post-card" style="margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                <div style="display: flex; gap: 0.5rem;">{tag_pills}</div>
                <div style="color: var(--text-muted); font-size: 0.85rem;">{date} • {reading_time}</div>
            </div>
            <h3 style="font-size: 1.5rem; margin-bottom: 0.75rem;">
                <a href="{slug}/" style="color: var(--text-primary);">{title}</a>
            </h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.25rem; line-height: 1.65;">
                {summary}
            </p>
            <div>
                <a href="{slug}/" class="link-arrow">
                    <span>Read Full Article</span>
                    <i data-lucide="arrow-right"></i>
                </a>
            </div>
        </article>
        """)

    if not posts:
        cards_joined = """
        <div class="spotlight-card" style="padding: 3.5rem 2rem; text-align: center; border-radius: 18px; background: var(--bg-card); border: 1px solid var(--border-subtle);">
            <div style="width: 54px; height: 54px; border-radius: 14px; background: rgba(56, 189, 248, 0.1); color: var(--cyan); display: inline-flex; align-items: center; justify-content: center; margin-bottom: 1.25rem;">
                <i data-lucide="sparkles" style="width: 26px; height: 26px;"></i>
            </div>
            <h3 style="font-size: 1.4rem; margin-bottom: 0.75rem;">Articles Coming Soon</h3>
            <p style="color: var(--text-secondary); max-width: 520px; margin: 0 auto 1.5rem auto; line-height: 1.65; font-size: 0.95rem;">
                In-depth technical writeups on LLM serving architectures, continuous dynamic batching, and distributed ML systems are currently in the pipeline.
            </p>
            <a href="../#projects" class="btn btn-secondary">
                <span>Explore Featured Projects</span>
                <i data-lucide="arrow-right"></i>
            </a>
        </div>
        """
    else:
        cards_joined = "\n".join(cards_html)

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog & Systems Research | {AUTHOR_NAME}</title>
    <meta name="description" content="Technical deep dives on high-throughput ML systems, continuous batching, LLM serving planes, and distributed software engineering by Harsha Karimikonda.">
    <meta name="author" content="{AUTHOR_NAME}">
    <link rel="canonical" href="{SITE_URL}/blog/">

    <!-- Open Graph -->
    <meta property="og:title" content="Engineering Blog | {AUTHOR_NAME}">
    <meta property="og:description" content="Technical deep dives on high-throughput ML systems, LLM serving engines, and distributed architectures.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/blog/">

    <link rel="stylesheet" href="../web.css">
    <style>
        .blog-index-container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 8rem 1.5rem 5rem 1.5rem;
        }}
    </style>
</head>
<body>
    <div class="ambient-mesh">
        <div class="mesh-orb orb-1"></div>
        <div class="mesh-orb orb-2"></div>
    </div>

    <header class="navbar">
        <div class="container nav-container">
            <a href="../#home" class="nav-logo">
                <i data-lucide="terminal"></i>
                <span>Harsha<span class="gradient-text">.dev</span></span>
            </a>

            <ul class="nav-links">
                <li><a href="../#home" class="nav-link">Home</a></li>
                <li><a href="../#about" class="nav-link">About</a></li>
                <li><a href="../#projects" class="nav-link">Projects</a></li>
                <li><a href="./" class="nav-link active">Blog</a></li>
                <li><a href="../#contact" class="nav-link">Contact</a></li>
            </ul>

            <div class="nav-actions">
                <a href="https://github.com/Harsha-Karimikonda" target="_blank" class="btn-icon" aria-label="GitHub">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-5-2-7-2"></path></svg>
                </a>
            </div>
        </div>
    </header>

    <main class="blog-index-container">
        <div class="section-header" style="text-align: left; max-width: 100%; margin-bottom: 3.5rem;">
            <div class="section-pill">Engineering Blog</div>
            <h1 class="section-title">Systems & Machine Learning Research</h1>
            <p class="section-desc">Practical deep dives into LLM serving architectures, memory management, and distributed backend pipelines.</p>
        </div>

        <div class="posts-list">
            {cards_joined}
        </div>
    </main>

    <footer class="footer">
        <div class="container footer-content">
            <div class="footer-copy">
                &copy; 2026 {AUTHOR_NAME}. All rights reserved.
            </div>
            <div class="footer-socials">
                <a href="https://github.com/Harsha-Karimikonda" target="_blank" class="btn-icon" aria-label="GitHub">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-5-2-7-2"></path></svg>
                </a>
                <a href="https://in.linkedin.com/in/harsha-karimikonda-602a47214" target="_blank" class="btn-icon" aria-label="LinkedIn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
                </a>
            </div>
        </div>
    </footer>

    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }});
    </script>
</body>
</html>
"""

def generate_sitemap(posts):
    """Generate search-engine sitemap.xml."""
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [
        f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""",
        f"""  <url>
    <loc>{SITE_URL}/blog/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>"""
    ]

    for p in posts:
        slug = p["slug"]
        date = p["meta"].get("date", today)
        urls.append(f"""  <url>
    <loc>{SITE_URL}/blog/{slug}/</loc>
    <lastmod>{date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    return sitemap_content

def generate_robots():
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""

def main():
    print("Building Markdown Blog Engine...")
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(BLOG_OUTPUT_DIR, exist_ok=True)

    post_files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    parsed_posts = []

    for pf in post_files:
        slug = os.path.splitext(os.path.basename(pf))[0]
        with open(pf, "r", encoding="utf-8") as f:
            content = f.read()

        meta, raw_body = parse_frontmatter(content)
        body_html = markdown_to_html(raw_body)
        reading_time = calculate_reading_time(raw_body)

        post_data = {
            "slug": slug,
            "meta": meta,
            "raw_body": raw_body,
            "body_html": body_html,
            "reading_time": reading_time
        }
        parsed_posts.append(post_data)

        # Generate individual post page at blog/<slug>/index.html
        post_dir = os.path.join(BLOG_OUTPUT_DIR, slug)
        os.makedirs(post_dir, exist_ok=True)
        post_html = generate_article_page(meta, body_html, raw_body, slug)
        with open(os.path.join(post_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(post_html)
        print(f"  -> Generated: blog/{slug}/index.html")

    # Sort posts by date descending
    parsed_posts.sort(key=lambda x: x["meta"].get("date", ""), reverse=True)

    # Generate main blog directory (/blog/index.html)
    blog_index_html = generate_blog_index(parsed_posts)
    with open(os.path.join(BLOG_OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(blog_index_html)
    print("  -> Generated: blog/index.html")

    # Generate sitemap.xml in root
    sitemap_xml = generate_sitemap(parsed_posts)
    root_dir = os.path.dirname(__file__)
    with open(os.path.join(root_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print("  -> Generated: sitemap.xml")

    # Generate robots.txt in root
    robots_txt = generate_robots()
    with open(os.path.join(root_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt)
    print("  -> Generated: robots.txt")

    print("Blog build complete with full SEO & sitemap!")

if __name__ == "__main__":
    main()
