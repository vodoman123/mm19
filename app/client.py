#! /usr/bin/env python2

# Basic Test Client for MechMania 19
# Copyright (c) 2013 Association for Computing Machinery at the University
# of Illinois, Urbana-Champaign. Inherits license from main MechMania 19 code.

import json
import logging
import random
import socket

from ship import Ship
from logic import Logic

# TODO (competitors): This is arbitrary but should be large enough
MAX_BUFFER = 65565

NOTIFY_RESPONSE_CODE = 100
SUCCESS_RESPONSE_CODE = 200
WARNING_RESPONSE_CODE = 201
ERROR_RESPONSE_CODE = 400
INTERRUPT_RESPONSE_CODE = 418
WIN_RESPONSE_CODE = 9001
LOSS_RESPONSE_CODE = -1

class Client(object):
    """
    A class for managing the client's connection.

    TODO (competitors): You should add the API functions you need here. You can
    remove the inheritance from object if "new style" classes freak you out, it
    isn't important.
    """

    def require_connection(func):
        """
        This is a decorator to wrap a function to require a server connection.

        func -- A Client class function with self as the first argument.
        """
        def wrapped(self, *args):
            if self.sock == None:
                logging.error("Connection not established")
            else:
                return func(self, *args)

        return wrapped

    def __init__(self, host, port, name, logic_obj):
        """
        Initialize a client for interacting with the game.

        host -- The hostname of the server to connect
                (e.g.  "example.com")
        port -- The port to connect on (e.g. 6969)
        name -- Unique name of the client connecting
        """
        self.host = host
        self.port = port
        self.name = name
        self.sock = None
        self.token = ""
        self.resources = 0
        self.logic = logic_obj

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        logging.info("Connection target is %s:%d", self.host, self.port)
        self.sock.connect((self.host, self.port))
        logging.info("Connection established")

    @require_connection
    def join_game(self, main_ship_and_shiparray):
        """
        Handle all the pre-work for game setup.

        This function won't return until the server is connected and the game
        begins. There's no real need to call it asynchronously, as you can't
        actually do anything until the server is connected.

        shiparray -- The initial positions for all ships
        """

        # Step 1: Set up the initial data payload
        payload = {'playerName': self.name}
        # TODO (competitors): This is really ugly because the main ship is
        # special cased. I'm sorry. Feel free to fix.
        payload['mainShip'] = main_ship_and_shiparray[0].getJSON()
        payload['ships'] = [ship.getJSON() for ship in main_ship_and_shiparray[1]]

        # Step 2: Transmit the payload and receive the reply
        logging.info("Transmitting start package to server... \n %s", payload)
        self._send_payload(payload)

        # Step 3: Process the reply

    def _send_payload(self, payload):
        #logging.debug("Payload: %s", json.dumps(payload))
        # Send this information to the server
        self.sock.sendall(json.dumps(payload) + '\n')

    def _start_game(self):
        while(True):
            json_data = json.loads(self.sock.recv(MAX_BUFFER))
            response_code = json_data['responseCode']
            logging.debug("response_code: %s", response_code)
            if response_code == NOTIFY_RESPONSE_CODE:
                self.play_turn(json_data)
            elif response_code == SUCCESS_RESPONSE_CODE or response_code == WARNING_RESPONSE_CODE:
                self.handle_response(json_data)
            elif response_code == INTERRUPT_RESPONSE_CODE or response_code == WIN_RESPONSE_CODE or response_code == LOSS_RESPONSE_CODE :
                self.game_interupted(json_data)
                break

            #self.wait_for_turn()
            #self.wait_for_turn_response()

    def game_interupted(self, data):
        logging.debug("Server ended the game")

    def play_turn(self, turn_notification):
        if self.logic.token == "":
            logging.debug("no player tolken... setting now")
            self.logic.token = turn_notification["playerToken"]
            for dict in turn_notification['ships']:
                self.logic.ships[dict['ID']] = Ship(dict['type'], dict['xCoord'], dict['yCoord'], dict['orientation'], dict['ID'])
            self.logic.set_ship_locations()

        payload = self.logic.turn(turn_notification)
        self._send_payload(payload)

    def handle_response(self, turn_response):

        logging.debug( "helo %s", turn_response['resources'])
        
        self.logic.handle_response( turn_response )


def main():
    establish_logger(logging.DEBUG)
    logic = Logic()
    logic.logging = logging

    client = Client("localhost", 6969, "DaKillers", logic)
    client.connect()
    client.join_game(logic.setup())
    client._start_game()

def establish_logger(loglevel):
    logging.basicConfig(format="%(asctime)s %(message)s",
            datefmt='%m/%d/%Y %I:%M:%S %p', level=loglevel)
    logging.debug("Logger initialized")

if __name__ == "__main__":
    main()
