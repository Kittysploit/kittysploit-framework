from kittysploit.core.utils.function_module import pythonize_path, import_module
from kittysploit.core.base.jobs import Jobs
from kittysploit.core.base.storage import LocalStorage
from kittysploit.core.database.schema import *
from kittysploit.core.framework.remotescanlauncher.port_list import PORT, PORT_SSL
from kittysploit.core.framework.remotescanlauncher.portscan import Scanner
from kittysploit.core.utils.locked_iterator import LockedIterator
import threading
import time
from itertools import chain
import requests


class RemoteScan:

    def __init__(self, target, threads_number, workspace):
        """
        :param target: target to scan
        :param threads_number: number of threads
        :param workspace: workspace
        """
        self.target = target
        self.compteur = 0
        self.total = 0
        self.all_modules = []
        self.jobs = Jobs()
        self.job_id = None
        self.local_storage = LocalStorage()
        self.scan_id = None
        self.threads_number = threads_number
        self.port = []
        self.cache = None
        self.protocols = []
        self.port_temporaire = {}
        self.port_scanned = []
        self.workspace = workspace
        self.protocols_ssl = []

    def scan_target(self) -> list:
        """
        Scan target
        :return: list of open ports
        """
        
        if self.target.startswith("http"):
            self.target = self.target.split("//")[1]
        elif self.target.startswith("https"):
            self.target = self.target.split("//")[1]
        scan = Scanner(target=self.target, port="20-10000", workspace=self.workspace)
        self.port_scanned = scan.scan()
        for port in self.port_scanned:
            check = (
                db.query(Workspace_data)
                .filter(
                    Workspace_data.name == self.workspace,
                    Workspace_data.target == False,
                    Workspace_data.ip == self.target,
                    Workspace_data.port == port,
                )
                .first()
            )
            if not check:
                add_info = Workspace_data(
                    name=self.workspace, target=False, ip=self.target, port=port
                )
                db.add(add_info)
                db.commit()

        #        my_target_port = db.query(Workspace_data.port).filter(Workspace_data.name==self.workspace, Workspace_data.ip==self.target, Workspace_data.target==False).all()
        for port in self.port_scanned:
            try:
                if int(port) in PORT:    
                    proto = PORT[int(port)]
                    self.protocols.append(proto)
                    if proto == "http" or proto == "https":
                        self.cache = requests.get(url=f"{proto}://{self.target}")
                    self.port_temporaire[port] = proto
                else:
                    self.port_temporaire[port] = port
            except:
                continue
        print(self.port_temporaire)
        
        return self.port_scanned

    def personnalize(self) -> None:
        """
        Personnalize the scan
        """
        for port in self.port_temporaire:
            proto = self.port_temporaire[port]
            self.protocols.append(proto)

    
    def get_all_modules(self):
        # Créer une liste de tuples (protocole, port)
        unique_protocols = []
        for port in self.port_scanned:
            if port in PORT:
                unique_protocols.append((PORT[port], port))  # Inclure le port

        # Un dictionnaire pour associer les protocoles à leurs ports
        protocol_to_ports = {}
        for protocol, port in unique_protocols:
            if protocol in PORT_SSL:
                ssl_protocol = PORT_SSL[protocol]
                ssl_ports = [p for p, pt in PORT.items() if pt == ssl_protocol]
                if ssl_ports:
                    protocol_to_ports.setdefault(ssl_protocol, set()).add(ssl_ports[0])
                protocol_to_ports.setdefault(protocol, set()).add(port)
            else:
                protocol_to_ports.setdefault(protocol, set()).add(port)

        # Liste pour contenir tous les résultats avec ports
        result_with_ports = []

        # Obtenir les modules pour chaque protocole avec tous les ports associés
        for protocol, ports in protocol_to_ports.items():
            # Ajouter les équivalents SSL si disponibles
            equivalent_protocols = [protocol]
            if protocol in PORT_SSL:
                equivalent_protocols.append(PORT_SSL[protocol])
            
            # Requêter tous les modules pour les protocoles équivalents
            modules_query = (db.query(Modules.path, Modules.protocol)
                            .filter(Modules.type_module == "remotescan")
                            .filter(Modules.protocol.in_(equivalent_protocols))
                            .all())
            
            for item in modules_query:
                for port in ports:
                    result_with_ports.append((item[0], item[1], port))
        
        self.all_modules = result_with_ports

        return len(self.all_modules)



    def run_threads(self, threads_number, target_function, *args, **kwargs):
        """
        Run threads
        :param threads_number: number of threads
        :param target_function: target function
        :param args: arguments
        :param kwargs: keyword arguments
        """
        threads = []
        threads_running = threading.Event()
        threads_running.set()

        for thread_id in range(int(threads_number)):
            thread = threading.Thread(
                target=target_function,
                args=chain((threads_running,), args),
                kwargs=kwargs,
                name="thread-{}".format(thread_id),
            )
            threads.append(thread)
            thread.start()

        try:
            while thread.is_alive():
                thread.join(1)

        except KeyboardInterrupt:
            threads_running.clear()

        for thread in threads:
            thread.join()
        self.local_storage.delete_element("jobs", self.job_id)
        end = time.time()
        update_status = (
            db.query(Remotescan).filter(Remotescan.id == self.scan_id).first()
        )
        update_status.status = "Finish"
        db.commit()

    def load_module(self, running, data):
        while running.is_set():
            new_module = data.__next__()
            print(new_module)
            if new_module is None:
                break
            else:
                #                print(new_module)
                #                proto_of_module = new_module.split("@@")[0]
                #                module = new_module.split("@@")[1]
                #                for i in self.port_temporaire.keys():
                #                    if self.port_temporaire[i] == proto_of_module:
                #                        port = i
                #               
                # break
                module_path, protocol, port = new_module
                
                module_path = pythonize_path(module_path)
                module_path = ".".join(("modules", module_path))
                current_module_scan = import_module(module_path)(self.target, port, self.cache)
                try:
                    r = current_module_scan.run()
                    if r:
                        info_return = ""
                        if isinstance(r, str):
                            info_return = r
                        info = current_module_scan.__info__
                        module_cvss3 = ""
                        module_name = ""
                        module_cve = ""
                        module_module = ""
                        if "cvss3" in info:
                            module_cvss3 = info["cvss3"]
                        if "name" in info:
                            module_name = info["name"]
                        if "cve" in info:
                            module_cve = info["cve"]
                        if "module" in info:
                            module_module = info["module"]
                        if "protocol" in info:
                            module_protocol = info["protocol"]
                        add_info = Remotescan_data(
                            remotescan_id=self.scan_id,
                            target=self.target,
                            port=port,
                            cvss3=module_cvss3,
                            name=module_name,
                            cve=module_cve,
                            modules=module_module,
                            protocol=protocol,
                            info=info_return,
                        )
                        db.add(add_info)
                        db.flush()
                except:
                    continue
            self.compteur += 1
            db.commit()

    def run(self):
        add_scan = Remotescan(
            workspace=self.workspace, target=self.target, status="In working..."
        )
        db.add(add_scan)
        db.commit()
        self.scan_id = add_scan.id
        self.job_id = self.jobs.create_job("Remote scan", self.target, self.attack)

    def attack(self):
        data = LockedIterator(self.all_modules)
        self.run_threads(self.threads_number, self.load_module, data)
