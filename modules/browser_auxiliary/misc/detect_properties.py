from kittysploit import *

class Module(BrowserAuxiliary):

	__info__ = {
		"name": "detect properties",
		"description": "Detects a list of browser enabled properties",
		"target": (
			"all",
		),
	}	
	

	def run(self):
		js = f"""var ret = '';
			var quicktime = false;
			var unsafe = true;
			if( window.navigator.javaEnabled() )	ret += "[+] java enabled \\n";
			else 									ret += "[-] java not available \\n";
			if (navigator.mimeTypes && navigator.mimeTypes["application/x-shockwave-flash"]) ret += "[+] flash available \\n";
			else 																			 ret += "[-] flash not available \\n";
			if (navigator.plugins)
				for (i=0; i < navigator.plugins.length; i++ )
					if (navigator.plugins[i].name.indexOf("QuickTime")>=0)
						quicktime = true;
			if ((navigator.appVersion.indexOf("Mac") > 0) && (navigator.appName.substring(0,9) == "Microsoft") && (parseInt(navigator.appVersion) < 5) )
				quicktime = true;

			(quicktime) ? ret += "[+] quicktime available \\n" : ret += "[-] quicktime not available \\n";
			if ((navigator.userAgent.indexOf('MSIE') != -1) && (navigator.userAgent.indexOf('Win') != -1))	ret += "[+] vbscript available \\n";
			else																							ret += "[-] vbscript not available \\n";
			try{{ test = new ActiveXObject("WbemScripting.SWbemLocator"); }}      
			catch(ex){{unsafe = false;}} 

			(unsafe) ? ret += "[+] unsafe active x activated \\n" : ret += "[-] unsafe active x not activated \\n";

			if (navigator.plugins && navigator.plugins.length > 0) {{
				var pluginsArrayLength = navigator.plugins.length;
				ret += "\\nPLUGINS : \\n";
				ret += "--------- \\n";
				for (pluginsArrayCounter = 0 ; pluginsArrayCounter < pluginsArrayLength ; pluginsArrayCounter++ ) {{
					ret += "\\t * " + navigator.plugins[pluginsArrayCounter].name;
					if(pluginsArrayCounter < pluginsArrayLength-1)
						ret += String.fromCharCode(10);
				}}
			}}
			console.log(ret);
   			{self.get_result("ret")}"""
		self.send_js(js)
