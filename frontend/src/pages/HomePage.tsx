import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-16">
        <h1 className="text-6xl font-bold text-tarot-gold mystical-font mb-4">
          歡迎來到神秘的塔羅世界
        </h1>
        <p className="text-xl text-tarot-accent mb-8">
          由 AI 驅動的偉特塔羅解讀系統
        </p>

        <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            to="/daily"
            className="inline-block rounded-lg bg-tarot-secondary px-8 py-4 text-lg text-white transition-all duration-300 hover:scale-105 hover:shadow-xl mystical-font"
          >
            每日一牌
          </Link>
          <Link
            to="/divine"
            className="inline-block px-8 py-4 bg-gradient-to-r from-tarot-primary to-tarot-secondary text-white text-lg rounded-lg hover:shadow-xl hover:scale-105 transition-all duration-300 mystical-font"
          >
            ✨ 開始你的塔羅之旅
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-8 mt-16">
        <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30">
          <div className="text-4xl mb-4">🎴</div>
          <h3 className="text-xl font-bold text-tarot-gold mb-2">
            傳統牌義
          </h3>
          <p className="text-tarot-light">
            基於經典偉特塔羅牌義，融合現代生活情境
          </p>
        </div>

        <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-xl font-bold text-tarot-gold mb-2">AI 解讀</h3>
          <p className="text-tarot-light">
            Claude AI 提供個人化、深入的塔羅解讀
          </p>
        </div>

        <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30">
          <div className="text-4xl mb-4">💬</div>
          <h3 className="text-xl font-bold text-tarot-gold mb-2">
            對話追問
          </h3>
          <p className="text-tarot-light">
            支援多輪對話，深入探討牌面意義
          </p>
        </div>
      </div>

      {/* How it works */}
      <div className="mt-16 bg-tarot-primary/10 backdrop-blur-sm p-8 rounded-lg border border-tarot-accent/20">
        <h2 className="text-3xl font-bold text-tarot-gold mb-6 mystical-font">
          如何使用
        </h2>

        <div className="space-y-4">
          <div className="flex items-start space-x-4">
            <span className="text-2xl text-tarot-accent">1️⃣</span>
            <div>
              <h4 className="text-lg font-bold text-tarot-light">
                輸入你的問題
              </h4>
              <p className="text-tarot-accent">
                清晰地描述你想詢問的事項
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <span className="text-2xl text-tarot-accent">2️⃣</span>
            <div>
              <h4 className="text-lg font-bold text-tarot-light">抽取塔羅牌</h4>
              <p className="text-tarot-accent">
                系統將為你抽取三張牌（過去-現在-未來）
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <span className="text-2xl text-tarot-accent">3️⃣</span>
            <div>
              <h4 className="text-lg font-bold text-tarot-light">
                獲取 AI 解讀
              </h4>
              <p className="text-tarot-accent">
                AI 將根據牌面與問題生成個人化解讀
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-4">
            <span className="text-2xl text-tarot-accent">4️⃣</span>
            <div>
              <h4 className="text-lg font-bold text-tarot-light">深入對話</h4>
              <p className="text-tarot-accent">
                可以針對解讀內容進一步提問
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-8 text-center text-sm text-tarot-accent">
        <p>
          ⚠️
          塔羅占卜僅供娛樂與自我反思，不應作為重大決策的唯一依據
        </p>
      </div>
    </div>
  )
}
