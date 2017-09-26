#! /usr/bin/python
# Python 2.x

import sys

# Set to true to force script to run in UTF8
forceUTF8 = False


if forceUTF8:
  # Set default encoding to 'UTF-8' instead of 'ascii'
  # http://stackoverflow.com/questions/11741574/how-to-set-the-default-encoding-to-utf-8-in-python
  # Bad things might happen though
  reload(sys)
  sys.setdefaultencoding("UTF8")


# Used github3.py - https://github.com/sigmavirus24/github3.py
# install using easy_install github3.py 
#            or pip install github3.py

#User specific values

CODEPLEX_PROJECT = "test.codeplex.com"
GITHUB_PROJECT = "test"
GITHUB_USERNAME = "username"
GITHUB_PASSWORD = "pwd"
GITHUB_ISSUELABEL = "CodePlex"

import urllib2
import HTMLParser
import re, time

try:
  from github3 import login
except ImportError, e:
    print "You haven't installed the github3 package"
    exit()




def getTupleValue(lst, key):
    """From a given list of tuples, searches for the key and returns its corresponding value
        List should be of the form [(a,b),(c,d),(e,f)]"""
    for k, v in lst:
        if k == key:
            return v


class CodePlexWorkItem():
    """Class to represent a single workitem on codeplex"""
    heading = ""
    description = ""
    comments = []
    submittedby = ""
    isClosed = False

    def __init__(self):
            self.comments = []
    
    def AppendHeading(self, h):
        self.heading = self.heading + h
    
    def SetDescription(self, d):
        self.description = d

    def AppendDescription(self, d):
        self.description = self.description + d
    
    def SetSubmittedBy(self, s):
        self.submittedby =  s
        self.description = "<b>" + s + "[CodePlex]</b> <br />" + self.description

    def AddComment(self, c):
        self.comments.insert(0,c)
        
    def SetIsClosed(self, c):
        self.isClosed = c


class IssuesListParser(HTMLParser.HTMLParser):
    """Uses HTMLParser to parse the /workitem/list/basic page for workitem links to follow"""
    itemLinks = []

    def __init__(self, url):
        """Begins the parsing on the given URL"""
        HTMLParser.HTMLParser.__init__(self)
        request = urllib2.urlopen(url)
        self.feed(request.read())



    def handle_starttag(self, tag, attrs):
        if tag == "a" and len(attrs) > 0:
            href = getTupleValue(attrs, "href")
            
            if re.match("(.)*/discussions/[0-9]+", href):
                self.itemLinks.append(href)

    def handle_data(self, data):
        pass


