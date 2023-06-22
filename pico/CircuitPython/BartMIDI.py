import adafruit_midi
import usb_midi
from adafruit_midi.midi_message import MIDIUnknownEvent, MIDIBadEvent, channel_filter, MIDIMessage

import time


class BartMessage(adafruit_midi.MIDIMessage):
    # pylint: disable=too-many-locals,too-many-branches
    @classmethod
    def from_message_bytes(cls, midibytes, channel_in):
        """Create an appropriate object of the correct class for the
        first message found in some MIDI bytes filtered by channel_in.

        Returns (messageobject, endplusone, skipped)
        or for no messages, partial messages or messages for other channels
        (None, endplusone, skipped).
        """
        endidx = len(midibytes) - 1
        skipped = 0
        preamble = True

        msgstartidx = 0
        msgendidxplusone = 0
        while True:
            msg = None
            # Look for a status byte
            # Second rule of the MIDI club is status bytes have MSB set
            while msgstartidx <= endidx and not midibytes[msgstartidx] & 0x80:
                msgstartidx += 1
                if preamble:
                    skipped += 1
            preamble = False

            # Either no message or a partial one
            if msgstartidx > endidx:
                return (None, endidx + 1, skipped)

            # Try and match the status byte found in midibytes
            (
                msgclass,
                status,
                known_message,
                complete_message,
                bad_termination,
                msgendidxplusone,
            ) = cls._match_message_status(
                midibytes, msgstartidx, msgendidxplusone, endidx
            )
            channel_match_orna = True
            if complete_message and not bad_termination:
                try:
                    msg = msgclass.from_bytes(midibytes[msgstartidx:msgendidxplusone])
                    if msg.channel is not None:
                        channel_match_orna = channel_filter(msg.channel, channel_in)

                except (ValueError, TypeError) as ex:
                    msg = MIDIBadEvent(midibytes[msgstartidx:msgendidxplusone], ex)

            # break out of while loop for a complete message on good channel
            # or we have one we do not know about
            if known_message:
                if complete_message:
                    if channel_match_orna:
                        break
                    # advance to next message
                    msgstartidx = msgendidxplusone
                else:
                    # Important case of a known message but one that is not
                    # yet complete - leave bytes in buffer and wait for more
                    break
            else:
                msg = MIDIUnknownEvent(status)
                # length cannot be known
                # next read will skip past leftover data bytes
                msgendidxplusone = msgstartidx + 1
                break

        return (msg, msgendidxplusone, skipped)


class BartMIDI(adafruit_midi.MIDI):
    def __init__(
            self,
            midi_in=None,
            midi_out=None,
            *,
            in_channel=None,
            out_channel=0,
            in_buf_size=30,
            debug=False
    ):
        print("BARTRRRRRR")
        super().__init__(midi_in=midi_in, in_channel=in_channel, midi_out=midi_out, out_channel=0)

    def read_next_midi_packet(self):
        packet = []
        synced = False

        while True:
            i = self._midi_in.read(1)
            i = hex(int.from_bytes(i, 'big'))

            if len(packet) > 14:
                packet = []
                synced = False
            if i == "0xf0":
                synced = True
            if synced:
                packet.append(i)
            if i == "0xf7" and len(packet) == 14 and synced:
                return packet

    def receive(self):
        packet = self.read_next_midi_packet()
        print(packet, KronosMessage(packet))
        input("next?")
        # print(f"\n{packet} - {KronosMessage(packet)}")

    def send(self, msg, channel=None):
        """Sends a MIDI message.

        :param msg: Either a MIDIMessage object or a sequence (list) of MIDIMessage objects.
            The channel property will be *updated* as a side-effect of sending message(s).
        :param int channel: Channel number, if not set the ``out_channel`` will be used.

        """
        # if channel is None:
        #     channel = self.out_channel
        # if isinstance(msg, MIDIMessage):
        #     msg.channel = channel
        #     # bytes(object) does not work in uPy
        #     print(msg._STATUS)
        #     data = msg.__bytes__()  # pylint: disable=unnecessary-dunder-call
        # else:
        #     data = bytearray()
        #     for each_msg in msg:
        #         each_msg.channel = channel
        #         data.extend(
        #             each_msg.__bytes__()  # pylint: disable=unnecessary-dunder-call
        #         )

        # Send as raw bytearray again
        self._send(msg, len(msg))


