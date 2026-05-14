import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Topbar } from './components/Topbar'
import { CallDetail } from './pages/CallDetail'
import { CallList } from './pages/CallList'

function App() {
  return (
    <BrowserRouter>
      <Topbar />
      <Routes>
        <Route path="/" element={<CallList />} />
        <Route path="/calls/:callId" element={<CallDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
