E0102-72.3 Fitting
========

When new E0102 observations become available, begin by adding them
to the list of all ObsIDs in `data/obsids/{i3,s3,all}.lst`, then download and reprocess
using current CalDB with
```
ciao
export CONTAMID=$(src/ciaostr)

new_obsids='31375 31374'

src/download $new_obsids

src/repro $new_obsids

# create -120C evt2 files
src/evt2-120C $new_obsids
```
The destination is `$datadir` which is set in `src/functions.sh`.
Optionally, reorder the `{i3,s3,all}.lst` by OBS-DATE,
```
for det in i3 s3 all; do
    cp -a data/obsids/det.lst data/obsids/$det.lst.bak
    src/rewrite_obsid_lst $det
done
```
and then re-create the observation info files.
```
datadir=$(./src/datadir)
. src/functions.sh
mkdir -p "$datadir/obs_info"
for det in i3 s3 all; do
    src/obs_info $(obsids $det) | tee "$datadir/obs_info/$det.txt"
done
```

If any combination of ObsIDs constitue a split observation,
add them to `data/simul/[is]3`.

For each new ObsID, create a background region file in `data/reg/bkg`.
This is easiest done by copying an existing region file from a similar
detector position, then find the appropriate evt2 file, and finally,
edit the region file while continually re-running ds9:
```
obsid=31374
evt2=$(\ls $datadir/$obsid/repro/acisf${obsid}_repro_evt2.fits)
bkgreg=data/reg/bkg/${obsid}_bkg.reg
srcreg=data/reg/src.reg
while [ true ]; do
  ds9 \
    "$evt2" \
    -regions "$bkgreg" \
    -regions "$srcreg" \
    -scale mode 99.5 \
    -pan to 01:04:01.996 -72:01:53.44 wcs \
    -bin factor 2 \
    -cmap heat
done
```
Generate JPG images of source and background regions with
```
src/images $new_obsids
```
which are written to `"$datadir"/images`.

For I3 and S3, perform the fits, parallelized where possible.
```
nproc=$(nproc)

# create a location for fit results
resdir="$datadir/fits/$CONTAMID/results"
mkdir -p "$resdir"

for det in i3 s3; do
  obsids=$(obsids $det)

  # extract spectra for each ObsID, output files will be placed in
  # "$datadir/fits/$CONTAMID/$obsid"
  parallel -j $nproc src/specextract ::: $obsids

  # perform the gain fits for each ObsID, compile the results, plot them all. Again,
  # output files will go to "$datadir/fits/CONTAMID/$obsid".
  #
  # This assumes `heainit` initializes HEASoft and both
  # data/NoLine_v1.3.1_coco.fits and
  # data/NoLine_v1.3.1_line.fits are placed in $HEADAS/../spectra/modelData

  # fit gain
  parallel -j $nproc src/gainfit ::: $obsids
  gainfits_txt="$resdir/gainfits_${det}.txt"
  perl src/compile_fit_results.pl gain $obsids | tee "$gainfits_txt"
  src/plot_gainfits "$gainfits_txt"
  psmerge_xspec gain $det

  # shift model line energies
  cd src
  echo '.run shift_lines.pro' | env DET=$det gdl
  cd -

  # fit line energies
  parallel -j $nproc src/linefit ::: $obsids
  linefits_txt="$resdir/linefits_${det}.txt"
  perl src/compile_fit_results.pl line $obsids | tee "$linefits_txt"
  src/plot_linefits "$linefits_txt"
  psmerge_xspec line

  # create plots of gain corrections, splines, fp_temp
  python3 ./plot_various.py $det

  # shift evt2 energies
  cd src
  echo '.run data_shift.pro' | env DET=$det gdl
  cd -

  # merge individual spline_test, gain_corrections plots into "$resdir/spline_test_${DET}.pdf"
  psmerge_gdl spline_test $det
  psmerge_gdl gain_corrections $det

  # create spectra with shifted energies
  parallel -j $nproc src/shift_pi ::: $obsids

  # fit shifted line normalizations
  parallel -j $nproc src/shiftfit ::: $obsids
  shiftfits_txt="$resdir/shiftfits_${det}.txt"
  perl src/compile_fit_results.pl shift $obsids | tee "$shiftfits_txt"
  src/plot_shiftfits "$shiftfits_txt"
  psmerge_xspec shift

  # plot fitted parameters vs time, locates obsinfo and shiftfits
  # results files based on $CONTAMID and $DET
  python3 \
    src/plot_fit_results.py \
    -p "$resdir/params_${DET}.pdf"
done
```

To test a new contamination file in `specextract`, set environment
variable `CONTAMFILE`. Generally this will be used in conjunction
with a correspondingly descriptive `CONTAMID` environment variable.

To use only -120C `p2_resp` files, pass command-line argument `--120C`
to `specextract`. This requires that `src/evt2-120C` has been
run for each ObsID.

To tie the Ne9 normalization to Ne10 in `gainfit`, `linefit` and
`shiftfit`, pass command-line argument `--tieNe9`.

