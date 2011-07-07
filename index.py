#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import gdata.spreadsheet.text_db as ss
import yapkke.features as features
import os
import simplejson

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

        ##Generate response
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, self.tv))

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
