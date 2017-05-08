"""
CraftyPluginOrganizer v0.5.1
Python

Requires modules from pip:
cfscrape
BeautifulSoup4

Linux only, curl and jsnode packages required.

Download from sites:
SpigotMC.org
GitHub
BukkitDev
Jenkins CI

TODO:

YAML config for specifying downloads
Add support for uncompressing .zip files.
EngineHub
Test with real server plugins
Get real name of file if possible (http://stackoverflow.com/questions/6881034/curl-to-grab-remote-filename-after-following-location)
Look at page if plugin has changed since last download. 
BungeeCord Downloading? (Could also be put in AutoBuildTools.)
LibreOffice Sheet to convert list into plugin downloader

"""


import subprocess
import os, shutil
import cfscrape
from bs4 import BeautifulSoup
import requests
import time

global datetime
global disableSSL

# Config
datetime = time.strftime("%m-%d-%Y--%I:%M%p")
disableSSL = True

# End Config

# Title
print("CraftyPluginOrganizer v0.5.1\ncolebob9")

# Delete Download directory
if os.path.exists("Download"):
    print("Deleting Download Directory...")
    shutil.rmtree("Download")

# Make directories
if not os.path.exists("Download"):
    os.mkdir("Download")
    print("Made Download directory. All downloaded plugins will be stored here.")
if not os.path.exists("Organized"):
    os.mkdir("Organized")
    print("Made Organized directory. All plugins will be sorted here.")
if not os.path.exists("Organized/" + datetime):
    os.mkdir("Organized/" + "/" + datetime)
    print("Made Organized/" + datetime + "directory. All plugins will be sorted here.")
    
# To sort plugins
def organize(pluginName, fileFormat, servers):
    os.chdir("..")
    for s in servers:
        if not os.path.exists("Organized/" + datetime + "/" + s):
            os.mkdir("Organized/" + datetime + "/" + s)
            print("Made " + s + " server directory.")
        shutil.copy("Download/" + pluginName + fileFormat, "Organized/" + datetime + "/" + s + "/" + pluginName + fileFormat)
        print("Copied: " + "Download/" + pluginName + fileFormat + " to " + "Organized/" + datetime + "/" + s + "/" + pluginName + fileFormat)
    

# To find the latest download link from SpigotMC website, then download latest plugin with found link.
# Make sure this is used with a resource that has the download through SpigotMC, not a redirect to another website.
def spigotmcLatestDownload(pluginName, url, fileFormat, servers):
    os.chdir("Download")
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

        print("Found link: " + latestDownload)
        fullLatestDownload = spigotMCAddress + latestDownload
        print("Full link: " + fullLatestDownload)
    
    # Download latest plugin.
    cookie_arg, user_agent = cfscrape.get_cookie_string(fullLatestDownload)
    print("Downloading jar file: " + pluginName + fileFormat)
    subprocess.call(["curl", "-o", pluginName + fileFormat, "--cookie", cookie_arg, "-A", user_agent, fullLatestDownload])
    # Sometimes fails with ProtocolLib, used too much?
    organize(pluginName, fileFormat, servers)

    
# To download a plugin from SpigotMC.org. Needs specific download link.
def spigotmcPluginDownload(pluginName, url, fileFormat, servers):
    os.chdir("Download")
    print("[DOWNLOAD] Downloading " + pluginName + " from SpigotMC.\n")
    pluginName = pluginName + fileFormat
    cookie_arg, user_agent = cfscrape.get_cookie_string(url)

    subprocess.call(["curl", "-o", pluginName, "--cookie", cookie_arg, "-A", user_agent, url])
    organize(pluginName, fileFormat, servers)
    
def githubLatestRelease(pluginName, url, fileFormat, servers):
    os.chdir("Download")
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
    # Rewrite with python code
    cmd = ("""curl -s %s | grep browser_download_url | grep '[.]%s' | head -n 1 | cut -d '"' -f 4""" % (url, fileFormat[1:]))
    latest = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = latest.communicate()[0]
    output = output.decode('utf8')
    print(output)
    
    # Take /n off
    output = output.rstrip() 
    
    print("Using curl command:")
    print(["curl", "-o", pluginName + fileFormat, "-L", output])
    subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", output])
    organize(pluginName, fileFormat, servers)
    
