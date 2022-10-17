# -*- coding:utf-8 -*-

"""
Created on Sep 27, 2022

Modified on 

@author: hilee
"""

# tunning: CDS Noise

import astropy.io.fits as fits
import numpy as np

def cal_mean(path):
    print("Get a mean value")

    head = fits.PrimaryHDU()
    frm = fits.open(path)
    data = frm[0].data
    head = frm[0].header

    #img = []
    img = np.array(data, dtype="f")
    
    _mean = np.mean(img)

    top_bottom_sum, left_right_sum = 0, 0
    
    top_bottom_sum = np.sum(img[0:4][:])
    top_bottom_sum += np.sum(img[2044:2048][:])

    for row in range(4, 2044):
        left_right_sum += np.sum(img[row][0:4])

    for row in range(4, 2044):
        left_right_sum += np.sum(img[row][2044:2048])

    offset_aver = (top_bottom_sum + left_right_sum) / ((2048*8) + (2040*8))

    '''
    top_bottom_sum2, left_right_sum2 = 0, 0
    
    for row in range(4):  
        for col in range(2048):
            top_bottom_sum2 += img[row][col]
 
    for row in range(2044, 2048):  
        for col in range(2048):
            top_bottom_sum2 += img[row][col]     

    for col in range(4):
        for row in range(4, 2044): 
            left_right_sum2 += img[row][col]
    
    for col in range(2044, 2048):
        for row in range(4, 2044):
            left_right_sum2 += img[row][col]

    total_aver2 = (top_bottom_sum2+left_right_sum2) / ((2048*8)+(2040*8))
    '''

    #print(top_bottom_sum, left_right_sum, total_aver)
    
    return _mean, offset_aver
    

#path = "/DCS/Data/CDSNoise/20220927_024513/Result/CDSNoise.fits"
#cal_mean(path)