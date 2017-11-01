//
// js library for the project.
// put here everything local
//

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}


function LoadControlStatus() {

    var d = new Date();
    var pb = $("#last_image");
    var src = pb.attr('src');
    src = src.split("?", 1);
    pb.attr("src", src + "?"+ d.getTime());

    $.get( "/control/status/json", function(data) {
        ShowControlStatus(data);
    
    }, "json" );
}

function handleChangeCmd(radio) {

    var data = {};
    data[radio.name] = radio.value;
    $.post( "/control/change/" + radio.name  , data );
      
    LoadControlStatus();
}


function change_radio(name, a, b, va, vb) {
    var na = '#' + name + '_' + a; // detector_high
    var nb = '#' + name + '_' + b; // detector_low

    $(na).prop("checked", va);
    $(nb).prop("checked", vb);

}
function disable_radio(name, a, b) {
    var na = '#' + name + '_' + a; // detector_high
    var nb = '#' + name + '_' + b; // detector_low

    $(na).prop("disabled", true);
    $(nb).prop("disabled", true);

}


function ShowControlStatus(data) {

    if (!data) {
        console.log("Problem with JSON call. Bailing out"); 
        return; 
    }
    
    var hwstate_auto   = $('#hwstate_auto');     // radio auto
    var hwstate_manual = $('#hwstate_manual');   // radio manual
    var hwvars         = $('#hwvars :input');    // control form
    
    if (data.state == "AUTO") {
        hwstate_auto.prop("checked", true);
        hwstate_manual.prop("checked", false);
        hwvars.prop("disabled", true);
    } else {
        hwstate_auto.prop("checked", false);
        hwstate_manual.prop("checked", true);
        hwvars.prop("disabled", false);
        
        disable_radio('sensor_open','low','high');
        disable_radio('sensor_closed','low','high');
        disable_radio('detector','low','high');
        disable_radio('activation','low','high');
        
    }
    
    // working functions
    
    if (data.light == 0) {
        change_radio('light','low','high', true, false);
    } 
    else {
         change_radio('light','low','high', false, true);
    }   
    
    if (data.door == 0) {
        change_radio('door','closed','open', true, false);
    } 
    else {
         change_radio('door','closed','open', false, true);
    }   
    
    if (data.led == 0) {
        change_radio('led','low','high', true, false);
    } 
    else {
         change_radio('led','low','high', false, true);
    }   
    
    
    
    // fixed sensors
    
    if (data.sensor_open == 0) {
        change_radio('sensor_open','low','high', true, false);
    } 
    else {
         change_radio('sensor_open','low','high', false, true);
    }     
    
    if (data.sensor_closed == 0) {
        change_radio('sensor_closed','low','high', true, false);
    } 
    else {
         change_radio('sensor_closed','low','high', false, true);
    } 

    if (data.detector == 0) {
        change_radio('detector','low','high', true, false);
    } 
    else {
         change_radio('detector','low','high', false, true);
    } 
 
     if (data.activation == 0) {
        change_radio('activation','low','high', true, false);
    } 
    else {
         change_radio('activation','low','high', false, true);
    } 
       
}


// testing

function SendPresence() {
    var o = Object();
    o.presence = "toggle"
    wsock.Send(JSON.stringify(o));
}




