srcdir=/data/legs/rpete/flight/e0102/src
datadir=/data/legs/rpete/data/e0102

o7_cutoff=2020
o8_cutoff=2023

# python3 Ne_ratio.py /data/legs/rpete/data/e0102/fits/ciao4.18.0_caldb4.12.3/results/shiftfits_s3.txt
Ne_ratio=0.9528

# Best-fit values for line normalizations on S3, 2003-2010
declare -A Params=(
    [1]=1.068      # cons
    [127]=1.267e-3 # O7
    [118]=4.307e-3 # O8
    [67]=1.336e-3  # Ne9
    [61]=1.402e-3  # Ne10
    [37]=0.120e-3  # Mg11
)

contelem_l=/data/legs/rpete/flight/acis_contam/xspec_model/mymodels

obsids()
{
    [ $# -eq 1 ] || {
	echo "Usage: $0 det" 1>&2
	return 1
    }
    local det=${1,,}
    \grep '^[0-9]' "${srcdir}/../data/obsids/$det.lst" | cut -f 1 #| tail -1
}

obsid_date()
{
    local obsids="$@"
    for o in $obsids; do
	o=$(printf %05d $((10#"$o")))
	\grep -h ^$o "$datadir/obs_info/"[is]3.txt  | cut -f2
    done
}

obsid_chipy() {
    local obsid="$1"
    chipy=$(\grep -h "^$obsid" "$datadir"/obs_info/[is]3.txt | perl -anle 'print int($F[3])')
    [ -z "$chipy" ] && {
	echo "Could not find ObsID $obsid in '$datadir'/obs_info/[is]3.txt" >&2
	return 1
    }
    str=High
    [ $chipy -lt 682 ] && str=Mid
    [ $chipy -lt 341 ] && str=Low
    echo $str
}

obsid_year() {
    local obsid="$1"

    # if the ObsID is a simul fit, use the first obsid
    obsid_simul=$(\grep -h "^$obsid=" "$srcdir/../data/simul/$DET"  | perl -F, -anle 'print $F[1]')
    [ -n "${obsid_simul}" ] && obsid=${obsid_simul}
    \grep -h "^${obsid}" "$datadir"/obs_info/[is]3.txt | perl -anle 'print int($F[1])'
}

energy_shift_plots()
{
    local obsids
    [[ "$DET" =~ ^[is]3$ ]] || {
	echo "DET must be i3|s3" 1>&2
	return 1
    }

    [ -z "$CONTAMID" ] && {
	echo "CONTAMID must be set" 1>&2
	return 1
    }

    [ $# -ge 1 ] && {
	obsids="$@"
    } || {
	obsids=$(obsids $DET)
    }

    obsids_=
    for obsid in $obsids; do
	obsids_+=" $(printf %05d $((10#$obsid)))"
    done
    obsids=$obsids_
    parallel -j 16 python3 $srcdir/plot_energy_shift.py -o $datadir/fits/$CONTAMID/{}/{}_energy_shift.pdf {} ::: $obsids

    pdffile=$datadir/fits/$CONTAMID/results/energy_shift_${DET}.pdf
    files=
    for obsid in $obsids; do
	files+=" $datadir/fits/$CONTAMID/$obsid/${obsid}_energy_shift.pdf"
    done
    pdftk $files cat output $pdffile
}


psmerge_xspec()
{
    local obsids
    [[ "$DET" =~ ^[is]3$ ]] || {
	echo "DET must be i3|s3" 1>&2
	return 1
    }

    [ -z "$CONTAMID" ] && {
	echo "CONTAMID must be set" 1>&2
	return 1
    }

    [ $# -ge 1 ] || {
	echo "Usage: $0 line|gain|shift" [obsid1 obsid2 ...] 1>&2
	return 1
    }

    local type="$1"
    shift

    [[ $type =~ ^(line|gain|shift|contam)$ ]] || {
	echo "Usage: $0 line|gain|shift|contam" 1>&2
	return 1
    }

    [ $# -ge 1 ] && {
	obsids="$@"
    } || {
	obsids=$(obsids $DET)
    }

    pdffile="$datadir/fits/$CONTAMID/results/${type}fits_${DET}.pdf"
    for obsid in $obsids; do
	obsid=$(printf %05d $((10#$obsid)))

	echo "$datadir/fits/$CONTAMID/$obsid/${obsid}_${type}fit.ps"
	[ "$type" = shift ] && {
	    obsid_simul=$(\grep -h ",$obsid$" "$srcdir/../data/simul/$DET"  | perl -F= -anle 'print $F[0]')
	    [ -n "$obsid_simul" ] && echo "$datadir/fits/$CONTAMID/${obsid_simul}/${obsid_simul}_${type}fit.ps"
	} || :
    done | xargs cat | ps2pdf - "$pdffile"
}

psmerge_gain_corrections()
{
    [[ "$DET" =~ ^[is]3$ ]] || {
	echo "DET must be i3|s3" 1>&2
	return 1
    }

    [ -z "$CONTAMID" ] && {
	echo "CONTAMID must be set" 1>&2
	return 1
    }

    [ $# -ge 1 ] && {
	obsids="$@"
    } || {
	obsids=$(obsids $DET)
    }

    pdffile="$datadir/fits/$CONTAMID/results/gain_corrections_${DET}.pdf"
    for obsid in $obsids; do
	obsid=$(printf %05d $((10#$obsid)))
	echo "$datadir/fits/$CONTAMID/$obsid/${obsid}_gain_corrections.ps"
    done | xargs cat | ps2pdf - - | pdftk - cat 1-endwest output "$pdffile"
}

psmerge_gdl()
{
    [[ "$DET" =~ ^[is]3$ ]] || {
	echo "DET must be i3|s3" 1>&2
	return 1
    }

    [ -z "$CONTAMID" ] && {
	echo "CONTAMID must be set" 1>&2
	return 1
    }

    local type="$1"
    shift

    [[ $type =~ ^(spline_test|gain_corrections)$ ]] || {
	echo "Usage: $0 spline_test|gain_corrections" 1>&2
	return 1
    }

    [ $# -ge 1 ] && {
	obsids="$@"
    } || {
	obsids=$(obsids $DET)
    }

    pdffile="$datadir/fits/$CONTAMID/results/${type}_gdl_${DET}.pdf"
    for obsid in $obsids; do
	obsid=$(printf %05d $((10#$obsid)))
	echo "$datadir/fits/$CONTAMID/$obsid/${obsid}_${type}.ps"
    done | xargs cat | ps2pdf - - | pdftk - cat 1-endwest output "$pdffile"
}

# see /data/paul11/plucinsk/chandra/data/e0102/I3/99999/repro_ciao4.15.1_caldb4.10.4/combine_spectra.com
combine_spectra()
{
    [ $# -eq 0 ] && return
    [ $# -eq 1 ] || {
	echo "Usage: $0 combined_obsid=obsid1,obsid2,..." 1>&2
	return 1
    }

    local outobs inobs
    read outobs inobs <<<$(echo "$1" | perl -F= -anle 'print "$F[0] $F[1]"')
    inobs=${inobs/,/ }

    local outdir="$datadir/fits/$CONTAMID/$outobs"
    mkdir -p "$outdir"

    local outroot="$outdir/$outobs"
    local pi_stack=$(echo $inobs | perl -anle 'print join(",", map { "'"$datadir/fits/$CONTAMID/"'$_/${_}_energy_shift.pi" } @F)')
    local pi_bkg_stack=$(echo $inobs | perl -anle 'print join(",", map { "'"$datadir/fits/$CONTAMID/"'$_/${_}_bkg_energy_shift.pi" } @F)')

    punlearn combine_spectra
    "$ASCDS_INSTALL/bin/combine_spectra" \
	"$pi_stack" \
	"$outroot" \
	bkg_spectra="$pi_bkg_stack" \
	bscale_method=counts \
	cl+

    local srcpi="$outdir/${outobs}_energy_shift.pi"
    local bkgpi="$outdir/${outobs}_bkg_energy_shift.pi"
    local srcarf="$outdir/${outobs}.arf"
    local bkgarf="$outdir/${outobs}_bkg.arf"
    local srcrmf="$outdir/${outobs}.rmf"
    local bkgrmf="$outdir/${outobs}_bkg.rmf"

    mv "$outdir/${outobs}_src.pi" "$srcpi"
    mv "$outdir/${outobs}_bkg.pi" "$bkgpi"
    mv "$outdir/${outobs}_src.arf" "$srcarf"
    mv "$outdir/${outobs}_src.rmf" "$srcrmf"

    punlearn dmhedit
    dmhedit \
	infile="$srcpi" \
	filelist=none \
	operation=add \
	key=backfile \
	value="'$bkgpi'"

    punlearn dmhedit
    dmhedit \
	infile="$srcpi" \
	filelist=none \
	operation=add \
	key=ancrfile \
	value="'$srcarf'"

    punlearn dmhedit
    dmhedit \
	infile="$srcpi" \
	filelist=none \
	operation=add \
	key=respfile \
	value="'$srcrmf'"

    punlearn dmhedit
    dmhedit \
	infile="$bkgpi" \
	filelist=none \
	operation=add \
	key=ancrfile \
	value="'$bkgarf'"

    punlearn dmhedit
    dmhedit \
	infile="$bkgpi" \
	filelist=none \
	operation=add \
	key=respfile \
	value="'$bkgrmf'"

}
