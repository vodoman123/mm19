# Ship class for Python Test Client, MM19

# Copyright (c) 2013 Association for Computing Machinery at the University
# of Illinois, Urbana-Champaign. Inherits license from main MechMania 19 code.

import random

main_length = 5
destroyer_length = 4
pilot_length = 2

class Ship(object):
    def __init__(self, ship_type, x, y, orient, _id):
        self.ship_type = ship_type
        self.x = x
        self.y = y
        self.orient = orient
        self.id = _id


    def getJSON(self):
        """Return the JSON dictionary representation of the ship."""
        out = {'xCoord': self.x, 'yCoord': self.y, 'orientation': self.orient}
        out['type'] = self.ship_type
        return out

    @classmethod
    def random_ship(Ship, ship_type):
        """
        Static method for placing a ship randomly.

        ship_type: The type of ship.
        """
        x = random.randint(0, 90)
        y = random.randint(0, 90)
        orient = random.choice(["H", "V"])

        ship_length = Ship.get_length_from_type(ship_type)
        if orient == "H" and x+ship_length-1 > 99:
            x = x - ship_length + 1
        if orient == "V" and y+ship_length-1 > 99:
            y = y - ship_length + 1

        return Ship(ship_type, x, y, orient, -1)

    @classmethod
    def get_length_from_type(Ship, type):
        if type == "D": 
            return destroyer_length
        elif type == "P":
            return pilot_length
        else: 
            return main_length

    def get_length(self):
        return Ship.get_length_from_type(self.ship_type)

    #returns a set of coordinate pairs where the ship is
    def get_coord_pairs(self):
        pairs = set()
        if ship.orient == "H":
            for i in range(self.get_length()):
                pairs.add(self.x + i, self.y)

        if ship.orient == "V":
            for i in range(self.get_length()):
                pairs.add(self.x, self.y+1)

        return pairs

