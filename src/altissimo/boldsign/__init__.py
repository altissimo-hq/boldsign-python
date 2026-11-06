"""boldsign-python client."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from altissimo.boldsign.client import BoldsignClient, BoldsignSettings
from altissimo.boldsign.exceptions import BoldsignConfigurationError, BoldsignError
from altissimo.boldsign.models import (
    BoldsignCallbackEvent,
    CreateUserSignLink,
    CreateUserSignLinkResponse,
)

try:
    __version__ = version("boldsign-python")
except PackageNotFoundError:  # pragma: no cover — editable install without metadata
    __version__ = "0.1.0"

__all__ = [
    "BoldsignCallbackEvent",
    "BoldsignClient",
    "BoldsignConfigurationError",
    "BoldsignError",
    "BoldsignSettings",
    "CreateUserSignLink",
    "CreateUserSignLinkResponse",
    "__version__",
]
