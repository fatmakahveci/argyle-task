from bs4 import BeautifulSoup
from datetime import datetime
import asyncio, httpx, json, logging, os, ssl, time
import database

BASE_URL = "https://www.upwork.com"
LOGIN_URL = BASE_URL+"/ab/account-security/login"
PROFILE_URL = BASE_URL+"/freelancers/"

CREDENTIALS = {
    "username": "fatmakahvecim@gmail.com",
    "password": "argyleSifresi1.",
    "answer": "pufi",
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
    'Upgrade-Insecure-Requests': '1',
    }

LOCAL_SSL_FILE_PATH = "/etc/ssl/cert.pem"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

class User:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.username = CREDENTIALS['username'] # (unique) email or username
        self.title = ""
        self.description = ""
        self.country = ""
        self.city = ""
        self.time_zone = ""
        self.skills = []
        self.hourly_rate = ""
        self.languages = []
        self.certificates = []
        self.employment_history = []
        self.education = []
        self.job_categories = []
        self.creation_date = ""
        self.updated_on = ""
        self.profile = ""

    def __str__(self):
        user = f"""
        id: {self.id}
        name: {self.name}
        title: {self.title}
        description: {self.description}
        country: {self.country}
        city: {self.city}
        time_zone: {self.time_zone}
        skills: {self.skills}
        hourly_rate: {self.hourly_rate}
        languages: {self.languages}
        certificates: {self.certificates}
        employment history: {self.employment_history}
        education: {self.education}
        job categories: {self.job_categories}
        creation date: {self.creation_date}
        updated on: {self.updated_on}
        """
        return user

async def load_cloudflare_stuff(client, retryCount: int):
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
        if response.status_code != 200:
            logger.info(f"Received {response.status_code}: Headers and cookies cannot be taken.")

        if 'set-cookie' in response.headers:
            for cookie in response.headers['set-cookie'].split(';'):
                cookieTokens = cookie.strip(' ').split("=", 1)
                if len(cookieTokens) == 2:
                    if cookieTokens[0] in CLOUDFLARE_COOKIE_NAMES:
                        cookies[cookieTokens[0]] = cookieTokens[1]

        if 'cf-ray' in response.headers:
            headers["cf-ray"] = response.headers["cf-ray"]
        
        if response.status_code == 200:
            logger.info(f"Received {response.status_code}: Headers and cookies are taken.")
            break

        time.sleep(1)
    return [headers, cookies]

def createClient(caFilePath: str):
    """_summary_

    Args:
        caFilePath (_type_): _description_

    Returns:
        _type_: _description_
    """
    context = ssl.create_default_context() # https://www.python-httpx.org/advanced/#ssl-certificates
    context.load_verify_locations(cafile=caFilePath)
    return httpx.AsyncClient(verify=context)

async def get_headers_and_cookies(client):
    """_summary_

    Returns:
        _type_: _description_
    """
    cf_headers, cf_cookies = await load_cloudflare_stuff(client, retryCount=CLOUDFLARE_RETRY_COUNT)

    cookies = {} | cf_cookies
    headers = COMMON_HEADERS.copy() | cf_headers

    response = await client.get(url=LOGIN_URL, headers=headers, cookies=cookies)

    if response.status_code == 200:
        logger.info("Received 200: Headers and cookies are taken.")
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

        cookies["cookie_prefix"]=""
    else:
        logger.error(f"Received {response.status_code}: Headers and cookies cannot be taken.")
    return [headers, cookies]

