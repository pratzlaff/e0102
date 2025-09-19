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
