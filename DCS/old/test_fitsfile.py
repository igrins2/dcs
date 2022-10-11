'''
import astropy.io.fits as fits

filename = "/home/dcs/macie_v5.2_centos/MacieApp/data/macie/H2RG_ASIC/CDS/20220523135356/Frame_R01_M01_N02.fits"

#headers = fits.getheader(filename)
#print(headers)

hdulist = fits.open(filename)
hdu = fits.PrimaryHDU(hdulist[0].data)

hdul = fits.HDUList([hdu])
hdul[0].header = hdulist[0].header[:-5]
                        
hdul[0].header["SAMPLING"] = (1, "Sample number")
                       
#print(hdul.info())

hdul[0].header["COMMENT"] = "This FITS file may contain long string keyword values that are"
hdul[0].header["COMMENT"] = "continued over multiple keywords.  This convention uses the  '&'"
hdul[0].header["COMMENT"] = "character at the end of a string which is then continued"
hdul[0].header["COMMENT"] = "on subsequent keywords whose name = 'CONTINUE'."

hdul[0].header["FITSFILE"] = "/home/dcs/macie/"
hdul[0].header["CONTINUE"] = "test.fits"        

hdul.writeto("/home/dcs/macie/test.fits")
hdul.close()
'''

'''
list1 = [i for i in range(10)]
print(list1)
list2 = [0 for i in range(5)]
list2[:] = list1[0:5]
print(list2)
'''

from astropy.time import Time

times = '2022-05-26T02:03:20.504298'
t = Time(times, format='isot', scale='utc')
print(t)
print(t.to_value('jd', 'long'))