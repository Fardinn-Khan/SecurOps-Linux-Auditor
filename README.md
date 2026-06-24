# SecurOps-Linux-Auditor v1.0 🛡️

An automated security auditing and configuration hardening tool designed for Linux server environments. Built entirely in Python, this utility scans systems against baseline security benchmarks, generates structured compliance reports, and provides an optional, safe mechanism to remediate discovered vulnerabilities dynamically.

---

## 🚀 Project Overview

Manually auditing system configurations across multiple Linux servers is error-prone and time-consuming. `SecurOps-Linux-Auditor` bridges this gap by acting as an automated Security Posture Management engine. It focuses on four critical infrastructure pillars: Secure Shell (SSH) access control, Firewall operational posture, Core System file access rights, and Active Network footprinting.

### Key Capabilities
* **Dual Execution Modes:** Support for risk-free **Scan Only** diagnostics as well as real-time **Scan & Auto-Harden** remediation.
* **Non-Disruptive Auditing:** Parses configuration schemas natively before applying surgical alterations via standard system hooks.
* **Deterministic Reporting:** Outputs uniform, timestamped telemetry data structured in JSON for effortless parsing by SIEMs or log collectors.

---

## 🛠️ Architecture & Core Security Modules



The auditor evaluates security vulnerabilities across specific vectors using standard Linux system tools abstracted through Python's automation layers:

### 1. SSH Server Hardening
* **Vulnerability Checked:** Remote administrative entry points and credential weak-spots.
* **Logic Execution:** Reads and analyzes `/etc/ssh/sshd_config`.
  * **`PermitRootLogin` Evaluation:** Ensures root cannot be targeted directly via SSH brute-force campaigns. 
  * **`PasswordAuthentication` Evaluation:** Confirms password-less, cryptographic SSH public/private key-pair authentication is mandated.
* **Remediation Action:** Modifies variables programmatically using automated `sed` editing and securely reloads the runtime daemon state via `systemctl`.

### 2. Host-Based Firewall Verification
* **Vulnerability Checked:** Unfiltered ingress network vectors.
* **Logic Execution:** Interrogates the Uncomplicated Firewall (`ufw`) API state.
* **Remediation Action:** Activates and commits firewall policy tables synchronously if found down.

### 3. Critical File Permissions Audit
* **Vulnerability Checked:** Local Privilege Escalation vectors and password hash leakage.
* **Logic Execution:** Collects octal file permissions data from `/etc/shadow` via standard system abstraction.
* **Remediation Action:** Forces strict Unix access controls (`600` permissions), isolating write/read permissions exclusively to the absolute root administrator account.

### 4. Network Exposure Footprinting
* **Vulnerability Checked:** Active listening network sockets and unauthorized applications.
* **Logic Execution:** Discovers sockets bound to local interfaces using low-level socket diagnostic tools (`ss -tuln`). 

---

## 📦 Laboratory Setup & Deployment

This project was built and validated inside a virtualized hypervisor sandbox environment (**VMware Workstation/ESXi**) running an enterprise Linux distribution (Ubuntu/Debian-derived target).

### Prerequisites
* Linux OS (Ubuntu 20.04 LTS or newer recommended)
* Python 3.8+ installed natively
* Root or administrative `sudo` access privileges

### Installation & Execution

1. **Clone the project repository to your target machine:**
   ```bash
   git clone [https://github.com/Fardinn-Khan/SecurOps-Linux-Auditor.git]
   cd SecurOps-Linux-Auditor
   
2. **Make the script executable & Run the script using Python 3
   ```bash
   chmod +x auditscript.py
   python3 auditscript.py
