import React, { useState } from 'react'
import { Mail, Copy, Send, Loader, CheckCircle } from 'lucide-react'

export default function EmailAutomation() {
  const [formData, setFormData] = useState({
    recruiter_name: '',
    recruiter_email: '',
    job_title: '',
    company_name: '',
    user_name: '',
    user_skills: '',
  })

  const [generatedEmail, setGeneratedEmail] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [sent, setSent] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const generateEmail = async () => {
    if (!formData.recruiter_name || !formData.job_title || !formData.company_name || !formData.user_name) {
      alert('Please fill in all required fields')
      return
    }

    setLoading(true)
    try {
      const skills = formData.user_skills.split(',').map(s => s.trim()).filter(s => s)
      
      const response = await fetch('http://localhost:8000/generate-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruiter_name: formData.recruiter_name,
          recruiter_email: formData.recruiter_email,
          job_title: formData.job_title,
          company_name: formData.company_name,
          user_name: formData.user_name,
          user_skills: skills,
        }),
      })
      const data = await response.json()
      setGeneratedEmail(data)
      setSent(false)
    } catch (error) {
      console.error('Error generating email:', error)
      alert('Error generating email. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const sendEmail = async () => {
    if (!formData.recruiter_email) {
      alert('Please enter recruiter email address')
      return
    }

    if (!generatedEmail) {
      alert('Please generate email first')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruiter_name: formData.recruiter_name,
          recruiter_email: formData.recruiter_email,
          job_title: formData.job_title,
          company_name: formData.company_name,
          user_name: formData.user_name,
          subject: generatedEmail.subject,
          email_body: generatedEmail.email_body,
        }),
      })
      const data = await response.json()
      if (data.success) {
        setSent(true)
        alert(`✅ Email sent to ${formData.recruiter_email}!`)
        setTimeout(() => setSent(false), 3000)
      } else {
        alert(`❌ Error: ${data.error || 'Failed to send email'}`)
      }
    } catch (error) {
      console.error('Error sending email:', error)
      alert('Error sending email. Please check console.')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedEmail.email_body)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="animate-fadeIn">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Email Automation</h1>
        <p className="text-slate-600">Generate and send personalized cold emails to recruiters</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form Section */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Email Details</h2>
          
          <div className="space-y-4">
            {/* Row 1 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Your Name *
                </label>
                <input
                  type="text"
                  name="user_name"
                  value={formData.user_name}
                  onChange={handleInputChange}
                  placeholder="John Doe"
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Recruiter Name *
                </label>
                <input
                  type="text"
                  name="recruiter_name"
                  value={formData.recruiter_name}
                  onChange={handleInputChange}
                  placeholder="Jane Smith"
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Row 2 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Recruiter Email *
              </label>
              <input
                type="email"
                name="recruiter_email"
                value={formData.recruiter_email}
                onChange={handleInputChange}
                placeholder="jane@company.com"
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Row 3 */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Job Title *
                </label>
                <input
                  type="text"
                  name="job_title"
                  value={formData.job_title}
                  onChange={handleInputChange}
                  placeholder="Senior Developer"
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleInputChange}
                  placeholder="Tech Corp"
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Skills */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Your Skills (comma-separated)
              </label>
              <input
                type="text"
                name="user_skills"
                value={formData.user_skills}
                onChange={handleInputChange}
                placeholder="Python, React, Docker, AWS..."
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                onClick={generateEmail}
                disabled={loading}
                className="flex-1 btn-primary flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader size={18} className="animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Mail size={18} />
                    Generate Email
                  </>
                )}
              </button>
              <button
                onClick={sendEmail}
                disabled={!generatedEmail || loading}
                className="flex-1 btn-secondary flex items-center justify-center gap-2"
              >
                <Send size={18} />
                Send Email
              </button>
            </div>
          </div>
        </div>

        {/* Preview Section */}
        {generatedEmail ? (
          <div className="space-y-4">
            {sent && (
              <div className="bg-green-100 border border-green-400 rounded-lg p-4 flex items-center gap-3">
                <CheckCircle className="text-green-600" size={24} />
                <div>
                  <p className="font-semibold text-green-800">Email sent successfully!</p>
                  <p className="text-sm text-green-700">Email has been sent to {formData.recruiter_email}</p>
                </div>
              </div>
            )}

            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-slate-900">Email Preview</h2>
                <button
                  onClick={copyToClipboard}
                  className="text-sm px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition flex items-center gap-2"
                >
                  <Copy size={16} />
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>

              <div className="bg-slate-50 rounded-lg p-6 mb-4 border border-slate-200">
                <div className="mb-4">
                  <p className="text-sm text-slate-600 font-medium mb-1">Subject:</p>
                  <p className="text-slate-900 font-semibold">{generatedEmail.subject}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 font-medium mb-2">Message:</p>
                  <div className="text-slate-800 whitespace-pre-wrap text-sm leading-relaxed">
                    {generatedEmail.email_body}
                  </div>
                </div>
              </div>

              <p className="text-sm text-slate-600 text-center">
                ✏️ Feel free to edit before sending
              </p>
            </div>

            {/* Tips */}
            <div className="bg-blue-50 rounded-2xl shadow-lg p-6 border border-blue-200">
              <h3 className="font-bold text-blue-900 mb-3">📧 Email Tips</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li>✓ Keep emails short and personalized</li>
                <li>✓ Include specific examples of your work</li>
                <li>✓ Add a clear call-to-action</li>
                <li>✓ Follow up after 3-5 days if no response</li>
                <li>✓ Customize each email to the company</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <Mail size={48} className="mx-auto text-slate-400 mb-4" />
            <p className="text-slate-600 text-lg">Fill in the form to generate a personalized email</p>
            <p className="text-slate-500 text-sm mt-2">AI will create a professional cold email tailored to the recruiter</p>
          </div>
        )}
      </div>
    </div>
  )
}