#!/usr/bin/env python3
"""
SavvyCANFD Device ID Tool
A Python tool for viewing and modifying SavvyCANFD USB device DEVICE ID (32-bit)

Features:
- List all connected SavvyCANFD devices
- View current device DEVICE ID (with hex display)
- Modify device DEVICE ID (0 - 0xFFFFFFFF)

Requirements:
- SavvyCANFD driver (Windows) or pcan driver (Linux)
- python-can: pip install python-can

Note: Replug the device or restart system after modifying DEVICE ID

Author: Kimi Claw
Date: 2025
"""

import sys
import argparse
from typing import List, Optional, Tuple

try:
    import can
    from can.interfaces.pcan import PcanBus
except ImportError:
    print("Error: python-can not installed. Run: pip install python-can")
    sys.exit(1)


# SavvyCANFD channel list
SAVVYCANFD_CHANNELS = [
    "PCAN_ISABUS1", "PCAN_ISABUS2", "PCAN_ISABUS3", "PCAN_ISABUS4",
    "PCAN_ISABUS5", "PCAN_ISABUS6", "PCAN_ISABUS7", "PCAN_ISABUS8",
    "PCAN_DNGBUS1",
    "PCAN_PCIBUS1", "PCAN_PCIBUS2", "PCAN_PCIBUS3", "PCAN_PCIBUS4",
    "PCAN_PCIBUS5", "PCAN_PCIBUS6", "PCAN_PCIBUS7", "PCAN_PCIBUS8",
    "PCAN_PCIBUS9", "PCAN_PCIBUS10", "PCAN_PCIBUS11", "PCAN_PCIBUS12",
    "PCAN_PCIBUS13", "PCAN_PCIBUS14", "PCAN_PCIBUS15", "PCAN_PCIBUS16",
    "PCAN_USBBUS1", "PCAN_USBBUS2", "PCAN_USBBUS3", "PCAN_USBBUS4",
    "PCAN_USBBUS5", "PCAN_USBBUS6", "PCAN_USBBUS7", "PCAN_USBBUS8",
    "PCAN_USBBUS9", "PCAN_USBBUS10", "PCAN_USBBUS11", "PCAN_USBBUS12",
    "PCAN_USBBUS13", "PCAN_USBBUS14", "PCAN_USBBUS15", "PCAN_USBBUS16",
    "PCAN_PCCBUS1", "PCAN_PCCBUS2",
    "PCAN_LANBUS1", "PCAN_LANBUS2", "PCAN_LANBUS3", "PCAN_LANBUS4",
    "PCAN_LANBUS5", "PCAN_LANBUS6", "PCAN_LANBUS7", "PCAN_LANBUS8",
    "PCAN_LANBUS9", "PCAN_LANBUS10", "PCAN_LANBUS11", "PCAN_LANBUS12",
    "PCAN_LANBUS13", "PCAN_LANBUS14", "PCAN_LANBUS15", "PCAN_LANBUS16",
]


def parse_id(id_str: str) -> int:
    """
    Parse Device ID string, supports decimal and hexadecimal
    
    Supported formats:
    - Decimal: "123456"
    - Hex: "0x80FF0000", "80FF0000h", "80FF0000H"
    """
    id_str = id_str.strip()
    
    # Hex with 0x prefix
    if id_str.lower().startswith('0x'):
        return int(id_str, 16)
    
    # Hex with h/H suffix
    if id_str.lower().endswith('h'):
        return int(id_str[:-1], 16)
    
    # Default decimal
    return int(id_str)


def format_id(device_id: int) -> str:
    """Format Device ID display, show both decimal and hexadecimal"""
    return f"{device_id} (0x{device_id:08X})"


def list_devices() -> List[Tuple[str, Optional[int], str]]:
    """
    Scan and list all available SavvyCANFD devices
    
    Returns:
        List of (channel, device_id, status)
    """
    devices = []
    
    for channel in SAVVYCANFD_CHANNELS:
        try:
            bus = PcanBus(channel=channel, bitrate=500000)
            try:
                device_id = bus.get_device_number()
                devices.append((channel, device_id, "Connected"))
            except Exception as e:
                devices.append((channel, None, f"Connected but no ID: {e}"))
            finally:
                bus.shutdown()
        except Exception:
            # Device not available, skip
            pass
    
    return devices


