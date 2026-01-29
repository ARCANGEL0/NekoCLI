
<div align="center">
<img src="nekocli.gif" width="250">

# ₊ ⊹ 𝗡𝗲𝗸𝗼_𝗖𝗟𝗜
<br>

**AI assistant for your terminal, able to view, edit or generate images; create short videos; generate and save code/scripts; run commands and answer or assist with any subject.**

[![Stars](https://img.shields.io/github/stars/ARCANGEL0/NekoCLI?style=for-the-badge&color=353535)](https://github.com/ARCANGEL0/NekoCLI)
[![Watchers](https://img.shields.io/github/watchers/ARCANGEL0/NekoCLI?style=for-the-badge&color=353535)](https://github.com/ARCANGEL0/NekoCLI)
[![Forks](https://img.shields.io/github/forks/ARCANGEL0/NekoCLI?style=for-the-badge&color=353535)](https://github.com/ARCANGEL0/NekoCLI/fork)
[![Repo Views](https://komarev.com/ghpvc/?username=NekoCLI&color=353535&style=for-the-badge&label=REPO%20VIEWS)](https://github.com/ARCANGEL0/NekoCLI)
[![AI](https://img.shields.io/badge/AI-Powered-cyan.svg?style=for-the-badge)](#)
![Version](https://img.shields.io/badge/version-5.6-blue?style=for-the-badge&color=00aacc)

![GitHub issues](https://img.shields.io/github/issues/ARCANGEL0/NekoCLI?style=for-the-badge&color=3f3972)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ARCANGEL0/NekoCLI?style=for-the-badge&color=3f3972)
![GitHub contributors](https://img.shields.io/github/contributors/ARCANGEL0/NekoCLI?style=for-the-badge&color=3f3972)
![GitHub last commit](https://img.shields.io/github/last-commit/ARCANGEL0/NekoCLI?style=for-the-badge&color=3f3972)

</div>



## ⬡ 𝗔𝗯𝗼𝘂𝘁 𝗡𝗘𝗞𝗢

NEKO is a lightweight, fast, and utility AI assistant for your terminal, to be acessible anytime you need.  
It supports multiple flags and modes with a tidy formatted and colourful output in your terminal window such as persistent chat history, code mode, shell mode, video generation, image edition and creation, web search, vision mode and an optional pentest agent (experimental).

## ᗢ Features

- **Fast & Lightweight** – Minimal dependencies, instant startup with a single binary.
- **Multiple Modes** – Generic AI chat with GPT5 + Web search and Real time content, shell commands and execution, code generation & save to file, image analysis, pentest mode with interactive and autonomous execution.
- **Formatted output** – Easy visualization data on terminal, outputs are displayed in colorful colorama boxes.
- **Persistent History** – Keeps context of chat if used with persistence flags. Chat history is saved in ~/.config/nekocli/chats.json
- **Free endpoint** – All the AI logic is run with my own API endpoint, alternatively ollama can be used for offline mode, change base api of *:11434 by editing the OLLAMA_BASE_URL.
- **Media file handling** - Neko can not only visualize images, but also generate videos & images and edit them based on user's prompt.
---

## ⟢ Installation .ᐟ

Clone the repository and make Neko globally available:

```bash
git clone https://github.com/ARCANGEL0/NekoCLI
cd NekoCLI
chmod +x neko.py
sudo mv neko.py /usr/bin/neko
```

## 𐱃 Usage

You can call neko anywhere in your terminal along with a prompt to make a question, you can also pass stdin arguments for NEKO to read.

```shell
$ cat serverLogs.txt | neko "Analyze these logs and return a solution for it"
```

You can also use custom flags for different agent modes in NEKO.

Usage: neko [options] {question or prompt}

| Flag | Description |
|---------|-------------|
| `-w` / `--web` | Ask with web searching and realtime results |
| `-c` / `--code` | Tells neko to handle code generation, to create a fully working code, being able to save directly onto file |
| `-s` / `--shell` | Tells neko to interpret, generate and run shells commands based on user request. |
| `-i` / `--interactive`   | Starts neko chat with persistent chat history saved on ~/.config/nekocli |
| `-f` / `--file` | Sends an image along with user prompt for neko to analyze. |
| `-g` / `--generate` | Asks Neko to generate an image using a prompt |
| `-gv` / `--generate-video` | Asks Neko to generate a small 8 seconds video using a prompt |
| `-e` / `--edit` | Asks Neko to edit an image based on your request |
| `-a` / `--auto` | (EXPERIMENTAL FEATURE [!]) Autonomous multi-step offensive security mode, pass an initial prompt and let neko autorun commands and learn from outputs and generate next steps continuously over a target|
| `-x` / `--agent` | Starts neko in cybersecurity agent mode, handling security, pentest questions and giving advices on command outputs |
| `-r` / `--reset` | Erases chat history saved on ~/.config/nekocli |
| `-h` / `--help` | Displays the help menu |
| `-u` / `--update` | Updates Neko |
| `-v` / `--version` | Displays current version |

### ⑇ Examples
```bash
$ neko -s "list all files sorted by size" # generates a command and asks user if he wants to Run it.
$ neko -c "Python script to merge two CSV files" # generates a short text and full python code, and asks user to copy code or save as a file in local dir.
$ neko -w "Latest CVE for OpenSSL in the last 2 months" # searches web for all possible index and findings on user prompt (CVE searches)
$ neko -a "Help me in a pentest process, to enumerate this IP 10.10.x.x and get a webshell" # neko will provide suggestions and commands to be run and ask authorization to run them, after running he will self collect the logs, analyze and suggest next steps and repeat the cycle.
$ neko -f /home/user/kitty.jpg "can you tell me the color of this cat?"
$ neko -g "Please generate an image of Donald trump vs Joe Biden in a MMA Octagon ring, both fighting" # Image generation with Neko
$ neko -gv "A video of a orange cat walking slowly in a cyberpunk city" # Video generation with Neko, usually a short video of 6 to 8 seconds.
$ neko -e /home/user/selfie.jpg "Please change the background and remove the people on it" # Neko will modify the image with AI and obey the request to remove people on background
$ neko -i "Tell me about Rutherford atom model" # after output, you will have option to ask a new question i.e: ''What about Schrodinger model?'' and continue conversation in context.
$ neko -x "i need help to enumerate 192.168.0.10 for open ports" # neko will return a small and a list of commands to be run by user, and ask them to retrieve the logs by calling command again, as in example below
$ cat nmapOutput.txt | neko -x "i have run nmap and found these info, what do you suggest now?" # Continues conversation saved on chat.json, analyzes nmap output and proceeds to suggest next steps
$ neko -r # resets all chat history.
$ neko --version # Outputs v5.6 🐈
```



## 🗈 Project Note

Not much to say, I just needed an interactive AI to speed up my workflow in terminals, and assist at pentesting or coding and hitting Alt + Tab consistently to navigate through documentations, chatGPT for assistance, among other things can be quite annoying. <br>
And most repo's that offer similar solutions always require an OpenAI key, which I, as an Engineer Grad. student, cannot afford because by tides of destiny, I was born poor. <br>
So I decided to make my own CLI assistant using G4F for Free GPT 5-1 with reasoning and vision capabilities without costs. 🐈

---

<div align="center">

### ❤️ Support

[![Star on GitHub](https://img.shields.io/github/stars/ARCANGEL0/NekoCLI?style=social)](https://github.com/ARCANGEL0/NekoCLI)
[![Follow on GitHub](https://img.shields.io/github/followers/ARCANGEL0?style=social)](https://github.com/ARCANGEL0)
<br>

<a href='https://ko-fi.com/J3J7WTYV7' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<br>
<strong>Hack the world. Byte by Byte.</strong> ⛛ <br>
𝝺𝗿𝗰𝗮𝗻𝗴𝗲𝗹𝗼 @ 2025

**[[ꋧ]](#About)**

</div>
