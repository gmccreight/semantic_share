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
    calculated_json_content = db.TextProperty()
    version = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class ChooseHandler(webapp.RequestHandler):

    def get(self):
        self.response.out.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
       "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title>semantic text</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    
    <style type="text/css">
    </style>
  </head>

  <body>
    <h3>Choose a default template for your new page</h3>
    <div><a href="/?template=tree">tree</a></div>
    <div><a href="/?template=hours">hours</a></div>
    <div>more to come...</div>
  </body>
</html>""")

class MainHandler(webapp.RequestHandler):

    def get(self):
        page_name = self.request.get('page_name')
        template = self.request.get('template')

        if page_name is None or page_name == "":
            if template is None or template == "":
                self.redirect('/choose')
                return
            else:
                self.redirect('/?template=' + template + '&page_name=' + base64.b16encode(os.urandom(10)))
                return

        text_content_default = ""
        if template == "tree":
            text_content_default = """26: Jordan
56: John : The man with the plan
  78 : Stacy : She who is the one
  90 : Brower : Jonny's buddy
100 : Margie : She's the one"""
        elif template == "hours":
            text_content_default = """-550
worked on something worth mentioning
and then did something else
115-
tue

-550
worked on something worth mentioning
and then did something else
115-
mon

-445
this is a test
and another line
330-
wed

-345
330-

-315
230-
tue

-120
115-
mon"""

        js_content_default = ""
        if template == "tree":
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

// Output the node data structure in a formatted way
nodes.forEach(outputNode);
function outputNode(node) {
    append_to_output(Array(node.indent_amount + 1 ).join("&nbsp;") + node.name
    + " <i>" + node.description + "</i>");
    node.children.forEach(outputNode);
}
/* ]]> */"""
        elif template == "hours":
            js_content_default = """/* <![CDATA[ */

