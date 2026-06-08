"""Boldsign data models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr


class BoldsignCallbackEvent(BaseModel):
    """Boldsign Callback Event model."""

    data: dict[str, Any]
    event: dict[str, Any]
    document: dict[str, Any] | None = None

    @property
    def event_id(self) -> str | None:
        """Get the BoldSign event ID."""
        return self.event.get("id")

    @property
    def document_id(self) -> str | None:
        """Get the BoldSign document ID."""
        return self.data.get("documentId")

    @property
    def event_type(self) -> str | None:
        """Get the BoldSign event type."""
        return self.event.get("eventType")


class CreateUserSignLink(BaseModel):
    """Create User Sign Link request model."""

    signer_name: str
    signer_email: EmailStr


class CreateUserSignLinkResponse(BaseModel):
    """Create User Sign Link Response model."""

    document_id: str
    sign_link: str
