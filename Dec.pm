#!/usr/bin/perl

package Dec;
sub decoder
{
        my $command = "python enc_dec.py -d " . $_[0];
        my $tmp = `$command`;
        chomp $tmp;
        return $tmp;
}
1;
