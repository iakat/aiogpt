import json
import os
import traceback
import uuid

import aiohttp

SESSION_TOKEN = os.environ.get("AIOGPT_SESSIONTOKEN")


class Chat:
    def __init__(self, session_token):
        self.session_token = session_token
        self.access_token = None
        self.history = []
        self.API_URL = "https://chat.openai.com/backend-api/conversation"
        self.reset()

    @property
    def headers(self):
        return {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "Host": "chat.openai.com",
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://chat.openai.com/chat",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }

    def reset(self):
        self.conversation_id = None
        self.parent_message_id = str(uuid.uuid4())

    async def say(self, message):
        response = await self._say(message)
        if not response:
            await self.refresh()
            response = await self._say(message)
        return response

    async def _say(self, message):
        if not self.access_token:
            await self.refresh()
        data = {
            "model": "text-davinci-002-render",
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_message_id,
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [message]},
                }
            ],
        }

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                self.API_URL,
                data=json.dumps(data),
                timeout=30,
            ) as resp:
                response = await resp.text()
        try:
            raw = json.loads((response.splitlines()[-4]).split(":", 1)[1])
            output = "\n".join(raw["message"]["content"]["parts"])
            self.conversation_id = raw["conversation_id"]
            self.parent_message_id = raw["message"]["id"]
            self.history.append([conversation_id, message, output])
            return (
                output,
                self.conversation_id,
                self.parent_message_id,
            )
        except:

            traceback.print_exc()
            print(response)
            return None

    async def refresh(self):
        cookies = {
            "__Secure-next-auth.session-token": self.session_token,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
            async with session.get("https://chat.openai.com/api/auth/session") as resp:
                response = await resp.text()
                try:
                    self.access_token = json.loads(response)["accessToken"]
                    self.session_token = session.cookie_jar._cookies["chat.openai.com"][
                        "__Secure-next-auth.session-token"
                    ].value
                except:
                    traceback.print_exc()
                    print("login", response)
                    return None


if __name__ == "__main__":
    chat = Chat(SESSION_TOKEN)
    chat.reset()
    import asyncio

    asyncio.run(chat.say("hello"))
