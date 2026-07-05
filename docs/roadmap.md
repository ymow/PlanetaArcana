# PlanetaArcana 產品 Roadmap

> 更新日期:2026-07-04
> 依據:Phase 1 MVP 完成後的產品規劃、競品調查驗證(見 [competitor-survey.md](./competitor-survey.md))、AIGC 卡牌視覺系統研究(見 [aigc-card-visual-system-research.md](./aigc-card-visual-system-research.md))、卡牌視覺底層知識架構(見 [card-visual-knowledge-architecture.md](./card-visual-knowledge-architecture.md))
> 執行版工作流:見 [development-workflow.md](./development-workflow.md)

## 產品方向

**留存優先 → 體驗深化 → 視覺系統 → 分享/PWA → 變現驗證。**

塔羅產品的天然優勢是儀式感與週期性(使用者會反覆回來問事)。競品調查證實:AI 解讀已是市場標配,差異化落在人格化角色、UX 降門檻與留存迴圈。新的 AIGC 卡牌方向補上第四個差異化層:每張牌可依語義 facet 與 style scaffold 產生多種有根據的視覺變體,但必須先有卡牌視覺原子與策展標準,不能直接做 78 張固定圖。

## 整體執行 Workflow

| 順序 | Phase | 交付焦點 | Release gate |
|---|---|---|---|
| 1 | Phase 1.5 還債與防禦 | 穩定核心 AI 流程、補成本保護、建立 API 測試基線 | 後端測試全綠;解讀/追問都有突發限流與每日配額;`.env.example` 完整 |
| 2 | Phase 2 留存基礎 | 帳號、歷史、每日一牌、免費配額,建立可追蹤留存迴圈 | OAuth 可用;新舊占卜能綁定使用者;Daily Draw 每日唯一;配額規則有測試 |
| 3 | Phase 3A 降低占卜門檻 | AI 自動選牌陣,讓使用者只要輸入問題即可開始 | 可不手選牌陣完成占卜;AI 失敗時有 deterministic fallback |
| 4 | Phase 3B/3C 體驗深化 | 追問串流(可選)、凱爾特十字決策、舊流程 polish | 核心解讀流程無回歸;桌機/手機通過手動 smoke test |
| 5 | Phase 4 AIGC 卡牌視覺系統 | 卡牌 slug、10 張 pilot 視覺原子、style scaffold、prompt composer、策展評分 | 10-card pilot 能產出結構化 prompt;至少一個 scaffold 通過策展 |
| 6 | Phase 5 分享/PWA 成長迴圈 | 翻牌/卡牌視覺、分享卡片、PWA 安裝與提醒 | 分享可追蹤且配額安全;PWA 提醒可 opt-in/退訂 |
| 7 | Phase 6 設計師/商業化 | style preview pack、Major Arcana prototype、權利/定價/上架流程 | 權利、原創性、預覽、印刷/數位 QA 全部過 gate |

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

## Phase 2 — 留存基礎(2–4 週)【Must】(已完成,分享成長迴圈可於 Phase 5 分享卡片再強化)

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

## Phase 3 — 體驗深化與降低門檻【Should】

- [x] **Streaming 解讀**:逐字流出取代 10–30 秒空白等待,本身就是儀式感
  - 初始解讀已串流:`POST /divines/{id}/interpret/stream`(SSE:delta → complete,失敗發 error);持久化只在完整驗證後發生,中斷即重試、不留半成品;前端漸進顯示 overall_summary
  - 待做:追問對話串流(等待較短,優先級低)
- [x] **人格化解讀角色**:同一解讀引擎、不同 system prompt 的占卜師角色
  - 競品驗證:最普遍的付費牆與情感連結點(Tarotap 6 角色其中 3 個鎖會員、MoriTarot 4 種星座人格);對現有 `prompts.py` 架構是低成本改造
  - 已上線 4 角色(星野老師/渡鴉/月見/奧術學者),registry 在 `prompts.py`,共用解讀規則與 JSON schema;提問時選角、存於 `Divine.persona_id`、追問自動沿用同角色;`GET /personas` 供前端渲染;每角色帶 `is_premium` flag 為付費牆預留(現全開放);每日一牌不套角色
- [x] **更多牌陣**(單張、二選一已上線;凱爾特十字待做):
  - 牌陣 registry 在 `prompts.py` `SPREADS`(有序 positions + 各牌陣解讀重點);`GET /spreads` 供前端渲染;建立占卜時驗證牌陣類型、張數與二選一選項
  - 單張指引(1 張,快問快答)、兩難抉擇(2 張,使用者描述選項 A/B,prompt 要求比較能量差異且不迴避結論)
  - 凱爾特十字(10 張)留待後續:成本高、需要專屬排版,適合搭配付費牆
