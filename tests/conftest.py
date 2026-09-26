import pytest

from demo.evaluation.mock_provider import mock_bailian


@pytest.fixture
def bailian_mock():
    with mock_bailian() as fake:
        yield fake
