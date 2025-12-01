;; adaptation of /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/shift_lines.pro

obsids=command_line_args(count=nargs)

; acting as a boolean, XSPEC line shift commands written to stdout if
; given ObsIDs on command line
stdout=nargs

spawn, './datadir', datadir
contamid=getenv('CONTAMID')
resdir=datadir+'/fits/'+contamid+'/results'

; get gainfit slope and offset
fit_results=resdir+'/gainfits_'+getenv('DET')+'.txt'
readcol,fit_results,obs,cons,mg11,mg11err,ne10,ne10err,ne9,ne9err,o8,o8err,o7,o7err,cstat,dof,redchi,chi,slope,slope_err,offset,off_err,comment='#'

if not nargs then obsids=obs

; line energies in IACHEC E0102 model
readcol,'../data/line_energies.txt',param,old

for k=0,n_elements(obsids)-1 do begin
   j = where(obs eq obsids[k])
   if (j eq -1) then begin
      printf, -2, 'Did not find ObsID '+obsids[k]+" in '"+fit_results+"'"
      exit, status=1
   endif else j=j[0]
   obsid = string(obs[j], format='%05d')

    fit_dir=datadir+'/fits/'+contamid+'/'+obsid

    new=old*slope[j]+offset[j]
    if stdout then begin
       lun = -1
    endif else begin
       get_lun, lun
       openw,lun,fit_dir+'/'+obsid+'_line_shifts.xcm'
    endelse

    for i=0,n_elements(param)-1 do begin
        printf,lun,'newpar '+string(param[i],format='(I3)')+' '+string(new[i],format='(F10.6)')+' 0.0001 '+string(new[i]-0.01,format='(F10.6)')+' '+string(new[i]-0.01,format='(F10.6)')+' '+string(new[i]+0.01,format='(F10.6)')+' '+string(new[i]+0.01,format='(F10.6)')
        printf,lun,'freeze '+string(param[i],format='(I3)')
    endfor

                                ; redo / update ties
    printf,lun,'newpar 68=65*'+strcompress(string(new[where(param eq 68)]/new[where(param eq 65)],format='(F10.6)'),/remove_all)
    printf,lun,'newpar 71=65*'+strcompress(string(new[where(param eq 71)]/new[where(param eq 65)],format='(F10.6)'),/remove_all)
    printf,lun,'newpar 74=65*'+strcompress(string(new[where(param eq 74)]/new[where(param eq 65)],format='(F10.6)'),/remove_all)
    
    printf,lun,'newpar 122=119*'+strcompress(string(new[where(param eq 122)]/new[where(param eq 119)],format='(F10.6)'),/remove_all)
    printf,lun,'newpar 125=119*'+strcompress(string(new[where(param eq 125)]/new[where(param eq 119)],format='(F10.6)'),/remove_all)
    ; Mg XI
    printf,lun,'newpar 32=29*'+strcompress(string(new[where(param eq 32)]/new[where(param eq 29)],format='(F10.6)'),/remove_all)
    printf,lun,'newpar 35=29*'+strcompress(string(new[where(param eq 35)]/new[where(param eq 29)],format='(F10.6)'),/remove_all)

    if not stdout then begin
       close, lun
       free_lun, lun
    endif

endfor

end
