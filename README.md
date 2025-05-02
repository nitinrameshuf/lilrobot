# lilrobot
Log path : /var/log/lilrobot

Communication Paths:
1) Command Center to Sentry (via Engine)
    - DC motor Commands
    - Servo Commands

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