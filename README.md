# SpaceX Launch Info to Meshtastic

A Python application that fetches information about the next SpaceX launch from Vandenberg Space Force Base and sends it to a Meshtastic channel.

## Features

- 🚀 Fetches next SpaceX launch from Vandenberg using the SpaceX API
- 🕐 Converts launch time to Arizona local time
- 📦 Retrieves mission name and payload information
- 📡 Sends formatted message to Meshtastic device via Serial or TCP
- ⚙️ Environment-based configuration
- 🔄 Cron-job compatible

## Requirements

- Python 3.7+
- Meshtastic device (radio with firmware 2.0+)
- Serial connection (USB) or TCP/IP connection to Meshtastic device

## Installation

1. Clone or navigate to this directory:
```bash
cd c:\DevOps\MeshtasticSpaceTools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create your configuration file:
```bash
cp .env.example .env
```

4. Edit `.env` with your settings:
```ini
# For Serial Connection (USB)
MESHTASTIC_CONNECTION_TYPE=serial
MESHTASTIC_SERIAL_PORT=COM3

# OR for TCP Connection
MESHTASTIC_CONNECTION_TYPE=tcp
MESHTASTIC_TCP_HOST=192.168.1.100

# Channel to send message to (0-7)
MESHTASTIC_CHANNEL=0
```

## Configuration

### Connection Types

**Serial (USB):**
- Windows: `COM3`, `COM4`, etc.
- Linux: `/dev/ttyUSB0`, `/dev/ttyACM0`
- macOS: `/dev/cu.usbserial-*`

**TCP:**
- Use the IP address of your Meshtastic device on the network
- Ensure your device has TCP enabled in settings

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MESHTASTIC_CONNECTION_TYPE` | Connection type: `serial` or `tcp` | `serial` | Yes |
| `MESHTASTIC_SERIAL_PORT` | Serial port path | `COM3` | If using serial |
| `MESHTASTIC_TCP_HOST` | TCP/IP hostname or address | `192.168.1.100` | If using TCP |
| `MESHTASTIC_CHANNEL` | Channel index (0-7) | `0` | No |

## Usage

### Standalone Execution

Run the script directly:
```bash
python spacex_meshtastic.py
```

Or on Unix-like systems (after making it executable):
```bash
chmod +x spacex_meshtastic.py
./spacex_meshtastic.py
```

### Cron Job Setup

To run automatically (e.g., daily at 8 AM):

**Linux/macOS:**
```bash
crontab -e
```

Add:
```
0 8 * * * cd /path/to/MeshtasticSpaceTools && /path/to/python spacex_meshtastic.py >> /var/log/spacex_meshtastic.log 2>&1
```

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 8:00 AM)
4. Action: Start a program
   - Program: `C:\DevOps\MeshtasticSpaceTools\.venv\Scripts\python.exe`
   - Arguments: `spacex_meshtastic.py`
   - Start in: `C:\DevOps\MeshtasticSpaceTools`

## Output Example

The script sends a formatted message like:
```
🚀 Starlink Group 6-34
📅 Jan 15, 2026 @ 07:30 AM AZ
📦 Starlink satellites
```

## Troubleshooting

### Serial Connection Issues
- Verify the correct port: Check Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac)
- Ensure no other application is using the port
- Check USB cable and connection

### TCP Connection Issues
- Verify device IP address
- Ensure Meshtastic device has TCP enabled
- Check firewall settings
- Confirm device is on the same network

### No Launches Found
- The script only looks for Vandenberg launches
- If no upcoming launches are scheduled, you'll see "No upcoming Vandenberg launches found"

### API Errors
- Check internet connection
- SpaceX API may be temporarily unavailable
- Rate limiting (unlikely with normal usage)

## Development

To test without sending to Meshtastic, you can comment out the `send_to_meshtastic()` call in the `main()` function.

## License

See LICENSE file for details.

## API Credits

This project uses the [Launch Library 2 API](https://thespacedevs.com/llapi) for launch data, which provides up-to-date information about SpaceX launches and other launch providers.
