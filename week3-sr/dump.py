#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import requests
import re
from bs4 import BeautifulSoup
import sys

# FIXME: Python package in the repos is too old!
# It should be upgraded and this line removed.
requests.packages.urllib3.disable_warnings()


if len(sys.argv) < 3:
    sys.stderr.write("Usage: %s <username> <password>\n"%sys.argv[0])
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]

# Subject to change!
list_url = "https://www.csrsupport.com/filter.php?f=YToxOntzOjE6ImIiO2E6MTp7czoxOiJ0IjthOjU6e2k6MDtpOjA7aToxO2k6MztpOjI7aTo0O2k6MztpOjE7aTo0O2k6Mjt9fX0%3d&m=psltr&y=ld"

payload = {
    "action" : "login",
    "returnto" : "/",
    "username" : username,
    "password" : password,
    "submit" : "Log in"
}

session = requests.Session()
login_request = session.post("https://www.csrsupport.com/post.php", data=payload)
listing = session.get(list_url)

# Change a list to a set and back to list ... to remove duplicates.
ids = list(set(re.findall("https://www.csrsupport.com/issue.php\?iid=(\d+)", listing.text)))

all_contents = {}

for sr_id in ids:
    messages = []
    print "Getting: %s"%sr_id
    html = session.get("https://www.csrsupport.com/issue.php?iid=%s"%sr_id)
    soup = BeautifulSoup(html.text, "lxml")
    for child in soup.findAll("table")[1].children:
        th = child.findChildren("th")[0]
        td = child.findChildren("td")[0]
        author = th.findChildren("a")[0].text
        date = th.text.replace(author, "").replace("[Get Link]", "")
        message = td.text.replace("[Quote Issue]", "")
        messages.append({
                    "author" : author,
                    "date" : date,
                    "message" : message
                })
    all_contents[sr_id] = messages
        
pickle.dump(all_contents, open("all.p", "wb"))
