import board
import busio
import digitalio
import usb_midi

import BartMIDI

import time

import adafruit_logging as logging
import board
import digitalio
import pwmio
import usb_midi
from analogio import AnalogIn

from BartMIDI import BartMIDI, KronosMessage
from util import print_uart

logger = logging.getLogger('test')

logger.setLevel(logging.INFO)


class Motor:
    def __init__(self, down_pin, up_pin, enable_pin):
        self._down = pwmio.PWMOut(down_pin, frequency=50_000, duty_cycle=0)
        self._up = pwmio.PWMOut(up_pin, frequency=50_000, duty_cycle=0)
        # self._enable = digitalio.DigitalInOut(enable_pin)

        # self._enable.direction = digitalio.Direction.OUTPUT
        # self._enable.value = True

        self.set_speed(100)

    @staticmethod
    def _percent_to_speed(speed_percent):
        max_speed = 65535
        min_speed = 40000
        range_speed = max_speed - min_speed
        return min_speed + (range_speed / 100) * speed_percent

    def set_speed(self, speed_percent):
        speed_percent = int(speed_percent)
        if speed_percent < 0 or speed_percent > 100:
            raise ValueError("Speed not percentage: ", speed_percent)
        u16_speed = int(self._percent_to_speed(speed_percent))
        return u16_speed
        # self._enable.duty_u16(u16_speed)

    def up(self, speed):
        self._down.duty_cycle = 0
        self._up.duty_cycle = self.set_speed(speed)

    def down(self, speed):
        self._down.duty_cycle = self.set_speed(speed)
        self._up.duty_cycle = 0

    def stop(self):
        self._down.duty_cycle = 0
        self._up.duty_cycle = 0


class Fader:
    def __init__(self, fader_pin, precision=7):
        self._potentiometer = AnalogIn(fader_pin)
        self._bit_precision = precision

    @property
    def value(self):
        return self._potentiometer.value >> 16 - self._bit_precision


class MotorisedFader:
    def __init__(self, motor, fader):
        self._motor = motor
        self._fader = fader
        self._p_value = 5

    def move_to(self, value, knob=False, direction=""):
        value = int(value)
        i = 0

        KP = 5

        reached = False
        move_motor_up = False
        move_motor_down = False

        motor_start_pos = fader1.value

        speed = 0

        while True:
            test_value = value if not knob else test_pot.value >> 16 - bit_precision
            fader_value = self._fader.value

            if fader_value < test_value - 1 and not reached:
                board_led.value = True
                move_motor_up = True
            elif fader_value > test_value + 1 and not reached:
                board_led.value = False
                move_motor_down = True
            else:
                reached = True

            if move_motor_up:
                error1 = fader_value - test_value
                speed = max(min(100, int(abs(error1 * KP))), 0)
                self._motor.set_speed(100)
                self._motor.up(speed)
                if fader_value >= test_value - 1:
                    self._motor.stop()
                    move_motor_up = False
            if move_motor_down:
                error1 = fader_value - test_value
                percentage1 = motor_start_pos - test_value
                speed = max(min(100, int(abs(error1 * KP))), 0)
                self._motor.set_speed(100)
                self._motor.down(speed)
                if fader_value <= test_value + 1:
                    self._motor.stop()
                    move_motor_down = False

            if reached:
                break

            if i % 5 == 0:
                print("%s | test %04d | fader %04d, speed %04d" % (
                    direction, test_value, fader_value, speed))
                i = 0

            i += 1
            time.sleep(clock_speed / 1000)


clock_speed = 10

bit_precision = 6

board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT

fader1 = Fader(board.A1, bit_precision)
fader2 = Fader(board.A0, bit_precision)
test_pot = AnalogIn(board.A2)

motor1 = Motor(up_pin=board.GP17,
               down_pin=board.GP16,
               enable_pin=board.GP0)
motor2 = Motor(up_pin=board.GP19,
               down_pin=board.GP18,
               enable_pin=board.GP1)

motofader = MotorisedFader(motor1, fader1)

board_led.value = False

print_uart("\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n")

time.sleep(3)

uart = busio.UART(tx=board.GP4, rx=board.GP5, baudrate=31250, timeout=0.0001)

print_uart(usb_midi.ports)
midi = BartMIDI(
    midi_in=uart, midi_out=usb_midi.ports[1]
)

print("Booting")

time.sleep(3)


def fader_to_kronos():
    last_value = 0
    while 1:
        a = fader1.value * 2
        if a + 2 < last_value or a - 2 > last_value:
            last_value = a
            print_uart(a)
            a = KronosMessage(fader=0, position=a)
            packet = a.to_bytearray()
            midi.send(packet)
        time.sleep(0.001)


def kronos_to_fader():
    while 1:
        packet = midi.receive()

        if packet is None:
            time.sleep(1)
            continue
        print("packet midi receive")

        postion = int(packet.VALUE_L)
        print("moving to: ", postion)
        motofader.move_to(postion / 2)
        time.sleep(0.025)


try:
    print("running kronos fader")
    kronos_to_fader()
except Exception as e:
    print(e)
    print("custom: ", e)
