import requests, http

MIDJOURNEY_COOKIE = None
with open('conf\midj.cookie', 'r') as f:
    MIDJOURNEY_COOKIE = f.read()

MIDJOURNEY_HEADERS={
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

# TODO:: Make a class, makeMidJourneyRequest becomes "POST" and the `getX` functions, become GET...
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
    global MIDJOURNEY_COOKIE,MIDJOURNEY_HEADERS
    url = "https://www.midjourney.com/api/app/recent-jobs"
    if page == 0:
        page = 1

    querystring = {"amount": num_jobs, "orderBy": "enqueueTime", "orderDirection": "desc",
                   "jobStatus": "completed", "userId": userId, "dedupe": "true", "refreshApi": "0", "page": page}
                   
    simple_cookie = http.cookies.SimpleCookie(MIDJOURNEY_COOKIE)
    cookie_jar = requests.cookies.RequestsCookieJar()
    cookie_jar.update(simple_cookie)

    return requests.request("GET", url, cookies=cookie_jar, headers=MIDJOURNEY_HEADERS, params=querystring)


def getRunningJobsForUser(userId, num_jobs):
    """
    Unfortunately the api seems to only update once a minute, so we can't really use this to get the latest jobs... though we could loop on it in the background every 30 seconds to 
    do the auto updating.

    In theory we could spoof websocket connection to pretend we're a connected client and then issue the interaction request for doing `/info` and then parse the response amidst the noise
    on the socket.... maybe later.

    Returns a list of running jobs for a user... it's not clear what the delay between the bot taking a job and the api say it's running is...
    It's not clear if a "queued" job is "running" or "queued"; 
    """

    # print("Sleeping for 2 seconds");
    # sleep(2);
    # print("Seeing if the job is 'running'...");
    # results = getRunningJobsForUser(userId,5)
    # if not results:
    #     return html.Div([html.H3(f"Failed to get running jobs for {node.id}... reason: {results.text}... repeated failures mean you should probably stop")])
    
    global MIDJOURNEY_COOKIE,MIDJOURNEY_HEADERS
    url = "https://www.midjourney.com/api/app/recent-jobs"
    querystring = {"amount": num_jobs, "orderBy": "enqueueTime", "orderDirection": "desc",
                "jobStatus": "running", "userId": userId, "dedupe": "true", "refreshApi": "1", "timeRangeMinutes":"60"}

    simple_cookie = http.cookies.SimpleCookie(MIDJOURNEY_COOKIE)
    cookie_jar = requests.cookies.RequestsCookieJar()
    cookie_jar.update(simple_cookie)

    return requests.request("GET", url, cookies=cookie_jar, headers=MIDJOURNEY_HEADERS, params=querystring)
