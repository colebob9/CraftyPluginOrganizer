"""
CraftyPluginOrganizer v0.6.0
Python

Requires modules from pip:
cfscrape
BeautifulSoup4

Linux only, `curl` and `nodejs` packages required.

Download from sites:
SpigotMC.org
GitHub
BukkitDev
Jenkins CI
EngineHub

TODO:

YAML config for specifying downloads
Add support for uncompressing .zip files.
Look at page if plugin has changed since last download. 
LibreOffice Sheet to convert list into plugin downloader

Clean up most of the output from the script to be more readable.
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
print("CraftyPluginOrganizer v0.6.0\ncolebob9\n")

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
    
# To sort plugins
def organize(pluginName, fileFormat, servers):
    os.chdir("..")
    for s in servers:
        if not os.path.exists("Organized/" + datetime + "/" + s):
            os.mkdir("Organized/" + datetime + "/" + s)
            print("Made " + s + " server directory.")
        shutil.copy("Download/" + pluginName + fileFormat, "Organized/" + datetime + "/" + s + "/" + pluginName + fileFormat)
        print("Copied: " + "Download/" + pluginName + fileFormat + " to " + "Organized/" + datetime + "/" + s + "/" + pluginName + fileFormat)
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

    
# To download a specific version of a plugin from SpigotMC.org. Requires more
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
    
    print('Saved \n\n')

# Put all download methods below here:


# Test Plugins:

# SpigotMC.org
spigotmcLatestDownload("PerWorldInventory", "https://www.spigotmc.org/resources/per-world-inventory.4482/", ".jar", ["Creative", "Survival"])
spigotmcPluginDownload("PerWorldInventory", "https://www.spigotmc.org/resources/per-world-inventory.4482/download?version=151285", ".jar", ["Creative", "Survival"])

# GitHub
githubLatestRelease("ProtocolLib", "https://github.com/dmulloy2/ProtocolLib/releases", ".jar", ["Hub", "Creative", "Survival"])

# BukkitDev
generalCurl("WorldEdit", "https://dev.bukkit.org/projects/worldedit/files/latest", ".jar", ["Hub", "Creative", "Survival"])

# Jenkins CI
jenkinsLatestDownload("Multiverse-Core", "https://ci.onarandombox.com/job/Multiverse-Core/lastSuccessfulBuild/", ".jar", "Multiverse-Core", "SNAPSHOT", ["Hub", "Creative", "Survival"])

# EngineHub
engineHubLatestDownload("WorldEdit-Dev", "http://builds.enginehub.org/job/worldedit/last-successful?branch=master", ".jar", ["Hub", "Creative"])
