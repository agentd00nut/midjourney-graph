import json
from time import sleep
from dotenv import load_dotenv
import requests, http, os
from pyjourney import MidjourneyAPI

MIDJOURNEY_COOKIE = None
with open("conf\midj.cookie", "r") as f:
    MIDJOURNEY_COOKIE = f.read()

load_dotenv()
MJ_API=MidjourneyAPI(os.getenv("MIDJOURNEY_USERID"))
print(f"USER:{MJ_API.user_id}")
MIDJOURNEY_HEADERS = {
    "authority": "www.midjourney.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "",
    "dnt": "1",
    "sec-ch-ua": 'Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
}


## TODO:: Make a class, makeMidJourneyRequest becomes "POST" and the `getX` functions, become GET...
def mj_POST(url, json=None):
    global MIDJOURNEY_COOKIE
    global MIDJOURNEY_HEADERS
    session = MJ_API.session

    r = session.post(url, json=json, headers=MIDJOURNEY_HEADERS)
    # r = requests.post(url, json=json, headers=MIDJOURNEY_HEADERS, cookies=cookie_jar)
    if not r:
        print("Error: ")
        print(r)
        print(r.text)
        print(r.json())
        print(r.reason)
        r.raise_for_status()
        return None
    return r


def mj_GET(url, querystring):
    global MIDJOURNEY_COOKIE, MIDJOURNEY_HEADERS
    simple_cookie = http.cookies.SimpleCookie(MIDJOURNEY_COOKIE)
    cookie_jar = requests.cookies.RequestsCookieJar()
    cookie_jar.update(simple_cookie)
    return requests.request(
        "GET", url, cookies=cookie_jar, headers=MIDJOURNEY_HEADERS, params=querystring
    )


def getRecentJobsForUser(userId, page, jobs_per_page, max_jobs):
    global MIDJOURNEY_COOKIE, MIDJOURNEY_HEADERS
    url = "https://www.midjourney.com/api/app/recent-jobs/"
    if page == 0:
        page = 1

    recent_jobs = []

    # While we haven't hit the max number of jobs, start at the `page` and ask for `jobs_per_page` from MJ, and add all the jobs to `recent_jobs`
    # paginate
    while len(recent_jobs) < int(max_jobs):
        print(f"Getting page: {page} of {max_jobs} jobs")
        result = MJ_API.recent_jobs()

        if result is None or result.status_code != 200:
            print("we got bonked by midjourney api", result.reason)
            sleep(5)
            continue
        # print(result.text)
        recent_jobs.extend(result.json())
        # print(len(recent_jobs), page)
        page += 1

        break 
    return recent_jobs


def getRunningJobsForUser(userId, num_jobs):
    """
    I lied, they did not, its still minutes or more out of date from what the bot is doing.
    (atleast for running jobs)
    Gets running jobs for the user.
    """

    # print("Sleeping for 2 seconds");
    # sleep(2);
    # print("Seeing if the job is 'running'...");
    # results = getRunningJobsForUser(userId,5)
    # if not results:
    #     return html.Div([html.H3(f"Failed to get running jobs for {node.id}... reason: {results.text}... repeated failures mean you should probably stop")])

    global MIDJOURNEY_COOKIE, MIDJOURNEY_HEADERS
    url = "https://www.midjourney.com/api/app/recent-jobs"
    querystring = {
        "amount": num_jobs,
        "orderBy": "enqueueTime",
        "orderDirection": "desc",
        "jobStatus": "running",
        "userId": userId,
        "dedupe": "true",
        "timeRangeMinutes": "5",
    }

    return mj_GET(url, querystring)


def getJobStatus(jobIds: list[str]):
    global MIDJOURNEY_COOKIE, MIDJOURNEY_HEADERS
    url = "https://www.midjourney.com/api/app/job-status"

    result = MJ_API.job_status(jobIds[0])
    if result is None or result.status_code != 200:
        print("we got bonked by midjourney api", result.reason)
        sleep(5)
        return None
    return result

    # querystring = json.dumps({"jobIds": jobIds})
    # return mj_POST(url, querystring)
