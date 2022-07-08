
import requests
from src.node import Node

DISCORD_COOKIE = None
with open('conf\discord.cookie', 'r') as f:
    DISCORD_COOKIE = f.read().strip('\n')
DISCORD_AUTHORIZATION = None
with open('conf\discord.authorization', 'r') as f:
    DISCORD_AUTHORIZATION = f.read().strip('\n')
DISCORD_SESSION = None
with open('conf\discord.sessionId', 'r') as f:
    DISCORD_SESSION = f.read().strip('\n')

class DiscordLink:

    def POST(self, url: str, payload: dict):
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

    def runJob(self, node: Node, number: int, type: str):
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
         

        payload = {
            "type": 3,
            "guild_id": node.job.guild_id,
            "channel_id": channelId,
            "message_flags": 0,
            "message_id": node.job.platform_message_id,
            # TODO:: Does the application_id rotate on bot deploys?
            "application_id": "936929561302675456",
            "session_id": DISCORD_SESSION,  
            "data": {
                "component_type": 2,
                "custom_id": type
            }
        } 
        print(payload)
        return self.POST(url, payload=payload)
