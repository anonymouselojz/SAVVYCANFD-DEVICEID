# SavvyCANFD Device ID Tool

A Python tool for viewing and modifying SavvyCANFD USB device DEVICE ID.

## Features

- List all connected SavvyCANFD devices
- View current device DEVICE ID
- Modify device DEVICE ID (0 - 0xFFFFFFFF)
- Find device by DEVICE ID

## Requirements

```bash
pip install python-can
```

## Platform Support

- **Windows**: Requires [SavvyCANFD Driver](https://www.peak-system.com/PCAN-USB.199.0.html)
- **Linux**: Requires `pcan` driver module

## Usage

### Interactive Mode
```bash
python savvycanfd_device_id.py
```

### Command Line Mode

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

## Notes

- DEVICE ID range: 0 - 0xFFFFFFFF (32-bit)
- Replug the device or restart system after modifying DEVICE ID
- Supports hex format: `0x80FF0000` or `80FF0000h`
- Supports decimal format: `2164191232`

## License

MIT
