/**
 * Validates email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid
 */
export const validateEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return false
  }
  
  // RFC 5322 compliant email regex (simplified)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  
  // Additional checks
  if (email.length > 254) return false // Max email length
  if (email.includes('..')) return false // No consecutive dots
  
  return emailRegex.test(email.trim().toLowerCase())
}

/**
 * Validates password strength
 * Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 number
 * @param {string} password - Password to validate
 * @returns {boolean} - True if valid
 */
export const validatePassword = (password) => {
  if (!password || typeof password !== 'string') {
    return false
  }

  // Minimum 8 characters
  if (password.length < 8) {
    return false
  }

  // At least one uppercase letter
  if (!/[A-Z]/.test(password)) {
    return false
  }

  // At least one lowercase letter
  if (!/[a-z]/.test(password)) {
    return false
  }

  // At least one number
  if (!/\d/.test(password)) {
    return false
  }

  return true
}

/**
 * Sanitizes input to prevent XSS attacks
 * @param {string|any} input - Input to sanitize
 * @returns {string|any} - Sanitized input
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') {
    return input
  }
  
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
}

/**
 * Sanitizes object recursively
 * @param {object} obj - Object to sanitize
 * @returns {object} - Sanitized object
 */
export const sanitizeObject = (obj) => {
  if (obj === null || typeof obj !== 'object') {
    return sanitizeInput(obj)
  }

  if (Array.isArray(obj)) {
    return obj.map(item => sanitizeObject(item))
  }

  const sanitized = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      sanitized[key] = sanitizeObject(obj[key])
    }
  }
  return sanitized
}

