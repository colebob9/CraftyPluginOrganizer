"""
CraftyPluginOrganizer v0.2
Python

Requires modules from pip:
cfscrape
BeautifulSoup4

Linux only, curl needed.

Download from sites:
SpigotMC.org
GitHub
BukkitDev
Jenkins CI
any other CI


TODO:

Test SpigotMC with different plugin.
Delete HTML after download is done.
Server folder organizing
Figure out GitHub api link when normal repo url is used.
specify if it is a .zip or .jar


"""


import subprocess
import cfscrape
from bs4 import BeautifulSoup
import os, shutil
import requests

# To find the latest download link from SpigotMC website, then download latest plugin with found link.
def spigotmcLatestDownload(pluginName, url):
    print("[DOWNLOAD] Downloading latest version of " + pluginName + " from SpigotMC.org.\n")
    pluginNameHtml = pluginName + ".html"
    pluginNameJar = pluginName + ".jar"
    spigotMCAddress = "https://www.spigotmc.org/"
    
    # To find link in web page.
    r = requests.get(url)
    
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "html5lib", from_encoding=encoding)
    
    for link in soup.find_all('a', {'class': "inner"}):
        latestDownload = link.get('href')
        # resources/protocollib.1997/download?version=131115
        # https://www.spigotmc.org/resources/protocollib.1997/download?version=131115
        # 
        
        print("Found link: " + latestDownload)
        fullLatestDownload = spigotMCAddress + latestDownload
        print("Full link: " + fullLatestDownload)
    
    # Download latest plugin.

    cookie_arg, user_agent = cfscrape.get_cookie_string(fullLatestDownload)
    print("Downloading jar file: " + pluginNameJar)
    subprocess.call(["curl", "-o", pluginNameJar, "--cookie", cookie_arg, "-A", user_agent, fullLatestDownload])
    

    
# To download a plugin from SpigotMC.org. Needs specific download link.
def spigotmcPluginDownload(pluginName, url):
    print("[DOWNLOAD] Downloading " + pluginName + " from SpigotMC.\n")
    pluginName = pluginName + ".jar"
    cookie_arg, user_agent = cfscrape.get_cookie_string(url)

    subprocess.call(["curl", "-o", pluginName, "--cookie", cookie_arg, "-A", user_agent, url])
    
def githubLatestRelease(pluginName, url): # Currently requires GitHub api link
    print("[DOWNLOAD] Downloading latest release of " + pluginName + " from GitHub")
    cmd = ("""curl -s %s | grep browser_download_url | 
grep '[.]jar' | head -n 1 | cut -d '"' -f 4""" % (url))
    latest = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = latest.communicate()[0]
    output = output.decode('utf8')
    print(output)
    
    subprocess.call(["curl", "-o", pluginName + ".jar", "-L", output])

# For any site that uses a permalink to download a specific or latest version. (Jenkins-LastSuccessfulBuild, Developer's Website, BukkitDev, etc.)
def generalCurl(pluginName, url):
    print("[DOWNLOAD] Downloading " + pluginName + " from URL: " + url)
    subprocess.call(["curl", "-o", pluginName + ".jar", "-L", url])
    
    
# Put all download methods below here:

#generalCurl("ProtocolLib-Dev", "http://ci.dmulloy2.net/job/ProtocolLib/lastSuccessfulBuild/artifact/modules/ProtocolLib/target/ProtocolLib.jar")
#githubLatestRelease("ProtocolLib-GitHub" , "https://api.github.com/repos/dmulloy2/ProtocolLib/releases")
#spigotmcPluginDownload("ProtocolLib-spigotmcPluginDownload", "https://www.spigotmc.org/resources/protocollib.1997/download?version=131115")
spigotmcLatestDownload("ProtocolLib", "https://www.spigotmc.org/resources/protocollib.1997/")
#spigotmcLatestDownload("RogueParkour", "https://www.spigotmc.org/resources/rogueparkour-random-generated-parkour.26563/")

#generalCurl("Vault", "https://dev.bukkit.org/projects/vault/files/latest")
