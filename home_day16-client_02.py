
from PyQt5 import QtWidgets, QtCore, uic, Qt
import sys
from PyQt5.QtWidgets import *
import webbrowser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication
from datetime import datetime
from PyQt5.QtGui import QPixmap
import threading
from plyer import notification
import time
import csv
import PyQt5
from socket import *
import ssl
from PyQt5 import QtGui
from PyQt5.QtCore import QRect
from PyQt5 import QtCore


home = uic.loadUiType("timetable04.ui")[0]
isThrd = False
delete = 0
name = ''
start = 0
yes = False
Datas = []

class Home(QMainWindow, home):
    url = ""
    timetable_color_list_index = -1
    def __init__(self):
        super().__init__()

        self.setWindowOpacity(0.8)
        self.setupUi(self)


        self.school_homepage.clicked.connect(self.school_img)
        self.school_homepage.setIcon(QtGui.QIcon('khu.png'))
        self.school_homepage.setIconSize(QtCore.QSize(55, 40))


        self.setting_btn.setIcon(QtGui.QIcon('setting.png'))
        self.setting_btn.setIconSize(QtCore.QSize(38, 38))

        self.pushButton_3.setIcon(QtGui.QIcon('plus.png'))
        self.pushButton_3.setIconSize(QtCore.QSize(38, 38))

        self.pushButton.setIcon(QtGui.QIcon('exit.png'))
        self.pushButton.setIconSize(QtCore.QSize(25, 36))

        self.setFixedSize(519, 768)#크기 고정
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)#상단바 없애기

        self.pushButton_3.clicked.connect(self.addSubject)


        menu_list = ['알림 설정', '시간표 공유받기']
        menu = PyQt5.QtWidgets.QMenu()

        get_share = menu.addAction("시간표 공유받기")
        get_share.triggered.connect(self.open_get_share_window)

        alarm_setting = menu.addAction("알림 설정")
        alarm_setting.triggered.connect(self.open_setting_window)


        self.setting_btn.setMenu(menu)

        cur_sec = int(datetime.now().second)
        self.calldata()
        self.st = 5
        self.yesorno = True
        t = threading.Timer(60-cur_sec, self.timealarm)
        t.start()

        self.show()


    # 마우스로 이동
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)


    # X 버튼
    def exit(self):
        isThrd = False
        sys.exit()

    #우측 상단의 설정 버튼 연결
    def open_setting_window(self):
        mysignal = settting_window(self)
        mysignal.signal2.connect(self.alarmload)

    @pyqtSlot(int, bool)
    def alarmload(self, start, yes):
        self.st = start
        self.yesorno = yes

    #학교 링크타는 버튼
    def school_img(self):
        webbrowser.open("https://e-campus.khu.ac.kr/index.php")

    #설정 버튼 클릯시 메뉴로 만들기
    def open_get_share_window(self):
        hsignal = get_share_sub(self)
        hsignal.signal_host.connect(self.get_host)

    #통신
    @pyqtSlot(str)
    def get_host(self, host):  # 공유받기 창에서 OK를 클릭하였을 때

        port = 31405

        clientSock = socket(AF_INET, SOCK_STREAM)
        clientSock.connect(('39.124.123.40', port))

        print('접속 완료')
        self.getlist = []
        for i in range(2):
            recvData = clientSock.recv(1024)
            self.getlist.append(recvData.decode('utf-8'))

        self.rUrl = self.getlist.pop()
        self.getlist2 = list(str(self.getlist[0]))
        self.rWeekday = int(self.getlist2.pop())
        self.rStartTimeTable = int("".join(self.getlist2))

        print("rUrl: ", self.rUrl)
        print("rWeekday: ", self.rWeekday)
        print("rStartTimeTable: ", self.rStartTimeTable)

        f = open('file.csv', 'r')  # 자신의 줌링크도 바꿔주는 코드
        rdr = csv.reader(f)
        for line in rdr:
            if (int(line[3]) == self.rWeekday and int(line[2]) == self.rStartTimeTable):  #line[3] = 요일 , line[2] = 시작시간
                name = str(line[0])
                break;
        f.close()

        f = open('file.csv', 'r')  # 자신의 줌링크도 바꿔주는 코드
        rdr = csv.reader(f)
        lines = []
        for line in rdr:
            if (str(line[0]) == name):
                line[1] = self.rUrl
                lines.append(line)
            else:
                lines.append(line)

        f = open('file.csv', 'w', newline='')
        wr = csv.writer(f)
        wr.writerows(lines)
        f.close()
        show_text = '호스트에 의해 ' + name + '의 zoom주소가 변경되었습니다'
        QMessageBox.question(self, 'Message', show_text, QMessageBox.Yes, QMessageBox.NoButton)



    #수업 알림

    def timealarm(self):
        Datas.sort()
        #print(Datas)
        weekday = datetime.today().weekday()
        current_time = datetime.now()
        cur_hour = int(current_time.hour)
        cur_min = int(current_time.minute)
        #classTime_Hour = 20          #수업 예정 시간(시간)
        #classTime_minute = 27       #수업 예정 시간(분)
        n = self.st        #수업 예정 시간 n분 전

        if (isThrd):
            thread = threading.Timer(60, self.timealarm)
            thread.start()
            #print("스레드")
        for lst in Datas:
            if (lst[0] == weekday):
                if (lst[1] == cur_hour) and (lst[2] == (cur_min + n)):
                    #print("알람")
                    notification.notify('알림', '{} 수업 시간 {}분 전입니다.'.format(lst[3], n), app_icon=None, app_name='알림')
                else:
                    if (lst[1] == cur_hour + (n // 60) + 1) and (lst[2] == (60 - cur_min - n % 60)):
                        print("알람2")
                        notification.notify('알림', '{} 수업 시간 {}분 전입니다.'.format(lst[3], n), app_icon=None, app_name='알림')

    def calldata(self):
        f = open("file.csv","a")
        f.close()

        f = open("file.csv", "r")
        rdr = csv.reader(f)

        global Datas
        lines = []
        c = 0
        for line in rdr:

            sub_name = ""
            idx = 0
            for t in line[0]:
                sub_name += t
                idx += 1
                if(idx%3 == 0 and idx != len(line[0])):
                    sub_name += "\n"

            sublist = [int(line[3])-1,int(line[5]),int(line[6]), line[0]]     #시간알림할때 쓸정보
            Datas.append(sublist)
            lines.append(line)

            self.bt1 = QtWidgets.QPushButton(str(line[0]), self.centralwidget)
            self.bt1.setMaximumHeight(10000)  # 10000 -> 1000000
            self.bt1.setMaximumWidth(74)
            self.bt1.setText(sub_name)
            self.gridLayout.addWidget(self.bt1, int(line[2]), int(line[3]),
                                      float(line[4]), 1)
            self.bt1.setStyleSheet("background-color: " + line[9]) #8열에 저장된 색정보 -> 스타일시트로 적용
            self.bt = self.bt1
            global name
            name = line[0]
            self.bt.installEventFilter(self)

        f.close()

    def addSubject(self):
        self.w = Screen(self)
        self.w.command.connect(self.btn_clicked1)

    #  self.buttonbox.accepted.connet(self.btn_clicked)

    def eventFilter(self, QObject, event):
        self.debt = QObject
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                mysignal = edit_sub(self) #우클릭해서 나온 창(삭제하시겠습니까?)에서 OK를 클릭했다는 시그널
                mysignal.signal1.connect(self.signal1_emitted)
                mysignal.signal3.connect(self.signal3_emitted)

            elif event.button() == Qt.LeftButton:
                f = open('file.csv', 'r')
                rdr = csv.reader(f)
                lines = []
                cnt = 0
                for line in rdr:
                    if (str(line[8]) == self.debt.text()): #이름으로 url 찾아서 연결해주기
                        self.url = line[1]
                        break;
                webbrowser.open(self.url)  # 여기 괄호 안에 zoom에 해당하는 주소 넘겨주면 됨x
        return False

    @pyqtSlot(str)
    def signal3_emitted(self, link):  # 우클릭해서 나온 창(공유하시겠습니까?)에서 OK를 클릭할 때 실행되는 함수 -> 공유하기
        self.share_list = []  # 공유할 정보들을 담은 리스트
        self.share_list.append(link)

        f = open('file.csv', 'r')  # 자신의 줌링크도 바꿔주는 코드
        rdr = csv.reader(f)
        lines = []
        cnt = 0
        for line in rdr:
            if (str(line[8]) == self.debt.text()):
                line[1] = link
                lines.append(line)
                date_x = int(line[2]) # 요일
                date_y = int(line[3]) # 시간
            else:
                cnt += 1
                lines.append(line)
        self.share_list.append(date_x)  # 공유할 리스트에 시작 행, 열 정보 추가 -> [링크, 행, 열]
        self.share_list.append(date_y)

        print(self.share_list)

        f = open('file.csv', 'w', newline='')
        wr = csv.writer(f)
        wr.writerows(lines)
        f.close()


    @pyqtSlot() # 우클릭해서 나온 창(삭제하시겠습니까?)에서 OK를 클릭할 때 실행되는 함수 -> 삭제하기
    def signal1_emitted(self):

        f = open('file.csv', 'r')
        rdr = csv.reader(f)
        lines = []
        cnt = 0
        for line in rdr:
            if (str(line[8]) != self.debt.text()):
                lines.append(line)
            else:
                cnt += 1

        f = open('file.csv', 'w', newline='')
        wr = csv.writer(f)
        wr.writerows(lines)
        f.close()

        self.debt.deleteLater()

    @QtCore.pyqtSlot(str, int, int, bool, bool, bool, bool, bool, int, str, int , int,str)
    def btn_clicked1(self, txt, start_on_table, total_minute, M, T, W, Th, F, cnt, zoom, start_hour, start_minute,color):
        self.buttonList = []
        self.fileList = []

        #색정보 list로 저장 / 새 버튼 만들어지면 index +1로 다음 색으로 지정
        self.timetable_color_list = ['#ff608f', '#fbc02d', '#9cff57', '#64d8cb', '#75a7ff', '#8187ff', '#b085f5', '#a98274', '#8eacbb']
        #self.timetable_color_list_index += 1



        print(color)
        print(self.timetable_color_list)
        if color in self.timetable_color_list:
            self.timetable_color_list_index += 1
            lattest_color = ''
            f = open('file.csv', 'r')
            rdr = csv.reader(f)
            for line in rdr:
                lattest_color = line[7]
            f.close()
            for clr in self.timetable_color_list:
                if clr == lattest_color:
                    self.timetable_color_list_index = self.timetable_color_list.index(clr) + 1
            if self.timetable_color_list_index >= 9:
                self.timetable_color_list_index = 0
            self.color = self.timetable_color_list[self.timetable_color_list_index]

            color = self.timetable_color_list[self.timetable_color_list_index]



        for i in range(cnt):
            self.bt1 = QtWidgets.QPushButton(txt,self.centralwidget)
            self.bt1.setMaximumHeight(10000)  # 10000 -> 1000000
            self.bt1.setMaximumWidth(self.label_232.width())

            sub_name = ""
            idx = 0
            for t in txt:
                sub_name += t
                idx += 1
                if(idx%3 == 0 and idx != len(txt)):
                    sub_name += "\n"

            self.bt1.setText(sub_name)
            a = int(total_minute) / 5

            self.url = zoom
            #우클릭 좌클릭 나누기 위해 bt 변수에 self.bt1으로 수정
            bt = self.bt1
            bt.installEventFilter(self)
            # 배경색 설정 (새로 만들 때)

            bt.setStyleSheet('background-color: {}'.format(color))



            self.buttonList.append(bt)

        # addWidget(행 열 세로칸수 가로칸수)
        Cnt = -1
        if M:
            x = 1
            Cnt += 1
            self.gridLayout.addWidget(self.buttonList[Cnt], start_on_table, x, a, 1)
            self.fileList.extend([txt,zoom,start_on_table,x,a,start_hour, start_minute])

            f = open('file.csv', 'a', newline='')
            makewrite = csv.writer(f)
            makewrite.writerow([txt,zoom,start_on_table,x,a, start_hour, start_minute,self.color ,self.buttonList[Cnt].text(),color])
            f.close()

        if T:
            x = 2
            Cnt += 1
            self.gridLayout.addWidget(self.buttonList[Cnt], start_on_table, x, a, 1)
            self.fileList.extend([txt,zoom,start_on_table,x, a, start_hour, start_minute])
            f = open('file.csv', 'a', newline='')
            makewrite = csv.writer(f)
            makewrite.writerow([txt,zoom,start_on_table,x,a, start_hour, start_minute,self.color,self.buttonList[Cnt].text(),color])
            f.close()

        if W:
            x = 3
            Cnt += 1
            self.gridLayout.addWidget(self.buttonList[Cnt], start_on_table, x, a, 1)
            self.fileList.extend([txt,zoom,start_on_table,x, a])
            f = open('file.csv', 'a', newline='')
            makewrite = csv.writer(f)
            makewrite.writerow([txt,zoom,start_on_table,x,a, start_hour, start_minute,self.color,self.buttonList[Cnt].text(),color])
            f.close()

        if Th:
            x = 4
            Cnt += 1
            self.gridLayout.addWidget(self.buttonList[Cnt], start_on_table, x, a, 1)
            self.fileList.extend([txt,zoom,start_on_table,x, a])
            f = open('file.csv', 'a', newline='')
            makewrite = csv.writer(f)
            makewrite.writerow([txt,zoom,start_on_table,x,a, start_hour, start_minute,self.color,self.buttonList[Cnt].text(),color])
            f.close()

        if F:
            x = 5
            Cnt += 1
            self.gridLayout.addWidget(self.buttonList[Cnt], start_on_table, x, a, 1)
            self.fileList.extend([txt,zoom,start_on_table,x, a])
            f = open('file.csv', 'a', newline='')
            makewrite = csv.writer(f)
            makewrite.writerow([txt,zoom,start_on_table,x,a, start_hour, start_minute,self.color,self.buttonList[Cnt].text(),color])
            f.close()

#설정 메뉴에 새 ui창을 띄우기 위함 클래스
class get_share_sub(QDialog):
    signal_host = pyqtSignal(str)
    def __init__(self, parent):
        super(get_share_sub, self).__init__(parent)
        new_w = 'get_share_subject.ui'
        uic.loadUi(new_w, self)
        self.buttonBox.accepted.connect(self.get_share_host)
        self.buttonBox.rejected.connect(self.close)
        self.show()

    def get_share_host(self):
        host = str(self.lineEdit.text())
        self.signal_host.emit(host)
        self.close()


class edit_sub(QDialog, QtCore.QObject):
    signal1 = pyqtSignal()
    signal3 = pyqtSignal(str)
    def __init__(self, parent):
        super(edit_sub, self).__init__(parent)
        new_w = 'pop_up.ui'
        uic.loadUi(new_w, self)
        self.buttonBox_2.accepted.connect(self.do_delete)
        self.buttonBox_2.rejected.connect(self.close)
        self.share_btn_box.accepted.connect(self.share_link)
        self.share_btn_box.rejected.connect(self.close)
        self.show()

    def do_delete(self):
        self.signal1.emit()
        self.close()

    def share_link(self):
        link = str(self.share_zoom.text())
        self.signal3.emit(link)
        self.close()



class settting_window(QDialog):
    signal2 = pyqtSignal(int, bool)
    def __init__(self, parent):
        super(settting_window, self).__init__(parent)
        new_w = 'alarm.ui'
        uic.loadUi(new_w, self)
        self.buttonBox.accepted.connect(self.get_alarm)
        self.buttonBox.rejected.connect(self.close)
        self.show()

    def get_alarm(self):
        start = int(self.comboBox_2.currentText())
        if self.radioButton.isChecked():
            yes = True
        else:
            yes = False

        self.signal2.emit(start, yes)
        self.close()


class Screen(QDialog):
    command = QtCore.pyqtSignal(str, int, int, bool, bool, bool, bool, bool, int, str, int, int,str)
    def __init__(self, parent):
        super(Screen, self).__init__(parent)
        new_w = 'addTimetable02.ui'
        uic.loadUi(new_w, self)
        self.c = 0
        self.colorButton.clicked.connect(self.get_color)
        self.buttonBox.accepted.connect(self.btn_clicked)
        self.show()

    #        loadUi("addTimetable.ui", self)
    def get_color(self):
        self.c = 1
        color = QColorDialog.getColor()
        sender = self.sender()
        self.getcolor = color.name()

        if sender == self.colorButton and color.isValid():
            self.colorButton.setStyleSheet('background-color: {}'. format(self.getcolor))
        else:
            self.getcolor = color.name
            self.colorButton.setStyleSheet('background-color: {}'. format(self.getcolor))


    @QtCore.pyqtSlot()
    def btn_clicked(self):
        txt = self.lineEdit.text()

        if(self.c == 1):
            color = self.getcolor
        else:
            color = '#ff608f'

        '''
        start_hour: 시작 시간 / start_minute: 시작 분 ... 으로 comboBox에서 받아오기
        comboBox에 이름은 각 변수 이름과 동일, total_minute: 두 시간 사이의 분수
        start_on_table: 시간표의 시작 지점
        '''
        zoom = self.lineEdit_2.text()
        start_hour = int(self.start_hour.currentText())
        start_minute = int(self.start_minute.currentText())
        end_hour = int(self.end_hour.currentText())
        end_minute = int(self.end_minute.currentText())
        total_minute = 0
        start_on_table = int((start_hour - 9) * 12 + (start_minute / 5))

        if (start_hour > end_hour) or ((start_hour == end_hour) and (start_minute > end_minute)):
            print("시작시간 > 끝 시간");
        elif start_hour == end_hour:
            total_minute += (end_minute - start_minute)
        else:
            total_minute = (60 - start_minute) + end_minute
            if start_hour != (end_hour - 1):
                total_minute += (end_hour - start_hour - 1) * 60

        x = 0
        cnt = 0
        M, T, W, Th, F = False, False, False, False, False

        if self.checkBox.isChecked():
            M = True
            cnt += 1
        if self.checkBox_2.isChecked():
            T = True
            cnt += 1
        if self.checkBox_3.isChecked():
            W = True
            cnt += 1
        if self.checkBox_4.isChecked():
            Th = True
            cnt += 1
        if self.checkBox_5.isChecked():
            F = True
            cnt += 1

        self.command.emit(txt, start_on_table, total_minute, M, T, W, Th, F, cnt, zoom, start_hour, start_minute,color)
        self.close()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    myWindow = Home()
    myWindow.show()
    isThrd = True
    if(app.exec_()):
        isThrd = False
        sys.exit()

    #sys.exit(app.exec_())



# main
