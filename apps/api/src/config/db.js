import mongoose from 'mongoose'

const connectDB = async () => {
  try {
    // Check if MongoDB URI is provided
    if (!process.env.MONGODB_URI) {
      console.error('❌ MONGODB_URI is not defined in environment variables')
      throw new Error('MONGODB_URI is not defined')
    }

    // Check if already connected
    if (mongoose.connection.readyState === 1) {
      console.log('✅ MongoDB already connected')
      return mongoose.connection
    }

    const options = {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 10000, // Increased to 10s for better reliability
      socketTimeoutMS: 45000, // Close sockets after 45s of inactivity
    }

    console.log('🔄 Connecting to MongoDB...')
    const conn = await mongoose.connect(process.env.MONGODB_URI, options)

    console.log(`✅ MongoDB Connected: ${conn.connection.host}`)
    console.log(`📊 Database: ${conn.connection.name}`)

    // Handle connection events
    mongoose.connection.on('error', (err) => {
      console.error('❌ MongoDB connection error:', err)
    })

    mongoose.connection.on('disconnected', () => {
      console.warn('⚠️  MongoDB disconnected')
    })

    mongoose.connection.on('reconnected', () => {
      console.log('✅ MongoDB reconnected')
    })

    // Graceful shutdown
    process.on('SIGINT', async () => {
      await mongoose.connection.close()
      console.log('MongoDB connection closed due to app termination')
      process.exit(0)
    })

  } catch (error) {
    console.error(`❌ MongoDB connection error: ${error.message}`)
    
    // Provide helpful error messages
    if (error.message.includes('authentication failed')) {
      console.error('💡 Check your MongoDB username and password in .env')
    } else if (error.message.includes('ENOTFOUND') || error.message.includes('getaddrinfo')) {
      console.error('💡 Check your internet connection and MongoDB cluster URL')
    } else if (error.message.includes('timeout')) {
      console.error('💡 Connection timeout - check your network or MongoDB cluster status')
    }
    
    // Re-throw error so server startup can handle it
    throw error
  }
}

export default connectDB

