import React, { useState } from 'react';

export default function ChatInput({ onSend, isDisabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e, fromKeyPress = false) => {
    e?.preventDefault();
    
    // If disabled or no content, don't submit
    if (isDisabled || !input.trim()) return;
    
    // Prevent duplicate submissions
    if (fromKeyPress && e.type === 'keydown' && (e.key !== 'Enter' || e.shiftKey)) {
      return;
    }
    
    onSend(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e, true);
    }
  };

  return (
    <form
      onSubmit={(e) => handleSubmit(e, false)}
      className="px-4 py-3 bg-netflix-darkGray sticky bottom-0"
      style={{
        WebkitBackdropFilter: 'blur(6px)',
        backdropFilter: 'blur(6px)',
      }}
    >
      <div className="max-w-full mx-auto flex items-center gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question..."
          className="flex-1 resize-none min-h-[44px] max-h-32 px-4 py-3 rounded-xl border border-black focus:outline-none focus:ring-2 bg-netflix-black text-sm"
        />
        <button
          type="submit"
          className={`px-4 py-2 rounded-xl shadow-md flex items-center gap-2 text-sm bg-netflix-red text-white cursor-not-allowed`}
          disabled={!input.trim() || isDisabled}
        >
          {isDisabled ? 'Wait…' : 'Send'}
        </button>
      </div>
    </form>
  );
}