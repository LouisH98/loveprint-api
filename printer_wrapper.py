import base64

from thermalprinter import ThermalPrinter
import textwrap
import os
from io import BytesIO
from PIL import Image
from datetime import datetime

here = os.path.dirname(os.path.abspath(__file__))

image_path = os.path.join(here, 'assets/LovePrint_resized.jpg')


class PrinterWrapper:
    def __init__(self, print_welcome=True):
        self.printer = ThermalPrinter("/dev/serial0", 9600, heat_time=60, heat_interval=15)

        if check_printer_status(self.printer):
            if print_welcome:
                self.print_boot_image()

            self.printer.sleep()

    def print_boot_image(self):
        self.printer.image(Image.open(image_path), True)
        self.printer.feed(3)

    # function also wraps by words
    # look at string, count characters
    def print_line(self, text, formatting=None):
        if formatting is None:
            formatting = {
                'justify': 'C',
                'size': 'L',
                'bold': False,
                'upside_down': False,
                'underline': 0
            }
        if check_printer_status(self.printer):
            max_col = (self.printer.max_column / (2 if formatting['size'] == 'L' else 1)) - 1
            print("Max col", self.printer.max_column)
            text = textwrap.fill(text, max_col)
            self.printer.wake()
            self.printer.out(text,
                             justify=formatting['justify'],
                             size=formatting['size'],
                             bold=formatting['bold'],
                             upside_down=formatting['upside_down'],
                             underline=formatting['underline']
                             )
            self.printer.feed(1)
            self.printer.sleep()
        else:
            self.printer.sleep()
            raise RuntimeError("Printer is out of paper")


    def print_image(self, image_data, is_data_uri=True):
        if is_data_uri:
            image = get_image_from_data_uri(data_uri=image_data)
        else:
            image = image_data

        self.printer.wake()
        self.printer.image(image)
        self.printer.sleep()

    def print_signature(self, sig):
        self.printer.wake()
        date_string = get_date_string()

        # padding to right-justify the timestamp (date_sting)
        space_padding = ' ' * (self.printer.max_column - 1 - (len(date_string) + len(sig)))
        self.printer.out('', line_feed=True)
        self.printer.out(f'{sig}{space_padding}{date_string}'.strip(), justify='L', size='S', underline=False)

        self.printer.feed(3)
        self.printer.sleep()

    def get_status(self):
        try:
            return self.printer.status()
        except:
            return {}


# Helper Methods
def has_paper(printer):
    status = printer.status()
    return status['paper']


def get_image_from_data_uri(data_uri):
    image_data = data_uri.split(',', 1)[1]
    print(image_data)
    im_bytes = base64.b64decode(image_data)  # im_bytes is a binary image
    im_file = BytesIO(im_bytes)  # convert image to file-like object
    image = Image.open(im_file)  # img is now PIL Image object

    # Paste transparent background drawings on white background
    white_image = Image.new('RGBA', image.size, 'WHITE')
    white_image.paste(image, (0, 0), image)

    return white_image


def get_date_string():
    return datetime.now().strftime("%H:%M %d/%m")


# checks printer status dictionary to see if all values are True
# if so - there is most likely a connection issue on RX pin on Pi
def check_printer_status(printer):
    try:
        if all(value for value in printer.status().values()):
            raise RuntimeError("Printer is not connected to LovePrint")
        else:
            return has_paper(printer)
    except Exception:
        raise RuntimeError("Printer is not connected to LovePrint")
