#!/usr/local/bin/perl

# adaptation of /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/compile_shifted_fit_results.pl

use strict;
use warnings;
use Carp;
use Config;
use Data::Dumper;
use FindBin;
use 5.010;

my $version = '0.1';

use Getopt::Long;
my %default_opts = (
		    datadir => qx!$FindBin::Bin/datadir!,
		    srcdir => $FindBin::Bin,
		    );
my %opts = %default_opts;
GetOptions(\%opts,
	   'help!', 'version!', 'debug!',
	   'datadir=s', 'srcdir=s',
	   ) or die "Try --help for more information.\n";
if ($opts{debug}) {
  $SIG{__WARN__} = \&Carp::cluck;
  $SIG{__DIE__} = \&Carp::confess;
}
$opts{help} and _help();
$opts{version} and _version();

my %types = ( 'shift' => 1, line =>1, gain => 1 );
my $type = shift;
if (not exists $types{$type}) {
  print STDERR "invalid type='$type', exiting\n";
  exit 1;
}

my @obsids = @ARGV;

if (not exists $ENV{CONTAMID}) {
  print STDERR "CONTAMID is unset, exiting\n";
  exit 1;
}

my $chip = uc($ENV{DET});
my $model="rgspn_mod_tbabs_tbvarabs_2apec_line_ratios_jd_v1.9.xcm";
my $emin="0.35";
my $emax="1.6";

for my $obsid (@obsids) {

  get_results($obsid);
  $type eq 'shift' || next;

  my @match = `grep --no-filename ",$obsid\$" "$opts{srcdir}/../data/simul/"[is]3`;
  @match and $obsid = +(split '=', $match[0])[0], get_results($obsid);

}

exit;

sub print_header {
  state $printed = 0;
  return if $printed;

  my $type = shift;
  $printed = 1;

  my %print_subs = (
		gain => \&print_header_gainfit,
		line => \&print_header_linefit,
		shift => \&print_header_shiftfit,
	       );
  $print_subs{$type}->(@_);
}

sub print_header_gainfit {
  print "# gain fit results for ${chip} with CONTAMID=$ENV{CONTAMID}\n";
  print "# fitting between ${emin} - ${emax} keV\n";
  print "# model: ${model}\n";
  print "#\n";
  print "#ObsID\tCons\tNe10\tNe10err\tNe9\tNe9err\tO8\tO8err\tO7\tO7err\tCstat\tDof\tRedChi\tChi\tSlope\tS_err\tOffset\tO_err\n";
}

sub print_header_linefit {
  print "# fit results for ${chip} with CONTAMID=$ENV{CONTAMID}\n";
  print "# fitting between ${emin} - ${emax} keV\n";
  print "# model: ${model} w/ line energies shifted & \"big 4\" energies free\n";
  print "#\n";
  print "#ObsID\tCons\tNe10\tNe10err\tNe9\tNe9err\tO8\tO8err\tO7\tO7err\tCstat\tDof\tRedChi\tChi\tNe10en\tNe10lo\tNe10hi\tNe9en\tNe9lo\tNe9hi\tO8en\tO8lo\tO8hi\tO7en\tO7lo\tO7hi\n";
}

sub print_header_shiftfit {
  my $val = shift;
  print "# fit results for ${chip} with CONTAMID=$ENV{CONTAMID} and gain adjustment (data shifted)\n";
  print "# fitting between ${emin} - ${emax} keV\n";
  print "# model: ${model}\n";
  print "# lo and hi give 1-sigma confidence interval\n";
  print "#\n";
  if (exists $val->{Mgnorm}) {
    print "#ObsID\tCons\tConsLo\tConsHi\tNe10\tNe10err\tNe10lo\tNe10hi\tNe9\tNe9err\tNe9lo\tNe9hi\tO8\tO8err\tO8lo\tO8hi\tO7\tO7err\tO7lo\tO7hi\tMg\tMgerr\tMglo\tMghi\tCstat\tDof\tRedChi\tChi\n";
  } else {
    print "#ObsID\tCons\tConsLo\tConsHi\tNe10\tNe10err\tNe10lo\tNe10hi\tNe9\tNe9err\tNe9lo\tNe9hi\tO8\tO8err\tO8lo\tO8hi\tO7\tO7err\tO7lo\tO7hi\tCstat\tDof\tRedChi\tChi\n";
  }
}

