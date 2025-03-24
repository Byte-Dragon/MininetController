# MininetController

## Project Structure
```markdown
MininetContoller/
├── README.md
├── README-CN.md            # README file in Chinese
├── run_mininet_env(CN).txt # lists of commands in Chinese for mininet controll
├── data_handler/           # Implements simple read/write operations for JSON data files
│   ├── config.json         # JSON data file
│   └── json_handler.py     # Implements simple JSON data read/write and sending to a specified IP
├── src/
│   ├── app.py              # A simple Flask application that wraps methods from controller.py into HTTP requests for frontend access
│   ├── controller.py       # Main control class, implementing a series of Mininet controls and access logic, encapsulating common methods from Mininet's net class
│   └── main_topology.py    # Topology class, creating a topology composed of Hosts, Switches, Controllers, and Links, and returning the corresponding Mininet net object
└── logs/                   # Directory for log files
    ├── app.log
    └── error.log
```

---

## Project Introduction

### Main Content
This project primarily develops a controller for the network simulation tool Mininet and the corresponding Flask service program, with logging of the Flask server's operation process.

### How dose MininetController work?
MininetController uses Mininet for network simulation and Ryu-controller for switch emulation.

### Dependencies
* RUN `sudo pip install --no-cache-dir -r requirements.txt`
* OR install dependencies manually
* Python 3.8.10
* Flask 3.0.3
  * `sudo pip install flask`
  * `sudo pip install flask-cors`
* Mininet 2.3.0.dev6
  * `sudo apt-get install mininet`
  * `sudo pip install mininet`                            # Python API


### Quick Start
* Clone repo
  * git clone https://github.com/MemorialAndUnique/MininetController.git
* cd to cloned repo
  * `cd MininetController/src`
* Run `sudo ryu-manager --verbose ryu.app.simple_switch`   # lanuch a remote ryu-controller
* Run `sudo python3 app.py`                                # run flask app, running on (127.0.0.1:8080)
  * or Run `sudo python3 app.py --cli True`                # open a mininet cli while running flask app(maybe lead to a bug)
* Use Ctrl+C to stop the server
* After simulating, Run `sudo mn -c`                       # clean up created mininet topology

---

## Basic Actions
* Start/Stop the entire network
* Start/Stop a node (Host/Switch/Controller)
* Get the topology of the running network (returns formatted JSON data)
* Adding hosts/switches
* Adding links
* Removing hosts/switches
* Removing links
* Changing node/switch/link configuration parameters
* Use ping tool
  * 'Ping/PingFull' between hosts (returns full data, optional)
  * 'Ping IP (str) on a host'
  * 'PingAll/PingAllFull' (returns full data, optional)
* Set a new controller (instance of Controller or RemoteController) for switch S

---

## Main API List

| Endpoint | Method | Parameters | Description |
| ---- | ---- | ---- | ---- |
| `/api/network/start` | POST | None | Start the entire network |
| `/api/network/stop` | POST | None | Stop the entire network,Do not run the method unless you finish your simulate |
| `/api/network/topology` | GET | None | Get the network topology |
| `/api/network/init` | POST | '{"cli": true,"data":{formatted as a config.json}}' | re-create a mininet network with config.json.<br>cli: open a mininet-CLI while cli=true|
| `/api/nodes/ping` | POST | `{ "host1": "h1", "host2": "h2", "get_full": false (optional, default false), "timeout": "10"(optional,default None) }` | Test connectivity between hosts |
| `/api/nodes/ping/ip` | POST | `{ "host": "h1",ip": "10.0.0.8" }` | Test connectivity from host to IP |
| `/api/network/ping` | POST | `{ "timeout": "10"(optional, string), "get_full": false (optional, default false),  }` | Test full network connectivity |
| `/api/nodes/add/<node_type>` | POST | for Hosts: `{ "name": string, "ip": string,"link_to":string(optional,indicates which switch to connect to when initializing the host.Connect to 's1' by default)}` for Switches: `{ "name": string }` | Add a node.<br>The switches' name must be of the form "s1" or "中国01",number "1" in"s1" will be a id for switch.<br>tips:You are suggested to run"/api/nodes/start/switch" after adding a switch
| `/api/nodes/del/<node_name>` | DELETE | None | Delete a node |
| `/api/links/add` | POST | `{ "fromNode": string, "toNode": string, "params": object }` | Create a link |
| `/api/links/del` | POST | `{ "fromNode": string, "toNode": string,"intf":string(one of the intfs connected via link) }` | Delete a link |
| `/api/config` | PUT | Configuration object | Apply network configuration |
| `/api/nodes/start/<node_type>` | POST | `{ "name": string }` | Start a specific node |
| `/api/nodes/stop/<node_type>` | POST | `{ "name": string, "keep_config": boolean }` (keep_config is optional) | Stop a specific node |

