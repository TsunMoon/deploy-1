import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryState } from 'nuqs'
import AssistantChatbot from '../screens/AssistantChatbot'
import MovieSuggestion from '../screens/MovieSuggestion'

export default function Portal() {
  const navigate = useNavigate()
  const [section, setSection] = useQueryState('section')

  const handleSelectChat = (sectionType) => {
    setSection(sectionType)
  }

  const handleBackToSelection = () => {
    setSection(null);
  };

/*************  ✨ Windsurf Command ⭐  *************/
/**
 * Clears any stored authentication tokens and redirects to the login or home page.
 */
/*******  e5ae058a-d57c-43bd-a398-3f831ce2a45e  *******/
  const handleLogout = () => {
    // Clear any stored authentication tokens
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('isAuthenticated', 'true')
    // Redirect to login or home page
    window.location.href = '/login'
  }

  return (
    <div className='min-h-screen bg-netflix-black flex items-center justify-center p-4 relative'>
      {/* Top Navigation Bar */}
      <div className='absolute top-6 right-6 z-20 flex gap-3'>
        <button
          onClick={() => navigate('/settings')}
          className='bg-gray-700 hover:bg-gray-600 text-white font-semibold px-6 py-2 rounded-lg transition shadow-lg flex items-center space-x-2'
        >
          <svg className='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
            />
            <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M15 12a3 3 0 11-6 0 3 3 0 016 0z' />
          </svg>
          <span>Settings</span>
        </button>
        <button
          onClick={handleLogout}
          className='bg-netflix-red hover:bg-netflix-darkRed text-white font-semibold px-6 py-2 rounded-lg transition shadow-lg flex items-center space-x-2'
        >
          <svg
            xmlns='http://www.w3.org/2000/svg'
            className='h-5 w-5'
            fill='none'
            viewBox='0 0 24 24'
            stroke='currentColor'
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1'
            />
          </svg>
          <span>Logout</span>
        </button>
      </div>

      <div className='absolute inset-0 size-full z-0 brightness-50'>
        <img src='/images/thumbnail.jpg' alt='Portal Background' className='size-full object-cover' />
      </div>
      <div className='w-1/2 bg-netflix-darkGray rounded-2xl shadow-2xl p-8 relative z-10'>
        {!section ? (
          <>
            <div className='text-center mb-8'>
              <div className='w-16 text-white h-16 rounded-lg bg-netflix-red flex items-center justify-center font-bold text-2xl mx-auto mb-4 shadow-lg'>
                CD
              </div>
              <h1 className='text-3xl font-bold text-netflix-offWhite'>Choose Your Assistant</h1>
              <p className='text-netflix-lightGray mt-2'>Select the type of conversation you'd like to have</p>
            </div>

            <div className='space-y-4'>
              <button
                onClick={() => handleSelectChat('movie-suggestion')}
                className='w-full bg-netflix-red hover:bg-netflix-darkRed text-white font-semibold py-4 px-6 rounded-lg transition flex items-center justify-center space-x-3'
              >
                <span className='text-lg'>Netflix Movie Suggestions</span>
              </button>

              <button
                onClick={() => window.open("https://frontend-azure-five-78.vercel.app/")}
                className='w-full bg-netflix-darkGray hover:bg-netflix-mediumGray border-2 border-netflix-red text-netflix-offWhite font-semibold py-4 px-6 rounded-lg transition flex items-center justify-center space-x-3'
              >
                <span className='text-lg'>Knowledge AI Assistant</span>
              </button>
            </div>

            <div className='mt-6 text-center'>
              <p className='text-netflix-lightGray text-sm'>
                Both assistants are powered by advanced AI to help you find what you're looking for
              </p>
            </div>
          </>
        ) : (
          <div className='w-full'>
            {/* Back to Selection button at top of chatbot */}
            {section === 'movie-suggestion' ? (
              <MovieSuggestion setSelectedChat={handleBackToSelection} />
            ) : (
              <AssistantChatbot setSelectedChat={handleBackToSelection} />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
