import express from 'express'
import { register, login, refresh, getMe } from '../controllers/authController.js'
import { verifyToken } from '../middleware/authMiddleware.js'
import { authRateLimiter } from '../middleware/rateLimiter.js'

const router = express.Router()

router.post('/register', authRateLimiter, register)
router.post('/login', authRateLimiter, login)
router.post('/refresh', refresh)
router.get('/me', verifyToken, getMe)

export default router

