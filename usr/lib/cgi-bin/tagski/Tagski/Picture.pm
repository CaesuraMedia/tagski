#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrapper DBi class for the Picture table.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
package Tagski::Picture;
use base 'Tagski::DBI';
use strict;
use warnings;
my @ColumnNames = (
    "Picture_id", "Location", "Thumbnail",
);
Tagski::Picture->table ('Picture');
Tagski::Picture->columns (All => @ColumnNames);

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hand crafted SQL to get pictures of one tag name.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
Tagski::Picture->set_sql (filter_by_tag_id => qq{
   SELECT Picture.Picture_id, Picture.Thumbnail, Picture.Location
   FROM Picture, Tag, PictureTag
   WHERE Picture.Picture_id = PictureTag.Picture_id
   AND PictureTag.Tag_id = Tag.Tag_id
   AND Tag.Tag_id = ?
});
1;

