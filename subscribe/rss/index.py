#!/usr/bin/python3
import datetime, mysql.connector
import xml.etree.ElementTree as ET

#1. Setup to prepare for RSS XML creation
#1.1. Create the basis of an RSS XML tree (spec: https://www.rssboard.org/rss-specification)
#1.1.1. RSS element
rssxml = ET.Element("rss")
rssxml.set("version","2.0")

#1.1.2. Channel element and channel data
rssxml.append(ET.Element("channel"))
rssxml[0].append(ET.Element("title"))
rssxml[0][-1].text = "***FILL THIS IN***"
rssxml[0].append(ET.Element("link"))
rssxml[0][-1].text = "***FILL THIS IN***" #~will need to be modified. Again, .conf file would be helpful here...
rssxml[0].append(ET.Element("description"))
rssxml[0][-1].text = "***FILL THIS IN***"
rssxml[0].append(ET.Element("language"))
rssxml[0][-1].text = "***FILL THIS IN***"
rssxml[0].append(ET.Element("copyright"))
rssxml[0][-1].text = "***FILL THIS IN***"
rssxml[0].append(ET.Element("generator"))
rssxml[0][-1].text = "indieMachine v0.0"
rssxml[0].append(ET.Element("docs"))
rssxml[0][-1].text = "https://www.rssboard.org/rss-specification"

#1.2. Open a database connection (borrowed from edit/home.py)
db = mysql.connector.connect(
    host="***FILL THIS IN***",
    user="***FILL THIS IN***",
    password="***FILL THIS IN***",
    database="***FILL THIS IN***"
) #~in the future, make a .conf file to securely store username and password
dbctrl = db.cursor()



#2. Fill the RSS XML tree
#2.1. First, get the latest 15 posts, in setDate order for now, that have already been released as of right now
dbctrl.execute("select postid,title,description,setDate from posts where setDate <= %s order by setDate desc limit 15",(datetime.datetime.now(),))
postList = dbctrl.fetchall()

#2.2. Then, run through these posts and add their details as <item>s
for post in postList:
    rssxml[0].append(ET.Element("item"))
    rssxml[0][-1].append(ET.Element("title"))
    rssxml[0][-1][-1].text = post[1]
    rssxml[0][-1].append(ET.Element("link"))
    rssxml[0][-1][-1].text = f"***FILL THIS IN***/?id={post[0]}" #~.conf, URL change
    rssxml[0][-1].append(ET.Element("description"))
    rssxml[0][-1][-1].text = post[2]
    
    #~Adding categories is a special case, there can be multiple categories
    dbctrl.execute("select distinct category from categories where postid=%s order by category",(post[0],))
    categList = dbctrl.fetchall()
    for categ in categList:
        rssxml[0][-1].append(ET.Element("category"))
        rssxml[0][-1][-1].text = categ[0]
    
    rssxml[0][-1].append(ET.Element("guid"))
    rssxml[0][-1][-1].text = str(post[0])
    rssxml[0][-1].append(ET.Element("pubDate"))
    rssxml[0][-1][-1].text = post[3].astimezone(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")



#3. Wrap up, and return the RSS XML
#3.1. First, close the database connection
db.close()

print("Content-Type: application/rss+xml\r\n")
print(ET.tostring(rssxml,encoding="unicode",xml_declaration=True))
