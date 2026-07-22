import React, { useState, useEffect } from 'react'
import { User, Mail, Phone, MapPin, Briefcase, Edit2, Save, X, AlertCircle, CheckCircle, Loader, Upload, Camera } from 'lucide-react'

export default function Profile() {
  const [user, setUser] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [profilePhoto, setProfilePhoto] = useState(null)
  const [photoPreview, setPhotoPreview] = useState(null)
  const [uploadingPhoto, setUploadingPhoto] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    bio: '',
    skills: '',
    phone: '',
    location: ''
  })

  useEffect(() => {
    fetchUserProfile()
  }, [])

  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('access_token')
      console.log('Token:', token ? 'exists' : 'missing')
      
      if (!token) {
        setError('No authentication token found. Please login again.')
        setLoading(false)
        return
      }
      
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      console.log('Profile response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch profile')
      }

      const data = await response.json()
      console.log('Profile data:', data)
      setUser(data)
      setFormData({
        full_name: data.full_name || '',
        bio: data.bio || '',
        skills: data.skills || '',
        phone: data.phone || '',
        location: data.location || ''
      })
      setLoading(false)
    } catch (error) {
      console.error('Profile error:', error)
      setError(error.message || 'Failed to load profile')
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handlePhotoChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Photo size must be less than 5MB')
      return
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    setProfilePhoto(file)
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (event) => {
      setPhotoPreview(event.target.result)
    }
    reader.readAsDataURL(file)
  }

  const handleSave = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/auth/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Failed to update profile')
        return
      }

      setUser(data)
      setSuccess('Profile updated successfully!')
      setIsEditing(false)
    } catch (error) {
      setError('Failed to update profile')
      console.error('Profile update error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading && !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="animate-spin text-blue-600" size={40} />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto animate-fadeIn">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900">My Profile</h1>
        <p className="text-slate-600 mt-2">Manage your account information and preferences</p>
      </div>

      {/* Error & Success Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-green-800">{success}</p>
        </div>
      )}

      {/* Profile Card */}
      {user && (
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* Profile Header */}
          <div className="flex items-start justify-between mb-8">
            <div className="flex items-center gap-6">
              {/* Profile Photo */}
              <div className="relative">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center overflow-hidden">
                  {photoPreview ? (
                    <img src={photoPreview} alt="Profile" className="w-full h-full object-cover" />
                  ) : user.profile_pic ? (
                    <img src={user.profile_pic} alt="Profile" className="w-full h-full object-cover" />
                  ) : (
                    <User className="text-white" size={48} />
                  )}
                </div>
                {isEditing && (
                  <label className="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full cursor-pointer hover:bg-blue-700 transition-all">
                    <Camera size={16} />
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handlePhotoChange}
                      className="hidden"
                    />
                  </label>
                )}
              </div>
              <div>
                <h2 className="text-3xl font-bold text-slate-900">{user.full_name}</h2>
                <p className="text-slate-600">@{user.username}</p>
                <div className="flex items-center gap-2 mt-2">
                  <div className={`w-3 h-3 rounded-full ${user.is_verified ? 'bg-green-600' : 'bg-yellow-600'}`}></div>
                  <span className="text-sm font-medium text-slate-600">
                    {user.is_verified ? 'Verified' : 'Not Verified'}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
            >
              {isEditing ? (
                <>
                  <X size={18} />
                  Cancel
                </>
              ) : (
                <>
                  <Edit2 size={18} />
                  Edit Profile
                </>
              )}
            </button>
          </div>

          {/* Divider */}
          <div className="border-t border-slate-200 my-8"></div>

          {/* Profile Information */}
          <div className="space-y-6">
            {/* Email */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                <Mail size={18} className="text-blue-600" />
                Email Address
              </label>
              <input
                type="email"
                value={user.email}
                disabled
                className="w-full px-4 py-2.5 bg-slate-100 border border-slate-300 rounded-lg text-slate-600 cursor-not-allowed"
              />
              <p className="text-xs text-slate-500 mt-1">Email cannot be changed</p>
            </div>

            {/* Full Name */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                <User size={18} className="text-blue-600" />
                Full Name
              </label>
              <input
                type="text"
                name="full_name"
                value={isEditing ? formData.full_name : user.full_name}
                onChange={handleChange}
                disabled={!isEditing}
                className={`w-full px-4 py-2.5 border border-slate-300 rounded-lg transition-all ${
                  isEditing
                    ? 'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                    : 'bg-slate-100 cursor-not-allowed'
                }`}
              />
            </div>

            {/* Phone */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                <Phone size={18} className="text-blue-600" />
                Phone Number
              </label>
              <input
                type="tel"
                name="phone"
                value={isEditing ? formData.phone : (user.phone || '')}
                onChange={handleChange}
                placeholder="+1 (555) 123-4567"
                disabled={!isEditing}
                className={`w-full px-4 py-2.5 border border-slate-300 rounded-lg transition-all ${
                  isEditing
                    ? 'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                    : 'bg-slate-100 cursor-not-allowed'
                }`}
              />
            </div>

            {/* Location */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                <MapPin size={18} className="text-blue-600" />
                Location
              </label>
              <input
                type="text"
                name="location"
                value={isEditing ? formData.location : (user.location || '')}
                onChange={handleChange}
                placeholder="City, Country"
                disabled={!isEditing}
                className={`w-full px-4 py-2.5 border border-slate-300 rounded-lg transition-all ${
                  isEditing
                    ? 'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                    : 'bg-slate-100 cursor-not-allowed'
                }`}
              />
            </div>

            {/* Bio */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                <Briefcase size={18} className="text-blue-600" />
                Bio
              </label>
              <textarea
                name="bio"
                value={isEditing ? formData.bio : (user.bio || '')}
                onChange={handleChange}
                placeholder="Tell us about yourself..."
                disabled={!isEditing}
                rows="4"
                className={`w-full px-4 py-2.5 border border-slate-300 rounded-lg transition-all ${
                  isEditing
                    ? 'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                    : 'bg-slate-100 cursor-not-allowed'
                }`}
              />
            </div>

            {/* Skills */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
                <Briefcase size={18} className="text-blue-600" />
                Skills (comma-separated)
              </label>
              <input
                type="text"
                name="skills"
                value={isEditing ? formData.skills : (user.skills || '')}
                onChange={handleChange}
                placeholder="Python, React, FastAPI, Docker..."
                disabled={!isEditing}
                className={`w-full px-4 py-2.5 border border-slate-300 rounded-lg transition-all ${
                  isEditing
                    ? 'focus:ring-2 focus:ring-blue-500 focus:border-transparent'
                    : 'bg-slate-100 cursor-not-allowed'
                }`}
              />
              {user.skills && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {user.skills.split(',').map((skill, idx) => (
                    <span
                      key={idx}
                      className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium"
                    >
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Account Info */}
            <div className="bg-slate-50 rounded-lg p-4 mt-8">
              <h3 className="font-semibold text-slate-900 mb-3">Account Information</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-600">Member Since</span>
                  <span className="font-medium text-slate-900">
                    {new Date(user.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Last Updated</span>
                  <span className="font-medium text-slate-900">
                    {new Date(user.updated_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Email Status</span>
                  <span className={`font-medium ${user.is_verified ? 'text-green-600' : 'text-yellow-600'}`}>
                    {user.is_verified ? 'Verified' : 'Pending Verification'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          {isEditing && (
            <div className="flex gap-4 mt-8 pt-8 border-t border-slate-200">
              <button
                onClick={handleSave}
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader size={18} className="animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save size={18} />
                    Save Changes
                  </>
                )}
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="flex-1 px-6 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-all"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}