- [x] **AI 自動選牌陣**:Tarotap 模式(使用者輸入問題 → 系統決定牌陣),移除選陣決策點;MVP 只在 `single`、`past_present_future`、`two_choice` 之間推薦
  - 已上線 deterministic recommender:`POST /spreads/recommend`,不消耗解讀配額;前端預設「讓 PlanetaArcana 選」,手動選牌陣保留;二選一題目會要求補選項 A/B
- [ ] **凱爾特十字決策**:先確認成本、排版、付費牆策略,不放入自動選陣 MVP

**Workflow**:

1. **Streaming contract**:先定義後端 streaming response 格式與前端狀態機,確保中斷、重試、完成後持久化都有明確行為。【done — SSE delta/complete/error;完整驗證後才持久化;有 API 測試覆蓋串流、配額、錯誤與權限】
2. **Persona registry**:在 `prompts.py` 建立角色設定表,角色只改 system prompt 與語氣,不複製解讀邏輯。【done — voice + 共用規則組合;初始解讀與追問都貫穿角色,有測試防「變聲」回歸】
3. **Spread expansion**:單張、二選一與 AI 自動選牌陣已完成;接下來只剩凱爾特十字決策與可能的追問串流。
4. **Release check**:使用者只輸入問題即可完成抽牌與 streaming 解讀;手動選牌陣仍可用。【done — backend tests + frontend build 通過】

**成功指標**:新使用者建立占卜時的表單中途放棄率下降;自動選陣後成功進入解讀的比例 > 90%。

## Phase 4 — AIGC 卡牌視覺系統【Should】

- [x] **底層牌義/市場知識層**:將牌義本體、既有牌組研究與語義轉譯規則封裝在 prompt composer 下方
  - 已落地 `meaning_axes.json`、`reference_decks.json`、`transformation_rules.json`;新增 `GET /api/card-visuals/knowledge`
  - 參考牌組只作為 lineage、market role、visual grammar、semantic lesson 研究來源;明確保留 `do_not_copy` 約束,不做活著藝術家風格模仿
- [x] **卡牌 slug**:為 78 張牌建立穩定 `slug`,如 `major_fool`、`wands_ace`,供資產路徑、prompt metadata、變體管理使用
  - 已補 `Card.slug` model/schema/API/frontend type;seed 會自動產生 78 個唯一 slug;SQLite `ensure_schema` 會 backfill 既有資料
- [x] **10-card pilot 視覺原子**:先做愚者、魔術師、女祭司、戀人、死神、高塔、星星、權杖王牌、聖杯二、寶劍十
  - 已落地 `backend/app/data/card_visual/facets.json`、`symbols.json`、`compositions.json`,每張 pilot 卡至少 3 facets、3 symbols、1 composition
- [x] **Style scaffold**:先定義 Canonical Echo、Archetype Abstract、Ritual Object、Emotional Weather
  - 已落地 `style_scaffolds.json`,包含 medium、palette、symbol treatment、composition bias、negative constraints
- [x] **Prompt composer**:輸入 card slug、route、orientation、可選 question context;輸出結構化 prompt JSON 與最終文字 prompt
  - 已上線 `POST /api/card-visuals/prompts`,輸出 subject/meaning/symbol/composition/style/negative constraints 與 final prompt;尚不生成圖片
- [x] **Generated variant metadata**:建立可追蹤的 AIGC 卡牌變體資料模型,先存 prompt metadata、狀態與策展分數,不接圖片生成
  - 已上線 `POST /api/card-visuals/variants`、`GET /api/card-visuals/variants`、`PATCH /api/card-visuals/variants/{id}`
- [x] **內部視覺實驗室**:讓開發/策展者可選卡牌、facet、style scaffold,產生 prompt、建立 variant draft、提交策展分數
  - 已上線前端 `/visual-lab` 與 `GET /api/card-visuals/catalog`
- [x] **策展評分契約**:每張變體固定評分 tarot recognizability、semantic accuracy、transform discipline、deck coherence、originality/safety
  - 已上線 `POST /api/card-visuals/variants/{id}/curation`;1-5 分驗證;自動建議 `approved`、`needs_revision` 或 `rejected`
  - 核准 gate 對齊研究文件:一般路線 recognizability >= 3、semantic accuracy >= 4、deck coherence >= 4、originality/safety >= 5;抽象路線需 title/border/symbol 支撐才可降低 recognizability
