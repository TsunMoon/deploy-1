import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const [showAllSources, setShowAllSources] = useState(false)

  // Format response type for display
  const formatResponseType = (type) => {
    if (!type || type === 'default') return null
    return type.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] p-6 rounded-lg shadow-sm transition-all duration-300 transform ${
          message.mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
        } bg-netflix-black text-white rounded-bl-none`}
      >
        {message.loading ? (
          <div className='flex items-center'>
            <div className='loading-dots'>
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className='ml-3 text-sm text-gray-500'>Thinking...</span>
          </div>
        ) : (
          <>
            {/* Response Type Badge */}
            {!isUser && message.responseType && formatResponseType(message.responseType) && (
              <div className='mb-2'>
                <span className='inline-block px-2 py-1 font-bold bg-netflix-red text-white rounded-full'>
                  {formatResponseType(message.responseType)}
                </span>
              </div>
            )}

            {/* Function Called Badge */}
            {!isUser && message.functionCalled && (
              <div className='mb-2'>
                <span className='inline-block px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full'>
                  🔧 Function: {message.functionCalled}
                </span>
              </div>
            )}

            {/* Message Content */}
            <div className='whitespace-pre-wrap break-words text-sm'>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw, rehypeSanitize]}
                components={{
                  a: ({ node, ...props }) => (
                    <a {...props} target='_blank' rel='noopener noreferrer' className='text-primary-600 underline'>
                      {props.children}
                    </a>
                  )
                }}
              >
                {message.text}
              </ReactMarkdown>
            </div>

            {/* Sources/Context Used */}
            {!isUser && message.sources && message.sources.length > 0 && (
              <div className='mt-3 pt-3 border-t border-gray-200'>
                <div className='text-xs font-semibold text-gray-600 mb-2 flex items-center justify-between'>
                  <span>Sources Used ({message.sources.length}):</span>
                </div>
                <div className='space-y-2'>
                  {(showAllSources ? message.sources : message.sources.slice(0, 3)).map((source, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        if (message.onSourceClick) {
                          const query = `Tell me more about ${source.title}`
                          message.onSourceClick(query)
                        }
                      }}
                      className='w-full text-left p-2 bg-gray-800 hover:bg-gray-700 rounded border border-gray-600 text-white transition-colors cursor-pointer'
                    >
                      <div className='font-semibold text-xs text-white flex items-center justify-between'>
                        <span>{source.title}</span>
                        <span className='text-netflix-red'>→</span>
                      </div>
                      <div className='text-xs text-gray-300 mt-1'>
                        {source.genre} • {source.year}
                        {source.rating && ` • ${source.rating}`}
                        {source.type && ` • ${source.type}`}
                      </div>
                      {source.description && (
                        <div className='text-xs text-gray-400 mt-1 line-clamp-2'>{source.description}</div>
                      )}
                    </button>
                  ))}
                  {message.sources.length > 3 && (
                    <button
                      onClick={() => setShowAllSources(!showAllSources)}
                      className='w-full mt-2 px-4 py-2 bg-netflix-red hover:bg-netflix-darkRed text-white text-xs font-semibold rounded-lg transition-colors flex items-center justify-center gap-2'
                    >
                      {showAllSources ? (
                        <>
                          <svg className='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                            <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M5 15l7-7 7 7' />
                          </svg>
                          Show Less
                        </>
                      ) : (
                        <>
                          <svg className='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                            <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M19 9l-7 7-7-7' />
                          </svg>
                          View {message.sources.length - 3} More Sources
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Audio Control */}
            {!isUser && (
              <div className='mt-3 pt-3'>
                <div className='text-xs font-semibold text-gray-600 mb-2 flex items-center justify-between'>
                  {!message.audioUrl && (
                    <button
                      onClick={() => message.onRequestAudio && message.onRequestAudio(message)}
                      disabled={message.loadingAudio}
                      className={`text-primary-600 hover:text-primary-700 transition-colors flex items-center gap-2 ${
                        message.loadingAudio ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                    >
                      {message.loadingAudio && (
                        <>
                          <div className='loading-dots'>
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                          <span>Generating Audio...</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
                {message.audioUrl && (
                  <audio controls src={message.audioUrl} className='w-full h-8' style={{ maxWidth: '100%' }}>
                    Your browser does not support audio playback.
                  </audio>
                )}
              </div>
            )}
          </>
        )}
      </div>
      <style jsx>{`
        .loading-dots {
          display: flex;
          gap: 4px;
        }
        .loading-dots span {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #9ca3af;
          animation: bounce 1s infinite;
        }
        .loading-dots span:nth-child(2) {
          animation-delay: 0.2s;
        }
        .loading-dots span:nth-child(3) {
          animation-delay: 0.4s;
        }
        @keyframes bounce {
          0%,
          100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-6px);
          }
        }
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  )
}
