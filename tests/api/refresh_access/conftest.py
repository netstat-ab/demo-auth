from functools import partial

import pytest
from django.urls import reverse

from tests.api.utils import authorization_header


@pytest.fixture
def url():
    return reverse('user-refresh-access-token')


@pytest.fixture
def request_refresh_access(client, url, authenticated_user_access_token):
    return partial(
        client.post,
        url,
        content_type='application/json',
        headers=authorization_header(authenticated_user_access_token),
    )
