import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Topbar } from './components/Topbar'
import { CallDetail } from './pages/CallDetail'
import { CallList } from './pages/CallList'
import { CoachingQueue } from './pages/CoachingQueue'
import { ComplianceQueue } from './pages/ComplianceQueue'
import { DisagreementLog } from './pages/DisagreementLog'

function App() {
  return (
    <BrowserRouter>
      <Topbar />
      <Routes>
        <Route path="/" element={<CallList />} />
        <Route path="/calls/:callId" element={<CallDetail />} />
        <Route path="/queue/coaching" element={<CoachingQueue />} />
        <Route path="/queue/compliance" element={<ComplianceQueue />} />
        <Route path="/disagreements" element={<DisagreementLog />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
