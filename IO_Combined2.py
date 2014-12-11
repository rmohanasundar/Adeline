# -*- coding: utf-8 -*-
"""
Created on Tue Nov 04 15:17:52 2014

@author: goh1
"""
import glob, os             #to remove all the temp files
import csv                  #import lu_parameters.csv file

#define a function to find the runoff coeff under different rainfall duration
def runoff_coeff(slp, ip, ni, np, si, sp, sperc, cn, cont):     
     timeseries = ["5min", "10min", "20min", "30min", "60min", "90min", "120min", "150min", "180min", "210min", "240min"]
     runoff_coeff_series=[]                                 
     duration_series=[]
     
     # Inputing timeseries and catchment properties from inp file, 
     for i, duration in enumerate (timeseries):                  
     #The following set of calculations needs to be completed in the same loop.
          fo=open("singlecell_2v.inp","w")
          ncont=cont%{"timeseries":duration,"pcnt_sl": slp,"pcnt_imp":ip, "n_imp": ni, "n_per":np, "s_imp":si, "s_per":sp,"pcnt_zero": sperc, "curve_number":cn}              #note: prog is only able to replace things one time, therefore need to lump them tgt
          fo.write(ncont)
          fo.close()
          #print ("For %s rainfall duration," %duration) 
          
          #To compute the total runoff at outfall,
          from swmm5.swmm5tools import SWMM5Simulation           #Assela's lib     
          st=SWMM5Simulation("singlecell_2v.inp")                 #Assela's lib   
          r1=list(st.Results('SUBCATCH','S1', 3))
          runoff_vol=sum(r1)*st.SWMM_ReportStep                  #units is m3/s*s=m
          #print ("Total runoff volume is %.2f m3." %runoff_vol)
          
          #To compute runoff depth,
          area=8100                                              #units is m2
          runoff_depth=(runoff_vol/area)*1000                    #units is mm
          #print("Runoff depth is %.2f mm." %runoff_depth)
          
          #To identify the rainfall intensity of specified rainfall duration,
          r2=list(st.Results('SUBCATCH','S1', 0))                #Assela's lib
          I=max(r2)                                              #units is mm/hr
          #print ("Rainfall intensity is %.1f mm/hr." %I)
          
          #To compute total rainfall depth,
          time_float=float(duration[:-3])
          rainfall_depth=I*(time_float/60.)                                   #units is mm
          #print ("Total rainfall depth is %.2f mm." %P)
          
          #To compute runoff coefficient,
          runoff_coeff=runoff_depth/rainfall_depth                            #dimensionless
          #print ("Runoff coefficient is %.2f." %runoff_coeff)
          
          #To consolidate all the runoff coeff and diff durations into 2 lists,
          runoff_coeff_series.append(runoff_coeff)
          duration_series.append(time_float)
          
          #To choose the maximum runoff coefficient and its corresponding rainfall duration
          max_runoff_coeff=max(runoff_coeff_series)                  #max runoff coeff value
          d=runoff_coeff_series.index(max_runoff_coeff)              #index at where max runoff coeff occurs
     return max_runoff_coeff, duration_series[d]

#define a funtion that reads the percent slope raster
def Slope_reader(slopefile):
     f=open(slopefile,"r")
     slp_series=[]                                  
     
     header1 = f.readline()
     header2 = f.readline()
     header3 = f.readline()
     header4 = f.readline()
     header5 = f.readline()
     header6 = f.readline()
     
     ncols=int(header1[-5:-1])
     
     for line in f:
          line = line.strip()
          columns = line.split()
          slp = columns[:ncols+1]                    #to read the number of columns from the header of the txt file
          """changing -9999 to zero"""          
          slp_float=[float(0) if i == '-9999' else float(i) for i in slp] 
          # slp_series.extend(slp_float) 
          slp_series.extend(slp_float)
     f.close()
     print slp_series[:1]
     print "length of slope cells", len(slp_series)              
     return slp_series

#define a function called lu_read which is used to read all the lu param in the csv file (Ip, Ni, Np, Si, Sp and Sperc) for each class
def lu_read(fn):
    lup=[]
    with open(fn, 'rU') as f:
        reader = csv.reader(f)
        for row in reader:
            lup.append(row)
    if (lup[0][0]!="ID" and lup[0][1]!="Ip"):           # to check if the right file has been opened
        print "I have a problem!"
    
    lup.pop(0)            #remove the first row of the lu_parameters.csv file (i.e header of csv table)
    nlup=[]
    for item in lup:
        nlup.append([])
        for col in item:
            nlup[-1].append(float(col))
            
    # for fast access let's create a different array. 
    # use max lu id to define the length of this array
    maxid=max([x[0] for x in nlup])             # for the variables in nlup, call them x. for each x, refer to the 0th col and find the max value
    nnlup=[None for x in range(int(maxid)+1)]   # new array is called nnlup
    for item in nlup:                           # purpose is to rearrange the landuse id into numerical order and store inside nnlup
        nnlup[int(item[0])]=item
    return nnlup                                # means return nnlup to lu_read

