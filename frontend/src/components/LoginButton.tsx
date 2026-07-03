import { useEffect, useRef, useState } from 'react'
import { useAuth } from '@/context/AuthContext'

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (options: {
            client_id: string
            callback: (response: { credential: string }) => void
          }) => void
          renderButton: (
            element: HTMLElement,
            options: Record<string, string>
          ) => void
        }
      }
    }
  }
}

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined

export default function LoginButton() {
  const { user, isLoading, loginWithGoogleCredential, devLogin, logout } = useAuth()
  const googleButtonRef = useRef<HTMLDivElement | null>(null)
  const [authError, setAuthError] = useState<string | null>(null)

  useEffect(() => {
    if (!googleClientId || user || !googleButtonRef.current) return

    const renderGoogleButton = () => {
      if (!window.google || !googleButtonRef.current) return
      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: async (response) => {
          try {
            await loginWithGoogleCredential(response.credential)
            setAuthError(null)
          } catch {
            setAuthError('Google 登入失敗')
          }
        },
      })
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'filled_black',
        size: 'medium',
        text: 'signin_with',
      })
    }

    const existingScript = document.querySelector(
      'script[src="https://accounts.google.com/gsi/client"]'
    )
    if (existingScript) {
      renderGoogleButton()
      return
    }

    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = renderGoogleButton
    document.body.appendChild(script)
  }, [loginWithGoogleCredential, user])

  if (isLoading) {
    return (
      <span className="text-sm text-tarot-accent" aria-live="polite">
        載入中
      </span>
    )
  }

  if (user) {
    return (
      <div className="flex items-center gap-3">
        <span className="max-w-[160px] truncate text-sm text-tarot-accent">
          {user.name || user.email}
        </span>
        <button
          type="button"
          onClick={logout}
          className="rounded border border-tarot-accent/40 px-3 py-1.5 text-sm text-tarot-light hover:border-tarot-accent hover:text-tarot-accent transition"
        >
          登出
        </button>
      </div>
    )
  }

  if (googleClientId) {
    return (
      <div className="flex flex-col items-end gap-1">
        <div ref={googleButtonRef} />
        {authError && <p className="text-xs text-red-300">{authError}</p>}
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={async () => {
        try {
          await devLogin()
          setAuthError(null)
        } catch {
          setAuthError('開發登入未啟用')
        }
      }}
      className="rounded bg-tarot-secondary px-4 py-2 text-sm text-white hover:bg-tarot-primary transition"
    >
      開發登入
    </button>
  )
}
