# aiogpt

aiogpt is a Python library for interacting with [ChatGPT](https://chat.openai.com/).

## Usage

```python
import asyncio
from aiogpt import Chat

TOKEN = [ value of your `__Secure-next-auth.session-token` cookie ]
async def main():
    C = Chat(TOKEN)
    response = await C.say("Hello!")
    if response:
        print(response[0])
    # To reset the conversation:
    C.reset()

asyncio.run(main())
```

Should print something like:
```
Hello! How can I help you today? Is there something you would like to talk about or learn more about? I'm here to assist you with any questions you may have.
```

## Installation

```bash
pip install aiogpt
```

## Contributions

Contributions are welcome! Please open a Pull Request or an Issue.
