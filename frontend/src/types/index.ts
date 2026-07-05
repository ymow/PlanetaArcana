// Card Types
export interface Card {
  id: string
  slug?: string
  name: string
  name_en: string
  type: 'major' | 'minor'
  suit?: 'wands' | 'cups' | 'swords' | 'pentacles'
  rank?: string
  number?: number
  upright_meaning: string
  upright_keywords: string
  reversed_meaning: string
  reversed_keywords: string
  symbolism?: string
  description?: string
  image_url?: string
}

// Card visual AIGC Types
export interface CardVisualFacet {
  id: string
  card_slug: string
  orientation: 'upright' | 'reversed' | 'both'
  context: 'general' | 'love' | 'career' | 'self' | 'decision' | 'spiritual'
  facet_name: string
  core_meaning: string
  emotional_tone: string[]
  motion: string
  polarity: string
  question_bias?: string
}

export interface CardVisualStyleScaffold {
  id: string
  name: string
  medium: string
  line_language: string
  palette_logic: string
  figure_treatment: string
  symbol_treatment: string
  composition_bias: string
  texture_language: string
  border_system: string
  typography_system: string
  negative_constraints: string[]
}

export interface CardVisualCatalog {
  facets: CardVisualFacet[]
  symbols: Array<Record<string, unknown>>
  compositions: Array<Record<string, unknown>>
  style_scaffolds: CardVisualStyleScaffold[]
}

export interface GeneratedVisualPrompt {
  subject_terms: string[]
  meaning_terms: string[]
  required_symbols: string[]
  transformed_symbols: string[]
  composition_terms: string[]
  style_modifiers: string[]
  quality_modifiers: string[]
  negative_constraints: string[]
  title_text?: string
}

export interface CardVisualPromptResponse {
  card_slug: string
  card_name: string
  card_name_en: string
  facet: CardVisualFacet
  style_scaffold: CardVisualStyleScaffold
  prompt: GeneratedVisualPrompt
  final_prompt: string
}

export interface CardVisualCurationScores {
  tarot_recognizability: number
  semantic_accuracy: number
  transform_discipline: number
  deck_coherence: number
  originality_safety: number
}

export interface CardVisualCurationResult extends Partial<CardVisualCurationScores> {
  average_score?: number
  recommended_status?: 'approved' | 'rejected' | 'needs_revision'
  gate_notes?: string[]
  reviewer_notes?: string
}

export interface CardVisualVariant {
  id: string
  card_id: string
  card_slug: string
  facet_id: string
  style_scaffold_id: string
  prompt_json: GeneratedVisualPrompt
  final_prompt: string
  image_url?: string
  model?: string
  seed?: number
  curation_scores?: CardVisualCurationResult
  status: 'draft' | 'generated' | 'approved' | 'rejected' | 'needs_revision'
  created_at: string
  updated_at?: string
}

// Divine (占卜) Types
export interface CardInSpread {
  position: string
  position_order: number
  card_id: string
  card_name: string
  card_name_en: string
  is_reversed: boolean
}

export interface SpreadData {
  type: string
  cards: CardInSpread[]
  options?: { a: string; b: string }
}

// Spread registry Types
export interface SpreadPosition {
  key: string
  name: string
  description: string
}

export interface SpreadInfo {
  id: string
  name: string
  description: string
  card_count: number
  requires_options: boolean
  positions: SpreadPosition[]
}

export interface SpreadRecommendation {
  spread_id: string
  spread_name: string
  description: string
  card_count: number
  requires_options: boolean
  positions: SpreadPosition[]
  reason: string
  confidence: 'high' | 'medium' | 'fallback'
  matched_rule: string
}

export interface Divine {
  id: string
  question_text: string
  question_type?: string
  question_category?: string
  spread_type: string
  spread_data: SpreadData
  persona_id?: string
  interpretation?: InterpretationData
  is_ai_interpreted: boolean
  ai_model?: string
  interpretation_tokens?: number
  interpreted_at?: string
  created_at: string
  updated_at: string
  user_id?: string
}

export interface DivineCreate {
  question_text: string
  question_type?: string
  question_category?: string
  spread_type: string
  spread_data: SpreadData
  persona_id?: string
}

// Persona Types
export interface Persona {
  id: string
  name: string
  name_en: string
  emoji: string
  tagline: string
  description: string
  is_premium: boolean
}

// AI Interpretation Types
export interface CardInterpretation {
  position: string
  card_name: string
  interpretation: string
}

export interface InterpretationData {
  overall_summary: string
  card_interpretations: CardInterpretation[]
  advice: string
  key_insights?: string[]
}

export interface InterpretationResponse {
  divine_id: string
  interpretation: InterpretationData
  conversation_id?: string
  metadata: {
    model: string
    generated_at: string
    tokens_used: number
  }
}

// Conversation Types
export interface Message {
  role: 'system' | 'user' | 'assistant'
  content: string
  timestamp: string
  tokens?: number
}

export interface Conversation {
  id: string
  divine_id: string
  messages: Message[]
  total_tokens: number
  created_at: string
  updated_at: string
  user_id?: string
}

export interface MessageResponse {
  conversation_id: string
  message: Message
  tokens_used: number
}

// Auth Types
export interface User {
  id: string
  email: string
  name?: string
  avatar_url?: string
  created_at: string
  last_login_at?: string
}

export interface AuthResponse {
  access_token: string
  token_type: 'bearer'
  user: User
}

// Quota Types
export interface QuotaStatus {
  daily_limit: number
  share_bonus: number
  used: number
  remaining: number
}

export interface ShareBonusResult {
  granted: boolean
  reason?: string
  quota: QuotaStatus
}

// Daily Draw Types
export interface DailyDrawInterpretation {
  key_theme: string
  summary: string
  advice: string
  reflection_prompt: string
}

export interface DailyDraw {
  id: string
  user_id: string
  draw_date: string
  card_id: string
  card_name: string
  card_name_en: string
  is_reversed: boolean
  interpretation: DailyDrawInterpretation
  ai_model?: string
  interpretation_tokens?: number
  created_at: string
}
