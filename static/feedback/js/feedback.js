/*
 * feedback.js
 *
 */

/////////////////////
// global variables
/////////////////////

var user;
var email;

var origin;
var feedback_type;

var app_callback;


var rendered = [];
var dirty = [];


////////////////////////
// backend interaction
////////////////////////

function get_origin() {
    x = encodeURIComponent(window.location.href).replace(/-/g, "--").replace(/%/g, "-")
    return x
}

// retrieve the set of existing feedback for (user, email, origin, feedback_type)
function backend_load() {
    /*
  alert("backend_load for user = [" + user +
        "], email = [" + email +
        "], origin = [" + origin +
        "], feedback_type = [" + feedback_type +
        "]");
    */
  var fbt = (feedback_type == 'idea') ? 'i' : 'q';

  // backend call
    $.getJSON('/feedback/' + fbt + '/' + get_origin() + "/", [], function (response) {
    // we expect an array of data records
    var data = [];
    var n = response.length;
    for (var i = 0; i < n; i++) {
      var rin = response[i];
      var rout = {
        // expected
        id: rin.id,
        feedback_type: (rin.feedbacktype == 'i') ? 'idea' : 'question',
        summary: rin.summary,
        description: rin.description,
        origin: rin.origin,
        user: rin.username,
        email: rin.email,
        // extra
        date: rin.pub_date,
        me2s: rin.metoo,
      };
      data[i] = rout;
    }

    dirty[feedback_type] = false;
 
    // render data
    feedback_render(data);
  });
}


// save the input for (user, email, origin, feedback_type)
function backend_save(input) {
  /*
  alert("backend_save for user = [" + user +
        "], email = [" + email +
        "], origin = [" + origin +
        "], feedback_type = [" + feedback_type +
        "], input = (description: [" + input.description + 
        "], summary: [" + input.summary + 
        "], me2s: [" + input.me2s + "])");
    */
  // backend call
  $.post('/feedback/', 
  { 
    feedbacktype: (feedback_type == 'idea') ? 'i' : 'q',
    summary: input.summary,
    description: input.description,
    origin: get_origin(),
    username: user,
    email: email 
  },
  function () {
    // deal with response
  }, 'json');

  alert("Vielen Dank, Ihr Feedback wurde gespeichert");
  dirty[feedback_type] = true;
  alert('cookie = [' + document.cookie + ']');
}

function me_too_toogle(id, checked) {
  $.post('/feedback/' + id, 
  { 
      metoo: checked,
  },
  function () {
    // deal with response
  }, 'json');
}

function feedback_render(data) {
    var html1 = '<div>' +
                '<table border="0" cellpadding="0">' +
                '<tr>' +
                '<td width="240">';
    // one 
    var html2 = ' (<a href="#" ' +
                'onclick="alert(' + "'";
    // details
    var html3 = "'" + ');" ' + 
                'title="Klicken Sie auf diesen Link, um zur Detailansicht zu gelangen.">Link</a>)' +
                '</td>' +
                '<td width="40" align="right">';
    // 224
    var html4a = '</td>' +
                // wuxxin: temporary disable
        '<td width="10">' +
        '<input type="checkbox"' +
        ' name="me2" value="1"';
    var html4b = ' title="W&auml;hlen Sie diese Auswahl, falls Sie dieses Feedback auch betrifft!"/>' +
        '</td>' +
        '</tr>' +
        '</table>' +
        '</div>';
    
    var id = feedback_type + 'Scrollable';
    var api = $('#' + id).scrollable();

    if (rendered[feedback_type]) {
      // remove entries from the scrollable
      api.getItems().remove();
      api.reload();  // might be not necessary
    }

    // add entries to scrollable
    var itemWrap = api.getItemWrap();
    var len = data.length;
    for (var i = 0; i < len; i++) {
        var d = data[i];
        var summary = d.summary;
        var details = d.description + "\\nvon " + d.user + " am " + d.date + "\\n";
        var checked = ' onchange="me_too_toogle(' + d.id + ', this.checked)" '
        
        if(d.me2s == 1)
            checked += " checked "
        if(d.me2s == 2)
            checked += " checked disabled "

        var html = html1 + summary + html2 + details + html3 +html4a + checked + html4b; // + me2s + html4;
        itemWrap.append(html);      
    }
    api.reload().end();
    rendered[feedback_type] = true;
}


// initialisation
// perform JavaScript after the document is scriptable. 
$(function() {

  //////////////////////////////
  // init jquery tools overlay
  //////////////////////////////

  var triggers = $('img#givefeedback').overlay({ 
    // some expose tweaks suitable for modal dialogs 
    expose: { 
      color: '#333', 
      loadSpeed: 200, 
      opacity: 0.9 
    }, 
    closeOnClick: false,

    // when the overlay is opened 
    onLoad: function (event) { 
      // TODO collect the user data from the host page
      user = 'Test Nutzer';
      email = 'nutzer@ecsdev.ep3.at';

      // reset the input
      $("#feedback textarea").val("");
      $("#feedback input").val("");

      // first open [for that user]?
      if (!feedback_type) {
          feedback_type = 'idea';
          backend_load();
      } else {
        if (dirty[feedback_type]) {
          backend_load();
        }
      }
    },

    // when the overlay is closed
    onClose: function (event) {
      // TODO call the application callback
      if (app_callback) {
        app_callback();
      }
    }

  });


  // on Submit handler
  $("#feedback form").submit(function(e) { 
    // close the overlay 
    triggers.eq(0).overlay().close(); 
 
    // collect user input
    var input = { 
      description: $("textarea", this).val(),
      summary: $("input", this).val(),
      me2s: []  // TODO me2 = ... 
    };

    // save input to server
    backend_save(input);
 
    // do not submit the form 
    return e.preventDefault(); 
  });


  ///////////////////////////////
  // init jquery tools tooltips
  ///////////////////////////////

  // select all desired input fields and attach tooltips to them 
  $("#ideaFeedbackForm :input, #questionFeedbackForm :input").tooltip({ 
 
    // place tooltip on the right edge 
    position: "center right", 
 
    // a little tweaking of the position 
    offset: [-50, -175], 
 
    // use the built-in fadeIn/fadeOut effect 
    effect: "fade", 
 
    // custom opacity setting 
    opacity: 1.0, 
 
    // use this single tooltip element 
    tip: '.tooltip' 

  });


  ///////////////////////////
  // init jquery tools tabs 
  ///////////////////////////

  // setup ul.tabs to work as tabs for each div directly under div.panes 
  $("ul.tabs").tooltabs("div.panes > div", {
   
    // when the tab is clicked (different tab, and at construction time)
    onClick: function (event, tabIndex) {
      if (!feedback_type) {
          return;
      }

      // determine and set feedback_type
      if (tabIndex == 0) {
        feedback_type = 'idea';
      } else if (tabIndex == 1) {
        feedback_type = 'question';
      } else {
        feedback_type = 'unknown';
      }

      // load it?
      if (!rendered[feedback_type]) {
        backend_load();
      }
    }

  });


  //////////////////////////////////
  // init jquery tools scrollables
  //////////////////////////////////

  $("div.scrollable").scrollable({ 
    vertical: true,  
    size: 5  // no. of elements visible at once
  // use mousewheel plugin 
  }).mousewheel();     
  
});
