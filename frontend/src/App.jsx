import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import PageSkeleton from './components/Skeleton'
import { DatasetProvider } from './context/DatasetContext'
import { ToastProvider } from './context/ToastContext'
import './App.css'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Upload = lazy(() => import('./pages/Upload'))
const Profile = lazy(() => import('./pages/Profile'))
const Analytics = lazy(() => import('./pages/Analytics'))
const Quality = lazy(() => import('./pages/Quality'))
const Warehouse = lazy(() => import('./pages/Warehouse'))
const History = lazy(() => import('./pages/History'))
const Settings = lazy(() => import('./pages/Settings'))

function RouteFallback() {
  return <PageSkeleton cards={4} label="Loading page…" />
}

function App() {
  // Vite `base` → import.meta.env.BASE_URL (e.g. "/" or "/dataforge/")
  const basename =
    import.meta.env.BASE_URL === '/'
      ? undefined
      : import.meta.env.BASE_URL.replace(/\/$/, '')

  return (
    <DatasetProvider>
      <ToastProvider>
        <BrowserRouter basename={basename}>
          <Suspense fallback={<RouteFallback />}>
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
          </Suspense>
        </BrowserRouter>
      </ToastProvider>
    </DatasetProvider>
  )
}

export default App
