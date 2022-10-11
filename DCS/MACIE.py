from ctypes import *
from DCS.DC_def import*

MACIE_OK = 0
MACIE_FAIL = 1

MACIE_NONE = 0
MACIE_USB = 1
MACIE_GigE = 2
MACIE_UART = 3

#MACIE_STATUS = {0:MACIE_OK, 1:MACIE_FAIL}
#MACIE_Connection = {0:MACIE_NONE, 1: MACIE_USB, 2:MACIE_GigE, 3:MACIE_UART}

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

HDR_INT = 0
HDR_FLOAT = 1
HDR_STR = 2

#need to check!!!
MACIE_ERROR_COUNTERS = 33

#Fits_HdrType = {0:HDR_INT, 1:HDR_FLOAT, 2:HDR_STR}

'''
class MACIE_FitsHdr(Structure):
    _fields_ = [("key", c_char*9),
                ("valType", c_int),
                ("iVal", c_int),
                ("fVal", c_float),
                ("sVal", c_char*72),
                ("comment", c_char*72)]
'''

lib = CDLL("/home/dcss/macie_v5.2_centos/MacieApp/libMACIE.so")
 
#input, output parameters  
lib.MACIE_LibVersion.restype = c_float  
lib.MACIE_Error.restype = c_char_p
lib.MACIE_Free.restype = c_int
lib.MACIE_Init.restype = c_int

lib.MACIE_SetGigeTimeout.argtypes = [c_ushort]
lib.MACIE_SetGigeTimeout.restype = c_int

lib.MACIE_CheckInterfaces.argtypes = [c_ushort, POINTER(MACIE_IpAddr), c_ushort, POINTER(c_ushort), POINTER(POINTER(MACIE_CardInfo))]
lib.MACIE_CheckInterfaces.restype = c_int

lib.MACIE_GetHandle.argtypes = [c_ushort, c_int]
lib.MACIE_GetHandle.restype = c_ulong

lib.MACIE_GetAvailableMACIEs.argtypes = [c_ulong]
lib.MACIE_GetAvailableMACIEs.restype = c_ubyte  #unsigned char

lib.MACIE_ReadMACIEReg.argtypes = [c_ulong, c_ubyte, c_ushort, POINTER(c_uint)]
lib.MACIE_ReadMACIEReg.restype = c_int

lib.MACIE_loadMACIEFirmware.argtypes = [c_ulong, c_ubyte, c_bool, POINTER(c_uint)]
lib.MACIE_loadMACIEFirmware.restype = c_int

lib.MACIE_DownloadMACIEFile.argtypes = [c_ulong, c_ubyte, c_char_p]
lib.MACIE_DownloadMACIEFile.restype = c_int

lib.MACIE_ReadMACIEBlock.argtypes = [c_ulong, c_ubyte, c_ushort, POINTER(c_uint), c_int]
lib.MACIE_ReadMACIEBlock.restype = c_int

lib.MACIE_ResetErrorCounters.argtypes = [ c_ulong, c_ubyte]
lib.MACIE_ResetErrorCounters.restype = c_int

lib.MACIE_WriteASICReg.argtypes = [c_ulong, c_ubyte, c_ushort, c_uint, c_bool]
lib.MACIE_WriteASICReg.restype = c_int

lib.MACIE_DownloadASICFile.argtypes = [c_ulong, c_ubyte, c_char_p, c_bool] 
lib.MACIE_DownloadASICFile.restype = c_int

lib.MACIE_GetAvailableASICs.argtypes = [c_ulong, c_int]
lib.MACIE_GetAvailableASICs.restype = c_ubyte

lib.MACIE_ReadASICReg.argtypes = [c_ulong, c_ubyte, c_ushort, POINTER(c_uint), c_bool, c_bool]
lib.MACIE_ReadASICReg.restype = c_int

lib.MACIE_ReadASICBlock.argtypes = [c_ulong, c_ubyte, c_ushort, POINTER(c_uint), c_int, c_bool, c_bool]
lib.MACIE_ReadASICBlock.restype = c_int

lib.MACIE_GetErrorCounters.argtypes = [c_ulong, c_ubyte, POINTER(c_ushort)]
lib.MACIE_GetErrorCounters.restype = c_int

lib.MACIE_ConfigureGigeScienceInterface.argtypes = [c_ulong, c_ubyte, c_ushort, c_int, c_ushort, POINTER(c_int)]
lib.MACIE_ConfigureGigeScienceInterface.restype = c_int

lib.MACIE_AvailableScienceData.argtypes = [c_ulong]
lib.MACIE_AvailableScienceData.restype = c_ulong

lib.MACIE_ReadGigeScienceFrame.argtypes = [c_ulong, c_ushort]
lib.MACIE_ReadGigeScienceFrame.restype = POINTER(c_ushort)

lib.MACIE_CloseGigeScienceInterface.argtypes = [c_ulong, c_ubyte]
lib.MACIE_CloseGigeScienceInterface.restype = c_int

#lib.MACIE_WriteFitsFile.argtypes = [c_char_p, c_ushort, c_ushort, POINTER(c_ushort), c_ushort, POINTER(MACIE_FitsHdr)]
#lib.MACIE_WriteFitsFile.restype = c_int

lib.MACIE_GetTelemetryAll.argtypes = [c_ulong, c_ubyte, POINTER(c_float)]
lib.MACIE_GetTelemetryAll.restype = c_int
