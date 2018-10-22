/*  Copyright (c) 2004-2015 Odoo S.A.
    Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('event_barcode_partner.event_models', function (require) {
"use strict";


    var toggleFullScreen = function(el){
        //copy-pasted from odoo
//        // The canvas and the navigation bar needs to be fullscreened
//        var el = this.canvas.parentNode.parentNode;

        var isFullscreenAvailable = document.fullscreenEnabled || document.mozFullScreenEnabled || document.webkitFullscreenEnabled || document.msFullscreenEnabled || false;
        if(isFullscreenAvailable){ // Full screen supported
            // get the actual element in FullScreen mode (Null if no element)
            var fullscreenElement = document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement;

            if (fullscreenElement) { // Exit the full screen mode
                if (document.exitFullscreen) {
                    // W3C standard
                    document.exitFullscreen();
                } else if (document.mozCancelFullScreen) {
                    // Firefox 10+, Firefox for Android
                    document.mozCancelFullScreen();
                } else if (document.webkitExitFullscreen) {
                    // Chrome 20+, Safari 6+, Opera 15+, Chrome for Android, Opera Mobile 16+
                    document.webkitExitFullscreen();
                } else if (document.webkitCancelFullScreen) {
                    // Chrome 15+, Safari 5.1+
                    document.webkitCancelFullScreen();
                } else if (document.msExitFullscreen) {
                    // IE 11+
                    document.msExitFullscreen();
                }
            }else { // Request to put the 'el' element in FullScreen mode
                if (el.requestFullscreen) {
                    // W3C standard
                    el.requestFullscreen();
                } else if (el.mozRequestFullScreen) {
                    // Firefox 10+, Firefox for Android
                    el.mozRequestFullScreen();
                } else if (el.msRequestFullscreen) {
                    // IE 11+
                    el.msRequestFullscreen();
                } else if (el.webkitRequestFullscreen) {
                    if (navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1) {
                        // Safari 6+
                        el.webkitRequestFullscreen();
                    } else {
                        // Chrome 20+, Opera 15+, Chrome for Android, Opera Mobile 16+
                        el.webkitRequestFullscreen();
                    }
                } else {
                    var requestMethod = el.requestFullScreen || el.webkitRequestFullScreen || el.mozRequestFullScreen || el.msRequestFullScreen;

                    if (requestMethod) { // Native full screen.
                        requestMethod.call(el);
                    } else if (typeof window.ActiveXObject !== "undefined") { // Older IE.
                        var wscript = new ActiveXObject("WScript.Shell");
                        if (wscript !== null) {
                            wscript.SendKeys("{F11}");
                        }
                    }

                }
            }
        }else{
            // Full screen not supported by the browser
            console.error("ERROR : full screen not supported by web browser");
        }
    }

    return {
        'toggleFullScreen': toggleFullScreen
    };

});

