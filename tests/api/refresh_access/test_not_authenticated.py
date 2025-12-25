from functools import partial

import pytest


@pytest.fixture
def request_refresh_access(client, url):
    return partial(client.post, url, content_type='application/json')


def test_it_returns_401(request_refresh_access):
    response = request_refresh_access()
    assert response.status_code == 401
