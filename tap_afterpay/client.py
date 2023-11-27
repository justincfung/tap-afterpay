"""REST client handling, including flexportStream base class."""

from urllib.parse import urlparse, parse_qs
import logging

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached
from functools import cached_property

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_afterpay.auth import afterpayAuthenticator

from http import HTTPStatus
from singer_sdk.exceptions import RetriableAPIError


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class afterpayStream(RESTStream):
    """flexport stream class."""
    

    url_base = "https://global-api.afterpay.com"
    # page_limit = 100
    records_jsonpath = "$.results[*]"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.nextPageUrl"  # Or override `get_next_page_token`.
    extra_retry_statuses = [HTTPStatus.PRECONDITION_FAILED, HTTPStatus.TOO_MANY_REQUESTS]

    @cached_property
    def authenticator(self) -> afterpayAuthenticator:
        """Return a new authenticator object."""
        return afterpayAuthenticator.create_for_stream(self)

    def validate_response(self, response):
        # Requires re-authentication
        if response.status_code == HTTPStatus.PRECONDITION_FAILED:
            self.authenticator = afterpayAuthenticator.create_for_stream(self)
        super().validate_response(response)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        
        res_json = response.json()
        
        page_limit = res_json.get('limit')  
        if (previous_token == None):
            previous_token = 1 
        if res_json:
            next_page_url = res_json.get('nextPageUrl')
            parsed_next_page_url = urlparse(next_page_url)
            next_page_token = parse_qs(parsed_next_page_url.query)
        else:
            next_page_token = None
        previous_token += 1
        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        
        if not next_page_token:
            params: dict = {
                "includeNextLink":"true"
            }
        else:
            params: dict = {
                "cursor":"cursor",
                "includeNextLink":"true"
            }
            
        if next_page_token:
            # print(next_page_token)
            cursor = next_page_token.get('cursor')[0]
            include_next_link = next_page_token.get('includeNextLink')[0]
            
            params["cursor"] = cursor
            params["includeNextLink"] = include_next_link
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        # TODO: Delete this method if not needed.
        return row