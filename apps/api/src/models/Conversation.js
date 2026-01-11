import mongoose from 'mongoose'

const messageSchema = new mongoose.Schema({
  role: {
    type: String,
    enum: ['user', 'assistant'],
    required: [true, 'Message role is required'],
  },
  content: {
    type: String,
    required: [true, 'Message content is required'],
    trim: true,
  },
  timestamp: {
    type: Date,
    default: Date.now,
    required: true,
  },
  sources: {
    type: [String],
    default: [],
  },
}, {
  _id: false, // Don't create _id for subdocuments
})

const conversationSchema = new mongoose.Schema(
  {
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: [true, 'User ID is required'],
      index: true,
    },
    sessionId: {
      type: String,
      required: [true, 'Session ID is required'],
      index: true,
    },
    messages: {
      type: [messageSchema],
      default: [],
    },
    context: {
      university: {
        type: String,
        default: '',
      },
      stage: {
        type: String,
        default: '',
      },
      preferences: {
        type: mongoose.Schema.Types.Mixed,
        default: {},
      },
    },
  },
  {
    timestamps: true, // Creates createdAt and updatedAt automatically
  }
)

// Indexes for faster queries
conversationSchema.index({ userId: 1, createdAt: -1 })
conversationSchema.index({ sessionId: 1 })
conversationSchema.index({ userId: 1, sessionId: 1 })
conversationSchema.index({ 'context.university': 1 })

// Virtual for message count
conversationSchema.virtual('messageCount').get(function() {
  return this.messages.length
})

// Method to get last message
conversationSchema.methods.getLastMessage = function() {
  return this.messages.length > 0 ? this.messages[this.messages.length - 1] : null
}

const Conversation = mongoose.model('Conversation', conversationSchema)

export default Conversation

