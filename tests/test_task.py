
import httpx
import os
import respx
import sys


RUNTESTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(
    RUNTESTS_DIR, '..', 'src'))
sys.path.insert(0, os.path.join(BASE_DIR, 'argyle_task'))
from main import BASE_URL, LOGIN_URL, PROFILE_URL, COMMON_HEADERS, get_cloudflare_headers_and_cookies, CLOUDFLARE_COOKIE_NAME

credentials = {
    "username": "username",
    "password": "password",
    "secret-key": "secret-key",
}

@respx.mock
async def test_cloudflare_headers_and_cookies_set(respx_mock):
    """when server returns 200 and all cookies are parsed, return cookies and headers

    Args:
        respx_mock (_type_): _description_
    """
    cf_ray_header_val = "1234"
    cf_cookie_val = "5678"
    response_headers = {
        "cf-ray": cf_ray_header_val,
        'set-cookie': f"{CLOUDFLARE_COOKIE_NAME}={cf_cookie_val};"
    }
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(200, headers=response_headers))
    async with httpx.AsyncClient() as client:
        headers, cookies = await get_cloudflare_headers_and_cookies(client=client, retryCount=1)
        assert 'cf-ray' in headers
        assert headers['cf-ray'] == cf_ray_header_val
        assert CLOUDFLARE_COOKIE_NAME in cookies
        assert cookies[CLOUDFLARE_COOKIE_NAME] == cf_cookie_val

@respx.mock
async def test_cloudflare_headers_and_cookies_missing(respx_mock):
    """when server returns 200, but no cookies are present, return no cookies

    Args:
        respx_mock (_type_): _description_
    """
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(200))
    async with httpx.AsyncClient() as client:
        headers, cookies = await get_cloudflare_headers_and_cookies(client=client, retryCount=1)
        assert 'cf-ray' not in headers
        assert CLOUDFLARE_COOKIE_NAME not in cookies

@respx.mock
async def test_cloudflare_headers_and_cookies_set_when_failed_request_retried(respx_mock):
    """when server returns non-200, retry until it returns 200

    Args:
        respx_mock (_type_): _description_
    """
    cf_ray_header_val = "1234"
    cf_cookie_val = "5678"
    response_headers = {
        "cf-ray": cf_ray_header_val,
        'set-cookie': f"{CLOUDFLARE_COOKIE_NAME}={cf_cookie_val};"
    }
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(403))
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(200, headers=response_headers))
    async with httpx.AsyncClient() as client:
        headers, cookies = await get_cloudflare_headers_and_cookies(client=client, retryCount=10)
        assert 'cf-ray' in headers
        assert headers['cf-ray'] == cf_ray_header_val
        assert CLOUDFLARE_COOKIE_NAME in cookies
        assert cookies[CLOUDFLARE_COOKIE_NAME] == cf_cookie_val

@respx.mock
async def test_sign_in_with_two_factor_auth_success(respx_mock):
    """successful sign-in with two-factor auth

    Args:
        respx_mock (_type_): _description_
    """
    pass

@respx.mock
async def test_sign_in_one_step_without_two_factor_auth_success(respx_mock):
    """successful sign-in without 2 factor
    
    Args:
        respx_mock (_type_): _description_
    """

    pass

@respx.mock
async def test_sign_in_with_non_200_error_fail(respx_mock):
    """failed sign-in with non-200 error
    
    Args:
        respx_mock (_type_): _description_
    """
    pass