import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { divinesApi, conversationsApi } from '@/services/api'
import type { Divine, InterpretationResponse, Message } from '@/types'

export default function InterpretationPage() {
  const { id } = useParams<{ id: string }>()
  const [divine, setDivine] = useState<Divine | null>(null)
  const [interpretation, setInterpretation] =
    useState<InterpretationResponse | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [userMessage, setUserMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    if (id) {
      loadDivine()
    }
  }, [id])

  const loadDivine = async () => {
    if (!id) return

    setIsLoading(true)
    try {
      const data = await divinesApi.getById(id)
      setDivine(data)

      // 如果已經有解讀，直接顯示
      if (data.is_ai_interpreted && data.interpretation) {
        setInterpretation({
          divine_id: data.id,
          interpretation: data.interpretation,
          metadata: {
            model: data.ai_model || 'claude-sonnet-4',
            generated_at: data.interpreted_at || new Date().toISOString(),
            tokens_used: data.interpretation_tokens || 0,
          },
        })
      }
    } catch (error) {
      console.error('載入占卜失敗:', error)
      alert('載入占卜失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const generateInterpretation = async () => {
    if (!id) return

    setIsGenerating(true)
    try {
      const result = await divinesApi.interpret(id, {
        interpretation_type: 'initial',
      })

      setInterpretation(result)
      setConversationId(result.conversation_id || null)

      // 重新載入以更新 divine 狀態
      await loadDivine()
    } catch (error) {
      console.error('生成解讀失敗:', error)
      alert('生成解讀失敗，請重試')
    } finally {
      setIsGenerating(false)
    }
  }

  const sendMessage = async () => {
    if (!conversationId || !userMessage.trim()) return

    const userMsg: Message = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    }

    setMessages([...messages, userMsg])
    setUserMessage('')
    setIsLoading(true)

    try {
      const response = await conversationsApi.sendMessage(
        conversationId,
        userMessage
      )

      setMessages((prev) => [...prev, response.message])
    } catch (error) {
      console.error('發送訊息失敗:', error)
      alert('發送訊息失敗')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading && !divine) {
    return (
      <div className="text-center py-16">
        <div className="text-6xl mb-4 animate-pulse">🔮</div>
        <h2 className="text-2xl text-tarot-gold">載入中...</h2>
      </div>
    )
  }

  if (!divine) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl text-tarot-accent">找不到占卜記錄</h2>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-tarot-gold mystical-font text-center mb-8">
        塔羅解讀
      </h1>

      {/* 問題 */}
      <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 mb-6">
        <h2 className="text-xl font-bold text-tarot-gold mb-2">你的問題</h2>
        <p className="text-tarot-light">{divine.question_text}</p>
      </div>

      {/* 抽到的牌 */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {divine.spread_data.cards.map((cardInfo, index) => {
          const positions = ['過去', '現在', '未來']
          return (
            <div
              key={index}
              className="bg-tarot-primary/20 backdrop-blur-sm p-4 rounded-lg border border-tarot-accent/30 text-center"
            >
              <h3 className="text-sm font-bold text-tarot-accent mb-2">
                {positions[index]}
              </h3>
              <div
                className={`text-4xl mb-2 ${
                  cardInfo.is_reversed ? 'transform rotate-180' : ''
                }`}
              >
                🎴
              </div>
              <p className="text-tarot-light font-bold">{cardInfo.card_name}</p>
              <p className="text-xs text-tarot-accent">
                {cardInfo.is_reversed ? '逆位' : '正位'}
              </p>
            </div>
          )
        })}
      </div>

      {/* AI 解讀 */}
      {!interpretation && (
        <div className="text-center">
          <button
            onClick={generateInterpretation}
            disabled={isGenerating}
            className="px-8 py-4 bg-gradient-to-r from-tarot-primary to-tarot-secondary text-white text-lg rounded-lg hover:shadow-xl hover:scale-105 transition-all disabled:opacity-50 mystical-font"
          >
            {isGenerating ? '正在生成解讀...' : '✨ 生成 AI 解讀'}
          </button>
        </div>
      )}

      {interpretation && (
        <>
          {/* 整體解讀 */}
          <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 mb-6">
            <h2 className="text-2xl font-bold text-tarot-gold mb-4 mystical-font">
              整體解讀
            </h2>
            <p className="text-tarot-light leading-relaxed">
              {interpretation.interpretation.overall_summary}
            </p>
          </div>

          {/* 單卡解讀 */}
          <div className="space-y-4 mb-6">
            <h2 className="text-2xl font-bold text-tarot-gold mystical-font">
              單卡解讀
            </h2>
            {interpretation.interpretation.card_interpretations.map(
              (cardInterp, index) => (
                <div
                  key={index}
                  className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30"
                >
                  <h3 className="text-lg font-bold text-tarot-accent mb-2">
                    {cardInterp.card_name}
                  </h3>
                  <p className="text-tarot-light">{cardInterp.interpretation}</p>
                </div>
              )
            )}
          </div>

          {/* 建議 */}
          <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 mb-6">
            <h2 className="text-2xl font-bold text-tarot-gold mb-4 mystical-font">
              建議
            </h2>
            <p className="text-tarot-light">{interpretation.interpretation.advice}</p>
          </div>

          {/* 關鍵洞察 */}
          {interpretation.interpretation.key_insights && (
            <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 mb-8">
              <h2 className="text-2xl font-bold text-tarot-gold mb-4 mystical-font">
                關鍵洞察
              </h2>
              <ul className="space-y-2">
                {interpretation.interpretation.key_insights.map(
                  (insight, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-tarot-accent mr-2">✦</span>
                      <span className="text-tarot-light">{insight}</span>
                    </li>
                  )
                )}
              </ul>
            </div>
          )}

          {/* 追問對話 */}
          {conversationId && (
            <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30">
              <h2 className="text-2xl font-bold text-tarot-gold mb-4 mystical-font">
                深入對話
              </h2>

              {/* 對話記錄 */}
              <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-tarot-secondary/30 ml-8'
                        : 'bg-tarot-dark/50 mr-8'
                    }`}
                  >
                    <p className="text-sm text-tarot-accent mb-1">
                      {msg.role === 'user' ? '你' : 'AI 解讀師'}
                    </p>
                    <p className="text-tarot-light">{msg.content}</p>
                  </div>
                ))}
              </div>

              {/* 輸入框 */}
              <div className="flex space-x-2">
                <input
                  type="text"
                  className="flex-1 p-3 bg-tarot-dark/50 border border-tarot-accent/30 rounded-lg text-tarot-light placeholder-tarot-accent/50 focus:outline-none focus:border-tarot-accent"
                  placeholder="針對解讀提問..."
                  value={userMessage}
                  onChange={(e) => setUserMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !userMessage.trim()}
                  className="px-6 py-3 bg-tarot-secondary text-white rounded-lg hover:bg-tarot-primary transition disabled:opacity-50"
                >
                  發送
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
