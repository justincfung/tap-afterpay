"""Stream type classes for tap-afterpay."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_afterpay.client import afterpayStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class PaymentsStream(afterpayStream):
    """Define payments stream."""
    name = "payments"
    path = "/v2/payments"
    primary_keys = ["id"]
    replication_key = "id"
    schema_filepath = SCHEMAS_DIR / "payments.json"