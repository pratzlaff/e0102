#!/usr/bin/perl

# adaptation of /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/compile_gainfit_results.pl

use strict;
use warnings;

my $datadir='/data/legs/rpete/data/e0102';

my @obsids = @ARGV;
if (not exists $ENV{CONTAMID}) {
  print STDERR "CONTAMID is unset, exiting\n";
  exit 1;
}

my $chip = "I3";
my $contam="contamN0015";
my $model="rgspn_mod_tbabs_tbvarabs_2apec_line_ratios_jd_v1.9.xcm";
my $emin="0.35";
my $emax="1.6";

print "# gain fit results for ${chip} with ${contam}\n";
print "# fitting between ${emin} - ${emax} keV\n";
print "# model: ${model}\n";
print "#\n";
print "#ObsID\tCons\tNe10\tNe10err\tNe9\tNe9err\tO8\tO8err\tO7\tO7err\tCstat\tDof\tRedChi\tChi\tSlope\tS_err\tOffset\tO_err\n";

for my $obsid (@obsids) {
  get_results($obsid);
}

sub get_results {

  my $obs = shift;
  $obs =~ s/^0*//g;
  $obs = sprintf '%05d', $obs;
  my $infile = "$datadir/fits/".$ENV{CONTAMID}."/$obs/${obs}_gainfit.log";
  my $const;
  my ($cstat, $O7norm, $O7err, $O8norm, $O8err);
  my ($Ne9norm, $Ne9err, $Ne10norm, $Ne10err);
  my ($dof, $chi, $slope, $slope_err, $offset, $off_err, $redchi);

  open (LOG, '<' , "$infile");

  while (<LOG>) {
    my @row = split (' ', $_);
    @row gt 1 or next;
    my $zeroth = $row[0];
    my $first = $row[1];
    my $second = $row[2];
    my $third = $row[3];
    my$fourth = $row[4];

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
# new on 20220402, XSPEC format for log files is different, so I must change the extraction
#
        elsif ($zeroth eq "#Fit" && $first eq "statistic" && $third eq "C-Statistic")
	{
	    $cstat = $row[4];
	}
#        elsif ($first eq "Reduced" && $second eq "chi-squared")
# new on 20220402, XSPEC format for log files is different, so I must change the extraction
#
        elsif ($zeroth eq "#" && $first eq "Null" && $second eq "hypothesis")
        {
#            $redchi = $row[4];
	    $dof = $row[7];
        }
#        elsif ($first eq "Chi-Squared" && $second eq "=")
# new on 20220402, XSPEC format for log files is different, so I must change the extraction
#
	elsif ($zeroth eq "#Test" && $first eq "statistic" && $third eq "Chi-Squared(model)")
        {
            $chi = $row[4];
        }
	elsif ($first eq "1" && $second eq "1" && $third eq "gain" && $fourth eq "slope")
	{
	    $slope=$row[5];
	    $slope_err=$row[7];
	}
	elsif ($first eq "2" && $second eq "1" && $third eq "gain" && $fourth eq "offset")
	{
	    $offset=$row[5];
	    $off_err=$row[7];
	}

    }	
    close (LOG);

# new on 20220402, XSPEC no longer reports redchi, I must calculate it
#    
    $redchi = $chi / $dof;
    
    printf "%5s\t%5.3f\t%8.3e\t%6.1e\t%8.3e\t%6.1e\t%8.3e\t%6.1e\t%8.3e\t%6.1e\t%8.3f\t%3.0f\t%5.2f\t%6.1f\t%5.3f\t%6.1e\t%8.3e\t%6.1e\n",${obs},${const},${Ne10norm},${Ne10err},${Ne9norm},${Ne9err},${O8norm},${O8err},${O7norm},${O7err},${cstat},${dof},${redchi},${chi},${slope},${slope_err},${offset},${off_err};

}

sub trim {
    my @out = @_;
    for (@out){
        s/^\s+//;
        s/\s+$//;
    }
    return wantarray ? @out: $out[0];
}

exit;
