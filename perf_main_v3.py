#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 16:48:00 2019

@author: burak
"""
import numpy as np
import threading as th
from osgeo import gdal
import time
import matplotlib.pyplot as plt
import sys, getopt
"""
# Default params
path_im_ms = './data/spot6/GEBZE/S6_GEBZE_MS.tiff'
path_im_pan = './data/spot6/GEBZE/S6_GEBZE_PAN.tiff'
path_xml = './data/spot6/GEBZE/S6_GEBZE_MS.XML'
filter_name = 'ideal_lpf'
path_im_ps = './data/spot6/GEBZE/OUT.tiff'
# hist_m = True
cutoff_freq=.125
ps_method = 'ihs_fft'
is_multi_thread = True
run_times = 10
"""
path_im_ms = ''
path_im_pan = ''
path_xml = ''
filter_name = ''
path_im_ps = ''
# hist_m = True
cutoff_freq=''
ps_method = ''
is_multi_thread = False
run_times = ''

def load_params(argv):
    global path_im_ms
    global path_im_pan
    global path_xml
    global filter_name
    global cutoff_freq
    global ps_method
    global path_im_ps
    global is_multi_thread
    global run_times
    def usage():
        msg = """test.py     --ms-file= <MS File Path> 
                    --pan-file= <PAN File Path> 
                    --xml-file= <XML File Path> 
                    --cutoff-freq= <Cutoff Frequency> 
                    --ps-method= <fft, ihs, ihs_fft, lab, lab-fft, brovey, hfm> 
                    --histogram-match 
                    --out-file= <PS File Path> 
                    --multi-thread"""
        print msg
    try:
        opts, args = getopt.getopt(argv,"m:p:x:f:c:t:o:a:r:",
        ["ms-file=","pan-file=","xml-file=","filter=",
        "cutoff-freq=","ps-method=","out-file=","multi-thread",
        "run-times="])
    except Exception as e:
        usage()
        print(str(e))
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-m", "--ms-file"):
            path_im_ms = arg
            print "path ms: ", arg
        elif opt in ("-p", "--pan-file"):
            path_im_pan = arg
        elif opt in ("-x","--xml-file"):
            path_xml = arg
        elif opt in ("-f","--filter"):
            filter_name = arg
        elif opt in ("-c","--cutoff-freq"):
            cutoff_freq = float(arg)
        elif opt in ("-t","--ps-method"):
            ps_method = arg
        elif opt in ("-o","--out-file"):
            path_im_ps = arg
        elif opt in ("-a","--multi-thread"):
            is_multi_thread = True
        elif opt in ("-r","--run-times"):
            run_times = int(arg)
    try:
        path_im_ms
        path_im_pan
        path_xml
        filter_name
        cutoff_freq
        ps_method
        path_im_ps
        is_multi_thread
        run_times
    except Exception as e:
        usage()
        print(str(e))
        exit()
        
def print_params():
    global path_im_ms
    global path_im_pan
    global path_xml
    global filter_name
    global cutoff_freq
    global ps_method
    global path_im_ps
    global is_multi_thread
    global run_times
    print '#'*50
    print ("%-20s : %s") % ("MS File Path", path_im_ms)
    print ("%-20s : %s") % ("PAN File Path", path_im_ms)
    print ("%-20s : %s") % ("XML File Path", path_xml)
    print ("%-20s : %s") % ("Filter Name", filter_name)
    print ("%-20s : %s") % ("Cutoff Freq", cutoff_freq)
    print ("%-20s : %s") % ("PS Methhod", ps_method)
    print ("%-20s : %s") % ("PS File Path", path_im_ps)
    print ("%-20s : %s") % ("Multi Thread", is_multi_thread)
    print ("%-20s : %s") % ("Run Times", run_times)

def load_datas_for_pansharpenning(pan_path, ms_path):
    from osgeo import gdal
    import cv2
    INTERPOLATION = cv2.INTER_LINEAR
    SCALE = 4
    gdal.UseExceptions()
    try:
        ds_pan = gdal.Open(pan_path, gdal.GA_ReadOnly)
        ds_ms = gdal.Open(ms_path, gdal.GA_ReadOnly)        
        pan = ds_pan.GetRasterBand(1).ReadAsArray()
        ms1 = ds_ms.GetRasterBand(1).ReadAsArray().astype('float64')
        ms2 = ds_ms.GetRasterBand(2).ReadAsArray().astype('float64')
        ms3 = ds_ms.GetRasterBand(3).ReadAsArray().astype('float64')
        pan = pan[0:-1:SCALE, 0:-1:SCALE]
        ms1 = ms1[0:-1:SCALE, 0:-1:SCALE]
        ms2 = ms2[0:-1:SCALE, 0:-1:SCALE]
        ms3 = ms3[0:-1:SCALE, 0:-1:SCALE]
        ms1 = cv2.resize(ms1, (0,0), fx=SCALE, fy=SCALE, interpolation=INTERPOLATION)
        ms2 = cv2.resize(ms2, (0,0), fx=SCALE, fy=SCALE, interpolation=INTERPOLATION)
        ms3 = cv2.resize(ms3, (0,0), fx=SCALE, fy=SCALE, interpolation=INTERPOLATION)
        return pan, ms1, ms2, ms3
    except Exception as e:
        print e.message, e.args

def write_ps_to_disk(path_im_ps, ps1, ps2, ps3):
    # write to file
    import numpy as np
    m, n = np.shape(ps1)
    driver = gdal.GetDriverByName('Gtiff')
    dataset = driver.Create(path_im_ps, m, n, 3, gdal.GDT_Float32)
    dataset.GetRasterBand(1).WriteArray(ps1)
    dataset.GetRasterBand(2).WriteArray(ps2)
    dataset.GetRasterBand(3).WriteArray(ps3)
    dataset.FlushCache()
    # read it
"""
    ds = gdal.Open('out.tiff', gdal.GA_ReadOnly)
    a1 = ds.GetRasterBand(1).ReadAsArray()
    a2 = ds.GetRasterBand(2).ReadAsArray()
    a3 = ds.GetRasterBand(3).ReadAsArray() 
