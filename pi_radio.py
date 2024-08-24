import RPi.GPIO as GPIO
from nrf24 import NRF24
import time

GPIO.setmode(GPIO.BCM)

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 8)

radio.setPayloadSize(32)
radio.setChannel(0x76)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)

radio.openWritingPipe(pipes[1])
radio.openReadingPipe(1, pipes[0])
radio.stopListening()

while True:
    message = list("Hello from Pi")
    while len(message) < 32:
        message.append(0)

    radio.write(message)
    print("Sent: {}".format(message))
    time.sleep(1)
