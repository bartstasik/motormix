import adafruit_midi
import usb_midi
from adafruit_midi.midi_message import MIDIUnknownEvent, MIDIBadEvent, channel_filter, MIDIMessage


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

    def receive(self):
        """Read messages from MIDI port, store them in internal read buffer, then parse that data
        and return the first MIDI message (event).
        This maintains the blocking characteristics of the midi_in port.

        :returns MIDIMessage object: Returns object or None for nothing.
        """
        ### could check _midi_in is an object OR correct object OR correct interface here?
        # If the buffer here is not full then read as much as we can fit from
        # the input port
        if len(self._in_buf) < self._in_buf_size:
            bytes_in = self._midi_in.read(self._in_buf_size - len(self._in_buf))
            if bytes_in:
                # print("Receiving: ", [hex(i) for i in bytes_in])
                print(bytes_in)
                self._in_buf.extend(bytes_in)
                del bytes_in

        (msg, endplusone, skipped) = MIDIMessage.from_message_bytes(
            self._in_buf, self._in_channel
        )
        if endplusone != 0:
            # This is not particularly efficient as it's copying most of bytearray
            # and deleting old one
            self._in_buf = self._in_buf[endplusone:]

        self._skipped_bytes += skipped

        # msg could still be None at this point, e.g. in middle of monster SysEx
        return msg, self._in_buf, self._in_channel

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

        self._send(msg, len(msg))
