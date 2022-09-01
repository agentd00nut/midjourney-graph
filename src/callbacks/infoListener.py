import time
import discum
from discum.gateway.response import Resp
import re

from src.callbacks.randomJob import setLastUpdate, setLiveJobs
from src.discord import DISCORD_AUTHORIZATION

bot = discum.Client(
    token=DISCORD_AUTHORIZATION,
    log=False,
)
runningJobs = re.compile("Jobs\*\*:\s*(\d+)")


def lolidk(clicks):
    @bot.gateway.command
    def countJobs(resp: Resp):

        global bot
        global runningJobs

        m = resp.parsed.auto()

        if resp.event.message_updated:
            m = resp.parsed.auto()
            guildID = m["guild_id"] if "guild_id" in m else None

            if guildID is None:

                embeds = m["embeds"]
                if len(embeds) == 0:
                    return
                desc = embeds[0]["description"]
                if "**Subscription**" not in desc:  # avoids "Your job is now running"
                    return

                # print("DESCRIPTION:\n", desc)
                results = runningJobs.findall(desc)
                # print("RESULTS:\n", results)
                jobs = sum([int(n) for n in results])

                DISCORD_LIVEJOBS = int(jobs)
                DISCORD_LIVEJOBS_LAST_UPDATE = int(time.time())

                print(
                    f"INFO LISTENER ({DISCORD_LIVEJOBS_LAST_UPDATE}): {DISCORD_LIVEJOBS}"
                )

                setLiveJobs(DISCORD_LIVEJOBS)
                setLastUpdate(DISCORD_LIVEJOBS_LAST_UPDATE)

    bot.gateway.run(auto_reconnect=True)
