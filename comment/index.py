#!/usr/bin/python3
import sys, urllib.parse, html, mysql.connector

#1. Get comment data from POST
poststring = sys.stdin.read()
postvalues = {}
for paramstring in poststring.split("&"):
    param = paramstring.split("=")
    if len(param) > 1 and len(param[1]) > 0:
        postvalues[param[0]] = param[1]
        
#1.1. Data clean-up
#~Source for URL "unquoting": https://stackoverflow.com/a/16566128
#~Source for HTML entity escaping: https://docs.python.org/3/library/html.html#html.escape
postvalues["name"] = html.escape(urllib.parse.unquote_plus(postvalues["name"]))
if "weburl" in postvalues:
    postvalues["weburl"] = urllib.parse.unquote(postvalues["weburl"])
    #~I don't think I'm doing enough. I'm simply leaving in the pluses to disrupt the potential for inserting unwanted code, like an endquote and then sketchy attributes afterwards. But will that really be enough?...
else:
    postvalues["weburl"] = None
postvalues["comment"] = "<br>".join((html.escape(urllib.parse.unquote_plus(postvalues["comment"]))).split("\r\n"))



#2. Insert the comment into the MySQL database
#2.1. Open the connection (borrowed from /home.py)
db = mysql.connector.connect(
    host="***FILL THIS IN***",
    user="***FILL THIS IN***",
    password="***FILL THIS IN***!",
    database="***FILL THIS IN***"
) #~in the future, make a .conf file to securely store username and password
dbctrl = db.cursor()

#2.2. Add a row for the comment
dbctrl.execute("insert into comments (postid,name,weburl,comment) values (%s,%s,%s,%s)",(int(postvalues["postid"]),postvalues["name"],postvalues["weburl"],postvalues["comment"]))
db.commit()

#2.3. Close the connection
db.close()



#3. Redirect the user back
#~Source for Python CGI redirects: https://stackoverflow.com/a/17111967
#~Better source for what headers to put: https://stackoverflow.com/a/6156239
print("Status: 303 See other")
print(f"Location: /***FILL THIS IN***/?id={postvalues['postid']}")#~change url domain for final blog, again with that damn .conf file I haven't made
print("Content-Type: text/html\r\n\r\n")#~stupid stupid I hate everything: https://stackoverflow.com/questions/37445901/how-to-return-http-303-from-python
