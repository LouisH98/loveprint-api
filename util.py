
# formatting looks like this:
# align: 0, 1, 2 - left, middle, right
# size: 0, 1, 2 - small, medium, large
# style: [1*, 2*, 3*] - Bold, upside_down, underline (* = optional)
def convert_web_formatting_to_printer_codes(web_formatting):
    justify_array = ['L', 'C', 'R']
    size_array = ['S', 'M', 'L']

    text_style = web_formatting['text_style']
    bold = 0 in text_style
    upside_down = 1 in text_style
    underline = 2 if 2 in text_style else 0

    return {
        'justify': justify_array[web_formatting['justify']],
        'size': size_array[web_formatting['size']],
        'bold': bold,
        'upside_down': upside_down,
        'underline': underline
    }
