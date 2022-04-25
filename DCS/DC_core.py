# -*- coding: utf-8 -*-

"""
Created on Mar 4, 2022

Modified on

@author: hilee
"""

import numpy as np
import astropy.io.fits as fits

from ctypes import *
from math import *
import time 
import os

from DCS.MACIE import *

class DC():
    def __init__(self, gui=False):
        
        self.gui = gui
        self.mainlogpath = "/home/dcs/macie/"
        self.logwrite(BOTH, "start DCS!!!")

        self.handle = 0
        self.slctMACIEs = 0
        self.slot1 = False  # slot 1-True, slot 2-False
        self.pCard = POINTER(POINTER((MACIE_CardInfo)))
        self.slctASICs = 0
        self.option = True

        self._24Bit = False  # 24bit-True, 16bit-False

        self.expTime = 0.0
        self.fowlerTime = 0.0

        self.preampInputScheme = 1    # 2
        self.preampInputVal = 0x4502    # 0xaaaa
        self.preampGain = 8  # 1

        self.samplingMode = UTR_MODE

        self.ROIMode = False
        self.x_start, self.x_stop, self.y_start, self.y_stop = 0, FRAME_X-1, 0, FRAME_Y
        self.resets, self.reads, self.ramps, self.groups = 1, 1, 1, 1 
        
        self.loadimg = None


    # Version
    def LibVersion(self):
        msg = "Version: %f" % lib.MACIE_LibVersion()
        self.logwrite(BOTH, msg)
        return msg

    # Error Msg
    def GetErrMsg(self):
        errMsg = lib.MACIE_Error()
        return errMsg

    # not yet!!!!
    # Memory Fee 
    def MemoryFree(self):
        sts = lib.MACIE_Free()
        res = ""
        if sts == MACIE_OK:
            res =  RET_OK
        else:
            res = RET_FAIL
        self.logwrite(BOTH, "MACIE_Free: " + res)
        return sts


    # Init
    def Init(self):
        sts = lib.MACIE_Init()
        res = ""
        if sts == MACIE_OK:
            res = RET_OK
        else:
            res = RET_FAIL
        self.logwrite(BOTH, "MACIE_Init: " + res)
        return sts


    # SetGigeTimeout
    def SetGigeTimeout(self):
        sts = lib.MACIE_SetGigeTimeout(1000)
        if sts == MACIE_OK:
            self.logwrite(BOTH, "MACIE_SetGigeTimeout: " + RET_OK)
            return True
        else:
            return False
        

    # CheckInterfaces
    def CheckInterfaces(self):
        numCards = c_ushort(1)

        slctCard = 0
        connection = MACIE_NONE

        try:
            sts = lib.MACIE_CheckInterfaces(0, None, 0, numCards, self.pCard)
            res = ""
            if sts == MACIE_OK:
                res = RET_OK
            else:
                res = RET_FAIL
            self.logwrite(BOTH, "MACIE_CheckInterfaces: " + res)

            if self.pCard == None:
                self.logwrite(BOTH, RET_FAIL)

            self.logwrite(BOTH, str(numCards))
            self.logwrite(BOTH, str(numCards.value))

            self.logwrite(BOTH, str(self.pCard[slctCard].contents.macieSerialNumber))
            self.logwrite(BOTH, "True" if self.pCard[slctCard].contents.bUART == True else "False")
            self.logwrite(BOTH, "True" if self.pCard[slctCard].contents.bGigE == True else "False")
            self.logwrite(BOTH, "True" if self.pCard[slctCard].contents.bUSB == True else "False")
            ipaddr = "%d.%d.%d.%d" % (self.pCard[slctCard].contents.ipAddr[0], self.pCard[slctCard].contents.ipAddr[1], self.pCard[slctCard].contents.ipAddr[2], self.pCard[slctCard].contents.ipAddr[3])
            self.logwrite(BOTH, ipaddr)
            self.logwrite(BOTH, str(self.pCard[slctCard].contents.gigeSpeed))
            self.logwrite(BOTH, self.pCard[slctCard].contents.serialPortName)
            self.logwrite(BOTH, self.pCard[slctCard].contents.usbSerialNumber)
            self.logwrite(BOTH, self.pCard[slctCard].contents.firmwareSlot1)
            #self.logwrite(BOTH, self.pCard[slctCard].contents.firmwareSlot2)
            #self.logwrite(BOTH, self.pCard[slctCard].contents.usbSpeed) 

            return True

        except:
            return False


    # GetHandle
    def GetHandle(self):
        slctCard = 0
        connection = MACIE_GigE  # input by user

        self.handle = lib.MACIE_GetHandle(
            self.pCard[slctCard].contents.macieSerialNumber, connection)
        msg = "Handle = %d" % self.handle
        self.logwrite(BOTH, msg)


    def GetAvailableMACIEs(self):
        if self.handle == 0:
            return False

        avaiMACIEs = lib.MACIE_GetAvailableMACIEs(self.handle)
        msg = "MACIE_GetAvailableMACIEs = %d" % avaiMACIEs
        self.logwrite(BOTH, msg)

        self.slctMACIEs = avaiMACIEs & 1
        val = 0
        msg = ""
        if self.slctMACIEs == 0:
            msg = "Select MACIE = %d invalid" % avaiMACIEs
        elif lib.MACIE_ReadMACIEReg(self.handle, self.slctMACIEs, MACIE_Reg, val) != MACIE_OK:
            msg = "MACIE read %d failed: %s" % (MACIE_Reg, self.GetErrMsg())
        else:
            msg = "MACIE h%04x = %04x" % (MACIE_Reg, val)
        self.logwrite(BOTH, msg)

        return True


    def Initialize(self, timeout=200):

        # self.InitBuffer()

        # 1. init
        if self.Init() == MACIE_FAIL:
            return False

        # 2. SetGigeTimeout
        if self.SetGigeTimeout() == False:
            return False
        
        # 3. CheckInterfaces
        if self.CheckInterfaces() == False:
            return False

        # 4. GetHandle
        self.GetHandle()

        # 5. GetAvailableMACIEs
        if self.GetAvailableMACIEs() == False:
            return False

        self.logwrite(BOTH, "Initialize " + RET_OK)

        return True


    def Initialize2(self):

        if self.handle == 0:
            return False

        msg = "Initialize with handle: %ld" % self.handle
        self.logwrite(BOTH, msg)

        if self.slctMACIEs == 0:
            self.logwrite(BOTH, "MACIE0 is not available")
            return False

        val = 0

        # step 1. load MACIE firmware from slot1 or slot2
        if lib.MACIE_loadMACIEFirmware(self.handle, self.slctMACIEs, self.slot1, val) != MACIE_OK:
            msg = "LOAD MACIE firmware " + RET_FAIL + ": " + self.GetErrMsg()
            self.logwrite(BOTH, msg)
            return False
        if val != 0xac1e:
            msg = "Verification of MACIE firmware load failed: readback of hFFFB = %d" % val
            self.logwrite(BOTH, msg)
            return False
        self.logwrite(BOTH, "Load MACIE firmware " + RET_OK)

        # step 2. download MACIE registers
        filename = "/home/dcs/macie_v5.2_centos/LoadFiles/DC/MACIE_Registers_Slow.mrf"
        if lib.MACIE_DownloadMACIEFile(self.handle, self.slctMACIEs, filename) != MACIE_OK:
            msg = "Download MACIE register file " + RET_FAIL + ": " + self.GetErrMsg()
            self.logwrite(BOTH, msg)
            return False
        self.logwrite(BOTH, "Download MACIE register file " + RET_OK)

        # check again!!!
        data = [0 for _ in range(5)]
        res = -1
        sts = lib.MACIE_ReadMACIEBlock(
            self.handle, self.slctMACIEs, MACIE_Block_Reg, data, 5)
        if sts != MACIE_OK:
            res = sts
        else:
            for i in range(5):
                msg = "val h%04x = %04x" % (MACIE_Block_Reg, data[i])
                self.logwrite(BOTH, msg)
            res = data[1]

        self.logwrite(BOTH, "Initialize2 " + RET_OK)

        return True


    def ResetASIC(self):
        if self.handle == 0:
            return False

        # step 1. reset science data error counters
        if lib.MACIE_ResetErrorCounters(self.handle, self.slctMACIEs) != MACIE_OK:
            self.logwrite(BOTH, "Reset MACIE error counters " + RET_FAIL)
            return False
        self.logwrite(BOTH, "Reset error counters " + RET_OK)

        # step 2. download ASIC file
        if lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_State, 0x8002, self.option) != MACIE_OK:
            self.logwrite(BOTH, "Reconfiguration sequence " + RET_FAIL)
            return False
        self.logwrite(BOTH, "Reconfiguration sequence" + RET_OK)

        self.logwrite(BOTH, "ResetASIC" + RET_OK)

        return True
        

    def DownloadMCD(self):
        if self.handle == 0:
            return False

        # step 1. downlaod asic file
        asicfile = "/home/dcs/macie_v5.2_centos/LoadFiles/DC/HxRG_Main_uj211205a.mcd"
        sts = lib.MACIE_DownloadASICFile(
            self.handle, self.slctMACIEs, asicfile, True)
        if sts != MACIE_OK:
            self.logwrite(BOTH, "Download ASIC firmware " + RET_FAIL + ":" + self.GetErrMsg())
            return False
        self.logwrite(BOTH, "Download ASIC firmware " + RET_OK)

        # step 2. checking!!!
        self.slctASICs = lib.MACIE_GetAvailableASICs(self.handle, False)
        if self.slctASICs == 0:
            self.logwrite(BOTH, "MACIE_GetAvailableASICs " + RET_FAIL)
            return False
        else:
            val = 0
            lib.MACIE_ReadASICReg(
                self.handle, self.slctASICs, ASICAddr, val, self._24Bit, self.option)
            msg = "ASIC h%04x = %04x" % (ASICAddr, val)
            self.logwrite(BOTH, msg)

            data = [0 for _ in range(5)]
            lib.MACIE_ReadASICBlock(
                self.handle, self.slctASICs, ASICAddr_NResets, data, 5, self._24Bit, self.option)
            for i in range(5):
                msg = "val h%04x = %04x" % (ASICAddr_NResets + i, data[i])
                self.logwrite(BOTH, msg)
        msg = "Available ASICs = %d" % self.slctASICs
        self.logwrite(BOTH, msg)

        self.logwrite(BOTH, "DownloadMCD " + RET_OK)

        return True


    def SetDetector(self, muxType, outputs):  # muxType = 2 (H2RG)
        if self.handle == 0:
            return False

        res = [MACIE_OK, MACIE_OK]

        res[0] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_HxRGVal, muxType, self.option)
        res[1] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_HxRGNumOutVal, outputs, self.option)

        for i in range(2):
            if res[i] != MACIE_FAIL:
                self.logwrite(BOTH, "Set Detector " + RET_FAIL)
                return False

        msg = "Set Detector (%d, %d) succeeded" % (muxType, outputs)
        self.logwrite(BOTH, msg)

        return True


    def GetErrorCounters(self):
        if self.handle == 0:
            return

        errArr = [0 for _ in range(lib.MACIE_ERROR_COUNTERS)]
        if lib.MACIE_GetErrorCounters(self.handle, self.slctMACIEs, errArr) != MACIE_OK:
            self.logwrite(BOTH, "Read MACIE error counter failed")
            return

        else:
            self.logwrite(BOTH, "Error counters....")
            for i in range(lib.MACIE_ERROR_COUNTERS):
                msg = "%d" % errArr[i]
                self.logwrite(BOTH, msg)


    def SetRampParam(self, p1, p2, p3, p4, p5):  # p1~p5 : int
        if self.handle == 0:
            return False

        res = [0 for _ in range(8)]

        res[0] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NResets, p1, self.option)
        res[1] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NReads, p2, self.option)
        res[2] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_Config, 12, self.option)
        res[3] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NRamps, p5, self.option)
        res[4] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NGroups, p3, self.option)
        res[5] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_nNDrops, p4, self.option)

        lowerCounter, upperCounter = 0, 0
        if self.expTime * pow(10, 6) >= BITSIZE_65536:
            upperCounter = int(
                (self.expTime * pow(10, 6) / 20) / BITSIZE_65536)
            lowerCounter = int(
                (self.expTime * pow(10, 6) / 20) % BITSIZE_65536)
        else:
            lowerCounter = int(self.expTime * pow(10, 6) / 20)
        res[6] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_TexpLower, lowerCounter, self.option)
        res[7] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_TexpUpper, upperCounter, self.option)

        for i in range(8):
            if res[i] != MACIE_OK:
                self.logwrite(BOTH, "SetRampParam failed - write ASIC registers")
                return False

        msg = "SetRampParam(%d, %d, %d, %d, %d)" % (p1, p2, p3, p4, p5)
        self.logwrite(BOTH, msg)

        return True


    def SetFSParam(self, p1, p2, p3, p4, p5):  # p1~5:int, p4:double
        if self.handle == 0:
            return False

        res = [0 for _ in range(9)]

        res[0] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NResets, p1, self.option)
        res[1] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NReads, p2, self.option)
        res[2] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_Config, 12, self.option)
        res[3] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NRamps, p5, self.option)
        res[4] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NGroups, p3, self.option)

        lowerCounter, upperCounter = 0, 0
        if p4 * pow(10, 6) >= BITSIZE_65536:
            upperCounter = int((p4 * pow(10, 6) / 20) / BITSIZE_65536)
            lowerCounter = int((p4 * pow(10, 6) / 20) % BITSIZE_65536)
        else:
            lowerCounter = int((p4 * pow(10, 6)) / 20)
        res[5] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_TfowlerLower, lowerCounter, self.option)
        res[6] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_TfowlerUpper, upperCounter, self.option)

        t_FowlerPair = 0
        # self.expTime = 2 * t_FowlerPair + p4
        t_FowlerPair = (self.expTime - p4) / 2
        if t_FowlerPair * pow(10, 6) >= BITSIZE_65536:
            upperCounter = int(
                ((t_FowlerPair * pow(10, 6)) / 20) / BITSIZE_65536)
            lowerCounter = int(
                ((t_FowlerPair * pow(10, 6)) / 20) % BITSIZE_65536)
        else:
            lowerCounter = int((t_FowlerPair * pow(10, 6)) / 20)
        res[7] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_TexpLower, lowerCounter, self.option)
        res[8] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_TexpUpper, upperCounter, self.option)

        for i in range(9):
            if res[i] != MACIE_OK:
                self.logwrite(BOTH, "SetFSParam failed - write ASIC registers")
                return False

        msg = "SetFSParam(%d, %d, %d, %f, %d)" % (p1, p2, p3, p4, p5)
        self.logwrite(BOTH, msg)

        return True


    def AcquireRamp(self):
        if self.handle == 0:
            return False

        self.logwrite(BOTH, "Acquire Science Data....")

        # step 1. ASIC configuration
        res = [0 for _ in range(6)]

        res[0] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_ASICInputRefVal, self.preampInputScheme, self.option)
        res[1] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_PreAmpReg1Ch1ENAddr, self.preampInputVal, self.option)
        res[2] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_ASICPreAmpGainVal, self.preampGain, self.option)
        res[3] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NReads, self.reads, self.option)
        res[4] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_NRamps, self.ramps, self.option)

        if self.samplingMode == UTR_MODE:
            if self.ROIMode == True:
                res[5] = lib.MACIE_WriteASICReg(
                    self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 2, self.option)  # UTR, window
                winarr = [self.xStart, self.xStop,
                          self.yStart, self.yStop]  # x1, x2, y1, y2
                wr = lib.MACIE_WriteASICBlock(
                    self.handle, self.slctASICs, ASICAddr_WinArr, winarr, 4, self.option)
            else:
                res[5] = lib.MACIE_WriteASICReg(
                    self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 0, self.option)  # UTR, Full frame
        else:
            if self.ROIMode == True:
                res[5] = lib.MACIE_WriteASICReg(
                    self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 3, self.option)  # FS, window
                winarr = [self.xStart, self.xStop,
                          self.yStart, self.yStop]  # x1, x2, y1, y2
                wr = lib.MACIE_WriteASICBlock(
                    self.handle, self.slctASICs, ASICAddr_WinArr, winarr, 4, self.option)
            else:
                res[5] = lib.MACIE_WriteASICReg(
                    self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 1, self.option)  # FS, Full frame
        res[6] = lib.MACIE_WriteASICReg(
            self.handle, self.slctASICs, ASICAddr_State, 0x8002, self.option)

        for i in range(7):
            if res[i] != MACIE_OK:
                self.logwrite(BOTH, "ASIC configuration failed - write ASIC registers")
                return False

        time.delay(1500)

        val = 0
        sts = lib.MACIE_ReadASICReg(
            self.handle, self.slctASICs, ASICAddr_State, val, self._24Bit, self.option)
        if (val & 1) != 0 or sts != MACIE_OK:
            self.logwrite(BOTH, "ASIC configuration for shorted preamp inputs failed")
            return False
        self.logwrite(BOTH, "Configuration succeeded")

        # step 2.science interface
        frameSize = 0
        if self.samplingMode == UTR_MODE:
            if self.ROIMode == True:
                frameSize = (self.xStop - self.xStart + 1) * \
                    (self.yStop - self.yStart + 1)
            else:
                frameSize = FRAME_X * FRAME_Y * self.reads * self.groups * self.ramps
        else:
            if self.ROIMode == True:
                frameSize = (self.xStop - self.xStart + 1) * \
                    (self.yStop - self.yStart + 1)
            else:
                frameSize = FRAME_X * FRAME_Y * 2 * self.reads * self.ramps

        buf = 0
        sts = lib.MACIE_ConfigureGigeScienceInterface(
            self.handle, self.slctMACIEs, 0, frameSize, 42037, buf)  # 0-16bit
        if sts != MACIE_OK:
            msg = "Science interface configuration failed. buf = %d" % buf
            self.logwrite(BOTH, msg)
            return False
        msg = "Science interface configuration succeeded. buf (KB) = %d" % buf
        self.logwrite(BOTH, msg)

        # step 3.trigger ASIC to read science data
        self.logwrite(BOTH, "Trigger image acquisition....")

        # make sure h6900 bit<0> is 0 before triggering.

        if lib.MACIE_ReadASICReg(self.handle, self.slctMACIEs, ASICAddr_State, val, self._24Bit, self.option) != MACIE_OK:
            msg = "Read ASIC h%04x failed" % ASICAddr_State
            self.logwrite(BOTH, msg)
            return False
        if (val & 1) != 0:
            msg = "Configure idle mode by writing ASIC h%04x failed" % ASICAddr_State
            self.logwrite(BOTH, msg)
            return False

        if lib.MACIE_WriteASICReg(self.handle, self.slctMACIEs, ASICAddr_State, 0x8001, self.option) != MACIE_OK:
            self.logwrite(BOTH, "Triggering " + RET_FAIL)
            return False

        self.logwrite(BOTH, "Triggering succeeded")

        return True

    
    def StopAcquisition(self):
        if self.handle == 0:
            return False

        if lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_State, 0x8002, self.option) != MACIE_OK:
            self.logwrite(BOTH, "Acquire Stop " + RET_FAIL)
            return False

        self.logwrite(BOTH, "Acquire Stop " + RET_OK)

        return True


    def ImageAcquisition(self):
        if self.handle == 0:
            return False

        # Wait for available science data bytes
        idleReset, moreDelay = 1, 2000
        triggerTimeout = (T_frame * 1000) * (self.Resets +
                                             idleReset) + moreDelay  # delay time for one frame

        time.delay(1500)

        getByte = 0
        if self.samplingMode == UTR_MODE:
            getByte = FRAME_X * FRAME_Y * 2 * self.reads * self.groups * self.ramps
            triggerTimeout *= self.reads * self.groups * self.ramps
        else:
            getByte = FRAME_X * FRAME_Y * 2 * 2 * self.reads * self.ramps
            triggerTimeout *= 2 * self.reads * self.ramps

        byte = 0
        for i in range(100):
            byte = lib.MACIE_AvailableScienceData(self.handle)
            if byte >= getByte:
                msg = "Available science data = %d bytes, Loop = %d" % (
                    byte, i)
                self.logwrite(BOTH, msg)
                break
            if self.ROIMode == True:
                self.logwrite(BOTH, "Wait (ROI)....")
            else:
                self.logwrite(BOTH, "Wait....")
            time.delay(triggerTimeout / 100)

        if byte <= 0:
            self.logwrite(BOTH, "Trigger timeout: no available science data")
            return False

        data = None
        data = lib.MACIE_ReadGigeScienceFrame(
            self.handle, 1500 + triggerTimeout)

        if data == None:
            if self.ROIMode:
                self.logwrite(BOTH, "Null frame (ROI)")
            else:
                self.logwrite(BOTH, "Null frame")
            return False

        frmcnt = 0
        if self.samplingMode == UTR_MODE:
            frmcnt = self.reads * self.groups * self.ramps
        else:
            frmcnt = 2 * self.reads * self.ramps

        self.loadimg = [[] for _ in range(frmcnt)]

        for i in range(frmcnt):
            start = FRAME_X * FRAME_Y
            self.loadimg[i] = data[start*i:start*(i+1)]

        self.WriteFitsFile()

        #exp_endT = clock()

        # CString strTemp
        #strTemp.Format(_T("%lf"), (double)(exp_endT - exp_startT) / CLK_TCK)
        # m_ctrlMeasureWaitTime.SetWindowTextW(strTemp)

        # m_nCurrentNum++
        #strTemp.Format(_T("%d / %d"), m_nCurrentNum, m_nRepeatNumber)
        # m_stsCurrentNum.SetWindowTextW(strTemp)
        #strMsg.Format(_T("Finished ") + strTemp)
        # SaveSystemLog(strMsg)

        lib.MACIE_CloseGigeScienceInterface(self.handle, self.slctMACIEs)

        # m_isWorkingThread=false
        # WaitForSingleObject(m_pThread -> m_hThread, 1000)
        #m_stsStatus.SetWindowTextW(_T("Finished thread"))

        return True


    def createFolder(self, dir):
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
        except OSError:
            self.logwrite(BOTH, "Error: Creating directory. " + dir)


    def WriteFitsFile(self):
        if self.ROIMode == True:
            self.logwrite(BOTH, "Write Fits file now (ROI)....")
        else:
            self.logwrite(BOTH, "Write Fits file now....")

        header_array = MACIE_FitsHdr * 3
        pHeaders = header_array()

        header_cnt = 0
        pHeaders[header_cnt] = MACIE_FitsHdr(key="NEXTRAP".encode(
        ), valType=HDR_INT, iVal=0, comment="Number of extral pixels per row".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="NEXTRAL".encode(
        ), valType=HDR_INT, iVal=1, comment="Number of extral line per frame".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        str = time.time()
        pHeaders[header_cnt] = MACIE_FitsHdr(key="ACQTIME".encode(
        ), valType=HDR_STR, sVal=str.encode(), comment="UTC Julian time".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        str = time.strftime("%Y-%m-%d-%H:%M:%S.%M",
                            time.localtime(time.time()))
        pHeaders[header_cnt] = MACIE_FitsHdr(key="ACQTIME1".encode(
        ), valType=HDR_STR, sVal=str.encode(), comment="UTC time (YYYY-MM-DD HH:MM:SS.MS".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        str = self.pCard[0].contents.macieSerialNumber
        pHeaders[header_cnt] = MACIE_FitsHdr(key="ASIC_NUM".encode(
        ), valType=HDR_STR, sVal=str.encode(), comment="ASIC serial number".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        # SCA_ID  = 'C001    '           /SCA number

        pHeaders[header_cnt] = MACIE_FitsHdr(key="MUXTYPE".encode(
        ), valType=HDR_INT, iVal=2, comment="1- H1RG; 2- H2RG; 4- H4RG".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="MUXTYPE".encode(
        ), valType=HDR_INT, iVal=2, comment="1- H1RG; 2- H2RG; 4- H4RG".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="NOUTPUTS".encode(
        ), valType=HDR_INT, iVal=32, comment="Number of detector outputs".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        # NADCS   =                    1 /Number of averaged ADCs used per output
        # PDDECTOR=                    0 /Power down detector
        # CLKOFF  =                    0 /Turn off clocks
        # WARMTST =                    0 /0- cold test; 1- warm test
        # CLOCKING=                    0 /0- normal clocking; 1- enhanced horizonal clocki
        # GLBRESET=                    0 /0- pixel-by-pixel or line-by-line rest; 1- globa

        pHeaders[header_cnt] = MACIE_FitsHdr(key="FRMODE".encode(
        ), valType=HDR_INT, iVal=self.ROIMode, comment="0- full frame mode; 1- window mode".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        if self.samplingMode == UTR_MODE:
            val = 0
        else:
            val = 1
        pHeaders[header_cnt] = MACIE_FitsHdr(key="EXPMODE".encode(
        ), valType=HDR_INT, iVal=val, comment="0- Ramp mode; 1- Fowler sampling mode".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="NRESETS".encode(
        ), valType=HDR_INT, iVal=self.resets, comment="Number of resets before integration".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="FRMTIME".encode(
        ), valType=HDR_FLOAT, fVal=self.fowlerTime, comment="Frame time at slow mode".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="EXPTIME".encode(
        ), valType=HDR_FLOAT, fVal=self.expTime, comment="sec".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        # ACQTYPE =                    2 /Dark Current Ramp Sequence(2)
        # DATAMODE=                    5 /Parallel read, 8 bit bus, 16 bit data
        #DATLEVEL=                    1 /0- CMO; 1- LVDS
        # ASICGAIN=                    8 /8 (12dB, large Cin)
        # NOMGAIN =                    8 /8 (12dB, large Cin)
        # AMPRESET=                    0 /0- Reset once per frame; 1- Reset once per row
        # KTCREMOV=                    0 /0- No kTC Removal; 1- kTC Removal
        # SRCCUR  =                    0 /0-No source current to inp ; 1 - Source current
        # AMPINPUT=                    1 /0- VREFMAIN as ref; 1- InPCommon as ref; 2- user

        str = str(self.preampInputVal)
        pHeaders[header_cnt] = MACIE_FitsHdr(key="V4V3V2V1".encode(
        ), valType=HDR_STR, sVal=str.encode(), comment="preamp input by user".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        # BZERO   =                32768 /Data is Unsigned Integer

        str = "ADU     "
        pHeaders[header_cnt] = MACIE_FitsHdr(key="UNITS".encode(
        ), valType=HDR_STR, sVal=str.encode(), comment="ADC digital steps".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        # TSTATION= 'Probe1  '           /Test station id.
        # HXRGVER = 'v2.3.2  '           /HXRG IDL software version number
        # BSCALE  =                    1 /No scaling
        # MCLK    =              10.0000 /MHz. Master Clock.

        pHeaders[header_cnt] = MACIE_FitsHdr(key="SEQNUM_R".encode(
        ), valType=HDR_INT, iVal=self.ramps, comment="Ramp number".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="SEQNUM_N".encode(
        ), valType=HDR_INT, iVal=self.reads, comment="Sample number within group".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        # INTTIME =            7.2739501 /integration time
        # SEQNUM_M=                    1 /0 before exposure; 1 after exposure.

        str = "R01_M01 "
        pHeaders[header_cnt] = MACIE_FitsHdr(key="SEQNNAME".encode(
        ), valType=HDR_STR, sVal=str.encode(), comment="Ramp and Group String".encode())
        self.logwrite(CMDLINE, pHeaders[header_cnt].key + "," + pHeaders[header_cnt].comment)
        header_cnt += 1

        path = "%s/Data/" % EXE_PATH
        self.createFolder(path)

        if self.samplingMode == UTR_MODE:  # single mode
            path += "UpTheRamp/"
        elif self.samplingMode == CDS_MODE:  # ramp=1, group=1, read=1
            path += "CDS/"
        elif self.samplingMode == CDSNOISE_MODE:  # ramp=2, group=1, read=1
            path += "CDSNoise/"
        elif self.samplingMode == FOWLER_MODE:  # ramp=1, group=1, read=1,2,4,8,16
            path += "Fowler/"
        self.createFolder(path)

        str = "%Y%m%d_%H%M%S" % time.localtime(time.time())
        path += str + "/"
        self.createFolder(path)

        arr = 0
        for ramp in range(self.ramps):
            for group in range(self.group):
                for read in range(self.reads):
                    filename = "%sH2RG_R%02d_M%02d_N%02d.fits" % (path,
                        ramp + 1, group+1, read + 1)
                    sts = lib.MACIE_WriteFitsFile(c_char_p(
                        filename.encode()), FRAME_X, FRAME_Y, self.loadimg[arr], header_cnt, pHeaders)

                    if sts != MACIE_OK:
                        self.logwrite(BOTH, "Write fits file failed: " + self.GetErrMsg())
                        # SaveSystemLog(strMsg);
                        return -1
                    else:
                        self.logwrite(BOTH, filename)

                    arr += 1

        #strMsg.Format(_T("%s %d %d"), strFullPath, m_nRamps, m_nReads);
        #pMsg.dwData = WM_CDS_MODE; WM_CDSNOISE_MODE;   WM_FOWLER_MODE

        start = 0
        startime = time.time()
        self.fowler_calculation(path)
        duration = time.time() - startime
        self.logwrite(BOTH, str(duration - start))


    def fowler_calculation(self, path):

        path += "Result/"
        group = 2  # fowler sampling prev, last
        channel = 32
        ch_pix_cnt = int(FRAME_X / channel)

        frm = 0
        for r in range(self.ramps):
            for g in range(self.groups):
                for n in range(self.reads):

                    # 1. top, bottom average
                    for ch in range(channel):
                        topbottom_sum = 0
                        aver = 0.0

                        for row in range(4):
                            topbottom_sum += np.sum(self.loadimg[frm][row][ch * ch_pix_cnt : (ch + 1) * ch_pix_cnt])

                        for row in range(FRAME_Y - 4, FRAME_Y):
                            topbottom_sum += np.sum(self.loadimg[frm][row][ch * ch_pix_cnt : (ch + 1) * ch_pix_cnt])
                        
                        aver = topbottom_sum / (ch_pix_cnt * 8)

                        for row in range(FRAME_Y):
                            self.loadimg[frm][row][ch * ch_pix_cnt : (ch + 1) * ch_pix_cnt] -= aver

                    # 2. row average
                    ROW_MULTI = 4  #2(5), 3(7), 4(9)

                    img_tmp = self.loadimg[frm]
                    for row in range(FRAME_Y):
                        RowSum, aver = 0, 0

                        startRow, endRow = 0, 0
                        if row - ROW_MULTI < 0:
                            startRow = 0
                        else:
                            startRow = row - ROW_MULTI
                        if row + ROW_MULTI > FRAME_Y - 1:
                            endRow = FRAME_Y - 1
                        else:
                            endRow = row + ROW_MULTI

                        # print(startRow, endRow)
                        for row2 in range(startRow, endRow + 1):
                            RowSum += np.sum(self.loadimg[frm][row2][0:4])
                            RowSum += np.sum(self.loadimg[frm][row2][FRAME_X - 4 : FRAME_X])

                        aver = RowSum / (8 * endRow - startRow + 1)
                        # print(row, img[i][row][:], aver)
                        img_tmp[:] -= aver
                        # print(row, img[i][row][:])

                    self.loadimg[frm] = img_tmp

                    frm += 1

                    if self.samplingMode == CDS_MODE:
                        res = self.loadimg[1][:] - self.loadimg[0][:]
                        filename = "%sCDSResult.fits" % path
                        self.save_fitsfile(filename, res)

                    elif self.samplingMode == CDSNOISE_MODE:
                        res = [[], []]
                        #S_n - P_n for each ramp.
                        for r in range(self.ramps):
                            res[r] = self.loadimg[self.ramps*r + 1][:] - self.loadimg[self.ramps*r][:]
                            filename = "%sCDSResult%d.fits" % (path, r+1)
                            self.save_fitsfile(filename, res[r])
                        #for one result
                        cds_result = (res[1][:] - res[0][:]) / np.sqrt(2)
                        filename = "%sCDSNoise.fits" % path
                        self.save_fitsfile(filename, cds_result)

                    elif self.samplingMode == FOWLER_MODE:
                        res = []
                        for n in range(self.reads):
                            res += self.loadimg[self.reads + n][:] - self.loadimg[n][:]
                        res[:] /= self.reads
                        filename = "%sCDSResult.fits" % path
                        self.save_fitsfile(filename, res)



    def save_fitsfile(self, filename, img):                     
        pass
        #add header!!!
        #fits.writeto(filename, img, header = head, output_verify="ignore", overwrite=True)


    def GetTelemetry(self):
        if self.handle == 0:
            return False

        tlm = [0.0 for _ in range(79)]
        if lib.MACIE_GetTelemetryAll(self.handle, self.slctMACIEs, tlm) != MACIE_OK:
            self.logwrite(BOTH, "MACIE_GetTelemetryAll ", RET_FAIL, ": ", self.GetErrMsg())
            return False
        else:
            self.logwrite(BOTH, "MACIE_GetTelemetryAll " +  RET_OK)
            for i in range(79):
                msg = "%f" % tlm[i]
                self.logwrite(BOTH, msg)

        return True 


    def logwrite(self, option, event):
        '''
        Function that write to file for Logging
        event : Logging Sentence
        option :  LOGGING(1) - Write to File
                  CMDLINE(2) - Write to Command Line
                  BOTH(3) - Wrte to File and Command Line
        '''
        thatday = time.strftime("%04Y%02m%02d.log", time.localtime())
        self.createFolder(self.mainlogpath)
        if option == LOGGING:
            file = open(self.mainlogpath+thatday, 'a+')
            file.write(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()) + ": " + event + "\n")
            file.close()
        elif option == CMDLINE:
            print(event)
        elif option == BOTH:
            file = open(self.mainlogpath+thatday, 'a+')
            file.write(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()) + ": " + event + "\n")
            file.close()
            print(event)
            

