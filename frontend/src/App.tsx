import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DivinePage from './pages/DivinePage'
import InterpretationPage from './pages/InterpretationPage'
import HistoryPage from './pages/HistoryPage'
import DailyDrawPage from './pages/DailyDrawPage'
import CardVisualLabPage from './pages/CardVisualLabPage'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-tarot-dark via-purple-900 to-tarot-dark">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/daily" element={<DailyDrawPage />} />
          <Route path="/divine" element={<DivinePage />} />
          <Route path="/divine/:id" element={<InterpretationPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/visual-lab" element={<CardVisualLabPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
