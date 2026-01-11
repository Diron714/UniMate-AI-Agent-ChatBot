import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import mongoose from 'mongoose'
import connectDB from './src/config/db.js'
import authRoutes from './src/routes/authRoutes.js'
import chatRoutes from './src/routes/chatRoutes.js'
import adminRoutes from './src/routes/adminRoutes.js'
import { globalRateLimiter } from './src/middleware/rateLimiter.js'

// Load environment variables
dotenv.config()

const app = express()
const PORT = process.env.PORT || 5000

// Security: CORS configuration
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true,
  optionsSuccessStatus: 200,
}

app.use(cors(corsOptions))

// Body parser middleware with size limits
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true, limit: '10mb' }))

// Security: Remove X-Powered-By header
app.disable('x-powered-by')

// Middleware to clean URL paths (remove newlines and spaces)
app.use((req, res, next) => {
  // Clean the path from URL-encoded newlines and spaces
  if (req.url.includes('%0A') || req.url.includes('%0D')) {
    // Clean the URL (req.url is writable, req.path is read-only)
    const cleanUrl = req.url
      .replace(/%0A/g, '')
      .replace(/%0D/g, '')
      .trim()
    
    // Update the URL (this will automatically update req.path)
    req.url = cleanUrl
  }
  next()
})

// Global rate limiter (applied to all routes)
app.use(globalRateLimiter)

// Request logging middleware (development only)
if (process.env.NODE_ENV === 'development') {
  app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`)
    next()
  })
}

// Health check route
app.get('/', (req, res) => {
  res.json({ 
    message: 'UniMate API Server', 
    status: 'running',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  })
})

app.get('/health', (req, res) => {
  const dbStatus = mongoose.connection.readyState
  const dbStates = {
    0: 'disconnected',
    1: 'connected',
    2: 'connecting',
    3: 'disconnecting'
  }
  
  res.json({ 
    status: dbStatus === 1 ? 'healthy' : 'unhealthy',
    database: dbStates[dbStatus] || 'unknown',
    timestamp: new Date().toISOString(),
  })
})

// API Routes - Standardized under /api prefix
app.use('/api/auth', authRoutes)
app.use('/api/chat', chatRoutes)
app.use('/api/admin', adminRoutes)

// Error handling middleware (must be after routes)
app.use((err, req, res, next) => {
  console.error('Error:', err.stack)
  
  // Mongoose validation error
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      success: false,
      message: 'Validation error',
      errors: Object.values(err.errors).map(e => e.message),
    })
  }

  // Mongoose duplicate key error
  if (err.code === 11000) {
    return res.status(409).json({
      success: false,
      message: 'Duplicate entry',
      field: Object.keys(err.keyPattern)[0],
    })
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      success: false,
      message: 'Invalid token',
    })
  }

  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      success: false,
      message: 'Token expired',
    })
  }

  // Default error
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { error: err.stack }),
  })
})

// 404 handler (must be last)
app.use((req, res) => {
  // Clean the path (remove URL-encoded newlines and spaces)
  const cleanPath = req.path.replace(/%0A/g, '').replace(/%0D/g, '').trim()
  
  // Provide helpful hints for common mistakes
  let hint = null
  if (cleanPath === '/auth/register' && req.method === 'GET') {
    hint = 'This endpoint requires POST method, not GET. Change method to POST in Postman.'
  } else if (cleanPath === '/auth/login' && req.method === 'GET') {
    hint = 'This endpoint requires POST method, not GET. Change method to POST in Postman.'
  } else if (cleanPath === '/chat/send' && req.method === 'GET') {
    hint = 'This endpoint requires POST method, not GET. Change method to POST in Postman.'
  } else if (cleanPath !== req.path) {
    hint = 'URL contained invalid characters (newlines/spaces). Please check your request URL.'
  }
  
  res.status(404).json({ 
    success: false,
    message: 'Route not found',
    path: cleanPath,
    method: req.method,
    hint: hint,
  })
})

// Start server with database connection
const startServer = async () => {
  try {
    // Connect to database first
    await connectDB()
    
    // Start server after database connection
    app.listen(PORT, () => {
      console.log(`🚀 Server running on port ${PORT}`)
      console.log(`📝 Environment: ${process.env.NODE_ENV || 'development'}`)
      console.log(`🌐 CORS enabled for: ${corsOptions.origin}`)
    })
  } catch (error) {
    console.error('❌ Failed to start server:', error)
    process.exit(1)
  }
}

startServer()

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server')
  process.exit(0)
})

export default app

