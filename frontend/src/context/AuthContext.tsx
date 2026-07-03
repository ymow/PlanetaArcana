import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import {
  authApi,
  clearAuthToken,
  getAuthToken,
  setAuthToken,
} from '@/services/api'
import type { User } from '@/types'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  loginWithGoogleCredential: (credential: string) => Promise<void>
  devLogin: () => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    if (!getAuthToken()) {
      setUser(null)
      setIsLoading(false)
      return
    }

    try {
      const currentUser = await authApi.me()
      setUser(currentUser)
    } catch {
      clearAuthToken()
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  const loginWithGoogleCredential = useCallback(async (credential: string) => {
    const response = await authApi.loginWithGoogle(credential)
    setAuthToken(response.access_token)
    setUser(response.user)
  }, [])

  const devLogin = useCallback(async () => {
    const response = await authApi.devLogin(
      'reader@planeta.local',
      'Planeta Reader'
    )
    setAuthToken(response.access_token)
    setUser(response.user)
  }, [])

  const logout = useCallback(() => {
    clearAuthToken()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      isLoading,
      loginWithGoogleCredential,
      devLogin,
      logout,
      refreshUser,
    }),
    [user, isLoading, loginWithGoogleCredential, devLogin, logout, refreshUser]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return value
}
