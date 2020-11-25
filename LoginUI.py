# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Login.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!
import json

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(401, 298)
        Dialog.setStyleSheet("#Dialog{background-color: gainsboro;\n"
                             "border-image: url(login.jpg);}")

        self.form = Dialog
        self.horizontalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(140, 240, 111, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Login_button = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.Login_button.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(16)
        self.Login_button.setFont(font)
        self.Login_button.setStyleSheet(
            "QPushButton { background-color: rgb(125, 127, 255); border-radius: 3px; color: rgb(255, 255, 255); } QPushButton:hover { background-color: rgb(255, 11, 84); }")
        self.Login_button.setObjectName("Login_button")
        self.horizontalLayout.addWidget(self.Login_button)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(170, 70, 211, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.server_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.server_edit.setMinimumSize(QtCore.QSize(0, 38))
        self.server_edit.setMaximumSize(QtCore.QSize(16777215, 38))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.server_edit.setFont(font)
        self.server_edit.setText("")
        self.server_edit.setDragEnabled(False)
        self.server_edit.setReadOnly(False)
        self.server_edit.setClearButtonEnabled(True)
        self.server_edit.setObjectName("UserID_edit")
        self.verticalLayout.addWidget(self.server_edit)
        self.username_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.username_edit.setMinimumSize(QtCore.QSize(0, 38))
        self.username_edit.setMaximumSize(QtCore.QSize(16777215, 38))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.username_edit.setFont(font)
        self.username_edit.setText("")
        self.username_edit.setObjectName("Password_edit")
        self.verticalLayout.addWidget(self.username_edit)
        self.Password_edit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.Password_edit.setMinimumSize(QtCore.QSize(0, 38))
        self.Password_edit.setMaximumSize(QtCore.QSize(16777215, 38))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.Password_edit.setFont(font)
        self.Password_edit.setText("")
        self.Password_edit.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.Password_edit.setObjectName("Password_edit_2")
        self.verticalLayout.addWidget(self.Password_edit)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(20, 70, 167, 151))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(20)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.server_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.server_label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.server_label.setFont(font)
        self.server_label.setTextFormat(QtCore.Qt.AutoText)
        self.server_label.setAlignment(QtCore.Qt.AlignCenter)
        self.server_label.setObjectName("UserID_label")
        self.verticalLayout_3.addWidget(self.server_label)
        self.user_name = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.user_name.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        self.user_name.setFont(font)
        self.user_name.setStyleSheet("")
        self.user_name.setAlignment(QtCore.Qt.AlignCenter)
        self.user_name.setObjectName("Password_label")
        self.verticalLayout_3.addWidget(self.user_name)
        self.Password_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.Password_label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.Password_label.setFont(font)
        self.Password_label.setTextFormat(QtCore.Qt.AutoText)
        self.Password_label.setAlignment(QtCore.Qt.AlignCenter)
        self.Password_label.setObjectName("UserID_label_2")
        self.verticalLayout_3.addWidget(self.Password_label)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(90, 10, 211, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "连接到服务器"))
        self.servername = ""
        self.username = ""
        self.password = ""
        self.Login_button.setText(_translate("Dialog", "登录"))
        self.server_label.setText(_translate("Dialog", "服务器名称："))
        self.user_name.setText(_translate("Dialog", "登录名："))
        self.Password_label.setText(_translate("Dialog", "密码："))
        self.label.setText(_translate("Dialog", "连接到服务器"))

        try:
            with open('login.txt', "r+") as f:
                read_data = f.read()
                if read_data:
                    list = json.loads(read_data)
                    self.server_edit.setText(list[0])
                    self.username_edit.setText(list[1])
                    self.Password_edit.setText(list[2])
        except:
            print("登录文件出错！！")

        self.Login_button.clicked.connect(self.login)

    def login(self):
        self.servername = self.server_edit.text()
        self.username = self.username_edit.text()
        self.password = self.Password_edit.text()

        list = [self.servername, self.username, self.password]
        with open('login.txt', "r+") as f:
            # read_data = f.read()
            f.seek(0)
            f.truncate()  # 清空文件
            f.write(str(list).replace("'", '"'))

        self.form.close()

    def getdata(self):
        return self.servername, self.username, self.password
