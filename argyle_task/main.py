# from bs4 import BeautifulSoup
import asyncio, httpx, json, logging, os, ssl, time
# import database

# BASE_URL = "https://www.upwork.com"
# LOGIN_URL = BASE_URL+"/ab/account-security/login"
# PROFILE_URL = BASE_URL+"/freelancers/"

# CREDENTIALS = {
#     "username": "fatmakahvecim@gmail.com", # "fatmaba@gmail.com", # "bobbybackupy",
#     "password": "argyleSifresi1.", #"argyleSifresi1.",   # "Argyleawesome123!",
#                                      # "secret-key": "TheDude!@"
#     }

# CLOUDFLARE_RETRY_COUNT = 10
# CLOUDFLARE_COOKIE_NAMES = ['__cf_bm']

# COMMON_HEADERS = { 
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0',
#     'content-type': 'application/json',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#     'Connection': 'keep-alive',
#     'Set-Fetch-Dest': 'document',
#     'Set-Fetch-Mode': 'navigate',
#     'Set-Fetch-Site': 'none',
#     'Upgrade-Insecure-Requests': '1',
#     }

# LOCAL_SSL_FILE_PATH = "/etc/ssl/cert.pem"

# DEFAULT_DB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

class User:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.title = ""
        self.description = ""
        self.country = ""
        self.city = ""
        self.time_zone = ""
        self.skills = []
    
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
        """
        return user

# async def load_cloudflare_stuff(client, retryCount: int):
#     """This function is needed to collect the cloudflare-needed cookies
#     that will be used for bypassing cloudflare's bot-prevention mechanisms.

#     Args:
#         client (_type_): _description_
#         retryCount (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     headers = COMMON_HEADERS | {}
#     cookies = {}
    
#     for _ in range(retryCount):
#         response = await client.get(headers=headers, cookies=cookies, url=LOGIN_URL)
#         if response.status_code != 200:
#             logger.info(f"Received {response.status_code}: Headers and cookies cannot be taken.")

#         if 'set-cookie' in response.headers:
#             for cookie in response.headers['set-cookie'].split(';'):
#                 cookieTokens = cookie.strip(' ').split("=", 1)
#                 if len(cookieTokens) == 2:
#                     if cookieTokens[0] in CLOUDFLARE_COOKIE_NAMES:
#                         cookies[cookieTokens[0]] = cookieTokens[1]

#         if 'cf-ray' in response.headers:
#             headers["cf-ray"] = response.headers["cf-ray"]
        
#         if response.status_code == 200:
#             logger.info(f"Received {response.status_code}: Headers and cookies are taken.")
#             break

#         time.sleep(1)
#     return [headers, cookies]

# def createClient(caFilePath: str):
#     """_summary_

#     Args:
#         caFilePath (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     context = ssl.create_default_context() # https://www.python-httpx.org/advanced/#ssl-certificates
#     context.load_verify_locations(cafile=caFilePath)
#     return httpx.AsyncClient(verify=context)

# async def get_headers_and_cookies():
#     """_summary_

#     Returns:
#         _type_: _description_
#     """
#     async with createClient(LOCAL_SSL_FILE_PATH) as client:
#         cf_headers, cf_cookies = await load_cloudflare_stuff(client, retryCount=CLOUDFLARE_RETRY_COUNT)

#         cookies = {} | cf_cookies
#         headers = COMMON_HEADERS.copy() | cf_headers

#         response = await client.get(url=LOGIN_URL, headers=headers, cookies=cookies)

#         if response.status_code == 200:
#             logger.info("Received 200: Headers and cookies are taken.")
#             for cookie in response.headers['set-cookie'].split(';'):
#                 # logging.debug(cookie)
#                 if "visitor_id" in cookie:
#                     cookies["visitor_id"] = cookie.split("=")[1]
#                 if "XSRF-TOKEN" in cookie:
#                     cookies["XSRF-TOKEN"] = cookie.split("XSRF-TOKEN=")[1]
#                 if "enabled_ff" in cookie:
#                     cookies["enabled_ff"] = cookie.split("=")[1]

#             headers['referer'] = LOGIN_URL
#             headers['x-requested-with'] = 'XMLHttpRequest'
#             headers['x-odesk-csrf-token'] = cookies["XSRF-TOKEN"]

#             cookies["cookie_prefix"]=""
#         else:
#             logger.error(f"Received {response.status_code}: Headers and cookies cannot be taken.")
#     return [headers, cookies]

# async def get_profile_text():
#     headers, cookies = await get_headers_and_cookies()
#     async with createClient(LOCAL_SSL_FILE_PATH) as client:
#         response = await client.post(
#                         url=LOGIN_URL,
#                         headers=headers,
#                         cookies=cookies,
#                         follow_redirects=True,
#                         timeout=50,
#                         json={
#                             "login": {
#                                 "password": f"{CREDENTIALS['password']}",
#                                 "mode": "password",
#                                 "username": f"{CREDENTIALS['username']}",
#                                 "elapsedTime":289170,
#                                 }
#                             }
#             )
#         response = await client.get(url=PROFILE_URL, headers=headers, follow_redirects=True)
#         if response.status_code != 200:
#             raise Exception(f"Received {response.status_code}: User ID cannot be taken.")
#         user_id = str(response.url).split('/')[-1] # user ID
    
#         profile_url = f"https://www.upwork.com/freelancers/api/v1/freelancer/profile/{user_id}/details"
#         response = await client.get(url=profile_url, headers=headers, cookies=cookies)
#         if response.status_code != 200:
#             raise Exception(f"Received {response.status_code}: User profile cannot be taken.")

#         return response.text

# async def get_profile_info():
def get_profile_info():
    # response = await get_profile_text()
    with open('/Users/fatmakhv/Desktop/out.txt', 'r') as file:
        content = file.read()
    response = json.loads(content)
    profile = response['profile']
    user = User()
    user.id = profile['identity']['uid']
    user.name = profile['profile']['name']
    user.title = profile['profile']['title']
    user.description = profile['profile']['description']
    user.country = profile['profile']['location']['country']
    user.city = profile['profile']['location']['city']
    user.time_zone = profile['profile']['location']['countryTimezone']
    # user.skills = profile.
    print(user)

# def write_profile_to_database(user_profile: str):
#     """_summary_

#     Args:
#         user_profile (str): _description_
#     """
#     database.create_table()

# async def main():
    # user_profile = await get_profile_info()
    # write_profile_to_database(user_profile)


if __name__ == "__main__":
    # logging.basicConfig(
    #     level = logging.DEBUG,
    #     format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    #     )
    # logger = logging.getLogger("task_logger")
    user_profile = get_profile_info()
    # asyncio.run(main())
