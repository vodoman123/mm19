

var util = {

    show_class : function(class_name) {
        var show = document.getElementsByName(class_name);

        for (var ind = 0; ind < show.length; ind += 1) {
            show[ind].style.display = "inline";
        }
    },

    hide_class : function(class_name) {
        var hidden = document.getElementsByName(class_name);

        for (var ind = 0; ind < hidden.length; ind += 1) {
            hidden[ind].style.display = "none";
        }
    },

    /*
        Maps func over arr to get some functional programming going :P
    */
    map_array : function(func, arr) {
        var ret_val = [];

        for (var ind = 0; ind < arr.length; ind++) {
            ret_val[ind] = func(arr[ind]);
        }

        return ret_val;
    },

    get_url_paramater : function(name) {
        var reg = new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)');
        var match = reg.exec(location.search);
        if (match) {
            return decodeURIComponent(match[1]);
        }
        return null;
    },

    get_url : function(url, callback) {
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState == 4 && request.status == 200) {
                callback(request);
            }
        };
        request.open('GET', url);
        request.send();
    }
};
