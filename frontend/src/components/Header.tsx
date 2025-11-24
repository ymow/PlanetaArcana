import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="bg-tarot-primary/30 backdrop-blur-md border-b border-tarot-accent/20">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-3xl">🔮</span>
            <h1 className="text-2xl font-bold text-tarot-gold mystical-font">
              Planeta Arcana
            </h1>
          </Link>

          <div className="flex space-x-6">
            <Link
              to="/"
              className="text-tarot-light hover:text-tarot-accent transition"
            >
              首頁
            </Link>
            <Link
              to="/divine"
              className="text-tarot-light hover:text-tarot-accent transition"
            >
              開始占卜
            </Link>
            <Link
              to="/history"
              className="text-tarot-light hover:text-tarot-accent transition"
            >
              歷史記錄
            </Link>
          </div>
        </div>
      </nav>
    </header>
  )
}
