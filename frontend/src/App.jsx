import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Menu, X, Briefcase, FileText, Mail, Home, LogOut, User, BarChart3 } from 'lucide-react'

// Pages
import Login from './pages/Login'
import Signup from './pages/Signup'
import JobSearch from './pages/JobSearch'
import ResumeAnalyzer from './pages/ResumeAnalyzer'
import EmailAutomation from './pages/EmailAutomation'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'

// Components
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected Routes */}
        <Route
          path="/search"
          element={
            <ProtectedRoute>
              <MainApp defaultPage="search" />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analyzer"
          element={
            <ProtectedRoute>
              <MainApp defaultPage="analyzer" />
            </ProtectedRoute>
          }
        />
        <Route
          path="/email"
          element={
            <ProtectedRoute>
              <MainApp defaultPage="email" />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <MainApp defaultPage="dashboard" />
            </ProtectedRoute>
          }
        />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <MainApp defaultPage="home" />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <MainApp defaultPage="profile" />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

function MainApp({ defaultPage }) {
  const [currentPage, setCurrentPage] = useState(defaultPage || 'home')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [stats, setStats] = useState(null)
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Get user from localStorage
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'search', label: 'Search Jobs', icon: Briefcase },
    { id: 'analyzer', label: 'Resume Analyzer', icon: FileText },
    { id: 'email', label: 'Email Automation', icon: Mail },
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  ]

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'search':
        return <JobSearch />
      case 'analyzer':
        return <ResumeAnalyzer />
      case 'email':
        return <EmailAutomation />
      case 'dashboard':
        return <Dashboard />
      case 'profile':
        return <Profile />
      case 'home':
      default:
        return (
          <div className="text-center py-20">
            <h1 className="text-5xl font-bold text-slate-900 mb-4">Welcome to Jobify</h1>
            <p className="text-xl text-slate-600 mb-8">AI-powered job search platform</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <Briefcase className="text-blue-600 mb-4 mx-auto" size={40} />
                <h3 className="font-bold text-lg mb-2">Search Jobs</h3>
                <p className="text-slate-600 text-sm">Find jobs from Naukri and Indeed</p>
              </div>
              <div className="bg-white rounded-xl shadow-lg p-6">
                <FileText className="text-blue-600 mb-4 mx-auto" size={40} />
                <h3 className="font-bold text-lg mb-2">Analyze Resume</h3>
                <p className="text-slate-600 text-sm">Get AI-powered resume analysis</p>
              </div>
              <div className="bg-white rounded-xl shadow-lg p-6">
                <Mail className="text-blue-600 mb-4 mx-auto" size={40} />
                <h3 className="font-bold text-lg mb-2">Cold Email</h3>
                <p className="text-slate-600 text-sm">Generate personalized emails</p>
              </div>
            </div>
          </div>
        )
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-2 cursor-pointer" onClick={() => setCurrentPage('home')}>
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Briefcase className="text-white" size={24} />
              </div>
              <span className="text-xl font-bold gradient-text">Jobify</span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
                    currentPage === item.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <item.icon size={18} />
                  <span className="hidden sm:inline">{item.label}</span>
                </button>
              ))}
            </div>

            {/* User Menu & Logout */}
            <div className="flex items-center gap-4">
              {/* Profile Button */}
              <button
                onClick={() => setCurrentPage('profile')}
                className="hidden sm:flex items-center gap-2 px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-all"
                title={user?.full_name}
              >
                <User size={18} />
                <span className="text-sm font-medium">{user?.full_name?.split(' ')[0] || 'User'}</span>
              </button>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-all"
                title="Logout"
              >
                <LogOut size={18} />
                <span className="hidden sm:inline text-sm font-medium">Logout</span>
              </button>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 hover:bg-slate-100 rounded-lg"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-4 animate-slideInRight">
              {navItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => {
                    setCurrentPage(item.id)
                    setMobileMenuOpen(false)
                  }}
                  className={`block w-full text-left px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 ${
                    currentPage === item.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <item.icon size={18} />
                  {item.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </nav>

      {/* Page Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderPage()}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Briefcase className="text-blue-400" size={24} />
                <span className="text-xl font-bold text-white">Jobify</span>
              </div>
              <p className="text-sm">AI-powered job search platform making career transitions effortless.</p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Features</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-blue-400 transition">Job Search</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">Resume Analysis</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">Email Automation</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">Tracking</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Resources</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-blue-400 transition">Documentation</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">API</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">Support</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">Blog</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-blue-400 transition">Privacy</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">Terms</a></li>
                <li><a href="#" className="hover:text-blue-400 transition">Contact</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-700 pt-8 text-center text-sm">
            <p>&copy; 2024 Jobify. All rights reserved. Built with ❤️ for job seekers.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
export default App