import pygame
import pygame.midi
from time import sleep
import sys

#                init
# =======================================
GRAND_PIANO = 0
CHURCH_ORGAN = 19
instrument = CHURCH_ORGAN
pygame.init()
pygame.midi.init()
port = 3
midi_out = pygame.midi.Output(port, 0)
midi_out.set_instrument(instrument)
print("using output_id :%s:" % port)


# =======================================

def exit():
    global midi_out, music

    music = 0
    del midi_out
    pygame.midi.quit()
    pygame.quit()
    sys.exit()


screen = pygame.display.set_mode((400, 400))
music = 1


def move_fader_to(pos, fader):
    # [[status, <data1>, <data2>, <data3>], timestamp]
    a = [[[[240, 66, 48, 104], 0]],
         [[[67, 4, fader - 1, 0], 0]],
         [[[2, 0, 0, 0], 0]],
         [[[pos, 247, 0, 0], 0]]]
    for i in a:
        midi_out.write(i)


while True:
    fader = int(input("Which fader?\n"))
    position = int(input("Where to?\n"))
    sleep(1)
    print(3)
    sleep(1)
    print(2)
    sleep(1)
    print(1)
    sleep(1)
    print("Now")
    move_fader_to(position, fader)
