"""afterpay Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class afterpayAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for AfterPay."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the AfterPay API."""
        return {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "scope": "merchant_api_v2",
            "grant_type": "client_credentials",
        }

    @classmethod
    def create_for_stream(cls, stream) -> afterpayAuthenticator:
        """Instantiate an authenticator for a specific Singer stream."""
        return cls(
            stream=stream,
            auth_endpoint="https://merchant-auth.afterpay.com/v2/oauth2/token",
        )