// Bunch of things to do when loaded - jQuery.
//
var hash = [];
function onloadInit () {

   // Get HTML/CSS for each tag container. As. A. Global. Variable.  Learn about objects later....
   //
   $(".tag_container").each (function () {
      var this_id = this.id;
      var tag_id = this_id.replace(/tag_container_/, '');  // "tag_id_27" to make it a string
      hash[tag_id] = this.innerHTML;
   });

   // Show full filename when hovering.
   //
   $( ".img_tag_text_truncate" ).hover(
     function() {
         var full_text = $( this ).text();
         $( this ).removeClass("img_tag_text_truncate");
         $( this ).addClass("img_tag_text_truncate_show_full");
     }, function() {
         $( this ).addClass("img_tag_text_truncate");
         $( this ).removeClass("img_tag_text_truncate_show_full");
     }
   );
}

// When a tag selection box is clicked on and changed, then convert the tag container to
// show text box for rename(convert link to text input), and a go button, or just a go
// button for delete, remove  checkbox.
//
function do_selector (s_id) {

   // Get tag_id from the id for the select.
   //
   var tag_id = s_id.replace(/delete_or_rename_selector_tag_id_/, '');

   // Get selector object.
   //
   var selector = document.getElementById(s_id);

   // Set up an event on the body for this #tag_container_tag_id when clicking away,
   // changes the selection to nothing ---.  Restore the original HTML, set the selection
   // to 0 and the rename value to "".
   //
   $('body').click(function(event) {
       if (!$(event.target).closest("#tag_container_tag_id_" + tag_id).length) {
          document.getElementById("tag_container_tag_id_"             + tag_id).innerHTML = hash["tag_id_" + tag_id];
          document.getElementById("delete_or_rename_selector_tag_id_" + tag_id).selectedIndex = 0;
       };
    });

   // If first option is activly selected then do above too.
   //
   if (selector.selectedIndex === 0) {
       document.getElementById("tag_container_tag_id_"             + tag_id).innerHTML = hash["tag_id_" + tag_id];
       document.getElementById("delete_or_rename_selector_tag_id_" + tag_id).selectedIndex = 0;

   // Delete - show go button.  Remove the checkbox.
   // 
   } else if (selector.selectedIndex === 1) {
      document.getElementById("delete_or_rename_go_tag_id_" + tag_id).style.display = "block";
      document.getElementById("tag_checkbox_tag_id_"        + tag_id).style.display = "none";

   // Rename, change the link to textbox and add go button.  Remove the checkbox.
   //
   } else if (selector.selectedIndex === 2) {
      document.getElementById("delete_or_rename_go_tag_id_" + tag_id).style.display = "block";
      document.getElementById("tag_checkbox_tag_id_"        + tag_id).style.display = "none";

      // Get the TagText from the enclosing div title:
      //
      // <div id=tag_text_tag_id_[% Col %]
      // title="[% Col %]">
      //
      var tag_text = document.getElementById("tag_text_tag_id_" + tag_id).title;

      document.getElementById("tag_text_tag_id_"            + tag_id).innerHTML =
         "<input type=text" +
           " value=" + tag_text +
           " id=rename_tag_textbox_" + tag_id +
           " name=rename_tag_" + tag_id  +
           " size=" + (tag_text.length - 3) +
           ">";
      //document.getElementById("tag_container_tag_id_" + tag_id).class = "clearfix";
   } else {
      console.log("Program error - ony three tag_id selections in this js");
   }
}

// File Upload.
// Courtesy : https://www.kirsle.net/blog/entry/simple-perl-uploader-with-progress-bar
// This function is called when submitting the upload form.
function startUpload() {
        // Hide upload, replace with progress div.
        document.getElementById("upload_form").style.display = "none";
        document.getElementById("upload_section").style.display = "none";

        // Show the progress div.
        document.getElementById("progress_div").style.display = "block";

        // Begin making ajax requests.
        setTimeout("ping()", 100);

        // Allow the form to continue submitting.
        return true;
}

// Make an ajax request to check up on the status of the upload
function ping() {
        var ajax = new XMLHttpRequest();

        ajax.onreadystatechange = function () {
                if (ajax.readyState == 4) {
                        parse(ajax.responseText);
                }
        };

        ajax.open("GET", "/cgi-bin/tagski/tagski.cgi?ping=ping", true);
        ajax.send(null);
}

// React to the returned value of our ping test
function parse(txt) {
        // document.getElementById("debug").innerHTML = "received from server: " + txt;

        var parts = txt.split(":");
        if (parts.length == 3) {
                document.getElementById("received").innerHTML = parts[0];
                document.getElementById("total").innerHTML = parts[1];
                document.getElementById("percent").innerHTML = parts[2];
                document.getElementById("bar").style.width = parts[2] + "%";
        }

        // Ping again!
        setTimeout("ping()", 100);
}

// Zip Progress.
// This function is called when starting the zip process.
function startZip() {

        // Show the progress div.
        document.getElementById("zip_progress_div").style.display = "block";

        // Begin making ajax requests.
        setTimeout("zip_ping()", 100);

        // Allow the form to continue submitting.
        return true;
}

// Make an ajax request to check up on the status of the upload
function zip_ping() {
        var ajax = new XMLHttpRequest();

        ajax.onreadystatechange = function () {
                if (ajax.readyState == 4) {
                        parse_zip(ajax.responseText);
                }
        };

        ajax.open("GET", "/cgi-bin/tagski/tagski.cgi?zip_progress=zip_progress", true);
        ajax.send(null);
}

// React to the returned value of our ping test
function parse_zip(txt) {
        document.getElementById("debug").innerHTML = "received from server: " + txt;

        var parts = txt.split(":");
        if (parts.length == 3) {
                document.getElementById("zip_received").innerHTML = parts[0];
                document.getElementById("zip_total").innerHTML = parts[1];
                document.getElementById("zip_percent").innerHTML = parts[2];
                document.getElementById("zip_bar").style.width = parts[2] + "%";
        }

        // Ping again!
        setTimeout("zip_ping()", 100);
}

