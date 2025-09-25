E0102-72.3 Fitting
========

When new E0102 observations become available, begin by adding them
list of all ObsIDs in `data/obsids/all.lst`, the download and reprocess
to current CalDB with
```
ciao
export CONTAMID=$(src/ciaostr)
export DET=all
src/download
src/repro
```
This downloads and to `$datadir`, which is set in `src/functions.sh`.
Optionally, reorder the `all.lst` by OBS-DATE,
```
cp -a data/obsids/all.lst data/obsids/all/lst.bak
src/rewrite_obsid_lst $DET
```
and then create the `obs_info` file.
```
. src/functions.sh
mkdir -p "$datadir/obs_info"
src/obs_info | tee "$datadir/obs_info/$DET.txt"
```

Note which detectors are used for each ObsID, and add them to
`data/obsids/[is].lst`, as appropriate. If any are split,
define a new combination in `data/combine/[is]3`.

Create new background region files for each new ObsID in `data/reg/bkg`.
This is easiest done by copying an existing region file from a similar
detector position, find the appropriate evt2 file,
```
obsid=12345
evt2=$(\ls $datadir/$obsid/repro/acisf${obsid}_repro_evt2.fits)
bkgreg=data/reg/bkg/${obsid}_bkg.reg
srcreg=data/reg/src.reg
```
then edit the region file while continually re-running
```
ds9 \
  "$evt2" \
  -regions "$bkgreg" \
  -regions "$srcreg" \
  -scale mode 99.5 \
  -pan to 01:04:01.996 -72:01:53.44 wcs \
  -bin factor 2 \
  -cmap heat
```
