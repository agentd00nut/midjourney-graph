import time
import discum
from discum.gateway.response import Resp
import re

bot = discum.Client(
    token=False,
    log=False,
)


runningJobs = re.compile("Jobs\*\*:\s*(\d)")


@bot.gateway.command
def countC(resp: Resp):
    global f
    m = resp.parsed.auto()
    if resp.event.message_updated:
        m = resp.parsed.auto()
        guildID = m["guild_id"] if "guild_id" in m else None
        if guildID is None:
            print(resp.raw["t"], m["author"]["username"])
            embeds = m["embeds"]
            if len(embeds) == 0:
                return
            desc = embeds[0]["description"]
            results = runningJobs.findall(desc)
            jobs = sum([int(n) for n in results])
            print("Currently running jobs: ", jobs)
            # f.seek(0)
            f = open("..\\running.txt", "w")
            f.write(str(jobs))
            f.close()
            f = open("..\\lastRun.txt", "w")
            f.write(str(int(time.time())))
            f.close()
            # f.write("\n")
            # print("wowza", m["channel_id"], m["id"])
            # print(m)


bot.gateway.run(auto_reconnect=True)
