import { createContext, useContext, useEffect, useState } from 'react'
import { api, getStoredToken, getStoredUser, setStoredToken, setStoredUser } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getStoredToken())
  const [user, setUser] = useState(() => getStoredUser())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    async function initAuth() {
      const storedToken = getStoredToken()
      if (!storedToken) {
        if (mounted) setLoading(false)
        return
      }

      try {
        const profile = await api.auth.getMe()
        if (mounted) {
          setUser(profile)
          setStoredUser(profile)
        }
      } catch (err) {
        // Token invalid or expired; clear credentials
        if (mounted) {
          setToken(null)
          setUser(null)
          setStoredToken(null)
          setStoredUser(null)
        }
      } finally {
        if (mounted) setLoading(false)
      }
    }

    initAuth()
    return () => {
      mounted = false
    }
  }, [])

  async function login(email, password) {
    const res = await api.auth.login({ email, password })
    const { access_token, user: loggedUser } = res
    setToken(access_token)
    setUser(loggedUser)
    setStoredToken(access_token)
    setStoredUser(loggedUser)
    return loggedUser
  }

  async function register(payload) {
    await api.auth.register(payload)
    // Automatically log in after registration
    return login(payload.email, payload.password)
  }

  async function logout() {
    try {
      await api.auth.logout()
    } catch {
      // Ignore network errors during logout
    } finally {
      setToken(null)
      setUser(null)
      setStoredToken(null)
      setStoredUser(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        isAuthenticated: Boolean(token && user),
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
