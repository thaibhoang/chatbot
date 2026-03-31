import pytest
from pydantic import ValidationError

from app.models.query import QueryRequest


def test_query_request_requires_customer_id() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(project_id="11111111-1111-1111-1111-111111111111", query="hello")


def test_query_request_rejects_blank_customer_id() -> None:
    with pytest.raises(ValidationError):
        QueryRequest(project_id="11111111-1111-1111-1111-111111111111", customer_id="  ", query="hello")
