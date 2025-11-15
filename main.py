import requests
import time
import os
import random
import threading

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = "1336317526472134706"
API_BASE = "https://discord.com/api/v9"
WEBHOOK_URL = "https://discord.com/api/webhooks/1336719255252504686/hrAFIW1ssYthJ2Q11tTdi5qcLTKoAcLUHpy7OKH3uUC8eEkjvmpQ8bIiltgVqH1MlLbk"
TARGET_USER_ID = os.getenv("UID")

paused = False

with open("text.txt", "r", encoding="utf-8") as f:
    text_lines = [line.strip().replace('"', '') for line in f.readlines() if line.strip()]

base_messages = ["obuy 1"]

headers = {
    "authorization": TOKEN
}

webhook_thread = None
webhook_stop_event = threading.Event()

def get_last_messages():
    r = requests.get(f"{API_BASE}/channels/{CHANNEL_ID}/messages?limit=1", headers=headers)
    if r.status_code == 200:
        return r.json()
    return []

def send_message(content):
    payload = {"content": content}
    r = requests.post(f"{API_BASE}/channels/{CHANNEL_ID}/messages", headers=headers, data=payload)
    return r.status_code == 200

def send_webhook_tag_loop(stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            payload = {"content": f"<@{TARGET_USER_ID}>"}
            requests.post(WEBHOOK_URL, json=payload, timeout=5)
        except Exception:
            pass
        stop_event.wait(2.0)

def listen_for_stop():
    global paused, webhook_thread, webhook_stop_event
    last_msg_id = None
    while True:
        msgs = get_last_messages()
        if msgs:
            msg = msgs[0]
            msg_id = msg.get("id")
            content = msg.get("content", "")
            if msg_id != last_msg_id:
                last_msg_id = msg_id
                if "Please complete this within 10 minutes or it may result in a ban!" in content:
                    if not paused:
                        paused = True
                        if webhook_thread is None or not webhook_thread.is_alive():
                            webhook_stop_event.clear()
                            webhook_thread = threading.Thread(target=send_webhook_tag_loop, args=(webhook_stop_event,), daemon=True)
                            webhook_thread.start()
                elif content.strip().lower() == "!resume":
                    if paused:
                        paused = False
                        webhook_stop_event.set()
        time.sleep(1)

def auto_send():
    global paused
    while True:
        if not paused:
            first = random.choice(base_messages)
            send_message(first)
            if text_lines:
                msg = random.choice(text_lines)
                send_message(msg)
            time.sleep(4)
        else:
            time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=listen_for_stop, daemon=True).start()
    auto_send()