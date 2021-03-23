import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from mainCrawler import *

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType('LMS.ui')[0]

class PlayThread(QThread, QObject): #쓰레딩
    # 시그널 정의
    signal_AddLogMessage = pyqtSignal(str)
    signal_SetLectureName = pyqtSignal(str)
    sinal_StopFunc = pyqtSignal()

    def __init__(self, parent):
        super().__init__()

        self.main = parent

        self.isRun = False
        self.links = None
        self.id = None
        self.pw = None
        self.chromeOption_Hide = False
        self.chromeOption_Mute = False
        self.powerOffOption = False
        self.spareSecond = 0
        self.spareMinute = 0
        self.sparePercent = 0

    def InitLinkData(self, new_links):          # 강의 링크 정보 저장
        self.links = new_links
    
    def InitUserData(self, user_id, user_pw):   # 유저 정보 저장
        self.id = user_id
        self.pw = user_pw

    def InitOption(self, optionName, option):         # 크롬창 숨기기 옵션 저장
        if optionName == 'Hide':
            self.chromeOption_Hide = option
        if optionName == 'Mute':
            self.chromeOption_Mute = option
        if optionName == 'PowerOff':
            self.powerOffOption = option

    def run(self):
        mainFunc(self)

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()

        # 스레드 선언 및 시그널 연결
        self.th = PlayThread(self)
        self.th.signal_AddLogMessage.connect(self.AddLogMessage)
        self.th.signal_SetLectureName.connect(self.SetLectureName)
        self.th.sinal_StopFunc.connect(self.StopFunc)

        # UI 커넥트
        self.setupUi(self)
        self.Button_Start.clicked.connect(self.StartFunc)
        self.Button_Stop.clicked.connect(self.StopFunc)
        self.Button_Login.clicked.connect(self.LoginFunc)
        self.Button_clearLog.clicked.connect(self.ClearLog)
        self.checkbox_toggleChromeToHide.stateChanged.connect(self.ToggleChromeToHide)
        self.checkbox_toggleChromeToMute.stateChanged.connect(self.ToggleChromeToMute)
        self.checkbox_togglePowerOff.stateChanged.connect(self.TogglePowerOff)
        self.spinBox_spareMinute.valueChanged.connect(self.SetSpareMinute)
        self.spinBox_spareSecond.valueChanged.connect(self.SetSpareSecond)
        self.spinBox_sparePercent.valueChanged.connect(self.SetSparePercent)


    def StartFunc(self):
        links = []
        links.append(self.link0.text())
        links.append(self.link1.text())
        links.append(self.link2.text())
        links.append(self.link3.text())
        links.append(self.link4.text())
        links.append(self.link5.text())
        links.append(self.link6.text())
        links.append(self.link7.text())
        links.append(self.link8.text())
        links.append(self.link9.text())
        links.append(self.link10.text())

        links = list(filter(None, links)) #공백인 리스트 제거
        self.th.InitLinkData(links)       #쓰레드 멤버 변수에 추가
        
        for index, link in enumerate(links):
            self.AddLogMessage(str(index) + '번째 강의 추가 : ' + link)
        
        if not self.th.isRun:
            self.th.isRun = True
            self.th.start()
            self.Button_Start.setDisabled(True)
            self.group_option.setDisabled(True)
            self.AddLogMessage("프로그램을 시작합니다..")


    def StopFunc(self):
        if self.th.isRun:
            self.th.isRun = False
            self.Button_Start.setDisabled(False)
            self.group_option.setDisabled(False)
            self.AddLogMessage("프로그램을 종료합니다..")

    def LoginFunc(self):
        _id = self.input_ID.text()
        _pw = self.input_PW.text()

        if not _id or not _pw:
            self.AddLogMessage('로그인 정보가 비어있습니다!')
        else:
            self.AddLogMessage('로그인 정보가 성공적으로 입력되었습니다!')
            self.th.InitUserData(_id, _pw)  #쓰레드 멤버 변수에 추가
            self.Button_Start.setDisabled(False)
            self.Button_Stop.setDisabled(False)

    def ToggleChromeToHide(self):
        flag = bool(self.checkbox_toggleChromeToHide.checkState())
        self.th.InitOption('Hide', flag)
        if flag:
            self.AddLogMessage('크롬 창을 숨긴채 실행합니다.')
        else:
            self.AddLogMessage('크롬 창을 보이게 실행합니다.')

    def ToggleChromeToMute(self):
        flag = bool(self.checkbox_toggleChromeToMute.checkState())
        self.th.InitOption('Mute', flag)
        if flag:
            self.AddLogMessage('크롬 창을 음소거 상태로 실행합니다')
        else:
            self.AddLogMessage('크롬 창을 음소거 상태로 실행하지 않습니다')

    def TogglePowerOff(self):
        flag = bool(self.checkbox_togglePowerOff.checkState())
        self.th.InitOption('PowerOff', flag)
        if flag:
            self.AddLogMessage('마지막에 자동으로 컴퓨터를 종료합니다')
        else:
            self.AddLogMessage('마지막에 자동으로 컴퓨터를 종료하지 않습니다')

    def SetSpareMinute(self, str):
        self.th.spareMinute = int(self.spinBox_spareMinute.value())

    def SetSpareSecond(self, str):
        self.th.spareSecond = int(self.spinBox_spareSecond.value())

    def SetSparePercent(self, str):
        self.th.sparePercent = int(self.spinBox_sparePercent.value())

    def SetLectureName(self, string):
        self.textBox_currentLecture.setPlainText(string)

    def AddLogMessage(self, string):
        self.textbox_Log.append(string)

    def ClearLog(self):
        self.textbox_Log.clear()
        self.AddLogMessage('로그 청소 완료!')


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()