from machine import Pin, lightsleep, PWM, ADC


class Motor:
    def __init__(self, down_pin, up_pin, enable_pin):
        self._down = PWM(Pin(down_pin))
        self._up = PWM(Pin(up_pin))
        self._enable = Pin(enable_pin)

        self._down.freq(50_000)
        self._up.freq(50_000)
        self.set_speed(100)
        self._down.duty_u16(0)
        self._up.duty_u16(0)
        self._enable.high()

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
        self._down.duty_u16(0)
        self._up.duty_u16(self.set_speed(speed))

    def down(self, speed):
        self._down.duty_u16(self.set_speed(speed))
        self._up.duty_u16(0)

    def stop(self):
        self._down.duty_u16(0)
        self._up.duty_u16(0)


class Fader:
    def __init__(self, fader_pin, precision=7):
        self._potentiometer = ADC(Pin(fader_pin))
        self._bit_precision = precision

    @property
    def value(self):
        return self._potentiometer.read_u16() >> 16 - self._bit_precision


clock_speed = 10

bit_precision = 6

board_led = Pin(25, Pin.OUT)

fader1 = Fader(27, bit_precision)
fader2 = Fader(26, bit_precision)
test_pot = ADC(Pin(28))

motor1 = Motor(up_pin=17,
               down_pin=16,
               enable_pin=0)
motor2 = Motor(up_pin=19,
               down_pin=18,
               enable_pin=1)

board_led.low()

lightsleep(3000)


def movetovalue(value, knob=False):
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
        test_value = value if not knob else test_pot.read_u16() >> 16 - bit_precision
        fader1_value = fader1.value
        fader2_value = fader2.value

        if fader2_value < test_value - 1 and not reached2:
            board_led.high()
            move_motor2_up = True
        elif fader2_value > test_value + 1 and not reached2:
            board_led.low()
            move_motor2_down = True
        else:
            reached2 = True

        if fader1_value < test_value - 1 and not reached1:
            board_led.high()
            move_motor1_up = True
        elif fader1_value > test_value + 1 and not reached1:
            board_led.low()
            move_motor1_down = True
        else:
            reached1 = True

        if move_motor1_up:
            error1 = fader1_value - test_value
            speed1 = max(min(100, int(abs(error1 * KP))), 0)
            motor1.set_speed(speed1)
            motor1.up(speed1)
            if fader1_value >= test_value - 1:
                motor1.stop()
                move_motor1_up = False
        if move_motor1_down:
            error1 = fader1_value - test_value
            percentage1 = motor1_start_pos - test_value
            speed1 = max(min(100, int(abs(error1 * KP))), 0)
            motor1.set_speed(speed1)
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
            print("up | %04d | %04d, %04d | %04d, %04d" % (test_value, fader1_value, speed1, fader2_value, speed2))
            i = 0

        i += 1
        lightsleep(clock_speed)


def test_movetorichard(value):
    # The main change here is that I'm assuming if the motor is already on there's
    # no harm in turning it on
    # again, and ditto for when it's off, so there's no need to track state of whether
    # we have started or not, which simplifies everything a lot.
    #
    # If you *do* need to track the state, then probably you should implement a
    # simple state machine,
    # which I guess is what ChatGPT did, although you could perhaps do it nicer
    # using enums rather than booleans.

    reached1 = False
    reached2 = False

    # probably want to check reached1 and reached2 rather than loop forever, i.e.
    # while not (reached1 and reached2):
    while not (reached1 and reached2):
        test_value = value  # test_pot.read_u16() >> 9
        fader1_value = fader1.value
        fader2_value = fader2.value
        # You should probably copy the readings into variables so they don't change
        # during the loop, i.e.:
        # f2_value = f2_value()
        # f1_value = f1_value()

        # Don't think necessary to check reached1, but to eliminate possibly of motor
        # turning back on because it's drifted or something could do it like this here:
        if not reached1:
            if fader2_value < test_value - 1:
                board_led.high()
                motor2.up(100)
            elif fader2_value > test_value + 1:
                board_led.low()
                motor2.down(100)
            else:
                motor2.stop()
                reached1 = True

        if not reached2:
            if fader1_value < test_value - 1:
                board_led.high()  # seems to be using same LED for two purposes at once?
                motor1.up(100)
            elif fader1_value > test_value + 1:
                board_led.low()
                motor1.down(100)
            else:
                motor1.stop()
                reached2 = True

        lightsleep(clock_speed)


def test_analogaverage():
    i = 0
    analog_value_counter = 0
    analog_value = 0

    while True:
        test_value = test_pot.read_u16()
        analog_value_counter += test_value

        if i % 10 == 0:
            print(test_value >> 7, analog_value >> 7)

        if i % 10 == 0:
            analog_value = int(analog_value_counter / 10)
            analog_value_counter = 0
            i = 0

        i += 1
        lightsleep(1)


def test_wave():
    while 1:
        for j in range(0, 63, 1):
            movetovalue(j)
            lightsleep(1)
        for j in range(63, 0, -1):
            movetovalue(j)
            lightsleep(1)


def test_backnforth():
    while 1:
        movetovalue(127, True)
        movetovalue(0, True)


test_wave()
