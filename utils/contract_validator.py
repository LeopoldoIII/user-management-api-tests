"""
contract_validator.py — OpenAPI Contract Oracle

Parses contract_api.yml with PyYAML and validates API response bodies against
the defined schemas using jsonschema. This wires the contract as an *active
oracle* rather than a passive reference document.

Usage:
    from utils.contract_validator import ContractValidator

    _contract = ContractValidator()

    # In a Then step:
    _contract.assert_response("/users", "post", 201, response.json())
"""

import os
import yaml
import jsonschema

_CONTRACT_PATH = os.path.join(os.path.dirname(__file__), "..", "contract_api.yml")


class ContractValidator:
    """
    Loads the OpenAPI contract once and exposes a single assertion method.

    Supported path patterns (matching contract_api.yml):
        "/users"          — GET / POST
        "/users/{email}"  — GET / PUT / DELETE
    """

    def __init__(self, contract_path: str = _CONTRACT_PATH):
        with open(contract_path, "r") as fh:
            self._spec = yaml.safe_load(fh)

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    def assert_response(
        self,
        openapi_path: str,
        method: str,
        status_code: int,
        body: object,
    ) -> None:
        """
        Assert that ``body`` conforms to the contract schema for the given
        (openapi_path, method, status_code) combination.

        Args:
            openapi_path:  OpenAPI path string, e.g. "/users" or "/users/{email}"
            method:        HTTP method in lower-case, e.g. "get", "post", "put"
            status_code:   HTTP status code as int, e.g. 200, 201, 400
            body:          Parsed JSON body (dict or list). Pass ``None`` for 204.

        Raises:
            AssertionError: if body does not match the contract schema.
        """
        schema = self._get_response_schema(openapi_path, method, status_code)

        if schema is None:
            # 204 No Content or a status code with no body defined — nothing to check
            return

        try:
            jsonschema.validate(instance=body, schema=schema)
        except jsonschema.ValidationError as exc:
            raise AssertionError(
                f"Response body does not match OpenAPI contract schema.\n"
                f"  Operation: {method.upper()} {openapi_path} → HTTP {status_code}\n"
                f"  Problem:   {exc.message}\n"
                f"  Body:      {body}"
            ) from exc

    # ──────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────

    def _resolve_ref(self, ref: str) -> dict:
        """
        Resolves a local JSON Reference like '#/components/schemas/User'
        to the actual schema dict in the loaded spec.
        """
        parts = ref.lstrip("#/").split("/")
        node = self._spec
        for part in parts:
            node = node[part]
        return node

    def _deep_resolve(self, schema: object) -> object:
        """
        Recursively replaces every ``$ref`` in a schema tree with the
        referenced schema, producing a fully-inlined dict that jsonschema
        can validate without a resolver.
        """
        if isinstance(schema, dict):
            if "$ref" in schema:
                return self._deep_resolve(self._resolve_ref(schema["$ref"]))
            return {key: self._deep_resolve(value) for key, value in schema.items()}
        if isinstance(schema, list):
            return [self._deep_resolve(item) for item in schema]
        return schema

    def _get_response_schema(
        self,
        openapi_path: str,
        method: str,
        status_code: int,
    ) -> dict | None:
        """
        Looks up and fully resolves the response JSON Schema for a specific
        (path, method, status_code) combination.

        Returns None when no ``application/json`` body is defined
        (e.g. 204 No Content).
        """
        paths = self._spec.get("paths", {})
        path_item = paths.get(openapi_path, {})
        operation = path_item.get(method.lower(), {})
        responses = operation.get("responses", {})
        response_spec = responses.get(str(status_code), {})
        content = response_spec.get("content", {})
        json_content = content.get("application/json", {})
        raw_schema = json_content.get("schema")

        if raw_schema is None:
            return None

        return self._deep_resolve(raw_schema)