"""

def dftuv(m, n):
    import numpy as np
    u = np.arange(m)
    v = np.arange(n)
    np.putmask(u, u > (m/2 -1 ), u - m +1)
    np.putmask(v, v > (n/2 -1 ), v - n +1)
    uu, vv = np.meshgrid(u, v, sparse=False)
    return uu, vv

def ffilters(filter_name, m, n, d0=.125, k=1):
    import numpy as np
    h = np.empty((m,n))
    u, v = dftuv(m, n)
    d0 = d0 * (max(m,n)/2)
    d = np.sqrt(u**2 + v**2)
    if filter_name == 'ideal_lpf':
        h = (d <= d0).astype('float64')
    elif filter_name == 'ideal_hpf':
        h = (d >= d0).astype('float64')
    elif filter_name == 'hamming':
        h = (.54 + .46 * np.cos(np.pi * (d/d0) )) * (d <= d0)
    elif filter_name == 'hanning':
        h = .5 * (1 + np.cos(np.pi * d/d0) ) * (d <= d0)
    elif filter_name == 'lbtw':
        h = 1 / (1 + (d / d0) ** (2 * k))
    elif filter_name == 'gauss_low':
        h = np.exp(-(d**2) / (2*(d0**2)))
    else:
        print "Unknown filter name."
        exit(1)
    return h

def hist_match(im, im_ref):
    import numpy as np
    m, n = np.shape(im)
    m_ref, n_ref = np.shape(im_ref)
    im_mean = np.mean(im)
    im_ref_mean = np.mean(im_ref)
    im_std = np.std(im)
    im_ref_std = np.std(im_ref)
    im = (im - im_mean) * (im_ref_std / im_std) + im_ref_mean;
    return im

def mean_rad(xml_file):
    import xml.etree.ElementTree as et
    root = et.parse(xml_file).getroot()
    g1 = float(root[8][4][0][0][4][5].text)
    g2 = float(root[8][4][0][0][5][5].text)
    g3 = float(root[8][4][0][0][6][5].text)
    return g1, g2, g3

def ps_quality_score(p_method, im_ps, im_ref, xml_file='none', ms_pan_ratio=0.25):
    import numpy as np
    m, n, k = np.shape(im_ps)
    if p_method == 'SAM':
        p1 = np.empty((k), dtype='float64')
        p2 = np.empty((k), dtype='float64')
        for i in range(k):
            p1[i] = np.dot(np.reshape(im_ps[:,:,i], (m*n)), np.reshape(im_ref[:,:,i], (m*n)))
            p2[i] = np.sqrt(np.sum(im_ps[:,:,i] ** 2.0)) * np.sqrt(np.sum(im_ref[:,:,i] ** 2.0))
        result = (np.arccos(p1 / p2) * (180.0 / np.pi))
    elif p_method == 'RMSE':
        p1 = np.empty((k), dtype='float64')
        p2 = np.empty((k), dtype='float64')
        for i in range(k):
            p1[i] = np.sum((im_ref[:,:,i] - im_ps[:,:,i]) ** 2.0)
        result = ((1.0 / (m*n)) * (np.sqrt(p1)))
    elif p_method == 'RASE':
        p1 = np.empty((k), dtype='float64')
        p2 = np.empty((k), dtype='float64')
        rmse = np.empty((k), dtype='float64')
        for i in range(k):
            p1[i] = np.sum((im_ref[:,:,i] - im_ps[:,:,i]) ** 2.0)
            rmse[i] = (1.0 / (m*n)) * (np.sqrt(p1[i]))
        gain = np.array(mean_rad(xml_file))
        p2 = np.sum((rmse ** 2.0) / gain)
        result = (100.0 * np.sqrt((1.0 / k) * p2))
    elif p_method == 'ERGAS':
        p1 = np.empty((k), dtype='float64')
        p2 = np.empty((k), dtype='float64')
        rmse = np.empty((k), dtype='float64')
        for i in range(k):
            p1[i] = np.sum((im_ref[:,:,i] - im_ps[:,:,i]) ** 2.0)
            rmse[i] = (1.0 / (m*n)) * (np.sqrt(p1[i]))
        gain = np.array(mean_rad(xml_file))
        p2 = np.sum((rmse ** 2.0) / gain)
        result = (100.0 * ms_pan_ratio * np.sqrt((1.0 / k) * p2))
    return result

def rgb_to_lab(ms1, ms2, ms3):
    import numpy as np
    global f_ms1
    global f_ms2
    global f_ms3
    f_ms1 = ms1 / float(2**12 - 1)
    f_ms2 = ms2 / float(2**12 - 1)
    f_ms3 = ms3 / float(2**12 - 1)
    threshold = 0.008856;
    m, n = np.shape(ms1)
    s = m*n
    f_ms1 = f_ms1.reshape((1,s))
    f_ms2 = f_ms2.reshape((1,s))
    f_ms3 = f_ms3.reshape((1,s))
    # RGB to XYZ
    cm = np.array([[0.412453, 0.357580, 0.180423],
                   [0.412453, 0.357580, 0.180423],
                   [0.019334, 0.119193, 0.950227]])
    xyz = np.matmul(cm, np.concatenate((f_ms1, f_ms2, f_ms3), axis=0))
    # Normalize for D65 white points
    x = xyz[0,:] / 0.950456
    y = xyz[1,:]
    z = xyz[2,:] / 1.088754
    
    xt = x > threshold
    yt = y > threshold
    zt = z > threshold
    
    y3 = y**(1.0/3.0); 
    
    fx = x[xt]**(1.0/3.0) + ()

def pansharpenning(ps_method, pan, ms1, ms2, ms3, filter_name, cutoff_freq=.125):
    import numpy as np
    
    m, n = np.shape(pan)
    h_low = ffilters(filter_name, m, n, cutoff_freq, 1)
    h_high = np.ones((m,n)) - h_low
    if ps_method == 'fft':
        f_pan1 = np.fft.fft2(hist_match(pan, ms1))
        f_pan2 = np.fft.fft2(hist_match(pan, ms2))
        f_pan3 = np.fft.fft2(hist_match(pan, ms3))
        g_pan1 = f_pan1 * h_high
        g_pan2 = f_pan2 * h_high
        g_pan3 = f_pan3 * h_high
        f_ms1 = np.fft.fft2(ms1)
        f_ms2 = np.fft.fft2(ms2)
        f_ms3 = np.fft.fft2(ms3)
        g_ms1 = f_ms1 * h_low
        g_ms2 = f_ms2 * h_low
        g_ms3 = f_ms3 * h_low
        f_ps1 = g_pan1 + g_ms1
        f_ps2 = g_pan2 + g_ms2
        f_ps3 = g_pan3 + g_ms3
        ps1 = np.fft.ifft2(f_ps1)
        ps2 = np.fft.ifft2(f_ps2)
        ps3 = np.fft.ifft2(f_ps3)
        return ps1, ps2, ps3
    elif ps_method == 'ihs':
        # IHS Transform
        ihs = np.multiply((1.0/3.0), (ms1 + ms2 + ms3))
        # Histogram matching
        f_pan = hist_match(pan, ihs)
        ps1 = (f_pan + ms1 - ihs)
        ps2 = (f_pan + ms2 - ihs)
        ps3 = (f_pan + ms3 - ihs)
        return ps1, ps2, ps3
    elif ps_method == 'ihs_fft':
        ihs = np.multiply((1.0/3.0), (ms1 + ms2 + ms3))
        f_pan = np.fft.fft2(hist_match(pan, ihs))
        g_pan = f_pan * h_high
        f_ms1 = np.fft.fft2(ms1)
        f_ms2 = np.fft.fft2(ms2)
        f_ms3 = np.fft.fft2(ms3)
        g_ms1 = f_ms1 * h_low
        g_ms2 = f_ms2 * h_low
        g_ms3 = f_ms3 * h_low
        f_ps1 = g_pan + g_ms1
        f_ps2 = g_pan + g_ms2
        f_ps3 = g_pan + g_ms3
        ps1 = np.fft.ifft2(f_ps1)
        ps2 = np.fft.ifft2(f_ps2)
        ps3 = np.fft.ifft2(f_ps3)
        return ps1, ps2, ps3
    elif ps_method == 'lab':
        
    elif ps_method == 'lab_fft':
        pass
    elif ps_method == 'brovey':
        pass
    elif ps_method == 'hfm':
        pass

############################################################################### 
# Multi-theaded functions
###############################################################################
    
def hist_match_mt(band):
    import numpy as np
    global pan
    global ms1
    global ms2
    global ms3
    global f_pan1
    global f_pan2
    global f_pan3
    m, n = np.shape(pan)
    im_mean = np.mean(pan)
    im_std = np.std(pan)
    if band == 1:
        im_ref_mean = np.mean(ms1)
        im_ref_std = np.std(ms1)
        f_pan1 = (pan - im_mean) * (im_ref_std / im_std) + im_ref_mean;
    elif band == 2:
        im_ref_mean = np.mean(ms2)
        im_ref_std = np.std(ms2)
        f_pan2 = (pan - im_mean) * (im_ref_std / im_std) + im_ref_mean;
    elif band == 3:
        im_ref_mean = np.mean(ms3)
        im_ref_std = np.std(ms3)
        f_pan3 = (pan - im_mean) * (im_ref_std / im_std) + im_ref_mean;

def fft2_pan_mt(band):
    import numpy as np
    global f_pan1
    global f_pan2
    global f_pan3
    if band == 1:
        f_pan1 = np.fft.fft2(f_pan1)
    elif band == 2:
        f_pan2 = np.fft.fft2(f_pan2)
    elif band == 3:
        f_pan3 = np.fft.fft2(f_pan3)

def fft2_ms_mt(band):
    import numpy as np
    global ms1
    global ms2
    global ms3
    global f_ms1
    global f_ms2
    global f_ms3
    if band == 1:
        f_ms1 = np.fft.fft2(ms1)
    elif band == 2:
        f_ms2 = np.fft.fft2(ms2)
    elif band == 3:
        f_ms3 = np.fft.fft2(ms3)


def filter_pan_mt(band, h_high):
    import numpy as np
    global f_pan1
    global f_pan2
    global f_pan3
    if band == 1:
        f_pan1 = np.multiply(f_pan1, h_high)
    elif band == 2:
        f_pan2 = np.multiply(f_pan2, h_high)
    elif band == 3:
        f_pan3 = np.multiply(f_pan3, h_high)

def filter_ms_mt(band, h_low):
    import numpy as np
    global f_ms1
    global f_ms2
    global f_ms3
    if band == 1:
        f_ms1 = np.multiply(f_ms1, h_low)
    elif band == 2:
        f_ms2 = np.multiply(f_ms2, h_low)
    elif band == 3:
        f_ms3 = np.multiply(f_ms3, h_low)
        
def create_f_ps_im_mt(band):
    global f_pan
    global f_pan1
    global f_ms1
    global f_ps1    
    global f_pan2    
    global f_ms2
    global f_ps2    
    global f_pan3
    global f_ms3
    global f_ps3    
    if band == 1:
        f_ps1 = f_pan1 + f_ms1
    elif band == 2:
        f_ps2 = f_pan2 + f_ms2
    elif band == 3:
        f_ps3 = f_pan3 + f_ms3
    elif band == 11:
        f_ps1 = f_pan + f_ms1
    elif band == 22:
        f_ps2 = f_pan + f_ms2
    elif band == 33:
        f_ps3 = f_pan + f_ms3
    
def ifft2_mt(band):
    import numpy as np
    global f_ps1
    global f_ps2
    global f_ps3
    global ps1
    global ps2
    global ps3
    if band == 1:
        ps1 = np.fft.ifft2(f_ps1)
    elif band == 2:
        ps2 = np.fft.ifft2(f_ps2)
    elif band == 3:
        ps3 = np.fft.ifft2(f_ps3)
    
def inverse_ihs_mt(band, ihs):
    global f_pan
    global ms1
    global ms2
    global ms3
    global ps1
    global ps2
    global ps3
    if band == 1:
        ps1 = (f_pan + ms1 - ihs)
    elif band == 2:
        ps2 = (f_pan + ms2 - ihs)
    elif band == 3:
        ps3 = (f_pan + ms3 - ihs)
       






"""
##############################################################################
    Starting Main Program
