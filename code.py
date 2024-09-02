# For CircuitPython

import board
import digitalio
import supervisor
import time

# Define relay pins for GP10 to GP13
relay_pins = {
    'GP10': digitalio.DigitalInOut(board.GP10),
    'GP11': digitalio.DigitalInOut(board.GP11),
    'GP12': digitalio.DigitalInOut(board.GP12),
    'GP13': digitalio.DigitalInOut(board.GP13)
}

# Initialize relay pins as outputs
for pin in relay_pins.values():
    pin.direction = digitalio.Direction.OUTPUT

def control_relay(command):
    try:
        # Extract pin and action from command
        pin_name = command[:4]  # The first 4 characters (e.g., 'GP10')
        action = command[4:]    # The last 2 characters (e.g., 'ON' or 'OFF')

        # Validate pin name and action
        if pin_name in relay_pins and action in ['ON', 'OFF']:
            relay_pins[pin_name].value = (action == 'ON')
            print(f"{pin_name} is now {'ON' if action == 'ON' else 'OFF'}")
        else:
            print("Invalid command. Use format 'GPxxON' or 'GPxxOFF'.")
    except Exception as e:
        print(f"Error: {e}. Command format should be 'GPxxON' or 'GPxxOFF'.")

while True:
    if supervisor.runtime.serial_bytes_available:
        command = input().strip()  # Read the command
        control_relay(command)
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage

