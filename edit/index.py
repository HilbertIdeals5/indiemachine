#!/usr/bin/python3

#1. Prepare to respond to request
import os, sys, urllib.parse, datetime, dateutil, base64, mysql.connector, defusedxml.ElementTree
import xml.etree.ElementTree as ET

#1.0. Save the root directory of the blog, to serve as a "working directory" (added in after-the-fact, should also be moved to a .conf file)
blogroot = "***FILL THIS IN***"
blogwebroot = "***FILL THIS IN***/"

#1.1. Retrieve POST data, log it, and process XML into a dictionary
#~Source of CGI GET and POST: https://stackoverflow.com/a/27893309
poststring = sys.stdin.read()

#logfile = open(f"{blogroot}log.txt","a")
#logfile.write("[PYTHON] Request made on " + datetime.datetime.today().strftime("%Y/%m/%d, at %H:%M:%S") + "...\r\n" + poststring + "\r\n\r\n") #~in the future, log.txt should also be put in the same separate, secure folder that the .conf file will be in

requestXML = defusedxml.ElementTree.fromstring(poststring)
#1.1.1. Refactor XML object into an easier-to-use JSON-like structure
methodCall = {}

def processValue(valueElem): #~Value tags must be processed specially, because the "scalar" data type tags are optional and may or may not be there
    if len(valueElem) > 0:
        match valueElem[0].tag:
            case "i4":
                return int(valueElem[0].text)
            case "int":
                return int(valueElem[0].text)
            case "boolean":
                return bool(int(valueElem[0].text))
            case "double":
                return float(valueElem[0].text)
            case "dateTime.iso8601":
                returnDate = dateutil.parser.isoparse(valueElem[0].text)
                if returnDate.tzinfo == None: #~assume a client has matched the timezone this server has told it, which will always be UTC
                    returnDate.replace(tzinfo=datetime.timezone.utc) #~Source: https://www.geeksforgeeks.org/how-to-make-a-timezone-aware-datetime-object-in-python/
                return returnDate.astimezone(dateutil.tz.tzlocal()) #~Source: https://stackoverflow.com/a/35058346. This assumes that MySQL's timezone setting is still set to match system time, so this needs a more adaptive solution later.
            case "base64":
                return base64.b64decode(valueElem[0].text)
            case "struct":
                returnValue = {}
                for member in valueElem[0]:
                    returnValue[member[0].text] = processValue(member[1])
                return returnValue
            case "array":
                returnValue = []
                for item in valueElem[0][0]:
                    returnValue.append(processValue(item))
                return returnValue
            case _: #~default is always string
                return str(valueElem[0].text)
    return valueElem.text

for childElem in requestXML:
    if childElem.tag == "methodName":
        methodCall["methodName"] = childElem.text
    if childElem.tag == "params":
        methodCall["params"] = []
        for param in childElem:
            methodCall["params"].append(processValue(param[0]))



#1.2. Define functions for creating XML-RPC responses

#1.2.1 XML-based function for setting up scalar values, structs, and arrays (explained in the comment next to processValue())
def createValue(value): #~probably too verbose? I'll figure out how to condense this down later, if it's even possible. E.g. can ints be directly inserted through Element.text?
    if type(value) is int:
        returnXML = ET.Element("int")
        returnXML.text = str(value)
    elif type(value) is bool:
        returnXML = ET.Element("boolean")
        returnXML.text = str(int(value))
    elif type(value) is float:
        returnXML = ET.Element("double")
        returnXML.text = str(value)
    elif type(value) is datetime.datetime: #~let's hope this works! source for what to check: https://stackoverflow.com/a/68743663
        returnXML = ET.Element("dateTime.iso8601")
        returnXML.text = value.astimezone(datetime.timezone.utc).strftime("%Y%m%dT%H:%M:%SZ") #~that Z at the end is important!!! It tells WLW that the timezone is UTC.
        #~!!! For now, this code assumes MySQL is using system time, so a little-bit-better solution should be made later (retrieving MySQL settings).
    #elif type(value) is base64:~obviously not complete, this is just a rough note/marker to let me know that I haven't implemented this yet
        #returnXML =
    elif type(value) is dict:
        returnXML = ET.Element("struct")
        for key in value:
            returnXML.append(ET.Element("member"))
            returnXML[-1].append(ET.Element("name"))
            returnXML[-1][0].text = key
            returnXML[-1].append(ET.Element("value"))
            returnXML[-1][1].append(createValue(value[key]))
    elif type(value) is list:
        returnXML = ET.Element("array")
        returnXML.append(ET.Element("data"))
        for entry in value:
            returnXML[0].append(ET.Element("value"))
            returnXML[0][-1].append(createValue(entry))
    else: #~default is always string
        returnXML = ET.Element("string")
        returnXML.text = str(value)
    return returnXML

