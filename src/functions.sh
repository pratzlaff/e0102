srcdir=/data/legs/rpete/flight/e0102/src
datadir=/data/legs/rpete/data/e0102

[[ "$PATH" =~ ^/gs ]] || PATH=/gs/bin:"$PATH"

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
	\grep --no-filename ^$o "$datadir/obs_info/"[is]3.txt  | cut -f2
    done
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

    [[ $type =~ ^(line|gain|shift)$ ]] || {
	echo "Usage: $0 line|gain|shift" 1>&2
	return 1
    }

    [ $# -ge 1 ] && {
	obsids="$@"
    } || {
	obsids=$(obsids $DET)
    }

    [ "$type" = shift ] && {
	obsids+=" "$(perl -F= -anle 'print $F[0]' < "$srcdir/../data/simul/$DET")
    }
    psfiletmp="$datadir/fits/$CONTAMID/results/${type}fits_${DET}.ps.tmp"
    psfile="${psfiletmp%%.tmp}"
    for obsid in $obsids; do
	obsid=$(printf %05d $((10#$obsid)))
	echo "$datadir/fits/$CONTAMID/$obsid/${obsid}_${type}fit.ps"
    done | xargs psmerge -o "$psfiletmp"

    gs \
	-dBATCH \
	-dNOPAUSE \
	-sOutputFile="$psfile" \
	-sDEVICE=ps2write \
	-dAutoRotatePages=/None \
	-c "<< /Orientation 3 >> setpagedevice" 0 rotate 0 0 translate -f "$psfiletmp"
    rm -f "$psfiletmp"

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

    psfiletmp="$datadir/fits/$CONTAMID/results/gain_corrections_${DET}.ps.tmp"
    psfile="${psfiletmp%%.tmp}"
    for obsid in $obsids; do
	obsid=$(printf %05d $((10#$obsid)))
	echo "$datadir/fits/$CONTAMID/$obsid/${obsid}_gain_corrections.ps"
    done | xargs psmerge -o "$psfiletmp"

    gs \
	-dBATCH \
	-dNOPAUSE \
	-sOutputFile="$psfile" \
	-sDEVICE=ps2write \
	-dAutoRotatePages=/None \
	-c "<< /Orientation 1 >> setpagedevice" 0 rotate 0 0 translate -f "$psfiletmp"
    rm "$psfiletmp"
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
