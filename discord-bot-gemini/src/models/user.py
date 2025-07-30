from typing import Optional

class User:
    """
    Data model for a Discord user.
    Attributes:
        user_id (str): Unique identifier for the user.
        username (str): Username of the user.
        age (Optional[int]): Age of the user.
        birthday (Optional[str]): Birthday of the user.
    """
    def __init__(self, user_id: str, username: str, age: Optional[int] = None, birthday: Optional[str] = None) -> None:
        self.user_id: str = user_id
        self.username: str = username
        self.age: Optional[int] = age
        self.birthday: Optional[str] = birthday

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, username={self.username}, age={self.age}, birthday={self.birthday})"

    def update_age(self, new_age: int) -> None:
        """Update the user's age."""
        self.age = new_age

    def update_birthday(self, new_birthday: str) -> None:
        """Update the user's birthday."""
        self.birthday = new_birthday

    def to_dict(self) -> dict:
        """Convert the user object to a dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "age": self.age,
            "birthday": self.birthday
        }