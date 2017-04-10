"""
CraftyPluginOrganizer v0.1
Python

Requires modules from pip:
cfscrape
BeautifulSoup4
"""

import subprocess
import cfscrape
from bs4 import BeautifulSoup

# To find the latest download link from SpigotMC website, then download latest plugin with found link.
def spigotmcLatestDownload(pluginName, url):
    pluginNameHtml = pluginName + ".html"
    pluginNameJar = pluginName + ".jar"
    spigotMCAddress = "https://www.spigotmc.org/"
    
    # Download HTML to find download link
    cookie_arg, user_agent = cfscrape.get_cookie_string(url)
    print("Downloading HTML...")
    subprocess.call(["curl", "-o", pluginNameHtml, "--cookie", cookie_arg, "-A", user_agent, url])
    
    # To find link in HTML.
    soup = BeautifulSoup(open(pluginNameHtml), "html5lib")
    for link in soup.find_all('a', {'class': "inner"}):
        latestDownload = link.get('href')
        # resources/protocollib.1997/download?version=131115
        # https://www.spigotmc.org/resources/protocollib.1997/download?version=131115
        # 
        print(latestDownload)
        fullLatestDownload = spigotMCAddress + latestDownload
        print("Full link: " + fullLatestDownload)
        cookie_arg, user_agent = cfscrape.get_cookie_string(fullLatestDownload)
    
    # Download latest plugin.
    print("Downloading jar file: " + pluginNameJar)
    subprocess.call(["curl", "-o", pluginNameJar, "--cookie", cookie_arg, "-A", user_agent, fullLatestDownload])

    
# To download a plugin from SpigotMC.org. Needs specific download link.
def spigotmcPluginDownload(pluginName, url):
    pluginName = pluginName + ".jar"
    cookie_arg, user_agent = cfscrape.get_cookie_string(url)

    subprocess.call(["curl", "-o", pluginName, "--cookie", cookie_arg, "-A", user_agent, url])
    


#spigotmcDownload("ProtocolLib", "https://www.spigotmc.org/resources/protocollib.1997/download?version=131115")
spigotmcLatestDownload("ProtocolLib", "https://www.spigotmc.org/resources/protocollib.1997/")