def LandusetoSubcatch(Landuseid_subcatchments):
     f1=open(Landuseid_subcatchments,"r")
     lu_id_series=[]
     #call the function to read land use parameter
     lu_param=lu_read("mp14_legend.csv")        #read LU parameters 
     #print lu_param                              
     
     sub_catch_prop_series = []
     
     header1 = f1.readline()
     header2 = f1.readline()
     header3 = f1.readline()
     header4 = f1.readline()
     header5 = f1.readline()
     header6 = f1.readline()
     
     ncols=int(header1[-5:-1])
     #ctr=0     
     for line in f1:
          #print ctr          
          #ctr=ctr+1         
          line = line.strip()
          columns = line.split()
          lu_id = columns[:ncols+1]
          """changing -9999 to zero"""          
          lu_id_int=[0 if int (i) == -9999 else int(i) for i in lu_id]
          #lu_id_int=[int(i) for i in lu_id]
          sub_catch_prop=[lu_param[0 if int (i) == -9999 else int(i)][1:] for i in lu_id]
          #sub_catch_prop=[lu_param[int(i)][1:] for i in lu_id]        #combining lu id with sub catchment properties
          #print sub_catch_prop
          lu_id_series.append(lu_id_int)
          sub_catch_prop_series.extend(sub_catch_prop)
     f1.close()
     print sub_catch_prop_series [:1]
     print "length of land use cells", len(sub_catch_prop_series)
     return sub_catch_prop_series
       
if __name__ == "__main__":
     results_runoff=[] 
     results_time=[]
     Subcatchslope=Slope_reader("slp_p.txt") 
     #print Subcatchslope
     Subcatchproperties= LandusetoSubcatch("lu_pc.txt")     
     #print Subcatchproperties
        
     for i in range(0,len(Subcatchslope)):
          Subcatchchar=[Subcatchslope[i]]
          Subcatchchar.extend(Subcatchproperties[i])
          #print Subcatchchar
          
          fi=open("singlecell_2.inp_","r")
          s=fi.read()                                                      #return template
          fi.close()
          """ Here an if - else conditional statement is being used to avoid the swmm analaysis of catchments with value -9999.
          The logic used is that ifsum of catchment parameter and slope is zero then runoff parameter is -9999 
          else it runs the swmm analysis and gets the runoff coefficient """          
          results_runoff.append(-9999)          
          if sum(Subcatchchar)==0: 
               results_runoff.append(-9999)         
          else:
               rc=runoff_coeff(Subcatchchar[0], Subcatchchar[1], Subcatchchar[2], Subcatchchar[3], Subcatchchar[4], Subcatchchar[5], Subcatchchar[6], Subcatchchar[7], s)              #These values are to be extracted from the raster data for each cell. s= template
               results_runoff.append(rc[0])
               #results_time.append(rc[1])
               #print ("Maximum runoff coefficient for this cell is %.2f for the %dmin rainfall." %rc)        
               #print results_runoff
               #print results_time
               
               #to remove all the temp files in the C directory     
               path="..//"
               retval = os.getcwd()
               os.chdir(path)
               filelist = glob.glob("*.dat")
               for f in filelist:
                    os.remove(f)
               filelist1 = glob.glob("*.rpt")
               for j in filelist1:
                    os.remove(j) 
               os.chdir(retval)                
          
               
     # to write output into txt file
     fo = open('mrc_out.txt', 'w')
     ncols = 1941
     nrows = 1141
     xllcorner = 2668.7346550003
     yllcorner = 21726.537653728
     cellsize  = 25
     NODATA_value = -9999
     """ Adeline, what you have done above is hardcoding. You already have this info in your other input files.
     Try to get them from those files and write it here""" 
          
     fo.write('ncols\t\t%d\n' %ncols)
     fo.write('nrows\t\t%d\n' %nrows)
     fo.write('xllcorner\t%f\n' %xllcorner)
     fo.write('yllcorner\t%f\n' %yllcorner)
     fo.write('cellsize\t%d\n' %cellsize)
     fo.write('NODATA_value\t%d\n' %NODATA_value)
     for i in range(0,nrows):
          for j in range(0,ncols):
               index = j+(i-1)*nrows
               fo.write('%f ' %results_runoff[index])
          fo.write('\n')
     fo.close()
     """ Hi Adeline the code is working but there seems to a problem in the way the output file is being written.
     I ran this with a 2X2 cell. the first row has values -9999, -9999 and the second row has values 01 and 02 for land use
     similary the slope input has -9999, -9999 in first row and 01, 02.345 in second row. the code skips the first row 
     and compute the results for second row but while printing the results the second row is printed first and the then the first row
     I am attching the modified code and the input files. run it and check them and fix it and let me know""" 
