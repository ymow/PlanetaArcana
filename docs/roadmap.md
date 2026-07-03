# PlanetaArcana 產品 Roadmap

> 更新日期:2026-07-03
> 依據:Phase 1 MVP 完成後的產品規劃,並經競品調查驗證(見 [competitor-survey.md](./competitor-survey.md))

## 產品方向

**留存優先 → 體驗深化 → 變現驗證。**

塔羅產品的天然優勢是儀式感與週期性(使用者會反覆回來問事),但目前沒有帳號系統、無從累積留存。競品調查證實:AI 解讀已是市場標配,差異化落在人格化角色、UX 降門檻與留存迴圈——這三者正是本 roadmap 的主軸。

## 三階段執行 Workflow

| 順序 | Phase | 交付焦點 | Release gate |
|---|---|---|---|
| 1 | Phase 1.5 還債與防禦 | 穩定核心 AI 流程、補成本保護、建立 API 測試基線 | 後端測試全綠;解讀/追問都有突發限流與每日配額;`.env.example` 完整 |
| 2 | Phase 2 留存基礎 | 帳號、歷史、每日一牌、免費配額,建立可追蹤留存迴圈 | OAuth 可用;新舊占卜能綁定使用者;Daily Draw 每日唯一;配額規則有測試 |
| 3 | Phase 3 體驗深化 | Streaming、角色、牌陣、分享、PWA,降低等待感並提升回訪與分享 | 核心解讀流程無回歸;分享與推播可量測;前端互動在桌機/手機通過手動驗收 |

每個功能固定走同一個小循環:

1. **Scope**:先寫清楚使用情境、資料歸屬、成本風險與成功事件。
2. **Backend**:model/schema/API/service 一起落地;牽涉資料表時補 migration 或初始化路徑。
3. **Frontend**:先完成可用流程,再補視覺細節;避免先做一次性展示頁。
4. **Tests**:後端至少覆蓋成功、失敗、權限/配額邊界;前端至少做手動 smoke test。
5. **Measure**:每個 release 至少能回答使用量、成功率、錯誤率與成本是否可控。

## Phase 1.5 — 還債與防禦(1 週內)【Must】

- [x] 修復核心 bug(import 錯誤、退役模型遷移、JSON 持久化、追問脈絡、重複解讀 500、SDK 升級)— PR #1
- [x] **Rate limiting + 每日解讀次數上限** — 兩層保護:每分鐘突發限制(in-memory)+ 每日配額(資料庫,`AI_DAILY_LIMIT` 預設 20 次/IP/日),套用於解讀與追問端點
- [x] 核心流程 API 測試(解讀、追問)— 13 個測試:CRUD、解讀流程、重複解讀 upsert、追問持久化與脈絡完整性、配額與突發限流

**Workflow**:

1. 先鎖住現有核心路徑:建立占卜 → AI 解讀 → 追問 → 查詢歷史。
2. 補成本防線:突發限流先擋濫用,每日配額再控 token 成本上限。
3. 把所有修復寫成回歸測試,避免 Phase 2 帳號與配額改造時破壞核心流程。
4. Release 前檢查:後端 `pytest` 全綠,`.env.example` 有所有必要設定,錯誤訊息對前端可處理。

**成功指標**:解讀成功率 > 99%;單日 token 成本有上限保護。

## Phase 2 — 留存基礎(2–4 週)【Must】(已完成,分享成長迴圈可於 Phase 3 分享卡片再強化)

- [x] **使用者帳號**:輕量 Google OAuth(model 已預留 `user_id`)— 後端支援 Google ID token 驗證 + app session token;本機 debug 可用 dev login
- [x] **每日一牌(Daily Draw)**:每天一張牌 + 簡短 AI 解讀。單卡 prompt 成本低、打開率高、養成習慣
  - 競品驗證:每日一牌 + 回訪提示是中文市場留存標配(MoriTarot 每日暖心牌 + 3 天後回訪、Astroverse 每日配額)
- [x] **占卜歷史綁定帳號** + 回顧視圖(「三個月前你問過這件事,牌面說…」)— 登入使用者只能看到自己的歷史;匿名占卜可登入後 claim
- [x] **免費配額機制**:免費每日 N 次,分享 +1(Astroverse 驗證過的模式);同時兼作成本控制
  - AI 配額由「登入使用者優先、匿名 IP fallback」計量;解讀、追問、每日一牌共用成本保護
  - 分享 +1:`POST /divines/{id}/share` 領取當日 +1 額度;同一 quota key 對同一占卜只能領一次(DB unique constraint 稽核),每日加額上限 `AI_SHARE_BONUS_DAILY_MAX`(預設 3);`GET /quota` 回報今日額度狀態

**Workflow**:

1. **Auth foundation**:新增 `User` model、Google OAuth callback/session 或 token 驗證,保留匿名使用路徑但讓新資料能帶 `user_id`。【done】
2. **History binding**:占卜列表與單筆詳情依使用者篩選;提供登入後綁定既有匿名占卜的過渡策略。【done】
3. **Daily Draw**:新增每日一牌資料模型與 API,同一使用者同一日期只能產生一次;AI prompt 使用低成本單卡版本。【done】
4. **Quota v2**:把現有 IP 配額升級為「登入使用者優先、匿名 IP fallback」;分享 +1 只增加當日額度且要可稽核。【done】
5. **Retention view**:前端新增歷史/回顧入口,讓 Daily Draw 與過往占卜可形成回訪理由。【done】
6. **Release check**:OAuth、匿名 fallback、每日唯一、配額耗用、分享加額與歷史查詢都要有 API 測試。【done】

