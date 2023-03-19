
import httpx
import respx
from main import LOGIN_URL, COMMON_HEADERS, CLOUDFLARE_COOKIE_NAME
from main import create_challenge_json, create_login_json, get_cloudflare_headers_and_cookies, sign_in, UserCredentials

credentials = UserCredentials("username", "password", "secret-key")

## Cloudflare cookies
cf_cookie_val = "2b"
response_cf_cookies = {
    "set-cookie": f"{CLOUDFLARE_COOKIE_NAME}={cf_cookie_val};"
}

## Cloudflare headers
cf_ray_header_val = "1a"
response_cf_headers = response_cf_cookies | {
    "cf-ray": cf_ray_header_val,
}

## Two-factor auth cookies
tf_cookie_visitor_id_val = "3c"
tf_cookie_XSRF_TOKEN_val = "4e"
tf_cookie_enabled_ff = "5f"
tf_cookie_cookie_prefix = "6g"
response_tf_cookies = response_cf_cookies | {
    "visitor_id": tf_cookie_visitor_id_val,
    "XSRF-TOKEN": tf_cookie_XSRF_TOKEN_val,
    "enabled_ff": tf_cookie_cookie_prefix,
    "cookie_prefix": "",
}

## Two-factor auth headers
tf_header_x_odesk_csrf_token_val = "7h"
response_tf_headers = COMMON_HEADERS | response_cf_headers | {
    "referer": LOGIN_URL,
    "x-requested-with": 'XMLHttpRequest',
    "x-odesk-csrf-token": tf_header_x_odesk_csrf_token_val,
}

@respx.mock
async def test_cloudflare_headers_and_cookies_set(respx_mock):
    """when server returns 200 and all cookies are parsed, return cookies and headers

    Args:
        respx_mock (_type_): _description_
    """
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(200, headers=response_cf_headers))
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
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(403))
    respx_mock.get(LOGIN_URL).mock(return_value=httpx.Response(200, headers=response_cf_headers))
    async with httpx.AsyncClient() as client:
        headers, cookies = await get_cloudflare_headers_and_cookies(client=client, retryCount=10)
        assert 'cf-ray' in headers
        assert headers['cf-ray'] == cf_ray_header_val
        assert CLOUDFLARE_COOKIE_NAME in cookies
        assert cookies[CLOUDFLARE_COOKIE_NAME] == cf_cookie_val

@respx.mock
async def test_sign_in_with_two_factor_auth_success(respx_mock, mocker):
    """successful sign-in with two-factor auth

    Args:
        respx_mock (_type_): _description_
        mocker (_type_): _description_
    """
    expected_login_json = create_login_json(credentials.username, credentials.password)
    auth_token_val = "a1"
    challenge_data_val = "b2"
    login_response = {
        'success': 0,
        'mode': 'challenge',
        'authToken': auth_token_val,
        'challengeData': challenge_data_val,
        }
    respx_mock.post(
        url=LOGIN_URL,
        headers=response_cf_headers,
        json=expected_login_json
    ).mock(return_value=httpx.Response(status_code=200, json=login_response))

    expected_challenge_json = create_challenge_json(credentials.username, credentials.answer, auth_token_val, challenge_data_val)
    respx_mock.post(
        url=LOGIN_URL,
        headers=response_tf_headers,
        json=expected_challenge_json,
    ).mock(return_value=httpx.Response(status_code=200))
    async with httpx.AsyncClient() as client:
        is_signed_in = await sign_in(client, response_tf_headers, response_tf_cookies, credentials)
        assert is_signed_in == True

@respx.mock
async def test_sign_in_one_step_without_two_factor_auth_success(respx_mock):
    """successful sign-in without 2 factor
    
    Args:
        respx_mock (_type_): _description_
    """
    expected_login_json = create_login_json(credentials.username, credentials.password)
    auth_token_val = "a1"
    challenge_data_val = "b2"
    login_response = {
        'success': 1,
        'mode': 'challenge',
        'authToken': auth_token_val,
        'challengeData': challenge_data_val,
        }
    respx_mock.post(
        url=LOGIN_URL,
        headers=response_cf_headers,
        json=expected_login_json
    ).mock(return_value=httpx.Response(status_code=200, json=login_response))

@respx.mock
async def test_sign_in_with_non_200_error_fail(respx_mock):
    """failed sign-in with non-200 error
    
    Args:
        respx_mock (_type_): _description_
    """
    expected_login_json = create_login_json(credentials.username, credentials.password)
    auth_token_val = "a1"
    challenge_data_val = "b2"
    login_response = {
        'success': 0,
        'mode': 'challenge',
        'authToken': auth_token_val,
        'challengeData': challenge_data_val,
        }
    respx_mock.post(
        url=LOGIN_URL,
        headers=response_cf_headers,
        json=expected_login_json
    ).mock(return_value=httpx.Response(status_code=400, json=login_response))
    async with httpx.AsyncClient() as client:
        is_signed_in = await sign_in(client, response_tf_headers, response_tf_cookies, credentials)
        assert is_signed_in == False
