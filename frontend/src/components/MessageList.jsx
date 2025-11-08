import React from 'react';
import MessageBubble from './MessageBubble';

export default function MessageList({ messages, scrollRef }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-3" id="messages-area">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={scrollRef} />
    </div>
  );
}