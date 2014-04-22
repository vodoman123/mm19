#!/usr/bin/env python
from subprocess import Popen
import sys
import os

import getopt
import time

import json


FNULL = open(os.devnull, 'w')
PLAYERONESTDOUT = FNULL
path, filename = os.path.split(os.path.abspath(__file__))
dummy_player_path = \
    path+'/dummy'


def testGame(name, run_script):
    print "running test ..."
    winner = runGame("test_game_"+name+".out", name, "dummy",
                     run_script, dummy_player_path)
    return (winner == name)


def runGame(match_name, name1, name2, run_script1, run_script2):
    """
    runs this years game
    args: match_name , the players names, the scripts used to run them
    """
    server = Popen(["java", "-jar", "server.jar", match_name], stdout=FNULL)
 
    time.sleep(2)
    bot1 = Popen(os.path.join(run_script1, "run.sh"), 
                 stdout=PLAYERONESTDOUT,cwd=run_script1)
    bot2 = Popen(os.path.join(run_script2, "run.sh"), stdout=FNULL,cwd=run_script2)
    try:
        server.wait()  # wait for the sever to exit
    except KeyboardInterrupt: # if the use kills the running script
        server.kill() # cleanly kill server

    if (bot1.poll() is None):
        bot1.terminate()  # kill client if it fails to exit
    if bot2.poll() is None:
        bot2.terminate()
    if ((bot1.poll() is None) or (bot2.poll() is None)):  # makes sure they die
        time.sleep(5)
        if not bot1.poll():
            bot1.kill()
        if not bot2.poll():
            bot2.kill()
    with open(match_name) as f:
        winner = f.readlines()[-1].rstrip()
    # the winner is in last line of the output file
    print json.loads(winner)
    return json.loads(winner)["winner"]


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
                                       "hsvo:", ["help", "self", "verbose", "logfile="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    self_mode = False
    output = "log.out"
    for o, a in opts:

        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--logfile"):
            output = a

        elif o in ("-v", "--verbose"):
            print "hi"
            global PLAYERONESTDOUT
            PLAYERONESTDOUT = None


        elif o in ("-s", "--self"):
            self_mode = True
        else:
            assert False, "unknown option"
    try:
        bot1_path = os.path.join(os.getcwd(), args[0])
    except IndexError:
        print "missing bot to run"
        sys.exit(1)
    print "trying to run" + bot1_path
    files = os.listdir(bot1_path)
    if "name.txt" in files:
        if "run.sh" in files:
            with open(os.path.join(bot1_path, "name.txt")) as f:
                name = f.readlines()[0].rstrip()
            if self_mode:
                print runGame(output, name, name,
                              bot1_path, bot1_path )
            else:
                print runGame(output, name, "dummy", bot1_path,
                              dummy_player_path)
        else:
            print "error can't find run.sh"
    else:
        print "error can't find name.text"


def usage():
    print """ mm19_runner - a game runner for the mm19 tournament
-Sam Laane

 usage: mm19_runner.py [-o output_file] path_to_run.sh

 -o or --logfile: set the name log file to save the outcome\ 
will default to log.out if not set

 -s or --self: play a copy of your bot insted of the dummy bot

 -v or --verbose: Prints your players copy of stdout to the screen

the input file should be a list the the teams competing

This file is needed for the tournament runner to work.
 """

if __name__ == "__main__":
    main()
