#!/usr/bin/perl -w
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
# Class DBI mysql connection.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
use strict;
package Tagski::DBI;
use base 'Class::DBI';
Tagski::DBI->connection('dbi:mysql:tagski:localhost:3306', 'root', 'not_my_password');
1;

