from machine import Pin, lightsleep, PWM, ADC

clock_speed = 10

bit_precision = 7

board_led = Pin(25, Pin.OUT)

fader_1 = ADC(Pin(27))
fader_2 = ADC(Pin(26))
test_pot = ADC(Pin(28))

motor_1_a = Pin(16, Pin.OUT)
motor_1_b = Pin(17, Pin.OUT)
motor_2_a = Pin(18, Pin.OUT)
motor_2_b = Pin(19, Pin.OUT)

motor1 = (motor_1_a, motor_1_b)
motor2 = (motor_2_a, motor_2_b)

motor_1_en = PWM(Pin(0))
motor_2_en = PWM(Pin(1))

motor_1_en.freq(50_000)
motor_2_en.freq(50_000)

board_led.low()
motor_1_en.duty_u16(55000)
motor_2_en.duty_u16(55000)

motor_1_a.low()
motor_1_b.low()
motor_2_a.low()
motor_2_b.low()

lightsleep(3000)


def motor_up(motor: (PWM, PWM)):
    motor[0].low()
    motor[1].high()


def motor_down(motor: (PWM, PWM)):
    motor[0].high()
    motor[1].low()


def motor_stop(motor: (PWM, PWM)):
    motor[0].low()
    motor[1].low()


def f1_value():
    return fader_1.read_u16() >> 16 - bit_precision


def f2_value():
    return fader_2.read_u16() >> 16 - bit_precision


def test_backnforth():
    clock_speed = 10
    i = 0
    while 1:
        test_value = test_pot.read_u16() >> 16 - bit_precision
        if f2_value() < 5:
            # i=0
            board_led.high()
            motor_up(motor2)
        elif f2_value() == 127:
            board_led.low()
            motor_down(motor2)
        if f1_value() < 5:
            # i=0
            board_led.high()
            motor_up(motor1)
        elif f1_value() == 127:
            board_led.low()
            motor_down(motor1)

        i += 1
        if i % 10 == 0:
            print(i, f1_value(), f2_value(), test_value)
            i = 0
        lightsleep(clock_speed)


def test_movetospot():
    clock_speed = 10
    motor_1_en.duty_u16(65535)
    motor_2_en.duty_u16(65535)
    i = 0
    while 1:
        test_value = test_pot.read_u16() >> 16 - bit_precision
        if f2_value() < test_value - 1:
            board_led.high()
            motor_up(motor2)
            while f2_value() < test_value - 1:
                pass
            motor_stop(motor2)
        if f2_value() > test_value + 1:
            board_led.low()
            motor_down(motor2)
            while f2_value() > test_value + 1:
                pass
            motor_stop(motor2)

        if f1_value() < test_value - 1:
            board_led.high()
            motor_up(motor1)
            while f1_value() < test_value - 1:
                pass
            motor_stop(motor1)
        if f1_value() > test_value + 1:
            board_led.low()
            motor_down(motor1)
            while f1_value() > test_value + 1:
                pass
            motor_stop(motor1)

        i += 1
        if i % 10 == 0:
            print(i, f1_value(), f2_value(), test_value)
            i = 0
        lightsleep(clock_speed)


def test_movetovalue():
    value = int(127 / 2)
    i = 0

    motor_1_en.duty_u16(65535)
    motor_2_en.duty_u16(65535)
    reached1 = False
    reached2 = False
    move_motor1_up = False
    move_motor1_down = False
    move_motor2_up = False
    move_motor2_down = False

    while True:
        test_value = value

        if f2_value() < test_value - 1 and not reached1:
            board_led.high()
            move_motor2_up = True
        elif f2_value() > test_value + 1 and not reached1:
            board_led.low()
            move_motor2_down = True
        else:
            reached1 = True

        if f1_value() < test_value - 1 and not reached2:
            board_led.high()
            move_motor1_up = True
        elif f1_value() > test_value + 1 and not reached2:
            board_led.low()
            move_motor1_down = True
        else:
            reached2 = True

        if move_motor1_up:
            motor_up(motor1)
            if f1_value() >= test_value - 1:
                motor_stop(motor1)
                move_motor1_up = False
        if move_motor1_down:
            motor_down(motor1)
            if f1_value() <= test_value + 1:
                motor_stop(motor1)
                move_motor1_down = False

        if move_motor2_up:
            motor_up(motor2)
            if f2_value() >= test_value - 1:
                motor_stop(motor2)
                move_motor2_up = False
        if move_motor2_down:
            motor_down(motor2)
            if f2_value() <= test_value + 1:
                motor_stop(motor2)
                move_motor2_down = False
        i += 1
        if i % 10 == 0:
            print(i, f1_value(), f2_value(), test_value, reached1, reached2)
            i = 0
        lightsleep(clock_speed)


test_backnforth()

