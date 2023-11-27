"""afterpay tap class."""

from __future__ import annotations

from typing import List


from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_afterpay.streams import PaymentsStream

STREAM_TYPES = [PaymentsStream]

class Tapafterpay(Tap):
    """afterpay tap class."""

    name = "tap-afterpay"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="Client ID passed to AfterPay OAuth2",
        ),
        th.Property(
            "start_date",
            th.DateType,
            default='2022-01-01',   
            description="The project start date",
        ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://global-api.afterpay.com",
            description="The base url for the AfterPay API service",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    Tapafterpay.cli()