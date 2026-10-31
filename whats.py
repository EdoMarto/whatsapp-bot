import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ollama import chat
from ollama import ChatResponse
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# Keep the model output short and on topic so the auto-sent reply stays sane.
SYSTEM_PROMPT = (
    "Sei un assistente che risponde ai messaggi WhatsApp in modo breve, "
    "educato e in italiano. Rispondi con una sola frase."
)
MAX_REPLY_LENGTH = 500

def start_whatsapp():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get('https://web.whatsapp.com/')
    print("Scannerizza il QR Code per accedere a WhatsApp Web")
    # Wait until the chat list is available instead of guessing with a fixed sleep.
    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.ID, 'pane-side'))
    )
    return driver

def get_chats_with_unread_messages(driver):
    chats = driver.find_elements(By.CLASS_NAME, '_ak72.false._ak73._ak7n')
    #chats = driver.find_elements(By.CLASS_NAME, 'x10l6tqk.xh8yej3.x1g42fcv')
    return chats

def open_chat(driver, chat):
    chat.click()
    # Wait for the message composer to load instead of a fixed sleep.
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@aria-label="Scrivi un messaggio"]')
        )
    )

def get_today_messages(driver):
    new_messages = []
    # Only consider the last bubble if it is an incoming message, otherwise the
    # bot would reply to its own outgoing messages (self-reply loop).
    messages = driver.find_elements(
        By.CSS_SELECTOR, 'div.message-in, div.message-out'
    )
    if not messages:
        return new_messages
    last_message = messages[-1]
    if 'message-in' not in (last_message.get_attribute('class') or ''):
        return new_messages
    bubbles = last_message.find_elements(By.CLASS_NAME, '_akbu')
    for message in bubbles[-1:]:
        print(message.text)
        message_text = message.text.strip()
        if message_text:
            new_messages.append(message_text)

    return new_messages


def respond_with_ollama(messages):
    if not messages:
        return ""

    chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    chat_history += [{"role": "user", "content": message} for message in messages]
    response: ChatResponse = chat(model=OLLAMA_MODEL, messages=chat_history)
    content = response['message']['content'].strip()
    # Basic length guard before auto-sending the reply.
    if len(content) > MAX_REPLY_LENGTH:
        content = content[:MAX_REPLY_LENGTH]
    return content

def send_message(driver, message):
    # Collapse newlines: a bare RETURN sends the message, so multi-line output
    # would otherwise fire as several partial messages.
    single_line = ' '.join(message.splitlines()).strip()
    if not single_line:
        return
    input_box = driver.find_element(By.XPATH, '//div[@aria-label="Scrivi un messaggio"]')
    input_box.send_keys(single_line + Keys.RETURN)

def whatsapp_bot():
    driver = start_whatsapp()

    while True:
        chats = get_chats_with_unread_messages(driver)
        # Loop by index and re-query each iteration: clicking a chat re-renders
        # the sidebar, which detaches previously collected nodes.
        for index in range(len(chats)):
            try:
                chats = get_chats_with_unread_messages(driver)
                if index >= len(chats):
                    break
                chat = chats[index]
                open_chat(driver, chat)
                today_messages = get_today_messages(driver)
                if today_messages:
                    response = respond_with_ollama(today_messages)
                    send_message(driver, response)
            except (StaleElementReferenceException, NoSuchElementException) as error:
                print(f"Chat skipped: {error}")
                continue
            time.sleep(3)
        time.sleep(10)

if __name__ == "__main__":
    whatsapp_bot()
