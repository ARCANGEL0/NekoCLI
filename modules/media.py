# coded by:
# ┏━┃┏━┃┏━┛┏━┃┏━ ┏━┛┏━┛┃  ┏━┃
# ┏━┃┏┏┛┃  ┏━┃┃ ┃┃ ┃┏━┛┃  ┃ ┃
# ┛ ┛┛ ┛━━┛┛ ┛┛ ┛━━┛━━┛━━┛━━┛
#------------------------------------------

import os
import sys
import subprocess
import mimetypes
import json
import random
import string
import base64
import time
import requests
import re

try:
    from .config import MEDIA_DIR, VIDEO_URL, PHOTOEDIT_URL, IMAGEGEN_URL
except ImportError:
    from modules.config import MEDIA_DIR, VIDEO_URL, PHOTOEDIT_URL, IMAGEGEN_URL
from utils import format_in_box_markdown
from colorama import Fore, Style

def _parse_json_object(raw_text: str):
    if not raw_text:
        return None
    try:
        return json.loads(raw_text)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def _first_dict(payload):
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                return item
    return None

def open_file(image_path: str):
    """
    Opens the image file. ie addedd fix for cross platform compability
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        if sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", image_path], check=True)
        elif sys.platform == "darwin":
            subprocess.run(["open", image_path], check=True)
        elif sys.platform == "win32":
            os.startfile(image_path)
        else:
            print(f"File saved at {image_path}")
    except Exception as e:
        print(f"Failed to open file: {e}")
        print(f"File saved at {image_path}")

def genVideo(prompt: str) -> str:
    os.makedirs(MEDIA_DIR, exist_ok=True)

    payload = {"prompt": prompt}
    timeout_seconds = 300
    start_time = time.time()
    try:
        response = requests.post(
            VIDEO_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

    except Exception as e:
        print(format_in_box_markdown(
            "[🞫] Error: Video request failed!",
            color=Fore.YELLOW
        ))
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        return None

    task_id = data.get("taskId")
    if not task_id:
        print(f"{Fore.RED}API Error: Video Task not initialized{Style.RESET_ALL}")
        print("Server response:", data)
        return None
    file_url = None
    current_percent = 0
    width = 30

    while True:
        if time.time() - start_time > timeout_seconds:
            print("\n\n")
            print(format_in_box_markdown(
                "[ ! ] T I M E O U T - E R R O R",
                color=Fore.YELLOW
            ))
            return None
        if current_percent < 95:
            current_percent += random.randint(1, 12)
            if current_percent > 98:
                current_percent = 98

        fill = int(width * (current_percent / 100))
        bar = Fore.CYAN + "█" * fill + Fore.WHITE + "░" * (width - fill)
        sys.stdout.write(
            f"\r| [{bar}] {Fore.YELLOW}{current_percent}%{Style.RESET_ALL} | "
            f"{Fore.MAGENTA}Rendering Video...{Style.RESET_ALL}"
        )
        sys.stdout.flush()

        time.sleep(10)

        try:
            vid_response = requests.post(
                VIDEO_URL,
                headers={"Content-Type": "application/json"},
                json={"taskId": task_id},
                timeout=20
            )

            vid_response.raise_for_status()
            vid_data = vid_response.json()

        except Exception:
            continue

        status = vid_data.get("status")

        if status == "completed":
            final_bar = Fore.GREEN + "█" * width
            sys.stdout.write(
                f"\r| [{final_bar}] {Fore.GREEN}100%{Style.RESET_ALL} | "
                f"{Fore.GREEN}Success!{Style.RESET_ALL}      \n"
            )
            sys.stdout.flush()

            file_url = vid_data.get("response")
            break
        elif status == "error":
            print(f"\n{Fore.RED}Error from server: {vid_data.get('message')}{Style.RESET_ALL}")
            return None

    if not file_url:
        print(f"{Fore.RED}No video URL returned.{Style.RESET_ALL}")
        return None

    wrdx = re.findall(r"[a-zA-Z0-9]+", prompt.lower())
    new_name = "_".join(wrdx[:6]) if wrdx else "video"
    filename = f"{new_name}_{int(time.time())}.mp4"
    videopath = os.path.join(MEDIA_DIR, filename)

    try:
        with requests.get(file_url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(videopath, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)

        return videopath

    except Exception as e:
        print(f"{Fore.RED}Error downloading video: {e}{Style.RESET_ALL}")
        return None


def editImage(image_path: str, prompt: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(image_path)

    try:
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(format_in_box_markdown(
            f"[🞫] Error reading file!",
            color=Fore.RED
        ))
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        return None

    payload = {
        "prompt": prompt,
        "image": image_base64,
    }

    try:
        response = requests.post(
            PHOTOEDIT_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        match = re.search(r'\{[\s\S]*\}', response.text)
        if not match:
            print(format_in_box_markdown(
                "[🞫] Error: no response from API!!",
                color=Fore.YELLOW
            ))
            return None
        data = json.loads(match.group(0))
    except Exception as e:
        print(format_in_box_markdown(
            "[🞫] Error: Something went wrong!",
            color=Fore.YELLOW
        ))
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        return None

    task_id = data.get("taskId")
    if not task_id:
        print(f"{Fore.RED}API Error: Task not initialized{Style.RESET_ALL}")
        return None

    file_url = None
    current_percent = 0
    width = 30

    while True:
        if current_percent < 98:
            current_percent += random.randint(2, 7)
            if current_percent > 98:
                current_percent = 98

        fill = int(width * (current_percent / 100))
        bar = Fore.CYAN + "█" * fill + Fore.WHITE + "░" * (width - fill)
        sys.stdout.write(f"\r| [{bar}] {Fore.YELLOW}{current_percent}%{Style.RESET_ALL} | {Fore.MAGENTA}Processing...{Style.RESET_ALL}")
        sys.stdout.flush()

        time.sleep(7)

        try:
            editresponse = requests.post(
                PHOTOEDIT_URL,
                headers={"Content-Type": "application/json"},
                json={"taskId": task_id},
                timeout=15
            )
            editresponse.raise_for_status()

            match = re.search(r'\{[\s\S]*\}', editresponse.text)
            if not match:
                continue

            edit_data = json.loads(match.group(0))

            if edit_data.get("status") == "completed":
                final_bar = Fore.GREEN + "█" * width
                sys.stdout.write(f"\r| [{final_bar}] {Fore.GREEN}100%{Style.RESET_ALL} | {Fore.GREEN}Success!{Style.RESET_ALL}      \n")
                sys.stdout.flush()
                file_url = edit_data.get("response")
                break

            elif edit_data.get("status") == "error":
                sys.stdout.write(f"\n{Fore.RED}Error from server: {edit_data.get('message')}{Style.RESET_ALL}\n")
                return None

        except Exception:
            continue

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }

    try:
        download_response = requests.get(file_url, headers=headers, timeout=30, stream=True)
        download_response.raise_for_status()

        os.makedirs(MEDIA_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        edited_image_path = os.path.join(MEDIA_DIR, f"{base_name}_edited.png")

        with open(edited_image_path, "wb") as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)

        return edited_image_path
    except Exception as e:
        print(f"{Fore.RED}Error downloading result: {e}{Style.RESET_ALL}")
        return None

def genImage(prompt: str) -> str:
    os.makedirs(MEDIA_DIR, exist_ok=True)
    payload = {"prompt": prompt}

    try:
        response = requests.post(
            IMAGEGEN_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        if response.status_code >= 400:
            preview = (response.text or "").strip().replace("\n", " ")[:220]
            print(format_in_box_markdown(
                f"[🞫] API returned HTTP {response.status_code}",
                color=Fore.YELLOW
            ))
            if preview:
                print(f"{Fore.RED}{preview}{Style.RESET_ALL}")
            return None

        parsed = _parse_json_object(response.text)
        data = _first_dict(parsed)

    except Exception as e:
        print(format_in_box_markdown(
            "[🞫] Error: Image generation failed 🥀",
            color=Fore.YELLOW
        ))
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        return None

    task_id = data.get("taskId") if data else None
    if not task_id:
        task_id_match = re.search(r'taskId["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]+)', response.text or "")
        if task_id_match:
            task_id = task_id_match.group(1)
    if not task_id:
        preview = (response.text or "").strip().replace("\n", " ")[:220]
        print(f"{Fore.RED}API Error: Task not initialized{Style.RESET_ALL}")
        if preview:
            print(f"{Fore.YELLOW}Raw API response: {preview}{Style.RESET_ALL}")
        return None

    file_url = None
    current_percent = 0
    width = 30
    max_polls = 45
    polls = 0

    while True:
        polls += 1
        if polls > max_polls:
            print(f"\n{Fore.RED}Timed out waiting for image generation status.{Style.RESET_ALL}")
            return None

        if current_percent < 98:
            current_percent += random.randint(2, 7)
            if current_percent > 98:
                current_percent = 98

        fill = int(width * (current_percent / 100))
        bar = Fore.CYAN + "█" * fill + Fore.WHITE + "░" * (width - fill)
        sys.stdout.write(f"\r| [{bar}] {Fore.YELLOW}{current_percent}%{Style.RESET_ALL} | {Fore.MAGENTA}Generating...{Style.RESET_ALL}")
        sys.stdout.flush()

        time.sleep(7)

        try:
            imageresponse = requests.post(
                IMAGEGEN_URL,
                headers={"Content-Type": "application/json"},
                json={"taskId": task_id},
                timeout=15
            )
            imageresponse.raise_for_status()
            if imageresponse.status_code >= 400:
                preview = (imageresponse.text or "").strip().replace("\n", " ")[:180]
                sys.stdout.write(f"\n{Fore.RED}Image status HTTP {imageresponse.status_code}{Style.RESET_ALL}\n")
                if preview:
                    sys.stdout.write(f"{Fore.YELLOW}{preview}{Style.RESET_ALL}\n")
                return None

            parsed_status = _parse_json_object(imageresponse.text)
            imagegendata = _first_dict(parsed_status)
            if not imagegendata:
                continue

            if imagegendata.get("status") == "completed":
                final_bar = Fore.GREEN + "█" * width
                sys.stdout.write(f"\r| [{final_bar}] {Fore.GREEN}100%{Style.RESET_ALL} | {Fore.GREEN}Success!{Style.RESET_ALL}      \n")
                sys.stdout.flush()
                file_url = imagegendata.get("response")
                break

            elif imagegendata.get("status") == "error":
                sys.stdout.write(f"\n{Fore.RED}Error from server: {imagegendata.get('message')}{Style.RESET_ALL}\n")
                return None

        except Exception:
            continue

    if not file_url:
        print(f"{Fore.RED}Error: Image URL not returned by API.{Style.RESET_ALL}")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    }

    try:
        download_response = requests.get(file_url, headers=headers, timeout=360, stream=True)
        download_response.raise_for_status()

        filename = f"gen_{int(time.time())}_{random.randint(1000, 9999)}.png"
        image_path = os.path.join(MEDIA_DIR, filename)

        with open(image_path, "wb") as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)

        return image_path

    except Exception as e:
        print(f"{Fore.RED}Error downloading result: {e}{Style.RESET_ALL}")
        return None

def upload_file(filepath: str) -> str:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(filepath)

    with open(filepath, "rb") as f:
        data = f.read()
    mime = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
    ext = mimetypes.guess_extension(mime) or ".bin"
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    filename = f"{rand}{ext}"
  
    hosts = [
        ("https://catbox.moe/user/api.php", {"reqtype":"fileupload"}, "fileToUpload"),
        ("https://litterbox.catbox.moe/resources/internals/api.php", {"reqtype":"fileupload","time":"72h"}, "fileToUpload"),
        ("https://0x0.st", {}, "file"),
        ("https://tmpfiles.org/api/v1/upload", {}, "file"),
        ("https://i.supa.codes/api/upload", {}, "file"),
        ("https://storage.neko.pe/api/upload.php", {}, "file"),
        ("https://file.btch.rf.gd/api/upload.php", {}, "file"),
        ("https://cdn.meitang.xyz/api/upload.php", {}, "file"),
        ("https://telegra.ph/upload", {}, "file"),
        ("https://api.anonfiles.com/upload", {}, "file"),
    ]

    for url, data_payload, field in hosts:
        try:
            r = requests.post(url, data=data_payload or None, files={field:(filename,data,mime)}, timeout=15)
            r.raise_for_status()
            if "telegra.ph" in url:
                j = r.json()
                if isinstance(j,list) and j[0].get("src"): return "https://telegra.ph"+j[0]["src"]
            elif "tmpfiles.org" in url:
                j = r.json()
                if j.get("status")=="success": return f"https://tmpfiles.org/dl/{j['data']['url'].split('tmpfiles.org/')[1]}"
            elif any(x in url for x in ["supa.codes","neko.pe","btch","cdn.meitang","anonfiles"]):
                j = r.json()
                if j.get("link"): return j["link"]
                if j.get("result",{}).get("url_file"): return j["result"]["url_file"]
                if j.get("result",{}).get("url"): return j["result"]["url"]
                if j.get("data",{}).get("file",{}).get("url",{}).get("full"): return j["data"]["file"]["url"]["full"]
            else:
                txt = r.text.strip()
                if txt.startswith("http"): return txt # img output
        except Exception:
            continue

    raise Exception("[!] Error uploading images: All providers failed")
