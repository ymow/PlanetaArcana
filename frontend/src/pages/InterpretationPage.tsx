import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { divinesApi, conversationsApi, personasApi, spreadsApi } from '@/services/api'
import { useAuth } from '@/context/AuthContext'
import type {
  Divine,
  InterpretationResponse,
  Message,
  Persona,
  SpreadInfo,
} from '@/types'

// 從串流中的 JSON 緩衝區抽出（可能尚未閉合的）overall_summary 字串做漸進顯示
function extractPartialSummary(raw: string): string {
  const match = raw.match(/"overall_summary"\s*:\s*"((?:[^"\\]|\\.)*)/)
  if (!match) return ''
  return match[1]
    .replace(/\\n/g, '\n')
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, '\\')
}

export default function InterpretationPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [divine, setDivine] = useState<Divine | null>(null)
  const [interpretation, setInterpretation] =
    useState<InterpretationResponse | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [userMessage, setUserMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSharing, setIsSharing] = useState(false)
  const [shareMessage, setShareMessage] = useState<string | null>(null)
  const [streamingPreview, setStreamingPreview] = useState('')
  const [personas, setPersonas] = useState<Persona[]>([])
  const [spreads, setSpreads] = useState<SpreadInfo[]>([])

  useEffect(() => {
    if (id) {
      loadDivine()
    }
    personasApi.getAll().then(setPersonas).catch(() => {
      // 角色資訊載入失敗只影響顯示名稱,不擋解讀流程
    })
    spreadsApi.getAll().then(setSpreads).catch(() => {
      // 牌陣資訊載入失敗只影響位置名稱顯示
    })
  }, [id])

  // 這筆占卜的解讀角色(舊資料沒有 persona_id 時退回第一個 = 預設角色)
  const persona =
    personas.find((p) => p.id === divine?.persona_id) ?? personas[0] ?? null
  const personaLabel = persona ? `${persona.emoji} ${persona.name}` : 'AI 解讀師'

  // 這筆占卜的牌陣(用於位置名稱顯示)
  const spread = spreads.find((s) => s.id === divine?.spread_type) ?? null
  const positionName = (positionKey: string, index: number) =>
    spread?.positions.find((p) => p.key === positionKey)?.name ??
    ['過去', '現在', '未來'][index] ??
    positionKey

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
    setStreamingPreview('')
    let rawBuffer = ''

    try {
      await divinesApi.interpretStream(id, {
        onDelta: (text) => {
          rawBuffer += text
          setStreamingPreview(extractPartialSummary(rawBuffer))
        },
        onComplete: async (result) => {
          setInterpretation(result)
          setConversationId(result.conversation_id || null)
          // 重新載入以更新 divine 狀態
          await loadDivine()
        },
        onError: (detail) => {
          console.error('生成解讀失敗:', detail)
          alert(`生成解讀失敗:${detail}`)
        },
      })
    } catch (error) {
      // 串流連線中斷（未持久化任何內容），可直接重試
      console.error('生成解讀失敗:', error)
      alert('生成解讀失敗，請重試')
    } finally {
      setIsGenerating(false)
      setStreamingPreview('')
    }
  }

  const claimDivine = async () => {
    if (!id) return

    setIsLoading(true)
    try {
      const claimed = await divinesApi.claim(id)
      setDivine(claimed)
    } catch (error) {
      console.error('綁定占卜失敗:', error)
      alert('綁定占卜失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const shareDivine = async () => {
    if (!id || !divine) return

    setIsSharing(true)
    setShareMessage(null)
    try {
      const shareUrl = window.location.href
      const shareText = `我在 Planeta Arcana 問了塔羅:「${divine.question_text}」`
      const canNativeShare = typeof navigator.share === 'function'
      if (canNativeShare) {
        await navigator.share({ title: 'Planeta Arcana 塔羅解讀', text: shareText, url: shareUrl })
      } else {
        await navigator.clipboard.writeText(`${shareText}\n${shareUrl}`)
      }

      const result = await divinesApi.share(id)
      if (result.granted) {
        setShareMessage(
          `分享成功!今日解讀額度 +1,剩餘 ${result.quota.remaining} 次`
        )
      } else {
        setShareMessage(
          `${canNativeShare ? '已分享' : '連結已複製'}(${result.reason})`
        )
      }
    } catch (error) {
      // 使用者取消系統分享面板時不視為錯誤
      if ((error as DOMException)?.name !== 'AbortError') {
        console.error('分享失敗:', error)
        setShareMessage('分享失敗,請重試')
      }
    } finally {
      setIsSharing(false)
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
        {divine.spread_data.options && (
          <div className="mt-3 text-sm text-tarot-accent space-y-1">
            <p>A:{divine.spread_data.options.a}</p>
            <p>B:{divine.spread_data.options.b}</p>
          </div>
        )}
        {user && !divine.user_id && (
          <button
            type="button"
            onClick={claimDivine}
            disabled={isLoading}
            className="mt-4 rounded bg-tarot-secondary px-4 py-2 text-sm text-white transition hover:bg-tarot-primary disabled:opacity-50"
          >
            保存到我的歷史
          </button>
        )}
      </div>

      {/* 抽到的牌 */}
      <div
        className={`grid gap-4 mb-8 ${
          divine.spread_data.cards.length === 1
            ? 'max-w-sm mx-auto'
            : divine.spread_data.cards.length === 2
              ? 'md:grid-cols-2'
              : 'md:grid-cols-3'
        }`}
      >
        {divine.spread_data.cards.map((cardInfo, index) => {
          return (
            <div
              key={index}
              className="bg-tarot-primary/20 backdrop-blur-sm p-4 rounded-lg border border-tarot-accent/30 text-center"
            >
              <h3 className="text-sm font-bold text-tarot-accent mb-2">
                {positionName(cardInfo.position, index)}
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

          {/* 串流中的漸進預覽 */}
          {isGenerating && (
            <div className="mt-6 bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 text-left">
              <h2 className="text-xl font-bold text-tarot-gold mb-3 mystical-font">
                <span className="animate-pulse">🔮</span>{' '}
                {persona ? `${persona.name}正在解讀…` : '塔羅師正在解讀…'}
              </h2>
              <p className="text-tarot-light leading-relaxed whitespace-pre-wrap">
                {streamingPreview || '正在感應牌面能量…'}
                <span className="animate-pulse">▍</span>
              </p>
            </div>
          )}
        </div>
      )}

      {interpretation && (
        <>
          {/* 整體解讀 */}
          <div className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 mb-6">
            <h2 className="text-2xl font-bold text-tarot-gold mb-1 mystical-font">
              整體解讀
            </h2>
            {persona && (
              <p className="text-sm text-tarot-accent mb-4">
                由 {personaLabel} 為你解讀
              </p>
            )}
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

          {/* 分享 +1 配額 */}
          <div className="text-center mb-8">
            <button
              onClick={shareDivine}
              disabled={isSharing}
              className="px-6 py-3 bg-tarot-secondary text-white rounded-lg hover:bg-tarot-primary transition disabled:opacity-50"
            >
              {isSharing ? '分享中...' : '🔗 分享這次解讀(+1 今日額度)'}
            </button>
            {shareMessage && (
              <p className="mt-3 text-sm text-tarot-accent">{shareMessage}</p>
            )}
          </div>

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
                      {msg.role === 'user' ? '你' : personaLabel}
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
