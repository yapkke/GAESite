MONTHS = ["", "January ", "February ", "March ", "April ", "May ", "June ",
          "July ", "August ", "September ", "October ", "November ", "December "]
KEYITEMS = [None, "topic", "title", "authors", "month", "year",
            "venue", "location", "highlight", "bibtex", "note"]

class list:
    """Class to handle publications
    """
    def __init__(self, title):
        self.title = title
        self.topic = []
        self.name = []

    def add(self, record):
        if (record.content["topic"] not in self.name):
            self.name.append(record.content["topic"])
            self.topic.append(topic(record.content["topic"]))
        self.topic[self.name.index(record.content["topic"])].add(record.content)

    def __str__(self):
        publist = "<h2>"+self.title+"</h2>\n"
        publist += "<ul>"
        for t in self.topic:
            publist += str(t)
        publist += "</ul>"
        
        return publist

class topic:
    """Class to repesent a topic
    """
    def __init__(self, name):
        self.name = name
        self.papers = []

    def add(self, content):
        self.papers.append(paper(content))

    def __str__(self):
        plist = "<li><b>"+self.name+"</b>\n"+\
                "<ul name=items>"
        for p in self.papers:
            plist += str(p)
        plist += "</ul>"+\
                 "</li><br>"
        return plist

class paper:
    """Class to represent a paper
    """
    def __init__(self, content):
        self.content = content

    def __str__(self):
        pstr = "<li>"+self.content["title"]
        if (self.content["highlight"] != None):
            pstr += "<div class=highlight>"+\
                    "&nbsp;"*7+\
                    self.content["highlight"]+"</div>"
        pstr+=  "<ul>"
        if (self.content["authors"] != None):
            pstr += self.content["authors"]+"<br>"

        if (self.content["year"] != None):
            month = 0
            if (self.content["month"] != None):
                month = self.content["month"]
            pstr += MONTHS[int(month)]+self.content["year"]
            if (self.content["location"] != None):
                pstr += ", "+self.content["location"]
            pstr += "<br>"
        
        if (self.content["venue"] != None):
            pstr += self.content["venue"]+"<br>"
        if (self.content["note"] != None):
            pstr += self.content["note"]+"<br>"

        hasLink = False
        for k,l in self.content.items():
            if ((l != None) and (k not in KEYITEMS)):
                hasLink = True
                pstr += "<a href=\""+l+"\">"+k.title()+"</a>"+"&nbsp;"*2
        if (hasLink):
            pstr += "<br>"
            
        pstr += "<br></ul>"
        pstr += "</li>"

        return pstr
