
import httpx
import respx
import pytest
import os
import sys
from respx.transports import MockTransport
import typing


RUNTESTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(
    RUNTESTS_DIR, '..', 'src'))
sys.path.insert(0, os.path.join(BASE_DIR, 'argyle_task'))

credentials = {
    "username": "username",
    "password": "password",
    "secret-key": "secret-key",
}

from main import BASE_URL, LOGIN_URL, PROFILE_URL, COMMON_HEADERS, get_cloudflare_headers_and_cookies, CLOUDFLARE_COOKIE_NAME


@respx.mock
async def test_client2(respx_mock):
    cf_ray_header_val = "1234"
    cf_cookie_val = "5678"
    response_headers = {
        "cf-ray": cf_ray_header_val,
        'set-cookie': f"{CLOUDFLARE_COOKIE_NAME}={cf_cookie_val};"
    }
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(200,
                                                               headers=response_headers))
    async with httpx.AsyncClient() as client:
        headers, cookies = await get_cloudflare_headers_and_cookies(client, 1)
        assert 'cf-ray' in headers
        assert headers['cf-ray'] == cf_ray_header_val
        assert CLOUDFLARE_COOKIE_NAME in cookies
        assert cookies[CLOUDFLARE_COOKIE_NAME] == cf_cookie_val



##
# Test: get_cloudflare_headers_and_cookies
# when mock client returns 200, and all cookies are parsed, return cookies and headers

# Test: get_cloudflare_headers_and_cookies
# when mock client returns 200 but no cookies are present, return no cookies

# Test: get_cloudflare_headers_and_cookies
# when mock client returns non 200, retry until it returns 200
##
# Test sign_in
# successful sign in with 2 factor

# Test sign_in
# - successful sign in without 2 factor

# Test sign_in
# - failed sign in with non-200 error
##
