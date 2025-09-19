#!/usr/local/bin/perl

# adaptation of /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/compile_shifted_fit_results.pl

use strict;
use warnings;
use Data::Dumper;

my $datadir='/data/legs/rpete/data/e0102';

my @obsids = @ARGV;
if (not exists $ENV{CONTAMID}) {
  print STDERR "CONTAMID is unset, exiting\n";
  exit 1;
}

my $chip = uc($ENV{DET});
my $model="rgspn_mod_tbabs_tbvarabs_2apec_line_ratios_jd_v1.9.xcm";
my $emin="0.35";
my $emax="1.6";

print "# fit results for ${chip} with CONTAMID=$ENV{CONTAMID} and gain adjustment (data shifted)\n";
print "# fitting between ${emin} - ${emax} keV\n";
print "# model: ${model}\n";
print "# lo and hi give 1-sigma confidence interval\n";
print "#\n";
print "#ObsID\tCons\tConsLo\tConsHi\tNe10\tNe10err\tNe10lo\tNe10hi\tNe9\tNe9err\tNe9lo\tNe9hi\tO8\tO8err\tO8lo\tO8hi\tO7\tO7err\tO7lo\tO7hi\tCstat\tDof\tRedChi\tChi\n";

for my $obsid (@obsids) {
  get_results($obsid);
}

sub get_results {

  my $obs=shift;
  $obs =~ s/^0*//g;
  $obs = sprintf '%05d', $obs;
  my $infile = "$datadir/fits/".$ENV{CONTAMID}."/$obs/${obs}_shiftfit.log";

  my ($const, $conslo, $conshi);
  my $cstat;
  my ($O7norm, $O7err, $O7en, $O7en_err, $o7lo, $o7hi);
  my ($O8norm, $O8err, $O8en, $O8en_err, $o8lo, $o8hi);
  my ($Ne9norm, $Ne9err, $Ne9en, $Ne9en_err, $ne9lo, $ne9hi);
  my ($Ne10norm, $Ne10err, $Ne10en, $Ne10en_err, $ne10lo, $ne10hi);
  my ($dof, $chi, $redchi);

  open (LOG, '<', "$infile");

  while (<LOG>) {
	my @row = split (/\s+/, $_);
	@row gt 1 or next;
        my $zeroth = $row[0];
	my $first = $row[1];
	my $second = $row[2];
	my $third = $row[3];
	my $fourth = $row[4];

	if ($first eq "1" && $second eq "1" && $fourth eq "factor")
	{
	    $const = $row[5];
	}
	elsif ($first eq "61" && $second eq "21")
	{
	    $Ne10norm = $row[5];
	    $Ne10err = $row[7];
	}
	elsif ($first eq "67" && $second eq "23")
	{
	    $Ne9norm = $row[5];
	    $Ne9err = $row[7];
	}
	elsif ($first eq "118" && $second eq "40")
	{
	    $O8norm = $row[5];
	    $O8err = $row[7];
	}
	elsif ($first eq "127" && $second eq "43")
	{
	    $O7norm = $row[5]*2.09009;# we fit the normalization of the O7 f line in the triplet, but are reporting the normalization of the r line
	    $O7err = $row[7]*2.09009;
	}
#	elsif ($first eq "C-Statistic" && $second eq "=")
# 20220402, XSPEC format for the log files is different, so I must change the extraction
#
        elsif ($zeroth eq "#Fit" && $first eq "statistic" && $third eq "C-Statistic")
	{
	    $cstat = $row[4];
	}
	elsif ($first eq "1")
	{
	    $conslo=$second;
	    $conshi=$third;
	}
	elsif ($first eq "61")
	{
	    $ne10lo=$second;
	    $ne10hi=$third;
	}
	elsif ($first eq "67")
	{
	    $ne9lo=$second;
	    $ne9hi=$third;
	}
	elsif ($first eq "118")
	{
	    $o8lo=$second;
	    $o8hi=$third;
	}
	elsif ($first eq "127")
	{
	    $o7lo=$second*2.09009;
	    $o7hi=$third*2.09009;
	}
#        elsif ($first eq "Reduced" && $second eq "chi-squared")
# 20220402, XSPEC format for the log files is different, so I must change the extraction
#
	 elsif ($zeroth eq "#" && $first eq "Null" && $second eq "hypothesis")
        {
#            $redchi = $row[4];
	    $dof = $row[7];
        }
#        elsif ($first eq "Chi-Squared" && $second eq "=")
# 20220402, XSPEC format for the log files is different, so I must change the extraction
#
        elsif ($zeroth eq "#Test" && $first eq "statistic" && $third eq "Chi-Squared(model)")
        {
            $chi = $row[4];
        }


    }	
    close (LOG);

# 20220402, XSPEC no longer reports redchi, so I must calculate it
#
    $redchi = $chi / $dof;

    
    printf "%5s\t%5.3f\t%5.3f\t%5.3f\t%8.3e\t%6.1e\t%8.3e\t%8.3e\t%8.3e\t%6.1e\t%8.3e\t%8.3e\t%8.3e\t%6.1e\t%8.3e\t%8.3e\t%8.3e\t%6.1e\t%8.3e\t%8.3e\t%8.3f\t%3.0f\t%5.2f\t%6.1f\n",${obs},${const},${conslo},${conshi},${Ne10norm},${Ne10err},${ne10lo},${ne10hi},${Ne9norm},${Ne9err},${ne9lo},${ne9hi},${O8norm},${O8err},${o8lo},${o8hi},${O7norm},${O7err},${o7lo},${o7hi},${cstat},${dof},${redchi},${chi};

}

exit;
