(function(){
    "use strict";
    var Web = openerp.web;
     Web.FormView.include({
         to_edit_mode: function() {
             var self = this;
             this._super.apply(this);
             self.load_color_data();
         },
         load_color_data: function(){
             var self = this;

             this.default_hue = this.datarecord.top_panel_hue;
             this.default_hex = this.datarecord.top_panel_hex;
             this.default_scheme = this.datarecord.top_panel_scheme;
             this.default_complement = this.datarecord.top_panel_complement;
             this.default_distance = this.datarecord.top_panel_distance;
             this.default_variation = this.datarecord.top_panel_variation;
             this.default_web_safe = this.datarecord.top_panel_web_safe;




             $("#hue-slider").slider({
                 min: 0,
                 max: 360,
                 slide: function(e, ui) {
                     // ui.value has the number
                     self.setHue(ui.value)
                 }
             });
             $('.hex input').change(function(){
                 self.setHex($('.hex input').val());
             });
             $('#set-hex').click(function(){
                 self.setHex($('.hex input').val());
             });
             $("#distance-slider").slider({
                 min: 0,
                 max: 1,
                 value: 0.5,
                 step: 0.01,
                 slide: function(e, ui) {
                     // ui.value has the number
                     self.setDistance(ui.value)
                 }
             });
             this.scheme = new ColorScheme;
             this.setHue(self.default_hue);
             this.setDistance(self.default_distance);
             this.setHex(self.default_hex);
             this.generateColors();
             $('#add-complement').click(function(){
                 self.addComplement();
             });
         },
         setHue: function(hue){
             var self = this;
             self.scheme.from_hue(hue);
             var bg = self.scheme.colors()[0];
             $('#hue-box').css('background-color', '#' + bg);
             $('.hex input').val( bg );
             $('#hex-box').css('background-color', '#' + bg);
             $('.hex input').val( bg );
             $('.hue input').val( hue );
             self.generateColors();
         },
         setHex: function(hex){
             // Strip possible leading hash
             var self = this;
             hex = hex.replace('#', '');
             console.log(hex);
             self.scheme.from_hex(hex);
             var bg = self.scheme.colors()[0];
             $('#hue-box').css('background-color', '#' + bg);
             $('#hex-box').css('background-color', '#' + hex);
             self.generateColors();
         },
         setDistance: function(distance){
             var self = this;
             $('.scheme_distance input').val( distance );

             self.scheme.distance(distance);
             self.generateColors();
         },
         generateColors: function(){
             var self = this;
             $('#colors').html('');
             var colors = self.scheme.colors();
             for (var i in colors) {
                 var c = colors[i];
                 var newDiv = '<div class="color" style="background-color: #' + c + '"></div>';
                 $('#colors').append(newDiv);
             }
         },
         setScheme: function(newScheme) {
             var self = this;
             if (newScheme == 'analogic') {
                 $('#add-complement').show();
             }
             else {
                 $('#add-complement').hide();
             }
             self.scheme.scheme(newScheme);
             self.generateColors();
         },
         addComplement: function() {
             var self = this;
             if ( $('#add-complement').hasClass('active') ) {
                 self.scheme.add_complement(false);
             } else {
                 self.scheme.add_complement(true);
             }
             self.generateColors();
         },
         setVariation: function(variation) {
             var self = this;
             self.scheme.variation(variation);
             self.generateColors();
         },
         setWebSafe: function(websafe) {
             var self = this;
             self.scheme.web_safe(websafe);
             self.generateColors();
         },
         randomHue:function() {
             var self = this;
             var h = Math.round(Math.random() * 360);
             self.scheme.from_hue(h);
             self.generateColors();
         }
     });
 })();
