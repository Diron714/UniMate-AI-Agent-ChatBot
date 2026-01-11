import bcrypt from 'bcrypt'
import jwt from 'jsonwebtoken'
import User from '../models/User.js'
import { validateEmail, validatePassword } from '../utils/validation.js'

const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET, {
    expiresIn: '7d',
  })
}

const generateRefreshToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_REFRESH_SECRET, {
    expiresIn: '30d',
  })
}

export const register = async (req, res) => {
  try {
    const { email, password } = req.body

    // Validation
    if (!email || !password) {
      return res.status(400).json({ 
        success: false,
        message: 'Email and password are required' 
      })
    }

    // Sanitize input
    const sanitizedEmail = email.trim().toLowerCase()

    if (!validateEmail(sanitizedEmail)) {
      return res.status(400).json({ 
        success: false,
        message: 'Invalid email format' 
      })
    }

    if (!validatePassword(password)) {
      return res.status(400).json({
        success: false,
        message: 'Password must be at least 8 characters with at least one uppercase letter, one lowercase letter, and one number',
      })
    }

    // Check if user exists
    const existingUser = await User.findOne({ email: sanitizedEmail })
    if (existingUser) {
      return res.status(409).json({ 
        success: false,
        message: 'User with this email already exists' 
      })
    }

    // Hash password
    const saltRounds = 10
    const passwordHash = await bcrypt.hash(password, saltRounds)

    // Create user
    const user = await User.create({
      email: sanitizedEmail,
      passwordHash,
      role: 'student',
      preferences: {
        language: 'en',
        university: '',
        course: '',
      },
    })

    // Generate tokens
    const token = generateToken(user._id)
    const refreshToken = generateRefreshToken(user._id)

    res.status(201).json({
      success: true,
      message: 'User created successfully',
      token,
      refreshToken,
      user: user.toJSON(),
    })
  } catch (error) {
    console.error('Register error:', error)
    
    // Handle duplicate key error
    if (error.code === 11000) {
      return res.status(409).json({ 
        success: false,
        message: 'User with this email already exists' 
      })
    }
    
    // Handle validation errors
    if (error.name === 'ValidationError') {
      return res.status(400).json({ 
        success: false,
        message: Object.values(error.errors).map(e => e.message).join(', ')
      })
    }
    
    res.status(500).json({ 
      success: false,
      message: 'Registration failed',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    })
  }
}

export const login = async (req, res) => {
  try {
    const { email, password } = req.body

    if (!email || !password) {
      return res.status(400).json({ 
        success: false,
        message: 'Email and password are required' 
      })
    }

    // Sanitize email
    const sanitizedEmail = email.trim().toLowerCase()

    // Find user (include passwordHash for comparison)
    const user = await User.findOne({ email: sanitizedEmail }).select('+passwordHash')
    if (!user) {
      return res.status(401).json({ 
        success: false,
        message: 'Invalid email or password' 
      })
    }

    // Check password
    const isPasswordValid = await user.comparePassword(password)
    if (!isPasswordValid) {
      return res.status(401).json({ 
        success: false,
        message: 'Invalid email or password' 
      })
    }

    // Generate tokens
    const token = generateToken(user._id)
    const refreshToken = generateRefreshToken(user._id)

    res.json({
      success: true,
      message: 'Login successful',
      token,
      refreshToken,
      user: user.toJSON(),
    })
  } catch (error) {
    console.error('Login error:', error)
    res.status(500).json({ 
      success: false,
      message: 'Login failed',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    })
  }
}

export const refresh = async (req, res) => {
  try {
    const { refreshToken } = req.body

    if (!refreshToken) {
      return res.status(400).json({ 
        success: false,
        message: 'Refresh token is required' 
      })
    }

    if (!process.env.JWT_REFRESH_SECRET) {
      console.error('JWT_REFRESH_SECRET is not configured')
      return res.status(500).json({ 
        success: false,
        message: 'Server configuration error' 
      })
    }

    const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET)
    const user = await User.findById(decoded.userId)

    if (!user) {
      return res.status(401).json({ 
        success: false,
        message: 'User not found' 
      })
    }

    const token = generateToken(user._id)
    const newRefreshToken = generateRefreshToken(user._id)

    res.json({
      success: true,
      token,
      refreshToken: newRefreshToken,
    })
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ 
        success: false,
        message: 'Invalid refresh token' 
      })
    }
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ 
        success: false,
        message: 'Refresh token expired' 
      })
    }
    console.error('Refresh token error:', error)
    res.status(401).json({ 
      success: false,
      message: 'Invalid refresh token' 
    })
  }
}

export const getMe = async (req, res) => {
  try {
    if (!req.user || !req.user._id) {
      return res.status(401).json({ 
        success: false,
        message: 'User not authenticated' 
      })
    }

    const user = await User.findById(req.user._id)
    
    if (!user) {
      return res.status(404).json({ 
        success: false,
        message: 'User not found' 
      })
    }

    res.json({
      success: true,
      user: user.toJSON(),
    })
  } catch (error) {
    console.error('GetMe error:', error)
    res.status(500).json({ 
      success: false,
      message: 'Failed to get user profile',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    })
  }
}

