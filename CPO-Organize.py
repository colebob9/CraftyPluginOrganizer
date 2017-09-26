"""
CraftyPluginOrganizer v0.8.0
Python 3

Requires modules from pip:
cfscrape
BeautifulSoup4

Linux only, `curl` and `nodejs` packages required.

(add more dependencies from github page for cfscrape)

Download from sites:
SpigotMC.org
GitHub
BukkitDev
Jenkins CI
EngineHub

TODO:

Add support for uncompressing .zip files.
Look at page if plugin has changed since last download. 
Add checks to make sure the file exists and is not an html page.
Clean up most of the output from the script to be more readable.
Add clean up for older organized plugin downloads
"""


import subprocess
import os, shutil
import cfscrape
from bs4 import BeautifulSoup
import requests
import time
import json
from urllib.request import urlopen
import configparser

global datetime
global disableSSL

# Config
datetime = time.strftime("%m-%d-%Y--%I:%M%p")
disableSSL = True
configDir = "config"

# End Config

# Title
print("CraftyPluginOrganizer v0.8.0\ncolebob9\n")

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
    print("Made Organized/" + datetime + " directory. All plugins will be sorted here.")
    
# Create config



if not os.path.exists(configDir):
    print("Did not find config directory. Creating...")
    os.mkdir(configDir)

config = configparser.RawConfigParser()
config.optionxform = str

if not os.path.isfile(configDir + "/" + "plugins.cfg"):
    print("Did not find plugins.cfg. Creating example...")
    # SpigotMCLatestDownload
    config.add_section('PerWorldInventory')
    config.set('PerWorldInventory', 'site', "SpigotMCLatest")
    config.set('PerWorldInventory', 'url', "https://www.spigotmc.org/resources/per-world-inventory.4482/")
    config.set('PerWorldInventory', 'filetype', ".jar")
    config.set('PerWorldInventory', 'servers', "Creative,Survival")

    #SpigotMCDownload
    config.add_section('PerWorldInventory2')
    config.set('PerWorldInventory2', 'site', "SpigotMCDownload")
    config.set('PerWorldInventory2', 'url', "https://www.spigotmc.org/resources/per-world-inventory.4482/download?version=151285")
    config.set('PerWorldInventory2', 'filetype', ".jar")
    config.set('PerWorldInventory2', 'servers', "Creative,Survival")

    # GitHubLatestRelease
    config.add_section('ProtocolLib')
    config.set('ProtocolLib', 'site', "GitHubRelease")
    config.set('ProtocolLib', 'url', "https://github.com/dmulloy2/ProtocolLib/releases")
    config.set('ProtocolLib', 'filetype', ".jar")
    config.set('ProtocolLib', 'servers', "Hub,Creative,Survival")

    # BukkitDev / GeneralCurl
    config.add_section('WorldEdit')
    config.set('WorldEdit', 'site', "Curl")
    config.set('WorldEdit', 'url', "https://dev.bukkit.org/projects/worldedit/files/latest")
    config.set('WorldEdit', 'filetype', ".jar")
    config.set('WorldEdit', 'servers', "Hub,Creative,Survival")


    # Jenkins CI
    config.add_section('Multiverse-Core')
    config.set('Multiverse-Core', 'site', "Jenkins")
    config.set('Multiverse-Core', 'url', "https://ci.onarandombox.com/job/Multiverse-Core/lastSuccessfulBuild/")
    config.set('Multiverse-Core', 'filetype', ".jar")
    config.set('Multiverse-Core', 'servers', "Hub,Creative,Survival")
    config.set('Multiverse-Core', 'searchfor', "Multiverse-Core")
    config.set('Multiverse-Core', 'searchforend', "SNAPSHOT")


    # EngineHub
    config.add_section('WorldEdit-Dev')
    config.set('WorldEdit-Dev', 'site', "EngineHub")
    config.set('WorldEdit-Dev', 'url', "http://builds.enginehub.org/job/worldedit/last-successful?branch=master")
    config.set('WorldEdit-Dev', 'filetype', ".jar")
    config.set('WorldEdit-Dev', 'servers', "Hub,Creative")


    with open(configDir + "/" + 'plugins.cfg', 'w') as configfile:
        config.write(configfile)
        
    print("An example plugins.cfg has been created.")
    print("Please configure and launch again.")
    

