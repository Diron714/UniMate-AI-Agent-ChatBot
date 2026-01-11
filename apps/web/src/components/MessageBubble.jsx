import { FileText, ExternalLink } from 'lucide-react'

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const timestamp = message.timestamp ? new Date(message.timestamp) : new Date()

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} items-start space-x-2`}>
      {!isUser && (
        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-sm">🤖</span>
        </div>
      )}
      <div
        className={`max-w-3xl rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-primary-600 text-white'
            : 'bg-white text-gray-800 shadow-sm border border-gray-200'
        }`}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        
        {message.sources && message.sources.length > 0 && (
          <div className={`mt-3 pt-3 ${isUser ? 'border-primary-400' : 'border-gray-200'} border-t`}>
            <div className="flex items-start space-x-1 mb-2">
              <FileText size={14} className={isUser ? 'text-primary-200' : 'text-gray-400 mt-0.5'} />
              <span className={`text-xs font-medium ${isUser ? 'text-primary-200' : 'text-gray-600'}`}>
                Sources:
              </span>
            </div>
            <div className="space-y-1">
              {message.sources.map((source, index) => (
                <div
                  key={index}
                  className={`text-xs flex items-center space-x-1 ${
                    isUser ? 'text-primary-100' : 'text-gray-500'
                  }`}
                >
                  <ExternalLink size={12} />
                  <span className="hover:underline">{source}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <p className={`text-xs mt-2 ${isUser ? 'text-primary-200' : 'text-gray-400'}`}>
          {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
      {isUser && (
        <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
          <span className="text-white text-xs font-medium">U</span>
        </div>
      )}
    </div>
  )
}

export default MessageBubble

