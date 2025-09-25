E0102-72.3 Fitting
========

When new E0102 observations become available, begin by adding them
list of all obsids in `data/obsids/all.lst`, the download and reprocess
to current CalDB with
```
ciao
export CONTAMID=$(src/ciaostr)
export DET=all
src/download
src/repro
```
This downloads and to `$datadir`, which is set in `src/functions.sh`.