#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import gdata.spreadsheet.text_db as ss
import yapkke.features as features
import yapkke.publications as publications
import os
import simplejson
import random

class Bib(webapp.RequestHandler):
    def get(self):
        #Configuration file
        configfile = open(os.path.join(os.path.dirname(__file__), 'config.json'), "r")
        configstr = ""
        for l in configfile:
            configstr += l
        self.config = simplejson.loads(configstr)
        configfile.close()

        #Generate response
        self.response.headers["Content-Type"] = "text/plain"
        table = self.request.get("table")
        index = self.request.get("index")
        r = ""
        if (table=="" and index==""):
            #Everything
            self.client = ss.DatabaseClient(username=self.config["username"],
                                            password=self.config["password"])
            self.db = self.client.GetDatabases(name=self.config["spreadsheet"])[0]
            for tname in ["Publications", "Research"]:
                table = self.db.GetTables(name=tname)[0]
                records = table.GetRecords(1,  self.config["maxrow"])
                for record in records:
                    r += self.get_bib(record) + "\n\n"
        else:
            #Specific entry
            self.client = ss.DatabaseClient(username=self.config["username"],
                                            password=self.config["password"])
            self.db = self.client.GetDatabases(name=self.config["spreadsheet"])[0]
            table = self.db.GetTables(name=table)[0]
            record = table.GetRecord(row_number=int(index)+1)
            r = self.get_bib(record)
            
        self.response.out.write(r)

    def get_bib(self, record):
        if (record.content["bibtex"] != None):
            return record.content["bibtex"]
        else:
            b = ""
            if (record.content["authors"] != None):
                b += "author = {{"+record.content["authors"]+"}},\n"
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
    
    
class Index(webapp.RequestHandler):
    def get(self):
        #Configuration file
        configfile = open(os.path.join(os.path.dirname(__file__), 'config.json'), "r")
        configstr = ""
        for l in configfile:
            configstr += l
        self.config = simplejson.loads(configstr)
        configfile.close()
        
        ##Dictionary for values
        self.tv = {}

        ##Get information from spreadsheet
        self.client = ss.DatabaseClient(username=self.config["username"],
                                        password=self.config["password"])
        self.db = self.client.GetDatabases(name=self.config["spreadsheet"])[0]
        self.get_settings()
        self.get_divisions()
        self.get_publications()
        self.get_research()
        self.get_teaching()
        self.get_sharing()
        self.get_quote()
        
        ##Generate response
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, self.tv))

    def get_teaching(self):
        """Populate teaching
        """
        cl = publications.courselist()
        ctable = self.db.GetTables(name="Teaching")[0]
        records = ctable.GetRecords(1,  self.config["maxrow"])
        for record in records:
            cl.add(record)

        self.tv["TEACHING"] = str(cl)

        return self.tv

    def get_sharing(self):
        """Populate sharing
        """
        sl = publications.sharelist("Shared")
        stable = self.db.GetTables(name="Sharing")[0]
        records = stable.GetRecords(1,  self.config["maxrow"])
        for record in records:
            sl.add(record)

        self.tv["SHARING"] = str(sl)

        return self.tv

    def get_quote(self):
        """Get quote
        """
        pubtable = self.db.GetTables(name="Quotes")[0]
        records = pubtable.GetRecords(1,  self.config["maxrow"])
        index = random.randint(0, len(records)-1)
        self.tv["QUOTE"] = '''%s ---%s
        ''' % (records[index].content["quote"], records[index].content["person"])

        return self.tv

    def get_publications(self):
        """Populate publications
        """
        pl = publications.list("Publications")
        pubtable = self.db.GetTables(name="Publications")[0]
        records = pubtable.GetRecords(1,  self.config["maxrow"])
        for record in records:
            pl.add(record, records.index(record))

        self.tv["PUBLICATIONS"] = pl.get_str("Publications")

        return self.tv

    def get_research(self):
        """Populate research
        """
        pl = publications.list("Research Activities")
        pubtable = self.db.GetTables(name="Research")[0]
        records = pubtable.GetRecords(1,  self.config["maxrow"])
        for record in records:
            pl.add(record, records.index(record))

        self.tv["RESEARCH"] = pl.get_str("Research")

        return self.tv

    def get_divisions(self):
        """Populate divisions
        """
        self.tv["DIVISIONS"] = ""
        divtable = self.db.GetTables(name="Divisions")[0]
        records = divtable.GetRecords(1,  self.config["maxrow"])
        for record in records:
            divstr = '''<div style="'''
            for k,v in record.content.items():
                if ((k != "content") and
                    (v != None)):
                    divstr += k+":"+v+";"
            divstr += '''">%s</div>\n''' % record.content["content"]
            self.tv["DIVISIONS"] += divstr

        return self.tv

    def get_settings(self):
        """Populate values from Settings table
        """
        settingtable = self.db.GetTables(name="Settings")[0]
        records = settingtable.GetRecords(1, self.config["maxrow"])
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
    

application = webapp.WSGIApplication([
    ('/bib', Bib),
    ('/', Index)],
    debug=True)

if __name__ == "__main__":
    run_wsgi_app(application)

