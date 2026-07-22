import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, CheckCircle, Clock, AlertCircle, Calendar, Briefcase, Loader } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [applications, setApplications] = useState([])
  const [weeklyData, setWeeklyData] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total_viewed: 0,
    total_applied: 0,
    this_week: 0,
  })

  useEffect(() => {
    fetchApplications()
  }, [])

  const fetchApplications = async () => {
    try {
      const response = await fetch('http://localhost:8000/jobs/applications')
      
      console.log('[Dashboard] Fetch response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('[Dashboard] Received data:', data)
        
        const appArray = Array.isArray(data) ? data : (data.applications || [])
        console.log('[Dashboard] Applications array:', appArray)
        console.log('[Dashboard] Total apps:', appArray.length)
        
        setApplications(appArray)
        
        // Calculate stats
        const viewed = appArray.length
        const applied = appArray.filter(a => a.status === 'applied').length
        const saved = appArray.filter(a => a.status === 'saved').length
        const thisWeek = appArray.filter(a => {
          const date = new Date(a.applied_date || a.created_at || Date.now())
          const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
          return date > weekAgo
        }).length
        
        console.log('[Dashboard] Stats:', { viewed, applied, saved, thisWeek })
        
        setStats({
          total_viewed: viewed,
          total_applied: applied,
          total_saved: saved,
          this_week: thisWeek,
        })
        
        // Generate weekly chart data
        generateWeeklyData(appArray)
      } else {
        console.error('[Dashboard] Response not ok:', response.status)
      }
      setLoading(false)
    } catch (error) {
      console.error('[Dashboard] Error fetching applications:', error)
      // Use demo data on error
      setApplications(getDemoApplications())
      setStats({
        total_viewed: 8,
        total_applied: 3,
        this_week: 5,
      })
      generateWeeklyData(getDemoApplications())
      setLoading(false)
    }
  }

  const generateWeeklyData = (apps) => {
    // Simple count of saved jobs
    const savedCount = apps.filter(a => a.status === 'saved').length
    
    // Simple data for chart
    const data = [
      { name: 'Saved Jobs', count: savedCount }
    ]
    
    setWeeklyData(data)
  }

  const getDemoApplications = () => [
    {
      id: 1,
      job_title: 'Senior Python Developer',
      company: 'Tech Corp',
      location: 'Bangalore',
      status: 'viewed',
      match_score: 85,
      applied_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 2,
      job_title: 'Full Stack Engineer',
      company: 'StartUp XYZ',
      location: 'Remote',
      status: 'applied',
      match_score: 72,
      applied_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: 3,
      job_title: 'React Developer',
      company: 'WebCo',
      location: 'Pune',
      status: 'viewed',
      match_score: 78,
      applied_date: new Date().toISOString()
    },
    {
      id: 4,
      job_title: 'DevOps Engineer',
      company: 'Cloud Inc',
      location: 'Mumbai',
      status: 'applied',
      match_score: 90,
      applied_date: new Date().toISOString()
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="animate-spin text-blue-600" size={40} />
      </div>
    )
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">📊 Dashboard</h1>
        <p className="text-slate-600">Track your job search progress and weekly activity</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm font-medium">Total Saved Jobs</p>
              <p className="text-4xl font-bold mt-2">{stats.total_saved}</p>
            </div>
            <CheckCircle size={40} className="opacity-30" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Jobs in Dashboard</p>
              <p className="text-4xl font-bold mt-2">{applications.length}</p>
            </div>
            <Briefcase size={40} className="opacity-30" />
          </div>
        </div>
      </div>

      {/* Job Status Chart */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-6">💾 Saved Jobs Count</h2>
        {weeklyData.length > 0 && weeklyData[0].count > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                formatter={(value) => `${value} saved`}
              />
              <Bar dataKey="count" fill="#fbbf24" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-600 text-lg">No saved jobs yet</p>
            <p className="text-slate-500 text-sm mt-2">Click "Save" on jobs in Search to see them here</p>
          </div>
        )}
      </div>

      {/* Saved Jobs Table */}
      <div className="bg-white rounded-xl shadow-lg">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-2xl font-bold text-slate-900">💾 My Saved Jobs</h2>
          <p className="text-slate-600 text-sm mt-1">Jobs you saved from the search</p>
        </div>
        
        {applications && applications.filter(a => a.status === 'saved').length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">#</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Job Title</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Company</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Location</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Match Score</th>
                </tr>
              </thead>
              <tbody>
                {applications.filter(a => a.status === 'saved').map((app, idx) => (
                  <tr key={idx} className="border-b border-slate-200 hover:bg-slate-50 transition">
                    <td className="px-6 py-4 text-sm font-semibold text-slate-900">💾 {idx + 1}</td>
                    <td className="px-6 py-4 text-sm text-slate-900 font-medium">{app.job_title || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-slate-700">{app.company || 'Unknown'}</td>
                    <td className="px-6 py-4 text-sm text-slate-700">{app.location || 'Remote'}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-slate-900">
                      {app.match_score ? `${app.match_score}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center">
            <Briefcase size={48} className="mx-auto text-slate-400 mb-4" />
            <p className="text-slate-600">No saved jobs yet. Go to Job Search and click "Save"!</p>
          </div>
        )}
      </div>
    </div>
  )
}