# For any site that uses a permalink to download a specific or latest version. (BukkitDev, Developer's Website, etc.)
def generalCurl(pluginName, url, fileFormat, servers):
    os.chdir("Download")
    print("[DOWNLOAD] Downloading " + pluginName + " from URL: " + url)
    subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", url])
    
    organize(pluginName, fileFormat, servers)
    
def jenkinsLatestDownload(pluginName, url, fileFormat, searchFor, searchForEnd, servers):
    os.chdir("Download")
    try:
        r = requests.get(url)
    except requests.exceptions.SSLError:
        #disableSSL = input("The script has detected that this website\'s SSL certificates are causing problems. (Most likely an untrusted SSL cert.) \nWould you like to disable SSL to continue? (ONLY DISABLE IF YOU TRUST THE SITE) y/n: ").lower()
        if disableSSL == True:
            r = requests.get(url, verify=False)
        elif disableSSL == False:
            print("skipping...")
            return
        
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(r.content, "html5lib", from_encoding=encoding)
    #soup = (soup.decode("utf-8"))
    
    for link in soup.find_all('a'):
        hrefLink = str(link.get('href'))
        #print(hrefLink) # Only uncomment if you want to see every link it finds on the page.
        if hrefLink.count(searchFor):
            if hrefLink.endswith(searchForEnd + fileFormat):
                latestDownload = hrefLink
    
    print("File found: " + latestDownload)
    latestDownloadLink = url + latestDownload
    print("Full link: " + latestDownloadLink)

    print("[DOWNLOAD] Downloading " + pluginName + " from Jenkins CI.")
    if disableSSL == True:
        subprocess.call(["curl", "-k", "-o", pluginName + fileFormat, "-L", latestDownloadLink])
    else:
        subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", latestDownloadLink])

    organize(pluginName, fileFormat, servers)
    
# Put all download methods below here:

# Test plugins
spigotmcLatestDownload("CommandSigns", "https://www.spigotmc.org/resources/command-signs.10512/", ".jar", ["SkyBlock"])
generalCurl("CoreProtect", "https://dev.bukkit.org/projects/coreprotect/files/latest", ".jar", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])
jenkinsLatestDownload("EssentialsX", "https://ci.drtshock.net/job/essentialsx/lastSuccessfulBuild/", ".jar", "EssentialsX-2", "", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])
jenkinsLatestDownload("EssentialsX-Spawn", "https://ci.drtshock.net/job/essentialsx/lastSuccessfulBuild/", ".jar", "EssentialsXSpawn-2", "", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])
generalCurl("Modifyworld", "https://dev.bukkit.org/projects/modifyworld/files/latest", ".jar", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])
jenkinsLatestDownload("Multiverse-Core", "https://ci.onarandombox.com/job/Multiverse-Core/lastSuccessfulBuild/", ".jar", "Multiverse-Core", "SNAPSHOT", ["Hub", "Creative", "Survival"])
generalCurl("NoCheatPlus", "https://dev.bukkit.org/projects/nocheatplus/files/latest", ".jar", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])  # Not sure to do BukkitDev or Jenkins
spigotmcLatestDownload("NuVotifier", "https://www.spigotmc.org/resources/nuvotifier.13449/", ".jar", ["Hub", "Creative", "Survival"])
generalCurl("PermissionsEx", "https://dev.bukkit.org/projects/permissionsex/files/latest", ".jar", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])
spigotmcLatestDownload("PerWorldInventory", "https://www.spigotmc.org/resources/per-world-inventory.4482/", ".jar", ["Creative", "Survival"])
generalCurl("uSkyBlock", "https://dev.bukkit.org/projects/uskyblock/files/latest", ".jar", ["SkyBlock"])
generalCurl("Vault", "https://dev.bukkit.org/projects/vault/files/latest", ".jar", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])
generalCurl("WorldEdit", "https://dev.bukkit.org/projects/worldedit/files/latest", ".jar", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])
generalCurl("WorldGuard", "https://dev.bukkit.org/projects/worldguard/files/latest", ["Hub", "Creative", "Survival", "SkyBlock", "OldCreative"])

