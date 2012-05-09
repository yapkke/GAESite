#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.runtime import DeadlineExceededError
import gdata.spreadsheet.text_db as ss
import yapkke.features as features
import yapkke.publications as publications
import os
import simplejson
import random

class GDocsPage(webapp.RequestHandler):
    def get_config(self, filename='config.json'):
        configfile = open(os.path.join(os.path.dirname(__file__),
                                       filename), "r")
        configstr = ""
        for l in configfile:
            configstr += l
        self.config = simplejson.loads(configstr)
        configfile.close()

    def get_db(self, name):
        client = ss.DatabaseClient(username=self.config["username"],
                                   password=self.config["password"])
        try:
            dbs = client.GetDatabases(name=name)
            if (len(dbs) == 0):
                self.response.out.write("Spreadsheet for website is not found...")
                return None
            return dbs[0]
        except DeadlineExceededError:
            self.response.redirect("http://yappke.appspot.com")
            self.response.out.write("This operation could not be completed in time...\nTrying again...")
            return None

    def get_table(self, name):
        try:
            return self.db.GetTables(name=name)[0]
        except DeadlineExceededError:
            self.response.redirect("http://yappke.appspot.com")
            self.response.out.write("This operation could not be completed in time...\nTrying again...")
            return None

    def get_records(self, table, start=1, end=None):
        if (end == None):
            end = self.config["maxrow"]
        try:
            return table.GetRecords(start,  end)
        except DeadlineExceededError, SSLCertificateError:
            self.response.redirect("http://yappke.appspot.com")
            self.response.out.write("This operation could not be completed in time...\nTrying again...")
            return None

class Bib(GDocsPage):
    def get(self):
        #Configuration file
        self.get_config()

        #Generate response
        self.response.headers["Content-Type"] = "text/plain"
        table = self.request.get("table")
        index = self.request.get("index")
        r = ""
        if (table=="" and index==""):
            #Everything
            self.client = ss.DatabaseClient(username=self.config["username"],
                                            password=self.config["password"])
            self.db = self.get_db(self.config["spreadsheet"])
            if (self.db == None):
                return
            for tname in ["Publications", "Research"]:
                table = self.get_table(tname)
                if (table == None):
                    return
                records = self.get_records(table)
                if (records == None):
                    return
                for record in records:
                    r += self.get_bib(record) + "\n\n"
        else:
            #Specific entry
            self.client = ss.DatabaseClient(username=self.config["username"],
                                            password=self.config["password"])
            self.db = self.get_db(self.config["spreadsheet"])
            table = self.get_table(table)
            if (table == None):
                return
            record = table.GetRecord(row_number=int(index)+1)
            r = self.get_bib(record)
            
        self.response.out.write(r)

    def get_bib(self, record):
        if (record.content["bibtex"] != None):
            return record.content["bibtex"]
        else:
            b = ""
            if (record.content["authors"] != None):
                b += "author = {"+\
                     self.format_authors(record.content["authors"])+"},\n"
            if (record.content["title"] != None):
                b += "title = {"+record.content["title"]+"},\n"

            b = "@misc{"+str(abs(hash(b)))+",\n"+b
            
            if (record.content["month"] != None):
                b += "month = {"+record.content["month"]+"},\n"
            if (record.content["year"] != None):
                b += "year = {"+record.content["year"]+"},\n"
            if (record.content["venue"] != None):
                b += "howpublished = {"+record.content["venue"]+"},\n"
            else:
                b += "howpublished = {"+self.config["defaultlink"]+"},\n"
            if (record.content["highlight"] != None):
                b += "note = {"+record.content["highlight"]+"},\n"
            else:
                if (record.content["note"] != None):
                    b += "note = {"+record.content["note"]+"},\n"

            b += "}"
            return b

    def format_authors(self, auth):
        authors = ""
        auths = auth.strip().split(",")
        for au in auths:
            aut = au.strip()
            splitindex = aut.index(" ")
            authors += aut[splitindex:].strip()+", "+\
                       aut[:splitindex].strip()
            if (auths.index(au) != (len(auths)-1)):
                authors += " and "
        return authors
    
