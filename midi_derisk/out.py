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
port = 5
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


def change_ch_to(enable, channel):
    a = [[[[240, 66, 48, 104], 0]],
         [[[67, 4, channel - 1, 0], 0]],
         [[[14, 0, 0, 0], 14753]],
         [[[int(not enable), 247, 0, 0], 0]]]
    for i in a:
        midi_out.write(i)


def switch_program_page(page):
    """
    0: Timbre 1-8
    1: Timre 9-16
    7: Audio
    4: Ext
    5: KARMA
    6: Tone
    ?: EQ
    :param page:
    :return:
    """
    a = [[[[240, 66, 48, 104], 0]],
         [[[67, 27, 0, 0], 0]],
         [[[3, 0, 0, 0], 0]],
         [[[int(page), 247, 0, 0], 0]]]
    for i in a:
        midi_out.write(i)


def countdown():
    sleep(1)
    print(3)
    sleep(1)
    print(2)
    sleep(1)
    print(1)
    sleep(1)
    print("Now")


countdown()
while True:
    for j in range(1, 17):
        fader = j
        position = 69
        move_fader_to(position, j)
        print(j)
        sleep(.25)
#
# while True:
#     what = int(input("1: Fader,\n2: Channel en/disable\n3: Toggle timbre page\n\nWhat's it gonna be? "))
#     if what == 1:
#         fader = int(input("Which fader? "))
#         position = int(input("Where to? "))
#         countdown()
#         move_fader_to(position, fader)
#     if what == 2:
#         countdown()
#         for j in range(15, 17):
#             print("on")
#             change_ch_to(enable=True, channel=j)
#             sleep(1)
#             print("off")
#             change_ch_to(enable=False, channel=j)
#             sleep(1)
#             print("on")
#             change_ch_to(enable=True, channel=j)
#             sleep(1)
#             print("off")
#             change_ch_to(enable=False, channel=j)
#             sleep(1)
#     if what == 3:
#         countdown()
#         print("on")
#         for j in range(16):
#             print(j)
#             switch_program_page(j)
#             sleep(1)
