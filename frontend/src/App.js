import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { NuqsAdapter } from 'nuqs/adapters/react-router'
import Login from './pages/Login'
import ProtectedRoute from './components/ProtectedRoute'
import Portal from './pages/Portal'
import ProfileSettings from './pages/ProfileSettings'

function App() {
  return (
    <BrowserRouter>
      <NuqsAdapter>
        <Routes>
          <Route path='/login' element={<Login />} />
          <Route
            path='/'
            element={
              <ProtectedRoute>
                <Portal />
              </ProtectedRoute>
            }
          />
          <Route
            path='/settings'
            element={
              <ProtectedRoute>
                <ProfileSettings />
              </ProtectedRoute>
            }
          />
          <Route path='*' element={<Navigate to='/' replace />} />
        </Routes>
      </NuqsAdapter>
    </BrowserRouter>
  )
}

export default App
