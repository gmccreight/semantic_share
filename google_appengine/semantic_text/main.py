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
    text_content = db.TextProperty()
    js_content = db.TextProperty()
    version = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):

    def get(self):
        page_name = self.request.get('page_name')
        
        if page_name is None or page_name == "":
            self.redirect('/?page_name=' + base64.b16encode(os.urandom(10)))
            return

        text_content_default = """26: Jordan
56: John : The man with the plan
  78 : Stacy : She who is the one
  90 : Brower : Jonny's buddy
100 : Margie : She's the one"""

        js_content_default = """/* <![CDATA[ */
var indent_num_spaces = 2;
      
function parse_nodes (lines_ref, indent_expected) {
  var nodes = [];
  var lines = lines_ref.slice();
  while (lines.length > 0) {
    var line = lines.shift();
    var indent = line.match(/^(\s+)/);
    var indent_amount = indent ? indent[0].length : 0;
    
    if ( indent_amount % indent_num_spaces > 0 ) {
      warn("Wrong amount of indent in one of the lines.");
    }
    
    if ( indent_amount < indent_expected ) {
      return nodes;
    }
    
    if ( indent_amount > indent_expected ) {
      continue;
    }
    
    line = line.replace(/^\s+/, "");
  
    var node = new Object;
    var array = line.split(/\s?:\s?/);
    
    node.id = array[0];
    node.name = array[1];
    node.description = array.length > 2 ? array[2] : "";
    node.indent_amount = indent_amount;
    node.children = parse_nodes(lines, indent_expected + indent_num_spaces);
    nodes.push(node);
  }
  return nodes;
}

var lines = data.split(/\\n/).filter(
  function (element) {
    return ! (element.match(/^$/) || element.match(/^#/));
  }
);

var nodes = parse_nodes(lines, 0);

//Check that there are no id clashes
var node_ids = new Object;
nodes.forEach(checkNodeId);
function checkNodeId(node) {    
  if ( node_ids[node.id] == 1 ) {
    warn("Node " + node.id + " already taken" );
  }
  node_ids[node.id] = 1;
  node.children.forEach(checkNodeId);
}

data = JSON.stringify(nodes);

// Log the node data structure in a formatted way
nodes.forEach(logNode);
function logNode(node) {
    log(Array(node.indent_amount + 1 ).join("&nbsp;") + node.name
    + " <i>" + node.description + "</i>");
    node.children.forEach(logNode);
}
/* ]]> */"""

        page = Page.get_or_insert(page_name, name=page_name, text_content=text_content_default, js_content=js_content_default, version=0)
        page_text_content = cgi.escape(page.text_content)
        page_js_content = cgi.escape(page.js_content)
        page_version = cgi.escape(str(page.version))

        page_previous_version_link = ""
        if page.version > 0:
            page_previous_version_link = '<a href="/?page_name=' + page.name + '_version_%s">back one version</a>' % str(page.version - 1)


        self.response.out.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
       "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title>semantic share</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <link rel="stylesheet" href="./static/style.css" type="text/css" />
    
    <script type="text/javascript" src="/js/json2.js"></script>
    
    <script type="text/javascript" language="javascript">
      /* <![CDATA[ */
      function $ (id) {
        return document.getElementById(id);
      }
      function do_onload () {
        do_parsing();
      }
      function do_parsing () {
        clear_warning();
        clear_log();
        var data = $('ta_data').value;
        parser_js = $('ta_parser_js').value;
        eval(parser_js);
        $('ta_output').value = data;
      }
      function textarea_changed () {
        do_parsing();
      }
      function warn (warning) {
        $('warning').innerHTML = warning;
      }
      function clear_warning () {
        $('warning').innerHTML = '';
      }
      function log (message) {
        $('log').innerHTML = $('log').innerHTML + message + "<br>";
      }
      function clear_log () {
        $('log').innerHTML = '';
      }
      function focused(element) {
        // Resize the textareas to have the most size on the one you're working on
        ['ta_data', 'ta_parser_js', 'ta_output'].forEach(
          function (element_id) {
            $(element_id).style.width = '300px';
          }
        );
        element.style.width = '700px';
      }
      /* ]]> */
    </script>
    <style type="text/css">
      body { margin-left:10px; }
      textarea { width:420px; height:500px; }
      #warning { color:red; font-size:24px; }
      #log { color:green; font-size:12px; }
    </style>
  </head>

  <body onload="do_onload()">
    <form action="/update" method="post">
    <input name="page_name" type="hidden" value=\"""" + page.name + """">
    <table>
      <tr><td>
      <textarea id="ta_data" name="page_text_content" rows="20" cols="20" onkeyup="textarea_changed()" onfocus="focused(this)">""" + page.text_content + """
</textarea></td>
    
      <td><textarea id="ta_parser_js" name="page_js_content" rows="20" cols="20" onkeyup="textarea_changed()" onfocus="focused(this)">""" + page.js_content + """
      </textarea></td>
      
      <td><textarea id="ta_output" rows="20" cols="20" onkeyup="textarea_changed()" onfocus="focused(this)">
      </textarea></td>
      </tr>
    </table>
    <input type="submit" name="submit" value="save">""" + page_previous_version_link + """
    </form>
    <div id="warning"></div>
    <div id="log"></div>
  </body>
</html>""")

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
