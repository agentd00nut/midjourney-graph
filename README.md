# MidJourney Graph

![An image showing the graph based UI](/example.png)

Shows the graph of recent jobs run by the provider userID for midjourney.

Also provides an interface to issue commands to the midjourney bot by hitting the discord API, discord might frown on that behavior though, use those buttons at your own risk.

### License

Whatever the one that means "give me some money if you make money with it, otherwise do what you want, not my fault if your computer explodes from using this"

# Setup

`pip install -r requirements.txt`

Follow the authorization steps down below then...

`python main.py`

# Use

Pretty self explanitory, the slider next to the job buttons goes from 1-4.

To run a V4 job, select a node, move the slider all the way right and hit the `V<>` button.

## Midjourney API inputs

You can change the defaults in the obvious places within `main.py` right at the top of the file.

The program loops iterating the page value on api calls, starting at `startPage` asking for `jobsPerQuery` until its taken in `numberOfJobs`.

Then we add all those jobs to the graph.

Then we iterate over the job references, depth first, moving to the next job if a reference was already in the graph...

You can change these values at any time and then click out or hit "enter", the title of the page should move to "Updating"... If you keep the jobs per query low you'll be able to "refresh" your graph after jobs complete running, auto refresh coming soon...

`userId` Your _MIDJOURNEY_ user id, or another user, change the default value of the `dcc.Input` to yours to not need to paste it in every time.

`numberOfJobs` This is a limit on the number of jobs to fetch from midjourney. **Should be divisible by the jobsPerQuery param or you'll be fetching jobs and then not displaying them**

`jobsPerQuery` Any value from 0-100. Asks the MidJourney api for that many recent jobs. **Even if you only fetch a single job the graph may end up with more nodes as it automatically iterates down the referenced nodes of each fetched job to populate all the way back to the original "prompt".**

`startPage` Pagination supported by the midj api, unclear if it respects the interval specified by jobsPerQuery or not.

## Buttons for Job Creation

Select a node

`Reroll` is the same as clicking the circle arrow icon on a 2x2 variation job.

`Make Variations` is the same as clicking the same named button on an upscale job.

`Max Upscale` not supported at the moment.

`Goto Discord` will attempt to go to the job in discord, it... usually works. (i don't use it that much tbh)

# The authorization setups

These shouldn't need to be done more than once every few days.

Obviously don't share your cookies with anyone

Obviously this is a really dumb and insecure way to manage your credentials.

## Getting your midjourney cookies

Login to midjourney, open the dev console, go anywhere that issues a `Fetch/XHR` request to midjourney

Click on any of those requests, in the headers tab scroll down and copy the entire `cookie` header string, paste it into the `conf/midj.cookie` file.

**Warning:** Obviously don't share this with anyone or make it public etc..

## Getting the discord cookie / authorization string

Much the same to the midjourney process. Login to discord with the web UI, go to the midjourney guild.

Go into a thread, not a channel (`#general`) but a _thread_.

Open dev console, make an interaction (click a button from the bot),

Click on that interaction request and check its "Request Headers"...

Put the `cookie` string, the whole thing, into `conf/discord.cookie`, make the file if it does not exist

Also grab the `authorization` string and put it into `conf/discord.authorization`, make the file if it does not exist

Lastly grab the `sessionId` string and put it into `conf/discord.sessionId`, make the file if it does not exist

# Known issues

- It's possible for a job from the midjourney api to come back with null's for the channel, thread, and message... usually this happens right before outages
  When it does it's problematic for obvious reasons. A possible solution would be to use `/show` on the id in a known channel (DM to the bot?); Another
  would be to check if `/interaction` requests can be performed outside the channel that the bot knows an image is in before using `/show`. Unfortunately none of these
  _update_ the job information coming from the api

# TODO

Vaguely in order.

## Important

- [] The api can return jobs that are "invalid"; having no guild or channel or thread or message values that are otherwise "real"... so our variation requests will always fail; we should make these with a red border or some other indicator of "hey midjourney kinda donked up the data on this one"
- [] Support less... dumb, ways of getting the necessary cookies for midj and discord.
- [] Accept just username+Password for discord and automatically the cookies / auths we need.
- [] Support for 2fa on discord logins.

## Optimizations

- [] Make an initial pass of reference jobs to remove jobs already in our graph, before starting the depth first search of referral jobs. Could reduce calls to midjourney api with larger "jobsPerQuery" settings.
- [] Modify the referral job loop to work on the next "set" of referral jobs as one unit instead of walking depth first down a nodes referral chain... Much faster, and utilizes that the job-status api accepts an array of nodes!

## Features

- [] Max-upscale button (unsure how to know if available)
- [] **Option to automatically move to `/fast` mode when issuing a "max upscale" command while in `/relax` state.**
- [] Fast / Relax buttons + show current state.
- [] Automatically add nodes for issued jobs / "running" nodes, update with progress images if possible.
- [] Show all running jobs status
- [] Any sort of "running" indicator
- [] A second graph view (ideally within the same viewport) showing the chain of reference images for the selected node. (All the nodes would _only_ be the image referenced and not the 2x2 grids)
- [] Hosting (obviously requires the better login managmenet)

## Unlikely to happen

- [] Style the page not like someone that only ever works on backend.
- [] Responsive design, phones be damned.
- [] Create a mp4 from the root node to the selected node following its parent chain.
- [] Somehow smoothly move between the frames.
- [] Somehow pull the progress frames for each node, and somehow smoothly move from the rendered node to the first blurry progress node.
