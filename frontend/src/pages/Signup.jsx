import React, { useState } from 'react'
import { Mail, Lock, User, AlertCircle, Loader, CheckCircle, Eye, EyeOff } from 'lucide-react'
import { useNavigate, Link } from 'react-router-dom'

export default function Signup() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // Step 1: Form, Step 2: OTP Verification
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirm_password: ''
  })
  const [otpData, setOtpData] = useState({
    otp_code: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState(0)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // Calculate password strength
    if (name === 'password') {
      let strength = 0
      if (value.length >= 8) strength++
      if (/[A-Z]/.test(value)) strength++
      if (/[a-z]/.test(value)) strength++
      if (/[0-9]/.test(value)) strength++
      if (/[!@#$%^&*]/.test(value)) strength++
      setPasswordStrength(strength)
    }
    
    setError('')
  }

  const handleOTPChange = (e) => {
    const { value } = e.target
    setOtpData(prev => ({
      ...prev,
      otp_code: value
    }))
    setError('')
  }

  const validateForm = () => {
    if (!formData.email || !formData.username || !formData.full_name || !formData.password) {
      setError('All fields are required')
      return false
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters')
      return false
    }

    if (!/[A-Z]/.test(formData.password)) {
      setError('Password must contain at least one uppercase letter')
      return false
    }

    if (!/[0-9]/.test(formData.password)) {
      setError('Password must contain at least one number')
      return false
    }

    if (!/[!@#$%^&*]/.test(formData.password)) {
      setError('Password must contain at least one special character (!@#$%^&*)')
      return false
    }

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match')
      return false
    }

    return true
  }

  const handleSignup = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!validateForm()) return

    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          full_name: formData.full_name,
          password: formData.password,
          confirm_password: formData.confirm_password
        })
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Signup failed')
        return
      }

      setSuccess(data.message)
      setStep(2) // Move to OTP verification
    } catch (error) {
      setError('Failed to connect to server. Please try again.')
      console.error('Signup error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleOTPVerify = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: formData.email,
          otp_code: otpData.otp_code
        })
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'OTP verification failed')
        return
      }

      // Save tokens
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      setSuccess('Email verified! Redirecting...')
      setTimeout(() => navigate('/dashboard'), 1500)
    } catch (error) {
      setError('Failed to verify OTP. Please try again.')
      console.error('OTP error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleResendOTP = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`http://localhost:8000/auth/resend-otp?email=${formData.email}`, {
        method: 'POST'
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Failed to resend OTP')
        return
      }

      setSuccess('OTP sent to your email')
    } catch (error) {
      setError('Failed to resend OTP')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl mb-4">
            <span className="text-2xl font-bold text-white">J</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">Jobify</h1>
          <p className="text-slate-600 mt-2">
            {step === 1 ? 'Create your account' : 'Verify your email'}
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex gap-2 mb-8">
          <div className={`flex-1 h-1 rounded-full transition-all ${step >= 1 ? 'bg-blue-600' : 'bg-slate-300'}`}></div>
          <div className={`flex-1 h-1 rounded-full transition-all ${step >= 2 ? 'bg-blue-600' : 'bg-slate-300'}`}></div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-green-800 text-sm">{success}</p>
          </div>
        )}

        {/* Signup Form - Step 1 */}
        {step === 1 && (
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <form onSubmit={handleSignup} className="space-y-4">
              {/* Email Field */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3.5 text-slate-400" size={20} />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="you@example.com"
                    required
                    className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Username Field */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3.5 text-slate-400" size={20} />
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="johndoe"
                    required
                    className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Full Name Field */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3.5 text-slate-400" size={20} />
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    placeholder="John Doe"
                    required
                    className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3.5 text-slate-400" size={20} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    required
                    className="w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3.5 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
                
                {/* Password Strength Indicator */}
                {formData.password && (
                  <div className="mt-2">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map(i => (
                        <div
                          key={i}
                          className={`h-1 flex-1 rounded-full transition-all ${
                            i <= passwordStrength ? 'bg-blue-600' : 'bg-slate-300'
                          }`}
                        ></div>
                      ))}
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      {passwordStrength < 3 ? 'Weak' : passwordStrength < 4 ? 'Good' : 'Strong'} password
                    </p>
                  </div>
                )}

                <p className="text-xs text-slate-500 mt-2">
                  Must be 8+ characters with uppercase, number, and special character (!@#$%^&*)
                </p>
              </div>

              {/* Confirm Password Field */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3.5 text-slate-400" size={20} />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    required
                    className="w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-3.5 text-slate-400 hover:text-slate-600"
                  >
                    {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Terms & Conditions */}
              <label className="flex items-start gap-2 text-sm">
                <input type="checkbox" className="mt-1" required />
                <span className="text-slate-600">
                  I agree to the{' '}
                  <a href="#" className="text-blue-600 hover:text-blue-700">
                    Terms of Service
                  </a>
                  {' '}and{' '}
                  <a href="#" className="text-blue-600 hover:text-blue-700">
                    Privacy Policy
                  </a>
                </span>
              </label>

              {/* Signup Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader size={18} className="animate-spin" />
                    Creating account...
                  </>
                ) : (
                  'Create Account'
                )}
              </button>
            </form>

            {/* Login Link */}
            <p className="text-center mt-6 text-slate-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        )}

        {/* OTP Verification - Step 2 */}
        {step === 2 && (
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <form onSubmit={handleOTPVerify} className="space-y-6">
              <div className="text-center">
                <p className="text-slate-600 mb-2">
                  We've sent a verification code to
                </p>
                <p className="font-medium text-slate-900">{formData.email}</p>
              </div>

              {/* OTP Input */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Verification Code
                </label>
                <input
                  type="text"
                  name="otp_code"
                  value={otpData.otp_code}
                  onChange={handleOTPChange}
                  placeholder="000000"
                  maxLength="6"
                  required
                  className="w-full px-4 py-3 text-center text-2xl tracking-widest border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                />
                <p className="text-xs text-slate-500 mt-2 text-center">
                  Enter the 6-digit code sent to your email
                </p>
              </div>

              {/* Verify Button */}
              <button
                type="submit"
                disabled={loading || otpData.otp_code.length !== 6}
                className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader size={18} className="animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify Email'
                )}
              </button>

              {/* Resend OTP */}
              <div className="text-center">
                <p className="text-slate-600 text-sm mb-2">Didn't receive the code?</p>
                <button
                  type="button"
                  onClick={handleResendOTP}
                  disabled={loading}
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm disabled:opacity-50"
                >
                  Resend OTP
                </button>
              </div>

              {/* Change Email */}
              <button
                type="button"
                onClick={() => {
                  setStep(1)
                  setOtpData({ otp_code: '' })
                  setError('')
                  setSuccess('')
                }}
                className="w-full text-slate-600 hover:text-slate-700 text-sm"
              >
                Use a different email
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}