import aiohttp
import json
import uuid
import os

SESSION_TOKEN = os.environ.get("AIOGPT_SESSIONTOKEN")


class Chat:
    def __init__(self, session_token):
        self.session_token = session_token
        self.access_token = None
        self.API_URL = "https://chat.openai.com/backend-api/conversation"
        self.reset()

    @property
    def headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
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

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.API_URL,
                headers=self.headers,
                data=json.dumps(data),
            ) as resp:
                response = await resp.text()
        try:
            raw = json.loads((response.splitlines()[-4]).split(":", 1)[1])
            self.conversation_id = raw["conversation_id"]
            self.parent_id = raw["message"]["id"]
            return (
                "\n".join(raw["message"]["content"]["parts"]),
                self.conversation_id,
                self.parent_id,
            )
        except:
            import traceback

            traceback.print_exc()
            return None

    async def refresh(self):
        cookies = {
            "__Secure-next-auth.session-token": self.session_token,
        }
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.get("https://chat.openai.com/api/auth/session") as resp:
                response = await resp.text()
                self.access_token = json.loads(response)["accessToken"]
                self.session_token = session.cookie_jar._cookies["chat.openai.com"][
                    "__Secure-next-auth.session-token"
                ].value


if __name__ == "__main__":
    chat = Chat(SESSION_TOKEN)
    chat.reset()
    import asyncio

    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(chat.say("Hello!")))
