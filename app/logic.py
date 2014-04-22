import random
import math
from ship import Ship

attack_cost = 50
main_move_cost = 250
destroyer_move_cost = 200
pilot_move_cost = 100
burst_cost = 250
sonar_cost = 110

class Logic(object):

    def __init__(self):
        self.resources = 0
        self.token = ""
        
        #dict of ID -> Ship key-value pairs
        self.ships = {}

        #dict of coordinate tuples where ships exist -> the ship itself
        self.ship_locations = {}

        #set of coordinate tuples where we've already attacked
        self.already_attacked = set()

        self.last_hits = []
        self.last_brute = (0, 0)

        #this is a set of coordinate tuples where we've hit them
        self.hits = set()
        self.turn_count = 0

        #set of coordinate tuples where they've already attacked
        self.they_attacked = set()

    def setup(self):
        print "Init ships"
        ships = []
        main_ship = Ship.random_ship("M")

        for i in range (8):
            temp_ship = Ship.random_ship("D")
            while not self.ship_space_free(temp_ship):
                temp_ship = Ship.random_ship("D")
            ships.append(temp_ship)

        for i in range(10):
            temp_ship = Ship.random_ship("P")
            while not self.ship_space_free(temp_ship):
                temp_ship = Ship.random_ship("P")
            ships.append(temp_ship)

        return (main_ship, ships)

    # data is the response to your turn submission
    # AKA the Server Turn Response -- tells the results of our actions
    def handle_response(self, data):
        self.last_hits = []
        for d in data['hitReport']:
            if d['hit'] == True:
                self.last_hits.append((d['xCoord'], d['yCoord']))

        self.token = data['playerToken']

        # Check self.resources with what the server tells us, just in case
        data_resources = data['resources']
        if self.resources != data_resources:
            self.resources = data_resources

        # Hopefully we hit things
        self.hits = self.hits.union([(hit['xCoord'], hit['yCoord']) for hit in data['hitReport'] if hit['hit']])
        if data['hitReport']:
            for hit in data['hitReport']:
                if not hit['hit'] and (hit['xCoord'], hit['yCoord']) in self.hits:
                    self.hits.discard((hit['xCoord'], hit['yCoord']))

        self.already_attacked = self.already_attacked.union([(hit['xCoord'], hit['yCoord']) for hit in data['hitReport']])

        # TODO: We also probably should handle pingReport

    """
    Helpful strategies:
        Keep track of all possible positions for ships that have >0 hits. The list never gets bigger than ~30K so it can be kept exactly, 
            unlike the list of all possible positions for all ships (which is very large).
        The GetShot algorithm has two parts, one which generates random shots and the other which tries to finish sinking an already hit ship. 
            We do random shots if there is a possible position (from the list above) in which all hit ships are sunk. Otherwise, we try to 
            finish sinking a ship by picking a location to shoot at which eliminates the most possible positions (weighted).
        For random shots, compute best location to shoot based on the likelihood of one of the unsunk ships overlapping the location.
        Adaptive algorithm which places ships in locations where the opponent is statistically less likely to shoot.
        Adaptive algorithm which prefers to shoot at locations where the opponent is statistically more likely to place his ships.
        Place ships mostly not touching each other.

    A good monte carlo strategy in js: http://jsfiddle.net/FgbAK/

    Machine learning -- adjust certain thresholds by playing itself a lot. Save them in a file and reload when starting so data isn't lost.
    """

    # data is the Server Turn Notification -- tells what the oponent did
    def turn(self, data):
        self.turn_count += 1
        payload = {'playerToken': self.token}

        for poop in data['ships']:
            if poop['health'] <= 0:
                del self.ships[poop['ID']]
                set_ship_locations()

        # Main ship generates 30 resources per turn
        # Pilor ship generates 50 resources per turn
        # Our max is +530 resources per turn
        pilots = len(self.get_ships_for_type("P"))
        self.resources = self.resources + 30 + (pilots * 50)

        current_turn_attacks = set()
        for hit in data['hitReport']:
            self.they_attacked.add((hit['xCoord'], hit['yCoord']))
            current_turn_attacks.add((hit['xCoord'], hit['yCoord']))

        to_move_id = -1
        mystery_counter = 0
        for atk in current_turn_attacks:
            if atk in self.ship_locations:
                the_ship = self.ship_locations[atk]
                if the_ship.ship_type == "P" and mystery_counter < 1:
                    mystery_counter = 1
                    to_move_id = the_ship.id
                elif the_ship.ship_type == "D" and mystery_counter < 2:
                    mystery_counter = 2
                    to_move_id = the_ship.id
                elif the_ship.ship_type == "M" and mystery_counter < 3:
                    mystery_counter = 3
                    to_move_id = the_ship.id

        (moved_id, move_JSON) = self.move_logic(to_move_id)
        if not move_JSON:
            self.set_ship_locations()

        ship_actions = self.attack_logic(moved_id)

        if move_JSON:
            ship_actions.append(move_JSON)

        payload['shipActions'] = ship_actions

        return payload

    # If they're going linearly, and they get too close, we should get away
    def move_logic(self, hit_id):
        if hit_id == -1:
            return (-1, None)
        elif self.ships[hit_id].ship_type == "M" and self.resources >= main_move_cost:
            self.resources -= main_move_cost 
            return (hit_id, 
                    self.move(hit_id, "MV", random.randint(0,99), random.randint(0,95)))
        elif self.ships[hit_id].ship_type == "D" and self.resources >= destroyer_move_cost:
            self.resources -= destroyer_move_cost 
            return (hit_id,
                    self.move(hit_id, "MV", random.randint(0,99), random.randint(0,96)))
        elif self.ships[hit_id].ship_type == "P" and self.resources >= pilot_move_cost:
            self.resources -= pilot_move_cost
            return (hit_id, 
                    self.move(hit_id, "MV", random.randint(0,99), random.randint(0,98)))
        else:
            return (-1, None)

    def move(self, ship_id, way, actionX, actionY):
        return {'ID': ship_id, 'actionID': way, 'actionX': actionX, 'actionY': actionY, 'actionExtra': 0}

    def attack_logic(self, move_id):

        attack_return = []
        destroyers = self.get_ships_for_type("D") + self.get_ships_for_type("M")
        num_brute = int( len(destroyers)/3)
        num_rand = len(destroyers)-num_brute

        if(len(self.last_hits) > 0):
            for dest in destroyers:
                if self.resources > 50 and move_id != dest.id:
                    attack_return.append( self.attack(dest, self.last_hits[0][0], self.last_hits[0][1]) )
        else:
            i = 0
            for dest in destroyers:
                i+= 1
                if self.resources > 50 and move_id != dest.id:

                    if(i < num_rand):
                        attack_return.append( self.attack(dest, random.randint(0, 99), random.randint(0, 99)) )

                    else:
                        x = int(self.turn_count/50)*2
                        y = self.turn_count % 50 * 2
                        self.turn_count+=1
                        attack_return.append(self.attack(dest, x, y))

            if self.resources >= burst_cost and move_id == -1:
                attack_return[0]['actionID'] = "B"


        return attack_return


    #Important: ships can only attack if they haven't used a special

    def space_blocked(self, x, y):
        for ship in self.ships:
            if ship.orient == "H":
                if ship.y == y and ship.x in range(x+1-ship.get_length(), x+1):
                    return True
            if ship.orient == "V":
                if ship.x == x and ship.y in range(y+1-ship.get_length(), y+1):
                    return True
        return False

    def ship_space_free(self, ship):
        if ship.orient == "H":
            for i in range(ship.get_length()):
                if self.space_blocked(ship.x + i, ship.y):
                    return False
        if ship.orient == "V":
            for i in range(ship.get_length()):
                if self.space_blocked(ship.x, ship.y + i):
                    return False
        return True

    def attack(self, ship, actionX, actionY):
        return_action = {'ID': ship.id, 'actionID': "F", 'actionX': actionX, 'actionY': actionY, 'actionExtra': 0}
        if self.resources > attack_cost:
            self.resources -= attack_cost
            return return_action
        else:
            return False

    def burst(self, ship, actionX, actionY):
        return_action = {'ID': ship.id, 'actionID': "B", 'actionX': actionX, 'actionY': actionY, 'actionExtra': 0}
        if self.resources > burst_cost:
            self.resources -= burst_cost
            return return_action
        else:
            return False

    def sonar(self, ship, actionX, actionY):
        return_action = {'ID': ship.id, 'actionID': "S", 'actionX': actionX, 'actionY': actionY, 'actionExtra': 0}
        if self.resources > sonar_cost:
            self.resources -= sonar_cost
            return return_action
        else:
            return False

    def set_ship_locations(self):
        for sh_id, ship in self.ships.iteritems():
            if ship.orient == "H":
                for the_x in range(ship.x, ship.x + ship.get_length()):
                    self.ship_locations[(the_x, ship.y)] = ship

            if ship.orient == "V":
                for the_y in range(ship.y, ship.y + ship.get_length()):
                    self.ship_locations[(ship.x, the_y)] = ship

    def get_ships_for_type(self, ship_type):
        a = []
        for key, value in self.ships.iteritems():
            if value.ship_type == ship_type:
                a.append(value)
        return a
