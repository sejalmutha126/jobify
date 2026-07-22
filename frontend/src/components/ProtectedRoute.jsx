import React from 'react'
import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children }) {
  /**
   * Check if user is authenticated by looking for access token
   * If not authenticated, redirect to login page
   */
  
  const accessToken = localStorage.getItem('access_token')
  const user = localStorage.getItem('user')

  if (!accessToken || !user) {
    // Not authenticated - redirect to login
    return <Navigate to="/login" replace />
  }

  // Authenticated - render the component
  return children
}