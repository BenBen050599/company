# Company — 团队协作平台

5人团队的文件共享 + AI 分析平台。

## 功能

- ✅ 用户管理（5人登录）
- ✅ 文件上传/下载/共享
- ✅ 标签/分类
- ✅ 讨论/评论
- ✅ API 接口（QClaw 集成）
- ✅ 分析结果展示

## 技术栈

- **后端**：Python FastAPI
- **数据库**：SQLite
- **前端**：React
- **部署**：Docker

## 项目结构

```
company/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── api/
│   │       ├── users.py
│   │       ├── files.py
│   │       └── comments.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # React 前端
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 快速开始

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm start
```

## API 文档

启动后访问：http://localhost:8000/docs
