import argparse
import sys
import os
import logging
from dotenv import load_dotenv
from pyunifi.controller import Controller

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Unifi Controller Config from Environment Variables
UNIFI_HOST = os.getenv('UNIFI_HOST', '192.168.1.1')  # Unifi Controller's IP address
UNIFI_USERNAME = os.getenv('UNIFI_USERNAME', 'admin')  # Unifi Controller username
UNIFI_PASSWORD = os.getenv('UNIFI_PASSWORD', 'password')  # Unifi Controller password
UNIFI_PORT = int(os.getenv('UNIFI_PORT', 8443))
UNIFI_VERSION = os.getenv('UNIFI_VERSION', 'UDMP-unifiOS')  # Version for UDM Pro
UNIFI_VERIFY_SSL = os.getenv('UNIFI_VERIFY_SSL', 'false').lower() in ['true', '1', 't']


def get_device_by_name(controller, device_name):
    logging.info(f"Looking up device by name: {device_name}")
    devices = controller.get_clients()
    for device in devices:
        if device.get('hostname', '').lower() == device_name.lower():
            logging.info(f"Device found: {device}")
            return device
    logging.warning(f"Device '{device_name}' not found, retrying with lowercase MAC address")
    for device in devices:
        if device.get('mac', '').lower() == device_name.lower():
            logging.info(f"Device found by MAC address: {device}")
            return device
    logging.warning(f"Device '{device_name}' not found")
    return None


def get_blocked_device(controller, mac_address):
    logging.info(f"Looking up blocked device by MAC address: {mac_address}")
    try:
        blocked_device = controller.get_client(mac_address)
        if blocked_device and blocked_device.get('blocked', False):
            logging.info(f"Blocked device found: {blocked_device}")
            return blocked_device
    except Exception as e:
        logging.warning(f"Could not get client by MAC address: {e}")
    logging.warning(f"Blocked device with MAC address '{mac_address}' not found")
    return None


def block_device(controller, device):
    logging.info(f"Attempting to block device: {device}")
    mac_address = device.get('mac')
    if not mac_address:
        logging.error("Device MAC address not found")
        raise ValueError("Device MAC address not found")

    # Check if the device is already blocked
    logging.info(f"Checking if device {mac_address} is already blocked")
    clients = controller.get_clients()
    for client in clients:
        if client.get('mac') == mac_address:
            if client.get('blocked', False):
                logging.error(f"Device {device['hostname']} ({mac_address}) is already blocked")
                print(f"Error: Device {device['hostname']} ({mac_address}) is already blocked.")
                sys.exit(1)
            else:
                # Enable the existing rule
                logging.info(f"Re-blocking device {device['hostname']} ({mac_address})")
                controller.block_client(mac_address)
                print(f"Internet access re-disabled for device {device['hostname']} ({mac_address})")
                return

    # Block the device using the API
    logging.info(f"Blocking device {device['hostname']} ({mac_address})")
    controller.block_client(mac_address)
    print(f"Internet access disabled for device {device['hostname']} ({mac_address})")


def unblock_device(controller, device):
    logging.info(f"Attempting to unblock device: {device}")
    mac_address = device.get('mac')
    if not mac_address:
        logging.error("Device MAC address not found")
        raise ValueError("Device MAC address not found")

    # Check if the device is currently blocked
    blocked_device = get_blocked_device(controller, mac_address)
    if blocked_device:
        # Unblock the device using the API
        logging.info(f"Unblocking device with MAC address {mac_address}")
        controller.unblock_client(mac_address)
        print(f"Internet access enabled for device with MAC address {mac_address}")
        return

    logging.error(f"No blocking rule found for device with MAC address '{mac_address}'")
    print(f"Error: No blocking rule found for device with MAC address '{mac_address}'")
    sys.exit(1)


def main(device_name, action):
    logging.info(f"Starting Unifi Device Internet Access Manager with device '{device_name}' and action '{action}'")
    try:
        logging.info("Connecting to Unifi Controller")
        controller = Controller(UNIFI_HOST, UNIFI_USERNAME, UNIFI_PASSWORD, UNIFI_PORT, version=UNIFI_VERSION, site_id='default', ssl_verify=UNIFI_VERIFY_SSL)
        device = get_device_by_name(controller, device_name)
        if not device:
            logging.error(f"Device '{device_name}' not found")
            print(f"Device '{device_name}' not found.")
            sys.exit(1)

        if action == 'block':
            block_device(controller, device)
        elif action == 'unblock':
            unblock_device(controller, device)
        else:
            logging.error(f"Invalid action: {action}")
            print(f"Invalid action: {action}. Use 'block' or 'unblock'.")
            sys.exit(1)
    except Exception as e:
        logging.exception("An error occurred")
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage internet access for a specific device on the Unifi network.')
    parser.add_argument('device_name', type=str, help='The name of the device to manage')
    parser.add_argument('action', type=str, choices=['block', 'unblock'], help="Action to perform: 'block' or 'unblock'")
    args = parser.parse_args()
    main(args.device_name, args.action)
