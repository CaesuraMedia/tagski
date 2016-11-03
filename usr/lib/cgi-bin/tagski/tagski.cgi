#!/usr/bin/perl -w
use strict;
use CGI ':cgi-lib';
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use DBI;
# DBI->trace(15, '/var/www/tagski/dbi.log');
use File::Find::Rule;
use Data::Dumper;
use Image::Epeg qw(:constants);
use Image::JpegTran::AutoRotate;
use Class::DBI;
use CGI ':cgi-lib';
use CGI qw/ :cgi -debug /;
use Template;
use lib "Tagski/";
$|++;
my $debug = undef;

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Two columns on the webpage : Tag names and thumbnail images.  The tag names are
# entered in the text box then Tag Pictures go button to put the tagname and id
# into the Tags table.  The user then selects images and tags and presses the Tag
# Pictures - Go button to create entries in the PictureTags table.
#
# Pictures are uploaded using the multiple Choose Files/Upload buttons, and
# the original is stored in /img with a thumbnail and a medium-sized pic as well,
# so need lots of storage on /var/www/.  The medium one is used for the fancy
# gallery javascript plugin (click on an image, and see a gallery of medium pics).
#
# A tag name can be clicked and only those pics are shown.  When the Zip button 
# then a zip file containing the large images is created in /zipped/.
#
# Various operations are provided to change tag names, untag, delete tags and 
# remove pics.
#
# Upload and zip progress bars are shown in Ajax styley.  There is a status box
# showing what just happened and any errors (ie an uploaded file is not a JPG,
# all uploaded files must be a JPG ...).
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Class::DBI section : Database::TableName
#
use Tagski;
use Tagski::Picture;
use Tagski::Tag;
use Tagski::PictureTag;
use Tagski::Common;

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# First look at the params from the POST button, on first start it will be undef.
# Do the database updates that the params require, then get the data in the tables
# and display it.  The whole page is in a <FORM> so any button pushed will put all
# hidden, button checkbox etc data will appear in params.
#
# Two tables : Picture and Tag, and one many-to-many table PictureTag.  Tags can
# be added without a pic, pics can have many tags, tags can have many pics.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Print a header first, so we can bung text on the 
# screen anywhere from here.
#
print CGI::header();
warningsToBrowser(1);
my $TagIdFiltered = 0;
my $query = CGI->new;

# TODO : some things come here, not $query->params ... oops.
#
my $parameters = Vars;  # All parameters.

