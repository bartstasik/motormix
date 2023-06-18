import sys
import os
from time import sleep

import pygame as pg
import pygame.midi


def print_device_info():
    pygame.midi.init()
    _print_device_info()
    pygame.midi.quit()


def _print_device_info():
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print(
            "%2i: interface :%s:, name :%s:, opened :%s:  %s"
            % (i, interf, name, opened, in_out)
        )


stored_events = []


#                init
# =======================================
GRAND_PIANO = 0
CHURCH_ORGAN = 19
instrument = CHURCH_ORGAN
pygame.init()
pygame.midi.init()
port = 4
midi_out = pygame.midi.Output(port, 0)
midi_out.set_instrument(instrument)
print("using output_id :%s:" % port)


def input_main(device_id=None):
    pg.init()
    pg.fastevent.init()
    event_get = pg.fastevent.get
    event_post = pg.fastevent.post

    pygame.midi.init()

    _print_device_info()

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()
    else:
        input_id = device_id

    print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    pg.display.set_mode((1, 1))

    going = True
    while going:
        try:
            events = event_get()
            for e in events:
                if e.type in [pg.QUIT]:
                    going = False
                if e.type in [pg.KEYDOWN]:
                    going = False
                if e.type in [pygame.midi.MIDIIN]:
                    pass

            if i.poll():
                midi_events = i.read(1)
                if midi_events[0][0][0] == 248:
                    continue
                stored_events.append(midi_events)
                midi_out.write(midi_events)
                print(midi_events)
                # convert them into pygame events.
                midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

                for m_e in midi_evs:
                    event_post(m_e)
        except KeyboardInterrupt:
            break

    with open('your_file.txt', 'w') as f:
        for line in stored_events:
            f.write(f"{line}\n")

    del i
    pygame.midi.quit()


input_main(2)


# =======================================

def exit():
    global midi_out, music

    music = 0
    del midi_out
    pygame.midi.quit()
    pygame.quit()
    sys.exit()


CM = [74, 78, 81]
D = [74, 76, 81]
FM = [72, 76, 79]
screen = pygame.display.set_mode((400, 400))
music = 1

fader_move = []

# sleep(2)
#
# for i in stored_events:
#     fader_move.append(i)
#     midi_out.write(i)
#     sleep(0.25)


