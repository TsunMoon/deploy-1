export default function ChatHeader({
  title,
  setSelectedChat
}) {

  return (
    <div className='px-4 py-3 border-b border-gray-100 flex items-center justify-between'>
      <div className='flex items-center gap-3'>
        <div className='w-10 h-10 rounded-full bg-netflix-red flex items-center justify-center text-white font-bold shadow-sm'>
          CD
        </div>
        <div>
          <div className='font-semibold text-white'>Chill Dev</div>
          <div className='text-xs text-white'>{title}</div>
        </div>
      </div>
      <button
        onClick={() => setSelectedChat(null)}
        className='mb-4 bg-netflix-darkGray hover:bg-netflix-mediumGray border-2 border-netflix-red text-netflix-offWhite font-semibold px-6 py-2 rounded-lg transition shadow-lg flex items-center space-x-2'
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
            d='M10 19l-7-7m0 0l7-7m-7 7h18'
          />
        </svg>
        <span>Back to Selection</span>
      </button>
    </div>
  )
}