#1.2.2 XML-based function for producing a normal response
def methodResponse(value):
    returnXML = defusedxml.ElementTree.fromstring("<?xml version=\"1.0\"?><methodResponse><params><param><value></value></param></params></methodResponse>")
    returnXML[0][0][0].append(createValue(value))
    return ET.tostring(returnXML,encoding="unicode",xml_declaration=True)

#1.2.3. XML-based revision to formerly string-based function for producing a fault response
def faultResponse(faultCode,faultString):
    returnXML = returnXML = defusedxml.ElementTree.fromstring("<?xml version=\"1.0\"?><methodResponse><fault><value></value></fault></methodResponse>")
    returnXML[0][0].append(createValue({
        "faultCode": int(faultCode),
        "faultString": str(faultString)
    }))
    return ET.tostring(returnXML,encoding="unicode",xml_declaration=True)



#1.3. Open the database connection
db = mysql.connector.connect(
    host="***FILL THIS IN***",
    user="***FILL THIS IN***",
    password="***FILL THIS IN***",
    database="***FILL THIS IN***"
) #~in the future, make a .conf file to securely store username and password
dbctrl = db.cursor()



#1.4. MIME-type header and subsequent blank line are required for CGI scripts
print("Content-Type: text/xml\r\n")





#2. Produce XML-RPC response
responseText = ""

#2.0.1 Function for checking username and password (they're in different goddamn positions for every goddamn method call, GODDAMMIT. And a rare single MT method call requires NO CREDENTIALS AT ALL)
def userpassOK(userPos,passPos):
    if not (methodCall["params"][userPos] == "***FILL THIS IN***" and methodCall["params"][passPos] == "***FILL THIS IN***"):
        #~in the future, put the blog username and password in a .conf file too
        global responseText
        responseText += faultResponse(1,"Either your username or password is incorrect.")#~will be revised later, fault code is likely temporary
        return False #~allows entire case to be skipped, a hacky workaround because "break" isn't supported in match-case (damn, Python, get with the program)
    else:
        return True
        


