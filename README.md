# SavvyCANFD Device ID Tool

A Python tool for viewing and modifying SavvyCANFD USB device DEVICE ID.

## Features

- List all connected SavvyCANFD devices
- View current device DEVICE ID
- Modify device DEVICE ID (0 - 0xFFFFFFFF)
- Find device by DEVICE ID
- **NEW: PyQt6 GUI version for easy operation**


## Requirements

```bash
pip install python-can
```

For GUI version:
```bash
pip install PyQt6 python-can
```

## Usage

### GUI Version (Recommended)

```bash
python savvycanfd_gui.py
```

Features:
- Visual device list with auto-scan
- One-click ID read/write
- Input validation and confirmation dialogs
- Operation log display

### CLI Version

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


## Notes

- DEVICE ID range: 0 - 0xFFFFFFFF (32-bit)
- Replug the device or restart system after modifying DEVICE ID
- Supports hex format: `0x80FF0000` or `80FF0000h`
- Supports decimal format: `2164191232`


## Files

- `savvycanfd_device_id.py` - CLI version
- `savvycanfd_gui.py` - PyQt6 GUI version


## Screenshots

GUI Layout:
```
┌────────────────────────────────────────────────────────┐
│ SavvyCANFD Device ID Tool                              │
├──────────────────────────┬─────────────────────────────┤
│ Connected Devices        │ Device Info                 │
│ ┌────────────────────┐   │ Channel: PCAN_USBBUS1       │
│ │ Channel   │ ID     │   │ Current ID: 2164191232      │
│ ├────────────────────┤   │ (0x80FF0000)                │
│ │PCAN_USBBUS1│0x80..│   ├─────────────────────────────┤
│ │PCAN_USBBUS2│N/A   │   │ [Get Device ID]             │
│ └────────────────────┘   │ Channel: [PCAN_USBBUS1 ]    │
│ [🔄 Scan Devices]        │ [📖 Get ID]                 │
│                          ├─────────────────────────────┤
│                          │ [Set Device ID]             │
│                          │ New ID: [0x80FF0000    ]    │
│                          │ [✏️ Set ID]                  │
└──────────────────────────┴─────────────────────────────┘
```
