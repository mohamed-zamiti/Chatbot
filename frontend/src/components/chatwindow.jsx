import { useEffect, useRef } from 'react'
import Message from './message.jsx'
import './ChatWindow.css'

function ChatWindow({ messages, isTyping }) {
  const bottomRef = useRef(null)

  // Auto-scroll to the latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <main className="chat-window">
      {messages.map((msg) => (
        <Message key={msg.id} sender={msg.sender} text={msg.text} time={msg.time} />
      ))}

      {isTyping && (
        <div className="message-row bot">
          <div className="avatar bot-avatar">
            <i className="bi bi-robot"></i>
          </div>
          <div className="typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      <div ref={bottomRef}></div>
    </main>
  )
}

export default ChatWindow