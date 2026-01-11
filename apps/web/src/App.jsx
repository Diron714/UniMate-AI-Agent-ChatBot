import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ChatPage from './pages/ChatPage'
import LoginPage from './pages/LoginPage'
import { useAuthStore } from './store/authStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

// Protected Route Component
function ProtectedRoute({ children }) {
  const { token, user } = useAuthStore()

  // Only check state, don't fetch - loadUser is called once at app startup
  if (!token) {
    return <Navigate to="/login" replace />
  }

  // Optional: Show loading state if user data is still being fetched
  if (!user) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  return children
}

function App() {
  const { loadUser } = useAuthStore()

  useEffect(() => {
    // Load user on app mount if token exists
    loadUser()
  }, [loadUser])

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/chat" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App

