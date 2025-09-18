srcdir=/data/legs/rpete/flight/e0102
datadir=/data/legs/rpete/data/e0102

obsids()
{
    \grep '^[0-9]' "${srcdir}/data/obsids" | cut -f 1 #| tail -1
}
