#!/usr/bin/env python3
"""
SpaceX Launch Info to Meshtastic
Fetches next Vandenberg launch information and sends it to a Meshtastic channel.
"""

import os
import sys
import logging
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv
import meshtastic
import meshtastic.tcp_interface
import meshtastic.serial_interface


def load_config():
    """Load configuration from environment variables."""
    load_dotenv()
    
    config = {
        'connection_type': os.getenv('MESHTASTIC_CONNECTION_TYPE', 'serial').lower(),
        'serial_port': os.getenv('MESHTASTIC_SERIAL_PORT', 'COM3'),
        'tcp_host': os.getenv('MESHTASTIC_TCP_HOST', '192.168.1.100'),
        'channel': int(os.getenv('MESHTASTIC_CHANNEL', '0')),
        'send_enabled': os.getenv('MESHTASTIC_SEND_ENABLED', 'true').lower() == 'true'
    }
    
    return config


def get_next_vandenberg_launch():
    """
    Fetch the next SpaceX launch from Vandenberg using Launch Library 2 API.
    Returns launch information or None if no launch found.
    """
    try:
        # Use Launch Library 2 API (more up-to-date than SpaceX API)
        # Filter for SpaceX launches only
        url = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
        
        params = {
            'lsp__name': 'SpaceX',  # Launch Service Provider
            'limit': 100,
            'mode': 'detailed'
        }
        
        logging.info("Querying Launch Library API for SpaceX launches...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        launches = data.get('results', [])
        logging.info(f"Found {len(launches)} total SpaceX launches")
        
        # Filter for Vandenberg launches
        vandenberg_keywords = ['vandenberg', 'vsfb', 'slc-4', 'slc-3']
        vandenberg_count = 0
        
        for launch in launches:
            # Check launch pad location
            pad = launch.get('pad', {})
            pad_name = pad.get('name', '').lower()
            location_name = pad.get('location', {}).get('name', '').lower()
            
            # Check if this is a Vandenberg launch
            if any(keyword in pad_name for keyword in vandenberg_keywords) or \
               any(keyword in location_name for keyword in vandenberg_keywords):
                vandenberg_count += 1
                
                # Return the first (soonest) Vandenberg launch
                if vandenberg_count == 1:
                    # Extract payload information
                    payload_names = []
                    mission = launch.get('mission', {})
                    mission_name = mission.get('name', '')
                    mission_description = mission.get('description', '')
                    
                    # Try to get payload from mission name or rocket
                    if mission_name:
                        payload_names.append(mission_name)
                    else:
                        rocket_name = launch.get('rocket', {}).get('configuration', {}).get('name', '')
                        if rocket_name:
                            payload_names.append(rocket_name)
                    
                    logging.info(f"Found next Vandenberg launch: {launch.get('name')}")
                    return {
                        'name': launch.get('name', 'Unknown Mission'),
                        'date_utc': launch.get('net', ''),  # NET = No Earlier Than
                        'payload_names': payload_names,
                        'launchpad_name': pad.get('name', 'Vandenberg'),
                        'mission_type': mission.get('type', 'Unknown')
                    }
        
        logging.info(f"No Vandenberg launches found (checked {vandenberg_count} Vandenberg launches)")
        return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching launch data: {e}")
        return None


def get_payload_info(payload_names):
    """Format payload information from launch data."""
    if not payload_names:
        return "No payload information"
    
    return ", ".join(payload_names)


def format_launch_message(launch_info):
    """Format launch information into a concise message."""
    if not launch_info:
        return "No upcoming Vandenberg launches found."
    
    # Convert UTC time to Arizona time
    utc_time = datetime.fromisoformat(launch_info['date_utc'].replace('Z', '+00:00'))
    az_tz = pytz.timezone('America/Phoenix')  # Arizona doesn't observe DST
    az_time = utc_time.astimezone(az_tz)
    
    # Get payload information
    payload_info = get_payload_info(launch_info.get('payload_names', []))
    
    # Format message
    message = (
        f"Next Vandenberg Launch:\n"
        f"🚀 {launch_info['name']}\n"
        f"📅 {az_time.strftime('%b %d, %Y @ %I:%M %p')} AZ\n"
        f"📦 {payload_info}"
    )
    
    return message


def send_to_meshtastic(message, config):
    """Send message to Meshtastic device or print to console in test mode."""
    # Truncate message to 200 character limit
    MAX_MESSAGE_LENGTH = 200
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[:MAX_MESSAGE_LENGTH-3] + "..."
        print(f"⚠️  Message truncated to {MAX_MESSAGE_LENGTH} characters")
    
    # Test mode - just print the message
    if not config['send_enabled']:
        print("\n" + "=" * 50)
        print("TEST MODE - Message NOT sent to Meshtastic")
        print("=" * 50)
        print(f"Channel: {config['channel']}")
        print(f"Message length: {len(message)} characters")
        print("\nMessage content:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        return True
    
    # Actually send to Meshtastic
    interface = None
    
    try:
        # Connect to Meshtastic device
        if config['connection_type'] == 'tcp':
            print(f"Connecting to Meshtastic via TCP: {config['tcp_host']}")
            interface = meshtastic.tcp_interface.TCPInterface(hostname=config['tcp_host'])
        else:
            print(f"Connecting to Meshtastic via Serial: {config['serial_port']}")
            interface = meshtastic.serial_interface.SerialInterface(devPath=config['serial_port'])
        
        # Send message to channel
        print(f"Sending message to channel {config['channel']} ({len(message)} chars)")
        interface.sendText(message, channelIndex=config['channel'])
        print("Message sent successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error sending to Meshtastic: {e}")
        return False
        
    finally:
        if interface:
            interface.close()


def main():
    """Main function to fetch launch info and send to Meshtastic."""
    # Configure logging
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    print("SpaceX Vandenberg Launch Info -> Meshtastic")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    print(f"Connection: {config['connection_type'].upper()}")
    print(f"Send to Meshtastic: {'ENABLED' if config['send_enabled'] else 'DISABLED (Test Mode)'}")
    
    # Fetch launch information
    print("Fetching next Vandenberg launch...")
    launch_info = get_next_vandenberg_launch()
    
    if not launch_info:
        logging.info("No upcoming Vandenberg launches found. Exiting.")
        return 0
    
    # Format message
    message = format_launch_message(launch_info)
    print("\nMessage to send:")
    print(message)
    print()
    
    # Send to Meshtastic
    success = send_to_meshtastic(message, config)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
