import requests
from bs4 import BeautifulSoup
import re
import subprocess
import psutil
import os
import sys
import ctypes
import time

# Not working function
def task_exists(task_name):
    cmd = f"schtasks /query /tn {task_name}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return "The specified task name was not found" not in result.stdout

task_name = "AutoBetterDiscord"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

if is_admin():
    # Function to download file from a link
    def download_file(url, file_name):
        response = requests.get(url, stream=True)
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)

    # Function to extract download link from a URL
    def find_nodejs_link(url, pattern):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        links = soup.find_all('a', href=re.compile(pattern))
        return links[0]['href'] if links else None

    # Function to retrieve Git download link
    def find_git_link(url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        link = soup.find('a', {'id': 'auto-download-link'})
        return link['href'] if link else None

    # Get Git download link
    git_url = "https://git-scm.com/download/win"
    git_link = find_git_link(git_url)

    # Check Git file name
    git_file_name = "./git-installer.exe"

    # Check if files exist before downloading
    if not os.path.isfile(git_file_name):
        if git_link:
            download_file(git_link, git_file_name)
            subprocess.call([git_file_name])

    # Get Node.js download link
    nodejs_url = "https://nodejs.org/en/download/current"
    nodejs_pattern = r"/dist/v\d+\.\d+\.\d+/node-v\d+\.\d+\.\d+-x64.msi"
    nodejs_link = find_nodejs_link(nodejs_url, nodejs_pattern)

    # Check Node.js file name
    nodejs_file_name = "./node-installer.msi"

    # Check if files exist before downloading
    if not os.path.isfile(nodejs_file_name):
        if nodejs_link:
            download_file(nodejs_link, nodejs_file_name)
            subprocess.call(["msiexec", "/i", nodejs_file_name.replace("./", "")])


    # Clone repo
    batch_git_content = "git clone https://github.com/BetterDiscord/BetterDiscord.git"
    with open('AutoBetterDiscord.bat', 'w') as batch_git:
        batch_git.write(batch_git_content)
    subprocess.run("Git_Source.bat", shell=True)

    time.sleep(5)

    # Update and inject BetterDiscord
    batch_file_content = '@echo off\ncd BetterDiscord\ngit pull\necho Y | npm install -g pnpm\necho Y | pnpm install\necho Y | pnpm build\npnpm inject'
    with open('AutoBetterDiscord.bat', 'w') as batch_file:
        batch_file.write(batch_file_content)
    subprocess.run("AutoBetterDiscord.bat", shell=True)

    # Task scheduling
    def execute_on_startup(task_name):
        script_path = sys.argv[0]  # Get the absolute path of the currently running Python script
        script_path = os.path.abspath(script_path)
        script_directory = os.path.dirname(script_path)
        batch_file_path = os.path.join(script_directory, f"{task_name}.bat")

        # Create the scheduled task on system startup
        subprocess.run(f"schtasks /create /tn {task_name} /tr {batch_file_path} /sc onlogon /ru System", shell=True)

    try :
        execute_on_startup(task_name)
    except Exception :
        print("Task already exist !")

    # Debug
    # time.sleep(100)

    # Kill the Discord.exe process
    for process in psutil.process_iter():
        if process.name() == "Discord.exe":
            process.kill()

    # subprocess.run('C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe', shell=True)


else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
