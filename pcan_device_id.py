#!/usr/bin/env python3
"""
PCAN Device ID Tool
用于查看和修改 PCAN USB 设备的 DEVICE ID (32位)

功能:
- 列出所有连接的 PCAN 设备
- 查看当前设备的 DEVICE ID (支持十六进制显示)
- 修改设备的 DEVICE ID (0 - 0xFFFFFFFF)

注意:
- 需要安装 PCAN 驱动 (Windows) 或 pcan 驱动 (Linux)
- 需要安装 python-can: pip install python-can
- 修改 DEVICE ID 后需要重新插拔设备或重启才能生效

作者: Kimi Claw
日期: 2025
"""

import sys
import argparse
import re
from typing import List, Optional, Tuple

try:
    import can
    from can.interfaces.pcan import PcanBus
except ImportError:
    print("错误: 未安装 python-can。请运行: pip install python-can")
    sys.exit(1)


# PCAN 通道列表
PCAN_CHANNELS = [
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
    解析 Device ID 字符串，支持十进制和十六进制
    
    支持的格式:
    - 十进制: "123456"
    - 十六进制: "0x80FF0000", "80FF0000h", "80FF0000H"
    """
    id_str = id_str.strip()
    
    # 匹配 0x 开头的十六进制
    if id_str.lower().startswith('0x'):
        return int(id_str, 16)
    
    # 匹配 h/H 结尾的十六进制
    if id_str.lower().endswith('h'):
        return int(id_str[:-1], 16)
    
    # 默认十进制
    return int(id_str)


def format_id(device_id: int) -> str:
    """格式化 Device ID 显示，同时显示十进制和十六进制"""
    return f"{device_id} (0x{device_id:08X})"


def list_pcan_devices() -> List[Tuple[str, Optional[int], str]]:
    """
    扫描并列出所有可用的 PCAN 设备
    
    Returns:
        列表，每项为 (通道名, 设备ID, 状态描述)
    """
    devices = []
    
    for channel in PCAN_CHANNELS:
        try:
            bus = PcanBus(channel=channel, bitrate=500000)
            try:
                device_id = bus.get_device_number()
                devices.append((channel, device_id, "已连接"))
            except Exception as e:
                devices.append((channel, None, f"已连接但无法获取ID: {e}"))
            finally:
                bus.shutdown()
        except Exception:
            # 设备不存在或无法访问，跳过
            pass
    
    return devices


def get_device_id(channel: str) -> Optional[int]:
    """
    获取指定 PCAN 通道的 DEVICE ID
    
    Args:
        channel: PCAN 通道名 (如 PCAN_USBBUS1)
        
    Returns:
        设备 ID，如果失败返回 None
    """
    try:
        bus = PcanBus(channel=channel, bitrate=500000)
        try:
            device_id = bus.get_device_number()
            return device_id
        finally:
            bus.shutdown()
    except Exception as e:
        print(f"错误: 无法访问 {channel}: {e}")
        return None


def set_device_id(channel: str, device_id: int) -> bool:
    """
    设置指定 PCAN 通道的 DEVICE ID
    
    Args:
        channel: PCAN 通道名 (如 PCAN_USBBUS1)
        device_id: 新的设备 ID (0 - 0xFFFFFFFF)
        
    Returns:
        是否设置成功
    """
    if not 0 <= device_id <= 0xFFFFFFFF:
        print(f"错误: 设备 ID 必须在 0 - 0xFFFFFFFF (4294967295) 范围内")
        return False
    
    try:
        bus = PcanBus(channel=channel, bitrate=500000)
        try:
            old_id = bus.get_device_number()
            result = bus.set_device_number(device_id)
            if result:
                print(f"✓ 成功将 {channel} 的 DEVICE ID 从 {format_id(old_id)} 修改为 {format_id(device_id)}")
                print("  注意: 请重新插拔设备或重启系统使更改生效")
                return True
            else:
                print(f"✗ 修改 {channel} 的 DEVICE ID 失败")
                return False
        finally:
            bus.shutdown()
    except Exception as e:
        print(f"错误: 无法访问 {channel}: {e}")
        return False


def find_device_by_id(target_id: int) -> Optional[str]:
    """
    通过 DEVICE ID 查找对应的 PCAN 通道
    
    Args:
        target_id: 目标设备 ID
        
    Returns:
        通道名，如果未找到返回 None
    """
    for channel in PCAN_CHANNELS:
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
    """交互式模式"""
    print("\n=== PCAN Device ID 管理工具 (32位) ===\n")
    
    while True:
        print("选项:")
        print("  1. 列出所有 PCAN 设备")
        print("  2. 查看指定通道的 DEVICE ID")
        print("  3. 修改指定通道的 DEVICE ID")
        print("  4. 通过 DEVICE ID 查找设备")
        print("  5. 退出")
        print()
        
        choice = input("请选择 (1-5): ").strip()
        
        if choice == "1":
            print("\n扫描 PCAN 设备...")
            devices = list_pcan_devices()
            if devices:
                print(f"\n找到 {len(devices)} 个设备:")
                print("-" * 60)
                print(f"{'通道':<20} {'设备ID':<30} {'状态':<20}")
                print("-" * 60)
                for channel, dev_id, status in devices:
                    id_str = format_id(dev_id) if dev_id is not None else "N/A"
                    print(f"{channel:<20} {id_str:<30} {status:<20}")
                print("-" * 60)
            else:
                print("未找到任何 PCAN 设备")
            print()
            
        elif choice == "2":
            channel = input("请输入通道名 (如 PCAN_USBBUS1): ").strip().upper()
            if channel:
                device_id = get_device_id(channel)
                if device_id is not None:
                    print(f"\n{channel} 的 DEVICE ID: {format_id(device_id)}\n")
                else:
                    print(f"\n无法获取 {channel} 的 DEVICE ID\n")
            else:
                print("通道名不能为空\n")
                
        elif choice == "3":
            channel = input("请输入通道名 (如 PCAN_USBBUS1): ").strip().upper()
            if not channel:
                print("通道名不能为空\n")
                continue
                
            current_id = get_device_id(channel)
            if current_id is None:
                print(f"无法访问 {channel}\n")
                continue
                
            print(f"当前 DEVICE ID: {format_id(current_id)}")
            print("支持格式: 十进制(123456) 或 十六进制(0x80FF0000 / 80FF0000h)")
            new_id_str = input("请输入新的 DEVICE ID: ").strip()
            
            try:
                new_id = parse_id(new_id_str)
                if 0 <= new_id <= 0xFFFFFFFF:
                    confirm = input(f"确认将 {channel} 的 DEVICE ID 从 {format_id(current_id)} 改为 {format_id(new_id)}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        set_device_id(channel, new_id)
                else:
                    print("错误: DEVICE ID 必须在 0 - 0xFFFFFFFF 范围内\n")
            except ValueError as e:
                print(f"错误: 无效的输入格式 - {e}\n")
            print()
            
        elif choice == "4":
            id_str = input("请输入要查找的 DEVICE ID (支持 0x 前缀或 h 后缀): ").strip()
            try:
                target_id = parse_id(id_str)
                channel = find_device_by_id(target_id)
                if channel:
                    print(f"\nDEVICE ID {format_id(target_id)} 对应的通道: {channel}\n")
                else:
                    print(f"\n未找到 DEVICE ID 为 {format_id(target_id)} 的设备\n")
            except ValueError as e:
                print(f"错误: 无效的输入格式 - {e}\n")
                
        elif choice == "5":
            print("再见!")
            break
            
        else:
            print("无效的选择，请重试\n")


def main():
    parser = argparse.ArgumentParser(
        description='PCAN Device ID 管理工具 (32位)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 交互式模式
  %(prog)s --list                    # 列出所有设备
  %(prog)s --get PCAN_USBBUS1        # 查看指定通道的 DEVICE ID
  %(prog)s --set PCAN_USBBUS1 0x80FF0000  # 修改 DEVICE ID (十六进制)
  %(prog)s --set PCAN_USBBUS1 2164191232   # 修改 DEVICE ID (十进制)
  %(prog)s --find 0x80FF0000         # 查找 DEVICE ID 对应的设备

DEVICE ID 格式支持:
  - 十进制: 2164191232
  - 十六进制: 0x80FF0000 或 80FF0000h
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true',
                        help='列出所有连接的 PCAN 设备')
    parser.add_argument('--get', '-g', metavar='CHANNEL',
                        help='获取指定通道的 DEVICE ID (如 PCAN_USBBUS1)')
    parser.add_argument('--set', '-s', nargs=2, metavar=('CHANNEL', 'ID'),
                        help='设置指定通道的 DEVICE ID (支持 0x 前缀或 h 后缀)')
    parser.add_argument('--find', '-f', metavar='ID',
                        help='通过 DEVICE ID 查找设备 (支持 0x 前缀或 h 后缀)')
    
    args = parser.parse_args()
    
    # 如果没有参数，进入交互式模式
    if not any([args.list, args.get, args.set, args.find]):
        interactive_mode()
        return
    
    # 命令行模式
    if args.list:
        devices = list_pcan_devices()
        if devices:
            print(f"找到 {len(devices)} 个 PCAN 设备:")
            print("-" * 60)
            print(f"{'通道':<20} {'设备ID':<30} {'状态':<20}")
            print("-" * 60)
            for channel, dev_id, status in devices:
                id_str = format_id(dev_id) if dev_id is not None else "N/A"
                print(f"{channel:<20} {id_str:<30} {status:<20}")
            print("-" * 60)
        else:
            print("未找到任何 PCAN 设备")
            sys.exit(1)
            
    elif args.get:
        device_id = get_device_id(args.get.upper())
        if device_id is not None:
            print(f"{args.get.upper()} 的 DEVICE ID: {format_id(device_id)}")
        else:
            print(f"无法获取 {args.get.upper()} 的 DEVICE ID")
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
            print(f"错误: 无效的 DEVICE ID 格式 '{args.set[1]}': {e}")
            sys.exit(1)
            
    elif args.find:
        try:
            target_id = parse_id(args.find)
            channel = find_device_by_id(target_id)
            if channel:
                print(f"DEVICE ID {format_id(target_id)} 对应的通道: {channel}")
            else:
                print(f"未找到 DEVICE ID 为 {format_id(target_id)} 的设备")
                sys.exit(1)
        except ValueError as e:
            print(f"错误: 无效的 DEVICE ID 格式 '{args.find}': {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