sub get_results {

  my $obs=shift;
  $obs =~ s/^0*//g;
  $obs = sprintf '%05d', $obs;
  my $infile = "$opts{datadir}/fits/".$ENV{CONTAMID}."/$obs/${obs}_${type}fit.log";

  # e.g.,
  #Model Model Component  Parameter  Unit     Value
  # par  comp
  #   1    1   constant   factor              1.14149      +/-  2.71383E-02
  #  29   11   gaussian   LineE      keV      1.32855      +/-  6.12033E-03
  #  61   21   gaussian   norm                1.52427E-03  +/-  1.42802E-04


  my %comps = (
		 slope    => [1, 1, 'slope'],
		 offset   => [2, 1, 'offset'],
		 Cons     => [1, 1, 'factor'],
		 Ne10norm => [61, 21, 'norm'],
		 Ne10en   => [59, 21, 'LineE'],
		 Ne9norm  => [67, 23, 'norm'],
		 Ne9en    => [65, 23, 'LineE'],
		 O8norm   => [118, 40, 'norm'],
		 O8en     => [116, 40, 'LineE'],
		 O7norm   => [127, 43, 'norm'],
		 O7en     => [119, 41, 'LineE'],
		 Mgnorm   => [37, 13, 'norm'],
		);
  my (%val, %err, %lo, %hi, %stat);

  open (LOG, '<', "$infile");

  while (<LOG>) {

    my @F = split (/\s+/, $_);
    @F > 4 or next;

    if (@F >= 8) {
      for my $key (keys %comps) {
	if ($F[1] eq $comps{$key}[0] and
	    $F[2] eq $comps{$key}[1] and
	    $F[4] eq $comps{$key}[2]
	   ) {
	  if ($F[4] eq 'LineE') {
	    $val{$key} = $F[6];
	    $err{$key} = $F[8];
	  } else {
	    $val{$key} = $F[5];
	    $err{$key} = $F[7];
	  }
	}
	next;
      }

      if ($F[1] eq "Null" and $F[2] eq "hypothesis") {
	$stat{dof} = $F[7];
	next;
      }

      if ($F[0] eq "#Fit" and $F[1] eq "statistic" and $F[3] eq "C-Statistic") {
	$stat{cstat} = $F[4];
	next;
      }
      if ($F[0] eq "#Test" and $F[1] eq "statistic" and $F[3] eq "Chi-Squared(model)") {
	$stat{chi} = $F[4];
	next;
      }
    }

    if (@F == 5) {
      for my $key (keys %comps) {
	if ($F[1] eq $comps{$key}[0]) {
	  $lo{$key} = $F[2];
	  $hi{$key} = $F[3];
	}
	next;
      }
    }

  }
  close (LOG);

  my @h = \(%val, %err, %lo, %hi);
  for my $h (@h) {
    exists $h->{O7norm} and $h->{O7norm}*=2.09009;
  }

# 20220402, XSPEC no longer reports redchi, so I must calculate it
#
  $stat{redchi} = $stat{chi} / $stat{dof};

  my %print_fit = (
		   gain => \&print_fit_gainfit,
		   line => \&print_fit_linefit,
		   shift => \&print_fit_shiftfit,
		  );

  print_header($type, \%val);
  $print_fit{$type}->($obs, \(%val, %err, %lo, %hi, %stat));

}

sub print_fit_gainfit {
  my ($obs, $val, $err, $lo, $hi, $stat) = @_;

  my @fmt = qw/ %5s %5.3f /;
  my @p = ($obs, $val->{Cons});

  for my $p (qw/ Ne10norm Ne9norm O8norm O7norm /) {
    if (exists $val->{$p}) {
      push(@p, map { $_->{$p} } ($val, $err));
      push @fmt, qw/ %8.3e %6.1e /;
    }
  }

  push @p, @{$stat}{qw/ cstat dof redchi chi /};
  push @fmt, qw/ %8.3f %3.0f %5.2f %6.1f /;

  for my $p (qw/ slope offset /) {
    if (exists $val->{$p}) {
      push(@p, map { $_->{$p} } ($val, $err));
    }
  }
  push @fmt, qw/ %5.3f %6.1e %8.3e %6.1e /;


  printf join("\t", @fmt)."\n", @p;

}

sub print_fit_linefit {
  my ($obs, $val, $err, $lo, $hi, $stat) = @_;

  my @fmt = qw/ %5s %5.3f /;
  my @p = ($obs, $val->{Cons});

  for my $p (qw/ Ne10norm Ne9norm O8norm O7norm /) {
    if (exists $val->{$p}) {
      push(@p, map { $_->{$p} } ($val, $err));
      push @fmt, qw/ %8.3e %6.1e /;
    }
  }

  push @p, @{$stat}{qw/ cstat dof redchi chi /};
  push @fmt, qw/ %8.3f %3.0f %5.2f %6.1f /;

  for my $p (qw/ Ne10en Ne9en O8en O7en /) {
    if (exists $val->{$p}) {
      push(@p, map { $_->{$p} } ($val, $lo, $hi));
      push @fmt, qw/ %7.5f %7.5f %7.5f /;
    }
  }

  printf join("\t", @fmt)."\n", @p;

}

sub print_fit_shiftfit {
  my ($obs, $val, $err, $lo, $hi, $stat) = @_;

  my @fmt = ('%5s', ('%5.3f')x3);
  my @p = ($obs, $val->{Cons}, $lo->{Cons}, $hi->{Cons});

  for my $p (qw/ Ne10norm Ne9norm O8norm O7norm Mgnorm /) {
    if (exists $val->{$p}) {
      push(@p, map { $_->{$p} } ($val, $err, $lo, $hi));
      push @fmt, qw/ %8.3e %6.1e %8.3e %8.3e /;
    }
  }

  push @p, @{$stat}{qw/ cstat dof redchi chi /};
  push @fmt, qw/ %8.3f %3.0f %5.2f %6.1f /;

  printf join("\t", @fmt)."\n", @p;
}


sub _help {
  exec("$Config{installbin}/perldoc", '-F', $FindBin::Bin . '/' . $FindBin::RealScript);
}

sub _version {
  print $version,"\n";
  exit 0;
}

=head1 NAME

compile_fit results - Compiles E0102 XSPEC fit results

=head1 SYNOPSIS

compile_fit_results gain|line|shift [obsid1 obsid2 ...]

=head1 DESCRIPTION

For each obsid given in the argument list, look up the appropriate XSPEC
log file. Requires environment variable CONTAMID to be set, as this is
where the fit appropriate log will be found under C<datadir>.

=head1 OPTIONS

=over 4

=item --help

Show help and exit.

=item --version

Show version and exit.

=back

=head1 AUTHOR

Pete Ratzlaff E<lt>pratzlaff@cfa.harvard.eduE<gt> Sept 2025

=head1 SEE ALSO

perl(1).

=cut

