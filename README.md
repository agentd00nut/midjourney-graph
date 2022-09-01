# MidJourney Graph

![An image showing the graph based UI](/example.png)

Shows the graph of recent jobs run by the provider userID for midjourney.

Also provides an interface to issue commands to the midjourney bot by hitting the discord API, discord might frown on that behavior though, use those buttons at your own risk.

Uses [discum](https://github.com/Merubokkusu/Discord-S.C.U.Mhttps://github.com/Merubokkusu/Discord-S.C.U.M) to scan for /info requests to parse the results to see how many running jobs you currently have to avoid hitting queue limits. 
# Setup

`pip install -r requirements.txt`

Follow the authorization steps down below then...

`python main.py`

# Security

Obviously putting all of your cookies and sessions to both discord and midjourney into plain text files on your hard drive is not... the most great idea.  All of the (spaghetti) code in graph is straight forward so you can see we're not doing anything suspicious with your credentials besides using them to call discord api's (though technically we're self botting which is a TOS violation) and midjourney api (which aren't technically public but we try really hard to be gentle on their api.)

Use at your discretion; obviously anything bad that happens from using this is entirely your own fault.

# Risks

Likely none besides whats said in the security section.

I've used this personally for about a month and left it running overnight, running hundreds of relaxed jobs and nothing bad has happened.  That said; again; technically it is "self-botting" on discord and is using semi-private midjourney apis.  

### License

Whatever the one that means "give me some money if you make money with it, otherwise do what you want, not my fault if your computer explodes from using this"


# Super quick authorization steps

You need the following files all in a `conf/` dir; make it if it doesn't exist.

```
discord.authorization   -- Header sent on interaction requests from discord web ui
discord.channel         -- What channel /imagine commands should go to;
discord.cookie          -- The entire cookie from the header on interaction requests from discord web ui
discord.guild           -- what guild the channel id is in when using /imagine
discord.sessionId       -- found WITHIN the payload of an interaction request
midj.cookie             -- the full cookie from any call to the api when browsing midjourney web app
midj.user               -- easily found from URL bar when viewing your own profile as a visitor. its the big number.
```

Place each piece of information in the files; you'll need to make the files; yes this is a goofy way to do the setup but that's okay.

# Use

Pretty self explanitory, the slider next to the job buttons goes from 1-4.

To run a V4 job, select a node, move the slider all the way right and hit the `V<>` button.

You can omit the discord configuration files and just use the graph as a visual aid... the "goto discord" button _should_ still work.

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

# The authorization setups

These shouldn't need to be done more than once every few days.

Obviously don't share your cookies with anyone

Obviously this is a really dumb and insecure way to manage your credentials.

## Getting your midjourney cookies

Login to midjourney, open the dev console, go anywhere that issues a `Fetch/XHR` request to midjourney

Click on any of those requests, in the headers tab scroll down and copy the entire `cookie` header string, paste it into the `conf/midj.cookie` file.

## Getting the discord cookie / authorization string

Much the same to the midjourney process. Login to discord with the web UI, go to the midjourney guild.

Go into a thread, not a channel (`#general`) but a _thread_.

Open dev console, make an interaction (click a button from the bot),

Click on that interaction request and check its "Request Headers"...

Put the `cookie` string, the whole thing, into `conf/discord.cookie`, make the file if it does not exist

Also grab the `authorization` string and put it into `conf/discord.authorization`, make the file if it does not exist

Lastly grab the `sessionId` string and put it into `conf/discord.sessionId`, make the file if it does not exist


# TODO

Vaguely in order.

## Important

- [] The api can return jobs that appear to return invalid / incomplete json.

## Optimizations

- [x] ~Make an initial pass of reference jobs to remove jobs already in our graph, before starting the depth first search of referral jobs. Could reduce calls to midjourney api with larger "jobsPerQuery" settings.~
- [x] ~Modify the referral job loop to work on the next "set" of referral jobs as one unit instead of walking depth first down a nodes referral chain... Much faster, and utilizes that the job-status api accepts an array of nodes!~

## Features

- [x] Imagine prompt input
- [x] Prompt "mixing", prompts from the left file, permutate with modifiers in right file.
- [x] Max-upscale button (unsure how to know if available)
- [x] **Option to automatically move to `/fast` mode when issuing a "max upscale" command while in `/relax` state.**
- [x] Fast / Relax buttons + show current state.
- [] Automatically add nodes for issued jobs / "running" nodes, update with progress images if possible.
- [x] Show all running jobs status (tried to do this; technically it "works" but MJ only updates once a minute from the bot, so it can really lag our knowledge of running jobs etc.)
- [] Any sort of "running" indicator
- [] A second graph view (ideally within the same viewport) showing the chain of reference images for the selected node. (All the nodes would _only_ be the image referenced and not the 2x2 grids)

## Unlikely to happen

- [] Style the page not like someone that only ever works on backend.
- [] Responsive design, phones be damned.
- [] Create a mp4 from the root node to the selected node following its parent chain.
- [] Somehow smoothly move between the frames.
- [] Somehow pull the progress frames for each node, and somehow smoothly move from the rendered node to the first blurry progress node.
