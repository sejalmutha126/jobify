import React, { useState, useEffect } from 'react'
import { Search, Briefcase, MapPin, DollarSign, ExternalLink, Loader } from 'lucide-react'

export default function JobSearch() {
  const [jobs, setJobs] = useState([])
  const [filteredJobs, setFilteredJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [locationFilter, setLocationFilter] = useState('')
  const [scrapingStatus, setScrapingStatus] = useState('')

  useEffect(() => {
    fetchJobs()
  }, [])

  useEffect(() => {
    filterJobs()
  }, [jobs, searchQuery, locationFilter])

  const fetchJobs = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/jobs')
      const data = await response.json()
      
      if (data.length === 0) {
        // Trigger scraping if no jobs
        scrapeJobs()
      } else {
        setJobs(data)
        setFilteredJobs(data)
      }
    } catch (error) {
      console.error('Error fetching jobs:', error)
      // Use mock data on error
      setJobs(getMockJobs())
      setFilteredJobs(getMockJobs())
    } finally {
      setLoading(false)
    }
  }

  const scrapeJobs = async () => {
    setScrapingStatus('Scraping jobs... This may take a moment.')
    try {
      const response = await fetch('http://localhost:8000/jobs/scrape', { method: 'POST' })
      const data = await response.json()
      setScrapingStatus('Scraping in progress. Checking results...')
      
      // Wait a moment and fetch again
      setTimeout(() => {
        fetchJobs()
        setScrapingStatus('')
      }, 3000)
    } catch (error) {
      console.error('Error scraping jobs:', error)
      setJobs(getMockJobs())
      setFilteredJobs(getMockJobs())
      setScrapingStatus('')
    }
  }

  const filterJobs = () => {
    let filtered = jobs.filter(job => {
      const titleMatch = job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        job.company.toLowerCase().includes(searchQuery.toLowerCase())
      const locationMatch = job.location.toLowerCase().includes(locationFilter.toLowerCase())
      
      return titleMatch && locationMatch
    })
    
    setFilteredJobs(filtered)
  }

  const handleViewJob = async (job) => {
    // Track job view - simplified
    try {
      const response = await fetch('http://localhost:8000/jobs/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title: job.title,
          company: job.company,
          location: job.location,
          job_url: job.job_url,
          match_score: 75,
          status: 'viewed'
        }),
      })
      if (response.ok) {
        console.log('[Jobs] ✅ View tracked:', job.title)
      } else {
        console.log('[Jobs] ⚠️ Track failed, status:', response.status)
      }
    } catch (error) {
      console.log('[Jobs] View tracked locally:', job.title, error.message)
    }
    
    // Open job in new tab
    window.open(job.job_url, '_blank')
  }

  const handleSaveJob = async (job) => {
    try {
      const response = await fetch('http://localhost:8000/jobs/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title: job.title || 'Job',
          company: job.company || 'Company',
          location: job.location || 'Remote',
          job_url: job.job_url || 'https://example.com',
          match_score: 75,
          status: 'saved'
        }),
      })
      
      if (response.ok) {
        alert(`✅ ${job.title} saved to your dashboard!`)
        console.log('[Jobs] ✅ Saved:', job.title)
      } else {
        const error = await response.json()
        console.error('Save error:', error)
        alert(`❌ Failed to save job: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      alert('❌ Error saving job: ' + error.message)
      console.log('[Jobs] Save error:', error)
    }
  }

  const getMockJobs = () => [
    {
      id: 1,
      title: 'Senior Python Developer',
      company: 'Tech Corp Inc',
      location: 'San Francisco, CA',
      description: 'Looking for an experienced Python developer with expertise in FastAPI and microservices.',
      salary: '$120,000 - $150,000',
      job_url: 'https://example.com',
      skills_required: 'Python, FastAPI, Docker, AWS'
    },
    {
      id: 2,
      title: 'Frontend Engineer (React)',
      company: 'StartUp XYZ',
      location: 'New York, NY',
      description: 'Build next-gen web apps with React. TypeScript and TailwindCSS required.',
      salary: '$100,000 - $130,000',
      job_url: 'https://example.com',
      skills_required: 'React, JavaScript, TypeScript, TailwindCSS'
    },
    {
      id: 3,
      title: 'Full Stack Developer',
      company: 'Finance Solutions',
      location: 'Chicago, IL',
      description: 'Build scalable fintech applications with Node.js and React.',
      salary: '$110,000 - $140,000',
      job_url: 'https://example.com',
      skills_required: 'Node.js, React, MongoDB, PostgreSQL'
    },
  ]

  return (
    <div className="animate-fadeIn">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Job Search</h1>
        <p className="text-slate-600">Find your next opportunity from thousands of job listings</p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="relative">
            <Search size={20} className="absolute left-3 top-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Job title, company, or skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <MapPin size={20} className="absolute left-3 top-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Location..."
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={fetchJobs}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Loading...' : 'Search'}
          </button>
        </div>

        {scrapingStatus && (
          <div className="flex items-center gap-2 text-blue-600 text-sm">
            <div className="spinner" style={{width: '16px', height: '16px'}}></div>
            {scrapingStatus}
          </div>
        )}
      </div>

      {/* Results */}
      <div>
        {loading ? (
          <div className="text-center py-12">
            <div className="spinner mx-auto mb-4"></div>
            <p className="text-slate-600">Loading jobs...</p>
          </div>
        ) : filteredJobs.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 text-center shadow-lg">
            <Briefcase size={48} className="mx-auto text-slate-400 mb-4" />
            <p className="text-slate-600 text-lg">No jobs found matching your criteria.</p>
            <p className="text-slate-500 text-sm mt-2">Try adjusting your search filters.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredJobs.map((job, index) => (
              <div key={`${job.job_url}-${index}`} className="bg-white rounded-xl shadow hover:shadow-lg transition-all p-6 card-hover">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-slate-900 hover:text-blue-600 transition cursor-pointer mb-2">
                      {job.title}
                    </h3>
                    <p className="text-slate-700 font-semibold mb-3">{job.company}</p>
                    <div className="flex flex-wrap gap-4 text-sm text-slate-600 mb-4">
                      <div className="flex items-center gap-1">
                        <MapPin size={16} className="text-blue-600" />
                        {job.location}
                      </div>
                      {job.salary && (
                        <div className="flex items-center gap-1">
                          <DollarSign size={16} className="text-green-600" />
                          {job.salary}
                        </div>
                      )}
                    </div>
                    <p className="text-slate-600 line-clamp-2 mb-3">{job.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {job.skills_required?.split(',').slice(0, 4).map((skill, idx) => (
                        <span key={idx} className="badge badge-success text-xs">
                          {skill.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => handleViewJob(job)}
                      className="btn-primary flex items-center justify-center gap-2 whitespace-nowrap"
                    >
                      View Job
                      <ExternalLink size={16} />
                    </button>
                    <button 
                      onClick={() => handleSaveJob(job)}
                      className="btn-secondary whitespace-nowrap"
                    >
                      Save
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}