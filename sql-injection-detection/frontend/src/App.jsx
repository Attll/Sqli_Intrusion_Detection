import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Demo from './pages/Demo'
import Analytics from './pages/Analytics'
import Logs from './pages/Logs'
import Models from './pages/Models'
import Settings from './pages/Settings'
import StressTest from './pages/StressTest'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="demo" element={<Demo />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="logs" element={<Logs />} />
          <Route path="models" element={<Models />} />
          <Route path="stress-test" element={<StressTest />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
