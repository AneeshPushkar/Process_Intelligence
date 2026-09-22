import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowRight, Building, Lock, Mail, User } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import Button from '../components/ui/Button'
import Card, { CardBody, CardHeader } from '../components/ui/Card'

export default function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [organization, setOrganization] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const { register } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!fullName.trim() || !email.trim() || !password) {
      setError('Please fill in all required fields.')
      return
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setSubmitting(true)
    try {
      await register({
        full_name: fullName.trim(),
        email: email.trim(),
        organization: organization.trim() || undefined,
        password,
      })
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.')
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
          <h2 className="mt-4 text-2xl font-bold tracking-tight text-fg">Register for ProcessIQ</h2>
          <p className="mt-1 text-xs text-muted">Create an account to start analyzing enterprise workflows</p>
        </div>

        <Card>
          <CardHeader>
            <h3 className="text-sm font-semibold text-fg">Create new account</h3>
            <p className="mt-0.5 text-xs text-muted">All processes will be isolated to your user account</p>
          </CardHeader>
          <CardBody>
            {error && (
              <div className="mb-4 flex items-start gap-2.5 rounded-lg border border-warn/30 bg-warn/10 p-3 text-xs text-warn">
                <AlertCircle size={15} className="mt-0.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3.5">
              <div className="space-y-1">
                <label className="text-xs font-medium text-muted" htmlFor="fullName">
                  Full Name
                </label>
                <div className="flex items-center gap-2 rounded-lg border border-line bg-canvas px-3 text-sm focus-within:border-accent">
                  <User size={15} className="text-faint" />
                  <input
                    id="fullName"
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Jane Doe"
                    className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-muted" htmlFor="email">
                  Email Address
                </label>
                <div className="flex items-center gap-2 rounded-lg border border-line bg-canvas px-3 text-sm focus-within:border-accent">
                  <Mail size={15} className="text-faint" />
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="jane@company.com"
                    className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-muted" htmlFor="organization">
                  Organization (Optional)
                </label>
                <div className="flex items-center gap-2 rounded-lg border border-line bg-canvas px-3 text-sm focus-within:border-accent">
                  <Building size={15} className="text-faint" />
                  <input
                    id="organization"
                    type="text"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    placeholder="Acme Operations"
                    className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-muted" htmlFor="password">
                  Password
                </label>
                <div className="flex items-center gap-2 rounded-lg border border-line bg-canvas px-3 text-sm focus-within:border-accent">
                  <Lock size={15} className="text-faint" />
                  <input
                    id="password"
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-muted" htmlFor="confirmPassword">
                  Confirm Password
                </label>
                <div className="flex items-center gap-2 rounded-lg border border-line bg-canvas px-3 text-sm focus-within:border-accent">
                  <Lock size={15} className="text-faint" />
                  <input
                    id="confirmPassword"
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat your password"
                    className="h-10 w-full bg-transparent text-sm text-fg outline-none placeholder:text-faint"
                  />
                </div>
              </div>

              <Button type="submit" className="w-full justify-center pt-2" disabled={submitting}>
                {submitting ? 'Creating account...' : 'Create account'}
                <ArrowRight size={15} />
              </Button>
            </form>

            <div className="mt-5 border-t border-line pt-4 text-center text-xs text-muted">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-accent hover:underline">
                Sign in
              </Link>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
