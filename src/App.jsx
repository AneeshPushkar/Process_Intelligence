import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ThemeProvider } from './hooks/useTheme'
import { AuthProvider } from './hooks/useAuth'
import ProtectedRoute from './components/auth/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'

import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import AnalyzeProcess from './pages/AnalyzeProcess'
import ProcessAnalysis from './pages/ProcessAnalysis'
import ProcessModel from './pages/ProcessModel'
import ProcessIntelligence from './pages/ProcessIntelligence'
import ProcessHistory from './pages/ProcessHistory'
import Settings from './pages/Settings'

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Application Routes */}
            <Route
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/analyze" element={<AnalyzeProcess />} />
              <Route path="/analysis" element={<ProcessAnalysis />} />
              <Route path="/process-analysis" element={<ProcessAnalysis />} />
              <Route path="/process-model" element={<ProcessModel />} />
              <Route path="/intelligence" element={<ProcessIntelligence />} />
              <Route path="/process-intelligence" element={<ProcessIntelligence />} />
              <Route path="/processes" element={<ProcessHistory />} />
              <Route path="/history" element={<ProcessHistory />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}
