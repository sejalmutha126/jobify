import React, { useState } from 'react'
import { Upload, CheckCircle, AlertCircle, Loader } from 'lucide-react'

export default function ResumeAnalyzer() {
  const [resumeText, setResumeText] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState('')

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploadedFile(file.name)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/jobs/upload-resume', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResumeText(data.resume_text || 'Resume uploaded successfully')
    } catch (error) {
      console.error('Error uploading resume:', error)
      alert('Error uploading resume')
    }
  }

  const analyzeResume = async () => {
    if (!resumeText || !jobDescription) {
      alert('Please provide both resume and job description')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/jobs/analyze-resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jobDescription,
        }),
      })
      const data = await response.json()
      setAnalysis(data)
    } catch (error) {
      console.error('Error analyzing resume:', error)
      alert('Error analyzing resume. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getPriorityColor = (score) => {
    if (score >= 70) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPriorityBg = (score) => {
    if (score >= 70) return 'bg-green-100'
    if (score >= 50) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  return (
    <div className="animate-fadeIn">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Resume Analyzer</h1>
        <p className="text-slate-600">Get instant AI-powered feedback on how your resume matches job descriptions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="space-y-6">
          {/* Resume Upload */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Your Resume</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Upload Resume (PDF/Text)
              </label>
              <div className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center cursor-pointer hover:bg-blue-50 transition">
                <input
                  type="file"
                  onChange={handleFileUpload}
                  accept=".pdf,.txt"
                  className="hidden"
                  id="resume-upload"
                />
                <label htmlFor="resume-upload" className="cursor-pointer block">
                  <Upload className="mx-auto text-blue-600 mb-2" size={32} />
                  <p className="text-slate-700 font-medium">{uploadedFile || 'Click to upload or drag and drop'}</p>
                  <p className="text-slate-500 text-sm">PDF or Text (Max 5MB)</p>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Or Paste Resume Text
              </label>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume content here..."
                className="w-full h-40 p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
              />
            </div>
          </div>

          {/* Job Description */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Job Description</h2>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description here..."
              className="w-full h-40 p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
          </div>

          {/* Analyze Button */}
          <button
            onClick={analyzeResume}
            disabled={loading || !resumeText || !jobDescription}
            className="btn-primary w-full py-3 text-lg"
          >
            {loading ? (
              <>
                <Loader size={20} className="animate-spin inline mr-2" />
                Analyzing...
              </>
            ) : (
              'Analyze Resume'
            )}
          </button>
        </div>

        {/* Results Section */}
        {analysis ? (
          <div className="space-y-6">
            {/* Match Score */}
            <div className={`${getPriorityBg(analysis.match_score)} rounded-2xl shadow-lg p-8`}>
              <div className="text-center">
                <p className="text-slate-700 text-sm font-medium mb-2">Overall Match Score</p>
                <div className={`text-6xl font-bold ${getPriorityColor(analysis.match_score)} mb-4`}>
                  {analysis.match_score.toFixed(1)}%
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 mb-4">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      analysis.match_score >= 70 ? 'bg-green-600' :
                      analysis.match_score >= 50 ? 'bg-yellow-600' :
                      'bg-red-600'
                    }`}
                    style={{ width: `${analysis.match_score}%` }}
                  ></div>
                </div>
                <p className="text-sm text-slate-600">
                  {analysis.match_score >= 70 ? '🎉 Great match! You\'re well qualified for this role.' :
                   analysis.match_score >= 50 ? '⚡ Decent match. Consider improving key skills.' :
                   '📚 Significant skill gaps. Review the suggestions below.'}
                </p>
              </div>
            </div>

            {/* Matching Keywords */}
            {analysis.matching_keywords?.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle className="text-green-600" size={24} />
                  <h3 className="text-lg font-bold text-slate-900">Matching Skills</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysis.matching_keywords.map((keyword, idx) => (
                    <span key={idx} className="badge badge-success">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Keywords */}
            {analysis.missing_keywords?.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-center gap-2 mb-4">
                  <AlertCircle className="text-orange-600" size={24} />
                  <h3 className="text-lg font-bold text-slate-900">Missing Skills</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysis.missing_keywords.map((keyword, idx) => (
                    <span key={idx} className="badge badge-warning">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {analysis.suggestions?.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-4">💡 Suggestions</h3>
                <ul className="space-y-3">
                  {analysis.suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <span className="text-blue-600 font-bold mt-1">→</span>
                      <span className="text-slate-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-slate-600 text-lg">
              Your analysis results will appear here
            </p>
            <p className="text-slate-500 text-sm mt-2">
              Upload your resume and paste a job description to get started
            </p>
          </div>
        )}
      </div>
    </div>
  )
}