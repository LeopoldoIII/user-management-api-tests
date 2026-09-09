"""
API Client — Wrapper

Centralizes:
- Base URL per environment
- Content-Type header
- Authentication header (only DELETE requires it according to the contract)
- Storage of the last response in context.response
"""

import requests


class ApiClient:
    """
    API Client Wrapper

    Using `requests.Session()` instead of simple `requests.get()` provides connection pooling
    It improves performance when running hundreds of tests because it reuses 
    the connection
    """

    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get(self, path: str) -> requests.Response:
        return self.session.get(self._url(path))

    def post(self, path: str, json: dict = None) -> requests.Response:
        return self.session.post(self._url(path), json=json)

    def put(self, path: str, json: dict = None) -> requests.Response:
        return self.session.put(self._url(path), json=json)

    def delete(self, path: str, token: str = None) -> requests.Response:
        """
        DELETE requires the 'Authentication' header according to the contract
        - token=valid   -> Authentication: Token
        - token=None    -> no header (expects 401)
        - token=invalid -> header with incorrect value (expects 401)
        """
        headers = {}
        if token is not None:
            headers["Authentication"] = token
        return self.session.delete(self._url(path), headers=headers)
