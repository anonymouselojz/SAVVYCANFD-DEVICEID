# SavvyCANFD Device ID Tool

用于查看和修改 PCAN USB 设备的 DEVICE ID 的 Python 工具。

## 功能

- 列出所有连接的 PCAN 设备
- 查看当前设备的 DEVICE ID (32位)
- 修改设备的 DEVICE ID (0 - 0xFFFFFFFF)
- 通过 DEVICE ID 查找设备

## 依赖

```bash
pip install python-can
```

## 平台支持

- **Windows**: 需要安装 [PEAK PCAN 驱动](https://www.peak-system.com/PCAN-USB.199.0.html)
- **Linux**: 需要安装 `pcan` 驱动模块

## 使用方法

### 交互式模式
```bash
python pcan_device_id.py
```

### 命令行模式

**列出所有设备：**
```bash
python pcan_device_id.py --list
```

**查看 DEVICE ID：**
```bash
python pcan_device_id.py --get PCAN_USBBUS1
```

**修改 DEVICE ID（支持十六进制）：**
```bash
python pcan_device_id.py --set PCAN_USBBUS1 0x80FF0000
python pcan_device_id.py --set PCAN_USBBUS1 2164191232
```

**通过 ID 查找设备：**
```bash
python pcan_device_id.py --find 0x80FF0000
```

## 注意事项

- DEVICE ID 范围为 0 - 0xFFFFFFFF (32位)
- 修改 DEVICE ID 后需要重新插拔设备或重启系统才能生效
- 支持多种输入格式：`0x80FF0000`、`80FF0000h`、十进制 `2164191232`

## License

MIT
