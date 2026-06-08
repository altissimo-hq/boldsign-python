"""boldsign-python client."""

from __future__ import annotations

from altissimo.boldsign.client import BoldsignClient, BoldsignSettings
from altissimo.boldsign.exceptions import BoldsignConfigurationError, BoldsignError
from altissimo.boldsign.models import (
    BoldsignCallbackEvent,
    CreateUserSignLink,
    CreateUserSignLinkResponse,
)

__all__ = [
    "BoldsignCallbackEvent",
    "BoldsignClient",
    "BoldsignConfigurationError",
    "BoldsignError",
    "BoldsignSettings",
    "CreateUserSignLink",
    "CreateUserSignLinkResponse",
]