class Main(GDocsPage):
    def get_teaching(self):
        """Populate teaching
        """
        cl = publications.courselist()
        ctable = self.get_table(name="Teaching")
        if (ctable == None):
            return
        records = self.get_records(ctable)
        if (records == None):
            return
        for record in records:
            cl.add(record)

        self.tv["TEACHING"] = str(cl)

        return self.tv

    def get_sharing(self, title=True):
        """Populate sharing
        """
        sl = publications.sharelist("Shared")
        stable = self.get_table(name="Sharing")
        if (stable == None):
            return
        records = self.get_records(stable)
        if (records == None):
            return
        for record in records:
            sl.add(record)

        self.tv["SHARING"] = sl.get_str(title=title)

        return self.tv

    def get_quote(self):
        """Get quote
        """
        pubtable = self.get_table(name="Quotes")
        if (pubtable == None):
            return
        records = self.get_records(pubtable)
        if (records == None):
            return
        index = random.randint(0, len(records)-1)
        self.tv["QUOTE"] = '''%s ---%s
        ''' % (records[index].content["quote"], records[index].content["person"])

        return self.tv

    def get_publications(self, title=True):
        """Populate publications
        """
        pl = publications.list("Publications")
        pubtable = self.get_table(name="Publications")
        if (pubtable == None):
            return
        records = self.get_records(pubtable)
        if (records == None):
            return
        for record in records:
            pl.add(record, records.index(record))

        self.tv["PUBLICATIONS"] = pl.get_str("Publications", title=title)

        return self.tv

    def get_research(self):
        """Populate research
        """
        pl = publications.list("Research Activities")
        pubtable = self.get_table(name="Research")
        if (pubtable == None):
            return
        records = self.get_records(pubtable)
        if (records == None):
            return
        for record in records:
            pl.add(record, records.index(record))

        self.tv["RESEARCH"] = pl.get_str("Research")

        return self.tv

    def get_divisions(self, add_mode, add_change_to_single=True):
        """Populate divisions
        """
        self.tv["DIVISIONS"] = ""
        divtable = self.get_table(name="Divisions")
        if (divtable == None):
            return
        records = self.get_records(divtable)
        if (records == None):
            return
        for record in records:
            divstr = '''<div style="'''
            for k,v in record.content.items():
                if ((k != "content") and
                    (v != None)):
                    divstr += k+":"+v+";"
            divstr += '''">%s</div>\n''' % record.content["content"]
            self.tv["DIVISIONS"] += divstr

        if (add_mode):
            self.tv["DIVISIONS"] += self.add_mode(add_change_to_single)

        return self.tv

    def get_about_me(self, add_mode, add_change_to_single=False):
        """Populate divisions
        """
        self.tv["ABOUT_ME"] = ""
        divtable = self.get_table(name="About Me")
        if (divtable == None):
            return
        records = self.get_records(divtable)
        if (records == None):
            return
        for record in records:
            divstr = '''<div style="'''
            for k,v in record.content.items():
                if ((k != "content") and
                    (v != None)):
                    divstr += k+":"+v+";"
            divstr += '''">%s</div>\n''' % record.content["content"]
            self.tv["ABOUT_ME"] += divstr

        if (add_mode):
            self.tv["ABOUT_ME"] += self.add_mode(add_change_to_single)

        return self.tv

    def add_mode(self, add_change_to_single):
        array = "<div>&nbsp</div>"
        if (add_change_to_single):
            array += "<div><small>View <a href=\"/single\">all-in-one version</a>.</small></div>"
        else:
            array += "<div><small>View <a href=\"/\">normal version</a>.</small></div>"
        array += "<div><small>Click on <font color=red>(+)</font>/<font color=red>(--)</font> to expand/collapse each item below...</small></div>"

        return array

    def get_settings(self):
        """Populate values from Settings table
        """
        settingtable = self.get_table(name="Settings")
        if (settingtable == None):
            return
        records = self.get_records(settingtable)
        if (records == None):
            return
        for record in records:
            if (record.content["item"] == "Google Analytics"):
                self.tv["google_analytics"] = features.get_google_analytics(record.content["value"])
            elif (record.content["item"] == "Stylesheet"):
                self.tv["css_link"] = features.get_css(record.content["value"])
            elif (record.content["item"] == "Javascript"):
                self.tv["js_link"] = features.get_js(record.content["value"])
            else:
                self.tv[record.content["item"]] = str(record.content["value"])
        
        return self.tv

class Multi(Main):
    def get(self):
        #Configuration file
        self.get_config()
        
        ##Dictionary for values
        self.tv = {}

        ##Get information from spreadsheet
        self.db = self.get_db(self.config["spreadsheet"])
        if (self.db == None):
            return
       
        self.get_settings()
        self.get_divisions(True)
        self.get_items()
        self.get_more()
        self.get_quote()
        
        ##Generate response
        path = os.path.join(os.path.dirname(__file__),
                            'templates/index.html')
        self.response.out.write(template.render(path, self.tv))        

    def get_more(self):
        pass

    def get_items(self):
        self.tv["ITEMS"] = "<br>"
        for i in range(0,len(NAMES)):
            if (len(NAMES[i]) > 0):
                if (isinstance(self, PAGES[i][1])):
                    self.tv["ITEMS"] += "<h1 class=pages>"+NAMES[i]+"</h1>"
                else:
                    self.tv["ITEMS"] += "<div><a class=pages href=\""+PAGES[i][0]+"\">"+NAMES[i]+"</a></div>"
                
        return self.tv

class Index(Multi):
    def get_more(self):
        self.get_about_me(False)

class Publications(Multi):
    def get_more(self):
        self.get_publications(False)
        
class Research(Multi):
    def get_more(self):
        self.get_research()
        self.get_teaching()

class Sharing(Multi):
    def get_more(self):
        self.get_sharing(False)

class Single(Main):
    def get(self):
        #Configuration file
        self.get_config()
        
        ##Dictionary for values
        self.tv = {}

        ##Get information from spreadsheet
        self.db = self.get_db(self.config["spreadsheet"])
        if (self.db == None):
            return

        self.get_settings()
        self.get_divisions(False)
        self.get_about_me(True)
        self.get_publications()
        self.get_research()
        self.get_teaching()
        self.get_sharing()
        self.get_quote()
        
        ##Generate response
        path = os.path.join(os.path.dirname(__file__),
                            'templates/index.html')
        self.response.out.write(template.render(path, self.tv))    

PAGES = [('/bib', Bib),
         ("/", Index),
         ("/publications",Publications),
         ("/research", Research),
         ("/sharing", Sharing),
         ("/single", Single)]
NAMES = ["","About Me", "Publications", "Research/Teaching", "Miscellaneous", ""]
application = webapp.WSGIApplication(PAGES, debug=True)

if __name__ == "__main__":
    run_wsgi_app(application)

