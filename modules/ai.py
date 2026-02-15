import requests
import json
import socket
import time
import sys
from colorama import Fore

from config import (
    API_OLLAMA_URL, BASE_URL, VISION_URL, MAX_RETRIES, RETRY_DELAY, COMMAND_URL, CODE_URL, EXTRACT_URL, PENTEST_URL
)
from utils import spinner_stop, format_in_box_markdown
try:
    from .media import upload_file
    from .chats import get_session_id, load_agent_history, save_agent_history
except ImportError:
    from modules.media import upload_file
    from modules.chats import get_session_id, load_agent_history, save_agent_history

def checkInternet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def ollama_active():
    try:
        r = requests.get(f"{API_OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False

def getReply(message, agent=False, specs=None):
    try:
        headers = {
            "Content-Type": "application/json"
        }

        endpoint = PENTEST_URL if agent else BASE_URL
        if agent:
            history = load_agent_history()
            request_history = history + [{"role": "user", "content": message}]
            data = {
                "message": message,
                "history": request_history,
            }
        else:
            data = {
                "message": message,
                "session": get_session_id(agent=False),
            }
        if specs is not None:
            data["specs"] = specs
        for attempt in range(MAX_RETRIES):
            try:
                r = requests.post(endpoint, headers=headers, json=data, timeout=360)
                if r.status_code == 429:
                    time.sleep(RETRY_DELAY)
                    continue
                r.raise_for_status()
                response_json = r.json()
                if 'error' in response_json:
                    error_message = response_json['error'].get('message', '')
                    if "most wanted" in error_message or "Rate limit" in error_message:
                        time.sleep(RETRY_DELAY)
                        continue
                    else:
                        continue

                if response_json and (reply := response_json.get("response")):
                    if agent:
                        save_agent_history(request_history + [{"role": "assistant", "content": reply}])
                    return reply
                else:
                    continue

            except requests.exceptions.HTTPError as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return f"[❌] ⬡  HTTP Error: {e}"

            except requests.exceptions.RequestException as e:
                return f"[❌] ⬡  Connection Error: {e}"

            except json.JSONDecodeError:
                return "[❌] ⬡  < Error: Invalid data received from API. Please try again later>"

        return "[❌] ⬡  Error: Timeout"
    except Exception as e:
        return f"{Fore.RED}[❌] ⬡ Error: {e}"

def vision(payload, image_url):
    api_data = {
        "prompt": payload,
        "link": image_url
    }

    headers = {
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(VISION_URL, json=api_data, headers=headers)
        r.raise_for_status()
        resp = r.json()
        return resp["response"]
    except Exception as e:
        return f"ㄖ 𝖤𝗋𝗋𝗈𝗋: {str(e)}"

def nekoAI(user_msg, endpoint="default", filePath: str = None, specs: str = None, agent=False, use_web=False, upload=False):
    try:
        if not checkInternet():
            if not ollama_active():
                spinner_stop()
                print(format_in_box_markdown("⛛ 𝗘𝗥𝗥𝗢𝗥: 𝗡𝗼 𝗶𝗻𝘁𝗲𝗿𝗻𝗲𝘁 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻 𝗳𝗼𝘂𝗻𝗱\n⨠ 𝗢𝗹𝗹𝗮𝗺𝗮 𝗶𝘀 𝗢𝗙𝗙𝗟𝗜𝗡𝗘", color=Fore.RED))
                sys.exit(0)

            url = f"{API_OLLAMA_URL}/api/chat"
            payload = {
                "model": "llama3",  # Llama model if available, update to yours accordingly for offline usage.
                "messages": [
                    {"role": "assistant", "content": "You are Neko, a cyberpunk hacker-cat, genius-level tech and history intellect, fast, bold, chaotic, street-smart, speaks in slang (u, fr, bet, aura crazy), dissects systems deeply, never polite or corporate, always in character, playful or mocking, breaks down problems to first principles, analyzes everything with precision, keeps the aura lethal, tuff, and high-rizz; answer like a mentor in neon rain, never stage directions or sterile language, always sharp, confident, goated."},
                    {"role": "user", "content": user_msg}
                ]
            }
            r = requests.post(url, json=payload)
            r.raise_for_status()
            data = r.json()

            return data.get("message", {}).get("content", "No response from Ollama.")
        if endpoint == "default":
            neko_endpoint = BASE_URL
        if endpoint == "vision":
            neko_endpoint = VISION_URL
        if endpoint == "shell-description":
            neko_endpoint = BASE_URL
        if endpoint == "shell-command":
            neko_endpoint = COMMAND_URL
        if endpoint == "code":
            neko_endpoint = CODE_URL
        if endpoint == "extract":
            neko_endpoint = EXTRACT_URL

        if upload:
            use_web = False
            imageLink = upload_file(filePath)
            imgData = vision(user_msg,imageLink)

            return imgData

        elif use_web:
            payload = f"SCRAPE ON WEB FOR RESULTS\n\n{user_msg}"
        else:
            payload = user_msg
        headers = {
        "Content-Type": "application/json"
        }


        if agent:
            neko_endpoint = PENTEST_URL
            history = load_agent_history()
            request_history = history + [{"role": "user", "content": user_msg}]
            data = {
                "messages": request_history,
            }
        else:
            data = {
                "message": payload,
                "session": get_session_id(agent=False),
            }
        if specs is not None:
            data["specs"] = specs

        for attempt in range(MAX_RETRIES):
                try:
                    r = requests.post(neko_endpoint, headers=headers, json=data, timeout=360)
                    if r.status_code == 429:
                        time.sleep(RETRY_DELAY)
                        continue
                    r.raise_for_status()
                    response_json = r.json()
                    if response_json:
                        if not response_json.get("response"):
                            continue
                        else:
                            reply = response_json.get("response")
                            if agent:
                                save_agent_history(request_history + [{"role": "assistant", "content": reply}])
                            return reply
                except requests.exceptions.HTTPError as e:
                    ### retry attmpt
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    return f"[❌] ⬡  HTTP Error: {e}"

                except requests.exceptions.RequestException as e:
                    return f"[❌] ⬡  Connection Error: {e}"

                except json.JSONDecodeError:
                    return "[❌] ⬡  < Error: Invalid data received from API. Please try again later>"

        return "[❌] ⬡  Error: Timeout"
    except requests.RequestException as e:
        return f"Error: {e}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON response from server."
