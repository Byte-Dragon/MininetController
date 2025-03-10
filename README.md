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
* or install dependencies manually
* Python 3.8.10
* Flask 3.0.3
  * `sudo pip install flask`
  * `sudo pip install flask-cors`
* Mininet 2.3.0.dev6
  * `sudo apt-get install mininet`
  * `sudo pip install mininet`                            # Python API


### Quick Start
* Clone repo
  * git clone https://github.com/Sirozha1337/NetworkSimulator.git
* cd to cloned repo
  * `cd MininetController/src`
* Run `sudo ryu-manager --verbose ryu.app.simple_switch`   # lanuch a remote ryu-controller
* Run `sudo python3 app.py`                                # run flask app, running on (127.0.0.1:8080)
  * or Run `sudo python3 app.py --cli True`                # open a mininet cli while running flask app
* Use Ctrl+C to stop the server
* Run `sudo mn -c`                                         # clean up created mininet topology

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
| `/api/nodes/ping` | POST | `{ "host1": string, "host2": string, "get_full": False (optional, default False), "timeout": string (optional, '10ms') }` | Test connectivity between hosts |
| `/api/nodes/ping/ip` | POST | `{ "host": str, "ip": str }` | Test connectivity from host to IP |
| `/api/network/ping` | POST | `{ "timeout": int, "get_full": False (optional, default False), "timeout": string (optional, '10ms') }` | Test full network connectivity |
| `/api/nodes/<node_type>` | POST | Host: `{ "name": string, "ip": string }`<br>Switch: `{ "name": string }` | Add a node |
| `/api/nodes/del/<node_name>` | DELETE | None | Delete a node |
| `/api/links` | POST | `{ "fromNode": string, "toNode": string, "params": object }` | Create a link |
| `/api/links` | DELETE | `{ "fromNode": string, "toNode": string }` | Delete a link |
| `/api/config` | PUT | Configuration object | Apply network configuration |
| `/api/nodes/<name>/start` | POST | `{ "controller": string }` (optional) | Start a specific node |
| `/api/nodes/<name>/stop` | POST | `{ "keep_config": boolean }` (optional) | Stop a specific node |

### Supplementary Notes
Data format required when accessing `/api/config`:
```json
{
  "links": [
    {
      "from": "s1",
      "to": "s2",
      "params": {
        "bandwidth": 10,
        "delay": "5ms"
      }
    }
  ],
  "hosts": [
    {
      "name": "h1",
      "params": {
        "IP": "192.168.1.2",
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
        "IP": "192.168.1.2",
        "Mask": "255.255.255.0",
        "MAC": "00:00:00:AA:BB:CC",
        "intfName": "s1-eth0",
        "status": "up"
      }
    }
  ]
}
```
### API TEST
```bash
* curl -X POST http://127.0.0.1:8080/api/network/start
* curl -X POST http://127.0.0.1:8080/api/network/stop
* curl -X GET http://127.0.0.1:8080/api/network/topology
* curl -X POST -H "Content-Type: application/json" -d '{"host1":"h1", "host2":"h8"}' http://localhost:8080/api/nodes/ping
```
---

## Notes of Log
Log files are stored in the `logs/` directory, with the following details:
- `app.log`: Current application log.
- `app.log.2023-07-19`: Historical log (named by date).
- `error.log`: Current error log.
- `error.log.1`: Backup of historical error logs.

---

