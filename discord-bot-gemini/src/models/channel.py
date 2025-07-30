from typing import Dict

class Channel:
    """
    Data model for a Discord channel.
    Attributes:
        channel_id (str): Unique identifier for the channel.
        name (str): Name of the channel.
        type (str): Type of the channel (e.g., text, voice).
    """
    def __init__(self, channel_id: str, name: str, type: str) -> None:
        self.channel_id: str = channel_id
        self.name: str = name
        self.type: str = type

    def __repr__(self) -> str:
        return f"<Channel id={self.channel_id} name={self.name} type={self.type}>"

    def to_dict(self) -> Dict[str, str]:
        """Convert the channel object to a dictionary."""
        return {
            "channel_id": self.channel_id,
            "name": self.name,
            "type": self.type
        }