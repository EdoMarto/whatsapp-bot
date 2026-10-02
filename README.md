# WhatsApp Bot (Selenium + Ollama)

An auto-responder for WhatsApp Web that runs entirely on your own machine. Selenium drives a Chrome
window logged into WhatsApp Web, picks up the chats with unread messages, and replies with text from a
local LLM running in [Ollama](https://ollama.com). Nothing is sent to a cloud AI service.

## How it works

It opens WhatsApp Web in Chrome, and every 10 seconds it checks the sidebar for chats with unread
messages. For each one it opens the chat, reads the last message, sends it to the Ollama model, and types
back the reply.

The main pieces:

| Function | What it does |
|---|---|
| `start_whatsapp()` | Starts Chrome (ChromeDriver comes from `webdriver-manager`) and opens WhatsApp Web |
| `get_chats_with_unread_messages()` | Finds the chats in the sidebar with unread messages |
| `open_chat()` / `get_today_messages()` | Opens a chat and reads its last message |
| `respond_with_ollama()` | Sends the message to the model and gets the reply |
| `send_message()` | Types the reply into the chat |
| `whatsapp_bot()` | The loop that ties it together |

## Getting started

You need Python 3.9+, Google Chrome and [Ollama](https://ollama.com).

```bash
pip install -r requirements.txt
ollama pull llama3.2
python whats.py
```

Chrome opens on WhatsApp Web. Scan the QR code with your phone (Linked devices in WhatsApp) within 15
seconds and the bot starts answering unread chats.

Want a different model? Set `OLLAMA_MODEL` (the default is `llama3.2`):

```bash
OLLAMA_MODEL=mistral python whats.py
```

## Things to know

A few rough edges, since this was a personal experiment:

* It expects WhatsApp Web in Italian. The message box is found by its Italian label
  (`Scrivi un messaggio`), so for another language you need to change the `aria-label` in
  `send_message()`.
* The selectors are fragile. Unread chats and messages are located by WhatsApp Web's generated CSS class
  names, and those change without warning. If it stops finding chats, open the page, inspect it and
  update the class names in `get_chats_with_unread_messages()` and `get_today_messages()`.
* There's no memory. Only the last message of each chat goes to the model.
* If 15 seconds isn't enough to scan the QR code, bump up the `time.sleep()` in `start_whatsapp()`.

## License

[MIT](LICENSE)

> Automating WhatsApp Web isn't endorsed by WhatsApp and may go against its Terms of Service. This was a
> personal experiment, so use it only on your own account.
