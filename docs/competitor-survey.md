# 塔羅占卜產品競品調查報告

> 調查日期:2026-07-03(所有功能與定價為當日快照,此品類迭代快,引用前應複查)
> 方法:深度研究流程 — 5 個搜尋角度 → 20 個來源 → 99 條聲明 → 25 條進行 3 票對抗式查證 → 22 條確認、3 條否決
> 範圍:全球英文市場 + 中文(台灣/華語)市場,以網站為主,對照 App 功能

## 核心結論

**AI 解讀已經是市場標配,不構成差異化。** 台灣/中文市場四個主要競品全部是 AI-first,英文市場也有成形的 AI 塔羅利基。真正的差異化落在三個地方:

1. **解讀角色人格化**(最普遍的付費牆)
2. **UX 降門檻**(自動選牌陣、免註冊、30 秒占卜)
3. **留存迴圈設計**(每日一牌 + 配額 + 回訪提示)

## 市場結構:三種類型

| 類型 | 代表產品 | 模式 |
|---|---|---|
| 純 AI 塔羅工具 | Tarotoo、Tarotap、TarotReader.ai、Taroscope、MoriTarot | 免費 / freemium / 訂閱 |
| 真人占卜師媒合平台 | Keen、Kasamba | 按分鐘計費,平台抽成 54–61% |
| 命理生態系 | Astroverse | 塔羅為入口,靠預約/電商/儀式服務變現 |

英文市場排名參考(RankMyAI,2026-05,以流量/評論加權、非品質評比):#1 Astroline(占星平台,塔羅為附屬)、#2 Tarotoo(免費)、#3 Tarotap。注意聚合站的 free/freemium/paid 標籤不精確(如 TarotReader.ai 實為首問免費 + 點數追問)。

## 中文市場競品功能比較(一手驗證)

| | Tarotap | Taroscope 望遠鏡 | Astroverse | MoriTarot 莫利 |
|---|---|---|---|---|
| **牌陣** | AI 自動選陣(3張時間線/7張完整/感情專用)+ 凱爾特十字、二三選一、是非、每日/月運/年運、神諭卡等 | 預設 3 張,可選牌陣 | 6 種:單牌、三牌(過去現在未來)、關係 7 張、決策 5 張、年運 12 張、凱爾特十字 10 張 | 單張、時間之流、六芒星、愛情十字、四元素 |
| **AI 角色** | 6 位占卜師,其中 3 位(星月阿嬤、奇靈、戀語)會員限定 | 解讀模式分層(roast / advance / insight) | AI 靈性顧問「靈曦」+ 跨工具記憶(Pro) | 4 種星座人格:雙魚溫柔/獅子犀利/雙子幽默/射手熱情(同一角色「小莫」的風格切換) |
| **UX 亮點** | 300 字自由提問,AI 決定牌陣(移除選陣決策點) | 付費加購深度解讀(advance 在點數 0 時鎖定) | 配額閘門全平台共用 | 30 秒快速占卜、完全免註冊 |
| **歷史記錄** | 有 | 伺服器端保存 + 收藏篩選 | 免費會員即含紀錄保存 | 占卜結果追蹤 |
| **留存機制** | 每日/月運內容 | 點數消耗迴圈 | 每日配額:訪客 1 次/裝置、免費會員每日 2 次、分享 +1 | 每日一卡(今日暖心牌)+ 3 天後回訪提示 + 社會證明計數 |
| **變現** | 純訂閱:Plus NT$358/月、Pro NT$2,750/月(無廣告/單次付費/真人媒合) | 四管齊下:AdSense 廣告 + 年費訂閱 + pentacles 星幣點數 + 捐款(金流全走綠界 ECPay) | 訂閱(Pro,有 NT$588 終身方案旁證)+ 真人命理師預約 + 代辦疏文 + 水晶/貔貅電商 | 完全免費;LINE 官方帳號導流 + B2B API 授權 |

### 各競品定位一句話

- **Tarotap**:「AI 人格角色 + 訂閱制 freemium」的標準型,UX 門檻最低
- **Taroscope**:混合變現最完整的實驗場(廣告+訂閱+點數+捐款同時跑)
- **Astroverse**:塔羅只是命理生態系的獲客入口
- **MoriTarot**:零門檻獲客 + 留存迴圈教科書,變現走 B2B

## 真人媒合平台經濟結構(英文市場)

| | Keen | Kasamba |
|---|---|---|
| 計費 | 按分鐘,占卜師自訂費率($1.99–12.50/分) | 按分鐘 |
| 平台抽成 | 54%(占卜師留 46%) | 61%(且連線費先扣:聊天 $0.39/分、語音 $0.59/分,實得低於名目 39%) |
| 附加費 | 每分鐘 $0.40 平台費(雙方各付 $0.20) | — |
| 訂閱 | 無,純 pay-per-minute | 無 |

來源為兩家平台官方文件(Keen Advisor Help Center、Kasamba Advisor Terms 2024-06-03 版),費率條款明示可隨時變更。

## 對 PlanetaArcana 的啟示

1. **每日一牌是留存標配** — 最完整的留存迴圈(MoriTarot)= 每日一卡 + 3 天後回訪提示 + 社會證明。PWA 推播可補上「回訪提示」環節,直接對標 App。
2. **人格化解讀角色是最普遍的付費牆** — 對我們是低成本高回報:同一解讀引擎換 system prompt 即可,與現有 `prompts.py` 架構相容。
3. **AI 自動選牌陣值得借鑑** — Tarotap 移除牌陣選擇決策點(輸入問題 → AI 決定牌陣),上手門檻最低。
4. **變現參考組合** — freemium 配額(免費每日 N 次 + 分享 +1)+ 訂閱解鎖深度解讀,可疊加消耗性點數(Taroscope pentacles 式)作低門檻付費。台灣金流:兩家在地競品都走綠界 ECPay。
5. **被查證否決的方向** — 「AI 結合生辰八字為中文市場差異化」經查證被推翻(0-3 票),不應作為 roadmap 依據。

## 注意事項與證據缺口

- 部分證據來自前端 bundle 反編譯(Taroscope、Astroverse):代碼存在的功能不代表已上線或有使用量
- MoriTarot 的「今日已有 1,200 人占卜」為硬編碼社會證明,非真實數據;其 LINE bot 內是否有付費未驗證
- **未覆蓋**:主流塔羅 App(Labyrinthos、Golden Thread 等)的每日一牌/推播/訂閱細節無一手驗證;英文純 AI 工具(Tarotoo、TarotReader.ai)的功能基線聲明在查證中被否決,需逐一一手查證
- 各競品 AI 技術實作(底層模型、prompt 策略、是否納入正逆位/牌位/使用者上下文)大多未知,僅 Astroverse 靈曦記憶有代碼證據
- 無任何競品的營收/轉換率數據可查,「何種變現模式轉換更高」屬未解問題

## 主要來源

一手(primary)來源:

- https://tarotap.com/tarot-reading 、https://tarotap.com/pricing
- https://www.taroscope.ai/ (含生產 JS bundle)
- https://astroverse.com.tw/tarot (含生產 JS bundle)
- https://moritarot.com/ 、https://moritarot.com/partnership
- https://www.rankmyai.com/rankings/top-ai-tarot-reading-tools
- https://help.keen.com/hc/en-us/articles/360049891413-Earnings-Calculation
- https://www.kasamba.com/pages/advisor-terms-and-conditions
- https://sensortower.com/blog/astrology-apps-2019-revenue-downloads

其餘為部落格/論壇類佐證來源,詳見調查原始輸出。
