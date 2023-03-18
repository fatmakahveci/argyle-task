
import asyncio
import httpx
import json
import logging
import ssl
import time
import database
from typing import Dict, Optional, List
from user import User


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger("task_logger")


BASE_URL = "https://www.upwork.com"
LOGIN_URL = BASE_URL+"/ab/account-security/login"
PROFILE_URL = BASE_URL+"/freelancers/"


CLOUDFLARE_RETRY_COUNT = 10
CLOUDFLARE_COOKIE_NAMES = ['__cf_bm']
COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0',
    'content-type': 'application/json',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Set-Fetch-Dest': 'document',
    'Set-Fetch-Mode': 'navigate',
    'Set-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
}


class UserCredentials:
    def __init__(self, username, password, answer):
        self.username = username
        self.password = password
        self.answer = answer


async def get_cloudflare_headers_and_cookies(client: httpx.AsyncClient, retryCount: int):
    """This function is needed to collect the cloudflare-needed cookies
    that will be used for bypassing cloudflare's bot-prevention mechanisms.

    Args:
        client (_type_): _description_
        retryCount (_type_): _description_

    Returns:
        _type_: _description_
    """
    headers = COMMON_HEADERS | {}
    cookies = {}

    for _ in range(retryCount):
        response = await client.get(headers=headers, cookies=cookies, url=LOGIN_URL)
        if 'set-cookie' in response.headers:
            for cookie in response.headers['set-cookie'].split(';'):
                cookieTokens = cookie.strip(' ').split("=", 1)
                if len(cookieTokens) == 2:
                    if cookieTokens[0] in CLOUDFLARE_COOKIE_NAMES:
                        cookies[cookieTokens[0]] = cookieTokens[1]
                else:
                    logger.error(
                        f"Could not parse set-cookie header: {cookie}")

        if 'cf-ray' in response.headers:
            headers["cf-ray"] = response.headers["cf-ray"]
        else:
            logger.error(f"Could not find cf-ray in headers")

        if response.status_code == httpx.codes.OK:
            logger.info(
                f"Received {response.status_code}: Headers and cookies are taken.")
            break

        logger.warning(
            f"Received {response.status_code} while getting cloudflare cookies")
        time.sleep(1)
    
    return [headers, cookies]


def create_client(certificate_path: str):
    """_summary_

    Args:
        caFilePath (_type_): _description_

    Returns:
        httpx.AsyncClient: _description_
    """
    context = ssl.create_default_context(
    )  # https://www.python-httpx.org/advanced/#ssl-certificates
    context.load_verify_locations(cafile=certificate_path)
    return httpx.AsyncClient(verify=context)


async def get_headers_and_cookies(client: httpx.AsyncClient):
    """_summary_

    Returns:
        _type_: _description_
    """
    cf_headers, cf_cookies = await get_cloudflare_headers_and_cookies(client, retryCount=CLOUDFLARE_RETRY_COUNT)

    cookies = {} | cf_cookies
    headers = {} | COMMON_HEADERS | cf_headers

    response = await client.get(url=LOGIN_URL, headers=headers, cookies=cookies)

    if response.status_code == httpx.codes.OK:
        logger.info(
            f"Received {response.status_code}: Headers and cookies are taken.")
        for cookie in response.headers['set-cookie'].split(';'):
            # logging.debug(cookie)
            if "visitor_id" in cookie:
                cookies["visitor_id"] = cookie.split("=")[1]
            if "XSRF-TOKEN" in cookie:
                cookies["XSRF-TOKEN"] = cookie.split("XSRF-TOKEN=")[1]
            if "enabled_ff" in cookie:
                cookies["enabled_ff"] = cookie.split("=")[1]

        headers['referer'] = LOGIN_URL
        headers['x-requested-with'] = 'XMLHttpRequest'
        headers['x-odesk-csrf-token'] = cookies["XSRF-TOKEN"]

        cookies["cookie_prefix"] = ""
    else:
        logger.error(
            f"Received {response.status_code}: Headers and cookies cannot be taken.")
    return [headers, cookies]


