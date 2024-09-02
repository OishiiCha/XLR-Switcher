import board
import digitalio
import supervisor
import time

# Define relay pins for GP10 to GP13
relay_pins = {
    # LED Pins
    'GP6': digitalio.DigitalInOut(board.GP6),
    'GP7': digitalio.DigitalInOut(board.GP7),
    'GP8': digitalio.DigitalInOut(board.GP8),
    'GP9': digitalio.DigitalInOut(board.GP9),
    # XLR Pins H + C
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

        # Map relay pins (GP10-GP13) to LED pins (GP6-GP9)
        led_pin_map = {
            'GP10': 'GP6',
            'GP11': 'GP7',
            'GP12': 'GP8',
            'GP13': 'GP9'
        }
        
        # Validate pin name and action
        if pin_name in relay_pins and action in ['ON', 'OFF']:
            relay_pins[pin_name].value = (action == 'ON')
            if pin_name in led_pin_map:
                led_pin = led_pin_map[pin_name]
                relay_pins[led_pin].value = (action == 'ON')
            print(f"{pin_name} is now {'ON' if action == 'ON' else 'OFF'}")
        else:
            print("Invalid command. Use format 'GPxxON' or 'GPxxOFF'.")
    except Exception as e:
        print(f"Error: {e}. Command format should be 'GPxxON' or 'GPxxOFF'.")


while True:
    if supervisor.runtime.serial_bytes_available:
        command = input().strip()  # Read the command
        control_relay(command)
    time.sleep(0.01)  # Small delay to prevent excessive CPU usage