def get_device_id(channel: str) -> Optional[int]:
    """
    Get DEVICE ID for specified SavvyCANFD channel
    
    Args:
        channel: SavvyCANFD channel name (e.g., PCAN_USBBUS1)
        
    Returns:
        Device ID or None if failed
    """
    try:
        bus = PcanBus(channel=channel, bitrate=500000)
        try:
            device_id = bus.get_device_number()
            return device_id
        finally:
            bus.shutdown()
    except Exception as e:
        print(f"Error: Cannot access {channel}: {e}")
        return None


def set_device_id(channel: str, device_id: int) -> bool:
    """
    Set DEVICE ID for specified SavvyCANFD channel
    
    Args:
        channel: SavvyCANFD channel name (e.g., PCAN_USBBUS1)
        device_id: New device ID (0 - 0xFFFFFFFF)
        
    Returns:
        True if successful
    """
    if not 0 <= device_id <= 0xFFFFFFFF:
        print(f"Error: Device ID must be in range 0 - 0xFFFFFFFF (4294967295)")
        return False
    
    try:
        bus = PcanBus(channel=channel, bitrate=500000)
        try:
            old_id = bus.get_device_number()
            result = bus.set_device_number(device_id)
            if result:
                print(f"✓ Successfully changed {channel} DEVICE ID from {format_id(old_id)} to {format_id(device_id)}")
                print("  Note: Replug the device or restart system for changes to take effect")
                return True
            else:
                print(f"✗ Failed to set {channel} DEVICE ID")
                return False
        finally:
            bus.shutdown()
    except Exception as e:
        print(f"Error: Cannot access {channel}: {e}")
        return False


def find_device_by_id(target_id: int) -> Optional[str]:
    """
    Find SavvyCANFD channel by DEVICE ID
    
    Args:
        target_id: Target device ID
        
    Returns:
        Channel name or None if not found
    """
    for channel in SAVVYCANFD_CHANNELS:
        try:
            bus = PcanBus(channel=channel, bitrate=500000)
            try:
                device_id = bus.get_device_number()
                if device_id == target_id:
                    return channel
            finally:
                bus.shutdown()
        except Exception:
            pass
    return None


