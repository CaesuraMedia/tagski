#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrapper DBi class for the PictureTag many-to-many table.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
package Tagski::PictureTag;
use base 'Tagski::DBI';
use strict;
use warnings;
my @ColumnNames = (
    "PictureTag_id",
    "Picture_id",
    "Tag_id",
);
Tagski::PictureTag->table ('PictureTag');
Tagski::PictureTag->columns (All => @ColumnNames);
1;

