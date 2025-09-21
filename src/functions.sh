srcdir=/data/legs/rpete/flight/e0102
datadir=/data/legs/rpete/data/e0102

obsids()
{
    [ $# -eq 1 ] || {
	echo "Usage: $0 det" 1>&2
	return 1
    }
    local det=${1,,}
    \grep '^[0-9]' "${srcdir}/data/obsids/$det.lst" | cut -f 1 #| tail -1
}

psmerge_xspec()
{
    [[ "$DET" =~ ^[is]3$ ]] || {
	echo "DET must be i3|s3" 2>&1
	return 1
    }

    [ -z "$CONTAMID" ] && {
	echo "CONTAMID must be set" 2>&1
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

    psfiletmp="$datadir/fits/$CONTAMID/${type}fits_${DET}.ps.tmp"
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
    rm "$psfiletmp"

}