- [ ] **知識根層追蹤補強**:把 `card-visual-knowledge-architecture.md` 的下一步納入實作追蹤
  - prompt metadata 加入 `knowledge_context`
  - variant 附掛 selected meaning axes 與 transformation rules
  - prompt 組合驗證 gate 檢查 card identity、facet、anchor contract、composition relation、style scaffold 與 do-not-copy constraints
  - pilot card facets 從 knowledge root 推導,避免長期依賴手寫 free-form interpretation
- [ ] **Pilot 圖片批次與人工策展**:10 張 pilot x 4 scaffold x 2 variants,用 scorecard 實際篩出可用風格

**Workflow**:

1. 先建立底層知識層:meaning axes、reference deck studies、transformation rules。
2. 在 `backend/app/data/card_visual/` 用 JSON/YAML 建立資料,不要先做 DB migration。
3. 將閱讀牌義與圖像生成語義分離:解讀 prompt 追求準確解釋,圖像 prompt 追求符號錨點、構圖與風格約束。
4. 為 pilot 卡建立 facets、symbol atoms、composition atoms、style scaffolds。
5. 建立 prompt composer 與資料驗證測試。
6. 用 `/visual-lab` 產生 prompt draft 並提交五項策展分數。
7. 小批量生成:10 張 pilot x 4 scaffold x 2 variants,通過策展後再擴張。

**成功指標**:至少一個 style scaffold 在 10-card pilot 中通過策展 gate,且不破壞現有占卜流程。

## Phase 5 — 卡牌視覺、分享與 PWA 成長迴圈【Should】

- [ ] **翻牌動畫與卡牌視覺**:只使用已持久化抽牌結果;動畫不得改變卡牌、正逆位或解讀資料
- [ ] **分享卡片**:解讀結果生成美觀分享圖,免費成長引擎;可與「分享 +1 配額」掛勾
- [ ] **PWA 化 + 推播**:對標 App 的推播留存(每日一牌提醒、3 天後回訪提示)

**Workflow**:

1. Card visual UI 先吃 Phase 4 的 curated asset contract,缺圖時有 fallback。
2. 分享圖包含可追蹤 referral 參數;分享 +1 額度仍由 `POST /divines/{id}/share` 控制,避免重複領取。
3. PWA 先做 installability,再做每日一牌與三天後回訪提醒;所有提醒必須 opt-in 且可退訂。
4. Release 前做桌機與手機 smoke test,重點檢查抽牌、正逆位、streaming、分享卡片、PWA 安裝與舊解讀頁回歸。

**成功指標**:分享卡片帶來的新訪客佔比 > 15%;Daily Draw 提醒 opt-in 使用者 7 日回訪率 > 25%。

## Phase 6 — 設計師/商業化【Could】

- [ ] **Designer style submission**:記錄 authorship model、rights statement、AI disclosure、style scaffold、sample cards、commercial permissions
- [ ] **Style preview pack**:先做 10 張風格預覽包或 22 張 Major Arcana prototype,不要直接賣 78 張
- [ ] **商業 gate**:權利、原創性、預覽、定價、退款、印刷/數位 QA 都過關後才上架

**Workflow**:

1. 先把每個 style route 當成可能商品,不是單純 prompt。
2. 先通過 commercial curation baseline:tarot integrity、style coherence、range、product story、originality、rights readiness、print readiness、buyer preview。
3. 明確標示 human / human + AI / AI-generated curated,並保留來源與修改紀錄。

**成功指標**:第一個 sellable style pack 過權利與策展 gate,並有足夠預覽讓使用者購買前判斷風格。

## Could(有餘裕再做)

- 追問次數分級(免費 3 次追問,為付費留伏筆)
- 變現分層:freemium 訂閱(基礎 vs 深度 AI 解讀)+ 可選消耗性點數(Taroscope pentacles 式低門檻付費);台灣金流參考綠界 ECPay
- 英文版(市場放大,先把中文市場做透)
- 月度運勢回顧(用歷史占卜資料生成)
- 78 張完整 AIGC deck、多設計師 marketplace、實體印刷與履約

## Won't(明確不做,現階段)

- **原生 App** — PWA-first,不分散火力
- **多 AI 模型切換** — 使用者在乎解讀品質,不在乎引擎
- **社群功能**(留言、公開占卜)— 審核成本高,時機未到
- **真人占卜師媒合** — 競品數據:Keen/Kasamba 平台抽成 54–61% 看似誘人,但招募、審核、客訴的運營成本重,屬後期選項
- **生辰八字結合 AI** — 競品調查中該差異化主張被查證否決,不列入依據
- **一張牌一個固定 prompt** — 會讓 AIGC 視覺變成靜態百科,不符合多 facet、多 scaffold 的產品方向

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
