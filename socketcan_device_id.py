#!/usr/bin/env python3
"""
SocketCAN Device ID Tool
A Python tool for managing SocketCAN interface identification on Linux

Features:
- List all SocketCAN interfaces
- Get interface information (alias, bitrate, status)
- Set interface alias
- Generate udev rules for persistent naming

Requirements:
- Linux with SocketCAN support

Author: Kimi Claw
Date: 2025
"""

import os
import sys
import subprocess
import argparse
from typing import List, Optional, Dict, Tuple


def run_cmd(cmd: str) -> Tuple[int, str, str]:
    """Run shell command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def list_interfaces() -> List[Dict]:
    """List all SocketCAN interfaces with details"""
    interfaces = []
    
    ret, stdout, _ = run_cmd("ip -details link show type can 2>/dev/null")
    if ret != 0:
        return interfaces
    
    current = {}
    for line in stdout.split('\n'):
        line = line.strip()
        
        if not line:
            continue
            
        # New interface
        if line[0].isdigit() and ': can' in line:
            if current:
                interfaces.append(current)
            parts = line.split(':')
            current = {'name': parts[1].strip().split()[0]}
        
        # State
        if 'state UP' in line:
            current['state'] = 'UP'
        elif 'state DOWN' in line:
            current['state'] = 'DOWN'
        
        # Bitrate
        if 'bitrate' in line.lower():
            parts = line.split()
            for i, p in enumerate(parts):
                if 'bitrate' in p.lower() and i + 1 < len(parts):
                    current['bitrate'] = parts[i + 1]
        
        # Alias
        if 'alias' in line.lower():
            parts = line.split('alias')
            if len(parts) > 1:
                current['alias'] = parts[1].strip().strip('"')
    
    if current:
        interfaces.append(current)
    
    return interfaces


def get_info(interface: str) -> Dict:
    """Get detailed information for a SocketCAN interface"""
    info = {'name': interface}
    
    ret, stdout, _ = run_cmd(f"ip -details link show {interface}")
    if ret == 0:
        if 'state UP' in stdout:
            info['state'] = 'UP'
        elif 'state DOWN' in stdout:
            info['state'] = 'DOWN'
        else:
            info['state'] = 'UNKNOWN'
        
        for line in stdout.split('\n'):
            if 'alias' in line.lower():
                parts = line.split('alias')
                if len(parts) > 1:
                    info['alias'] = parts[1].strip().strip('"')
            if 'bitrate' in line.lower():
                parts = line.split()
                for i, p in enumerate(parts):
                    if 'bitrate' in p.lower() and i + 1 < len(parts):
                        info['bitrate'] = parts[i + 1]
    
    # USB device info
    sys_path = f"/sys/class/net/{interface}/device"
    if os.path.exists(sys_path):
        info['sys_path'] = os.path.realpath(sys_path)
        for attr in ['idVendor', 'idProduct', 'serial']:
            attr_path = os.path.join(info['sys_path'], attr)
            if os.path.exists(attr_path):
                try:
                    with open(attr_path, 'r') as f:
                        info[attr] = f.read().strip()
                except:
                    pass
    
    return info


def set_alias(interface: str, alias: str) -> bool:
    """Set alias for SocketCAN interface"""
    ret, _, stderr = run_cmd(f"ip link set {interface} alias '{alias}'")
    if ret == 0:
        print(f"✓ Set {interface} alias to '{alias}'")
        return True
    else:
        print(f"✗ Failed: {stderr}")
        print("Note: Requires root privileges")
        return False


def generate_udev_rule(interface: str, new_name: str = None) -> str:
    """Generate udev rule for persistent naming"""
    info = get_info(interface)
    
    if 'idVendor' not in info or 'idProduct' not in info:
        print(f"Cannot generate rule: USB info not available for {interface}")
        return ""
    
    vendor = info.get('idVendor', 'XXXX')
    product = info.get('idProduct', 'XXXX')
    serial = info.get('serial', '*')
    name = new_name or interface
    
    rule = f'''# SocketCAN rule for {interface}
SUBSYSTEM=="net", ACTION=="add", \\
    ATTR{{idVendor}}=="{vendor}", \\
    ATTR{{idProduct}}=="{product}", \\
    ATTR{{serial}}=="{serial}", \\
    NAME="{name}"
'''
    return rule


def show_udev_info(interface: str):
    """Show udev information"""
    info = get_info(interface)
    
    print(f"\n=== {interface} udev Info ===\n")
    
    if 'sys_path' in info:
        print(f"Path: {info['sys_path']}")
    
    print("\nUSB Attributes:")
    for attr in ['idVendor', 'idProduct', 'serial', 'manufacturer', 'product']:
        if attr in info:
            print(f"  {attr}: {info[attr]}")
    
    if 'idVendor' in info:
        print("\n--- Suggested udev Rule ---")
        print(generate_udev_rule(interface))


def interactive_mode():
    """Interactive mode"""
    print("\n=== SocketCAN Device ID Tool ===\n")
    
    while True:
        print("Options:")
        print("  1. List all CAN interfaces")
        print("  2. Get interface info")
        print("  3. Set interface alias")
        print("  4. Show udev info")
        print("  5. Generate udev rule")
        print("  6. Exit")
        print()
        
        choice = input("Select (1-6): ").strip()
        
        if choice == "1":
            interfaces = list_interfaces()
            if interfaces:
                print(f"\nFound {len(interfaces)} interface(s):")
                print("-" * 60)
                print(f"{'Name':<12} {'State':<8} {'Bitrate':<12} {'Alias':<20}")
                print("-" * 60)
                for iface in interfaces:
                    name = iface.get('name', 'N/A')
                    state = iface.get('state', 'N/A')
                    bitrate = iface.get('bitrate', 'N/A')
                    alias = iface.get('alias', '')
                    print(f"{name:<12} {state:<8} {bitrate:<12} {alias:<20}")
                print("-" * 60)
            else:
                print("No SocketCAN interfaces found")
            print()
            
        elif choice == "2":
            iface = input("Enter interface name (e.g., can0): ").strip()
            if iface:
                info = get_info(iface)
                print(f"\nInterface: {info['name']}")
                print(f"State: {info.get('state', 'N/A')}")
                print(f"Bitrate: {info.get('bitrate', 'N/A')}")
                print(f"Alias: {info.get('alias', 'None')}")
                if 'idVendor' in info:
                    print(f"USB Vendor: {info['idVendor']}")
                    print(f"USB Product: {info['idProduct']}")
                    print(f"USB Serial: {info.get('serial', 'N/A')}")
                print()
            
        elif choice == "3":
            iface = input("Enter interface name: ").strip()
            if iface:
                alias = input("Enter alias: ").strip()
                if alias:
                    set_alias(iface, alias)
            print()
            
        elif choice == "4":
            iface = input("Enter interface name: ").strip()
            if iface:
                show_udev_info(iface)
            print()
            
        elif choice == "5":
            iface = input("Enter interface name: ").strip()
            if iface:
                new_name = input("Enter new interface name (press Enter to keep current): ").strip()
                rule = generate_udev_rule(iface, new_name if new_name else None)
                if rule:
                    print("\n--- udev Rule ---")
                    print(rule)
                    print("\nSave this to: /etc/udev/rules.d/99-can.rules")
                    print("Then run: sudo udevadm control --reload-rules")
            print()
            
        elif choice == "6":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice\n")


def main():
    parser = argparse.ArgumentParser(
        description='SocketCAN Device ID Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --list             # List all interfaces
  %(prog)s --info can0        # Show interface info
  %(prog)s --alias can0 mycan # Set alias
  %(prog)s --udev can0        # Show udev info
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all SocketCAN interfaces')
    parser.add_argument('--info', '-i', metavar='INTERFACE',
                        help='Get interface information')
    parser.add_argument('--alias', '-a', nargs=2, metavar=('INTERFACE', 'ALIAS'),
                        help='Set interface alias')
    parser.add_argument('--udev', '-u', metavar='INTERFACE',
                        help='Show udev information for interface')
    parser.add_argument('--rule', '-r', nargs=2, metavar=('INTERFACE', 'NEWNAME'),
                        help='Generate udev rule with new interface name')
    
    args = parser.parse_args()
    
    if not any([args.list, args.info, args.alias, args.udev, args.rule]):
        interactive_mode()
        return
    
    if args.list:
        interfaces = list_interfaces()
        if interfaces:
            print(f"Found {len(interfaces)} interface(s):")
            for iface in interfaces:
                name = iface.get('name', 'N/A')
                state = iface.get('state', 'N/A')
                bitrate = iface.get('bitrate', 'N/A')
                alias = iface.get('alias', '')
                print(f"  {name:<12} {state:<8} {bitrate:<12} {alias}")
        else:
            print("No SocketCAN interfaces found")
            
    elif args.info:
        info = get_info(args.info)
        print(f"Interface: {info['name']}")
        print(f"State: {info.get('state', 'N/A')}")
        print(f"Bitrate: {info.get('bitrate', 'N/A')}")
        print(f"Alias: {info.get('alias', 'None')}")
        if 'idVendor' in info:
            print(f"USB Vendor: {info['idVendor']}")
            print(f"USB Product: {info['idProduct']}")
            print(f"USB Serial: {info.get('serial', 'N/A')}")
            
    elif args.alias:
        set_alias(args.alias[0], args.alias[1])
        
    elif args.udev:
        show_udev_info(args.udev)
        
    elif args.rule:
        rule = generate_udev_rule(args.rule[0], args.rule[1])
        if rule:
            print(rule)


if __name__ == '__main__':
    main()
