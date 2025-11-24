# Planeta Arcana - 部署指南

## 開發環境設置

### 1. Backend 設置

```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env，填入你的設定：
# - ANTHROPIC_API_KEY=sk-ant-... (必填)
# - DATABASE_URL (選填，預設使用 SQLite)

# 初始化資料庫（建立表格並載入塔羅牌資料）
python -m app.db.init_db

# 啟動開發伺服器
uvicorn app.main:app --reload --port 8000
```

API 將運行在 http://localhost:8000
- Swagger 文件: http://localhost:8000/docs
- ReDoc 文件: http://localhost:8000/redoc

### 2. Frontend 設置

```bash
cd frontend

# 安裝依賴
npm install

# 設定環境變數
cp .env.example .env
# 預設值已足夠開發使用

# 啟動開發伺服器
npm run dev
```

前端將運行在 http://localhost:5173

## 取得 Anthropic API Key

1. 前往 https://console.anthropic.com/
2. 註冊或登入帳號
3. 在 API Keys 頁面建立新的 API Key
4. 複製 API Key 並貼到 `backend/.env` 的 `ANTHROPIC_API_KEY`

## 資料庫選項

### SQLite (預設，適合開發)

```env
DATABASE_URL=sqlite:///./planeta_arcana.db
```

### PostgreSQL (建議用於生產)

```bash
# 安裝 PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql

# 建立資料庫
createdb planeta_arcana

# 設定 .env
DATABASE_URL=postgresql://username:password@localhost:5432/planeta_arcana
```

## 生產環境部署

### Backend 部署選項

#### 1. 使用 Docker (推薦)

建立 `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

建立 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/planeta_arcana
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=planeta_arcana
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

啟動：
```bash
docker-compose up -d
```

#### 2. Railway / Render / Fly.io

這些平台都支援 FastAPI 應用，只需：
1. 連接 GitHub 倉庫
2. 設定環境變數
3. 部署

### Frontend 部署選項

#### 1. Vercel (推薦)

```bash
cd frontend
npm install -g vercel
vercel
```

環境變數設定：
- `VITE_API_BASE_URL`: 你的 Backend API URL

#### 2. Netlify

在 `frontend` 目錄建立 `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 3. 靜態托管 (Nginx)

```bash
cd frontend
npm run build

# 將 dist/ 目錄的內容上傳到伺服器
```

Nginx 設定範例：

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /var/www/planeta-arcana;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 環境變數檢查清單

### Backend (.env)

- [x] `ANTHROPIC_API_KEY` - **必填**
- [ ] `DATABASE_URL` - 選填（預設 SQLite）
- [ ] `SECRET_KEY` - 生產環境必填
- [ ] `DEBUG` - 生產環境設為 False
- [ ] `CORS_ORIGINS` - 設定允許的前端網域

### Frontend (.env)

- [x] `VITE_API_BASE_URL` - API 端點 URL

## 初始化資料

首次部署後，執行：

```bash
cd backend
python -m app.db.init_db
```

這會建立 78 張塔羅牌的資料。

## 監控與日誌

### Backend 日誌

使用 uvicorn 的日誌輸出，或整合 Sentry:

```bash
pip install sentry-sdk[fastapi]
```

在 `app/main.py` 加入：

```python
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
```

### 效能監控

考慮使用：
- New Relic
- Datadog
- Prometheus + Grafana

## 成本估算

### Anthropic API (Claude Sonnet 4)

- Input: $3 / 1M tokens
- Output: $15 / 1M tokens
- 單次解讀: ~$0.018
- 1,000 次/月: ~$18
- 10,000 次/月: ~$180

### 托管成本

- **Backend**: Railway/Render 免費層或 $5-10/月
- **Database**: Railway 免費層或 Supabase 免費層
- **Frontend**: Vercel/Netlify 免費層

**總計**: 每月 $20-50 (包含 1,000 次 AI 解讀)

## 安全性建議

1. **API Key 保護**: 永遠不要將 API Key 提交到 Git
2. **CORS 設定**: 限制允許的來源網域
3. **Rate Limiting**: 實作 API 請求速率限制
4. **HTTPS**: 生產環境必須使用 HTTPS
5. **環境變數**: 使用平台提供的環境變數管理

## 故障排除

### Backend 無法啟動

```bash
# 檢查 Python 版本
python --version  # 需要 3.11+

# 重新安裝依賴
pip install --upgrade -r requirements.txt

# 檢查環境變數
echo $ANTHROPIC_API_KEY
```

### Frontend 無法連接 API

1. 檢查 `VITE_API_BASE_URL` 設定
2. 確認 CORS 設定正確
3. 檢查 Backend 是否運行

### 資料庫錯誤

```bash
# 重新初始化資料庫
rm planeta_arcana.db  # SQLite only
python -m app.db.init_db
```

## 支援

如有問題，請查看：
- [GitHub Issues](https://github.com/your-repo/issues)
- [API 文件](http://localhost:8000/docs)