##############################################################################
"""
if __name__ == "__main__":
    # Params
    load_params(sys.argv[1:])
    print_params()
    
    # Load images
    print '#'*50
    print 'Compute Performance'
    start = time.time()
    pan, ms1, ms2, ms3 = load_datas_for_pansharpenning(path_im_pan, path_im_ms)
    print("%-20s : %f") % ("Image load time", time.time() - start)
    m, n = np.shape(pan)
    # Initialize vars
    f_pan = np.empty((m,n), dtype='float64')
    f_pan1 = np.empty((m,n), dtype='float64')
    f_pan2 = np.empty((m,n), dtype='float64')
    f_pan3 = np.empty((m,n), dtype='float64')
    f_ms1 = np.empty((m,n), dtype='complex128')
    f_ms2 = np.empty((m,n), dtype='complex128')
    f_ms3 = np.empty((m,n), dtype='complex128')
    f_ps1 = np.empty((m,n), dtype='complex128')
    f_ps2 = np.empty((m,n), dtype='complex128')
    f_ps3 = np.empty((m,n), dtype='complex128')
    ps1 = np.empty((m,n), dtype='float64')
    ps2 = np.empty((m,n), dtype='float64')
    ps3 = np.empty((m,n), dtype='float64')
    try:
        time_scores = []
        for i in range(run_times):
            start = time.time()
            h_low = ffilters(filter_name, m, n, cutoff_freq, 1)
            h_high = np.ones((m,n)) - h_low
    
            if (ps_method == 'fft' and is_multi_thread):
                # Initialize threads
                # Part 1 - Histogram matching
                th1 = th.Thread(target=hist_match_mt, name='th1', args=(1,))
                th2 = th.Thread(target=hist_match_mt, name='th2', args=(2,))
                th3 = th.Thread(target=hist_match_mt, name='th3', args=(3,))
                # Part 2 - FFT PAN
                th4 = th.Thread(target=fft2_pan_mt, name='th4', args=(1,))
                th5 = th.Thread(target=fft2_pan_mt, name='th5', args=(2,))
                th6 = th.Thread(target=fft2_pan_mt, name='th6', args=(3,))
                # Part 3 - Filtering PAN
                th7 = th.Thread(target=filter_pan_mt, name='th7', args=(1,h_high))
                th8 = th.Thread(target=filter_pan_mt, name='th8', args=(2,h_high))
                th9 = th.Thread(target=filter_pan_mt, name='th9', args=(3,h_high))
                # Part 4 - FFT MS
                th10 = th.Thread(target=fft2_ms_mt, name='th10', args=(1,))
                th11 = th.Thread(target=fft2_ms_mt, name='th11', args=(2,))
                th12 = th.Thread(target=fft2_ms_mt, name='th12', args=(3,))
                # Part 5 - Filtering MS
                th13 = th.Thread(target=filter_ms_mt, name='th13', args=(1,h_low))
                th14 = th.Thread(target=filter_ms_mt, name='th14', args=(2,h_low))
                th15 = th.Thread(target=filter_ms_mt, name='th15', args=(3,h_low))
                # Part 6 - Creating Pan-Sharpenned Image
                th16 = th.Thread(target=create_f_ps_im_mt, name='th16', args=(1,))
                th17 = th.Thread(target=create_f_ps_im_mt, name='th17', args=(2,))
                th18 = th.Thread(target=create_f_ps_im_mt, name='th18', args=(3,))
                # Part7 - I-FFT of PS Image
                th19 = th.Thread(target=ifft2_mt, name='th19', args=(1,))
                th20 = th.Thread(target=ifft2_mt, name='th20', args=(2,))
                th21 = th.Thread(target=ifft2_mt, name='th21', args=(3,))
                # Run Part 1 - Histogram matching
                th1.start(); th2.start(); th3.start()                
                # Run Part 2 - FFT PAN
                th1.join(); th4.start()                
                th2.join(); th5.start()
                th3.join(); th6.start()
                # Run Part 3 - Filtering PAN
                th4.join(); th7.start()
                th5.join(); th8.start()
                th6.join(); th9.start()
                # Run Part 4 - FFT MS
                th10.start(); th11.start(); th12.start()
                # Run Part 5 - Filtering MS
                th10.join(); th13.start()
                th11.join(); th14.start()
                th12.join(); th15.start()
                # Run Part 6 - Creating Pan-Sharpenned Image
                th7.join(); th13.join(); th16.start()
                th8.join(); th14.join(); th17.start()
                th9.join(); th15.join(); th18.start()
                # Run Part7 - I-FFT of PS Image
                th16.join(); th19.start()
                th17.join(); th20.start()
                th18.join(); th21.start()
                # Wait till all threads are done
                th19.join(); th20.join(); th21.join()
            elif (ps_method == 'ihs' and (is_multi_thread)):
                # IHS Transform
                ihs = np.multiply((1.0/3.0), (ms1 + ms2 + ms3))
                # Histogram matching
                f_pan = hist_match(pan, ihs)
                th1 = th.Thread(target=inverse_ihs_mt, name='th1', args=(1,ihs))
                th2 = th.Thread(target=inverse_ihs_mt, name='th1', args=(2,ihs))
                th3 = th.Thread(target=inverse_ihs_mt, name='th1', args=(3,ihs))
                th1.start(); th2.start(); th3.start()
                th1.join(); th2.join(); th3.join()
            elif (ps_method == 'ihs_fft' and (is_multi_thread)):
                # IHS Transform
                ihs = np.multiply((1.0/3.0), (ms1 + ms2 + ms3))
                # Part 1&2 - Histogram matching & FFT PAN
                f_pan = np.fft.fft2(hist_match(pan, ihs))
                # Part 3 - Filtering PAN
                f_pan = f_pan * h_high
                # Part 4 - FFT MS
                th1 = th.Thread(target=fft2_ms_mt, name='th1', args=(1,))
                th2 = th.Thread(target=fft2_ms_mt, name='th2', args=(2,))
                th3 = th.Thread(target=fft2_ms_mt, name='th3', args=(3,))
                # Part 5 - Filtering MS
                th4 = th.Thread(target=filter_ms_mt, name='th4', args=(1,h_low))
                th5 = th.Thread(target=filter_ms_mt, name='th5', args=(2,h_low))
                th6 = th.Thread(target=filter_ms_mt, name='th6', args=(3,h_low))
                # Part 6 - Creating Pan-Sharpenned Image
                th7 = th.Thread(target=create_f_ps_im_mt, name='th7', args=(11,))
                th8 = th.Thread(target=create_f_ps_im_mt, name='th8', args=(22,))
                th9 = th.Thread(target=create_f_ps_im_mt, name='th9', args=(33,))
                # Part7 - I-FFT of PS Image
                th10 = th.Thread(target=ifft2_mt, name='th10', args=(1,))
                th11 = th.Thread(target=ifft2_mt, name='th11', args=(2,))
                th12 = th.Thread(target=ifft2_mt, name='th12', args=(3,))
                # Run Part 4
                th1.start(); th2.start(); th3.start()
                # Run Part 5
                th1.join(); th4.start()
                th2.join(); th5.start()
                th3.join(); th6.start()
                # Run Part 6
                th4.join(); th7.start()
                th5.join(); th8.start()
                th6.join(); th9.start()
                # Run Part 7
                th7.join(); th10.start()
                th8.join(); th11.start()
                th9.join(); th12.start()
                # Wait till all threads are done
                th10.join(); th11.join(); th12.join()
            elif (ps_method == 'lab' and (is_multi_thread)):
                pass
            elif (ps_method == 'lab_fft' and (is_multi_thread)):
                pass
            elif (ps_method == 'brovey' and (is_multi_thread)):
                pass
            elif (ps_method == 'hfm' and (is_multi_thread)):
                pass
            elif (not is_multi_thread):
                ps1, ps2, ps3 = pansharpenning(ps_method, pan, ms1, ms2, ms3, 
                                            filter_name='ideal_lpf', 
                                            cutoff_freq=.125)
            time_scores.append(time.time() - start)
    except Exception as e:
        print(str(e))
    print '#'*50
    print 'Compute Performance'
    print ("%-20s : %f") % ("Pansharpenning Compute Time ", np.mean(time_scores))
    
        
    
    # Performance results
    print '#'*50
    print "Quality Report"
    im_ps = np.empty((m,n,3), dtype='float64')
    im_ref = np.empty((m,n,3), dtype='float64')
    im_ps[:,:,0] = np.abs(ps1); im_ps[:,:,1] = np.abs(ps2); im_ps[:,:,2] = np.abs(ps3)
    im_ref[:,:,0] = ms1; im_ref[:,:,1] = ms2; im_ref[:,:,2] = ms3
    results = []
    for p_method in ['SAM','RMSE','RASE','ERGAS']:
        result = ps_quality_score(p_method, im_ps, im_ref, 
                                  xml_file=path_xml, ms_pan_ratio=0.25)
        results.append({p_method: result})
        print p_method, "\tscores:", str(result)
    
    

    
    # Print
    """
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    ax1.imshow(pan,cmap=plt.cm.gray)
    ax2.imshow(pan,cmap=plt.cm.gray)
    
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    ax1.imshow(ms1,cmap=plt.cm.Reds)
    ax2.imshow(a1,cmap=plt.cm.Reds)
    
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    ax1.imshow(ms2,cmap=plt.cm.Greens)
    ax2.imshow(a2,cmap=plt.cm.Greens)
    
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    ax1.imshow(ms3,cmap=plt.cm.Blues)
    ax2.imshow(ps3.astype('float32'),cmap=plt.cm.Blues)
    
    
    fig, (ax1, ax2, ax3) = plt.subplots(ncols=3)
    ax1.imshow(np.abs(ps1).astype('float64'),cmap=plt.cm.Reds)
    ax2.imshow(np.abs(ps2).astype('float64'),cmap=plt.cm.Greens)
    ax3.imshow(np.abs(ps3).astype('float64'),cmap=plt.cm.Blues)
    
    
    start = time.time()
    ps11, ps22, ps33 = pansharpenning_mt('fft', pan, ms1, ms2, ms3, 'ideal_low', cutoff_freq=.125)
    print "## ", str(time.time() - start), " seconds."
    start = time.time()
    ps1, ps2, ps3 = pansharpenning('fft', pan, ms1, ms2, ms3, 'ideal_low',  cutoff_freq=.125)
    print "## ", str(time.time() - start), " seconds."
    
    fig, (ax1, ax2) = plt.subplots(ncols=2)
    ax1.imshow(ps1.astype('float64'),cmap=plt.cm.gray)
    ax2.imshow(ps11.astype('float64'),cmap=plt.cm.gray)
    
    
    """