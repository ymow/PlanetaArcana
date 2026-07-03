// Card Types
export interface Card {
  id: string
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
