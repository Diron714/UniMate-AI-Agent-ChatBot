import mongoose from 'mongoose'
import bcrypt from 'bcrypt'

const userSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^\S+@\S+\.\S+$/, 'Please provide a valid email'],
      index: true,
    },
    passwordHash: {
      type: String,
      required: [true, 'Password is required'],
      select: false, // Don't include in queries by default
    },
    role: {
      type: String,
      enum: ['student', 'admin'],
      default: 'student',
      required: true,
    },
    preferences: {
      language: {
        type: String,
        enum: ['en', 'si', 'ta'],
        default: 'en',
      },
      university: {
        type: String,
        default: '',
      },
      course: {
        type: String,
        default: '',
      },
    },
  },
  {
    timestamps: true, // Creates createdAt and updatedAt automatically
  }
)

// Index for faster queries
userSchema.index({ email: 1 })

// Method to compare password
userSchema.methods.comparePassword = async function (candidatePassword) {
  if (!candidatePassword) {
    return false
  }
  try {
    return await bcrypt.compare(candidatePassword, this.passwordHash)
  } catch (error) {
    console.error('Password comparison error:', error)
    return false
  }
}

// Remove password from JSON output
userSchema.methods.toJSON = function () {
  const obj = this.toObject()
  delete obj.passwordHash
  delete obj.__v
  return obj
}

const User = mongoose.model('User', userSchema)

export default User

