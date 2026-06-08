"""Unit tests for Boldsign clients and models."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from altissimo.boldsign import (
    BoldsignCallbackEvent,
    BoldsignClient,
    BoldsignConfigurationError,
    BoldsignSettings,
    CreateUserSignLink,
    CreateUserSignLinkResponse,
)


def test_boldsign_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test BoldsignSettings environment variables parsing and custom naming."""
    monkeypatch.delenv("BOLDSIGN_API_KEY", raising=False)
    monkeypatch.delenv("BOLDSIGN_LMM_API_KEY", raising=False)

    with pytest.raises(BoldsignConfigurationError, match="Neither BOLDSIGN_API_KEY nor BOLDSIGN_LMM_API_KEY is set"):
        BoldsignSettings.from_env()

    # Test legacy/fallback
    monkeypatch.setenv("BOLDSIGN_LMM_API_KEY", "fallback-key")
    settings = BoldsignSettings.from_env()
    assert settings.api_key == "fallback-key"
    assert settings.templates == {}

    # Test modern takes preference
    monkeypatch.setenv("BOLDSIGN_API_KEY", "modern-key")
    settings = BoldsignSettings.from_env()
    assert settings.api_key == "modern-key"

    # Test custom environment variable names
    monkeypatch.setenv("MY_CUSTOM_KEY", "custom-key")
    settings = BoldsignSettings.from_env(
        api_key_env="MY_CUSTOM_KEY",
        fallback_api_key_env="OTHER_FALLBACK_KEY",
    )
    assert settings.api_key == "custom-key"

    # Test templates registry injection
    tpls = {"health": "tpl-123"}
    settings = BoldsignSettings.from_env(templates=tpls)
    assert settings.templates == tpls


@patch("boldsign.api_client.ApiClient")
@patch("boldsign.api.document_api.DocumentApi")
def test_create_embedded_signing_link(mock_document_api_cls: MagicMock, mock_api_client_cls: MagicMock) -> None:
    """Test creating an embedded signing link wraps the SDK correctly."""
    mock_api_client = MagicMock()
    mock_api_client_cls.return_value = mock_api_client
    # Mocking context manager __enter__
    mock_api_client.__enter__.return_value = mock_api_client

    mock_doc_api = MagicMock()
    mock_document_api_cls.return_value = mock_doc_api

    mock_response = MagicMock()
    mock_doc_api.get_embedded_sign_link.return_value = mock_response

    settings = BoldsignSettings(api_key="test-api-key")
    client = BoldsignClient(settings)

    result = client.create_embedded_signing_link("doc-123", "user@example.com")

    assert result is mock_response
    mock_document_api_cls.assert_called_once_with(mock_api_client)
    mock_doc_api.get_embedded_sign_link.assert_called_once_with(document_id="doc-123", signer_email="user@example.com")


@patch("boldsign.api_client.ApiClient")
@patch("boldsign.api.document_api.DocumentApi")
def test_get_document_properties(mock_document_api_cls: MagicMock, mock_api_client_cls: MagicMock) -> None:
    """Test getting document properties wraps the SDK correctly."""
    mock_api_client = MagicMock()
    mock_api_client_cls.return_value = mock_api_client
    mock_api_client.__enter__.return_value = mock_api_client

    mock_doc_api = MagicMock()
    mock_document_api_cls.return_value = mock_doc_api

    mock_response = MagicMock()
    mock_doc_api.get_properties.return_value = mock_response

    settings = BoldsignSettings(api_key="test-api-key")
    client = BoldsignClient(settings)

    result = client.get_document_properties("doc-123")

    assert result is mock_response
    mock_document_api_cls.assert_called_once_with(mock_api_client)
    mock_doc_api.get_properties.assert_called_once_with(document_id="doc-123")


@patch("boldsign.api_client.ApiClient")
@patch("boldsign.api.template_api.TemplateApi")
@patch("boldsign.models.role.Role")
@patch("boldsign.models.send_for_sign_from_template_form.SendForSignFromTemplateForm")
def test_send_using_template(
    mock_form_cls: MagicMock,
    mock_role_cls: MagicMock,
    mock_template_api_cls: MagicMock,
    mock_api_client_cls: MagicMock,
) -> None:
    """Test sending document using template wraps the SDK correctly."""
    mock_api_client = MagicMock()
    mock_api_client_cls.return_value = mock_api_client
    mock_api_client.__enter__.return_value = mock_api_client

    mock_template_api = MagicMock()
    mock_template_api_cls.return_value = mock_template_api

    mock_role = MagicMock()
    mock_role_cls.return_value = mock_role

    mock_form = MagicMock()
    mock_form_cls.return_value = mock_form

    mock_response = MagicMock()
    mock_template_api.send_using_template.return_value = mock_response

    settings = BoldsignSettings(api_key="test-api-key")
    client = BoldsignClient(settings)

    result = client.send_using_template("Test User", "test@example.com", "tpl-123")

    assert result is mock_response
    mock_role_cls.assert_called_once_with(
        roleIndex=1,
        signerRole="Customer",
        signerName="Test User",
        signerEmail="test@example.com",
    )
    mock_form_cls.assert_called_once_with(
        roles=[mock_role],
        disableEmails=True,
        disableSMS=True,
        enableReassign=False,
    )
    mock_template_api.send_using_template.assert_called_once_with(
        template_id="tpl-123",
        send_for_sign_from_template_form=mock_form,
    )


def test_models_validation() -> None:
    """Test validations for CreateUserSignLink request/response models."""
    # 1. Validation error on bad email
    with pytest.raises(ValidationError):
        CreateUserSignLink(signer_name="Valid Name", signer_email="invalid-email")

    # 2. Correct validation
    req = CreateUserSignLink(signer_name="John Doe", signer_email="john@example.com")
    assert req.signer_name == "John Doe"
    assert req.signer_email == "john@example.com"

    # 3. CreateUserSignLinkResponse parsing
    res = CreateUserSignLinkResponse(document_id="doc-999", sign_link="https://sign.here")
    assert res.document_id == "doc-999"
    assert res.sign_link == "https://sign.here"


def test_boldsign_callback_event() -> None:
    """Test BoldsignCallbackEvent property parsing and accessors."""
    payload = {
        "event": {
            "id": "event-abc",
            "eventType": "Signed",
        },
        "data": {
            "documentId": "doc-xyz",
            "otherField": "value",
        },
        "document": {
            "documentId": "doc-xyz",
            "title": "Consent Form",
        },
    }

    event = BoldsignCallbackEvent(**payload)

    assert event.event_id == "event-abc"
    assert event.document_id == "doc-xyz"
    assert event.event_type == "Signed"
    assert event.document == {"documentId": "doc-xyz", "title": "Consent Form"}
    assert event.data == {"documentId": "doc-xyz", "otherField": "value"}
