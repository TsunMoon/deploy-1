"""
Simple conversation memory service
"""
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Simple in-memory conversation storage"""
    
    def __init__(self, max_history: int = 10):
        self.conversations: Dict[str, List[Tuple[str, str]]] = {}
        self.max_history = max_history
    
    def add_message(self, session_id: str, question: str, answer: str):
        """Add a message to conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append((question, answer))
        
        # Keep only last N messages
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
        
        logger.info(f"Added message to session {session_id}. Total: {len(self.conversations[session_id])}")
    
    def get_history(self, session_id: str) -> List[Tuple[str, str]]:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared session {session_id}")
    
    def format_history_for_prompt(self, session_id: str) -> str:
        """Format conversation history for LLM prompt"""
        history = self.get_history(session_id)
        if not history:
            return ""
        
        formatted = "\n\n**Previous Conversation:**\n"
        for i, (q, a) in enumerate(history[-5:], 1):  # Last 5 messages
            formatted += f"\nUser: {q}\nAssistant: {a}\n"
        
        return formatted


# Singleton instance
_memory_service = None


def get_memory_service() -> ConversationMemory:
    """Get or create memory service instance"""
    global _memory_service
    if _memory_service is None:
        _memory_service = ConversationMemory(max_history=10)
    return _memory_service
