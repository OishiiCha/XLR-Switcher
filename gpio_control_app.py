import serial
import serial.tools.list_ports
import threading
import time
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from qt_toggle import QToggle
import os
import sys

class GPIOControlApp(QtWidgets.QWidget):
    def __init__(self):
        """Initialize the GPIO Control application and start the connection thread."""
        super().__init__()
        self.ser = None
        self.device_connected = False
        self.notes = {}
        self.init_ui()
        self.load_notes()
        self.start_connection_thread()

    def init_ui(self):
        """Set up the user interface."""
        self.setWindowTitle('XLR Switch')
        self.setGeometry(100, 100, 600, 300)  # Adjusted height for layout
        self.setFixedSize(self.size())  # Make the window non-resizable

        # Set the window icon
        if getattr(sys, 'frozen', False):  # Check if running in a PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, 'images', 'logo.ico')

            
        self.setWindowIcon(QIcon(icon_path))

        # Create a grid layout with 4 columns and 3 rows
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(10)

        self.switches, self.circles, self.button_states = {}, {}, {}
        self.note_inputs = {}

        for index, gpio in enumerate(range(10, 14)):
            # Calculate the column and row positions
            col = index
            row_text = 0
            row_switch = 1
            row_circle = 2
            row_note = 3

            label = QtWidgets.QLabel(f"Input {gpio - 9}")  
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(14)  # Set font size
            font.setBold(True)     # Set font to bold
            label.setFont(font)
            grid_layout.addWidget(label, row_text, col, Qt.AlignmentFlag.AlignCenter)

            # Create and add the toggle switch
            toggle = QToggle()
            toggle.setFixedSize(120, 30)
            toggle.toggled.connect(lambda checked, g=gpio: self.toggle_gpio(g))
            grid_layout.addWidget(toggle, row_switch, col, Qt.AlignmentFlag.AlignCenter)
            self.switches[gpio] = toggle

            # Create and add the circle indicator with updated size
            circle = QtWidgets.QLabel()
            circle.setFixedSize(30, 30)  # Increased size for the circle
            circle.setStyleSheet("background-color: white; border: 1px solid black; border-radius: 15px;")
            grid_layout.addWidget(circle, row_circle, col, Qt.AlignmentFlag.AlignCenter)
            self.circles[gpio] = circle
            self.button_states[gpio] = 'OFF'
            
            # Add a note input field
            note_input = QtWidgets.QLineEdit()
            note_input.setPlaceholderText("Enter Description")
            note_input.setReadOnly(True)
            font2 = QFont()
            font2.setPointSize(10)
            font2.setBold(True) 
            note_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            note_input.setFont(font2)
            grid_layout.addWidget(note_input, row_note, col, Qt.AlignmentFlag.AlignCenter)
            self.note_inputs[gpio] = note_input

        # Add buttons to mute/unmute all switches
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
                # Add Edit button
        self.edit_button = QtWidgets.QPushButton("Edit")
        self.edit_button.setFixedSize(120, 40)  # Make the button larger
        self.edit_button.setFont(QFont('Arial', 12, QFont.Weight.Bold))  # Bold text
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        button_layout.addWidget(self.edit_button)
        
        # Button to mute all switches
        self.mute_button = QtWidgets.QPushButton("Mute All")
        self.mute_button.setFixedSize(120, 40)  # Make the button larger
        self.mute_button.setFont(QFont('Arial', 12, QFont.Weight.Bold))  # Bold text
        self.mute_button.setStyleSheet("background-color: #D3D3D3; color: black;")  # Light grey background
        self.mute_button.clicked.connect(self.turn_all_off)
        button_layout.addWidget(self.mute_button)

        # Button to unmute all switches
        self.unmute_button = QtWidgets.QPushButton("Unmute All")
        self.unmute_button.setFixedSize(120, 40)  # Make the button larger
        self.unmute_button.setFont(QFont('Arial', 12, QFont.Weight.Bold))  # Bold text
        self.unmute_button.setStyleSheet("background-color: #D3D3D3; color: black;")  # Light grey background
        self.unmute_button.clicked.connect(self.turn_all_on)
        button_layout.addWidget(self.unmute_button)

        grid_layout.addLayout(button_layout, 4, 0, 1, 4)  # Span across all columns

        self.setLayout(grid_layout)
        self.setStyleSheet("background-color: #333; color: white;")

        # Initially disable all controls
        self.set_controls_enabled(False)

    def start_connection_thread(self):
        """Start the thread that manages the serial connection."""
        self.connection_thread = threading.Thread(target=self.manage_connection, daemon=True)
        self.connection_thread.start()
    
    def toggle_edit_mode(self):
        """Toggle between editing and saving mode."""
        is_editing = self.edit_button.text() == "Edit"
        for note_input in self.note_inputs.values():
            note_input.setReadOnly(not is_editing)
        if is_editing:
            self.edit_button.setText("Save")
        else:
            self.save_notes()
            self.edit_button.setText("Edit")

    def load_notes(self):
        """Load notes from the .conf file."""
        if os.path.exists("notes.conf"):
            with open("notes.conf", "r") as file:
                for line in file:
                    gpio, note = line.strip().split(":", 1)
                    gpio = int(gpio)
                    self.notes[gpio] = note
                    if gpio in self.note_inputs:
                        self.note_inputs[gpio].setText(note)
        else:
            # Create the file if it does not exist
            with open("notes.conf", "w") as file:
                pass

    def save_notes(self):
        """Save notes to the .conf file."""
        with open("notes.conf", "w") as file:
            for gpio, note_input in self.note_inputs.items():
                note = note_input.text()
                self.notes[gpio] = note
                file.write(f"{gpio}:{note}\n")

    def start_connection_thread(self):
        """Start the thread that manages the serial connection."""
        self.connection_thread = threading.Thread(target=self.manage_connection, daemon=True)
        self.connection_thread.start()

    
    def manage_connection(self):
        """Manage the connection to the serial device, handling reconnections."""
        while True:
            if not self.ser:
                self.find_pico_port()
            else:
                try:
                    print("Sending PING command...")
                    self.ser.write(b'PING\r')
                    self.ser.flush()
                    response = self.ser.read_until().strip()
                    print(f"Received response: {response}")
                    if not response:
                        raise serial.SerialException("No response from device")
                except serial.SerialException as e:
                    print(f"Serial exception: {e}. Reconnecting...")
                    self.update_status("Device disconnected. Reconnecting...")
                    self.ser.close()
                    self.ser = None
                    self.device_connected = False
                    self.set_controls_enabled(False)
                except OSError as e:
                    print(f"OS error: {e}. Reconnecting...")
                    self.update_status("Device disconnected. Reconnecting...")
                    self.ser.close()
                    self.ser = None
                    self.device_connected = False
                    self.set_controls_enabled(False)

            time.sleep(2)
        
    def find_pico_port(self):
        """Find and connect to the available serial port."""
        self.update_status("Connecting...")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                print(f"Trying port {port.device}")
                s = serial.Serial(port.device, 9600, timeout=1)
                time.sleep(2)
                s.write(b'PING\r')
                s.flush()
                response = s.read_until().strip()
                if response:
                    print(f"Connected to {port.device}")
                    self.ser = s
                    self.device_connected = True
                    self.update_status(f"Connected to {port.device}")
                    self.set_controls_enabled(True)
                    return
            except (OSError, serial.SerialException) as e:
                print(f"Error with port {port.device}: {e}")
                continue

    def send_command(self, gpio_number, state):
        """Send a command to the GPIO device."""
        if not self.ser:
            print("No device connected.")
            return
        command = f"GP{gpio_number}{state}\r".encode('utf-8')
        print(f"Sending command: {command.decode('utf-8').strip()}")
        self.ser.write(command)
        self.ser.flush()

    def toggle_gpio(self, gpio_number):
        """Toggle the GPIO pin and update the UI accordingly."""
        current_state = self.button_states[gpio_number]
        new_state = 'OFF' if current_state == 'ON' else 'ON'
        self.send_command(gpio_number, new_state)
        self.button_states[gpio_number] = new_state
        self.switches[gpio_number].setChecked(new_state == 'ON')
        self.update_circle(gpio_number, new_state)

    def update_circle(self, gpio_number, state):
        """Update the color of the indicator circle based on the state."""
        color = 'red' if state == 'ON' else 'white'
        self.circles[gpio_number].setStyleSheet(f"background-color: {color}; border: 1px solid black; border-radius: 15px;")

    def update_status(self, message):
        """Update the status label with a message and window title."""
        self.setWindowTitle(f'XLR Switch - {message}')
        self.update_button_styles()

    def closeEvent(self, event):
        """Handle application close events."""
        if self.ser:
            for gpio in range(10, 14):
                self.send_command(gpio, 'OFF')
            self.ser.close()
        event.accept()

    def turn_all_on(self):
        """Turn all GPIO switches on."""
        for gpio in self.switches:
            self.send_command(gpio, 'ON')
            self.switches[gpio].setChecked(True)
            self.button_states[gpio] = 'ON'
            self.update_circle(gpio, 'ON')

    def turn_all_off(self):
        """Turn all GPIO switches off."""
        for gpio in self.switches:
            self.send_command(gpio, 'OFF')
            self.switches[gpio].setChecked(False)
            self.button_states[gpio] = 'OFF'
            self.update_circle(gpio, 'OFF')

    def set_controls_enabled(self, enabled):
        """Enable or disable all controls based on connection status."""
        for toggle in self.switches.values():
            toggle.setEnabled(enabled)
        self.mute_button.setEnabled(enabled)
        self.unmute_button.setEnabled(enabled)
        self.update_button_styles()

    def update_button_styles(self):
        """Update the styles of the mute and unmute buttons based on connection status."""
        if self.device_connected:
            self.mute_button.setStyleSheet("background-color: #B22222; color: white;")  # Dark red background
            self.unmute_button.setStyleSheet("background-color: #228B22; color: white;")  # Dark green background
        else:
            self.mute_button.setStyleSheet("background-color: #494A4A; color: black;")  # Light grey background
            self.unmute_button.setStyleSheet("background-color: #494A4A; color: black;")  # Light grey background

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = GPIOControlApp()
    window.show()
    app.exec()

