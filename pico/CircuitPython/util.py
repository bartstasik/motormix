import board
import busio

uart = busio.UART(tx=board.GP0, rx=board.GP1)


def print_uart(value, endline="\r\n"):
    uart.write(
        str.encode(f"{value}{endline}"))
