import React from 'react';
import { useChat } from '../hooks/useChat';
import { useAutoScroll } from '../hooks/useAutoScroll';
import ChatHeader from '../components/ChatHeader';
import MessageList from '../components/MessageList';
import ChatInput from '../components/ChatInput';
import SuggestedQuestions from '../components/SuggestedQuestions';

export default function FAQChatbot({setSelectedChat}) {
  const { messages, isResponding, sendMessage, suggestedQuestions } = useChat();
  const scrollRef = useAutoScroll([messages, isResponding]);


  return (
    <div className="w-full h-[90vh] bg-netflix-darkGray text-white rounded-2xl shadow-xl flex flex-col overflow-hidden">
      <ChatHeader setSelectedChat={setSelectedChat} title={"Movie Knowledge Assistant"} />
      <MessageList messages={messages} scrollRef={scrollRef} />
      <SuggestedQuestions questions={suggestedQuestions} onSelect={sendMessage} />
      <ChatInput onSend={sendMessage} isDisabled={isResponding} />
    </div>
  );
}