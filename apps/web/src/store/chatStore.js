import { create } from 'zustand'

export const useChatStore = create((set) => ({
  messages: [], // array of {role, content, timestamp, sources}
  isLoading: false,
  currentUniversity: null,
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, {
      role: message.role,
      content: message.content,
      timestamp: message.timestamp || new Date(),
      sources: message.sources || [],
    }],
  })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setUniversity: (university) => set({ currentUniversity: university }),
  
  clearMessages: () => set({ messages: [] }),
}))

