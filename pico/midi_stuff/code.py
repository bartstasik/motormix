import board
import digitalio
import pwmio
import time
import adafruit_midi
import usb_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

from BartMIDI import BartMIDI

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

# while True:
#     ix = 0
#
#     print("note %d started" % ix)
#     led.value = True
#     midi.send([NoteOn(a, 60) for a in note_mapping[ix]])
#     time.sleep(1)
#
#     print("note %d stopped" % ix)
#     led.value = False
#     midi.send([NoteOff(a, 0) for a in note_mapping[ix]])
#     time.sleep(1)

# while True:
#     # print("sending")
#     # msg = midi.send(msg=b'\xf0B0hC\x04\x01\x00\x02\x00\x00\x00E\xf7')
#     # time.sleep(1)
#     msg, buffer, channel = midi.receive()
#     if msg is None:
#         continue
#     print(msg, buffer, channel)
#
#     with open("/recorded_data.csv", "a+") as f:
#         f.write(f"{buffer}\n")

    # midi.send(msg)
    # print(msg)
    # time.sleep(1)
    # print(msg, msg.__str__, msg.status)

with open("/recorded_data.csv", "r") as f:
    lines = f.readlines()

    while True:
        for i in lines:
            j = i.strip()
            while j[-1] == ",":
                j = j[:-1]
            buffer = eval(j)
            print(buffer)
            midi.send(buffer)
            time.sleep(0.025)
        time.sleep(2)

