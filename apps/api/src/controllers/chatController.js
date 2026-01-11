import axios from 'axios'
import Conversation from '../models/Conversation.js'

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000'
const AI_SERVICE_TIMEOUT = 30000 // 30 seconds

/**
 * Send message to AI service and store conversation
 */
export const sendMessage = async (req, res) => {
  const startTime = Date.now()
  const userId = req.user._id
  const userEmail = req.user.email

  try {
    // Validate JWT (already done by middleware, but double-check)
    if (!req.user || !userId) {
      return res.status(401).json({
        success: false,
        message: 'User not authenticated',
      })
    }

    // Extract message and context from request
    const { message, context = {} } = req.body

    // Validate message
    if (!message || typeof message !== 'string' || !message.trim()) {
      return res.status(400).json({
        success: false,
        message: 'Message is required and must be a non-empty string',
      })
    }

    const trimmedMessage = message.trim()

    // Log request
    console.log(`[Chat] User ${userEmail} sending message: ${trimmedMessage.substring(0, 50)}...`)

    // Get or create conversation with sessionId
    // Find conversation by userId and sessionId (if provided) for better session management
    let conversation
    if (context.sessionId) {
      conversation = await Conversation.findOne({ 
        userId, 
        sessionId: context.sessionId 
      })
    } else {
      // Fallback: find any conversation for user (for backward compatibility)
      conversation = await Conversation.findOne({ userId })
    }
    
    // Generate sessionId if new conversation, otherwise reuse existing
    let sessionId
    if (!conversation) {
      // Create new conversation with new sessionId
      sessionId = context.sessionId || `session_${userId.toString()}_${Date.now()}`
      conversation = new Conversation({
        userId,
        sessionId,
        messages: [],
        context: {
          university: context.university || '',
          stage: context.stage || '',
          preferences: context.preferences || {},
        },
      })
    } else {
      // Reuse existing sessionId
      sessionId = conversation.sessionId
    }

    // Prepare conversation history for AI service (last 10 messages)
    const conversationHistory = conversation.messages.slice(-10).map(msg => ({
      role: msg.role,
      content: msg.content,
    }))

    // Forward to AI service with timeout handling
    let aiResponse
    try {
      const response = await axios.post(
        `${AI_SERVICE_URL}/ai/chat`,
        {
          message: trimmedMessage,
          context: {
            university: context.university || '',
            stage: context.stage || '',
            preferences: context.preferences || {},
            conversation_history: conversationHistory, // Pass history from backend
          },
          userId: userId.toString(),
          sessionId: sessionId,
        },
        {
          timeout: AI_SERVICE_TIMEOUT,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )
      aiResponse = response.data
      console.log(`[Chat] AI service responded in ${Date.now() - startTime}ms`)
    } catch (error) {
      const errorTime = Date.now() - startTime
      
      // Handle different types of errors
      if (error.code === 'ECONNREFUSED') {
        console.error(`[Chat] AI service connection refused after ${errorTime}ms`)
        return res.status(503).json({
          success: false,
          message: 'AI service is not available. Please try again later.',
          error: 'Service unavailable',
        })
      }
      
      if (error.code === 'ETIMEDOUT' || error.message.includes('timeout')) {
        console.error(`[Chat] AI service timeout after ${errorTime}ms`)
        return res.status(504).json({
          success: false,
          message: 'AI service request timed out. Please try again.',
          error: 'Request timeout',
        })
      }

      if (error.response) {
        // AI service returned an error response - normalize to prevent error leakage
        const statusCode = error.response.status || 500
        const errorMessage = error.response.data?.message || 'AI service returned an error'
        console.error(`[Chat] AI service error: ${statusCode} - ${errorMessage}`)
        
        // Map AI service errors to user-friendly messages
        let userMessage = 'AI service is temporarily unavailable. Please try again later.'
        if (statusCode === 400) {
          userMessage = 'Invalid request to AI service. Please check your message.'
        } else if (statusCode === 429) {
          userMessage = 'AI service is rate limited. Please try again in a moment.'
        } else if (statusCode >= 500) {
          userMessage = 'AI service is experiencing issues. Please try again later.'
        }
        
        return res.status(statusCode).json({
          success: false,
          message: userMessage,
        })
      }

      // Unknown error - normalize to prevent error leakage
      console.error(`[Chat] AI service error after ${errorTime}ms:`, error.message)
      return res.status(503).json({
        success: false,
        message: 'AI service is temporarily unavailable. Please try again later.',
      })
    }

    // Add user message to conversation (before AI call for history)
    conversation.messages.push({
      role: 'user',
      content: trimmedMessage,
      timestamp: new Date(),
    })
    
    // Update context if provided
    if (context.university) conversation.context.university = context.university
    if (context.stage) conversation.context.stage = context.stage
    if (context.preferences) {
      conversation.context.preferences = {
        ...conversation.context.preferences,
        ...context.preferences,
      }
    }

    // Save user message first (for conversation continuity)
    await conversation.save()

    // Add AI response to conversation
    const aiMessageContent = aiResponse.message || aiResponse.response || aiResponse.content || 'No response received'
    conversation.messages.push({
      role: 'assistant',
      content: aiMessageContent,
      sources: aiResponse.sources || [],
      timestamp: new Date(),
    })

    // Save conversation with AI response
    await conversation.save()

    const totalTime = Date.now() - startTime
    console.log(`[Chat] Conversation saved for user ${userEmail} in ${totalTime}ms`)

    // Return AI response to frontend
    res.json({
      success: true,
      message: aiMessageContent,
      sources: aiResponse.sources || [],
      context: aiResponse.context || conversation.context,
    })
  } catch (error) {
    const totalTime = Date.now() - startTime
    console.error(`[Chat] Error processing message for user ${userEmail} after ${totalTime}ms:`, error)
    
    res.status(500).json({
      success: false,
      message: 'Failed to process message',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    })
  }
}

/**
 * Get chat history with pagination
 */
export const getHistory = async (req, res) => {
  try {
    // Validate JWT (already done by middleware)
    if (!req.user || !req.user._id) {
      return res.status(401).json({
        success: false,
        message: 'User not authenticated',
      })
    }

    const userId = req.user._id
    const page = Math.max(1, parseInt(req.query.page) || 1)
    const limit = Math.min(50, Math.max(1, parseInt(req.query.limit) || 20))
    const skip = (page - 1) * limit

    // Get conversations with pagination
    const conversations = await Conversation.find({ userId })
      .sort({ updatedAt: -1 })
      .limit(limit)
      .skip(skip)
      .select('messages context createdAt updatedAt')
      .lean()

    const total = await Conversation.countDocuments({ userId })

    console.log(`[Chat] Retrieved ${conversations.length} conversations for user ${req.user.email} (page ${page})`)

    res.json({
      success: true,
      conversations,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
        hasMore: page * limit < total,
      },
    })
  } catch (error) {
    console.error('[Chat] Error getting history:', error)
    res.status(500).json({
      success: false,
      message: 'Failed to get chat history',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    })
  }
}

