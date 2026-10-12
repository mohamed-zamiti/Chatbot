import './Header.css'

function Header({ onClear }) {
  return (
    <header className="header">
      <div className="header-left">
        <div className="header-avatar">
          <i className="bi bi-robot"></i>
          <span className="status-dot"></span>
        </div>
        <div className="header-info">
          <h1>AI Assistant</h1>
          <p>Online</p>
        </div>
      </div>

      <button className="header-btn" onClick={onClear} title="Clear conversation">
        <i className="bi bi-trash3"></i>
      </button>
    </header>
  )
}

export default Header