def create_login_json(username: str, password: str) -> Dict[str, str]:
    return {
        "login": {
            "username": username,
            "password": password,
            "mode": "password",
        }
    }


def create_challenge_json(username: str, answer: str, authToken: str, challengeData: str) -> Dict[str, str]:
    return {
        'login': {
            "deviceAuthorization": {
                "answer": answer,
                "remember": True,
            },
            "mode": "challenge",
            "username": username,
            "authToken": authToken,
            "challengeData": challengeData,
        }
    }


def response_error_str(message, response):
    return f"""
            {message}.
            response code: {response.status_code}
            headers: {response.headers}
            body: {response.text}
            """


async def sign_in(client, headers, cookies, credentials: UserCredentials) -> bool:
    """
    """

    login_response = await client.post(
        url=LOGIN_URL,
        headers=headers,
        cookies=cookies,
        follow_redirects=True,
        timeout=50,
        json=create_login_json(
            credentials.username, credentials.password)
    )

    if login_response.status_code != httpx.codes.OK:
        logger.error(response_error_str(
            "username & password login failed", login_response))
        return False

    login_response_json = json.loads(login_response.text)

    if login_response_json['success'] == 1:
        # sign in complete. no need for two factor auth
        return True

    if 'mode' not in login_response_json or 'authToken' not in login_response_json or 'challengeData' not in login_response_json:
        logger.error(response_error_str(
            "Unexpected JSON in login response", login_response))
        return False

    two_factor_response = await client.post(
        url=LOGIN_URL,
        headers=headers,
        cookies=cookies,
        follow_redirects=True,
        timeout=50,
        json=create_challenge_json(
            credentials.username, credentials.answer, login_response_json['authToken'], login_response_json['challengeData']),
    )

    if two_factor_response.status_code != httpx.codes.OK:
        logger.error(response_error_str(
            "two factor challenge failed", two_factor_response))
        return False

    return True


async def get_profile_text(client, headers, cookies, credentials: UserCredentials) -> Optional[User]:
    response = await client.get(url=PROFILE_URL, headers=headers, follow_redirects=True)

    if response.status_code != httpx.codes.OK:
        logger.error(response_error_str(
            "Could not load profile page", response))
        return None

    user_id = str(response.url).split('/')[-1]  # user ID
    profile_url = f"https://www.upwork.com/freelancers/api/v1/freelancer/profile/{user_id}/details"
    response = await client.get(url=profile_url, headers=headers, cookies=cookies)

    if response.status_code != httpx.codes.OK:
        logger.error(response_error_str(
            "Could not fetch user profile details", response))
        return None

    return User(username=credentials.username, profile_response_json=json.loads(response.text))


async def crawl_user_data(client: httpx.AsyncClient, credentials: UserCredentials) -> Optional[User]:
    logger.info(f"Crawling data for {credentials.username}")
    headers, cookies = await get_headers_and_cookies(client)
    is_signed_in = await sign_in(client, headers, cookies, credentials)
    if not is_signed_in:
        logger.error(
            f"Crawling of {credentials.username} failed due to sign in error")
        return None

    user = await get_profile_text(client, headers, cookies, credentials)
    if user is None:
        logger.error(
            f"Crawling of {credentials.username} failed due to user profile load error")
        return None

    return user


async def crawl_users(certificate_path, credentials: List[UserCredentials]):
    users = []
    async with create_client(certificate_path) as client:
        tasks = []
        for c in credentials:
            tasks.append(crawl_user_data(client=client, credentials=c))

        for user in await asyncio.gather(*tasks):
            if user is not None:
                users.append(user)
    return users


def crawl_and_save_users(certificate_path, credentials: List[UserCredentials]):
    database.create_table()
    users = asyncio.run(crawl_users(certificate_path=certificate_path,
                                    credentials=credentials))
    database.insert_users(users)


if __name__ == "__main__":
    certificate_path = "/etc/ssl/cert.pem"
    credentials = [UserCredentials(
        username="fatmakahvecim@gmail.com", password="argyleSifresi1.", answer="pufi")]
    crawl_and_save_users(certificate_path=certificate_path,
                         credentials=credentials)