/**
 * Delete a conversation by ID
 */
export const deleteConversation = async (req, res) => {
  try {
    // Validate JWT (already done by middleware)
    if (!req.user || !req.user._id) {
      return res.status(401).json({
        success: false,
        message: 'User not authenticated',
      })
    }

    const userId = req.user._id
    const conversationId = req.params.id

    // Validate conversation ID
    if (!conversationId || !conversationId.match(/^[0-9a-fA-F]{24}$/)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid conversation ID',
      })
    }

    // Find and delete conversation (only if it belongs to the user)
    const conversation = await Conversation.findOneAndDelete({
      _id: conversationId,
      userId, // Ensure user owns this conversation
    })

    if (!conversation) {
      return res.status(404).json({
        success: false,
        message: 'Conversation not found or you do not have permission to delete it',
      })
    }

    // Note: sessionId is cleared when conversation is deleted
    // This ensures AI memory is reset for new conversations
    console.log(`[Chat] Deleted conversation ${conversationId} (sessionId: ${conversation.sessionId}) for user ${req.user.email}`)

    res.json({
      success: true,
      message: 'Conversation deleted successfully',
    })
  } catch (error) {
    console.error('[Chat] Error deleting conversation:', error)
    res.status(500).json({
      success: false,
      message: 'Failed to delete conversation',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    })
  }
}

