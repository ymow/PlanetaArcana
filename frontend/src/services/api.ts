import axios from 'axios'
import type {
  Card,
  Divine,
  DivineCreate,
  InterpretationResponse,
  Conversation,
  MessageResponse,
  AuthResponse,
  User,
  DailyDraw,
  QuotaStatus,
  ShareBonusResult,
  Persona,
  SpreadInfo,
  SpreadRecommendation,
  CardVisualCatalog,
  CardVisualCurationScores,
  CardVisualPromptResponse,
  CardVisualVariant,
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const TOKEN_STORAGE_KEY = 'planeta_arcana_token'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getAuthToken = () => localStorage.getItem(TOKEN_STORAGE_KEY)

export const setAuthToken = (token: string) => {
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export const clearAuthToken = () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth API
export const authApi = {
  me: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  loginWithGoogle: async (credential: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/google', { credential })
    return response.data
  },

  devLogin: async (email: string, name?: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/dev', { email, name })
    return response.data
  },
}

// Cards API
export const cardsApi = {
  getAll: async (params?: {
    skip?: number
    limit?: number
    type?: string
    suit?: string
  }): Promise<Card[]> => {
    const response = await api.get('/cards', { params })
    return response.data
  },

  getById: async (id: string): Promise<Card> => {
    const response = await api.get(`/cards/${id}`)
    return response.data
  },

  create: async (data: Partial<Card>): Promise<Card> => {
    const response = await api.post('/cards', data)
    return response.data
  },

  update: async (id: string, data: Partial<Card>): Promise<Card> => {
    const response = await api.put(`/cards/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/cards/${id}`)
  },
}

// Divines API
export const divinesApi = {
  getAll: async (params?: {
    skip?: number
    limit?: number
    user_id?: string
  }): Promise<Divine[]> => {
    const response = await api.get('/divines', { params })
    return response.data
  },

  getById: async (id: string): Promise<Divine> => {
    const response = await api.get(`/divines/${id}`)
    return response.data
  },

  create: async (data: DivineCreate): Promise<Divine> => {
    const response = await api.post('/divines', data)
    return response.data
  },

  update: async (id: string, data: Partial<Divine>): Promise<Divine> => {
    const response = await api.put(`/divines/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/divines/${id}`)
  },

  claim: async (id: string): Promise<Divine> => {
    const response = await api.post(`/divines/${id}/claim`)
    return response.data
  },

  share: async (id: string): Promise<ShareBonusResult> => {
    const response = await api.post(`/divines/${id}/share`)
    return response.data
  },

  interpret: async (
    id: string,
    data: { interpretation_type: 'initial' | 'follow_up'; user_message?: string }
  ): Promise<InterpretationResponse> => {
    const response = await api.post(`/divines/${id}/interpret`, data)
    return response.data
  },

  /**
   * SSE 串流解讀。事件：delta（逐段文字）→ complete（完整解讀）；失敗時 error。
   * EventSource 不支援 POST 與自訂 header，改用 fetch + ReadableStream。
   */
  interpretStream: async (
    id: string,
    handlers: {
      onDelta: (text: string) => void
      onComplete: (result: InterpretationResponse) => void
      onError: (detail: string) => void
    }
  ): Promise<void> => {
    const token = getAuthToken()
    const response = await fetch(
      `${API_BASE_URL}/api/divines/${id}/interpret/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      }
    )

    if (!response.ok || !response.body) {
      let detail = `串流請求失敗（${response.status}）`
      try {
        detail = (await response.json()).detail || detail
      } catch {
        // 回應非 JSON 時沿用預設訊息
      }
      handlers.onError(detail)
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    const dispatch = (block: string) => {
      let event = ''
      let data = ''
      for (const line of block.split('\n')) {
        if (line.startsWith('event: ')) event = line.slice(7)
        else if (line.startsWith('data: ')) data = line.slice(6)
      }
      if (!event || !data) return
      if (event === 'delta') handlers.onDelta(JSON.parse(data).text)
      else if (event === 'complete') handlers.onComplete(JSON.parse(data))
      else if (event === 'error') handlers.onError(JSON.parse(data).detail)
    }

    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      let idx
      while ((idx = buffer.indexOf('\n\n')) !== -1) {
        dispatch(buffer.slice(0, idx))
        buffer = buffer.slice(idx + 2)
      }
    }
  },
}

// Conversations API
export const conversationsApi = {
  getById: async (id: string): Promise<Conversation> => {
    const response = await api.get(`/conversations/${id}`)
    return response.data
  },

  sendMessage: async (
    id: string,
    message: string
  ): Promise<MessageResponse> => {
    const response = await api.post(`/conversations/${id}/message`, { message })
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/conversations/${id}`)
  },
}

// Personas API（角色列表是靜態的,模組層快取一次）
let personasCache: Promise<Persona[]> | null = null

export const personasApi = {
  getAll: (): Promise<Persona[]> => {
    if (!personasCache) {
      personasCache = api
        .get('/personas')
        .then((response) => response.data)
        .catch((error) => {
          personasCache = null // 失敗不快取,允許重試
          throw error
        })
    }
    return personasCache
  },
}

// Spreads API（牌陣列表是靜態的,模組層快取一次）
let spreadsCache: Promise<SpreadInfo[]> | null = null

export const spreadsApi = {
  getAll: (): Promise<SpreadInfo[]> => {
    if (!spreadsCache) {
      spreadsCache = api
        .get('/spreads')
        .then((response) => response.data)
        .catch((error) => {
          spreadsCache = null // 失敗不快取,允許重試
          throw error
        })
    }
    return spreadsCache
  },

  recommend: async (data: {
    question_text: string
    options?: { a: string; b: string }
  }): Promise<SpreadRecommendation> => {
    const response = await api.post('/spreads/recommend', data)
    return response.data
  },
}

// Card Visuals API
export const cardVisualsApi = {
  getCatalog: async (): Promise<CardVisualCatalog> => {
    const response = await api.get('/card-visuals/catalog')
    return response.data
  },

  composePrompt: async (data: {
    card_slug: string
    style_scaffold_id?: string
    facet_id?: string
    orientation?: 'upright' | 'reversed'
    context?: 'general' | 'love' | 'career' | 'self' | 'decision' | 'spiritual'
    question_context?: string
  }): Promise<CardVisualPromptResponse> => {
    const response = await api.post('/card-visuals/prompts', data)
    return response.data
  },

  createVariant: async (data: {
    card_slug: string
    style_scaffold_id?: string
    facet_id?: string
    orientation?: 'upright' | 'reversed'
    context?: 'general' | 'love' | 'career' | 'self' | 'decision' | 'spiritual'
    question_context?: string
    image_url?: string
    model?: string
    seed?: number
    status?: 'draft' | 'generated' | 'approved' | 'rejected' | 'needs_revision'
  }): Promise<CardVisualVariant> => {
    const response = await api.post('/card-visuals/variants', data)
    return response.data
  },

  getVariants: async (params?: {
    card_slug?: string
    status?: string
  }): Promise<CardVisualVariant[]> => {
    const response = await api.get('/card-visuals/variants', { params })
    return response.data
  },

  curateVariant: async (
    variantId: string,
    data: {
      scores: CardVisualCurationScores
      reviewer_notes?: string
    }
  ): Promise<CardVisualVariant> => {
    const response = await api.post(
      `/card-visuals/variants/${variantId}/curation`,
      data
    )
    return response.data
  },
}

// Quota API
export const quotaApi = {
  getStatus: async (): Promise<QuotaStatus> => {
    const response = await api.get('/quota')
    return response.data
  },
}

// Daily Draw API
export const dailyDrawsApi = {
  getToday: async (): Promise<DailyDraw> => {
    const response = await api.get('/daily-draws/today')
    return response.data
  },

  createToday: async (): Promise<DailyDraw> => {
    const response = await api.post('/daily-draws/today')
    return response.data
  },
}

export default api
