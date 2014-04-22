

Rudimentary visualizer for mm19.

Log files are loaded by the browser.
An example log can be found in visualizer/test_log.json.
The main idea is it contatins the board configuration on one line followed by a list of turns, each on one line.
A turn consists of a playerName, the resources that player has at the beginning of a turn, the state of each ship at the beginning of the turn, and a list of actions the player makes during their turn.
There must be at least two turns in the log to setup the initial configuration of the board.

LIBRARIES :
    Uses Raphael library, raphael.js, for drawing shapes and interacting with HTML 5 canvas.  May also be used for animations and other cool features.
    Uses Douglas Crockford's json_parse.js to parse the json.

BUGS :
    Happy to report, none at the moment.

TODO :
    * [X] fix coordinates
    * [X] use new json
    * [X] show who won
    * [X] new UI
    * [X] Board resizing - all board space
    * [X] Different ship image
    * [X] Different ship color
    * [X] GET paramaters
        -round#
        -log location
    * [ ] Effects
        -hit
        -miss
        -burst
        -sonar
        -fire
    * [ ] New controls

