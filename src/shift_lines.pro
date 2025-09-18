;; adaptation of /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/shift_lines.pro

obsids=command_line_args()
for i=0,n_elements(obsids)-1 do begin
   obsids[i] = string(obsids[i], format='%05d')
endfor

; get gainfit slope and offset
fit_results='/data/legs/rpete/data/e0102/fits/'+getenv('CONTAMID')+'/gainfits.txt'
print,fit_results
readcol,fit_results,obs,cons,ne10,ne10err,ne9,ne9err,o8,o8err,o7,o7err,cstat,dof,redchi,chi,slope,slope_err,offset,off_err,comment='#'

; line energies in IACHEC E0102 model
readcol,'/data/legs/rpete/flight/e0102/data/line_energies.txt',param,old

; printf to stdout

for j=0,n_elements(obsids)-1 do begin

    fit_dir='/data/legs/rpete/data/e0102/fits/CALDB/'+obsids[j]

    new=old*slope[j]+offset[j] 
    get_lun, lun
    openw,lun,fit_dir+'/line_shifts_contam.xcm'

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
    close, lun
    free_lun, lun

endfor

end
