# lilrobot
Log path : /var/log/lilrobot

Function Mapping:
1) Sentry
    - Command & Response
        - Poll for new commands
    - Servo Control
        - Poll the serial for 

Communication Flows:
1) Command Center to Sentry (via Engine)
    - DC motor Commands
    - Servo Commands
        -  Engine_Command:Sentry_Command:Servo_Number:Servo_Angle (Example: S:1:120)

2) Command Center to Engine
    - Terrain modes
    - AI modes
    - Voice Commands

3) Engine to Command Center
    - Logs
    - Image data (RGB Frames + Point Clouds + Depth Maps)
    - Motor Metrics (Speed, Distance travelled)
    - Servo Positions
    - Battery Level
    - CPU Usage (Compute power, Voltage, Amp)
    - Error messages

Serial Formats
    - COMMAND:ARG1:ARG2:...ARGN
    - Example: S:1:120


#My_Notes
1) Resizing partitions in SD cards:
sudo apt update
sudo apt install cloud-guest-utils
sudo parted /dev/mmcblk0 print
sudo growpart /dev/mmcblk0 1
sudo resize2fs /dev/mmcblk0p1
df -h /
Check the partition name correctly before running.
