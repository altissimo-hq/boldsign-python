"""Boldsign exceptions."""

from __future__ import annotations


class BoldsignError(Exception):
    """Base exception for Boldsign library."""


class BoldsignConfigurationError(BoldsignError):
    """Exception raised when Boldsign configuration is missing or invalid."""
