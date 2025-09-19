;; adaptation of /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/data_shift.pro

; Apply gain correction to level=2 event file energies and update PI values.

args=command_line_args()

datadir='/data/legs/rpete/data/e0102'
fitdir=datadir+'/fits/'+getenv('CONTAMID')

;; read in obs info to get data mode
obsinfo=args[0]
readcol,obsinfo,obsids,date,chx,chy,node,exp,rdmode,datamode,comment='#',format='(A5,F7.2,F5.1,F5.1,I1,F8.2,A5,A6)'

get_lun, lun
openw,lun,fitdir+'/gain_correction_ratios_'+getenv('DET'+'.txt' ; output text file with ratios of best-fit energy/model energy
printf,lun,'# obsid  chx   chy  node  o7   o7lo   o7hi   o8     o8lo   o8hi   ne9    ne9lo  ne9hi  ne10   ne10lo ne10hi'

;; get best-fit energies:
fit_results=fitdir+'/linefits_'+getenv('DET')+'.txt'
readcol,fit_results,obs,cons,ne10,ne10err,ne9,ne9err,o8,o8err,o7,o7err,cstat,dof,redchi,chi,ne10_energy,ne10lo,ne10hi,ne9_energy,ne9lo,ne9hi,o8_energy,o8lo,o8hi,o7_energy,o7lo,o7hi,comment='#'

;; get gainfit slope and offset:
fit_results=fitdir+'/gainfits_'+getenv('DET')+'.txt'
readcol,fit_results,obs,cons,ne10,ne10err,ne9,ne9err,o8,o8err,o7,o7err,cstat,dof,redchi,chi,slope,slope_err,offset,off_err,comment='#'

;; set up things for plot
;peasecolr,white=white
;drakopy,'vinay'
!p.thick=5
!x.thick=5
!y.thick=5
!p.charsize=1.5
!x.charsize=1
!y.charsize=1
!p.charthick=5
set_plot,'ps'

for i=0,n_elements(obsids)-1 do begin

   obsid=obsids[i]
   infile=datadir+'/'+obsid+'/repro/acisf'+obsid+'_repro_evt2.fits'
   outfile=fitdir+'/'+obsid+'/'+obsid+'_evt2_energy_shift.fits'

   ;; un-shifted energies (eV)
   en=[0.573900,0.653600,0.922100,1.02170]*1000.  

   new=[o7_energy[i],o8_energy[i],ne9_energy[i],ne10_energy[i]] ; best-fit energies (params 119, 116, 65, 59)
   lo=[o7lo[i],o8lo[i],ne9lo[i],ne10lo[i]] 
   hi=[o7hi[i],o8hi[i],ne9hi[i],ne10hi[i]] 

   printf,lun,obsid,chx[i],chy[i],node[i],new[0]*1000./en[0],lo[0]*1000./en[0],hi[0]*1000./en[0],new[1]*1000./en[1],lo[1]*1000./en[1],hi[1]*1000./en[1],new[2]*1000./en[2],lo[2]*1000./en[2],hi[2]*1000./en[2],new[3]*1000./en[3],lo[3]*1000./en[3],hi[3]*1000./en[3],format='(A5,2X,F5.1,2X,F5.1,2X,I1,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3,2X,F5.3)'

    gf=(en/1000.)*slope[i] + offset[i] ; gain fit shifts
    
; plot the correction

    device,filename=fitdir+'/'+obsid+'/'+obsid+'_gain_corrections_cstat.ps',/landscape,/color
;    plot,en/1000.,gf-en/1000.,/xs,/ys,xr=[0.5,1.1],xtitle="Energy [keV]",ytitle="Delta Energy [Measured - Theoretical; keV]",title='Corrections for ObsID '+obsid+', contam '+contam,linestyle=0,col=0,psym=-6,yr=[-0.02,0.02],/nodata
;    plot,en/1000.,gf-en/1000.,/xs,/ys,xr=[0.5,1.1],xtitle="Energy [keV]",ytitle="Delta Energy [Measured - Theoretical; keV]",title='Corrections for ObsID '+obsid+' with test CALDB',linestyle=0,col=0,psym=-6,yr=[-0.02,0.02],/nodata
    plot,en/1000.,gf-en/1000.,/xs,/ys,xr=[0.5,1.1],xtitle="Energy [keV]",ytitle="Delta Energy [Measured - Theoretical; keV]",title='Cor. for ObsID '+obsid,linestyle=0,col=0,psym=-6,yr=[-0.04,0.04],/nodata
    oplot,en/1000.,gf-en/1000.,linestyle=2,col=1,psym=-2
    oplot,en/1000.,new-en/1000.,linestyle=0,col=2,psym=-2
    oplot,en/1000.,lo-en/1000.,linestyle=1,col=2
    oplot,en/1000.,hi-en/1000.,linestyle=1,col=2
    al_legend,['Linear corretion (gainfit)','Best-fit non-linear correction','1 sigma uncertainty'],linestyle=[2,0,1],col=[1,2,2],/bottom,/left,box=0
    device,/close

; the correction
   
    ; force it to be 0 at 0.001 keV and  1.1 and 1.5 keV 
    en=[0.001,0.573900,0.653600,0.922100,1.02170,1.1,1.5]*1000. 
    new=[0.001,o7_energy[i],o8_energy[i],ne9_energy[i],ne10_energy[i],1.1,1.5] ; best-fit energies (params 119, 116, 65, 59) 

    x=findgen(1500)
    shift=spline(new*1000.,en,x)

    device,filename=fitdir+'/'+obsid+'/'+obsid+'_spline_test.ps',/landscape,/color
    plot,x,shift,/xs,/ys,title=obsid
    device,/close


; read in default evt2 file
    evt2=mrdfits(infile,1,hevt)
    gti=mrdfits(infile,2,hgti)


; set up structure for output evt2 file               
    if datamode[i] eq "VFAINT" then evt_out={time:0.0D,ccd_id:0,node_id:0,expno:0L,chipx:0,chipy:0,tdetx:0,tdety:0,detx:0.0,dety:0.0,x:0.0,y:0.0,phas:intarr(5,5),pha:0L,pha_ro:0L,energy:0.0,pi:0L,fltgrade:0,grade:0,status:bytarr(4)}
    if datamode[i] eq "FAINT" then evt_out={time:0.0D,ccd_id:0,node_id:0,expno:0L,chipx:0,chipy:0,tdetx:0,tdety:0,detx:0.0,dety:0.0,x:0.0,y:0.0,phas:intarr(3,3),pha:0L,pha_ro:0L,energy:0.0,pi:0L,fltgrade:0,grade:0,status:bytarr(4)}
    bitcols=20
    
    evt_out=replicate(evt_out,n_elements(evt2.time))

; copy over values from input evt2 file
    evt_out.time=evt2.time
    evt_out.ccd_id=evt2.ccd_id
    evt_out.node_id=evt2.node_id
    evt_out.expno=evt2.expno
    evt_out.chipx=evt2.chipx
    evt_out.chipy=evt2.chipy
    evt_out.tdetx=evt2.tdetx
    evt_out.tdety=evt2.tdety
    evt_out.detx=evt2.detx
    evt_out.dety=evt2.dety
    evt_out.x=evt2.x
    evt_out.y=evt2.y
    evt_out.phas=evt2.phas
    evt_out.pha=evt2.pha
    evt_out.pha_ro=evt2.pha_ro
    evt_out.fltgrade=evt2.fltgrade
    evt_out.grade=evt2.grade
    evt_out.status=evt2.status
    
    for j=0L,n_elements(evt2.time)-1L do begin
        
                                ; modify energies between 0.2 - 1.1 keV
        if (evt2[j].energy ge 200 and evt2[j].energy le 1100) then evt_out[j].energy=interpol(shift,x,evt2[j].energy) else evt_out[j].energy = evt2[j].energy
        
                                ; update PI values:
        evt_out[j].pi=floor(evt_out[j].energy/14.6)+1
        
    endfor

; write out new evt2 file:
    mwrfits,evt_out,outfile,hevt,/create,nbit_cols=32,bit_cols=bitcols
    mwrfits,gti,outfile,hgti
    
endfor

close, lun
free_lun, lun

end
