#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from datetime import datetime

# Ensure the script is run as root
if os.geteuid() != 0:
    print("\n[!] CRITICAL: This script modifies system configurations and MUST be run as root (sudo).\n")
    sys.exit(1)

REPORT_DATA = {
    "timestamp": datetime.now().isoformat(),
    "scans": []
}

def log_result(check_name, status, details, fixed=False):
    """Helper function to log scan results to terminal and report data."""
    color = "\033[92m[+]" if status == "PASSED" else "\033[91m[-]"
    if fixed:
        color = "\033[93m[*]"
    
    print(f"{color}\033[0m {check_name}: {status} - {details}")
    REPORT_DATA["scans"].append({
        "check_name": check_name,
        "status": status,
        "details": details,
        "fixed": fixed
    })

def run_cmd(cmd):
    """Executes a system shell command and returns output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

# ==========================================
# 1. SSH HARDENING CHECKS
# ==========================================
def audit_ssh(auto_fix=False):
    config_path = "/etc/ssh/sshd_config"
    if not os.path.exists(config_path):
        log_result("SSH Audit", "FAILED", "SSHD config file not found. SSH might not be installed.")
        return

    with open(config_path, "r") as f:
        content = f.read()

    # Check 1: Root Login
    root_login_forbidden = "PermitRootLogin no" in content
    if root_login_forbidden:
        log_result("SSH Root Login", "PASSED", "Root login is disabled.")
    else:
        if auto_fix:
            run_cmd(r"sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config")
            run_cmd("systemctl restart sshd || systemctl restart ssh")
            log_result("SSH Root Login", "FIXED", "Disabled Root login and restarted SSH service.", fixed=True)
        else:
            log_result("SSH Root Login", "FAILED", "Root login is ENABLED! (High Risk)")

    # Check 2: Password Authentication (Enforce SSH Keys instead)
    pass_auth_disabled = "PasswordAuthentication no" in content
    if pass_auth_disabled:
        log_result("SSH Password Auth", "PASSED", "Password authentication is disabled.")
    else:
        if auto_fix:
            run_cmd(r"sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config")
            run_cmd("systemctl restart sshd || systemctl restart ssh")
            log_result("SSH Password Auth", "FIXED", "Disabled Password Auth (Enforced Keys) and restarted SSH.", fixed=True)
        else:
            log_result("SSH Password Auth", "FAILED", "Password Auth is ENABLED. (Should use Key-based pairs)")

# ==========================================
# 2. FIREWALL AUDIT
# ==========================================
def audit_firewall(auto_fix=False):
    # Check for UFW (Ubuntu/Debian)
    status_out, _ = run_cmd("ufw status")
    if "Status: active" in status_out:
        log_result("UFW Firewall", "PASSED", "Firewall is active.")
    else:
        if auto_fix:
            run_cmd("ufw --force enable")
            log_result("UFW Firewall", "FIXED", "Enabled UFW firewall automatically.", fixed=True)
        else:
            log_result("UFW Firewall", "FAILED", "Firewall is completely DISABLED!")

# ==========================================
# 3. WEAK FILE PERMISSIONS AUDIT
# ==========================================
def audit_permissions(auto_fix=False):
    # Check shadow file permissions (Should be 600 or 640 depending on distro)
    stat_out, _ = run_cmd("stat -c '%a' /etc/shadow")
    if stat_out in ["600", "640", "000"]:
        log_result("Shadow File Perms", "PASSED", f"Permissions are secure ({stat_out}).")
    else:
        if auto_fix:
            run_cmd("chmod 600 /etc/shadow")
            log_result("Shadow File Perms", "FIXED", "Hardened /etc/shadow permissions to 600.", fixed=True)
        else:
            log_result("Shadow File Perms", "FAILED", f"Permissions are loose ({stat_out})! Risk of user hash theft.")

# ==========================================
# 4. NETWORK & PORT ANALYSIS
# ==========================================
def audit_network():
    # Scanning for listening TCP ports
    ports_out, _ = run_cmd("ss -tuln | grep LISTEN")
    log_result("Network Open Ports", "INFO", f"Active listening ports detected:\n{ports_out}")

# ==========================================
# MAIN EXECUTION ENGINE
# ==========================================
if __name__ == "__main__":
    print("="*60)
    print("      SecurOps-Linux-Auditor v1.0 - Automation Tool     ")
    print("="*60)
    
    # Prompt user for Action Mode
    mode = input("Choose mode: [1] Scan Only  [2] Scan & Auto-Harden (Fix) \nEnter choice (1 or 2): ").strip()
    auto_fix = True if mode == "2" else False
    
    print("\n[*] Starting Security Baseline Audits...\n")
    
    audit_ssh(auto_fix)
    audit_firewall(auto_fix)
    audit_permissions(auto_fix)
    audit_network()
    
    # Export cleanly formatted JSON Report
    report_file = "securops_report.json"
    with open(report_file, "w") as rf:
        json.dump(REPORT_DATA, rf, indent=4)
        
    print("\n"+"="*60)
    print(f"[+] System Audit Complete. Neat JSON Log saved to: {os.path.abspath(report_file)}")
    print("="*60)
