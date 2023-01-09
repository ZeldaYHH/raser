import sys,time
import numpy
from PyQt5 import QtGui, QtCore, uic, QtWidgets

tctEnable = True
if tctEnable:
    import pymotor
    import thread
    import MDO3034Control
    import VitualDevice as vitual_dev

testpass = False


class ControlandCapture:

    def EmumDevice(self):
        pymotor.enum_device()
        print('\nemum complete!\n')
        self.device_name ,self.dev_count, self.friend_name = pymotor.enum_device()
        self.device = numpy.empty(5,dtype=object)
        if self.dev_count == 0:
            print("\nNo finding of device.")
            print("\nUse the vitual device:\n")
            self.device_name = ["testxmotor","testymotor","testzmotor"]
            self.i = 0
            for self.str_device in self.device_name:
                print('str_device:'+self.str_device)
                self.device[self.i] = vitual_dev.VitualDevice(self.device_name[self.i])
                print('device[]' + str(self.device[self.i]))
                #self.testmotor = pymotor.Motor(vitual_dev.VitualDevice(self.str_device).open_name)
                #self.testmotor.move(10)
                self.i = self.i + 1
        else:
            for self.dev_ind in range(0,self.dev_count):
                if 'Axis 1' in repr(self.friend_name[self.dev_ind]): self.device[0] =pymotor.Motor(self.device_name[self.dev_ind])
                if 'Axis 2' in repr(self.friend_name[self.dev_ind]): self.device[1] =pymotor.Motor(self.device_name[self.dev_ind])
                if 'Axis 3' in repr(self.friend_name[self.dev_ind]): self.device[2] =pymotor.Motor(self.device_name[self.dev_ind])

    def SetMotor(self):
        self.setdevice = numpy.empty(3,dtype=object)
        self.setdevice[0] = self.device[0]
        self.setdevice[1] = self.device[1]
        self.setdevice[2] = self.device[2]

    def SpeedMode(self):
        self.SetSpeed(True)

    def SetSpeed(self,default):
        self.steps = numpy.empty(3,dtype=int)
        self.speed = numpy.empty(3,dtype=int)
        if default:
            self.steps = [0,0,0]
            self.speed = [1000,1000,1000]

    def Scan(self):
        x0,y0,z0,dx,dy,dz,Nx,Ny,Nz=0,0,0,1,1,1,0,0,0
        self.scan_thread = thread.ScanThread(self.setdevice)
        self.scan_thread.flag = True
        self.scan_thread.pos_o = [x0,y0,z0]
        self.scan_thread.dp = [dx,dy,dz]
        self.scan_thread.Np = [Nx,Ny,Nz]
        self.scan_thread.scan()

    def ScanContinue(self):
        self.scan_thread.continue_flag = True

    def SaveData(self):
        '''if self.ui.Frequency_mode.isChecked() == True:
            self.CaptureMode(False)
        if self.ui.step_mode.isChecked() == True:
            self.Scan()
            self.scan_thread.CaptureSignal.connect(self.StepCapture)'''
        self.StepCapture

    def StepCapture(self):
        print("capture\n")
        self.scan_thread.continue_flag = False             #let scan thread wait
        #self.SignalCapture.emit()
        self.CaptureMode(True)

    def CaptureMode(self,mode):
        self.capture_thread = thread.DataCapture()
        self.readythread = thread.ReadyThread()
        self.capture_thread.flag = True
        self.capture_thread.stepmode_flag = mode
        self.capture_thread.resource = self.ui.Interface.currentText()
        self.capture_thread.folder = self.ui.FolderText.text()
        self.capture_thread.device = self.setdevice
        self.capture_thread.frequency = self.ui.Frequency.value()
        self.capture_thread.point_num = self.ui.Points.value()
        self.capture_thread.ymult = float(str(self.readythread.ymult))
        self.capture_thread.yzero = float(str(self.readythread.yzero))
        self.capture_thread.yoff = float(str(self.readythread.yoff))
        self.capture_thread.xincr = float(str(self.readythread.xincr))
        self.capture_thread.xzero = float(str(self.readythread.xzero))
        self.capture_thread.scope = self.scope
        self.capture_thread.info = self.oscilloscope_info
        self.capture_thread.start()
        self.capture_thread.scan_signal.connect(self.SignalScanContinue.emit)  #scan continue
        #self.capture_thread.wait()

    def Ready(self):
        self.readythread = thread.ReadyThread()
        self.readythread.resource_name = self.ui.Interface.currentText()
        self.readythread.channel = self.ui.Channel.value()
        self.readythread.point_number = self.ui.Points.value()
        self.readythread.start()
        self.readythread.sinOut.connect(self.DisplayReadyInfo)

    def DisplayReadyInfo(self,dis_message):
        if dis_message == "offset":
            self.ui.InfoText.append(self.readythread.message)
            self.ui.ymult.setText(str(self.readythread.ymult))
            self.ui.yzero.setText(str(self.readythread.yzero))
            self.ui.yoff.setText(str(self.readythread.yoff))
            self.ui.xincr.setText(str(self.readythread.xincr))
            self.ui.xzero.setText(str(self.readythread.xzero))
        elif dis_message == "open":
            self.scope = self.readythread.scope
            self.oscilloscope_info = self.readythread.message
            self.ui.InfoText.append(self.readythread.message)
        else:
            self.ui.InfoText.append(self.readythread.message)