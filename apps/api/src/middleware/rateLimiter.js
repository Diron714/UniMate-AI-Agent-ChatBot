import rateLimit from 'express-rate-limit'
import crypto from 'crypto'

/**
 * Chat rate limiter - 30 requests per minute per user
 * Uses user ID from req.user (set by verifyToken middleware)
 * Falls back to IP + user-agent hash for edge cases
 */
export const chatRateLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 30, // 30 requests per minute
  message: {
    success: false,
    message: 'Too many chat requests. Please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Use user ID for rate limiting (more accurate than IP)
  // Fallback order: userId -> IP+UserAgent hash -> IP
  keyGenerator: (req) => {
    if (req.user && req.user._id) {
      return `user:${req.user._id.toString()}`
    }
    // Fallback: IP + user-agent hash for unauthenticated edge cases
    const userAgent = req.get('user-agent') || 'unknown'
    const uaHash = crypto.createHash('md5').update(userAgent).digest('hex').substring(0, 8)
    return `ip:${req.ip}:${uaHash}`
  },
  skip: (req) => {
    // Skip rate limiting for admin users
    return req.user && req.user.role === 'admin'
  },
})

/**
 * Auth rate limiter - 5 requests per 15 minutes per IP
 * Stricter limits for authentication endpoints
 */
export const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 requests per 15 minutes
  message: {
    success: false,
    message: 'Too many authentication attempts. Please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Use IP + user-agent hash for better tracking
  keyGenerator: (req) => {
    const userAgent = req.get('user-agent') || 'unknown'
    const uaHash = crypto.createHash('md5').update(userAgent).digest('hex').substring(0, 8)
    return `auth:${req.ip}:${uaHash}`
  },
})

/**
 * Global IP rate limiter - 100 requests per 15 minutes per IP
 * Catches abuse before it reaches specific endpoints
 */
export const globalRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per 15 minutes
  message: {
    success: false,
    message: 'Too many requests. Please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => {
    return req.ip
  },
})

