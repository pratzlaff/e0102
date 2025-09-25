E0102-72.3 Fitting
========

When new E0102 observations become available, begin by adding them
to the list of all ObsIDs in `data/obsids/all.lst`, then download and reprocess
to current CalDB with
```
ciao
export CONTAMID=$(src/ciaostr)
export DET=all
src/download
src/repro
```
The destination is `$datadir` which is set in `src/functions.sh`.
Optionally, reorder the `all.lst` by OBS-DATE,
```
cp -a data/obsids/all.lst data/obsids/all/lst.bak
src/rewrite_obsid_lst $DET
```
and then re-create the observation info file.
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
Next, generation JPG images of the new observations with
```
src/images
```
which are written to `"$datadir"/images`.

Now for each of i3 and s3, generate the fits for current CalDB.
```
for det in i3 s3; do

  export DET=$det
  obsids=$(obsids $det)

  # generate a new observation info file

  src/obs_info | tee "$datadir/obs_info/$det.txt"

  # extract spectra for each ObsID, at this point an alternative contamination file
  # can used by assigning the CONTAMFILE environmental variable. For
  # such a case, it would be assumed that a different CONTAMID would be used,
  # other than the output of src/ciaostr, as the output will be
  # "$datadir/fits/CONTAMID/$obsid"

  src/specextract

  # perform the gain fits for each ObsID, compile the results, plot them all. Again,
  # output files will go to "$datadir/fits/CONTAMID/$obsid".
  #
  # This assumes `heainit` initializes HEASoft and both
  # data/NoLine_v1.3.1_coco.fits and
  # data/NoLine_v1.3.1_line.fits are placed in $HEADAS/../spectra/modelData

  src/gainfit
  gainfits_txt="$datadir/fits/$CONTAMID/gainfits_${DET}.txt"
  perl src/compile_gainfit_results.pl $obsids | tee "$gainfits_txt"
  src/plot_gainfits "$gainfits_txt"
  psmerge_xspec gain

    echo '.run shift_lines.pro'  | gdl -args $obsids

  src/linefit
  linefits_txt="$datadir/fits/$CONTAMID/linefits_${DET}.txt"
  perl src/compile_linefit_results.pl $obsids | tee "$linefits_txt"
  src/plot_linefits "$linefits_txt"
  psmerge_xspec line

  cd src
  echo '.run data_shift.pro'  | gdl -args "$datadir/obs_info/$DET.txt"
  psmerge_gain_corrections
  cd -

  src/shift_pi

  src/shiftfit
  shiftfits_txt="$datadir/fits/$CONTAMID/shiftfits_${DET}.txt"
  perl src/compile_shiftfit_results.pl $obsids | tee "$shiftfits_txt"
  src/plot_shiftfits "$shiftfits_txt"
  psmerge_xspec shift

  python3 \
    src/plot_fit_results.py \
    /data/legs/rpete/data/e0102/obs_info/$DET.txt \
    "$shiftfits_txt" \
    -p "$datadir/fits/$CONTAMID/params_${DET}.pdf"
done
```