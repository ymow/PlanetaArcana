import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { cardsApi, divinesApi, personasApi, spreadsApi } from '@/services/api'
import type {
  Card,
  DivineCreate,
  Persona,
  SpreadInfo,
  SpreadRecommendation,
} from '@/types'

// 牌陣資料載入失敗時的離線 fallback(維持原本的三牌陣流程)
const FALLBACK_SPREAD: SpreadInfo = {
  id: 'past_present_future',
  name: '過去-現在-未來',
  description: '經典三牌陣',
  card_count: 3,
  requires_options: false,
  positions: [
    { key: 'past', name: '過去', description: '影響問題的過去因素' },
    { key: 'present', name: '現在', description: '當前的狀態與挑戰' },
    { key: 'future', name: '未來', description: '可能的發展方向' },
  ],
}

export default function DivinePage() {
  const navigate = useNavigate()
  const [step, setStep] = useState<'question' | 'drawing' | 'drawn'>('question')
  const [question, setQuestion] = useState('')
  const [personas, setPersonas] = useState<Persona[]>([])
  const [personaId, setPersonaId] = useState<string | null>(null)
  const [spreads, setSpreads] = useState<SpreadInfo[]>([])
  const [spreadMode, setSpreadMode] = useState<'auto' | 'manual'>('auto')
  const [spreadId, setSpreadId] = useState('past_present_future')
  const [recommendation, setRecommendation] =
    useState<SpreadRecommendation | null>(null)
  const [optionA, setOptionA] = useState('')
  const [optionB, setOptionB] = useState('')
  const [drawnCards, setDrawnCards] = useState<
    Array<{ card: Card; is_reversed: boolean }>
  >([])
  const [isLoading, setIsLoading] = useState(false)

  const recommendedSpread: SpreadInfo | null =
    recommendation && recommendation.spread_id === spreadId
      ? {
          id: recommendation.spread_id,
          name: recommendation.spread_name,
          description: recommendation.description,
          card_count: recommendation.card_count,
          requires_options: recommendation.requires_options,
          positions: recommendation.positions,
        }
      : null
  const spread =
    spreads.find((s) => s.id === spreadId) ?? recommendedSpread ?? FALLBACK_SPREAD
  const showOptionInputs =
    spreadMode === 'manual'
      ? spread.requires_options
      : recommendation?.requires_options ?? false

  useEffect(() => {
    personasApi
      .getAll()
      .then((list) => {
        setPersonas(list)
        setPersonaId((current) => current ?? list[0]?.id ?? null)
      })
      .catch((error) => {
        // 角色列表載入失敗不擋占卜流程,後端會用預設角色
        console.error('載入解讀角色失敗:', error)
      })
    spreadsApi
      .getAll()
      .then(setSpreads)
      .catch((error) => {
        // 牌陣列表載入失敗時 fallback 到經典三牌陣
        console.error('載入牌陣失敗:', error)
      })
  }, [])

  const handleQuestionSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setIsLoading(true)
    setStep('drawing')

    try {
      let activeSpread = spread

      if (spreadMode === 'auto') {
        const recommended = await spreadsApi.recommend({
          question_text: question.trim(),
          ...(optionA.trim() && optionB.trim()
            ? { options: { a: optionA.trim(), b: optionB.trim() } }
            : {}),
        })
        const nextSpread: SpreadInfo = {
          id: recommended.spread_id,
          name: recommended.spread_name,
          description: recommended.description,
          card_count: recommended.card_count,
          requires_options: recommended.requires_options,
          positions: recommended.positions,
        }

        setRecommendation(recommended)
        setSpreadId(recommended.spread_id)
        activeSpread =
          spreads.find((s) => s.id === recommended.spread_id) ?? nextSpread

        if (
          recommended.requires_options &&
          (!optionA.trim() || !optionB.trim())
        ) {
          setIsLoading(false)
          setStep('question')
          return
        }
      } else if (spread.requires_options && (!optionA.trim() || !optionB.trim())) {
        alert('請填寫兩個選項的描述')
        setIsLoading(false)
        setStep('question')
        return
      }

      // 取得所有卡片
      const allCards = await cardsApi.getAll({ limit: 78 })

      // 依牌陣張數隨機抽取不重複的牌
      const shuffled = [...allCards].sort(() => Math.random() - 0.5)
      const selected = shuffled.slice(0, activeSpread.card_count).map((card) => ({
        card,
        is_reversed: Math.random() > 0.5, // 50% 機率逆位
      }))

      setDrawnCards(selected)

      // 模擬抽牌動畫
      setTimeout(() => {
        setStep('drawn')
        setIsLoading(false)
      }, 2000)
    } catch (error) {
      console.error('抽牌失敗:', error)
      alert('抽牌失敗，請重試')
      setIsLoading(false)
      setStep('question')
    }
  }

  const handleCreateDivine = async () => {
    setIsLoading(true)

    try {
      const divineData: DivineCreate = {
        question_text: question,
        ...(personaId ? { persona_id: personaId } : {}),
        spread_type: spread.id,
        spread_data: {
          type: spread.id,
          cards: drawnCards.map((item, index) => ({
            position: spread.positions[index]?.key ?? `position_${index}`,
            position_order: index + 1,
            card_id: item.card.id,
            card_name: item.card.name,
            card_name_en: item.card.name_en,
            is_reversed: item.is_reversed,
          })),
          ...(spread.requires_options
            ? { options: { a: optionA.trim(), b: optionB.trim() } }
            : {}),
        },
      }

      const divine = await divinesApi.create(divineData)

      // 導航到解讀頁面
      navigate(`/divine/${divine.id}`)
    } catch (error) {
      console.error('建立占卜失敗:', error)
      alert('建立占卜失敗，請重試')
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-tarot-gold mystical-font text-center mb-8">
        塔羅占卜
      </h1>

      {/* Step 1: 輸入問題 */}
      {step === 'question' && (
        <div className="bg-tarot-primary/20 backdrop-blur-sm p-8 rounded-lg border border-tarot-accent/30">
          <h2 className="text-2xl font-bold text-tarot-light mb-4">
            請輸入你的問題
          </h2>
          <p className="text-tarot-accent mb-6">
            清晰具體地描述你想詢問的事項，塔羅牌將為你指引方向。
          </p>

          <form onSubmit={handleQuestionSubmit}>
            <textarea
              className="w-full p-4 bg-tarot-dark/50 border border-tarot-accent/30 rounded-lg text-tarot-light placeholder-tarot-accent/50 focus:outline-none focus:border-tarot-accent resize-none"
              rows={4}
              placeholder="例如：我的工作會有什麼發展？"
              value={question}
              onChange={(e) => {
                setQuestion(e.target.value)
                setRecommendation(null)
              }}
              required
            />

            {/* 選擇牌陣 */}
            {spreads.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-bold text-tarot-light mb-3">
                  選擇牌陣
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setSpreadMode('auto')
                      setRecommendation(null)
                    }}
                    className={`p-4 rounded-lg border text-left transition ${
                      spreadMode === 'auto'
                        ? 'border-tarot-gold bg-tarot-secondary/30 shadow-lg'
                        : 'border-tarot-accent/30 bg-tarot-dark/30 hover:border-tarot-accent/60'
                    }`}
                  >
                    <div className="font-bold text-tarot-light">
                      讓 PlanetaArcana 選
                    </div>
                    <div className="text-xs text-tarot-accent mt-1">
                      依問題自動推薦單張、三牌或二選一牌陣
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setSpreadMode('manual')
                      setRecommendation(null)
                    }}
                    className={`p-4 rounded-lg border text-left transition ${
                      spreadMode === 'manual'
                        ? 'border-tarot-gold bg-tarot-secondary/30 shadow-lg'
                        : 'border-tarot-accent/30 bg-tarot-dark/30 hover:border-tarot-accent/60'
                    }`}
                  >
                    <div className="font-bold text-tarot-light">手動選擇</div>
                    <div className="text-xs text-tarot-accent mt-1">
                      自己指定要使用的牌陣
                    </div>
                  </button>
                </div>

                {spreadMode === 'manual' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
                    {spreads.map((s) => (
                      <button
                        key={s.id}
                        type="button"
                        onClick={() => {
                          setSpreadId(s.id)
                          setRecommendation(null)
                        }}
                        className={`p-4 rounded-lg border text-left transition ${
                          spreadId === s.id
                            ? 'border-tarot-gold bg-tarot-secondary/30 shadow-lg'
                            : 'border-tarot-accent/30 bg-tarot-dark/30 hover:border-tarot-accent/60'
                        }`}
                      >
                        <div className="font-bold text-tarot-light">
                          {s.name}
                          <span className="ml-2 text-xs text-tarot-accent">
                            {s.card_count} 張牌
                          </span>
                        </div>
                        <div className="text-xs text-tarot-accent mt-1">
                          {s.description}
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {spreadMode === 'auto' && recommendation && (
                  <div className="mt-3 rounded-lg border border-tarot-accent/30 bg-tarot-dark/30 p-4">
                    <div className="font-bold text-tarot-light">
                      推薦牌陣：{recommendation.spread_name}
                      <span className="ml-2 text-xs text-tarot-accent">
                        {recommendation.card_count} 張牌
                      </span>
                    </div>
                    <div className="text-sm text-tarot-accent mt-1">
                      {recommendation.reason}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 二選一牌陣的選項描述 */}
            {showOptionInputs && (
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-bold text-tarot-light mb-2">
                    選項 A
                  </label>
                  <input
                    type="text"
                    className="w-full p-3 bg-tarot-dark/50 border border-tarot-accent/30 rounded-lg text-tarot-light placeholder-tarot-accent/50 focus:outline-none focus:border-tarot-accent"
                    placeholder="例如:留在現在的公司"
                    value={optionA}
                    onChange={(e) => setOptionA(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-tarot-light mb-2">
                    選項 B
                  </label>
                  <input
                    type="text"
                    className="w-full p-3 bg-tarot-dark/50 border border-tarot-accent/30 rounded-lg text-tarot-light placeholder-tarot-accent/50 focus:outline-none focus:border-tarot-accent"
                    placeholder="例如:接受新的工作機會"
                    value={optionB}
                    onChange={(e) => setOptionB(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}

            {/* 選擇解讀角色 */}
            {personas.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-bold text-tarot-light mb-3">
                  選擇你的塔羅師
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {personas.map((persona) => (
                    <button
                      key={persona.id}
                      type="button"
                      onClick={() => setPersonaId(persona.id)}
                      className={`p-4 rounded-lg border text-left transition ${
                        personaId === persona.id
                          ? 'border-tarot-gold bg-tarot-secondary/30 shadow-lg'
                          : 'border-tarot-accent/30 bg-tarot-dark/30 hover:border-tarot-accent/60'
                      }`}
                    >
                      <div className="text-3xl mb-2">{persona.emoji}</div>
                      <div className="font-bold text-tarot-light">
                        {persona.name}
                        {persona.is_premium && <span className="ml-1">🔒</span>}
                      </div>
                      <div className="text-xs text-tarot-accent mt-1">
                        {persona.tagline}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="mt-4 w-full py-3 bg-gradient-to-r from-tarot-primary to-tarot-secondary text-white rounded-lg hover:shadow-xl hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed mystical-font"
            >
              開始抽牌 🔮
            </button>
          </form>
        </div>
      )}

      {/* Step 2: 抽牌中 */}
      {step === 'drawing' && (
        <div className="text-center py-16">
          <div className="text-6xl mb-4 animate-pulse">🔮</div>
          <h2 className="text-2xl font-bold text-tarot-gold mystical-font">
            正在為你抽取塔羅牌...
          </h2>
          <p className="text-tarot-accent mt-2">請靜心等待</p>
        </div>
      )}

      {/* Step 3: 顯示抽到的牌 */}
      {step === 'drawn' && (
        <div>
          <div className="bg-tarot-primary/20 backdrop-blur-sm p-8 rounded-lg border border-tarot-accent/30 mb-6">
            <h2 className="text-2xl font-bold text-tarot-gold mystical-font mb-2">
              你的問題
            </h2>
            <p className="text-tarot-light">{question}</p>
          </div>

          <div
            className={`grid gap-6 mb-8 ${
              drawnCards.length === 1
                ? 'max-w-sm mx-auto'
                : drawnCards.length === 2
                  ? 'md:grid-cols-2'
                  : 'md:grid-cols-3'
            }`}
          >
            {drawnCards.map((item, index) => {
              const position = spread.positions[index] ?? {
                key: `position_${index}`,
                name: `位置 ${index + 1}`,
                description: '',
              }

              return (
                <div
                  key={index}
                  className="bg-tarot-primary/20 backdrop-blur-sm p-6 rounded-lg border border-tarot-accent/30 transform hover:scale-105 transition"
                >
                  <div className="text-center mb-4">
                    <h3 className="text-xl font-bold text-tarot-gold mystical-font">
                      {position.name}
                    </h3>
                    <p className="text-sm text-tarot-accent">
                      {position.description}
                    </p>
                  </div>

                  <div className="text-center">
                    <div
                      className={`text-6xl mb-3 ${
                        item.is_reversed ? 'transform rotate-180' : ''
                      }`}
                    >
                      🎴
                    </div>
                    <h4 className="text-lg font-bold text-tarot-light mb-1">
                      {item.card.name}
                    </h4>
                    <p className="text-sm text-tarot-accent mb-2">
                      {item.card.name_en}
                    </p>
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs ${
                        item.is_reversed
                          ? 'bg-purple-500/30 text-purple-200'
                          : 'bg-green-500/30 text-green-200'
                      }`}
                    >
                      {item.is_reversed ? '逆位' : '正位'}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>

          <button
            onClick={handleCreateDivine}
            disabled={isLoading}
            className="w-full py-4 bg-gradient-to-r from-tarot-primary to-tarot-secondary text-white text-lg rounded-lg hover:shadow-xl hover:scale-105 transition-all disabled:opacity-50 mystical-font"
          >
            {isLoading ? '處理中...' : '✨ 獲取 AI 解讀'}
          </button>
        </div>
      )}
    </div>
  )
}
