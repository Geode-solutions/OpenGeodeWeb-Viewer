import pytest
from vtkw_server import _Server


@pytest.fixture
def client():
    client = app.test_client()
    yield client
