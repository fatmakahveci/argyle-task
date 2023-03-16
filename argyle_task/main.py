from bs4 import BeautifulSoup
import asyncio, httpx, json, logging, ssl, time

BASE_URL = "https://www.upwork.com"
LOGIN_URL = BASE_URL+"/ab/account-security/login"
# CREDENTIALS = {
#     "username": "bobbybackupy",
#     "password": "Argyleawesome123!",
#     "secret-key": "TheDude!@"
#     }

CREDENTIALS = {
    "username": "fatmaba@gmail.com",
    "password": "argyleSifresi1.",
    }

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
    'Upgrade-Insecure-Requests': '1'
    }

LOCAL_SSL_FILE_PATH = "/etc/ssl/cert.pem"

async def load_cloudflare_stuff(client, retryCount):
    """This function is needed to collect the cloudflare-needed cookies
    that will be used for bypassing cloudflare's bot-prevention mechanisms.

    Args:
        client (_type_): _description_
        retryCount (_type_): _description_

    Returns:
        _type_: _description_
    """
    cookies = {}
    headers = COMMON_HEADERS | {}
    
    for _ in range(retryCount):
        logger.debug(f"request headers: {headers}")
        logger.debug(f"request cookies: {cookies}")
        response = await client.get(headers=headers, cookies=cookies, url=LOGIN_URL)
        if response.status_code == 403:
            logger.warning("Received 403")
            logger.debug(response.headers)

        if 'set-cookie' in response.headers:
            for cookie in response.headers['set-cookie'].split(';'):
                cookieTokens = cookie.strip(' ').split("=", 1)
                if len(cookieTokens) == 2:
                    if cookieTokens[0] in CLOUDFLARE_COOKIE_NAMES:
                        cookies[cookieTokens[0]] = cookieTokens[1]

        if 'cf-ray' in response.headers:
            headers["cf-ray"] = response.headers["cf-ray"]
        
        if response.status_code == 200:
            break

        time.sleep(1)
    return (cookies, headers)


def createClient(caFilePath):
    """createClient

    Args:
        caFilePath (_type_): _description_

    Returns:
        _type_: _description_
    """
    context = ssl.create_default_context() # https://www.python-httpx.org/advanced/#ssl-certificates
    context.load_verify_locations(cafile=caFilePath)
    return httpx.AsyncClient(verify=context)

async def main(): 

    async with createClient(LOCAL_SSL_FILE_PATH) as client:

        cf_cookies, cf_headers = await load_cloudflare_stuff(client, retryCount=CLOUDFLARE_RETRY_COUNT)

        cookies = {} | cf_cookies
        headers = COMMON_HEADERS.copy() | cf_headers

        login_page_response = await client.get(url=LOGIN_URL, headers=headers, cookies=cookies)

        for cookie in login_page_response.headers['set-cookie'].split(';'):
            logging.debug(cookie)
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
        redirect_url = BASE_URL+json.loads(login_post_response.text)['redirectUrl']
        login_page_response = await client.get(url=redirect_url, headers=headers, follow_redirects=True)
        with open('/Users/fatmakhv/Desktop/out.html', 'w') as file:
            file.write(login_page_response.text)


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        )
    logger = logging.getLogger("task_logger")

    asyncio.run(main())