"""
[43] Parameter Change (integer)                                           Receive/Transmit
        F0, 42, 3g, 68          Excl Header
        43                      Function
        TYP                     part of parameter id (see combi.txt, etc)
        SOC                     part of parameter id (see combi.txt, etc)
        SUB                     part of parameter id (see combi.txt, etc)
        PID                     part of parameter id (see combi.txt, etc)
        IDX                     part of parameter id (see combi.txt, etc)
        valueH                  Value   (bit14-20)   (*4)
        valueM                  Value   (bit7-13)    (*4)
        valueL                  Value   (bit0-6)     (*4)
        F7                      End of Excl

 or

        DEPRECATED

        F0, 42, 3g, 68          Excl Header
        43                      Function
        TYP                     part of parameter id (see combi.txt, etc)
        SOC                     part of parameter id (see combi.txt, etc)
        SUB                     part of parameter id (see combi.txt, etc)
        7F                      part of parameter id (see combi.txt, etc)
        PIDH                    (bits 7-14) part of parameter id (see combi.txt, etc)
        PIDL                    (bits 0-6) part of parameter id (see combi.txt, etc)
        IDX                     part of parameter id (see combi.txt, etc)
        valueH                  Value   (bit14-20)   (*4)
        valueM                  Value   (bit7-13)    (*4)
        valueL                  Value   (bit0-6)     (*4)
        F7                      End of Excl

        DEPRECATED
"""

"""
Channel change

        self.FUNCTION = 0x43
        self.TYP = 0x4
        self.SOC = 0x8
        self.SUB = 0x0
        self.PID = 0xe
        self.IDX = 0x0
        self.VALUE_H = 0x0
        self.VALUE_M = 0x0
        self.VALUE_L = <0 or 1>

Fader change

        self.FUNCTION = 0x43
        self.TYP = 0x4
        self.SOC = 0x8
        self.SUB = 0x0
        self.PID = 0x2
        self.IDX = 0x0
        self.VALUE_H = 0x0
        self.VALUE_M = 0x0
        self.VALUE_L = <0 to 127>

Page change

        self.FUNCTION = 0x43
        self.TYP = 0x1b
        self.SOC = 0x0
        self.SUB = 0x0
        self.PID = 0x3
        self.IDX = 0x0
        self.VALUE_H = 0x0
        self.VALUE_M = 0x0
        self.VALUE_L = 0x1
        
# 0000000000000000000000001100
# F042306843040000020000002DF7
buffer = b'\xf0B0hC\x04\x00\x00\x02\x00\x00\x00-\xf7'  # 45
# F0423068430408000200000045F7
buffer = b'\xf0B0hC\x04\x08\x00\x02\x00\x00\x00E\xf7'  # 69

# 0000000000000000000000001100
# F0423068431B00000300000001F7
buffer = b'\xf0B0hC\x1b\x00\x00\x03\x00\x00\x00\x01\xf7'  # page_change

# 0000000000001100000000001100
# F0423068430408000E00000000F7
buffer = b'\xf0B0hC\x04\x08\x00\x0e\x00\x00\x00\x00\xf7'  # ch_change
"""


class KronosMessage:
    def __init__(self, hexarray=None, fader=None, position=None):
        if hexarray is None:
            self.FUNCTION = 0x43
            self.TYP = 0x4
            self.SOC = fader
            self.SUB = 0x0
            self.PID = 0x2
            self.IDX = 0x0
            self.VALUE_H = 0x0
            self.VALUE_M = 0x0
            self.VALUE_L = position
            return

        # Assume buffer starts and ends with F0...F7
        print(hexarray)
        if hexarray[:4] != ['0xf0', '0x42', '0x30', '0x68'] and len(hexarray) != 14:
            raise Exception("Not a Kronos SysEx message!")

        self.FUNCTION = hexarray[4]  # 5th byte
        self.TYP = hexarray[5]
        self.SOC = hexarray[6]
        self.SUB = hexarray[7]
        self.PID = hexarray[8]
        self.IDX = hexarray[9]
        self.VALUE_H = hexarray[10]
        self.VALUE_M = hexarray[11]
        self.VALUE_L = hexarray[12]

    def __str__(self):
        return (f"""
        self.FUNCTION = {self.FUNCTION}
        self.TYP = {self.TYP}
        self.SOC = {self.SOC}
        self.SUB = {self.SUB}
        self.PID = {self.PID}
        self.IDX = {self.IDX}
        self.VALUE_H = {self.VALUE_H}
        self.VALUE_M = {self.VALUE_M}
        self.VALUE_L = {self.VALUE_L}
        """)

    def to_bytearray(self):
        packet = bytearray()
        packet.append(int('0xf0'))
        packet.append(int('0x42'))
        packet.append(int('0x30'))
        packet.append(int('0x68'))
        packet.append(int(self.FUNCTION))
        packet.append(int(self.TYP))
        packet.append(int(self.SOC))
        packet.append(int(self.SUB))
        packet.append(int(self.PID))
        packet.append(int(self.IDX))
        packet.append(int(self.VALUE_H))
        packet.append(int(self.VALUE_M))
        packet.append(int(self.VALUE_L))
        packet.append(int('0xf7'))
        return packet
