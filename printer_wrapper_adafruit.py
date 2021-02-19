import base64

import textwrap
import os
from io import BytesIO
from PIL import Image, ImageChops
from datetime import datetime
from Adafruit_Thermal import Adafruit_Thermal

here = os.path.dirname(os.path.abspath(__file__))

image_path = os.path.join(here, 'assets/LovePrint_resized.jpg')


class PrinterWrapper:
    def __init__(self, print_welcome=True):
        self.printer = Adafruit_Thermal("/dev/serial0", 9600, 23)

        if check_printer_status(self.printer):
            if print_welcome:
                self.print_boot_image()

            self.printer.sleep()

    def print_boot_image(self):
        self.printer.printImage(Image.open(image_path))
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
            max_col = int((32 / (2 if formatting['size'] == 'L' else 1)) - 1)
            text = textwrap.fill(text, max_col)
            self.printer.wake()
            self.set_printer_formatting(formatting)
            self.printer.print(text)
            self.printer.feed(1)
            self.printer.sleep()
        else:
            self.printer.sleep()
            raise RuntimeError("Printer is out of paper")

    def set_printer_formatting(self, formatting: dict):
        if formatting['upside_down']: self.printer.upsideDownOn()
        else: self.printer.upsideDownOff()

        if formatting['underline'] != 0: self.printer.underlineOn(formatting['underline'])
        else: self.printer.underlineOff()

        if formatting['bold']: self.printer.boldOn()
        else: self.printer.boldOff()

        self.printer.setSize(formatting['size'])
        self.printer.justify(formatting['justify'])


    def print_image(self, image_data, is_data_uri=True):
        if is_data_uri:
            image = get_image_from_data_uri(data_uri=image_data)
        else:
            image = image_data

        self.printer.wake()
        self.printer.printImage(image)
        self.printer.sleep()

    def print_signature(self, sig):
        self.printer.wake()
        date_string = get_date_string()

        # padding to right-justify the timestamp (date_sting)
        space_padding = ' ' * (32 - 1 - (len(date_string) + len(sig)))
        self.printer.printLn('')
        self.set_printer_formatting({
            "justify": 'L',
            "size": 'S',
            "underline": False,
            "bold": False,
            "upside_down": False
        })
        self.printer.print(f'{sig}{space_padding}{date_string}'.strip(), justify='L', size='S', underline=False)

        self.printer.feed(3)
        self.printer.sleep()

    def get_status(self):
        try:
            return {"paper": has_paper(self.printer)}
        except:
            return {}


# Helper Methods
def has_paper(printer):
    return printer.hasPaper()


def get_image_from_data_uri(data_uri):
    image_data = data_uri.split(',', 1)[1]
    im_bytes = base64.b64decode(image_data)  # im_bytes is a binary image
    im_file = BytesIO(im_bytes)  # convert image to file-like object
    image = Image.open(im_file)  # img is now PIL Image object

    # Paste transparent background drawings on white background
    white_image = Image.new('RGBA', image.size, 'WHITE')
    white_image.paste(image, (0, 0), image)

    # get bounding box and crop whitespace
    bg = Image.new(image.mode, image.size, 'WHITE')
    diff = ImageChops.difference(white_image, bg)
    bbox = diff.getbbox()

    if bbox:
        image_bbox = white_image.getbbox()
        # keep same width of original image
        bbox_same_width = (image_bbox[0], bbox[1], image_bbox[2], bbox[3])
        return white_image.crop(bbox_same_width)

    return white_image


def get_date_string():
    return datetime.now().strftime("%H:%M %d/%m")


# checks printer status dictionary to see if all values are True
# if so - there is most likely a connection issue on RX pin on Pi
def check_printer_status(printer):
    try:
        return has_paper(printer)
    except Exception:
        raise RuntimeError("Printer is not connected to LovePrint")