### API TEST by Curl
```bash
* curl -X POST http://127.0.0.1:8080/api/network/start
* curl -X POST http://127.0.0.1:8080/api/network/stop
* curl -X GET http://127.0.0.1:8080/api/network/topology
* curl -X POST http://localhost:8080/api/network/init -H "Content-Type: application/json" -d '{
    "cli": false,
    "data":{
        "links": [
            {"from": "s1", "to": "h1"},
            {"from": "s2", "to": "h2"},
            {"from": "s2", "to": "h3"},
            {"from": "s1", "to": "s2"}
        ],
        "hosts": [
            {"name": "h1", "ip": "192.168.1.2/16"},
            {"name": "h2", "ip": "192.168.1.3"},
            {"name": "h3", "ip": "192.168.1.4"}
        ],
        "switches": [
            {"name": "s1"},
            {"name": "s2"}
        ]
    }}'    
    
* curl -X POST -H "Content-Type: application/json" -d '{"host1":"h2","host2":"h3","get_full":true}' http://localhost:8080/api/nodes/ping
* curl -X POST -H "Content-Type: application/json" -d '{"host":"h1", "ip":"119.75.217.109"}' http://localhost:8080/api/nodes/ping/ip
* curl -X POST -H "Content-Type: application/json" -d '{"get_full":false,"timeout":"10"}' http://localhost:8080/api/network/ping

* curl -X POST -H "Content-Type: application/json" -d '{"name":"祖国01"}' http://localhost:8080/api/nodes/add/switch
* curl -X POST -H "Content-Type: application/json" -d '{"name":"中国", "ip":"10.0.0.9"}' http://localhost:8080/api/nodes/add/host
* curl -X POST -H "Content-Type: application/json" -d '{"name":"h9", "ip":"10.0.0.9","link_to":"祖国01"}' http://localhost:8080/api/nodes/add/host
* curl -X DELETE http://localhost:8080/api/nodes/del/h9

* curl -X POST -H "Content-Type: application/json" -d '{"name":"s1"}' http://localhost:8080/api/nodes/start/switch
* curl -X POST -H "Content-Type: application/json" -d '{"name":"h2"}' http://localhost:8080/api/nodes/start/host
* curl -X POST -H "Content-Type: application/json" -d '{"name":"s1","keep_config":true}' http://localhost:8080/api/nodes/stop/switch
* curl -X POST -H "Content-Type: application/json" -d '{"name":"h2","keep_config":true}' http://localhost:8080/api/nodes/stop/host

* curl -X POST -H "Content-Type: application/json" -d '{"fromNode":"h2", "toNode":"s2","params":{"delay":5,"bw": 10}}' http://localhost:8080/api/links/add
* curl -X POST -H "Content-Type: application/json" -d '{"fromNode":"h1", "toNode":"s2"}' http://localhost:8080/api/links/del

* curl -X PUT -H "Content-Type: application/json" -d '{"hosts": [
    {
      "name": "h1",
      "params": {
        "ip": "192.168.1.4/24"
      }
    }
  ]}' http://localhost:8080/api/config
  
  
* curl -X PUT -H "Content-Type: application/json" -d '{"links": [{"from": "h-1","to": "s1","params": {"delay":5,"bandwidth": 10}}]}' http://localhost:8080/api/config


```

### Supplementary Notes
* If you are experiencing the “400 Bad Request” problem, please make sure that your request method(POST or PUT) and parameters(true/false, not True/False or "True"/"False") are correct.

* Data format required when accessing `/api/config`:
```json
{
  "links": [
    {
      "from": "s1",
      "to": "s2",
      "params": {
        "bandwidth": 10,
        "delay": 5
      }
    }
  ],
  "hosts": [
    {
      "name": "h1",
      "params": {
        "ip": "192.168.1.2",
        "Mask": "255.255.255.0",
        "MAC": "00:00:00:AA:BB:CC",
        "intfName": "h1-eth0",
        "status": "up"
      }
    }
  ],
  "switches": [
    {
      "name": "s1",
      "params": {
        "ip": "",
        "Mask": "255.255.255.0",
        "MAC": "00:00:00:AA:BB:CC",
        "intfName": "s1-eth0",
        "status": "up"
      }
      
    }
  ]
}
```

---

## Notes of Log
Log files are stored in the `logs/` directory, with the following details:
- `app.log`: Current application log.
- `app.log.2023-07-19`: Historical log (named by date).
- `error.log`: Current error log.
- `error.log.1`: Backup of historical error logs.

---

