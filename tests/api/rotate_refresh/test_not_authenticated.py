from functools import partial

import pytest


@pytest.fixture
def request_rotate_refresh(client, url):
    return partial(client.post, url, content_type='application/json')


def test_it_returns_401(request_rotate_refresh):
    response = request_rotate_refresh()
    assert response.status_code == 401
