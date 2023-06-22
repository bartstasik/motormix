import board
import digitalio
import pwmio
import time
import adafruit_midi
import usb_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

from analogio import AnalogIn

from BartMIDI import BartMIDI, KronosMessage

print(usb_midi.ports)
midi = BartMIDI(
    midi_in=usb_midi.ports[0], midi_out=usb_midi.ports[1]
)

print("Booting")
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

note_mapping = [
    ["C3", "C2"],
    ["D3", "D2"],
    ["E3", "E2"],
    ["F3", "F2"],
    ["G3", "G2"],
    ["A3", "A2"],
    ["B3", "B2"],
    ["C4", "C3"],
    ["G2", "G1"]
]


class Fader:
    def __init__(self, fader_pin, precision=7):
        self._potentiometer = AnalogIn(fader_pin)
        self._bit_precision = precision

    @property
    def value(self):
        return (self._potentiometer.value >> 16 - self._bit_precision) * 2


clock_speed = 10

bit_precision = 6

fader1 = Fader(board.A1, bit_precision)

time.sleep(3)

last_value = 0

while True:
    a = fader1.value
    if a + 2 < last_value or a - 2 > last_value:
        last_value = a
        print(a)
        a = KronosMessage(fader=0, position=a)
        packet = a.to_bytearray()
        midi.send(packet)
    time.sleep(0.001)
