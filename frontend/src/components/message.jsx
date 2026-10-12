import './Message.css'

// sender is either "user" or "bot"
function Message({ sender, text, time }) {
  const isUser = sender === 'user'

  return (
    <div className={`message-row ${sender}`}>
      <div className={`avatar ${isUser ? 'user-avatar' : 'bot-avatar'}`}>
        <i className={`bi ${isUser ? 'bi-person-fill' : 'bi-robot'}`}></i>
      </div>

      <div className="bubble-wrapper">
        <div className="bubble">{text}</div>
        <span className="time">{time}</span>
      </div>
    </div>
  )
}

export default Message