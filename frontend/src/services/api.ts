import axios from 'axios'
import type {
  Card,
  Divine,
  DivineCreate,
  InterpretationResponse,
  Conversation,
  MessageResponse,
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

  interpret: async (
    id: string,
    data: { interpretation_type: 'initial' | 'follow_up'; user_message?: string }
  ): Promise<InterpretationResponse> => {
    const response = await api.post(`/divines/${id}/interpret`, data)
    return response.data
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

export default api
