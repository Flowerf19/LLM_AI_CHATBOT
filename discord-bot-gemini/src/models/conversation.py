from typing import List, Optional

class Conversation:
    """
    Data model for a user's conversation history.
    Attributes:
        user_id (str): Unique identifier for the user.
        messages (List[str]): List of messages in the conversation.
    """
    def __init__(self, user_id: str, messages: Optional[List[str]] = None) -> None:
        self.user_id: str = user_id
        self.messages: List[str] = messages if messages is not None else []

    def add_message(self, message: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append(message)

    def get_history(self) -> List[str]:
        """Get the conversation history as a list of messages."""
        return self.messages

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.messages = []

    def __repr__(self) -> str:
        return f"<Conversation user_id={self.user_id} messages_count={len(self.messages)}>"