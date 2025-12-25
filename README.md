# 🏠 Lily's Blog

基于 VitePress 构建的个人技术博客，专注于 Java 开发和编程技术分享。

## ✨ 特性功能

- **🚀 现代技术栈**：基于 VitePress + Vue 3 + TypeScript 构建
- **🎨 精美主题**：使用 Tailwind CSS 定制的响应式设计
- **📝 自动路由**：新增 Markdown 文件自动生成路由，专注内容创作
- **🔍 全文搜索**：内置本地搜索功能，快速定位内容
- **📖 数学公式支持**：集成 MathJax 3，完美支持数学公式渲染
- **📱 响应式设计**：适配桌面端和移动端设备
- **🎯 多页面支持**：博客、项目展示、友链、关于我页面
- **🔥 Notes 新增文件自动刷新侧边栏**：在 `docs/src/Notes/` 下新增/删除 `.md` 会自动重启 dev server，侧边栏实时更新

## 🗂️ 项目结构

```
my-blog/
├── docs/                    # VitePress 文档目录
│   ├── .vitepress/         # 配置和主题文件
│   │   ├── components/     # 自定义 Vue 组件
│   │   ├── theme/         # 主题样式文件
│   │   ├── utils/         # 工具函数
│   │   └── config.mjs     # 配置文件
│   └── src/               # 文档源文件
│       ├── Notes/         # 博客文章目录
│       │   ├── a-dt/      # 项目开发笔记
│       │   ├── a-lucky/   # 项目架构相关
│       │   ├── b-ddd/     # DDD 相关技术
│       │   ├── b-leetcode/# 算法题解
│       │   ├── c-Nginx/   # Nginx 配置
│       │   └── z-Java/    # Java 技术深入
│       ├── public/        # 静态资源
│       ├── AboutMe.md     # 关于我页面
│       ├── Friends.md     # 友情链接
│       └── index.md       # 首页
├── package.json           # 项目依赖配置
├── tailwind.config.js    # Tailwind CSS 配置
└── tsconfig.json        # TypeScript 配置
```

## 🚀 快速开始

### 环境要求

- Node.js 16+（22.16可行）
- npm 或 yarn

### 安装依赖

```bash
npm install --loglevel=verbose
```

### 本地开发

```bash
npm run docs:dev
```

访问 http://localhost:5173 查看效果。

> 说明：本项目的侧边栏是启动时通过 `docs/.vitepress/utils/getSidebar.ts` 扫描 `docs/src/Notes/` 生成的。
> 因此 **新增/删除** md 文件需要让配置重新执行一次；`docs:dev` 已经内置 watcher，会在检测到 `Notes` 目录结构变化时自动重启 VitePress。新增文件夹不会更新，但在新增文件夹下新增 .md 文件会触发更新，直接新增文件夹，不在 translations.ts 指定别名时，目录名称就是新增文件夹的名称。

如果你想使用原始 VitePress dev（不带 watcher）：

```bash
npm run docs:dev:raw
```

### 构建部署

```bash
# 构建静态文件
npm run docs:build

# 预览构建结果
npm run docs:preview

# 部署到服务器
npm run docs:deploy
```

## 🚀 服务器：只 scp 到 Notes 即自动构建发布（适合“只想传文件”的流程）

> 结论：Nginx 只负责服务 `dist` 静态文件，它不会直接把 `Notes/*.md` 当网页。
> 想要“scp 到 Notes 就自动更新网站”，需要在服务器上常驻一个 watcher：监听文件变化 -> 自动 `npm run docs:build` -> 发布 `dist` 到 Nginx 目录。

### 1) 服务器准备（一次性）

- Node/npm：能在仓库根目录执行 `npm run docs:build`
- Python 版依赖：`pip install watchdog`

### 2) 前台试跑 watcher（推荐先这样验证）

在服务器仓库根目录执行：

- **Python 版**（不用 inotifywait，但需要 watchdog）：

```bash
pip install watchdog
python3 scripts/server-watch-build.py
```

之后你只要把文件上传到服务器的 `docs/src/Notes/`（例如用 `scp`/`sftp`），它就会自动触发：

- `npm run docs:build`
- 把 `docs/.vitepress/dist` 原子发布到 `OUTPUT_DIR`（默认：`/root/nginx/volumes/html/blog/dist`）

## 📚 内容管理

### 添加新文章

在 `docs/src/Notes/` 目录下创建新的 Markdown 文件，系统会自动生成对应路由。

### 文章分类

所有文章按分类组织在 `Notes/` 目录下：
- **a-***: 项目开发和实践
- **b-***: 技术理论和算法
- **c-***: 工具和配置
- **z-***: Java 技术深入

### 自定义组件

项目内置了多个实用组件：
- `LinkCard`: 链接卡片展示
- `HText`: 标题文本组件
- 自定义页脚和更新时间显示

## 🛠️ 技术栈

- **框架**: VitePress 1.0.0
- **前端**: Vue 3, TypeScript
- **样式**: Tailwind CSS 3.3.3
- **构建工具**: Vite
- **数学渲染**: MathJax 3
- **日期处理**: Day.js
- **Markdown解析**: gray-matter

## 🌐 相关链接

- [GitHub 主页](https://github.com/cnzhangxy51)
- [项目示例页面](https://example.zbwer.work/)

## 📄 许可证

MIT License

---

**欢迎交流探讨各种技术问题！** ✨