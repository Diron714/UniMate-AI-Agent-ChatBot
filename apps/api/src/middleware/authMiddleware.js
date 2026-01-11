import jwt from 'jsonwebtoken'
import User from '../models/User.js'

export const verifyToken = async (req, res, next) => {
  try {
    // Check for token in Authorization header
    const authHeader = req.headers.authorization
    
    if (!authHeader) {
      return res.status(401).json({ 
        success: false,
        message: 'No authorization header provided' 
      })
    }

    // Extract token from "Bearer <token>"
    const token = authHeader.startsWith('Bearer ') 
      ? authHeader.slice(7) 
      : authHeader

    if (!token) {
      return res.status(401).json({ 
        success: false,
        message: 'No token provided' 
      })
    }

    if (!process.env.JWT_SECRET) {
      console.error('JWT_SECRET is not configured')
      return res.status(500).json({ 
        success: false,
        message: 'Server configuration error' 
      })
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    
    // Find user (exclude passwordHash)
    const user = await User.findById(decoded.userId).select('-passwordHash')

    if (!user) {
      return res.status(401).json({ 
        success: false,
        message: 'User not found' 
      })
    }

    // Attach user to request
    req.user = user
    next()
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ 
        success: false,
        message: 'Invalid token' 
      })
    }
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ 
        success: false,
        message: 'Token expired' 
      })
    }
    console.error('Token verification error:', error)
    res.status(500).json({ 
      success: false,
      message: 'Authentication error',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    })
  }
}

export const requireRole = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        success: false,
        message: 'Authentication required' 
      })
    }

    if (!roles || roles.length === 0) {
      return next()
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ 
        success: false,
        message: 'Insufficient permissions. Required role: ' + roles.join(' or ') 
      })
    }

    next()
  }
}

