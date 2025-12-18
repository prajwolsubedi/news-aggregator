import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core import database


@dataclass
class Subscriber:
    """Subscriber model representing an email subscriber."""
    id: int
    email: str
    subscribed_at: datetime
    unsubscribe_token: str
    is_active: bool

    @classmethod
    def from_dict(cls, data: dict) -> "Subscriber":
        """Create Subscriber instance from database dict."""
        return cls(
            id=data["id"],
            email=data["email"],
            subscribed_at=data["subscribed_at"],
            unsubscribe_token=data["unsubscribe_token"],
            is_active=data["is_active"],
        )

    def to_dict(self) -> dict:
        """Convert Subscriber instance to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "subscribed_at": self.subscribed_at,
            "unsubscribe_token": self.unsubscribe_token,
            "is_active": self.is_active,
        }


def generate_unsubscribe_token() -> str:
    """Generate a unique unsubscribe token using UUID."""
    return str(uuid.uuid4())


def get_subscriber_by_email(email: str) -> Optional[Subscriber]:
    """Get subscriber by email address. Returns Subscriber or None."""
    data = database.get_subscriber_by_email(email)
    if data:
        return Subscriber.from_dict(data)
    return None


def get_subscriber_by_token(token: str) -> Optional[Subscriber]:
    """Get subscriber by unsubscribe token. Returns Subscriber or None."""
    data = database.get_subscriber_by_token(token)
    if data:
        return Subscriber.from_dict(data)
    return None


def get_all_active_subscribers() -> list[Subscriber]:
    """Get all active subscribers. Returns list of Subscriber instances."""
    subscribers_data = database.get_all_active_subscribers()
    return [Subscriber.from_dict(data) for data in subscribers_data]


def add_subscriber(email: str, unsubscribe_token: Optional[str] = None) -> Optional[Subscriber]:
    """Add a new subscriber or reactivate existing one.
    
    Args:
        email: Email address of the subscriber
        unsubscribe_token: Optional token. If not provided, generates a new one.
    
    Returns:
        Subscriber instance if successful, None otherwise.
    """
    if unsubscribe_token is None:
        unsubscribe_token = generate_unsubscribe_token()
    
    data = database.add_subscriber(email, unsubscribe_token)
    if data:
        return Subscriber.from_dict(data)
    return None


def deactivate_subscriber(token: str) -> bool:
    """Deactivate a subscriber by unsubscribe token.
    
    Args:
        token: Unsubscribe token
        
    Returns:
        True if subscriber was deactivated, False otherwise.
    """
    return database.deactivate_subscriber(token)


def get_subscriber_count() -> int:
    """Get count of active subscribers."""
    return database.get_subscriber_count()


def is_email_subscribed(email: str) -> bool:
    """Check if an email is already subscribed and active.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email is subscribed and active, False otherwise.
    """
    subscriber = get_subscriber_by_email(email)
    return subscriber is not None and subscriber.is_active
