import { useRef, useState } from 'react'
import Header from './components/header.jsx'
import ChatWindow from './components/chatwindow.jsx'
import ChatInput from './components/chatinput.jsx'
import './App.css'

const API_URL = 'http://localhost:8000/api/ask'

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Hello! 👋 I am your assistant. How can I help you today?',
      time: getTime(),
    },
  ])
  const [isTyping, setIsTyping] = useState(false)
  const requestController = useRef(null)

  // Identifies this conversation. The backend uses it to find the bot's memory.
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID())

  async function handleSend(text) {
    const question = text.trim()
    if (!question || isTyping) return

    const controller = new AbortController()
    requestController.current = controller
    setMessages((prev) => [...prev, {
      id: crypto.randomUUID(),
      sender: 'user',
      text: question,
      time: getTime(),
    }])
    setIsTyping(true)

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: sessionId }),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      if (controller.signal.aborted) return
      setMessages((prev) => [...prev, {
        id: crypto.randomUUID(),
        sender: 'bot',
        text: data.answer,
        time: getTime(),
      }])
    } catch (error) {
      if (controller.signal.aborted) return
      console.error('Chat request failed:', error)
      setMessages((prev) => [...prev, {
        id: crypto.randomUUID(),
        sender: 'bot',
        text: 'Sorry, I could not reach the server. Please try again.',
        time: getTime(),
      }])
    } finally {
      if (!controller.signal.aborted) setIsTyping(false)
      if (requestController.current === controller) requestController.current = null
    }
  }

  function handleClear() {
    requestController.current?.abort()
    requestController.current = null
    setIsTyping(false)
    // A new session id = a brand new conversation, the bot forgets the old one
    setSessionId(crypto.randomUUID())
    setMessages([{
      id: crypto.randomUUID(),
      sender: 'bot',
      text: 'Conversation cleared. How can I help you?',
      time: getTime(),
    }])
  }

  return (
    <div className="app">
      <div className="chat-container">
        <Header onClear={handleClear} />
        <ChatWindow messages={messages} isTyping={isTyping} />
        <ChatInput onSend={handleSend} disabled={isTyping} />
      </div>
    </div>
  )
}

export default App