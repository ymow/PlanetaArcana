# Planeta Arcana - AI 塔羅解讀系統

基於 Claude AI 的偉特塔羅占卜與解讀系統。

## 技術棧

### Backend
- **FastAPI** - Python Web Framework
- **SQLAlchemy** + **PostgreSQL** - ORM & Database
- **Anthropic Claude API** - AI 解讀引擎
- **Pydantic** - 資料驗證

### Frontend
- **React 18** + **TypeScript** + **Vite**
- **Base-UI** - 無樣式 UI 組件
- **Tailwind CSS** - 樣式框架
- **React Router** - 路由管理

## 專案結構

```
PlanetaArcana/
├── backend/              # FastAPI 後端
│   ├── app/
│   │   ├── main.py      # FastAPI 應用進入點
│   │   ├── models/      # SQLAlchemy Models
│   │   ├── schemas/     # Pydantic Schemas
│   │   ├── api/         # API Routes
│   │   ├── services/    # Business Logic
│   │   │   └── ai/      # AI Service Layer
│   │   ├── core/        # 核心設定
│   │   └── db/          # 資料庫設定
│   ├── requirements.txt
│   └── .env.example
├── frontend/            # React 前端
│   ├── src/
│   │   ├── components/  # React Components
│   │   ├── pages/       # 頁面
│   │   ├── services/    # API Client
│   │   ├── types/       # TypeScript Types
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 快速開始

### 1. 環境需求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 2. Backend 設定

```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env，填入：
# - DATABASE_URL
# - ANTHROPIC_API_KEY

# 初始化資料庫
python -m app.db.init_db

# 啟動伺服器
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend 設定

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
```

## API 文件

啟動 Backend 後，訪問：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 核心功能

### Phase 1 (MVP)

- ✅ 78 張偉特塔羅牌資料庫
- ✅ 三牌陣（過去-現在-未來）
- ✅ AI 解讀生成
- ✅ 多輪對話追問
- ✅ 占卜記錄 CRUD
- ✅ 對話歷史管理

### API Endpoints

#### Cards (塔羅牌)
- `GET /api/cards` - 取得所有卡片
- `GET /api/cards/{id}` - 取得特定卡片
- `POST /api/cards` - 新增卡片（管理）
- `PUT /api/cards/{id}` - 更新卡片（管理）
- `DELETE /api/cards/{id}` - 刪除卡片（管理）

#### Divines (占卜)
- `GET /api/divines` - 取得占卜列表
- `GET /api/divines/{id}` - 取得特定占卜
- `POST /api/divines` - 建立新占卜
- `POST /api/divines/{id}/interpret` - 生成 AI 解讀
- `PUT /api/divines/{id}` - 更新占卜
- `DELETE /api/divines/{id}` - 刪除占卜

#### Conversations (對話)
- `GET /api/conversations/{id}` - 取得對話歷史
- `POST /api/conversations/{id}/message` - 發送追問訊息
- `DELETE /api/conversations/{id}` - 刪除對話

## AI 解讀系統

### 工作流程

```
使用者提問 → 抽牌 → 建立占卜記錄 → 調用 AI 解讀 → 生成解讀 → 支援追問
```

### Prompt 架構

- **System Prompt**: 定義 AI 為專業塔羅解讀師
- **User Prompt**: 包含問題、牌陣、卡片資訊
- **輸出格式**: 結構化 JSON（整體解讀 + 單卡解讀 + 建議）

### 成本估算

- 單次解讀: ~1,900 tokens (~$0.018)
- 1,000 次/月: ~$18
- 10,000 次/月: ~$180

## 開發

### 執行測試

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### 程式碼格式化

```bash
# Backend
black app/
isort app/

# Frontend
npm run lint
npm run format
```

## 環境變數

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/planeta_arcana

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# App Settings
DEBUG=true
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 授權

MIT License

## 作者

Ymow
