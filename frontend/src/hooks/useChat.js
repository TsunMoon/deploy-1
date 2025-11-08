import { useState } from "react";
import { generateId } from "../utils/helpers";
import { INITIAL_MESSAGE, SUGGESTED_QUESTIONS } from "../utils/constants";
import { faqService } from "../services/faqService";

export function useChat() {
  const [messages, setMessages] = useState([
    {
      id: generateId(),
      ...INITIAL_MESSAGE,
    },
  ]);
  const [isResponding, setIsResponding] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] =
    useState(SUGGESTED_QUESTIONS);

  const pushMessage = (msg) => {
    setMessages((prev) => [...prev, { ...msg, mounted: false }]);
    requestAnimationFrame(() => {
      setMessages((prev) =>
        prev.map((m) => (m.id === msg.id ? { ...m, mounted: true } : m))
      );
    });
  };

  const requestAudio = async (message) => {
    if (!message.text) return;

    // Set loading state
    setMessages((prev) =>
      prev.map((m) =>
        m.id === message.id
          ? {
              ...m,
              loadingAudio: true,
            }
          : m
      )
    );

    try {
      const response = await faqService.getAudioForText(message.text);

      // Update message with audio URL
      setMessages((prev) =>
        prev.map((m) =>
          m.id === message.id
            ? {
                ...m,
                audioUrl: response.audioUrl,
                loadingAudio: false,
              }
            : m
        )
      );
    } catch (error) {
      console.error("Error getting audio:", error);
      // Reset loading state on error
      setMessages((prev) =>
        prev.map((m) =>
          m.id === message.id
            ? {
                ...m,
                loadingAudio: false,
              }
            : m
        )
      );
    }
  };

  const sendMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    // Add user message
    const userMsg = {
      id: generateId(),
      role: "user",
      text: trimmed,
    };
    pushMessage(userMsg);

    // Add AI placeholder
    const aiPlaceholder = {
      id: generateId(),
      role: "ai",
      text: "",
      loading: true,
    };
    pushMessage(aiPlaceholder);
    setSuggestedQuestions([]);
    setIsResponding(true);

    try {
      const {
        answer,
        audioUrl,
        relatedQuestions,
        contextUsed,
        responseType,
        functionCalled,
        sources,
      } = await faqService.getAnswer(trimmed);

      // Update AI message with response
      setMessages((prev) =>
        prev.map((m) =>
          m.id === aiPlaceholder.id
            ? {
                ...m,
                text: answer,
                audioUrl: audioUrl,
                loading: false,
                responseType: responseType,
                functionCalled: functionCalled,
                sources: sources || contextUsed,
                contextUsed: contextUsed,
                onRequestAudio: requestAudio,
                onSourceClick: sendMessage, // Add this line to handle source clicks
              }
            : m
        )
      );

      // Update suggested questions
      setSuggestedQuestions(relatedQuestions);
    } catch (error) {
      console.error("Error getting AI response:", error);

      // Show error message
      setMessages((prev) =>
        prev.map((m) =>
          m.id === aiPlaceholder.id
            ? {
                ...m,
                text: '❌ Sorry, I can only help with movie and TV show related questions. Please ask about films, series, actors, genres, or recommendations.',
                loading: false,
                error: true,
              }
            : m
        )
      );

      // Reset suggested questions on error
      setSuggestedQuestions(SUGGESTED_QUESTIONS);
    } finally {
      setIsResponding(false);
    }
  };

  // Clear conversation (optional feature)
  const clearConversation = async () => {
    try {
      await faqService.clearMemory();
      setMessages([
        {
          id: generateId(),
          ...INITIAL_MESSAGE,
        },
      ]);
      setSuggestedQuestions(SUGGESTED_QUESTIONS);
    } catch (error) {
      console.error("Error clearing conversation:", error);
    }
  };

  return {
    messages,
    isResponding,
    sendMessage,
    suggestedQuestions,
    clearConversation,
  };
}