# 2.1. Decide based on what method was called
match methodCall["methodName"]:

    case "blogger.getUsersBlogs":
        if userpassOK(1,2): #~tragically, credentials-checking is on a per-method basis
            responseText += methodResponse([
                {
                    "url": str(f"{blogwebroot}"),
                    "blogid": str("0"),
                    "blogName": str("Dummy Blog")
                }
            ])
    
    case "metaWeblog.getCategories":
        if userpassOK(1,2):
            #~Source for eliminating duplicates: https://stackoverflow.com/a/12239206
            dbctrl.execute("select distinct category from categories")
            categList = dbctrl.fetchall()
            
            responseText += methodResponse([{"description":categ[0]} for categ in categList])
    
    case "metaWeblog.getRecentPosts":
        if userpassOK(1,2):
            #~.1. Get a list of all posts as per request
            dbctrl.execute("select postid,title,description,setDate from posts order by postid desc limit %s",[int(methodCall["params"][3])])
            queryResult = dbctrl.fetchall()
            
            #~.2. Assemble list of structs
            recentPosts = []
            for entry in queryResult:
                #~Added in after-the-fact for category support
                dbctrl.execute("select distinct category from categories where postid=%s order by category",(entry[0],))
                categList = dbctrl.fetchall()
            
                recentPosts.append({
                    "postid": str(entry[0]),
                    "title": str(entry[1]),
                    "link": str(f"{blogwebroot}post/?id={entry[0]}"),
                    "description": str(entry[2]),
                    "categories": [categ[0] for categ in categList],
                    "dateCreated": entry[3]
                })
                
            #~.3. Assemble final methodResponse
            responseText += methodResponse(recentPosts)
    
    case "metaWeblog.newPost":
        if userpassOK(1,2):
            #~Similar to editPost
            if methodCall["params"][4] == True:
                #~.1. Requests won't always have ALL data, so create parallel lists of what post properties were sent (THIS NEEDS TO BE MADE INTO YET ANOTHER FUNCTION, ALL THE DAMN FUNCTIONS. Or maybe...it could be combined into the methodCall function?? Hrm...idk. This is more specific to handling post structs, which not every methodCall has.)
                postCols = []
                postVals = []
                for key in methodCall["params"][3]:
                    match key:
                        case "title":
                            postCols.append("title")
                            postVals.append(methodCall["params"][3][key])
                        case "description":
                            postCols.append("description")
                            postVals.append(methodCall["params"][3][key])
                        case "dateCreated":
                            postCols.append("setDate")
                            postVals.append(methodCall["params"][3][key])
                        case _:
                            continue
            
                #~.2. Add database row using data sent in request
                dbctrl.execute(f"insert into posts ({','.join(postCols)}) values ({','.join(['%s'] * len(postVals))})",postVals) #~Source for creating identical-element list: https://stackoverflow.com/a/3459131
                db.commit()
                
                #~.2.1. Now that you have a postid, also create entries for categories
                if "categories" in methodCall["params"][3]:
                    #~Get the new post's postid
                    dbctrl.execute("select postid from posts order by postid desc limit 1")
                    postid = dbctrl.fetchone()[0] #~this all looks awfully familiar to substep 3...opportunity to condense code later on
                
                    for category in methodCall["params"][3]["categories"]:
                        dbctrl.execute("insert into categories (category,postid) values (%s,%s)",(category,postid))
                        db.commit()
                
                #~.3. Return postid of latest post
                dbctrl.execute("select postid from posts order by postid desc limit 1")
                responseText += methodResponse(str(dbctrl.fetchone()[0]))
            else:
                #~ Currently, saving as an online draft isn't supported
                responseText += faultResponse(0,"The weblog server does not currently support saving drafts online.")#~will be revised later, fault code of 0 is temporary
    
    case "metaWeblog.getPost":
        if userpassOK(1,2):
            #~.1. Get the requested post
            dbctrl.execute("select postid,title,description,setDate from posts where postid = %s",[int(methodCall["params"][0])])
            queryResult = dbctrl.fetchone()
            
            #~Added in after-the-fact for category support
            dbctrl.execute("select distinct category from categories where postid=%s order by category",[int(methodCall["params"][0])])
            categList = dbctrl.fetchall()
            
            #~.2. Assemble struct
            responseText += methodResponse({
                "postid": str(queryResult[0]),
                "title": str(queryResult[1]),
                "link": str(f"{blogwebroot}post/?id={queryResult[0]}"),
                "description": str(queryResult[2]),
                "categories": [categ[0] for categ in categList],
                "dateCreated": queryResult[3]
            })
    
    case "blogger.deletePost":
        if userpassOK(2,3):
            #~.1. Remove database rows with postid
            dbctrl.execute("delete from posts where postid = %s",(int(methodCall["params"][1]),))
            dbctrl.execute("delete from categories where postid = %s",(int(methodCall["params"][1]),))
            db.commit()
            
            #~.2. Return boolean True as success message
            responseText += methodResponse(True)
    
    case "metaWeblog.editPost":
        if userpassOK(1,2):
            if methodCall["params"][4] == True:
                #~.1. Requests won't always have ALL data, so create parallel lists of what post properties were sent (THIS NEEDS TO BE MADE INTO YET ANOTHER FUNCTION, ALL THE DAMN FUNCTIONS. Or maybe...it could be combined into the methodCall function?? Hrm...idk. This is more specific to handling post structs, which not every methodCall has.)
                postCols = []
                postVals = []
                for key in methodCall["params"][3]:
                    match key:
                        case "title":
                            postCols.append("title")
                            postVals.append(methodCall["params"][3][key])
                        case "description":
                            postCols.append("description")
                            postVals.append(methodCall["params"][3][key])
                        case "dateCreated":
                            postCols.append("setDate")
                            postVals.append(methodCall["params"][3][key])
                        case "categories": #~behavior unique to editPost
                            #~Get all pre-existing categories for the post
                            dbctrl.execute("select distinct category from categories where postid=%s order by category",[int(methodCall["params"][0])])
                            categList = [categ[0] for categ in dbctrl.fetchall()]
                            
                            #~Add new ones
                            for applyCateg in methodCall["params"][3][key]:
                                if applyCateg not in categList:
                                    dbctrl.execute("insert into categories (category,postid) values (%s,%s)",(applyCateg,int(methodCall["params"][0])))
                                    db.commit()
                            
                            #~Prune removed ones
                            for existCateg in categList:
                                if existCateg not in methodCall["params"][3][key]:
                                    dbctrl.execute("delete from categories where category = %s and postid = %s",(existCateg,int(methodCall["params"][0])))
                                    db.commit()
                        case _:
                            continue
            
                #~.2. Update database row using data sent in request
                dbctrl.execute(f"update posts set {','.join([f'{key}=%s' for key in postCols])} where postid=%s",postVals + [int(methodCall["params"][0])])
                db.commit()
                
                #~.3. Return boolean True as success message
                responseText += methodResponse(True)
            else:
                #~ Currently, saving as an online draft isn't supported
                responseText += faultResponse(0,"The weblog server does not currently support saving drafts online.")#~will be revised later, fault code of 0 is temporary
    
    case "metaWeblog.newMediaObject":
        if userpassOK(1,2):
            #~Major resource: https://stackoverflow.com/a/12517490
            #~.1. Prepare directory and filename before saving the media
            mediaDir = os.path.dirname(methodCall["params"][3]["name"])
            mediaFName = os.path.basename(methodCall["params"][3]["name"])
            
            #~.1.1. Check if desired directory exists - make it if not
            if not os.path.exists(os.path.join(blogroot,"Graphics/media",mediaDir)):
                os.makedirs(os.path.join(blogroot,"Graphics/media",mediaDir)) #~I'm not worried about "race condition" for now
            
            #~.1.2. Check if desired filename exists - alter if so
            if os.path.exists(os.path.join(blogroot,"Graphics/media",mediaDir,mediaFName)):
                dupeNum = 1
                while os.path.exists(os.path.join(blogroot,"Graphics/media",mediaDir,f"/dupe{dupeNum}-"+mediaFName)):
                    dupeNum += 1
                mediaFName = f"dupe{dupeNum}-" + mediaFName #~not the most elegant naming, will adjust later
            
            #~.2. Actually save the media
            with open(os.path.join(blogroot,"Graphics/media",mediaDir,mediaFName),"wb") as mediaFile:
                mediaFile.write(methodCall["params"][3]["bits"])
            
            #~.3. Return media URL
            responseText += methodResponse({"url":urllib.parse.urljoin(blogwebroot,os.path.join("Graphics/media",mediaDir,urllib.parse.quote_plus(mediaFName)))})
    
    case _:
        responseText += faultResponse(0,"Your blogging application sent a command called \"" + methodCall["methodName"] + "\", which the weblog server doesn't understand.")#~will be revised later, fault code of 0 is temporary
    


#2.2. Finally output to HTTP response body
#if methodCall["methodName"] != "metaWeblog.newMediaObject":
    #logfile.write("Server-generated response:\r\n" + responseText + "\r\n\r\n")
print(responseText)





#3. Wrap up
#logfile.close()
db.close()
