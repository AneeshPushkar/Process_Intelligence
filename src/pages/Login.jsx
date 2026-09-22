import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowRight, Lock, Mail } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import Button from '../components/ui/Button'
import Card, { CardBody, CardHeader } from '../components/ui/Card'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!email.trim() || !password) {
      setError('Please enter both email and password.')
      return
    }

    setSubmitting(true)
    try {
      await login(email.trim(), password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4 py-12 text-fg sm:px-6">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl border border-accent/30 bg-accent/10 text-lg font-bold text-accent">
            IQ
          </div>
          <h2 className="mt-4 text-2xl font-bold tracking-tight text-fg">Welcome to ProcessIQ</h2>
          <p className="mt-1 text-xs text-muted">
            AI-Powered Enterprise Process Intelligence Using Multi-Agent LLMs
          </p>
        </div>

        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-fg">Sign in to your account</h3>
            <p className="mt-0.5 text-xs text-muted">Enter your registered email and password</p>
          </CardHeader>
          <CardBody>
            {error && (
              <div className="mb-4 flex items-start gap-2.5 rounded-lg border border-warn/30 bg-warn/10 p-3 text-xs text-warn">
                <AlertCircle size={15} className="mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted" htmlFor="email">
                  Email Address
                </label>
                <div className="flex items-center gap-2 rounded-lg border border-line bg-canvas px-3 text-sm focus-within:border-accent">
                  <Mail size={15} className="text-faint" />
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted" htmlFor="password">
                  Password
                </label>
                <div className="flex items-center gap-2 rounded-lg border border-line bg-canvas px-3 text-sm focus-within:border-accent">
                  <Lock size={15} className="text-faint" />
                  <input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
                  />
                </div>
              </div>

              <Button type="submit" className="w-full justify-center" disabled={submitting}>
                {submitting ? 'Signing in...' : 'Sign in'}
                <ArrowRight size={15} />
              </Button>
            </form>

            <div className="mt-5 border-t border-line pt-4 text-center text-xs text-muted">
              Don't have an account?{' '}
              <Link to="/register" className="font-medium text-accent hover:underline">
                Create an account
              </Link>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
