import requests, http

MIDJOURNEY_COOKIE = None
with open('conf\midj.cookie', 'r') as f:
    MIDJOURNEY_COOKIE = f.read()

def makeMidJourneyRequest(url, json=None):
    global MIDJOURNEY_COOKIE
    
    headers = {
        'cookie': MIDJOURNEY_COOKIE,
        'authority': "www.midjourney.com",
        'accept': "*/*",
        'accept-language': "en-US,en;q=0.9",
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'dnt': "1",
        'referer': "https://www.midjourney.com/app/feed/all/",
        'sec-ch-ua-mobile': "?0",
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': "empty",
        'sec-fetch-mode': "cors",
        'sec-fetch-site': "same-origin",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }

    r = requests.post(url, json=json, headers=headers)
    if not r:
        print("Error: ")
        print(r)
        print(r.text)
        print(r.json())
        print(r.reason)
        r.raise_for_status()
        return None
    return r


def getRecentJobsForUser(userId, num_jobs, page=1):
    global MIDJOURNEY_COOKIE
    url = "https://www.midjourney.com/api/app/recent-jobs"
    if page == 0:
        page = 1

    querystring = {"amount": num_jobs, "orderBy": "enqueueTime", "orderDirection": "orderDirection",
                   "jobStatus": "completed", "userId": userId, "dedupe": "true", "refreshApi": "0", "page": page}
                   
    simple_cookie = http.cookies.SimpleCookie(MIDJOURNEY_COOKIE)
    cookie_jar = requests.cookies.RequestsCookieJar()
    cookie_jar.update(simple_cookie)

    headers = {
        "authority": "www.midjourney.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "",
        "dnt": "1",
        "referer": "https://www.midjourney.com/app/feed/all/",
        "sec-ch-ua": 'Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }

    return requests.request("GET", url, cookies=cookie_jar, headers=headers, params=querystring)

