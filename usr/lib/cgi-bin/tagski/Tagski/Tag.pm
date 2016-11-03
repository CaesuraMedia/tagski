#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Wrapper DBi class for the Tag table.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
package Tagski::Tag;
use base 'Tagski::DBI';
use strict;
use warnings;
my @ColumnNames = (
    "Tag_id",
    "TagText", 
);
Tagski::Tag->table ('Tag');
Tagski::Tag->columns (All => @ColumnNames);
1;

