from numpy import *
from ctypes import *
  
lib = CDLL("/home/dcs/macie_v5.2_centos/MacieApp/libMACIE.so")

MACIE_OK = 0
MACIE_FAIL = 1

HDR_INT = 0
HDR_FLOAT = 1
HDR_STR = 2

# Version
lib.MACIE_LibVersion.restype = c_float  
msg = "Version: %f" % lib.MACIE_LibVersion()
print(msg)

# Init
lib.MACIE_Init.restype = c_ushort
bRet = lib.MACIE_Init()
if bRet == MACIE_OK:
    print("MACIE_Init: succeeded")
else:
    print("MACIE_Init: failed")
    
# SetGigeTimeout
lib.MACIE_SetGigeTimeout.argtypes = [c_ushort]
lib.MACIE_SetGigeTimeout.restype = c_ulong

bRet = lib.MACIE_SetGigeTimeout(1000)
if bRet == MACIE_OK:
    print("MACIE_SetGigeTimeout: succeeded")

'''
ct_str = [(c_char*9) for _ in range(3)]
#ct_str = c_byte * 9
for i in range(3):
    ct_str[i] = 'Hi again'.encode()
    print(ct_str[i])
'''

# SaveFitsFile
class MACIE_FitsHdr(Structure):
    _fields_ = [("key", c_char*9),
                ("valType", c_int),
                ("iVal", c_int),
                ("fVal", c_float),
                ("sVal", c_char*72),
                ("comment", c_char*72)]


lib.MACIE_WriteFitsFile.argtypes = [c_char_p, c_ushort, c_ushort, POINTER(c_ushort), c_ushort, POINTER(MACIE_FitsHdr)]
lib.MACIE_WriteFitsFile.restype = c_int

#pHeaders = pt_MACIE_FITSHDR(MACIE_FitsHdr())
#header_array = MACIE_FitsHdr * 3
#print(header_array)

#headers = header_array(MACIE_FitsHdr(),
#                        MACIE_FitsHdr(),
#                        MACIE_FitsHdr())
#print(headers[0])

header_array = MACIE_FitsHdr * 4
headers = header_array()

headers[0] = MACIE_FitsHdr(key="ASICGAIN".encode(), valType=HDR_INT, iVal=1, comment="SIDECAR Preamp gain setting".encode())
print(headers[0].key, headers[0].comment)

headers[1] = MACIE_FitsHdr(key="FrmTime".encode(), valType=HDR_FLOAT, fVal=1.47, comment="Frame time at slow mode".encode())
print(headers[1].key, headers[1].comment)

headers[2] = MACIE_FitsHdr(key="AcqDate".encode(), valType=HDR_STR, sVal="20220402".encode(), comment="Test comments here".encode())
print(headers[2].key, headers[2].comment)

headers[3] = MACIE_FitsHdr(key="history".encode(), valType=HDR_STR, sVal="60K".encode(), comment="bench temp.".encode())

arr_list = [1 for i in range(2048) for j in range(2048)]
arr = array(arr_list, dtype=int16)
print(arr)
arr_type =arr.ctypes.data_as(POINTER(c_ushort))
#headers_type =arr.ctypes.data_as(POINTER(c_byte))
#print(headers_type)
sts= lib.MACIE_WriteFitsFile(c_char_p("test.fits".encode()), 2048, 2048, arr_type, 4, headers)
print(sts)


#import astropy.io.fits as fits
'''
class MACIE_IpAddr(Structure):
    _fields_ = [("ipAddr", c_ubyte*4)]

class MACIE_CardInfo(Structure):
    _fields_ = [("macieSerialNumber", c_ushort),
                ("bUART", c_bool),
                ("bGigE", c_bool),
                ("bUSB", c_bool),
                ("ipAddr", c_ubyte*4),
                ("gigeSpeed", c_ushort),
                ("serialPortName", c_char*10),
                ("usbSerialNumber", c_char*16),
                ("firmwareSlot1", c_char*100),
                ("firmwareSlot2", c_char*100),
                ("usbSpeed", c_ushort)]

lib.MACIE_CheckInterfaces.argtypes = [c_ushort, POINTER(MACIE_IpAddr), c_ushort, POINTER(c_ushort), POINTER(POINTER(MACIE_CardInfo))]
lib.MACIE_CheckInterfaces.restype = c_int

gigecmdport = c_ushort()
ip = MACIE_IpAddr()

arr_list = [0, 1]
arr = array(arr_list)
print(arr)

card = arr.ctypes.data_as(POINTER(c_ushort))
Cards = pointer(pointer(MACIE_CardInfo()))
#cardinfo = pointer(Cards())

sts = lib.MACIE_CheckInterfaces(gigecmdport, ip, 0, card, Cards)
print(sts)
print(Cards[0].contents.macieSerialNumber)
print(Cards[0].contents.bUART)
print(Cards[0].contents.bGigE)
print(Cards[0].contents.bUSB)
print(Cards[0].contents.ipAddr[0],Cards[0].contents.ipAddr[1],Cards[0].contents.ipAddr[2],Cards[0].contents.ipAddr[3])
print(Cards[0].contents.gigeSpeed)
print(Cards[0].contents.macieSerialNumber)
print(Cards[0].contents.serialPortName)
print(Cards[0].contents.usbSerialNumber)
print(Cards[0].contents.firmwareSlot1)
print(Cards[0].contents.firmwareSlot2)
print(Cards[0].contents.usbSpeed)
'''

'''
self.logwrite(BOTH, str(self.pCard[slctCard].contents.macieSerialNumber))
            self.logwrite(BOTH, "True" if self.pMACIE_FILE
            self.logwrite(BOTH, str(self.pCard[slctCard].contents.gigeSpeed))
            self.logwrite(BOTH, self.pCard[slctCard].contents.serialPortName)
            self.logwrite(BOTH, self.pCard[slctCard].contents.usbSerialNumber)
            self.logwrite(BOTH, self.pCard[slctCard].contents.firmwareSlot1)
            #self.logwrite(BOTH, self.pCard[slctCard].contents.firmwareSlot2)
            #self.logwrite(BOTH, self.pCard[slctCard].contents.usbSpeed) 
'''