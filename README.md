# Unifi Device Internet Access Manager

This script allows you to manage internet access for specific devices on your Unifi network. It uses the Unifi Controller API to block or unblock devices by creating or disabling firewall rules based on their MAC address.

## Prerequisites

- Python 3.6 or newer
- Install the required dependencies using pip:
  ```bash
  pip install pyunifi
  ```
- Ensure you have appropriate access to the Unifi Controller (e.g., username and password with sufficient privileges).

## Running the Application with `uv`

To run the application, you can use the `uv` command. Here is a concrete example of how to use `uv` to run the script:

1. Install `uv` using `pip` (if you haven't done so already):
   ```bash
   pip install uv
   ```

2. Run the script using `uv`:
   ```bash
   uv python unifi_device_blocker.py <device_name> <action>
   ```

   For example, to block a device named "laptop-123":
   ```bash
   uv python unifi_device_blocker.py laptop-123 block
   ```
   To unblock the same device:
   ```bash
   uv python unifi_device_blocker.py laptop-123 unblock
   ```

## Input Arguments

The script takes the following input arguments:

1. `device_name` (required): The name of the device to manage. This should match the hostname of the device on your Unifi network.
2. `action` (required): The action to perform on the device. You can choose between:
   - `block`: Block the device from accessing the internet.
   - `unblock`: Unblock the device, restoring its internet access.

## Required Environment Variables

The script uses the following environment variables to configure access to the Unifi Controller:

1. `UNIFI_HOST` (required): The IP address of your Unifi Controller. For example: `192.168.1.1`
2. `UNIFI_USERNAME` (required): The username used to access the Unifi Controller.
3. `UNIFI_PASSWORD` (required): The password associated with the `UNIFI_USERNAME`.
4. `UNIFI_PORT` (optional): The port used to connect to the Unifi Controller. Defaults to `8443` if not provided.
5. `UNIFI_VERSION` (optional): The version of the Unifi Controller. Defaults to `UDMP-unifiOS` for Unifi Dream Machine Pro (UDM Pro). You may need to adjust this depending on your specific setup.

To set these environment variables, you can use the following commands:

```bash
export UNIFI_HOST='192.168.1.1'
export UNIFI_USERNAME='your_username'
export UNIFI_PASSWORD='your_password'
export UNIFI_PORT='8443'  # Optional
export UNIFI_VERSION='UDMP-unifiOS'  # Optional
```

## Error Handling

The script includes error handling for the following scenarios:

- If the device cannot be found, the script will print an error message and exit.
- If the device is already blocked, the script will print an error and exit without duplicating the rule.
- If the device is not currently blocked when trying to unblock, the script will print an error and exit.

## Example Usage

### Blocking a Device

To block a device named "smartphone-456":
```bash
uv python unifi_device_blocker.py smartphone-456 block
```

### Unblocking a Device

To unblock the same device:
```bash
uv python unifi_device_blocker.py smartphone-456 unblock
```

## Notes

- Ensure that the Unifi Controller API credentials have sufficient permissions to modify client settings.
- Make sure that the device name (`device_name`) matches the hostname as seen in the Unifi Controller, otherwise the script may not find the device.
- Use environment variables to keep your credentials secure and avoid hardcoding sensitive information into the script.

## License

This project is licensed under the GNUv3 License. Feel free to modify and use it as needed.

## Support

If you encounter any issues or have questions about the script, feel free to reach out or open an issue on the project's repository.