def interactive_mode():
    """Interactive mode"""
    print("\n=== SavvyCANFD Device ID Tool (32-bit) ===\n")
    
    while True:
        print("Options:")
        print("  1. List all SavvyCANFD devices")
        print("  2. Get DEVICE ID for channel")
        print("  3. Set DEVICE ID for channel")
        print("  4. Find device by DEVICE ID")
        print("  5. Exit")
        print()
        
        choice = input("Select (1-5): ").strip()
        
        if choice == "1":
            print("\nScanning SavvyCANFD devices...")
            devices = list_devices()
            if devices:
                print(f"\nFound {len(devices)} device(s):")
                print("-" * 60)
                print(f"{'Channel':<20} {'Device ID':<30} {'Status':<20}")
                print("-" * 60)
                for channel, dev_id, status in devices:
                    id_str = format_id(dev_id) if dev_id is not None else "N/A"
                    print(f"{channel:<20} {id_str:<30} {status:<20}")
                print("-" * 60)
            else:
                print("No SavvyCANFD devices found")
            print()
            
        elif choice == "2":
            channel = input("Enter channel name (e.g., PCAN_USBBUS1): ").strip().upper()
            if channel:
                device_id = get_device_id(channel)
                if device_id is not None:
                    print(f"\n{channel} DEVICE ID: {format_id(device_id)}\n")
                else:
                    print(f"\nCannot get {channel} DEVICE ID\n")
            else:
                print("Channel name cannot be empty\n")
                
        elif choice == "3":
            channel = input("Enter channel name (e.g., PCAN_USBBUS1): ").strip().upper()
            if not channel:
                print("Channel name cannot be empty\n")
                continue
                
            current_id = get_device_id(channel)
            if current_id is None:
                print(f"Cannot access {channel}\n")
                continue
                
            print(f"Current DEVICE ID: {format_id(current_id)}")
            print("Supported formats: decimal(123456) or hex(0x80FF0000 / 80FF0000h)")
            new_id_str = input("Enter new DEVICE ID: ").strip()
            
            try:
                new_id = parse_id(new_id_str)
                if 0 <= new_id <= 0xFFFFFFFF:
                    confirm = input(f"Confirm change {channel} DEVICE ID from {format_id(current_id)} to {format_id(new_id)}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        set_device_id(channel, new_id)
                else:
                    print("Error: DEVICE ID must be in range 0 - 0xFFFFFFFF\n")
            except ValueError as e:
                print(f"Error: Invalid input format - {e}\n")
            print()
            
        elif choice == "4":
            id_str = input("Enter DEVICE ID to find (supports 0x prefix or h suffix): ").strip()
            try:
                target_id = parse_id(id_str)
                channel = find_device_by_id(target_id)
                if channel:
                    print(f"\nDEVICE ID {format_id(target_id)} found on channel: {channel}\n")
                else:
                    print(f"\nNo device found with DEVICE ID {format_id(target_id)}\n")
            except ValueError as e:
                print(f"Error: Invalid input format - {e}\n")
                
        elif choice == "5":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice, please try again\n")


def main():
    parser = argparse.ArgumentParser(
        description='SavvyCANFD Device ID Tool (32-bit)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode
  %(prog)s --list                    # List all devices
  %(prog)s --get PCAN_USBBUS1        # Get DEVICE ID for channel
  %(prog)s --set PCAN_USBBUS1 0x80FF0000  # Set DEVICE ID (hex)
  %(prog)s --set PCAN_USBBUS1 2164191232   # Set DEVICE ID (decimal)
  %(prog)s --find 0x80FF0000         # Find device by ID

DEVICE ID format support:
  - Decimal: 2164191232
  - Hex: 0x80FF0000 or 80FF0000h
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all connected SavvyCANFD devices')
    parser.add_argument('--get', '-g', metavar='CHANNEL',
                        help='Get DEVICE ID for channel (e.g., PCAN_USBBUS1)')
    parser.add_argument('--set', '-s', nargs=2, metavar=('CHANNEL', 'ID'),
                        help='Set DEVICE ID for channel (supports 0x prefix or h suffix)')
    parser.add_argument('--find', '-f', metavar='ID',
                        help='Find device by DEVICE ID (supports 0x prefix or h suffix)')
    
    args = parser.parse_args()
    
    # If no arguments, enter interactive mode
    if not any([args.list, args.get, args.set, args.find]):
        interactive_mode()
        return
    
    # Command line mode
    if args.list:
        devices = list_devices()
        if devices:
            print(f"Found {len(devices)} SavvyCANFD device(s):")
            print("-" * 60)
            print(f"{'Channel':<20} {'Device ID':<30} {'Status':<20}")
            print("-" * 60)
            for channel, dev_id, status in devices:
                id_str = format_id(dev_id) if dev_id is not None else "N/A"
                print(f"{channel:<20} {id_str:<30} {status:<20}")
            print("-" * 60)
        else:
            print("No SavvyCANFD devices found")
            sys.exit(1)
            
    elif args.get:
        device_id = get_device_id(args.get.upper())
        if device_id is not None:
            print(f"{args.get.upper()} DEVICE ID: {format_id(device_id)}")
        else:
            print(f"Cannot get {args.get.upper()} DEVICE ID")
            sys.exit(1)
            
    elif args.set:
        channel = args.set[0].upper()
        try:
            new_id = parse_id(args.set[1])
            if set_device_id(channel, new_id):
                sys.exit(0)
            else:
                sys.exit(1)
        except ValueError as e:
            print(f"Error: Invalid DEVICE ID format '{args.set[1]}': {e}")
            sys.exit(1)
            
    elif args.find:
        try:
            target_id = parse_id(args.find)
            channel = find_device_by_id(target_id)
            if channel:
                print(f"DEVICE ID {format_id(target_id)} found on channel: {channel}")
            else:
                print(f"No device found with DEVICE ID {format_id(target_id)}")
                sys.exit(1)
        except ValueError as e:
            print(f"Error: Invalid DEVICE ID format '{args.find}': {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