def organize(pluginName, fileFormat, servers):
    os.chdir("..")
    
    # To check plugin was downloaded correctly
    
    # To sort plugins
    for s in servers:
        if not os.path.exists("Organized/" + datetime + "/" + s):
            os.mkdir("Organized/" + datetime + "/" + s)
            print("Made " + s + " server directory.")
        fromDownloadJar = "Download/" + pluginName + fileFormat
        toOrganizedJar = "Organized/" + datetime + "/" + s + "/" + pluginName + fileFormat
        shutil.copy(fromDownloadJar, toOrganizedJar)
        print("Copied: " + fromDownloadJar + " to " + toOrganizedJar)
    print("")
    
    
    

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

    
# To download a specific version of a plugin from SpigotMC.org. Requires specific version download link.
def spigotmcPluginDownload(pluginName, url, fileFormat, servers):
    os.chdir("Download")
    print("[DOWNLOAD] Downloading " + pluginName + " from SpigotMC.\n")
    
    cookie_arg, user_agent = cfscrape.get_cookie_string(url)

    subprocess.call(["curl", "-o", pluginName + fileFormat, "--cookie", cookie_arg, "-A", user_agent, url])
    organize(pluginName, fileFormat, servers)
    
def githubLatestRelease(pluginName, url, fileFormat, servers):
    os.chdir("Download")
    # Convert to API link
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
    
    # Rewritten code! Yay!
    response = urlopen(url).read().decode('utf8')
    jsonDict = json.loads(response)
    
    #print(jsonDict)
    latestDownloadLink = jsonDict[0]['assets'][0]['browser_download_url']
    print("Found latest release download: " + latestDownloadLink)
    
    print("Using curl command:")
    print(["curl", "-o", pluginName + fileFormat, "-L", latestDownloadLink])
    subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", latestDownloadLink])
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
    
def engineHubLatestDownload(pluginName, url, fileFormat, servers):
    # Modified code from obzidi4n's plugins.py script
    # get page
    r = requests.get(url)

    # parse download link with BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    soup2 = soup.find(class_="col-md-8")
    soup3 = soup2.find('a')
    target = soup3['href']

    response = requests.get(target, stream=True, verify=False)
    fileName = pluginName + fileFormat

    # report
    print('Plugin:', pluginName)
    print('Target:', target)
    print('File: ', fileName, '\n')

    os.chdir("Download")
    print("[DOWNLOAD] Downloading " + pluginName + " from EngineHub.")
    subprocess.call(["curl", "-o", pluginName + fileFormat, "-L", target])
    
    organize(pluginName, fileFormat, servers)

    
config.read(configDir + "/" + "plugins.cfg")
for each_section in config.sections():
    #spigotmcLatestDownload(pluginName, url, fileFormat, servers)
    
    site = config.get(each_section, 'site')
    url = config.get(each_section, 'url')
    filetype = config.get(each_section, 'filetype')
    servers = (config.get(each_section, 'servers')).split(',')
    
    
    if site == "SpigotMCLatest":
        spigotmcLatestDownload(each_section, url, filetype, servers)
    elif site == "SpigotMCDownload":
        spigotmcPluginDownload(each_section, url, filetype, servers)
    elif site == "GitHubRelease":
        githubLatestRelease(each_section, url, filetype, servers)
    elif site == "Curl":
        generalCurl(each_section, url, filetype, servers)
    elif site == "Jenkins":
        searchFor = config.get(each_section, 'searchfor')
        searchForEnd = config.get(each_section, 'searchforend')
        jenkinsLatestDownload(each_section, url, filetype, searchFor, searchForEnd, servers)
    elif site == "EngineHub":
        engineHubLatestDownload(each_section, url, filetype, servers)
    else:
        print(each_section + " has an invalid site: " + site)
        print("Please fix in your plugins.cfg config")
        
        
