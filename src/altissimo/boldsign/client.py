"""Boldsign API client."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from altissimo.boldsign.exceptions import BoldsignConfigurationError

if TYPE_CHECKING:
    from boldsign.models.document_created import DocumentCreated
    from boldsign.models.document_properties import DocumentProperties
    from boldsign.models.embedded_signing_link import EmbeddedSigningLink


@dataclass(frozen=True)
class BoldsignSettings:
    """Settings for Boldsign client."""

    api_key: str
    templates: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(
        cls,
        *,
        api_key_env: str = "BOLDSIGN_API_KEY",
        fallback_api_key_env: str = "BOLDSIGN_LMM_API_KEY",
        templates: dict[str, str] | None = None,
    ) -> BoldsignSettings:
        """Build settings from environment variables."""
        api_key = os.environ.get(api_key_env) or os.environ.get(fallback_api_key_env, "")
        if not api_key:
            raise BoldsignConfigurationError(f"Neither {api_key_env} nor {fallback_api_key_env} is set")
        return cls(api_key=api_key, templates=templates or {})


class BoldsignClient:
    """Thin Boldsign API adapter."""

    def __init__(self, settings: BoldsignSettings | None = None) -> None:
        """Initialize the BoldsignClient."""
        self._settings = settings

    def _get_settings(self) -> BoldsignSettings:
        if self._settings is None:
            self._settings = BoldsignSettings.from_env()
        return self._settings

    def _build_api_client(self) -> Any:
        from boldsign.api_client import ApiClient
        from boldsign.configuration import Configuration

        configuration = Configuration(api_key=self._get_settings().api_key)
        return ApiClient(configuration)

    def create_embedded_signing_link(self, document_id: str, signing_email: str) -> EmbeddedSigningLink:
        """Create an embedded signing link for a document."""
        from boldsign.api.document_api import DocumentApi

        with self._build_api_client() as api_client:
            document_api = DocumentApi(api_client)
            response = document_api.get_embedded_sign_link(document_id=document_id, signer_email=signing_email)
            return response

    def get_document_properties(self, document_id: str) -> DocumentProperties:
        """Get document properties by document id."""
        from boldsign.api.document_api import DocumentApi

        with self._build_api_client() as api_client:
            document_api = DocumentApi(api_client)
            response = document_api.get_properties(document_id=document_id)
            return response

    def send_using_template(self, signer_name: str, signer_email: str, template_id: str) -> DocumentCreated:
        """Send a document for signature using a template."""
        from boldsign.api.template_api import TemplateApi
        from boldsign.models.role import Role
        from boldsign.models.send_for_sign_from_template_form import SendForSignFromTemplateForm

        with self._build_api_client() as api_client:
            template_api = TemplateApi(api_client)

            role = Role(
                roleIndex=1,
                signerRole="Customer",
                signerName=signer_name,
                signerEmail=signer_email,
            )
            form = SendForSignFromTemplateForm(
                roles=[role],
                disableEmails=True,
                disableSMS=True,
                enableReassign=False,
            )

            response = template_api.send_using_template(
                template_id=template_id,
                send_for_sign_from_template_form=form,
            )
            return response
