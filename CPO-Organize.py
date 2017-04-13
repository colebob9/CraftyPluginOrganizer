"""
CraftyPluginOrganizer v0.4
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

Server folder organizing: date -> Server
    Use arguement in function call to specify which server directories to copy to.
YAML config for configuration
Add support for uncompressing .zip files.


"""


import subprocess
import os, shutil
import cfscrape
from bs4 import BeautifulSoup
import requests


if not os.path.exists("Download"):
    os.mkdir("Download")
    print("Made Download folder. All downloaded plugins will be stored here.")
os.chdir("Download")
    

# To find the latest download link from SpigotMC website, then download latest plugin with found link.
# Make sure this is used with a resource that has the download through SpigotMC, not a redirect to another website.
def spigotmcLatestDownload(pluginName, url, fileFormat):
    print("[DOWNLOAD] Downloading latest version of " + pluginName + " from SpigotMC.org.\n")
    pluginNameHtml = pluginName + ".html"
    spigotMCAddress = "https://www.spigotmc.org/"
    scraper = cfscrape.create_scraper()
    
    # To find link in web page.
    #r = requests.get(url)
    r = scraper.get(url)
    
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
    print("Downloading jar file: " + pluginName + fileFormat)
    subprocess.call(["curl", "-o", pluginName + fileFormat, "--cookie", cookie_arg, "-A", user_agent, fullLatestDownload])
    # Sometimes fails with ProtocolLib, used too much?
    

    
# To download a plugin from SpigotMC.org. Needs specific download link.
def spigotmcPluginDownload(pluginName, url, fileFormat):
    print("[DOWNLOAD] Downloading " + pluginName + " from SpigotMC.\n")
    pluginName = pluginName + fileFormat
    cookie_arg, user_agent = cfscrape.get_cookie_string(url)

    subprocess.call(["curl", "-o", pluginName, "--cookie", cookie_arg, "-A", user_agent, url])
    
def githubLatestRelease(pluginName, url, fileFormat):
    print("Link: " + url)
    if url.startswith('https://github.com'):
        print("URL is a normal release link. Converting to an API link...")
        url = "https://api.github.com/repos" + url[18:]
        print("API link: " + url)
    elif url.startswith("https://api.github.com") and url.endswith("releases"):
        print("URL is an API link. Proceeding...")
    else:
        print("GitHub link may be invalid, proceeding as if it is an API link.")
    
    
    print("[DOWNLOAD] Downloading latest release of " + pluginName + " from GitHub")
    cmd = ("""curl -s %s | grep browser_download_url | grep '[.]%s' | head -n 1 | cut -d '"' -f 4""" % (url, fileFormat[1:]))
    latest = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = latest.communicate()[0]
    output = output.decode('utf8')
    print(output)
    
    subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", output])

# For any site that uses a permalink to download a specific or latest version. (Developer's Website, BukkitDev, etc.)
def generalCurl(pluginName, url, fileFormat):
    print("[DOWNLOAD] Downloading " + pluginName + " from URL: " + url)
    subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", url])
    
def jenkinsLatestDownload(pluginName, url, fileFormat):
    r = requests.get(url)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "html5lib", from_encoding=encoding)
    #soup = (soup.decode("utf-8"))
    
    for link in soup.find_all('a'):
        hrefLink = str(link.get('href'))
        #print(hrefLink) # Only uncomment if you want to see 
        bukkit = "bukkit"
        if hrefLink.count(bukkit):
            if hrefLink.endswith(fileFormat):
                latestDownload = hrefLink
    
    print("File found: " + latestDownload)
    latestDownloadLink = url + latestDownload
    print("Full link: " + latestDownloadLink)

    print("[DOWNLOAD] Downloading " + pluginName + " from Jenkins CI.")
    subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", latestDownloadLink])

    
# Put all download methods below here:
jenkinsLatestDownload("FastAsyncWorldEdit", "http://ci.athion.net/job/FastAsyncWorldEdit/lastSuccessfulBuild/artifact/target/", ".jar")



"""
#generalCurl("ProtocolLib-Dev", "http://ci.dmulloy2.net/job/ProtocolLib/lastSuccessfulBuild/artifact/modules/ProtocolLib/target/ProtocolLib.jar")
#githubLatestRelease("ProtocolLib-GitHub" , "https://github.com/dmulloy2/ProtocolLib/releases")
#spigotmcPluginDownload("ProtocolLib-spigotmcPluginDownload", "https://www.spigotmc.org/resources/protocollib.1997/download?version=131115")
spigotmcLatestDownload("ProtocolLib", "https://www.spigotmc.org/resources/protocollib.1997/")
#spigotmcLatestDownload("RogueParkour", "https://www.spigotmc.org/resources/rogueparkour-random-generated-parkour.26563/")

#generalCurl("Vault", "https://dev.bukkit.org/projects/vault/files/latest")
"""
