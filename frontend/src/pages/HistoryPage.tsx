import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { divinesApi } from '@/services/api'
import type { Divine } from '@/types'

export default function HistoryPage() {
  const [divines, setDivines] = useState<Divine[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setIsLoading(true)
    try {
      const data = await divinesApi.getAll({ limit: 20 })
      setDivines(data)
    } catch (error) {
      console.error('載入歷史記錄失敗:', error)
      alert('載入歷史記錄失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('確定要刪除這筆占卜記錄嗎？')) return

    try {
      await divinesApi.delete(id)
      setDivines(divines.filter((d) => d.id !== id))
    } catch (error) {
      console.error('刪除失敗:', error)
      alert('刪除失敗')
    }
  }

  if (isLoading) {
    return (
      <div className="text-center py-16">
        <div className="text-6xl mb-4 animate-pulse">🔮</div>
        <h2 className="text-2xl text-tarot-gold">載入中...</h2>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-tarot-gold mystical-font text-center mb-8">
        占卜歷史
      </h1>

      {divines.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-6xl mb-4">📜</div>
          <p className="text-xl text-tarot-accent mb-4">尚無占卜記錄</p>
          <Link
            to="/divine"
            className="inline-block px-6 py-3 bg-tarot-secondary text-white rounded-lg hover:bg-tarot-primary transition"
          >
            開始第一次占卜
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {divines.map((divine) => (
            <div
              key={divine.id}
              className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 hover:border-tarot-accent/60 transition"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-tarot-light mb-2">
                    {divine.question_text}
                  </h3>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {divine.spread_data.cards.map((card, idx) => (
                      <span
                        key={idx}
                        className="text-xs px-2 py-1 bg-tarot-dark/50 rounded-full text-tarot-accent"
                      >
                        {card.card_name}{' '}
                        {card.is_reversed ? '(逆)' : '(正)'}
                      </span>
                    ))}
                  </div>
                  <p className="text-sm text-tarot-accent">
                    {new Date(divine.created_at).toLocaleString('zh-TW')}
                  </p>
                </div>

                <div className="flex space-x-2">
                  <Link
                    to={`/divine/${divine.id}`}
                    className="px-4 py-2 bg-tarot-secondary text-white rounded hover:bg-tarot-primary transition text-sm"
                  >
                    {divine.is_ai_interpreted ? '查看' : '解讀'}
                  </Link>
                  <button
                    onClick={() => handleDelete(divine.id)}
                    className="px-4 py-2 bg-red-500/50 text-white rounded hover:bg-red-600 transition text-sm"
                  >
                    刪除
                  </button>
                </div>
              </div>

              {divine.is_ai_interpreted && (
                <div className="mt-3 pt-3 border-t border-tarot-accent/20">
                  <span className="inline-flex items-center text-xs text-green-400">
                    <span className="mr-1">✓</span>
                    已完成 AI 解讀
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
