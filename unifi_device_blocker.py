import argparse
import sys
import os
from pyunifi.controller import Controller

# Unifi Controller Config from Environment Variables
UNIFI_HOST = os.getenv('UNIFI_HOST', '192.168.1.1')  # Unifi Controller's IP address
UNIFI_USERNAME = os.getenv('UNIFI_USERNAME', 'admin')  # Unifi Controller username
UNIFI_PASSWORD = os.getenv('UNIFI_PASSWORD', 'password')  # Unifi Controller password
UNIFI_PORT = int(os.getenv('UNIFI_PORT', 8443))
UNIFI_VERSION = os.getenv('UNIFI_VERSION', 'UDMP-unifiOS')  # Version for UDM Pro


def get_device_by_name(controller, device_name):
    devices = controller.get_clients()
    for device in devices:
        if device.get('hostname', '').lower() == device_name.lower():
            return device
    return None


def block_device(controller, device):
    # Create a firewall rule to block the device's internet access
    mac_address = device.get('mac')
    if not mac_address:
        raise ValueError("Device MAC address not found")

    # Check if the device is already blocked
    blocked_clients = controller.get_blocked_clients()
    for blocked in blocked_clients:
        if blocked.get('mac') == mac_address:
            if blocked.get('blocked', False):
                print(f"Error: Device {device['hostname']} ({mac_address}) is already blocked.")
                sys.exit(1)
            else:
                # Enable the existing rule
                controller.block_client(mac_address)
                print(f"Internet access re-disabled for device {device['hostname']} ({mac_address})")
                return

    # Block the device using the API
    controller.block_client(mac_address)
    print(f"Internet access disabled for device {device['hostname']} ({mac_address})")


def unblock_device(controller, device):
    # Remove the firewall rule blocking the device's internet access
    mac_address = device.get('mac')
    if not mac_address:
        raise ValueError("Device MAC address not found")

    # Check if the device is currently blocked
    blocked_clients = controller.get_blocked_clients()
    for blocked in blocked_clients:
        if blocked.get('mac') == mac_address:
            if not blocked.get('blocked', False):
                print(f"Error: Device {device['hostname']} ({mac_address}) is not currently blocked.")
                sys.exit(1)
            else:
                # Unblock the device using the API
                controller.unblock_client(mac_address)
                print(f"Internet access enabled for device {device['hostname']} ({mac_address})")
                return

    print(f"Error: No blocking rule found for device {device['hostname']} ({mac_address})")
    sys.exit(1)


def main(device_name, action):
    try:
        controller = Controller(UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD, UNIFI_PORT, version=UNIFI_VERSION, site_id='default')
        device = get_device_by_name(controller, device_name)
        if not device:
            print(f"Device '{device_name}' not found.")
            sys.exit(1)

        if action == 'block':
            block_device(controller, device)
        elif action == 'unblock':
            unblock_device(controller, device)
        else:
            print(f"Invalid action: {action}. Use 'block' or 'unblock'.")
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage internet access for a specific device on the Unifi network.')
    parser.add_argument('device_name', type=str, help='The name of the device to manage')
    parser.add_argument('action', type=str, choices=['block', 'unblock'], help="Action to perform: 'block' or 'unblock'")
    args = parser.parse_args()
    main(args.device_name, args.action)
