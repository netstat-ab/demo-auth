from functools import partial

import pytest
from django.urls import reverse


@pytest.fixture
def url():
    return reverse('user-login')


@pytest.fixture
def request_login(client, url):
    return partial(client.post, url, content_type='application/json')
