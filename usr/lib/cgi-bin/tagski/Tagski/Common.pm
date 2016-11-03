#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Common methods used by all kinds of other methods.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
package Tagski::Common;
use strict;
use warnings;
use Tagski::Picture;
use base 'Tagski::DBI';
use Data::Dumper;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS);
use Archive::Zip::SimpleZip qw($SimpleZipError);

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Zip the files into one file for download.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub ZipPicturesWithIdTo {

   my $FilteredByTag     = shift;
   my @PictureObjects = Tagski::Picture->search_filter_by_tag_id($FilteredByTag);

   # DirectoryToZipTo docroot/zipped
   #
   my $DirectoryToZipTo = '/var/www/tagski/zipped';

   # Get tag text for zipfile name.
   #
   my @tag_objects = Tagski::Tag->search (tag_id => $FilteredByTag);

   # Only one.
   #
   my $TagText = $tag_objects[0]->TagText;
   $TagText =~ s/\s+/_/g;

   my $ZipFilename = "$DirectoryToZipTo/PicsTagged_" . $TagText . ".zip";
   my $ZippedFile = new Archive::Zip::SimpleZip $ZipFilename;

   my $i = 1;
   foreach my $PictureObject (@PictureObjects) {

      # 'Location' is /img/DSC_7777.JPG, so add the docroot.
      #
      my $SourceLargePic = '/var/www/tagski/' . $PictureObject->location;

      if (-f $SourceLargePic) {
         $ZippedFile->add( $SourceLargePic,
                           FilterName => sub { s/^.*\/Large_// }   # remove directory structure and
                                                                   # the word Large_ from file in zip.
         ) or die "Cannot add $SourceLargePic to $ZipFilename : $SimpleZipError";

         # Progress bar!
         #
         my $Percent =  sprintf ("%.1f", ($i / scalar @PictureObjects) * 100);
         open (FILE_COUNTER, ">zip_counter.txt") || die "Cannot open zip_counter.txt";
         print FILE_COUNTER "$i:" . scalar @PictureObjects . ":" . $Percent;
         close FILE_COUNTER;
         $i++;

      } else {
         return "File " . $SourceLargePic . " does not exist.";
      }
   }
   $ZippedFile->close() or die "Cannot create $ZipFilename : $SimpleZipError";

   # Rel to docroot.
   #
   (my $rel_location = $ZipFilename) =~ s/.*zipped\//zipped\//;  # could be a tag name with "zipped" in.
   return $rel_location;
};             

1;
