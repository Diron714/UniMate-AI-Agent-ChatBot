import express from 'express'
import { verifyToken, requireRole } from '../middleware/authMiddleware.js'

const router = express.Router()

// All admin routes require admin role
router.use(verifyToken)
router.use(requireRole('admin'))

router.get('/dashboard', (req, res) => {
  res.json({ message: 'Admin dashboard', user: req.user })
})

// Placeholder routes - will be implemented later
router.post('/documents/upload', (req, res) => {
  res.json({ message: 'Document upload endpoint - to be implemented' })
})

router.get('/cutoffs', (req, res) => {
  res.json({ message: 'Cut-off management - to be implemented' })
})

router.get('/logs', (req, res) => {
  res.json({ message: 'Logs viewer - to be implemented' })
})

export default router