var lines = data.split(/\\n/).filter(
  function (element) {
    return ! (element.match(/^#/));
  }
);

lines = lines.reverse();

var days_of_week = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
var day_num_for_name = {};
for ( var x = 0; x < days_of_week.length; x++ ) {
  day_num_for_name[days_of_week[x]] = x + 1;
}

var days = [];
var day = {};
day.time_chunks = [];

var capture_text_into_time_chunk = false;

for (var i = 0; i < lines.length; i++) {
  line = lines[i];

  var matched_day = "";
  if ( matched_day = line.match(RegExp("^(" + days_of_week.join('|') + ")$")) ) {
    if ( day.time_chunks.length > 0 ) {
      days.push(day);
    }
    day = {};
    day.time_chunks = [];
    day.name = matched_day[1];
  }
  else if ( matched_time = line.match(/^(-*)([0-9]{1,2})([0-9]{2})(-*)$/) ) {

    var end_indicator = matched_time[1];
    var matched_hour = matched_time[2];
    var matched_minute = matched_time[3];
    var start_indicator = matched_time[4];

    if ( start_indicator == '-' ) {
      var time_chunk = { "text_lines":[]};
      time_chunk.start_hour = parseInt(matched_hour);
      time_chunk.start_minute = parseInt(matched_minute);
      day.time_chunks.push(time_chunk);
      capture_text_into_time_chunk = true;
    }
    else if ( end_indicator == '-' ) {
      if ( day.time_chunks.length > 0 ) {
        day.time_chunks[day.time_chunks.length - 1].end_hour = parseInt(matched_hour);
        day.time_chunks[day.time_chunks.length - 1].end_minute = parseInt(matched_minute);
      }
      capture_text_into_time_chunk = false;
    }
  }
  else {
    if ( capture_text_into_time_chunk == true ) {
      day.time_chunks[day.time_chunks.length - 1].text_lines.push(line);
    }
  }

  if (i == lines.length - 1) {
    if ( day.time_chunks.length > 0 ) {
      days.push(day);
    }
  }
}

data = JSON.stringify(days);

function minutes_to_hours(minutes) {
  var hours = parseInt(minutes / 60);
  var minutes = (minutes % 60) + "";
  if (minutes.length < 2) {
    minutes = "0" + minutes;
  }
  return hours + ":" + minutes;
}

var week_total = 0;
var last_day_num = 0;
var formatted_days = [];

for (var x = 0; x < days.length; x++) {
  var day = days[x];
  var formatted_day = "";
  var is_new_week = false;

  var day_num = day_num_for_name[day.name];
  if (last_day_num > day_num) {
    week_total = 0;
    is_new_week = true;
  }
  last_day_num = day_num;
  var time_chunks = day.time_chunks.reverse();

  var day_total_hours = 0;
  for (var y = 0; y < time_chunks.length; y++) {
    var start_minutes = time_chunks[y].start_hour * 60 + time_chunks[y].start_minute;
    if ( time_chunks[y].end_hour ) {
      var end_minutes = time_chunks[y].end_hour * 60 + time_chunks[y].end_minute;
      day_total_hours += end_minutes - start_minutes;
    }
  }

  week_total += day_total_hours;

  var bg_color = is_new_week ? "#ccc" : "#ddd";

  formatted_day += '<div style="background-color:' + bg_color + ';margin-top:10px;">' + day.name + ": day hours = " + minutes_to_hours(day_total_hours) + " week hours = " + minutes_to_hours(week_total) +"</div>";
  
  for (var y = 0; y < time_chunks.length; y++) {
    var tc = time_chunks[y];
    var end_time = "";
    if ( tc.end_hour) {
      end_time = " - " + tc.end_hour + ":" + tc.end_minute;
    }
    else {
      end_time = ' - <span style="color:green;">current</span>';
    }
    formatted_day += tc.start_hour + ":" + tc.start_minute + end_time;
    formatted_day += '<div style="margin-left:10px;">' + time_chunks[y].text_lines.reverse().join('<br>').replace(/\\n/, "<br>") + '</div>';
  }

  formatted_days.push(formatted_day);
}

append_to_output(formatted_days.reverse().join(""));

/* ]]> */"""

        page = Page.get_or_insert(page_name, name=page_name, text_content=text_content_default, js_content=js_content_default, version=0)
        page_text_content = cgi.escape(page.text_content)
        page_js_content = cgi.escape(page.js_content)
        page_version = cgi.escape(str(page.version))


        page_edit_css = "form { display:none }\n"
        page_edit_link = "<a class=\"edit_link\" href=\"/?page_name=" + page.name + "&edit=1\">edit</a><br>"
        if self.request.get('edit'):
            page_edit_css = ""
            page_edit_link = ""

        page_previous_version_link = ""
        if page.version > 0:
            page_previous_version_link = ' <a href="/?page_name=' + page.name + '_version_%s">back one version</a>' % str(page.version - 1)

        if template == "hours" or template == "tree":
            self.redirect('/?page_name=' + page.name)
            return

        self.response.out.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
       "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <title>semantic text</title>
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
        clear_formatted_output();
        var data = $('ta_data').value;
        parser_js = $('ta_parser_js').value;
        eval(parser_js);
        $('ta_calculated_json').value = data;
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
      function append_to_output (message) {
        $('formatted_output').innerHTML = $('formatted_output').innerHTML + message + "<br>";
      }
      function clear_formatted_output () {
        $('formatted_output').innerHTML = '';
      }
      function focused(element) {
        // Resize the textareas to have the most size on the one you're working on
        ['ta_data', 'ta_parser_js', 'ta_calculated_json'].forEach(
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
      a.edit_link { font-size:12px; }
      #warning { color:red; font-size:24px; }
      #formatted_output { color:black; font-size:12px; }
      """ + page_edit_css + """
    </style>
  </head>

  <body onload="do_onload()">
    <form action="/update" method="post">
        <input name="page_name" type="hidden" value=\"""" + page.name + """" />
        <table>
          <tr><td>
          <textarea id="ta_data" name="page_text_content" rows="20" cols="20" onkeyup="textarea_changed()" onfocus="focused(this)">""" + page.text_content + """</textarea></td>
        
          <td><textarea id="ta_parser_js" name="page_js_content" rows="20" cols="20" onkeyup="textarea_changed()" onfocus="focused(this)">""" + page.js_content + """</textarea></td>
          
          <td><textarea id="ta_calculated_json" name="page_calculated_json_content" rows="20" cols="20" onkeyup="textarea_changed()" onfocus="focused(this)"></textarea></td>
          </tr>
        </table>
        <input type="submit" name="submit" value="save" />""" + page_previous_version_link + """
    </form>
    """ + page_edit_link + """
    <div id="warning"></div>
    <div id="formatted_output"></div>
  </body>
</html>""")

class PageHandler(webapp.RequestHandler):

    def post(self):
        page = Page.get_or_insert(self.request.get('page_name'))
        page.text_content = self.request.get('page_text_content')
        page.js_content = self.request.get('page_js_content')
        page.calculated_json_content = self.request.get('page_calculated_json_content')
        
        version = page.version
        if version is None:
            version = 0
        page.version=version + 1

        page.put()

        # Save an older version of the page
        version_page = Page(key_name=page.name + '_version_' + str(version), name=page.name, text_content=page.text_content, js_content=page.js_content, calculated_json_content=page.calculated_json_content, version=page.version - 1)
        version_page.put()

        self.redirect('/?page_name=' + page.name)

def main():
    application = webapp.WSGIApplication(
                                     [('/', MainHandler),
                                      ('/choose', ChooseHandler),
                                      ('/update', PageHandler)],
                                     debug=True)

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
