import React from 'react';

export default function SuggestedQuestions({ questions, onSelect }) {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="p-4 border-gray-100 flex flex-wrap gap-2">
      {questions.map((question, index) => (
        <button
          key={index}
          onClick={() => onSelect(question)}
          className="px-3 py-1 bg-netflix-black hover:bg-netflix-black/10 text-white rounded-full text-sm transition-colors duration-200"
        >
          {question}
        </button>
      ))}
    </div>
  );
}