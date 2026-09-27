import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from ollama import chat
from ollama import ChatResponse
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

def start_whatsapp():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get('https://web.whatsapp.com/')
    print("Scannerizza il QR Code per accedere a WhatsApp Web")
    time.sleep(15)
    return driver
    
def get_chats_with_unread_messages(driver):
    chats = driver.find_elements(By.CLASS_NAME, '_ak72.false._ak73._ak7n')
    #chats = driver.find_elements(By.CLASS_NAME, 'x10l6tqk.xh8yej3.x1g42fcv')
    return chats
    
def open_chat(chat):
    chat.click()
    time.sleep(2)

def get_today_messages(driver):
    new_messages = []
    messages = driver.find_elements(By.CLASS_NAME, '_akbu')
    for message in messages[-1:]:
        print(message.text)
        message_text = message.text.strip()
        if message_text:
            new_messages.append(message_text)
    
    return new_messages


def respond_with_ollama(messages):
    if not messages:
        return ""
    
    chat_history = [{"role": "user", "content": message} for message in messages]
    response: ChatResponse = chat(model=OLLAMA_MODEL, messages=chat_history)
    return response['message']['content']

def send_message(driver, message):
    input_box = driver.find_element(By.XPATH, '//div[@aria-label="Scrivi un messaggio"]')
    input_box.send_keys(message + Keys.RETURN)

def whatsapp_bot():
    driver = start_whatsapp()

    while True:
        chats = get_chats_with_unread_messages(driver)
        for chat in chats:
            open_chat(chat)
            today_messages = get_today_messages(driver)
            if today_messages:
                response = respond_with_ollama(today_messages)
                send_message(driver, response)
            time.sleep(3)
        time.sleep(10)

if __name__ == "__main__":
    whatsapp_bot()