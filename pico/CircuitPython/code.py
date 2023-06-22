import board
import digitalio
import pwmio
import time
import adafruit_midi
import usb_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
import pwmio
from analogio import AnalogIn

import adafruit_logging as logging

logger = logging.getLogger('test')

logger.setLevel(logging.INFO)


class Motor:
    def __init__(self, down_pin, up_pin, enable_pin):
        self._down = pwmio.PWMOut(down_pin, frequency=50_000, duty_cycle=0)
        self._up = pwmio.PWMOut(up_pin, frequency=50_000, duty_cycle=0)
        self._enable = digitalio.DigitalInOut(enable_pin)

        self._enable.direction = digitalio.Direction.OUTPUT
        self._enable.value = True

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

board_led.value = False

time.sleep(3)


def movetovalue(value, knob=False, direction=""):
    value = int(value)
    i = 0

    KP = 5

    reached1 = False
    reached2 = False
    move_motor1_up = False
    move_motor1_down = False
    move_motor2_up = False
    move_motor2_down = False

    motor1_start_pos = fader1.value
    motor2_start_pos = fader2.value

    speed1 = 0
    speed2 = 0

    while True:
        test_value = value if not knob else test_pot.value >> 16 - bit_precision
        fader1_value = fader1.value
        fader2_value = fader2.value

        if fader2_value < test_value - 1 and not reached2:
            board_led.value = True
            move_motor2_up = True
        elif fader2_value > test_value + 1 and not reached2:
            board_led.value = False
            move_motor2_down = True
        else:
            reached2 = True

        if fader1_value < test_value - 1 and not reached1:
            board_led.value = True
            move_motor1_up = True
        elif fader1_value > test_value + 1 and not reached1:
            board_led.value = False
            move_motor1_down = True
        else:
            reached1 = True

        if move_motor1_up:
            error1 = fader1_value - test_value
            speed1 = max(min(100, int(abs(error1 * KP))), 0)
            motor1.set_speed(100)
            motor1.up(speed1)
            if fader1_value >= test_value - 1:
                motor1.stop()
                move_motor1_up = False
        if move_motor1_down:
            error1 = fader1_value - test_value
            percentage1 = motor1_start_pos - test_value
            speed1 = max(min(100, int(abs(error1 * KP))), 0)
            motor1.set_speed(100)
            motor1.down(speed1)
            if fader1_value <= test_value + 1:
                motor1.stop()
                move_motor1_down = False

        if move_motor2_up:
            error2 = fader2_value - test_value
            speed2 = max(min(100, int(abs(error2 * KP))), 0)
            motor2.set_speed(speed2)
            motor2.up(speed2)
            if fader2_value >= test_value - 1:
                motor2.stop()
                move_motor2_up = False
        if move_motor2_down:
            error2 = fader2_value - test_value
            percentage2 = motor2_start_pos - test_value
            speed2 = max(min(100, int(abs(error2 * KP))), 0)
            motor2.set_speed(speed2)
            motor2.down(speed2)
            if fader2_value <= test_value + 1:
                motor2.stop()
                move_motor2_down = False

        if reached1 and reached2:
            break

        if i % 5 == 0:
            print("%s | t1 %04d | f1 %04d, s1 %04d | f2 %04d, s2 %04d" % (
                direction, test_value, fader1_value, speed1, fader2_value, speed2))
            i = 0

        i += 1
        time.sleep(clock_speed / 1000)


def test_analogaverage():
    i = 0
    analog_value_counter = 0
    analog_value = 0

    while True:
        test_value = test_pot.value
        analog_value_counter += test_value

        if i % 10 == 0:
            print(test_value >> 7, analog_value >> 7)

        if i % 10 == 0:
            analog_value = int(analog_value_counter / 10)
            analog_value_counter = 0
            i = 0

        i += 1
        time.sleep(1 / 1000)


def test_wave():
    while 1:
        for j in range(0, 63, 5):
            movetovalue(j)
            time.sleep(1 / 1000)
        for j in range(63, 0, -5):
            movetovalue(j)
            time.sleep(1 / 1000)


def test_backnforth():
    while 1:
        movetovalue(63, False, "up")
        movetovalue(0, False, "down")


def test_with_testpot():
    while 1:
        movetovalue(0, True)


test_with_testpot()
