
/*
    Handles user input and game loop
*/
var controller = {

    /*
        Inititilizes UI.
    */
    init : function () {
        var path = util.get_url_paramater("path");
        if (path) {
            util.get_text(path, controller.init_game);
        } else {
            controller.load_file();
        }
    },

    load_file : function() {
        // Check for the various File API support.
        if (!(window.File && window.FileReader && window.FileList && window.Blob)) {
            alert('The File APIs are not fully supported in this browser.');
            return;
        }

        /**
        * File loading handler for loading JSON
        */
        var file_select_handler = function(evt) {
            var file = evt.target.files[0]; // File object

            var reader = new FileReader();

            // Closure to capture the file information.
            reader.onload = function(e) {
                controller.init_game(e.target.result);
            };

            // Read in the json file as a string.
            reader.readAsText(file);
        };

        //cannot interact with anything on the page until this statement
        document.getElementById('file_select').addEventListener('change', file_select_handler, false);
        util.map_array(
            function (node) {
                node.style.display = 'inline';
            },
            document.getElementsByClassName('file_ui'));
    },

    init_game : function(raw_log) {
        controller.log = raw_log.split("\n");
        controller.frame = 0;
        controller.pause = true;

        try {
            var setup = util.map_array(json_parse, controller.log.slice(0, 3));
        } catch (error) {
            console.log(error.message);
            console.log("One of the first three lines are invalid JSON.  Did you upload the right file?");
            return;
        }

        document.getElementById("p1_name").innerHTML = setup[1].playerName;
        document.getElementById("p2_name").innerHTML = setup[2].playerName;

        model.new_game_state(setup);
        view.init_ui();
        view.render_game();
    },

    /*
        Runs a tick of the game.  Pauses if out of turns.
    */
    run_tick : function(backwards) {
        var direction = backwards ? -1 : 1;

        var turn;
        var complete = false;
        while (!complete) {
            this.frame += direction;

            if (this.frame >= this.log.length && !backwards) {
                this.frame = this.log.length - 1;
                this.buttons.pause();
                console.log("Reached end of game");
                return;
            }

            try {
                turn = json_parse(this.log[this.frame]);
                complete = true;
            } catch (error) {
                console.log("Turn " + this.frame + " inproperly formatted.  Skipping to next turn...");
            }
        }

        if ("winner" in turn) {
            alert(turn.winner + " Wins!");
            this.buttons.pause();
            return;
        }

        view.set_turn(this.frame);

        // apply turn to game state
        model.perform_turn(turn);
        // apply that to render state
        view.render_game(true);
    },

    pause : true,

    frame : 0,

    log : [],

    size: 0,

    buttons : {
        play : function() {
            controller.pause = false;

            util.hide_class("pause");
            util.show_class("play");

            var run_until_pause = function() {
                if (controller.pause) {
                    return;
                }

                controller.run_tick();

                var timeout = parseInt(document.getElementById("tick_rate").value);

                if (timeout < 1) {
                    timeout = 1;
                } else if (timeout > 99999) {
                    timeout = 99999;
                }

                //timeout
                window.setTimeout(run_until_pause, timeout);
            };

            run_until_pause();
        },

        pause : function() {
            controller.pause = true;

            util.hide_class("play");
            util.show_class("pause");
        },

        increase_sleep : function() {
            var node = document.getElementById("tick_rate");
            node.value = Math.ceil(parseInt(node.value) * 1.1) + 1;
        },

        decrease_sleep : function() {
            var node = document.getElementById("tick_rate");
            node.value = Math.ceil(parseInt(node.value) * 0.9);
        },

        step_forward : function() {
            controller.run_tick();
        },

        step_backward : function() {
            if (controller.frame <= 1) {
                return;
            }
            controller.run_tick(true);
        },

        restart : function() {
            controller.frame = 0;
            view.set_turn(0);

            var setup = util.map_array(json_parse, controller.log.slice(0, 3));
            model.new_game_state(setup);
            view.render_game();
            view.init_ui();
        },

        set_turn : function() {
            controller.frame = parseInt(document.getElementById("turn_number").value) - 1;
            if (controller.frame < 0) {
                controller.frame = 0;
            } else if (controller.frame >= controller.log.length) {
                controller.frame = controller.log.length - 2;
            }
            controller.run_tick();
        }
    }
};

window.onload = controller.init;


