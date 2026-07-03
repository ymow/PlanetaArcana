import { useEffect, useState } from 'react'
import axios from 'axios'
import { dailyDrawsApi } from '@/services/api'
import { useAuth } from '@/context/AuthContext'
import LoginButton from '@/components/LoginButton'
import type { DailyDraw } from '@/types'

export default function DailyDrawPage() {
  const { user } = useAuth()
  const [draw, setDraw] = useState<DailyDraw | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) {
      setDraw(null)
      return
    }

    const loadToday = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const today = await dailyDrawsApi.getToday()
        setDraw(today)
      } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 404) {
          setDraw(null)
        } else {
          setError('載入每日一牌失敗')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadToday()
  }, [user])

  const createToday = async () => {
    setIsGenerating(true)
    setError(null)
    try {
      const today = await dailyDrawsApi.createToday()
      setDraw(today)
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || '每日一牌生成失敗')
      } else {
        setError('每日一牌生成失敗')
      }
    } finally {
      setIsGenerating(false)
    }
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl text-center">
        <h1 className="mystical-font mb-4 text-4xl font-bold text-tarot-gold">
          每日一牌
        </h1>
        <div className="rounded-lg border border-tarot-accent/30 bg-tarot-primary/20 p-8 backdrop-blur-sm">
          <p className="mb-6 text-tarot-light">
            登入後每天保留一張專屬牌面,回來時可以延續今天的提醒與紀錄。
          </p>
          <div className="flex justify-center">
            <LoginButton />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mystical-font mb-8 text-center text-4xl font-bold text-tarot-gold">
        每日一牌
      </h1>

      {isLoading ? (
        <div className="py-16 text-center">
          <div className="mb-4 text-6xl animate-pulse">🔮</div>
          <h2 className="text-2xl text-tarot-gold">載入中...</h2>
        </div>
      ) : (
        <div className="rounded-lg border border-tarot-accent/30 bg-tarot-primary/20 p-8 backdrop-blur-sm">
          {draw ? (
            <div>
              <p className="mb-2 text-sm text-tarot-accent">
                {new Date(draw.draw_date).toLocaleDateString('zh-TW')}
              </p>
              <div className="mb-6 text-center">
                <div
                  className={`mb-3 text-7xl ${
                    draw.is_reversed ? 'rotate-180 transform' : ''
                  }`}
                >
                  🎴
                </div>
                <h2 className="mystical-font text-3xl font-bold text-tarot-gold">
                  {draw.card_name}
                </h2>
                <p className="text-sm text-tarot-accent">
                  {draw.card_name_en} · {draw.is_reversed ? '逆位' : '正位'}
                </p>
              </div>

              <div className="space-y-5">
                <section>
                  <h3 className="mb-2 text-lg font-bold text-tarot-accent">
                    今日主題
                  </h3>
                  <p className="text-2xl font-bold text-tarot-light">
                    {draw.interpretation.key_theme}
                  </p>
                </section>
                <section>
                  <h3 className="mb-2 text-lg font-bold text-tarot-accent">
                    牌面提醒
                  </h3>
                  <p className="leading-relaxed text-tarot-light">
                    {draw.interpretation.summary}
                  </p>
                </section>
                <section>
                  <h3 className="mb-2 text-lg font-bold text-tarot-accent">
                    今日建議
                  </h3>
                  <p className="text-tarot-light">
                    {draw.interpretation.advice}
                  </p>
                </section>
                <section>
                  <h3 className="mb-2 text-lg font-bold text-tarot-accent">
                    反思問題
                  </h3>
                  <p className="text-tarot-light">
                    {draw.interpretation.reflection_prompt}
                  </p>
                </section>
              </div>
            </div>
          ) : (
            <div className="text-center">
              <div className="mb-4 text-7xl">🎴</div>
              <h2 className="mystical-font mb-3 text-2xl font-bold text-tarot-gold">
                今天尚未抽牌
              </h2>
              <p className="mb-6 text-tarot-accent">
                每天只會產生一張牌,適合作為今天的提醒與回訪起點。
              </p>
              <button
                type="button"
                onClick={createToday}
                disabled={isGenerating}
                className="rounded-lg bg-gradient-to-r from-tarot-primary to-tarot-secondary px-8 py-3 text-white transition hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 mystical-font"
              >
                {isGenerating ? '生成中...' : '抽取今日牌'}
              </button>
            </div>
          )}

          {error && <p className="mt-6 text-center text-sm text-red-300">{error}</p>}
        </div>
      )}
    </div>
  )
}
