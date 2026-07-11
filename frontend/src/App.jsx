import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import { DatasetProvider } from './context/DatasetContext'
import Analytics from './pages/Analytics'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import Profile from './pages/Profile'
import Quality from './pages/Quality'
import Settings from './pages/Settings'
import Upload from './pages/Upload'
import Warehouse from './pages/Warehouse'
import './App.css'

function App() {
  return (
    <DatasetProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="upload" element={<Upload />} />
            <Route path="overview" element={<Profile />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="quality" element={<Quality />} />
            <Route path="warehouse" element={<Warehouse />} />
            <Route path="history" element={<History />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DatasetProvider>
  )
}

export default App
