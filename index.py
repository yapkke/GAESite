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
            pl.add(record)

        self.tv["PUBLICATIONS"] = str(pl)

        return self.tv

    def get_research(self):
        """Populate research
        """
        pl = publications.list("Research Activities")
        pubtable = self.db.GetTables(name="Research")[0]
        records = pubtable.GetRecords(1,  self.config["maxrow"])
        for record in records:
            pl.add(record)

        self.tv["RESEARCH"] = str(pl)

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
    ('/', Index)],
    debug=True)

if __name__ == "__main__":
    run_wsgi_app(application)

