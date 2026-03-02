# SavvyCANFD Device ID Tool

A Python tool for viewing and modifying SavvyCANFD USB device DEVICE ID.

## Features

- List all connected SavvyCANFD devices
- View current device DEVICE ID
- Modify device DEVICE ID (0 - 0xFFFFFFFF)
- Find device by DEVICE ID
- Linux SocketCAN support (alias and udev rules)

## Requirements

```bash
pip install python-can
```

## Usage

### Windows - SavvyCANFD Mode

For PCAN-USB hardware using PEAK driver.

**Interactive Mode:**
```bash
python savvycanfd_device_id.py
```

**List all devices:**
```bash
python savvycanfd_device_id.py --list
```

**Get DEVICE ID:**
```bash
python savvycanfd_device_id.py --get PCAN_USBBUS1
```

**Set DEVICE ID (hex):**
```bash
python savvycanfd_device_id.py --set PCAN_USBBUS1 0x80FF0000
```

**Set DEVICE ID (decimal):**
```bash
python savvycanfd_device_id.py --set PCAN_USBBUS1 2164191232
```

**Find device by ID:**
```bash
python savvycanfd_device_id.py --find 0x80FF0000
```

### Linux - SocketCAN Mode

For devices recognized as SocketCAN interfaces (can0, can1, etc.).

**List all CAN interfaces:**
```bash
python socketcan_device_id.py --list
```

**Get interface info:**
```bash
python socketcan_device_id.py --info can0
```

**Set interface alias:**
```bash
sudo python socketcan_device_id.py --alias can0 my_project_can
```

**Show udev info (USB attributes):**
```bash
python socketcan_device_id.py --udev can0
```

**Generate udev rule for persistent naming:**
```bash
python socketcan_device_id.py --rule can0 can_fixed_name
```

Then save the rule:
```bash
sudo tee /etc/udev/rules.d/99-can.rules << 'EOF'
# Paste the generated rule here
EOF
sudo udevadm control --reload-rules
```

## Notes

- DEVICE ID range: 0 - 0xFFFFFFFF (32-bit)
- Replug the device or restart system after modifying DEVICE ID
- Supports hex format: `0x80FF0000` or `80FF0000h`
- Supports decimal format: `2164191232`
- Linux SocketCAN mode requires root privileges for setting alias

## Files

- `savvycanfd_device_id.py` - Windows/SavvyCANFD driver mode
- `socketcan_device_id.py` - Linux SocketCAN mode

## License

MIT
