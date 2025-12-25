from functools import partial

import pytest
from django.urls import reverse


@pytest.fixture
def url():
    return reverse('user-verify')


@pytest.fixture
def request_verify_email(client, url):
    return partial(client.get, url, content_type='application/json')