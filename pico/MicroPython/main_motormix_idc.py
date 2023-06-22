from machine import Pin, lightsleep

# Shift every 2 secs
# Flip direction every 1 sec
# Move each channel up and down

clock_speed = 2000

board_led = Pin(25, Pin.OUT)

shift_data = Pin(15, Pin.OUT)
shift_sck = Pin(14, Pin.OUT)
shift_rck = Pin(13, Pin.OUT)

# Active Low
plx_s0 = Pin(18, Pin.OUT)
plx_s1 = Pin(19, Pin.OUT)
plx_s2 = Pin(20, Pin.OUT)
com_io = Pin(21, Pin.OUT)

board_led.low()
shift_sck.low()
shift_rck.low()
shift_data.high()
plx_s0.high()
plx_s1.high()
plx_s2.high()
com_io.low()

lightsleep(3000)

i = 0

plx_s0.low()
plx_s1.low()
plx_s2.low()

while 1:
    if i == 0:
        shift_data.low()

    plx_s0.value(not (i & (1 << 0)))
    plx_s1.value(not (i & (1 << 1)))
    plx_s2.value(not (i & (1 << 2)))

    com_io.low()

    board_led.high()
    shift_sck.high()
    shift_rck.high()

    lightsleep(500)

    shift_sck.low()
    shift_rck.low()
    shift_data.high()
    board_led.low()

    lightsleep(500)

    com_io.high()

    lightsleep(1000)

    i += 1
    i &= 0x7