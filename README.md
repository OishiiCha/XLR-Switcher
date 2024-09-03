# XLR Switcher

Currently in progress application which uses a RP2040 chip along with relays to switch on and off XLR inputs from a PC

There are no current plans to change this to run on macOS or Linux based systems, however a simple flask server could have similar functionality so could be run from something as simple as a Raspberry Pi and then remotely controlled. 
However for this type of device, it may not be worth doing that, you may instead want to build a DSP to have that functionality.

The app will auto detect the com which the device is connected to, if it is not detecting the pico still, disconnect the pico, then close any program that may be using it such as Thonny and connect the Pico again.

### Generating the .exe File
```
pyinstaller --clean --onefile --noconsole --icon=images/logo.ico --add-data "images/logo.ico;images" main.py --name "XLR Switcher"
```

## Example 3D Printed Box

![drawio xlrbox](https://github.com/user-attachments/assets/6e8eabfc-940a-495b-8606-ca7b54af6004)

## Software
![image](https://github.com/user-attachments/assets/7ddc317c-d209-4e54-baa2-9902061662cb)

## Example config
![image](https://github.com/user-attachments/assets/b4e4beaf-83d5-4a29-8fc9-3464d575df2a)