class WorkItemParser(HTMLParser.HTMLParser):
    """Class to handle parsing a /workitem/XXXX page for information"""
    titleFound = False
    titleSet = False
    
    descriptionFound = False
    descriptionSet = False

    commentByFound = False
    commentAreaFound = False
    commentFound = False
    comment = ""
    
    submittedByFound = False
    submittedBySet = False
    
    itemStatusFound = False

    currentWorkItem = None

    def __init__(self, url):
        """Begins the parsing process"""
        HTMLParser.HTMLParser.__init__(self)
        request = urllib2.urlopen(url)
        self.currentWorkItem = CodePlexWorkItem()
        self.currentWorkItem.SetIsClosed(True)
        self.feed(request.read())

    def handle_starttag(self, tag, attrs):

        #print "tag: %s" %(tag)

        if tag == "h1" and len(attrs) > 0: 
            h1Id = getTupleValue(attrs, "class")
            if h1Id == "page_title WordWrapBreakWord":
                self.titleFound = True
                
        if tag == "a" and len(attrs) > 0: 
            h1Id = getTupleValue(attrs, "class")
            if h1Id == "UserProfileLink":
                self.submittedByFound = True

        if tag == "div" and len(attrs) > 0: 
            h1Id = getTupleValue(attrs, "class")
            if h1Id == "markDownOutput ":
                self.descriptionFound = True
                
        if tag == "a" and len(attrs) > 0 and self.submittedBySet: 
            h1Id = getTupleValue(attrs, "class")
            if h1Id == "UserProfileLink":
                self.commentByFound = True

        if tag == "div" and len(attrs) > 0 and self.descriptionSet: 
            h1Id = getTupleValue(attrs, "class")
            if h1Id == "markDownOutput ":
                self.commentFound = True
                
        '''                
        if tag == "p" and len(attrs) > 0: 
            pId = getTupleValue(attrs, "id")
            if pId != None and "VotedLabel" in pId:
                self.itemStatusFound = True
                
        if tag == "div" and len(attrs) > 0:
            divId = getTupleValue(attrs, "id")
            divClass = getTupleValue(attrs, "class")
            #print "   DivId: %s,  DivClass:%s" %(divId, divClass)
            if divId == "descriptionContent":
                self.descriptionFound = True
            elif divId != None and "CommentContainer" in divId:
                self.commentAreaFound = True
            elif self.commentAreaFound and divClass!= None and "markDownOutput" in divClass:
                self.commentFound = True

        if tag == "a" and len(attrs) > 0:
            aId = getTupleValue(attrs, "id")
            if aId != None and "PostedByLink" in aId:
                self.commentByFound = True
            if aId == "ReportedByLink":
                self.submittedByFound = True
        '''

    def handle_data(self, data):
        if self.titleFound and not self.titleSet:
            header = "Discussion: " + data
            self.currentWorkItem.AppendHeading(header)
            self.titleSet = True
            print "Title: %s" %(header)
            
        if self.submittedByFound and not self.submittedBySet:
            self.currentWorkItem.SetSubmittedBy(data)
            self.submittedBySet = True
            print "SubmittedBy: %s" % (data)
            
        if self.descriptionFound and not self.descriptionSet:
            self.currentWorkItem.AppendDescription(data)
            print "Description: %s" % (data)
            
        if self.commentByFound:
            self.comment = "<b>" + data + "[CodePlex]</b> <br />" + self.comment
            self.commentByFound = False
            print "CommentBy: %s" % (data)
            
        if self.commentFound:
            self.comment = self.comment + data
            print "Comment: %s" % (data)
        '''
        if self.itemStatusFound:
            if data == "Closed":
                self.currentWorkItem.SetIsClosed(True)
                
            print "CLOSED: %s" % (True)
        '''
            
    
    def handle_endtag(self, tag):
        if self.descriptionFound and not self.descriptionSet and tag == "div":
            self.descriptionSet = True
        if self.commentFound and tag == "div":
            self.currentWorkItem.AddComment(self.comment)
            self.commentFound = False
            self.comment = ""

        '''
        if self.itemStatusFound and tag == "p":
            self.itemStatusFound = False        
        if self.titleFound and tag == "h1":
            self.titleFound = False
        if self.descriptionFound and tag == "div":
            self.descriptionFound = False
        if self.commentByFound and tag == "a":
            self.commentByFound = False
        if self.commentFound and tag == "div":
            self.commentFound = False
            self.commentAreaFound = False
            self.currentWorkItem.AddComment(self.comment)
            self.comment = ''
        if self.submittedByFound:
            self.submittedByFound = False
        '''
    
    
    def handle_entityref(self, name):
        #print "ref: %s" %(name)
        '''
        if self.descriptionFound:
            self.currentWorkItem.AppendDescription(name)
        #if self.commentFound:
            #self.comment = self.comment + data
        if self.titleFound:
            self.currentWorkItem.AppendHeading(name)
        '''
            
    '''
    def handle_charref(self, name):
        #Don't unescape entities 60 and 62
        if self.descriptionFound:
            self.currentWorkItem.AppendDescription("&#" + name + ";")
        if self.commentFound:
            if name == "60" or name == "62":
                self.comment = self.comment + "&#" + name + ";"
            else:
                self.comment = self.comment + self.unescape("&#" + name + ";")
        if self.titleFound:
            self.currentWorkItem.AppendHeading(self.unescape("&#" + name + ";"))
            
    def handle_startendtag(self, tag, attrs):
        """For self closing tags such as <img /> or <br />"""
        if tag == "br":
            if self.descriptionFound:
                self.currentWorkItem.AppendDescription("<br />")
            if self.commentFound:
                self.comment = self.comment + " <br />"
    '''        


issuesUrlFormat = "http://" + CODEPLEX_PROJECT + "/discussions?field=CreationDate&direction=Ascending&issuesToDisplay=All&keywords=&emailSubscribedItemsOnly=false&size=100&page={pn}"

continuePaging = True
pageNumber = -1
totalLinks = 0

#Extract links from the main issues page
while continuePaging:
    pageNumber += 1
    issuePageUrl = issuesUrlFormat.format(pn=str(pageNumber)) 
    print "Parsing page ", pageNumber, "(", issuePageUrl, ")"

    ilp = IssuesListParser(issuePageUrl)

    if len(ilp.itemLinks) == totalLinks:
        continuePaging = False
        print "Reached end of issue pages"
    else:
        totalLinks = len(ilp.itemLinks)
        continuePaging = True

#print len(ilp.itemLinks), " work item links found"

parsedWorkItems = []


#Loop through, process each work item link
for itemUrl in ilp.itemLinks:
    if "#post" in itemUrl:
        continue

    print "\n\nParsing %s" % (itemUrl)
    #if itemUrl == "http://camlex.codeplex.com/workitem/13992":
    #    print "Skip/////////////////////////////////////////////////"
    #    continue

    wiParser = WorkItemParser(itemUrl)
    #print wiParser.currentWorkItem.heading
    parsedWorkItems.append(wiParser.currentWorkItem)
    #break
    
print len(parsedWorkItems), " work items parsed from CodePlex"

#exit()

#initialize github
gh = login(GITHUB_USERNAME, password=GITHUB_PASSWORD)

for wi in parsedWorkItems:
    print "gh.create_issue(%s,%s,%s,%s,labels=[%s])" % (GITHUB_USERNAME,GITHUB_PROJECT,wi.heading,wi.description,GITHUB_ISSUELABEL)
    newIssue = gh.create_issue(GITHUB_USERNAME,GITHUB_PROJECT,wi.heading,wi.description,labels=[GITHUB_ISSUELABEL])
    if not newIssue:
        print "Unable to create issue"
        continue

    # Github has added an 'abuse prevention' feature which will interrupt this process
    # unless waits are used. Github 'best practice' recommends at least one second
    # between activities; I'm being paranoid and using two second delays.
    time.sleep(2)
    for c in wi.comments:
        newIssue.create_comment(c)
        time.sleep(2)

    if wi.isClosed:
        newIssue.close()
    print "Created Github issue", newIssue.number, "for", "[" + wi.heading + "]"
    time.sleep(3)

print "End of script"
