# tagski
First attempt at getting some Perl on GitHub - a simple CGI picture tagger.

Tagski is a web-based picture tagger, mainly developed by me in order to keep my Perl skills alive, and make something useful -  some Ubuntu picture taggers I downloaded weren't simple enough.  Probably only useful to me, but I wanted something on GitHub, and I spent many happy hours on this thing.

So : Tagski needs mysql, apache, perl (and lots of CPAN).  It provides a single page where images can be uploaded to the server, then displayed on the page.  Tag names can be entered and then pictures can be tagged with the tag names.  That's about it.  Three mysql tables - Tag, Picture and PictureTag (see the var/www/tagski/sql/tagski.sql file).

I'll leave the setup to the user for now, there are some TODO's and some don'ts too. No warrantee etc etc.

Here's a synopsis:

Two columns on the webpage : Tag names and thumbnail images.  The tag names are
entered in the text box then Tag Pictures go button to put the tagname and id
into the Tags table.  The user then selects images and tags and presses the Tag
Pictures - Go button to create entries in the PictureTags table.

Pictures are uploaded using the multiple Choose Files/Upload buttons, and
the original is stored in /img with a thumbnail and a medium-sized pic as well,
so need lots of storage on /var/www/.  The medium one is used for the fancybox
gallery javascript plugin (click on an image, and see a gallery of medium pics).

A tag name can be clicked and only those tagged pics are shown.  When the Zip button is clicked  a zip file containing the large images is created in /zipped/ and a link to download it appears.  Most useful bit.

Various operations are provided to change tag names, untag, delete tags and
remove pics.

Upload and zip progress bars are shown in Ajax styley.  There is a status box
showing what just happened and any errors (ie an uploaded file is not a JPG,
all uploaded files must be a JPG ...).

Uses CGI.pm, Class::DBI, Template Toolkit, jQuery, Image::Epeg (fast thumbnailer) etc.

Installation instructions on a clean Ubuntu 16.04 are here : http://chintzbaby.com/wp/caesuramedia/2016/11/04/tagski-picture-tagger-install/ 

Enjoy!
