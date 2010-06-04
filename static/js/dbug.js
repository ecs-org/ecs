dbug = {
   logged: [], firebug: false, debug: false,
   log: function(msg) {this.logged.push(msg);},
   enable: function() { if(this.firebug) this.debug = true; this.log = console.debug; this.log('enabling dbug');
       db = this; this.logged.each(function(msg){db.log(msg)}); this.logged=[];
   },
   disable: function(){ if(this.firebug) this.debug = false; this.log = function(){this.logged.push(msg);}; }
}
if (typeof console != "undefined") { // safari, firebug
   if (typeof console.debug != "undefined") { // firebug
       dbug.firebug = true; if(window.location.href.indexOf("debug=true")>0) dbug.enable();
   }
}             
