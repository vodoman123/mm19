
//all in pixels
var CANVAS_HEIGHT = Math.min(window.innerWidth / 2, window.innerHeight - 80);
var MARGIN = 3;
var GAME_HEIGHT = CANVAS_HEIGHT - MARGIN * 2;

//in ms
var ANIMATION_LENGTH = 200;

/*
    Holds the render state, and functions that render the game
*/
var view = {

    //translates game coordinates to pixel coordinates
    g2p : function (game_coordinate) {
        return MARGIN + game_coordinate * (GAME_HEIGHT / controller.size);
    },

    render_state : {
        paper1 : Raphael("paper1", CANVAS_HEIGHT, CANVAS_HEIGHT),
        paper2 : Raphael("paper2", CANVAS_HEIGHT, CANVAS_HEIGHT)
    },

    /*
        Initializes user interface by showing and hiding what needs to be shown and hidden.
    */
    init_ui : function() {
        util.hide_class("play");
        document.getElementById("controls").style.visibility = "visible";
        document.getElementById("board").style.visibility = "visible";
        view.render_state.paper1.canvas.style.backgroundColor = "#00CED1";
        view.render_state.paper2.canvas.style.backgroundColor = "#00CED1";
    },

    set_turn : function(turn_number) {
        document.getElementById("turn_number").value = "" + turn_number;
        document.getElementById("turn_info").innerHTML = "Turn " + turn_number;
    },

    animations : {
        //Fire
        "F" : function(my_paper, enemy_paper, x, y, color) {
            if (!color) {
                color = "#FF8C00";
            }
            var shape = enemy_paper
                .circle(view.g2p(x), view.g2p(y), 0);
            shape
                .attr(
                    {
                        "fill" : color
                    })
                .animate(
                    {
                        "r" : (GAME_HEIGHT / controller.size) * 3,
                    },
                    ANIMATION_LENGTH,
                    null,
                    function () {
                        shape.remove();
                    });
        },
        //Move horizontal
        "MH" : function(my_paper, enemy_paper, x, y) {
            //do nothing
        },
        //Move vertical
        "MV" : function(my_paper, enemy_paper, x, y) {
            //do nothing
        },
        //Burst
        "B" : function(my_paper, enemy_paper, x, y) {
            for (var a = x - 1; a <= x + 1; a += 1) {
                for (var b = y - 1; b <= y + 1; b += 1) {
                    view.animations.F(my_paper, enemy_paper, a, b);
                }
            }
        },
        //Sonar
        "S" : function(my_paper, enemy_paper, x, y) {
            view.animations.F(my_paper, enemy_paper, x, y, "#9400D3");
        },
        //Nothing
        "N" : function(my_paper, enemy_paper, x, y) {
            //do nothing
        }
    },

    display_winner : function (winner) {
        var disp = document.getElementById('winner_display');
        disp.innerHTML = winner + ' Wins!';
        disp.style.visibility = 'visible';
    },

    /*
        do_animate is a flag that says whether we should render animations or not.
    */
    render_game : function (do_animate) {
        var draw_ship = function(ship, paper) {
            var box_width = GAME_HEIGHT / controller.size;
            //width and height of ship in pixels
            var width = box_width * model.ship_lib[ship.type].width;
            var height = box_width;

            var x = view.g2p(ship.x);
            var y = view.g2p(ship.y);

            //map ship health to integers 1, 2, 3 for ship's health status
            var ship_status = Math.min(Math.floor((ship.health / model.ship_lib[ship.type].health) * 3) + 1, 3);

            var src = "images/" + ship.type.toLocaleLowerCase() + ship_status + ".svg";

            var image = paper.image(src, x, y, width, height);

            if (ship.orientation === "V") {
                image.transform("r90," + (x + (box_width / 2)) + "," + (y + (box_width / 2)));
            }
        };

        var draw_animation = function(my_paper, enemy_paper, action) {
            view.animations[action.action_id](my_paper, enemy_paper, action.target_x, action.target_y);
        };

        //set resources
        document.getElementById("p1_resources").innerHTML = model.game_state[0].resources;
        document.getElementById("p2_resources").innerHTML = model.game_state[1].resources;
        //clear shapes
        this.render_state.paper1.clear();
        this.render_state.paper2.clear();
        //draw new ships
        util.map_array(function(ship) {
                draw_ship(ship, view.render_state.paper1);
            },
            model.game_state[0].ships);
        util.map_array(function(ship) {
                draw_ship(ship, view.render_state.paper2);
            },
            model.game_state[1].ships);
        if (do_animate) {
            //draw animations
            util.map_array(function(action) {
                    draw_animation(view.render_state.paper1, view.render_state.paper2, action);
                },
                model.game_state[0].actions);
            util.map_array(function(action) {
                    draw_animation(view.render_state.paper2, view.render_state.paper1, action);
                },
                model.game_state[1].actions);
        }
    }
};


