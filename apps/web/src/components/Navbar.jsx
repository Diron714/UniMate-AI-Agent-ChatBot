import { User, LogOut } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useChatStore } from '../store/chatStore'

function Navbar() {
  const { user, logout } = useAuthStore()
  const { currentUniversity } = useChatStore()

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">U</span>
              </div>
              <h1 className="text-xl font-bold text-primary-600">UniMate AI Agent</h1>
            </div>
            {currentUniversity && (
              <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                🎓 {currentUniversity}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <User size={16} className="text-primary-600" />
                </div>
                <span className="hidden sm:inline">{user.email}</span>
              </div>
            )}
            <button
              onClick={logout}
              className="btn-secondary text-sm flex items-center space-x-1 hover:bg-gray-300 transition-colors"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