**成功指標**:註冊使用者 7 日回訪率 > 25%。

## Phase 3 — 體驗深化(4–8 週)【Should】

- [x] **Streaming 解讀**:逐字流出取代 10–30 秒空白等待,本身就是儀式感
  - 初始解讀已串流:`POST /divines/{id}/interpret/stream`(SSE:delta → complete,失敗發 error);持久化只在完整驗證後發生,中斷即重試、不留半成品;前端漸進顯示 overall_summary
  - 待做:追問對話串流(等待較短,優先級低)
- [x] **人格化解讀角色**:同一解讀引擎、不同 system prompt 的占卜師角色
  - 競品驗證:最普遍的付費牆與情感連結點(Tarotap 6 角色其中 3 個鎖會員、MoriTarot 4 種星座人格);對現有 `prompts.py` 架構是低成本改造
  - 已上線 4 角色(星野老師/渡鴉/月見/奧術學者),registry 在 `prompts.py`,共用解讀規則與 JSON schema;提問時選角、存於 `Divine.persona_id`、追問自動沿用同角色;`GET /personas` 供前端渲染;每角色帶 `is_premium` flag 為付費牆預留(現全開放);每日一牌不套角色
- [ ] **更多牌陣**:單張(快問)、兩難抉擇(二選一)、凱爾特十字(進階)
  - 搭配 **AI 自動選牌陣**(Tarotap 模式:使用者輸入問題,AI 決定牌陣),移除選陣決策點
- [ ] **翻牌動畫與卡牌視覺**
- [ ] **分享卡片**:解讀結果生成美觀分享圖,免費成長引擎;可與「分享 +1 配額」掛勾
- [ ] **PWA 化 + 推播**:對標 App 的推播留存(每日一牌提醒、3 天後回訪提示)

**Workflow**:

1. **Streaming contract**:先定義後端 streaming response 格式與前端狀態機,確保中斷、重試、完成後持久化都有明確行為。【done — SSE delta/complete/error;完整驗證後才持久化;有 API 測試覆蓋串流、配額、錯誤與權限】
2. **Persona registry**:在 `prompts.py` 建立角色設定表,角色只改 system prompt 與語氣,不複製解讀邏輯。【done — voice + 共用規則組合;初始解讀與追問都貫穿角色,有測試防「變聲」回歸】
3. **Spread expansion**:先做單張與二選一,再做十字牌陣;AI 自動選牌陣要能回傳理由與 fallback。
4. **Visual layer**:翻牌動畫與卡牌視覺只依賴已持久化的抽牌結果,避免動畫狀態影響占卜資料。
5. **Share loop**:分享圖生成要包含可追蹤 referral 參數;確認分享 +1 配額不會被重複領取。
6. **PWA/push**:先做安裝體驗與每日一牌提醒,再做「3 天後回訪」等情境推播;所有推播需可退訂。
7. **Release check**:桌機與手機手動 smoke test,重點檢查 streaming 空白等待、分享卡片、PWA 安裝與舊解讀頁回歸。

**成功指標**:分享卡片帶來的新訪客佔比 > 15%。

## Could(有餘裕再做)

- 追問次數分級(免費 3 次追問,為付費留伏筆)
- 變現分層:freemium 訂閱(基礎 vs 深度 AI 解讀)+ 可選消耗性點數(Taroscope pentacles 式低門檻付費);台灣金流參考綠界 ECPay
- 英文版(市場放大,先把中文市場做透)
- 月度運勢回顧(用歷史占卜資料生成)

## Won't(明確不做,現階段)

- **原生 App** — PWA-first,不分散火力
- **多 AI 模型切換** — 使用者在乎解讀品質,不在乎引擎
- **社群功能**(留言、公開占卜)— 審核成本高,時機未到
- **真人占卜師媒合** — 競品數據:Keen/Kasamba 平台抽成 54–61% 看似誘人,但招募、審核、客訴的運營成本重,屬後期選項
- **生辰八字結合 AI** — 競品調查中該差異化主張被查證否決,不列入依據

## 定價參考(競品快照,2026-07)

| 產品 | 模式 | 價格 |
|---|---|---|
| Tarotap | 純訂閱 | Plus NT$358/月、Pro NT$2,750/月 |
| Astroverse | 訂閱 + 生態系 | Pro 有 NT$588 終身方案 |
| Taroscope | 廣告 + 訂閱 + 點數 + 捐款 | 年費制 + pentacles 點數 |
| MoriTarot | 完全免費 | B2B API 授權變現 |

## 未解問題(待後續調查)

- 主流塔羅 App(Labyrinthos、Golden Thread)的留存/訂閱設計細節
- 中文市場各種變現模式的實際轉換率(無公開數據)
- 競品 AI 實作深度(模型、prompt 策略、記憶)