async def is_logged_in(client, headers, cookies):
    response = await client.post(
                url=LOGIN_URL,
                headers=headers,
                cookies=cookies,
                follow_redirects=True,
                timeout=50,
                json={
                    "login": {
                        "password": CREDENTIALS['password'],
                        "mode": "password",
                        "username": CREDENTIALS['username'],
                        }
                    }
        )

    if response.status_code != 200:
        raise Exception(f"""
            username pw failed.
            response code: {response.status_code}
            headers: {response.headers}
            response body: {response.text}
            """)

    response_json = json.loads(response.text)
    if response_json['success'] == 0: # two-factor authentication is required
        if 'mode' not in response_json or 'authToken' not in response_json or 'challengeData' not in response_json:
            raise Exception(f"""
                Unexpected JSON.
                response code: {response.status_code}
                headers: {response.headers}
                response body: {response.text}
                """)
    
        challenge_request_json = {
            'login': {
                "deviceAuthorization": {
                    "answer": CREDENTIALS["answer"],
                    "remember": True,
                },
                "mode": "challenge",
                "username": CREDENTIALS['username'],
                "authToken": response_json['authToken'],
                "challengeData": response_json['challengeData'],
            }
        }

        two_factor_response = await client.post(
                            url=LOGIN_URL,
                            headers=headers,
                            cookies=cookies,
                            follow_redirects=True,
                            timeout=50,
                            json=challenge_request_json,
                )
        if two_factor_response.status_code == 200:
            return True
    else: # two-factor authentication is not required
        return True
    return False

async def get_profile_text(client, headers, cookies):
    response = await client.get(url=PROFILE_URL, headers=headers, follow_redirects=True)

    if response.status_code != 200:
        raise Exception(f"Received {response.status_code}: User ID cannot be taken.")

    user_id = str(response.url).split('/')[-1] # user ID
    profile_url = f"https://www.upwork.com/freelancers/api/v1/freelancer/profile/{user_id}/details"
    response = await client.get(url=profile_url, headers=headers, cookies=cookies)

    if response.status_code != 200:
        raise Exception(f"Received {response.status_code}: User profile cannot be taken.")
    with open(ROOT_DIR+'out.txt', 'w') as file:
        file.write(response.text)
    content = response.text
#     return content

# def get_profile_info():
#     with open(ROOT_DIR+'out.txt', 'r') as file:
#         content = file.read()
    response = json.loads(content)
    user = User()
    # profile
    profile = response['profile']
    # profile.identity
    user.id = profile['identity']['uid']
    # profile.profile
    user.name = profile['profile']['name']
    user.title = profile['profile']['title']
    user.description = profile['profile']['description']
    user.country = profile['profile']['location']['country']
    user.city = profile['profile']['location']['city']
    user.time_zone = profile['profile']['location']['countryTimezone'].split(' ')[0]
    for s in profile['profile']['skills']:
        user.skills.append(s['name'])
    # profile.stats
    user.hourly_rate = str(profile['stats']['hourlyRate']['amount'])+profile['stats']['hourlyRate']['currencyCode']
    # profile.languages
    for l in profile['languages']:
        user.languages.append(l['language']['name'])
    # profile.certificates
    user.certificates = []
    for c in profile['certificates']:
        user.certificates.append(c['certificate']['name'])
    # profile.employmentHistory
    user.employment_history = []
    for eh in profile['employmentHistory']:
        job_title = f"{eh['jobTitle']} at {eh['companyName']}, {eh['city']}, {eh['country']}, s:{eh['startDate']}, e:{eh['endDate']}"
        user.employment_history.append(job_title)
    # profile.education
    for e in profile['education']:
        education = f"{e['degree']} at {e['areaOfStudy']} Department in {e['institutionName']} s:{e['dateStarted']}, e:{e['dateStarted']}"
        user.education.append(education)
    # profile.jobCategoriesV2
    for jc in profile['jobCategoriesV2']:
        user.job_categories.append(jc['groupName'])
    # person
    user.creation_date = datetime.strptime(response['person']['creationDate'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
    user.updated_on = datetime.strptime(response['person']['updatedOn'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
    return user

def write_profile_to_database(user: str):
    """_summary_

    Args:
        user_profile (str): _description_
    """
    database.create_table()
    database.insert_user(user)

async def main():
    # user = get_profile_info()
    
    async with createClient(LOCAL_SSL_FILE_PATH) as client:
        headers, cookies = await get_headers_and_cookies(client)
        if await is_logged_in(client, headers, cookies):
            user = await get_profile_text(client, headers, cookies)
            write_profile_to_database(user)
        else:
            raise Exception('User profile cannot be created.')


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        )
    logger = logging.getLogger("task_logger")

    asyncio.run(main())
