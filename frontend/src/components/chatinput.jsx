import { useState } from 'react'
import './ChatInput.css'

function ChatInput({ onSend, disabled }) {
  // What the user is currently typing
  const [text, setText] = useState('')

  function handleSubmit(e) {
    e.preventDefault() // stop the page from reloading
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Type your message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button type="submit" disabled={!text.trim() || disabled} title="Send">
        <i className="bi bi-send-fill"></i>
      </button>
    </form>
  )
}

export default ChatInput