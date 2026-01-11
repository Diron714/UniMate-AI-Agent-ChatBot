import express from 'express'
import { sendMessage, getHistory, deleteConversation } from '../controllers/chatController.js'
import { verifyToken } from '../middleware/authMiddleware.js'
import { chatRateLimiter } from '../middleware/rateLimiter.js'

const router = express.Router()

// POST /chat/send - Send a message (protected, rate limited)
router.post('/send', verifyToken, chatRateLimiter, sendMessage)

// GET /chat/history - Get chat history (protected, paginated)
router.get('/history', verifyToken, getHistory)

// DELETE /chat/history/:id - Delete a conversation (protected)
router.delete('/history/:id', verifyToken, deleteConversation)

export default router

