import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'

export default function Login() {
  const navigate = useNavigate()

  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate('/', { replace: true })
    }
  }, [navigate])

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    console.log(123)
    try {
      await authService.login(email, password)
      navigate('/')
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className='min-h-screen bg-netflix-black flex items-center justify-center p-4 relative'>
      <div className='absolute inset-0 size-full z-0 brightness-50'>
        <img src='/images/thumbnail.jpg' alt='Login Background' className='size-full' />
      </div>
      <div className='w-full max-w-md bg-netflix-darkGray rounded-2xl shadow-2xl p-8 relative z-10'>
        <div className='text-center mb-8'>
          <div className='w-16 text-white h-16 rounded-lg bg-netflix-red flex items-center justify-center font-bold text-2xl mx-auto mb-4 shadow-lg'>
            CD
          </div>
          <h1 className='text-3xl font-bold text-netflix-offWhite'>Welcome Back</h1>
          <p className='text-netflix-lightGray mt-2'>Sign in to continue watching</p>
        </div>

        <form onSubmit={handleSubmit} className='space-y-6'>
          {error && (
            <div className='bg-netflix-darkRed border border-netflix-red text-netflix-offWhite px-4 py-3 rounded-lg text-sm'>{error}</div>
          )}

          <div>
            <label htmlFor='email' className='block text-sm font-medium text-netflix-offWhite mb-2'>
              Email
            </label>
            <input
              id='email'
              type='email'
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className='w-full px-4 py-3 bg-netflix-darkGray border border-netflix-mediumGray rounded-lg text-netflix-offWhite placeholder-netflix-mediumGray focus:ring-2 focus:ring-netflix-red focus:border-netflix-red outline-none transition'
              placeholder='Enter your email'
              required
              autoFocus
            />
          </div>

          <div>
            <label htmlFor='password' className='block text-sm font-medium text-netflix-offWhite mb-2'>
              Password
            </label>
            <input
              id='password'
              type='password'
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className='w-full px-4 py-3 bg-netflix-darkGray border border-netflix-mediumGray rounded-lg text-netflix-offWhite placeholder-netflix-mediumGray focus:ring-2 focus:ring-netflix-red focus:border-netflix-red outline-none transition'
              placeholder='Enter your password'
              required
            />
          </div>

          <button
            type='submit'
            disabled={isLoading}
            className='w-full bg-netflix-red hover:bg-netflix-darkRed text-white font-semibold py-3 px-4 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed'
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}
