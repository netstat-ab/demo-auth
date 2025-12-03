import string
from functools import partial

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from app.constants import text

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def configure_email_backend(settings):
    settings.EMAIL_SERVICE_BACKEND = 'tests.mocks.email.EmailServiceMock'


@pytest.fixture
def url():
    return reverse('user-register')