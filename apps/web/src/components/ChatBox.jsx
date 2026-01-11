import { useState, useRef } from 'react'
import { Send, Paperclip, X } from 'lucide-react'
import { useChatStore } from '../store/chatStore'
import { sendMessage } from '../utils/api'

const MAX_CHARACTERS = 2000

function ChatBox() {
  const [input, setInput] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)
  const { addMessage, setLoading, isLoading } = useChatStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    addMessage(userMessage)
    const messageToSend = input
    setInput('')
    setLoading(true)

    try {
      const response = await sendMessage(messageToSend, {})
      const aiMessage = {
        role: 'assistant',
        content: response.message || response.response || response.content || 'No response received',
        sources: response.sources || [],
        timestamp: new Date(),
      }
      addMessage(aiMessage)
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = {
        role: 'assistant',
        content: error.response?.data?.message || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      addMessage(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      // For now, just store the file reference
      // Future: implement file upload functionality
      setSelectedFile(file)
      console.log('File selected:', file.name)
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const characterCount = input.length
  const isNearLimit = characterCount > MAX_CHARACTERS * 0.9

  return (
    <div className="bg-white border-t border-gray-200 px-4 py-4">
      <div className="max-w-4xl mx-auto">
        {selectedFile && (
          <div className="mb-2 flex items-center justify-between bg-primary-50 px-3 py-2 rounded-lg">
            <div className="flex items-center space-x-2">
              <Paperclip size={16} className="text-primary-600" />
              <span className="text-sm text-primary-700">{selectedFile.name}</span>
            </div>
            <button
              onClick={handleRemoveFile}
              className="text-primary-600 hover:text-primary-800"
              disabled={isLoading}
            >
              <X size={16} />
            </button>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => {
                if (e.target.value.length <= MAX_CHARACTERS) {
                  setInput(e.target.value)
                }
              }}
              placeholder="Ask UniMate anything about universities..."
              className="input-field pr-20"
              disabled={isLoading}
              maxLength={MAX_CHARACTERS}
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center space-x-2">
              <span className={`text-xs ${isNearLimit ? 'text-red-500' : 'text-gray-400'}`}>
                {characterCount}/{MAX_CHARACTERS}
              </span>
            </div>
          </div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
            accept=".pdf,.doc,.docx,.txt"
            disabled={isLoading}
          />
          <label
            htmlFor="file-upload"
            className={`btn-secondary px-4 py-2 flex items-center justify-center cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-300'}`}
          >
            <Paperclip size={20} />
          </label>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Send size={20} />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatBox

