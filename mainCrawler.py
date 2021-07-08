import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys                     #send_key에 필요
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait             #웹드라이버 딜레이
from selenium.webdriver.support import expected_conditions as EC    #예외처리
from selenium.common.exceptions import TimeoutException             

def NewSleep(self, driver, _second): #sleep을 0.5초 간격으로 검사, 중간에 스레드가 정지되는걸 체크하기 위함
    currtime = 0
    while currtime <= _second:
        if self.isRun == True:
            time.sleep(0.5)
            currtime += 0.5
        else:
            self.signal_AddLogMessage.emit("스레드가 실행 도중 종료되었습니다!")
            driver.quit()
            exit()

def Shutdown(_time):
    os.system("shutdown -s -t " + str(_time))

def CheckIframe(driver):    #디버그 전용
    iframes = driver.find_elements_by_tag_name('iframe')
    print('현재 페이지에 iframe은 %d개가 있습니다.' % len(iframes))

    for i, iframe in enumerate(iframes):
	    try:
	    	print('%d번째 iframe 입니다.' % i)

	    	# i 번째 iframe으로 변경합니다.
	    	driver.switch_to_frame(iframes[i])

	    	# 변경한 iframe 안의 소스를 확인합니다.
	    	print(driver.page_source)

	    	# 원래 frame으로 돌아옵니다.
	    	driver.switch_to_default_content()
	    except:
	    	# exception이 발생했다면 원래 frame으로 돌아옵니다.
	    	driver.switch_to_default_content()

	    	# 몇 번째 frame에서 에러가 났었는지 확인합니다.
	    	print('pass by except : iframes[%d]' % i)

	    	# 다음 for문으로 넘어갑니다.
	    	pass


def WaitForClass_CanBeClicked(driver, delaySec, class_name):
    wait = WebDriverWait(driver, delaySec)
    element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))

def WaitForClass_Visible(driver, delaySec, class_name):
    wait = WebDriverWait(driver, delaySec)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))

def WaitForTag_Visible(driver, delaySec, tag_name):
    wait = WebDriverWait(driver, delaySec)
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))


def Login(self, driver, id, password):
    NewSleep(self, driver, 1)
    try:
        driver.get('https://myclass.ssu.ac.kr/login.php')

        WaitForClass_CanBeClicked(driver, 10, 'loginform')
        # (유세인트 업데이트 이후 버튼 추가)
        driver.find_element_by_xpath('//*[@id="region-main"]/div/div/div/div[3]/div[1]/div[1]/div[2]/div/button').click()
        #ID, PW 필드 채우기
        driver.find_element_by_xpath('//*[@id="input-username"]').send_keys(id)
        driver.find_element_by_xpath('//*[@id="input-password"]').send_keys(password)

        #로그인 버튼 클릭
        driver.find_element_by_xpath('//*[@id="region-main"]/div/div/div/div[3]/div[1]/div[2]/form/div[2]/input').click()

        self.signal_AddLogMessage.emit("스마트캠퍼스에 로그인합니다..")
    except:
        self.signal_AddLogMessage.emit("웹페이지 로그인 실패, 서버에 문제가 발생했습니다")
        return

def OpenLecture(self, driver, link):
    driver.get(link)

    #동영상 재생버튼 클릭을 위해서 iframe 안에 있는 요소를 확인해주어야 함, 확인하는 함수는 CheckIframe
    #https://dejavuqa.tistory.com/198 참고
    WaitForTag_Visible(driver, 10, 'iframe')
    iframes = driver.find_elements_by_tag_name('iframe')
    driver.switch_to_frame(iframes[0])
    NewSleep(self, driver, 3)
    WaitForClass_CanBeClicked(driver, 10, 'ViewerFrm')
    driver.find_element_by_class_name('ViewerFrm').click() #재생버튼 클릭
    NewSleep(self, driver, 3)
    driver.switch_to_default_content()


    # 이어서 시청 팝업창 처리
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = driver.switch_to.alert
        alert.accept()
        self.signal_AddLogMessage.emit("시청기록이 있어 이어서 재생합니다. ")
        self.signal_AddLogMessage.emit("*재생은 전체 영상시간만큼 진행됩니다. 영상이 끝나고도 한동안 다음으로 넘어가지 않을 수 있습니다")
    except TimeoutException:
        self.signal_AddLogMessage.emit("시청기록이 없어 처음부터 재생합니다. ")

    self.signal_AddLogMessage.emit("강의를 시작합니다")
    lectureName = driver.find_element_by_xpath('//*[@id="vod_header"]/h1').text
    self.signal_AddLogMessage.emit("강의 이름 : " + str(lectureName))
    self.signal_SetLectureName.emit(str(lectureName))

def CloseLecture(self, driver):
    self.signal_AddLogMessage.emit('강의를 종료합니다')
        
    driver.execute_script("window.open('');")

    window_to_close = driver.window_handles[0]
    window_to_open = driver.window_handles[1]

    driver.switch_to.window(window_name=window_to_close)
    driver.close()
    driver.switch_to.window(window_name=window_to_open)

def GetLecturePlaytime(self, driver):
    NewSleep(self, driver, 5)
    #time.sleep(5)
    playtime = driver.find_element_by_class_name('playtime').text
    self.signal_AddLogMessage.emit("현재 강의의 출석인정 수강시간 : " + str(playtime))
    
    hour = 0
    minute = 0
    second = 0

    splitTime = playtime.split(':')
    count = playtime.count(':')

    if count == 2:  #1시간 이상 강의
        hour = int(splitTime[0])
        minute = int(splitTime[1])
        second = int(splitTime[2])
    elif count == 1:    #1시간 미만 강의
        minute = int(splitTime[0])
        second = int(splitTime[1])
    #print(count, hour, minute, second)


    totalSecond = hour * 3600 + minute * 60 + second
    self.signal_AddLogMessage.emit("초로 환산 : " + str(totalSecond) + "초")

    return totalSecond

def DelayBySparetime(self, driver, playtime):
    print(self.spareSecond, self.spareMinute, self.sparePercent)
    if self.spareSecond != 0 or self.spareMinute != 0: #강의 끝난 후 여유시간동안 대기
        self.signal_AddLogMessage.emit('여유시간인 %d분 %d초만큼 더 재생합니다' %(self.spareMinute, self.spareSecond))
        NewSleep(self, driver, self.spareSecond + self.spareMinute*60)

    if self.sparePercent!=0:
        delaySec = playtime*(self.sparePercent/100)
        self.signal_AddLogMessage.emit('출석인정 요구시간의 %d퍼센트만큼 더 재생합니다.' %self.sparePercent)
        self.signal_AddLogMessage.emit('%d초의 %d퍼센트인 %d초 만큼 더 재생합니다.' %(playtime, self.sparePercent, delaySec))
        NewSleep(self, driver, delaySec)


def mainFunc(self):
    #Initialize
    links = self.links
    user_id = self.id
    user_pw = self.pw

    # =====드라이버 및 옵션 생성=====
    options = webdriver.ChromeOptions()

    # 필요없고 해결방법도 없는 에러로그들 제거 옵션 추가
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # 창 숨기는 옵션 추가
    if self.chromeOption_Hide:
        options.add_argument("headless")
        self.signal_AddLogMessage.emit("크롬 창을 숨긴 채 진행합니다...")

    # 음소거 옵션 추가
    if self.chromeOption_Mute:
        options.add_argument("--mute-audio")
        self.signal_AddLogMessage.emit("크롬 창을 음소거 상태로 진행합니다...")

    # 드라이버 로드
    try:
        driver = webdriver.Chrome('.\chromedriver\chromedriver.exe', options=options)
    except:
        self.signal_AddLogMessage.emit("! 크롬 드라이버 로드 실패. 최신버전의 크롬이 설치되어 있는지, chromedriver.exe가 폴더 내에 있는지 확인해주세요.")
        return;
    
    # =====로그인=====
    try:
        Login(self, driver, user_id, user_pw)
        #ID, 비밀번호는 사용 직후 초기화
        user_id = None
        user_pw = None
    except:
        self.signal_AddLogMessage.emit("! 로그인에 실패하였습니다")
        self.sinal_StopFunc.emit()
        return

    # =====강의 링크 로드=====
    if not links:
        self.signal_AddLogMessage.emit("! 강의 링크가 없습니다. 강의 영상 상단의 링크를 복사해주세요.")
        self.sinal_StopFunc.emit()
    else:
        lectureLinks = links
        try:
            for link in links:
                OpenLecture(self, driver, link)                     #강의 재생시작
                playtime = GetLecturePlaytime(self, driver)         #강의 시간
                NewSleep(self, driver, playtime)                    #강의 끝까지 대기
                DelayBySparetime(self, driver, playtime)            #최소 수강시간 시청 후에 더 재생 (옵션)
                CloseLecture(self, driver)                          #강의 종료
            self.signal_AddLogMessage.emit("강의를 모두 재생했습니다!")
            self.signal_SetLectureName.emit("실행중인 강의 없음 (모두 재생함)")
            if self.powerOffOption:
                Shutdown(300)   #5분 뒤 컴퓨터 자동종료
                self.signal_AddLogMessage.emit("5분 뒤 컴퓨터가 종료됩니다")
        except:
            self.signal_AddLogMessage.emit("! 강의 로드에 실패했습니다. 로그인 정보와 강의 링크를 확인해주세요")
            self.sinal_StopFunc.emit()
    driver.quit()        