# 📡 Packet Logger using SDN Controller

> **Course:** Computer Networks | **Tool:** Mininet + Ryu (OpenFlow 1.3)

---

## 📌 Problem Statement

Implement an SDN-based **Packet Logger** using Mininet and Ryu Controller that:

- 📥 Captures packet headers traversing the network via controller events
- 🔍 Identifies protocol types (ARP, ICMP, TCP, UDP)
- 🗂️ Maintains timestamped logs of all intercepted packets
- 📊 Displays packet information in real time on the controller terminal

---

## 🗺️ Network Topology

```
  h1 (10.0.0.1)
       |
  h2 (10.0.0.2) ───── s1 (OVS Switch) ───── Ryu Controller (127.0.0.1:6633)
       |
  h3 (10.0.0.3)
```

| Node | Role | IP Address | MAC Address |
|------|------|------------|-------------|
| h1 | Host 1 | 10.0.0.1 | 00:00:00:00:00:01 |
| h2 | Host 2 | 10.0.0.2 | 00:00:00:00:00:02 |
| h3 | Host 3 | 10.0.0.3 | 00:00:00:00:00:03 |
| s1 | OVS Switch | — | — |
| c0 | Ryu Controller | 127.0.0.1:6633 | — |

---

## ⚙️ Setup & Installation

### Prerequisites
- Ubuntu 20.04 / 22.04 / 24.04
- Python 3.9
- Mininet
- Ryu SDN Framework

### Step 1 — Install Mininet
```bash
sudo apt-get update
sudo apt-get install mininet -y
```

### Step 2 — Install Python 3.9 and create virtual environment
```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv python3.9-dev -y

python3.9 -m venv ~/ryu-env
source ~/ryu-env/bin/activate
```

### Step 3 — Install Ryu Controller
```bash
pip install setuptools==58.0.0
pip install ryu
pip install eventlet==0.30.2
```

### Step 4 — Install supporting tools
```bash
sudo apt-get install iperf wireshark -y
```

---

## ▶️ How to Run

> You need **two terminals** open simultaneously.

### Terminal 1 — Start the Ryu Controller
```bash
source ~/ryu-env/bin/activate
cd ~/sdn-packet-logger
ryu-manager --observe-links packet_logger.py
```

Wait until you see:
```
Packet Logger Controller Started. Logging to packet_log.txt
```

### Terminal 2 — Start the Mininet Topology
```bash
cd ~/sdn-packet-logger
sudo python3 topology.py
```

You will enter the `mininet>` prompt once the network is ready.

---

## 🧪 Test Scenarios

### Scenario 1 — ICMP Ping Test (Allowed traffic)
```bash
mininet> h1 ping h2 -c 4
mininet> h1 ping h3 -c 4
```
**What to observe:** ARP + ICMP packets logged, 0% packet loss.

---

### Scenario 2 — TCP Throughput Test using iperf
```bash
mininet> h2 iperf -s &
mininet> h1 iperf -c 10.0.0.2
```
**What to observe:** TCP SYN/ACK packets logged with port numbers, bandwidth displayed.

---

### Check Flow Tables (3rd terminal)
```bash
sudo ovs-ofctl dump-flows s1
```

### View Packet Log
```bash
cat ~/sdn-packet-logger/packet_log.txt
```

---

## ✅ Expected Output

### Ryu Controller Terminal
```
Switch connected: DPID 1
[ARP]  10.0.0.1 -> 10.0.0.2
[ARP]  10.0.0.2 -> 10.0.0.1
[ICMP] 10.0.0.1 -> 10.0.0.2
[ICMP] 10.0.0.1 -> 10.0.0.3
[TCP]  10.0.0.1:36244 -> 10.0.0.2:5001
[TCP]  10.0.0.2:5001  -> 10.0.0.1:36244
```

### packet_log.txt Sample
```
======================================================================
       SDN PACKET LOGGER - SESSION STARTED
       2026-04-07 15:41:45.805872
======================================================================

[2026-04-07 15:42:36.858508]
  ETH  | Src MAC: 00:00:00:00:00:01  ->  Dst MAC: 00:00:00:00:00:02
  IP   | Src IP: 10.0.0.1            ->  Dst IP: 10.0.0.2
       | Protocol: ICMP | Type: 8 | Code: 0
----------------------------------------------------------------------

[2026-04-07 15:43:26.206598]
  ETH  | Src MAC: 00:00:00:00:00:01  ->  Dst MAC: 00:00:00:00:00:02
  IP   | Src IP: 10.0.0.1            ->  Dst IP: 10.0.0.2
       | Protocol: TCP  | Src Port: 36244  ->  Dst Port: 5001
----------------------------------------------------------------------
```

### Ping Result
```
4 packets transmitted, 4 received, 0% packet loss
rtt min/avg/max/mdev = 0.074/1.705/6.038/2.507 ms
```

### iperf Result
```
[ 1] 0.0-10.0 sec   110 GBytes   94.5 Gbits/sec
```

---

## 📁 Project Structure

```
sdn-packet-logger/
├── packet_logger.py       # Ryu SDN controller — packet capture & logging
├── topology.py            # Mininet custom topology (3 hosts + 1 switch)
├── packet_log.txt         # Auto-generated log file at runtime
├── screenshots/           # Proof of execution
│   ├── ryu_controller_output.png
│   ├── ping_results.png
│   ├── iperf_results.png
│   ├── packet_log.png
│   ├── flow_table.png
│   └── topology_dump.png
└── README.md
```

---

## 📸 Proof of Execution

All screenshots are available in the [`/Screenshots`](./Screenshots/) folder, including:

| Screenshot | Description |
|------------|-------------|
| `ryu_controller_output.jpeg` | Live packet logs shown in Ryu terminal |
| `ping_results.jpeg` | Ping test — 0% packet loss across all hosts |
| `iperf_results.jpeg` | TCP throughput test — 94.5 Gbits/sec |
| `packet_log.txt` | Contents of `packet_log.txt` with timestamped entries |
| `flow_table.jpeg` | OVS flow table dump using `ovs-ofctl dump-flows s1` |
| `topology_dump.jpeg` | Mininet `net` and `dump` output |

---

## 🔄 How to Stop the Project Safely

```bash
# In Mininet terminal
mininet> exit
sudo mn -c        # clean up leftover state

# In Ryu terminal
Ctrl + C          # stop the controller
deactivate        # exit virtual environment
```

---

## 📚 References

- [Ryu SDN Framework Documentation](https://ryu.readthedocs.io)
- [Mininet Official Documentation](http://mininet.org)
- [OpenFlow 1.3 Specification](https://opennetworking.org)
- [Open vSwitch Documentation](https://www.openvswitch.org)
- [Ryu API Reference — ofproto_v1_3](https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html)
