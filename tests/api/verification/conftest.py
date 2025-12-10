import pytest
from django.urls import reverse


@pytest.fixture
def url():
    return reverse('user-verify')
