#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# To deploy:
# Deploy by being in ../ and typing
# ./appcfg.py update semantic_text

import cgi
import os
import base64

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

class Page(db.Model):
    name = db.StringProperty(multiline=False)
    text_content = db.StringProperty(multiline=True)
    js_content = db.StringProperty(multiline=True)
    version = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):

    def get(self):
        page_name = self.request.get('page_name')
        
        if page_name is None or page_name == "":
            self.redirect('/?page_name=' + base64.b16encode(os.urandom(10)))
            return

        page = Page.get_or_insert(page_name, name=page_name, text_content="fill in", js_content="fill in", version=0)
        page_text_content = cgi.escape(page.text_content)
        page_js_content = cgi.escape(page.js_content)
        page_version = cgi.escape(str(page.version))

        self.response.out.write('<form action="/update" method="post">')
        self.response.out.write('<input name="page_name" type="hidden" value="%s">' % page_name)
        self.response.out.write('<textarea name="page_text_content">%s</textarea>' % page_text_content)
        self.response.out.write('<textarea name="page_js_content">%s</textarea>' % page_js_content)
        self.response.out.write('<input type="submit" name="submit" value="save">')
        self.response.out.write('</form>')

        if page.version > 0:
            self.response.out.write('<br><a href="/?page_name=' + page.name + '_version_%s">back one version</a>' % str(page.version - 1))

class PageHandler(webapp.RequestHandler):

    def post(self):
        page = Page.get_or_insert(self.request.get('page_name'))
        page.text_content = self.request.get('page_text_content')
        page.js_content = self.request.get('page_js_content')
        
        version = page.version
        if version is None:
            version = 0
        page.version=version + 1

        page.put()

        # Save an older version of the page
        version_page = Page(key_name=page.name + '_version_' + str(version), name=page.name, text_content=page.text_content, js_content=page.js_content, version=page.version - 1)
        version_page.put()

        self.redirect('/?page_name=' + page.name)

def main():
    application = webapp.WSGIApplication(
                                     [('/', MainHandler),
                                      ('/update', PageHandler)],
                                     debug=True)

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
