#! venv/bin/python3

from flask import request
from flask_api import FlaskAPI, status

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_cors import CORS

from printer_wrapper import PrinterWrapper
import os
import sys
from util import convert_web_formatting_to_printer_codes

sys.path.append(os.path.abspath(__file__))
here = os.path.dirname(os.path.abspath(__file__))

app = FlaskAPI(__name__)

# enable cross-origin
CORS(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["50 per day", "20 per hour"]
)

printer = PrinterWrapper(False)

MAX_WORDS = 30


@app.route('/api/print-text', methods=['POST'])
@limiter.limit("5 per minute")
@limiter.limit("10 per hour")
# @limiter.exempt
def print_text():
    try:
        try:
            data = request.get_json()
            if 'message' in data:
                message = data['message']
            else:
                message = ''

            if len(message.split()) > MAX_WORDS:
                return {
                           'error': 'Message too long'
                       }, status.HTTP_400_BAD_REQUEST

            if 'formatting' in data:
                formatting = convert_web_formatting_to_printer_codes(data['formatting'])
            else:
                formatting = None

            if 'image' in data and data['image'] != "":
                printer.print_image(data['image'])

            if len(message) > 0:
                printer.print_line(message, formatting)

            if 'username' in data:
                printer.print_signature(data['username'])

            return {
                'status': 'Message Printed!',
                'paper': printer.get_status()['paper']
            }
        except Exception as error:
            return {
                       "error": str(error),
                       "paper": printer.get_status()['paper']
                   }, status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as error:
        print('Error communicating with printer. Check the power and serial connections.')
        return {
                   'error': 'Could not communicate with printer. Tell Louis to fix it.'
               }, status.HTTP_500_INTERNAL_SERVER_ERROR


@app.route('/api/get-status', methods=['GET'])
@limiter.exempt
def get_status():
    try:
        return printer.get_status()
    except Exception as error:
        return {"error": str(error)}, status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    cert = os.path.join(here, 'cert.pem')
    key = os.path.join(here, 'key.pem')
    context = (cert, key)
    app.run(host='0.0.0.0', ssl_context=context, port=2053, debug=False)
