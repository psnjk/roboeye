"""
Utility functions for RoboEye library
"""

import os
import subprocess


def run_command(cmd):
    """Run a shell command and return result

    Args:
        cmd (str): Command to run

    Returns:
        tuple: (status, result)
    """
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    result = process.stdout.read().decode('utf-8')
    status = process.poll()
    return status, result


def get_ip_addresses():
    """Get IP addresses for network interfaces

    Returns:
        tuple: (wlan0_ip, eth0_ip)
    """
    wlan0 = os.popen("ifconfig wlan0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip()
    eth0 = os.popen("ifconfig eth0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip()

    if wlan0 == '':
        wlan0 = None
    if eth0 == '':
        eth0 = None

    return wlan0, eth0


def check_machine_type():
    """Check machine architecture

    Returns:
        tuple: (bit_size, machine_type)
    """
    import platform
    machine_type = platform.machine()

    if machine_type == "armv7l":
        return 32, machine_type
    elif machine_type == "aarch64":
        return 64, machine_type
    else:
        return None, machine_type