# See if any changes are coming in from $params.
#
my @StatusText;
my @ZipScriptText;

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# File upload : 
# Ping from javascript - send it back the status in the right format using print.
# Then quit - using tagski.cgi as a ping.cgi.
# TODO : make this a separate file.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if ($query->param('ping')) {
   if (-f "file_counter.txt") {
      open (FILE_COUNTER, "file_counter.txt");
      my $file_counts = <FILE_COUNTER>;
      close FILE_COUNTER;
      print $file_counts;  # outputs to javascript ajax call.
   } else {
      print "0:0:0";
   }
   exit (0);
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Zip progress
# Ping from javascript - send it back the status in the right format using print.
# Then quit - using tagski.cgi as a ping.cgi.
# TODO : make this a separate file.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
if ($query->param('zip_progress')) {
   if (-f "zip_counter.txt") {
      open (FILE_COUNTER, "zip_counter.txt");
      my $file_counts = <FILE_COUNTER>;
      close FILE_COUNTER;
      print $file_counts;  # outputs to javascript ajax call.
   } else {
      print "0:0:0";
   }
   exit (0);
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Check for the Zip operation - Create zip of tagged files.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
if ($query->param('ZipTaggedFiles')) {

   # Zip them up.
   #
   my $Link = Tagski::Common::ZipPicturesWithIdTo (
       $query->param('tag_filter'),
   );

   push @ZipScriptText, "Pictures available to download from this link :";
   (my $LinkText = $Link) =~ s/.*\///;
   push @ZipScriptText, "<a href=\"/$Link\">$LinkText</a>";
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete or rename a tag. And untag or remove picture.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# TODO, need to work out how to do this properly, 'rename_tag_4' => 'WasTagThree' does
# not appear in $query->param or $query->multi_param but does appear in Vars
# my $parameters = Vars;
#
# This needs tidying :
# $parameters = {
#   Delete : 
#   'delete_or_rename_tagid_1' => 'do_nothing',
#   'delete_or_rename_tagid_2' => 'do_nothing',
#   'delete_or_rename_tagid_3' => 'del_3',       # Delete tag 3
#   'delete_or_rename_go' => 'Go',
#   'delete_or_rename_tagid_4' => 'do_nothing',
#   ...
#   Or rename :
#
#   'delete_or_rename_tagid_8' => 'ren_8',
#   'rename_tag_8' => 'NewTagName',
#
#   Or remove pic :
#   'select_pic_id_22' => 'remove_pic_id_22',
#   'select_pic_id_21' => 'remove_pic_id_21',
#
#   Or untag :
#   'select_pic_id_20' => 'untag_26',
#
foreach my $key (sort keys %$parameters) {

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # Rename a tag.
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   #
   if ($key =~ /rename_tag_(\d+)/) {
      my $tag_id = $1;
      my $new_tag_name = $parameters->{$key};
      my @tag_objects = Tagski::Tag->search (tag_id => $tag_id);

      # Should only be one, but ...
      #
      my $old_tag_text = "";
      foreach my $tag_object (@tag_objects) {
         $old_tag_text = $tag_object->TagText;
         $tag_object->TagText($new_tag_name);
         $tag_object->update;
      }
      push @StatusText, "Tag $old_tag_text [id = $tag_id] is now $new_tag_name";
   }

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # Delete a tag.
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   #
   if ($key =~ /delete_or_rename_tagid_(\d+)/) {
      my $tag_id = $1;
      my $delete_or_not = $parameters->{$key};
      if ($delete_or_not =~ /del_/) {

         # Search and delete the Tag.
         #
         Tagski::Tag->search (tag_id => $tag_id)->delete_all;

         # Search and delete the PictureTag.
         #
         Tagski::PictureTag->search (tag_id => $tag_id)->delete_all;

         push @StatusText, "Tag id $tag_id is deleted";
      }
   }

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # Untag a picture.
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   #
   # 'select_pic_id_20' => 'untag_26'
   #
   if ($key =~ /select_pic_id_(\d+)/) {
      my $pic_id = $1;
      if ($parameters->{$key} =~ /^untag_(\d+)/) {
         my $tag_id = $1;
         Tagski::PictureTag->search (tag_id => $tag_id, picture_id => $pic_id)->delete_all;

         # Status, get from dB.
         #
         my @tag_objects     = Tagski::Tag->search     (tag_id     => $tag_id);
         my @picture_objects = Tagski::Picture->search (picture_id => $pic_id);

         push @StatusText, "Tag " . $tag_objects[0]->TagText . " removed from " . $picture_objects[0]->Location;

      }
   }

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # Remove pic from database. And from img.
   #    'select_pic_id_22' => 'remove_pic_id_22'
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   #
   if ($key =~ /select_pic_id_(\d+)/) {
      my $pic_id = $1;
      if ($parameters->{$key} =~ /remove_pic_id_$pic_id/) {
         my @picture_objects = Tagski::Picture->search (picture_id => $pic_id);
         push @StatusText, "Picture " . $picture_objects[0]->Location . " removed";
         unlink ('/var/www/tagski' . $picture_objects[0]->Location);
         unlink ('/var/www/tagski' . $picture_objects[0]->Thumbnail);
         unlink ('/var/www/tagski' . "Med_" . $picture_objects[0]->Thumbnail);
         Tagski::Picture->search (picture_id => $pic_id)->delete_all;
      }
   }

} # end foreach in $parameters - TODO : don't.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Check for uploaded images, add to db, then display.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
if ($query->param('upload_images')) {

   # Image names and filehandles are got from the query by two different
   # CGI methods - both should contain the same number of things.
   #
   my @image_names  = $query->param('upload_images');
   my @file_handles = $query->upload('upload_images');

   my $i = 0; # count into images.
   foreach my $file_handle (@file_handles) {

      # For files processed bar - send NumDone:Total:PC to a file for 
      # reading when this gets called again as ping.cgi.
      #
      # See https://www.kirsle.net/blog/entry/simple-perl-uploader-with-progress-bar
      #
      # TODO : make this based on a session id like kirsle did, not one file/one-and-only
      #        user (me).
      #
      my $Percent =  sprintf ("%.1f", ($i / scalar @file_handles) * 100);
      open (FILE_COUNTER, ">file_counter.txt") || die "Cannot open file_counter.txt";
      print FILE_COUNTER "$i:" . scalar @file_handles . ":" . $Percent;
      close FILE_COUNTER;

      my $image_name = $image_names[$i];
      $i++; # increment as soon as not need so next can be used in the loop.

      # Do some things with the image name.
      #
      $image_name =~ s/\s//g;   # remove any spaces.

      my $io_handle = $file_handle->handle;
      if ($io_handle) {

         # Needs to be a JPG for the thumbnail prog to work.
         #
         my $type = $query->uploadInfo($file_handle)->{'Content-Type'};
         # print "image_name is $image_name, type is $type <br />\n";
         unless ($type eq "image/jpeg") {
            push @StatusText, "$image_name is not a JPG, ignored.";
            next;
         }

         # From perldoc CGI :
         #
         open ( my $out_file,'>>',"/var/www/tagski/img/Large_$image_name" );
         my $buffer;
         while ( my $bytesread = $io_handle->read($buffer,1024) ) {
            print $out_file $buffer;
         }
         # end perldoc CGI.

         # Auto-rotate! Image::JpegTran::AutoRotate;
         #
         auto_rotate ("/var/www/tagski/img/Large_$image_name");

         # Create thumbnail from this image.
         #
         my $epg = new Image::Epeg( "/var/www/tagski/img/Large_$image_name" );
         $epg->resize( 150, 150, MAINTAIN_ASPECT_RATIO );
         $epg->write_file( "/var/www/tagski/img/$image_name" );

         # Create a medium one for the lightbox.
         #
         $epg = new Image::Epeg( "/var/www/tagski/img/Large_$image_name" );
         $epg->resize( 850, 850, MAINTAIN_ASPECT_RATIO );
         $epg->write_file( "/var/www/tagski/img/Med_$image_name" );

         # Now put this into thse database. 
         # TODO : Really only need one extra column in Picture - filename.
         #
         my $NewPictureRow = {
            Location  => "/img/Large_$image_name",
            Thumbnail => "/img/$image_name", 
         };
         my $NewPictureObject = Tagski::Picture->find_or_create ($NewPictureRow); # insert if not there

      } else {
         push @StatusText, "Ooops, image name \"$image_name\" cannot be loaded";
      }

   } # end foreach file handle.
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# If TagPictures then see if there is a new tag, add its id to the param list,
# then get the pic/tag associations. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
if ($query->param('TagPictures')) {

   # If a new tag is to be added, then add it to the dB.
   #
   my $TagName = $query->param('add_tag');

   unless ($TagName eq "") {

      my $NewTagRow = {'TagText'   => $TagName};
      my $RowObject = Tagski::Tag->find_or_create ($NewTagRow); # insert if not there

      print "Tag id is : " . $RowObject->tag_id . "\n";

      # Insert the new tag_id into the params for later on where we get tag_ids
      # from the params for tagging selected pictures.
      #
      # 'tag_id_3' => 'on'
      $query->param(
            -name  => 'tag_id_' . $RowObject->tag_id,
            -value => 'on',
      );

      push @StatusText, "Added new tag : $TagName";

   } else {
      push @StatusText, "Empty tag text, no tag added";
   }

   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   # Do The Thing - create entries for each pic and tag in PictureTag.
   #
   # On tagging :
   #   $params = { 'TagPictures' => 'Tag Pictures - go',
   #               'pic_id_1' => 'on',
   #               'pic_id_2' => 'on',
   #               'pic_id_8' => 'on',
   #               'tag_id_3' => 'on',
   #               'tag_id_4' => 'on',
   #               'tag_id_6' => 'on',
   #               'add_tag' => '' };
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   #
   # Create a hash :
   #   http://search.cpan.org/~tmtm/Class-DBI-v3.0.17/lib/Class/DBI.pm#insert
   #   pic_ids : 25, 77
   #   tag_ids : 14,13,12
   #
   my @PicIds;
   my @TagIds;
   foreach my $Key ($query->param) {                    # array of all keys in the params
      push @PicIds, $1 if ($Key =~ /^pic_id_(\d+)$/);   # lots of _pic_id
      push @TagIds, $1 if ($Key =~ /^tag_id_(\d+)$/);
   }

   # Check to see if there is at least one pic id and one tag id.
   #
   if (@PicIds > 0 && @TagIds > 0) {

      # All combos of pic and tag ids into the many-to-many PictureTag table.
      # There appears to be no way of using insert on more than one row.
      #
      foreach my $PicId (@PicIds) {
         foreach my $TagId (@TagIds) {
            Tagski::PictureTag->find_or_create ( # insert if not there
               {
                  Picture_id => $PicId,
                  Tag_id     => $TagId,
               }
            );
         }
      }
      push @StatusText, "Tagged " . scalar @PicIds . " pictures with " . scalar @TagIds . " tags.";
   } else {
      push @StatusText, "Nothing tagged : num pics chosen : " . scalar @PicIds . ", num tags chosen : " . scalar @TagIds . ".";
   }

} # end TagPictures


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get all data from database, updated from above.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
my @TagRows;
my $TagIteration     = Tagski::Tag->retrieve_all();
while (my $RowTagObject = $TagIteration->next) {

   # For TT.
   #
   my @Row = ($RowTagObject->Tag_id, $RowTagObject->TagText);
   push @TagRows, \@Row;
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Picture details from the database and that tag id->text hash.
#
# If tag_filter is in params via tagski?tag_filter=34 then filter the 
# pictures by tag.  Otherwise load all of them.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
my @PictureObjects;
if ($query->param('tag_filter') && ! $query->param('Refresh')) {

   my $FilterTagId = $query->param('tag_filter');
   @PictureObjects = Tagski::Picture->search_filter_by_tag_id($FilterTagId);
   $TagIdFiltered = $FilterTagId;
} else {
   @PictureObjects  = Tagski::Picture->retrieve_all();
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get all pics for TT @PictureRows - in reverse, retrieve_all gets them in id
# order, want latest pic first.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
my @PictureRows;
foreach my $RowPictureObject (reverse @PictureObjects) {

   # Get the tags for this picture.
   #
   my $tag_text_hash = {};
   my @pictag_objects = Tagski::PictureTag->search (picture_id => $RowPictureObject->picture_id);
   foreach my $pictag_object (@pictag_objects) {
      my @tag_objects = Tagski::Tag->search (tag_id => $pictag_object->tag_id);
      foreach my $tag_object (@tag_objects) {
         $tag_text_hash->{$tag_object->tag_id} = $tag_object->TagText;
      }
   }

   # Picture details for TT.
   #
   my $picture_name = $RowPictureObject->location;
   $picture_name =~ s/^.*\///;
   $picture_name =~ s/Large_//; # text in the box.

   # 0: hash of tags, 1: DSC_4444.JPG, 2: 23
   #
   my @Row = (
              $tag_text_hash,
              $picture_name,
              $RowPictureObject->picture_id,
              );
   push @PictureRows, \@Row;
}

print Data::Dumper->Dump ([$parameters], ["parameters"]) if ($debug);

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data to be displayed in HTML via variables in TT.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
my $file = 'tagski.html';
my $vars = {
   Tags          => \@TagRows,
   Pictures      => \@PictureRows,
   StatusText    => \@StatusText,
   TagIdFiltered => $TagIdFiltered,
   ZipScriptText => \@ZipScriptText,
};

my $template = Template->new({

    # Where to find template files.
    #
    INCLUDE_PATH => ['/var/www/tagski/tt/src',
                     '/var/www/tagski/tt/lib'],

    # pre-process lib/config to define any extra values
    #
    PRE_PROCESS  => 'config',
});

$template->process($file, $vars)
    || die "Template process failed: ", $template->error(), "\n";

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete file and zip counters if they exist.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
if (-f "file_counter.txt") {
   unlink ("file_counter.txt");
}
if (-f "zip_counter.txt") {
   unlink ("zip_counter.txt");
}
