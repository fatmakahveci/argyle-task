from bs4 import BeautifulSoup
import asyncio, httpx, logging, requests
import json

BASE_URL = "https://www.upwork.com"
LOGIN_URL = BASE_URL+"/ab/account-security/login"
CREDENTIALS = {
    "username": "bobbybackupy",
    "password": "Argyleawesome123!",
    "secret-key": "TheDude!@"
    }

CREDENTIALS = {
    "username": "fatmaba@gmail.com",
    "password": "argyleSifresi1.",
    }

CLOUDFLARE_COOKIE_NAMES = ['__cf_bm']

COMMON_HEADERS = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'content-type': 'application/json',
        }

async def load_cloudflare_stuff(client):
    response = await client.get(headers=COMMON_HEADERS, url=LOGIN_URL)
    if response.status_code == 403:
            logger.warning("Received 403")
        
    cookies = {}
    headers = {}
    for cookie in response.headers['set-cookie'].split(';'):
        cookieTokens = cookie.strip(' ').split("=", 1)
        if len(cookieTokens) == 2:
            if cookieTokens[0] in CLOUDFLARE_COOKIE_NAMES:
                cookies[cookieTokens[0]] = cookieTokens[1]

    if response.headers["cf-ray"]:
            headers["cf-ray"] = response.headers["cf-ray"]

    print(f"cf cookies: {cookies}")
    return (cookies, headers)


async def main():
    async with httpx.AsyncClient() as client:
        
        cf_cookies, cf_headers = await load_cloudflare_stuff(client)

        cookies = {} | cf_cookies
        headers = COMMON_HEADERS.copy() | cf_headers
        
        login_page_response = await client.get(url=LOGIN_URL, headers=headers, cookies=cookies)

        for cookie in login_page_response.headers['set-cookie'].split(';'):
            logging.info(cookie)
            if "visitor_id" in cookie:
                cookies["visitor_id"] = cookie.split("=")[1]
            if "XSRF-TOKEN" in cookie:
                cookies["XSRF-TOKEN"] = cookie.split("XSRF-TOKEN=")[1]
            if "enabled_ff" in cookie:
                cookies["enabled_ff"] = cookie.split("=")[1]

        headers['referer'] = LOGIN_URL
        headers['x-requested-with'] = 'XMLHttpRequest'
        headers['x-odesk-csrf-token'] = cookies["XSRF-TOKEN"]

        cookies["cookie_prefix"]=""
        
        login_post_response = await client.post(
                                url=LOGIN_URL,
                                headers=headers,
                                cookies=cookies,
                                follow_redirects=False,
                                timeout=50,
                                json={
                                    "login": {
                                        "password": f"{CREDENTIALS['password']}",
                                        "mode": "password",
                                        "username": f"{CREDENTIALS['username']}",
                                        "elapsedTime":289170,
                                        }
                                    }
        )

        # print(login_post_response.text)
        redirect_url = BASE_URL+json.loads(login_post_response.text)['redirectUrl']
        login_page_response = await client.get(url=redirect_url, headers=headers, follow_redirects=True)


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        )
    logger = logging.getLogger("task_logger")

    asyncio.run(main())
