# Travel Planner

一个智能旅行规划应用，使用AI生成个性化行程，并集成Unsplash图片和地图功能。

## 功能特性

- 🧠 AI驱动的行程规划（基于Google Gemini）
- 📸 自动获取景点图片（Unsplash API）
- 🗺️ 集成Google Maps查看位置
- 🌤️ 天气和交通提示
- 📱 响应式前端界面
- 🐳 Docker容器化部署

## 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.11+ (可选，用于本地开发)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd travel-planner
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   ```
   编辑 `.env` 文件，填入您的API密钥：
   - `UNSPLASH_API_KEY`: 从 [Unsplash Developers](https://unsplash.com/developers) 获取
   - `GEMINI_API_KEY`: 从 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取

3. **启动服务**
   ```bash
   docker-compose up --build
   ```

4. **访问应用**
   打开浏览器访问 `http://localhost`

### 本地开发

如果想本地开发后端：

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

前端直接在浏览器中打开 `frontend/index.html`。

## API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看FastAPI自动生成的API文档。

## 项目结构

```
travel-planner/
├── backend/          # FastAPI后端
│   ├── main.py       # 主应用
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # 前端静态文件
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── Dockerfile
├── docker-compose.yml
├── .env.example      # 环境变量模板
└── .gitignore
```
