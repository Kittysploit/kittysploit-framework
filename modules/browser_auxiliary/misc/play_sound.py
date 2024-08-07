from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "play sound",
		"description": "play sound",
		"browser": Browser.ALL,
		"platform": Platform.ALL
	}	
	
	url_audio = OptString("", "Url audio file", "yes")
	
	def run(self):
		data = f"""var sound = new Audio("{self.url_audio}");
		sound.play();
		"""
		self.send_js(data)
