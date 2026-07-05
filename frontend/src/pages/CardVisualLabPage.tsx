import { useEffect, useMemo, useState } from 'react'
import { cardVisualsApi, cardsApi } from '@/services/api'
import type {
  Card,
  CardVisualCatalog,
  CardVisualCurationScores,
  CardVisualFacet,
  CardVisualPromptResponse,
  CardVisualVariant,
} from '@/types'

const CONTEXTS = ['general', 'love', 'career', 'self', 'decision', 'spiritual'] as const
const CURATION_FIELDS: Array<{
  key: keyof CardVisualCurationScores
  label: string
}> = [
  { key: 'tarot_recognizability', label: 'Tarot readability' },
  { key: 'semantic_accuracy', label: 'Semantic accuracy' },
  { key: 'transform_discipline', label: 'Transform discipline' },
  { key: 'deck_coherence', label: 'Deck coherence' },
  { key: 'originality_safety', label: 'Originality / safety' },
]

const DEFAULT_CURATION_SCORES: CardVisualCurationScores = {
  tarot_recognizability: 4,
  semantic_accuracy: 4,
  transform_discipline: 4,
  deck_coherence: 4,
  originality_safety: 5,
}

export default function CardVisualLabPage() {
  const [cards, setCards] = useState<Card[]>([])
  const [catalog, setCatalog] = useState<CardVisualCatalog | null>(null)
  const [cardSlug, setCardSlug] = useState('major_fool')
  const [styleId, setStyleId] = useState('canonical_echo')
  const [facetId, setFacetId] = useState('')
  const [orientation, setOrientation] = useState<'upright' | 'reversed' | ''>('')
  const [context, setContext] = useState<(typeof CONTEXTS)[number] | ''>('')
  const [questionContext, setQuestionContext] = useState('')
  const [prompt, setPrompt] = useState<CardVisualPromptResponse | null>(null)
  const [variants, setVariants] = useState<CardVisualVariant[]>([])
  const [selectedVariantId, setSelectedVariantId] = useState('')
  const [curationScores, setCurationScores] = useState<CardVisualCurationScores>(
    DEFAULT_CURATION_SCORES
  )
  const [reviewerNotes, setReviewerNotes] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    Promise.all([cardsApi.getAll({ limit: 100 }), cardVisualsApi.getCatalog()])
      .then(([cardList, visualCatalog]) => {
        setCards(cardList.filter((card) => card.slug))
        setCatalog(visualCatalog)
      })
      .catch((error) => {
        console.error('載入視覺資料失敗:', error)
        setMessage('載入視覺資料失敗')
      })
  }, [])

  useEffect(() => {
    cardVisualsApi
      .getVariants({ card_slug: cardSlug })
      .then((items) => {
        setVariants(items)
        setSelectedVariantId(items[0]?.id ?? '')
      })
      .catch(() => {
        // variant 列表不阻擋 prompt 操作
      })
  }, [cardSlug])

  const pilotSlugs = useMemo(
    () => new Set(catalog?.facets.map((facet) => facet.card_slug) ?? []),
    [catalog]
  )
  const pilotCards = cards.filter((card) => card.slug && pilotSlugs.has(card.slug))
  const facets: CardVisualFacet[] =
    catalog?.facets.filter((facet) => facet.card_slug === cardSlug) ?? []

  const requestPayload = () => ({
    card_slug: cardSlug,
    style_scaffold_id: styleId,
    ...(facetId ? { facet_id: facetId } : {}),
    ...(orientation ? { orientation } : {}),
    ...(context ? { context } : {}),
    ...(questionContext.trim() ? { question_context: questionContext.trim() } : {}),
  })

  const composePrompt = async () => {
    setIsLoading(true)
    setMessage('')
    try {
      const result = await cardVisualsApi.composePrompt(requestPayload())
      setPrompt(result)
    } catch (error) {
      console.error('產生 prompt 失敗:', error)
      setMessage('產生 prompt 失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const saveVariant = async () => {
    setIsLoading(true)
    setMessage('')
    try {
      const variant = await cardVisualsApi.createVariant(requestPayload())
      setVariants((current) => [variant, ...current])
      setSelectedVariantId(variant.id)
      setMessage('已建立 variant draft')
    } catch (error) {
      console.error('建立 variant 失敗:', error)
      setMessage('建立 variant 失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const curateVariant = async () => {
    if (!selectedVariantId) return
    setIsLoading(true)
    setMessage('')
    try {
      const variant = await cardVisualsApi.curateVariant(selectedVariantId, {
        scores: curationScores,
        ...(reviewerNotes.trim() ? { reviewer_notes: reviewerNotes.trim() } : {}),
      })
      setVariants((current) =>
        current.map((item) => (item.id === variant.id ? variant : item))
      )
      setMessage(`策展完成：${variant.status}`)
    } catch (error) {
      console.error('策展評分失敗:', error)
      setMessage('策展評分失敗')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="mb-6 text-center text-4xl font-bold text-tarot-gold mystical-font">
        卡牌視覺實驗室
      </h1>

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <section className="rounded-lg border border-tarot-accent/30 bg-tarot-primary/20 p-5 backdrop-blur-sm">
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-bold text-tarot-light">
                卡牌
              </label>
              <select
                className="w-full rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                value={cardSlug}
                onChange={(event) => {
                  setCardSlug(event.target.value)
                  setFacetId('')
                  setPrompt(null)
                }}
              >
                {pilotCards.map((card) => (
                  <option key={card.slug} value={card.slug}>
                    {card.name} / {card.name_en}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-bold text-tarot-light">
                Style Scaffold
              </label>
              <select
                className="w-full rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                value={styleId}
                onChange={(event) => {
                  setStyleId(event.target.value)
                  setPrompt(null)
                }}
              >
                {catalog?.style_scaffolds.map((style) => (
                  <option key={style.id} value={style.id}>
                    {style.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-bold text-tarot-light">
                Facet
              </label>
              <select
                className="w-full rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                value={facetId}
                onChange={(event) => {
                  setFacetId(event.target.value)
                  setPrompt(null)
                }}
              >
                <option value="">Auto select</option>
                {facets.map((facet) => (
                  <option key={facet.id} value={facet.id}>
                    {facet.facet_name} ({facet.orientation})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-2 block text-sm font-bold text-tarot-light">
                  Orientation
                </label>
                <select
                  className="w-full rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                  value={orientation}
                  onChange={(event) => {
                    setOrientation(event.target.value as 'upright' | 'reversed' | '')
                    setPrompt(null)
                  }}
                >
                  <option value="">Auto</option>
                  <option value="upright">upright</option>
                  <option value="reversed">reversed</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-bold text-tarot-light">
                  Context
                </label>
                <select
                  className="w-full rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                  value={context}
                  onChange={(event) => {
                    setContext(event.target.value as (typeof CONTEXTS)[number] | '')
                    setPrompt(null)
                  }}
                >
                  <option value="">Auto</option>
                  {CONTEXTS.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-bold text-tarot-light">
                Question Context
              </label>
              <textarea
                className="h-24 w-full resize-none rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                value={questionContext}
                onChange={(event) => {
                  setQuestionContext(event.target.value)
                  setPrompt(null)
                }}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={composePrompt}
                disabled={isLoading || !cardSlug}
                className="rounded-lg bg-tarot-secondary px-4 py-3 font-bold text-white transition hover:bg-tarot-primary disabled:opacity-50"
              >
                Compose
              </button>
              <button
                type="button"
                onClick={saveVariant}
                disabled={isLoading || !cardSlug}
                className="rounded-lg border border-tarot-gold/60 px-4 py-3 font-bold text-tarot-gold transition hover:bg-tarot-gold/10 disabled:opacity-50"
              >
                Save Draft
              </button>
            </div>

            {message && <p className="text-sm text-tarot-accent">{message}</p>}
          </div>
        </section>

        <section className="space-y-6">
          {prompt ? (
            <div className="rounded-lg border border-tarot-accent/30 bg-tarot-primary/20 p-5 backdrop-blur-sm">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-2xl font-bold text-tarot-gold">
                    {prompt.card_name} / {prompt.card_name_en}
                  </h2>
                  <p className="text-sm text-tarot-accent">
                    {prompt.facet.facet_name} · {prompt.style_scaffold.name}
                  </p>
                </div>
                <span className="rounded-full bg-tarot-dark/60 px-3 py-1 text-xs text-tarot-accent">
                  {prompt.card_slug}
                </span>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <PromptList title="Required Symbols" items={prompt.prompt.required_symbols} />
                <PromptList title="Composition" items={prompt.prompt.composition_terms} />
                <PromptList title="Style" items={prompt.prompt.style_modifiers} />
                <PromptList title="Negative" items={prompt.prompt.negative_constraints} />
              </div>

              <pre className="mt-5 max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-tarot-dark/70 p-4 text-sm text-tarot-light">
                {prompt.final_prompt}
              </pre>
            </div>
          ) : (
            <div className="rounded-lg border border-tarot-accent/30 bg-tarot-primary/20 p-8 text-center text-tarot-accent backdrop-blur-sm">
              選擇卡牌與 scaffold 後產生 prompt。
            </div>
          )}

          <div className="rounded-lg border border-tarot-accent/30 bg-tarot-primary/20 p-5 backdrop-blur-sm">
            <h2 className="mb-4 text-xl font-bold text-tarot-light">
              Variant Drafts
            </h2>
            {variants.length === 0 ? (
              <p className="text-sm text-tarot-accent">目前沒有 variant。</p>
            ) : (
              <div className="space-y-3">
                {variants.slice(0, 8).map((variant) => (
                  <div
                    key={variant.id}
                    className="rounded-lg border border-tarot-accent/20 bg-tarot-dark/40 p-3"
                  >
                    <div className="flex flex-wrap justify-between gap-2">
                      <span className="font-mono text-xs text-tarot-accent">
                        {variant.id}
                      </span>
                      <span className="rounded-full bg-tarot-secondary/40 px-2 py-1 text-xs text-tarot-light">
                        {variant.status}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-tarot-light">
                      {variant.facet_id} · {variant.style_scaffold_id}
                    </p>
                    {variant.curation_scores?.average_score && (
                      <p className="mt-1 text-xs text-tarot-accent">
                        average {variant.curation_scores.average_score} ·{' '}
                        {variant.curation_scores.recommended_status}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-lg border border-tarot-accent/30 bg-tarot-primary/20 p-5 backdrop-blur-sm">
            <h2 className="mb-4 text-xl font-bold text-tarot-light">
              Curation Scorecard
            </h2>
            {variants.length === 0 ? (
              <p className="text-sm text-tarot-accent">先建立 variant draft。</p>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-bold text-tarot-light">
                    Variant
                  </label>
                  <select
                    className="w-full rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                    value={selectedVariantId}
                    onChange={(event) => setSelectedVariantId(event.target.value)}
                  >
                    {variants.map((variant) => (
                      <option key={variant.id} value={variant.id}>
                        {variant.status} / {variant.facet_id} / {variant.id.slice(0, 8)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  {CURATION_FIELDS.map((field) => (
                    <label
                      key={field.key}
                      className="rounded-lg bg-tarot-dark/40 p-3 text-sm text-tarot-light"
                    >
                      <span className="mb-2 block font-bold">{field.label}</span>
                      <input
                        type="range"
                        min="1"
                        max="5"
                        step="1"
                        value={curationScores[field.key]}
                        onChange={(event) =>
                          setCurationScores((current) => ({
                            ...current,
                            [field.key]: Number(event.target.value),
                          }))
                        }
                        className="w-full accent-tarot-gold"
                      />
                      <span className="mt-1 block text-tarot-accent">
                        {curationScores[field.key]} / 5
                      </span>
                    </label>
                  ))}
                </div>

                <textarea
                  className="h-24 w-full resize-none rounded-lg border border-tarot-accent/30 bg-tarot-dark/70 p-3 text-tarot-light"
                  value={reviewerNotes}
                  onChange={(event) => setReviewerNotes(event.target.value)}
                  placeholder="Reviewer notes"
                />

                <button
                  type="button"
                  onClick={curateVariant}
                  disabled={isLoading || !selectedVariantId}
                  className="rounded-lg bg-tarot-secondary px-4 py-3 font-bold text-white transition hover:bg-tarot-primary disabled:opacity-50"
                >
                  Submit Curation
                </button>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

function PromptList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-lg bg-tarot-dark/40 p-4">
      <h3 className="mb-2 font-bold text-tarot-light">{title}</h3>
      <ul className="space-y-1 text-sm text-tarot-accent">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}
