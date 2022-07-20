import requests
from src.node import Node

DISCORD_COOKIE = None
DISCORD_AUTHORIZATION = None
DISCORD_SESSION = None
DISCORD_CHANNEL = None

try:
    with open("conf\discord.cookie", "r") as f:
        DISCORD_COOKIE = f.read().strip("\n")

    with open("conf\discord.authorization", "r") as f:
        DISCORD_AUTHORIZATION = f.read().strip("\n")

    with open("conf\discord.sessionId", "r") as f:
        DISCORD_SESSION = f.read().strip("\n")

    with open("conf\discord.channel", "r") as f:
        DISCORD_CHANNEL = f.read().strip("\n")
except FileNotFoundError:
    print(
        "Error: discord.cookie, discord.authorization, or discord.sessionId not found... dont try to run a job"
    )


class DiscordLink:
    def POST(self, url: str, payload: dict) -> requests.Response:
        global DISCORD_COOKIE

        headers = {
            "cookie": DISCORD_COOKIE,
            "authority": "discord.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": DISCORD_AUTHORIZATION,
            "content-type": "application/json",
            "dnt": "1",
            "origin": "https://discord.com",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        return response

    def runJob(self, node: Node, type: str):
        """
        Send a message to the Discord channel.

        Args:
                node: The node to send the message to.
                number: The number of the variance to run a job for. 1-4
                type: "variation" or "upsample"
        """
        url = "https://discord.com/api/v9/interactions"

        channelId = node.job.platform_channel_id
        if node.job.platform_thread_id is not None:
            channelId = node.job.platform_thread_id

        if DISCORD_SESSION is None:
            print("Error: discord.sessionId not found... dont try to run a job")
            return

        payload = {
            "type": 3,
            "guild_id": node.job.guild_id,
            "channel_id": channelId,
            "message_flags": 0,
            "message_id": node.job.platform_message_id,
            # TODO:: Does the application_id rotate on bot deploys?
            "application_id": "936929561302675456",
            "session_id": DISCORD_SESSION,
            "data": {"component_type": 2, "custom_id": type},
        }
        print(payload)
        return self.POST(url, payload=payload)

    def imagine(self, prompt: str) -> requests.Response | None:
        """
        Send an "Imagine" job to discord

        Need a better way to handle the channel at some point.
        """
        url = "https://discord.com/api/v9/interactions"

        if DISCORD_SESSION is None:
            print("Error: discord.sessionId not found... dont try to run a job")
            return None
        payload = {
            "type": 2,
            "guild_id": 662267976984297473,
            "channel_id": DISCORD_CHANNEL,  # TODO:: Better channel handling for /imagine prompts
            "application_id": "936929561302675456",
            "session_id": DISCORD_SESSION,
            "data": {
                "version": "994261739745050686",
                "id": "938956540159881230",
                "name": "imagine",
                "type": 1,
                "options": [{"type": 3, "name": "prompt", "value": prompt}],
                "attachments": [],
            },
        }

        return self.POST(url, payload=payload)

    def fast(
        self,
    ) -> requests.Response | None:
        url = "https://discord.com/api/v9/interactions"

        if DISCORD_SESSION is None:
            print("Error: discord.sessionId not found... dont try to run a job")
            return None

        payload = {
            "type": 2,
            "application_id": "936929561302675456",
            "guild_id": "662267976984297473",
            "channel_id": "945077390839787570",  # daily-theme channel
            "session_id": DISCORD_SESSION,
            "data": {
                "version": "987795926183731231",
                "id": "972289487818334212",
                "name": "fast",
                "type": 1,
                "options": [],
                "attachments": [],
            },
        }

        return self.POST(url, payload=payload)

    def relax(self) -> requests.Response | None:
        url = "https://discord.com/api/v9/interactions"

        if DISCORD_SESSION is None:
            print("Error: discord.sessionId not found... dont try to run a job")
            return None

        payload = {
            "type": 2,
            "application_id": "936929561302675456",
            "guild_id": 662267976984297473,
            "channel_id": 945077390839787570,
            "session_id": DISCORD_SESSION,
            "data": {
                "version": "987795926183731232",
                "id": "972289487818334213",
                "name": "relax",
                "type": 1,
                "options": [],
                "attachments": [],
            },
        }

        return self.POST(url, payload=payload)

    def max(
        self,
        node: Node,
    ) -> requests.Response | None:
        url = "https://discord.com/api/v9/interactions"
        channelId = node.job.platform_channel_id
        if node.job.platform_thread_id is not None:
            channelId = node.job.platform_thread_id

        if DISCORD_SESSION is None:
            print("Error: discord.sessionId not found... dont try to run a job")
            return None

        payload = {
            "type": 3,
            "guild_id": node.job.guild_id,
            "channel_id": channelId,
            "message_flags": 0,
            "message_id": node.job.platform_message_id,
            "application_id": "936929561302675456",
            "session_id": DISCORD_SESSION,
            "data": {
                "component_type": 2,
                "custom_id": "MJ::JOB::upsample_max::1::SOLO",
            },
        }
        print(payload)
        return self.POST(url, payload=payload)
