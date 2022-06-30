from PyQt5 import QtWidgets, QtGui, QtCore
from Journal import Journal
from random import randint
import datetime as dt
import pathlib
import json
import os
import sys

# Default Settings
settings = {
    "FONT": "Acme",
    "FONT_SIZE_PRIMARY": 52,
    "FONT_SIZE_SECONDARY": 30,
    "COLOR_PRIMARY": "#ffc800",
    "COLOR_SECONDARY": "#ffffff",
    "COLOR_BG_PRIMARY": "#3f3f3f",
    "COLOR_BG_SECONDARY": "#000000",
    "COLOR_BG_BUTTON": "#595959"
}

class JournalsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.mainWindow = None
        self.settingsWindow = None
        self.selectedJName = ""
        self.CreateSettings()
        self.LoadSettings()
        self.InitUI()

    def InitUI(self):
        # Create stacked widget
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setWindowTitle("Journal")
        self.stackedWidget.setGeometry(400, 150, 1024, 720)
        self.stackedWidget.setWindowIcon(QtGui.QIcon("./images/icon.png"))
        self.stackedWidget.addWidget(self)

        # Create layouts
        widget_main = QtWidgets.QWidget()
        vbox_main = QtWidgets.QVBoxLayout()
        hbox_title = QtWidgets.QHBoxLayout()
        hbox_buttons = QtWidgets.QHBoxLayout()

        # Create title 'Journals'
        self.lbl_title = QtWidgets.QLabel("Journals")
        self.lbl_title.setAlignment(QtCore.Qt.AlignCenter)

        # Create settings button
        pbtn_settings = QtWidgets.QPushButton()
        pbtn_settings.setIcon(QtGui.QIcon("./images/settings.png"))
        pbtn_settings.setIconSize(QtCore.QSize(40, 40))
        pbtn_settings.setMinimumSize(60, 60)
        pbtn_settings.setMaximumSize(80, 80)
        pbtn_settings.setCursor(QtCore.Qt.PointingHandCursor)
        pbtn_settings.setShortcut(QtGui.QKeySequence("CTRL+S"))
        pbtn_settings.setToolTip(f"Go to settings ({pbtn_settings.shortcut().toString()})")
        pbtn_settings.clicked.connect(self.OpenSettings)

        # Create list widget and fill journals in it
        self.listWidget = QtWidgets.QListWidget()
        self.UpdateJournalList()
        self.listWidget.setCurrentRow(0)
        self.listWidget.setMinimumSize(450, 200)
        self.listWidget.setFrameShape(QtWidgets.QFrame.Box)
        self.listWidget.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.listWidget.setLineWidth(5)
        self.listWidget.setToolTip(f"Double-click on a journal to open it (Enter)")
        self.listWidget.setCursor(QtCore.Qt.PointingHandCursor)
        self.listWidget.itemDoubleClicked.connect(self.OnDoubleClick)

        # 'New' button
        pbtn_new = QtWidgets.QPushButton("New")
        pbtn_new.setMinimumHeight(60)
        pbtn_new.setCursor(QtCore.Qt.PointingHandCursor)
        pbtn_new.setShortcut(QtGui.QKeySequence("CTRL+N"))
        pbtn_new.setToolTip(f"Create a new journal ({pbtn_new.shortcut().toString()})")
        pbtn_new.clicked.connect(self.ButtonNew)

        # 'Delete' button
        pbtn_delete = QtWidgets.QPushButton("Delete")
        pbtn_delete.setMinimumHeight(60)
        pbtn_delete.setCursor(QtCore.Qt.PointingHandCursor)
        pbtn_delete.setShortcut(QtGui.QKeySequence("DEL"))
        pbtn_delete.setToolTip(f"Permanently delete the selected journal ({pbtn_delete.shortcut().toString()})")
        pbtn_delete.clicked.connect(self.ButtonDelete)

        # hbox_title assignment
        hbox_title.addWidget(self.lbl_title)
        hbox_title.addWidget(pbtn_settings)
        hbox_title.setContentsMargins(60, 0, 0, 0)

        # hbox_buttons assignment
        hbox_buttons.addWidget(pbtn_new)
        hbox_buttons.addStrut(1)
        hbox_buttons.addWidget(pbtn_delete)
        hbox_buttons.setSpacing(20)

        # vbox_main assignment
        vbox_main.addLayout(hbox_title)
        vbox_main.addWidget(self.listWidget)
        vbox_main.addLayout(hbox_buttons)
        vbox_main.setContentsMargins(30, 30, 30, 10)

        # Central widget assignment
        widget_main.setLayout(vbox_main)
        self.setCentralWidget(widget_main)

        self.ApplySettings()
        self.stackedWidget.show()

    def GetJournals(self):
        path = pathlib.Path(r"./Journals")
        jrnPaths = sorted(path.iterdir(), key=os.path.getmtime, reverse=True)
        journals = [(p.name[4:-5], self.PrettyTimeStamp(os.path.getmtime(p)),
                     self.PrettyTimeStamp(os.path.getctime(p))) for p in jrnPaths]
        return journals

    def UpdateJournalList(self):
        self.listWidget.clear()
        journals = self.GetJournals()
        for jrnName, mTime, cTime in journals:
            lWidget = QtWidgets.QListWidgetItem(jrnName.title(), self.listWidget)
            lWidget.setToolTip(f"""Journal: {jrnName.title()}
Last Modified: {mTime:>21}
Created Date: {cTime:>22}""")
            if jrnName == self.selectedJName:
                self.listWidget.setCurrentItem(lWidget)
        if self.listWidget.currentItem() is None:
            self.listWidget.setCurrentRow(0)

    def GetSelectedName(self):
        current = self.listWidget.currentItem()
        if current is not None:
            return current.text().lower()

    def OnDoubleClick(self):
        jName = self.GetSelectedName()
        self.OpenJournal(jName)

    def ButtonNew(self):
        # Create input dialog for journal name, validate file name, then create and open a new journal
        dlg = QtWidgets.QInputDialog(self)
        dlg.setWindowTitle("New Journal")
        dlg.setLabelText("Enter a name:")
        dlg.show()
        dlg_ledit = dlg.findChild(QtWidgets.QLineEdit)
        # A file name can't contain: \/:*?"<>|
        regex = QtCore.QRegExp(r'^[^</*?"\\>:|]+$')
        filename_validator = QtGui.QRegExpValidator(regex, dlg_ledit)
        dlg_ledit.setValidator(filename_validator)
        # Get the file name and create and open the journal
        if dlg.exec_():
            jrnName = dlg_ledit.text().strip()
            if jrnName != "":
                self.OpenJournal(jrnName)
                self.selectedJName = jrnName.lower()
            else:
                msg = QtWidgets.QMessageBox(self)
                msg.setWindowTitle("Invalid Name")
                msg.setText("Journal name can't be whitespace only!")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setIconPixmap(QtGui.QPixmap("./images/warning.png"))
                msg.exec_()

    def ButtonDelete(self):
        jName = self.GetSelectedName()
        if jName is not None:
            path = pathlib.Path(rf"./Journals/jrn_{jName}.json")
            # Create confirmation dialog
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Deleting Journal")
            dlg.setText(f"Journal {jName.title()} will be deleted. Proceed?")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            dlg.setIconPixmap(QtGui.QPixmap("./images/warning.png"))
            dlg.setDefaultButton(QtWidgets.QMessageBox.No)
            answer = dlg.exec_()
            # Delete the journal if the answer is yes
            if answer == QtWidgets.QMessageBox.Yes:
                path.unlink()
                self.UpdateJournalList()

    def MainWindowToJournalslWindow(self):
        # If TextEdit has unsubmitted entry, warn the user to stay
        if self.mainWindow.mode == "edit":
            # If TextEdit has unsaved changes, warn the user to stay
            isUnsubmitted = self.mainWindow.CheckUnsubmittedEdit()
            if isUnsubmitted == QtWidgets.QMessageBox.Yes or isUnsubmitted is None:
                currentWidget = self.stackedWidget.currentWidget()
                self.stackedWidget.removeWidget(currentWidget)
                self.stackedWidget.setCurrentIndex(0)
                self.UpdateJournalList()
                self.mainWindow.draftEditText = self.mainWindow.entriesOfToday
        else:
            isUnsubmitted = self.mainWindow.CheckUnsubmittedEntry()
            if isUnsubmitted == QtWidgets.QMessageBox.Yes or isUnsubmitted is None:
                currentWidget = self.stackedWidget.currentWidget()
                self.stackedWidget.removeWidget(currentWidget)
                self.stackedWidget.setCurrentIndex(0)
                self.UpdateJournalList()
                self.mainWindow.draftText = ""
            else:
                if self.mainWindow.mode == "read":
                    self.mainWindow.ButtonAdd()

    def OpenJournal(self, jrnName):
        self.selectedJName = self.GetSelectedName()
        self.mainWindow = MainWindow(jrnName)
        self.mainWindow.tbtn_toJournalsWindow.clicked.connect(self.MainWindowToJournalslWindow)
        self.stackedWidget.addWidget(self.mainWindow)
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget.closeEvent = self.OnClose
        self.mainWindow.tedit_entry.setFocus()

    def SettingsWindowToJournalsWindow(self):
        currentWidget = self.stackedWidget.currentWidget()
        self.stackedWidget.removeWidget(currentWidget)
        self.stackedWidget.setCurrentIndex(0)
        self.UpdateJournalList()

    def OpenSettings(self):
        self.selectedJName = self.GetSelectedName()
        self.settingsWindow = SettingsWindow()

        self.settingsWindow.tbtn_toJournalsWindow.clicked.connect(self.SettingsWindowToJournalsWindow)
        self.settingsWindow.cmbox_font.currentFontChanged.connect(self.OnFontChange)
        self.settingsWindow.spbox_fontSizePrimary.valueChanged.connect(self.OnFontSizePrimaryChange)
        self.settingsWindow.spbox_fontSizeSecondary.valueChanged.connect(self.OnFontSizeSecondaryChange)
        self.settingsWindow.pbtn_defaultSettings.clicked.connect(self.RestoreDefaultSettings)
        self.settingsWindow.pbtn_colorPrimary.clicked.connect(self.OnColorPrimaryChange)
        self.settingsWindow.pbtn_colorSecondary.clicked.connect(self.OnColorSecondaryChange)
        self.settingsWindow.pbtn_colorBgPrimary.clicked.connect(self.OnColorBgPrimaryChange)
        self.settingsWindow.pbtn_colorBgSecondary.clicked.connect(self.OnColorBgSecondaryChange)
        self.settingsWindow.pbtn_colorBgButton.clicked.connect(self.OnColorBgButtonChange)

        self.stackedWidget.addWidget(self.settingsWindow)
        self.stackedWidget.setCurrentIndex(1)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.OpenJournal(self.GetSelectedName())

    @staticmethod
    def PrettyTimeStamp(timeStamp):
        dateTime = dt.datetime.fromtimestamp(timeStamp)
        return dateTime.strftime('%Y/%m/%d  %H:%M:%S')

    def OnClose(self, event):
        self.SaveSettings()
        if self.mainWindow.mode == "edit":
            # Check unsaved changes
            isUnsaved = self.mainWindow.CheckUnsubmittedEdit()
            if isUnsaved == QtWidgets.QMessageBox.Yes or isUnsaved is None:
                event.accept()
            else:
                event.ignore()
        else:
            # Check unsubmitted entry
            isUnsubmitted = self.mainWindow.CheckUnsubmittedEntry()
            if isUnsubmitted == QtWidgets.QMessageBox.Yes or isUnsubmitted is None:
                event.accept()
            else:
                if self.mainWindow.mode == "read":
                    event.ignore()
                    self.mainWindow.ButtonAdd()
                else:
                    event.ignore()

    def CreateSettings(self):
        path = pathlib.Path("./Settings")
        settingsPath = pathlib.Path("./Settings/settings.json")
        defaultSettingsPath = pathlib.Path("./Settings/defaultSettings.json")
        if path.exists():
            if not settingsPath.exists():
                with open(settingsPath, 'w') as f:
                    json.dump(settings, f)
        else:
            path.mkdir()
            with open(settingsPath, 'w') as f:
                json.dump(settings, f)

        with open(defaultSettingsPath, 'w') as f:
            json.dump(settings, f)


    def LoadSettings(self):
        global settings
        path = pathlib.Path("./Settings/settings.json")
        with open(path) as f:
            settings = json.load(f)

    def SaveSettings(self):
        path = pathlib.Path("./Settings/settings.json")
        with open(path, 'w') as f:
            json.dump(settings, f)

    def RestoreDefaultSettings(self):
        global settings
        path = pathlib.Path("./Settings/defaultSettings.json")
        with open(path) as f:
            settings = json.load(f)
        self.settingsWindow.UpdateFormSettings()
        self.ApplySettings()

    def ApplySettings(self):
        if self.settingsWindow is not None:
            self.settingsWindow.lbl_settings.setStyleSheet(f"font-size: {settings['FONT_SIZE_PRIMARY']}px;\
            font-weight: bold; font-style: italic;")
            self.settingsWindow.pbtn_colorPrimary.setStyleSheet(f"background-color: {settings['COLOR_PRIMARY']};")
            self.settingsWindow.pbtn_colorSecondary.setStyleSheet(f"background-color: {settings['COLOR_SECONDARY']};")
            self.settingsWindow.pbtn_colorBgPrimary.setStyleSheet(f"background-color: {settings['COLOR_BG_PRIMARY']};")
            self.settingsWindow.pbtn_colorBgSecondary.setStyleSheet(f"background-color: {settings['COLOR_BG_SECONDARY']};")
            self.settingsWindow.pbtn_colorBgButton.setStyleSheet(f"background-color: {settings['COLOR_BG_BUTTON']};")

        self.stackedWidget.setStyleSheet(
f"QWidget{{background-color: {settings['COLOR_BG_PRIMARY']}; selection-background-color: {settings['COLOR_PRIMARY']}; selection-color: {settings['COLOR_BG_SECONDARY']};}}"
f"QAbstractScrollArea{{background-color: {settings['COLOR_BG_SECONDARY']};}}"
f"QPushButton{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.8)}px; font-family: {settings['FONT']}; font-weight: bold; color: {settings['COLOR_PRIMARY']}; background-color: {settings['COLOR_BG_BUTTON']};}}"
f"QToolButton{{font-size: {int(settings['FONT_SIZE_PRIMARY']*0.6)}px; font-family: {settings['FONT']}; font-weight: bold; color: {settings['COLOR_PRIMARY']}; background-color: {settings['COLOR_BG_BUTTON']};}}"
f"QLabel{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.8)}px; font-family: {settings['FONT']}; color: {settings['COLOR_PRIMARY']};}}"
f"QLineEdit{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.8)}px; font-family: {settings['FONT']}; min-width: 14em; color: {settings['COLOR_SECONDARY']}; background-color: {settings['COLOR_BG_BUTTON']};}}"
f"QToolTip{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.75)}px; font-family: {settings['FONT']};}}"
f"QListWidget{{font-size: {int(settings['FONT_SIZE_SECONDARY']*1.05)}px; font-family: {settings['FONT']}; color: {settings['COLOR_PRIMARY']};}}"
f"QListWidget::item:selected{{background-color: {settings['COLOR_PRIMARY']};}}"    
f"QTextEdit{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.9)}px; font-family: {settings['FONT']}; color: {settings['COLOR_SECONDARY']};}}"
f"QScrollBar{{background-color: {settings['COLOR_PRIMARY']};}}"
f"QComboBox{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.65)}px; color: {settings['COLOR_SECONDARY']};}}"
f"QComboBox QAbstractScrollArea{{background-color: {settings['COLOR_SECONDARY']};}}"
f"QSpinBox{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.65)}px; color: {settings['COLOR_SECONDARY']};}}"
)
        self.lbl_title.setStyleSheet(f"font-size: {int(settings['FONT_SIZE_PRIMARY'] * 1.2)}px; font-weight: bold; font-style: italic;")
        self.SaveSettings()

    def OnFontChange(self):
        global settings
        font = self.settingsWindow.cmbox_font.currentFont().toString().split(',')[0]
        settings["FONT"] = font
        self.ApplySettings()

    def OnFontSizePrimaryChange(self):
        global settings
        size = self.settingsWindow.spbox_fontSizePrimary.value()
        settings["FONT_SIZE_PRIMARY"] = size
        self.ApplySettings()

    def OnFontSizeSecondaryChange(self):
        global settings
        size = self.settingsWindow.spbox_fontSizeSecondary.value()
        settings["FONT_SIZE_SECONDARY"] = size
        self.ApplySettings()

    def OnColorPrimaryChange(self):
        global settings
        initalColor = QtGui.QColor(settings['COLOR_PRIMARY'])
        dlg = QtWidgets.QColorDialog(self)
        dlg.setWindowTitle("Select Primary Color")
        dlg.setCurrentColor(initalColor)
        if dlg.exec_() == 0:
            color = initalColor.name()
        else:
            color = dlg.currentColor().name()
        settings["COLOR_PRIMARY"] = color
        self.ApplySettings()

    def OnColorSecondaryChange(self):
        global settings
        initalColor = QtGui.QColor(settings['COLOR_SECONDARY'])
        dlg = QtWidgets.QColorDialog(self)
        dlg.setWindowTitle("Select Secondary Color")
        dlg.setCurrentColor(initalColor)
        if dlg.exec_() == 0:
            color = initalColor.name()
        else:
            color = dlg.currentColor().name()
        settings["COLOR_SECONDARY"] = color
        self.ApplySettings()

    def OnColorBgPrimaryChange(self):
        global settings
        initalColor = QtGui.QColor(settings['COLOR_BG_PRIMARY'])
        dlg = QtWidgets.QColorDialog(self)
        dlg.setWindowTitle("Select Primary Background Color")
        dlg.setCurrentColor(initalColor)
        if dlg.exec_() == 0:
            color = initalColor.name()
        else:
            color = dlg.currentColor().name()
        settings["COLOR_BG_PRIMARY"] = color
        self.ApplySettings()

    def OnColorBgSecondaryChange(self):
        global settings
        initalColor = QtGui.QColor(settings['COLOR_BG_SECONDARY'])
        dlg = QtWidgets.QColorDialog(self)
        dlg.setWindowTitle("Select Secondary Background Color")
        dlg.setCurrentColor(initalColor)
        if dlg.exec_() == 0:
            color = initalColor.name()
        else:
            color = dlg.currentColor().name()
        settings["COLOR_BG_SECONDARY"] = color
        self.ApplySettings()

    def OnColorBgButtonChange(self):
        global settings
        initalColor = QtGui.QColor(settings['COLOR_BG_BUTTON'])
        dlg = QtWidgets.QColorDialog(self)
        dlg.setWindowTitle("Select Button Background Color")
        dlg.setCurrentColor(initalColor)
        if dlg.exec_() == 0:
            color = initalColor.name()
        else:
            color = dlg.currentColor().name()
        settings["COLOR_BG_BUTTON"] = color
        self.ApplySettings()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, jrnName):
        super().__init__()

        self.jrn = Journal(jrnName)
        self.keys = list(self.jrn.jrnDict.keys())
        self.draftText = ""
        self.entriesOfToday = self.jrn.GetEntries(self.jrn.date, settings['COLOR_PRIMARY'], "edit")
        self.draftEditText = self.entriesOfToday
        self.mode = "add"
        self.lastValidDate = self.jrn.date
        self.lastReadDate = None

        self.InitUI()

    def InitUI(self):
        # Create layouts and central widget
        widget_main = QtWidgets.QWidget()
        vbox_main = QtWidgets.QVBoxLayout()
        hbox_labels = QtWidgets.QHBoxLayout()
        hbox_buttons = QtWidgets.QHBoxLayout()

        # Label for journal name
        lbl_jName = QtWidgets.QLabel(self.jrn.name.title())
        lbl_jName.setStyleSheet(f"font-size: {int(settings['FONT_SIZE_PRIMARY']*0.9)}px; font-weight: bold;\
        font-style: italic")
        lbl_jName.setMaximumWidth(600)

        # Tool button for returning to Journals Window
        self.tbtn_toJournalsWindow = QtWidgets.QToolButton()
        self.tbtn_toJournalsWindow.setText("...")
        self.tbtn_toJournalsWindow.setMinimumHeight(40)
        self.tbtn_toJournalsWindow.setCursor(QtCore.Qt.PointingHandCursor)
        self.tbtn_toJournalsWindow.setShortcut(QtGui.QKeySequence("ESC"))
        self.tbtn_toJournalsWindow.setToolTip(f"Return to the journals window ({self.tbtn_toJournalsWindow.shortcut().toString()})")

        # QDateEdit for date selection
        self.dateEdit = QtWidgets.QDateEdit()
        self.dateEdit.setStyleSheet(
            f"QDateEdit{{font-size: {int(settings['FONT_SIZE_PRIMARY']*0.6)}px; font-family: {settings['FONT']};\
        color: {settings['COLOR_PRIMARY']};background-color: {settings['COLOR_BG_PRIMARY']};}}"
            f"QCalendarWidget{{font-size: {int(settings['FONT_SIZE_SECONDARY']*0.7)}px;\
            font-family: {settings['FONT']}; selection-background-color: {settings['COLOR_PRIMARY']}; selection-color: {settings['COLOR_BG_SECONDARY']};}}"
            f"QAbstractItemView{{background-color: {settings['COLOR_PRIMARY']};}}"
            f"QMenu{{font-family: {settings['FONT']};background-color: {settings['COLOR_BG_PRIMARY']};\
            color: {settings['COLOR_SECONDARY']};}}"
            f"QMenu::item:selected{{background: {settings['COLOR_PRIMARY']}; color: {settings['COLOR_BG_SECONDARY']}}}"
            f"#qt_calendar_navigationbar{{background: {settings['COLOR_BG_PRIMARY']};}}"
            f"#qt_calendar_prevmonth{{background: {settings['COLOR_BG_PRIMARY']};}}"
            f"#qt_calendar_nextmonth{{background: {settings['COLOR_BG_PRIMARY']};}}"
            f"#qt_calendar_monthbutton{{background: {settings['COLOR_BG_PRIMARY']};}}"
            f"#qt_calendar_yearbutton{{background: {settings['COLOR_BG_PRIMARY']};}}"
            f"#qt_calendar_yearedit{{color: {settings['COLOR_PRIMARY']};}}"
        )
        self.dateEdit.setMinimumSize(200,30)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setCorrectionMode(1)  # 0: Previous value | 1: Nearest value
        self.dateEdit.setDate(self.StrToQDate(self.jrn.date))
        min, max = self.StrToQDate(self.keys[0]), self.StrToQDate(self.keys[-1])
        self.dateEdit.setDateRange(min, max)
        self.dateEdit.setEnabled(False)
        self.dateEdit.setCursor(QtCore.Qt.PointingHandCursor)
        self.dateEdit.dateChanged.connect(self.OnQDateChange)

        # Textedit for adding entries
        self.tedit_entry = QtWidgets.QTextEdit()
        self.tedit_entry.setPlaceholderText("What happened today?")
        self.tedit_entry.setMinimumSize(360, 120)
        self.tedit_entry.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.tedit_entry.setFrameShape(QtWidgets.QFrame.Box)
        self.tedit_entry.setLineWidth(2)
        self.tedit_entry.textChanged.connect(self.SaveDraft)

        # Pushbutton for submitting entries
        self.pbtn_submit = QtWidgets.QPushButton("Submit")
        self.pbtn_submit.setMinimumHeight(60)
        self.pbtn_submit.setCursor(QtCore.Qt.PointingHandCursor)
        self.pbtn_submit.setShortcut(QtGui.QKeySequence("CTRL+S"))
        self.pbtn_submit.setToolTip(f"Submit entry to the journal ({self.pbtn_submit.shortcut().toString()})")
        self.pbtn_submit.clicked.connect(self.ButtonSubmit)

        # Pushbutton for reading entries
        self.pbtn_read = QtWidgets.QPushButton("Read")
        self.pbtn_read.setMinimumHeight(60)
        self.pbtn_read.setCursor(QtCore.Qt.PointingHandCursor)
        self.pbtn_read.setShortcut(QtGui.QKeySequence("CTRL+R"))
        self.pbtn_read.setToolTip(f"Read entries of the journal ({self.pbtn_read.shortcut().toString()})")
        self.pbtn_read.clicked.connect(self.ButtonRead)

        # Scrollbar for traversing the entriesW
        self.sbar_entry = QtWidgets.QScrollBar()
        self.sbar_entry.setOrientation(QtCore.Qt.Horizontal)
        self.sbar_entry.setRange(0, len(self.keys) - 1)
        self.sbar_entry.setEnabled(False)
        self.sbar_entry.setMinimumHeight(30)
        self.sbar_entry.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.sbar_entry.setInvertedControls(False)
        self.sbar_entry.setPageStep(7)
        self.RandomizeSliderPos()
        self.sbar_entry.setCursor(QtCore.Qt.OpenHandCursor)
        self.sbar_entry.sliderPressed.connect(lambda: self.sbar_entry.setCursor(QtCore.Qt.ClosedHandCursor))
        self.sbar_entry.sliderReleased.connect(lambda: self.sbar_entry.setCursor(QtCore.Qt.OpenHandCursor))
        self.sbar_entry.valueChanged.connect(self.SlideEntry)

        # hbox_labels assignment
        hbox_labels.addWidget(lbl_jName)
        hbox_labels.addWidget(self.tbtn_toJournalsWindow)
        hbox_labels.addStretch()
        hbox_labels.addWidget(self.dateEdit)
        # hbox_labels options
        hbox_labels.setContentsMargins(0, 0, 0, 20)
        hbox_labels.setSpacing(10)

        # hbox_buttons assignment
        hbox_buttons.addWidget(self.pbtn_submit)
        hbox_buttons.addStrut(1)
        hbox_buttons.addWidget(self.pbtn_read)
        # hbox_buttons options
        hbox_buttons.setContentsMargins(0, 8, 0, 0)
        hbox_buttons.setSpacing(20)
        hbox_buttons.setStretch(0, 3)
        hbox_buttons.setStretch(2, 3)

        # vbox_main assignment
        vbox_main.addLayout(hbox_labels)
        vbox_main.addWidget(self.sbar_entry)
        vbox_main.addWidget(self.tedit_entry)
        vbox_main.addLayout(hbox_buttons)
        # vbox_main options
        vbox_main.setSpacing(0)
        vbox_main.setContentsMargins(30, 20, 30, 10)

        # Central widget assignment
        widget_main.setLayout(vbox_main)
        self.setCentralWidget(widget_main)

    def ButtonSubmit(self):
        # Get the text from textedit and add entry to journal
        entry = self.tedit_entry.toPlainText()
        self.tedit_entry.clear()
        # Get time and add entry
        time = dt.datetime.now().strftime("%#I:%M %p")
        self.jrn.AddEntry(entry, time)
        self.entriesOfToday = self.jrn.GetEntries(self.jrn.date, settings['COLOR_PRIMARY'], "edit")
        self.tedit_entry.setFocus()

    def ButtonEdit(self):
        # Change 'tedit_entry' properties
        self.tedit_entry.setText(self.jrn.GetEntries(self.jrn.date, settings['COLOR_PRIMARY'], "edit"))
        # Toggle mode
        self.mode = "edit"
        self.tedit_entry.setReadOnly(False)
        self.tedit_entry.setFocus()
        cursor = self.tedit_entry.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.tedit_entry.setTextCursor(cursor)
        self.Reconnect(self.tedit_entry.textChanged, self.SaveEditDraft, self.SaveDraft)
        # Change 'sbar_entry' properties
        self.sbar_entry.setEnabled(False)
        # Change 'dateEdit' properties
        self.dateEdit.setEnabled(False)
        # Change 'Edit' button properties
        self.pbtn_submit.setText("Save")
        self.pbtn_submit.setShortcut(QtGui.QKeySequence("CTRL+S"))
        self.pbtn_submit.setToolTip(f"Save the changes ({self.pbtn_submit.shortcut().toString()})")
        self.Reconnect(self.pbtn_submit.clicked, self.ButtonSaveEdit, self.ButtonEdit)
        # Change 'Add' button properties
        self.pbtn_read.setText("Revert")
        self.pbtn_read.setShortcut(QtGui.QKeySequence("CTRL+R"))
        self.pbtn_read.setToolTip(f"Discard the changes and revert to original entry ({self.pbtn_read.shortcut().toString()})")
        self.Reconnect(self.pbtn_read.clicked, self.ButtonRevertEdit, self.ButtonAdd)

    def ButtonSaveEdit(self):
        # Save changed entry
        time = dt.datetime.now().strftime("%#I:%M %p")
        self.jrn.EditEntry(self.draftEditText, time)
        self.entriesOfToday = self.jrn.GetEntries(self.jrn.date, settings['COLOR_PRIMARY'], "edit")
        # Toggle mode
        self.mode = "read"
        # Change 'tedit_entry' properties
        self.tedit_entry.setReadOnly(True)
        self.SlideEntry()
        self.Reconnect(self.tedit_entry.textChanged,self.SaveDraft, self.SaveEditDraft)
        # Change 'sbar_entry' properties
        self.sbar_entry.setEnabled(True)
        # Change 'dateEdit' properties
        self.dateEdit.setEnabled(True)
        # Change 'SaveEdit' button properties
        self.pbtn_submit.setText("Edit")
        self.pbtn_submit.setShortcut(QtGui.QKeySequence("CTRL+S"))
        self.pbtn_submit.setToolTip(f"Edit the entries of today ({self.pbtn_submit.shortcut().toString()})")
        self.Reconnect(self.pbtn_submit.clicked, self.ButtonEdit, self.ButtonSaveEdit)
        # Change 'RevertEdit' button properties
        self.pbtn_read.setText("Add")
        self.pbtn_read.setShortcut(QtGui.QKeySequence("CTRL+R"))
        self.pbtn_read.setToolTip(f"Add entry to the journal ({self.pbtn_read.shortcut().toString()})")
        self.Reconnect(self.pbtn_read.clicked, self.ButtonAdd, self.ButtonRevertEdit)

    def ButtonRevertEdit(self):
        # Toggle mode
        self.mode = "read"
        # Reset draftEditText
        self.draftEditText = self.entriesOfToday
        # Change 'tedit_entry' properties
        self.tedit_entry.setReadOnly(True)
        self.SlideEntry()
        self.Reconnect(self.tedit_entry.textChanged, self.SaveDraft, self.SaveEditDraft)
        # Change 'sbar_entry' properties
        self.sbar_entry.setEnabled(True)
        # Change 'dateEdit' properties
        self.dateEdit.setEnabled(True)
        # Change 'SaveEdit' button properties
        self.pbtn_submit.setText("Edit")
        self.pbtn_submit.setShortcut(QtGui.QKeySequence("CTRL+S"))
        self.pbtn_submit.setToolTip(f"Edit the entries of today ({self.pbtn_submit.shortcut().toString()})")
        self.Reconnect(self.pbtn_submit.clicked, self.ButtonEdit, self.ButtonSaveEdit)
        # Change 'RevertEdit' button properties
        self.pbtn_read.setText("Add")
        self.pbtn_read.setShortcut(QtGui.QKeySequence("CTRL+R"))
        self.pbtn_read.setToolTip(f"Add entry to the journal ({self.pbtn_read.shortcut().toString()})")
        self.Reconnect(self.pbtn_read.clicked, self.ButtonAdd, self.ButtonRevertEdit)

    def ButtonRead(self):
        # Toggle read mode
        self.mode = "read"
        # Change 'Textedit' properties
        self.tedit_entry.setReadOnly(True)
        self.tedit_entry.setPlaceholderText("Blank... Click 'Add' to add the first entry of today.")
        # Change QDateEdit properties
        self.dateEdit.setEnabled(True)
        self.dateEdit.setDate(self.StrToQDate(self.lastReadDate))
        # Change 'ScrollBar' properties
        self.sbar_entry.setEnabled(True)
        self.SlideEntry()
        self.sbar_entry.setFocus()
        # Change 'Read' button properties
        self.pbtn_read.setText("Add")
        self.pbtn_read.setShortcut(QtGui.QKeySequence("CTRL+R"))
        self.pbtn_read.setToolTip(f"Add entry to the journal ({self.pbtn_read.shortcut().toString()})")
        self.Reconnect(self.pbtn_read.clicked, self.ButtonAdd, self.ButtonRead)
        # Change 'Submit' button properties
        self.pbtn_submit.setText("Edit")
        self.pbtn_submit.setShortcut(QtGui.QKeySequence("CTRL+S"))
        self.pbtn_submit.setToolTip(f"Edit the entries of today ({self.pbtn_submit.shortcut().toString()})")
        self.Reconnect(self.pbtn_submit.clicked, self.ButtonEdit, self.ButtonSubmit)

    def ButtonAdd(self):
        # Change QDateEdit properties
        self.lastReadDate = self.dateEdit.date().toString("yyyy-MM-dd")
        self.dateEdit.setDate(self.StrToQDate(self.jrn.date))
        self.dateEdit.setEnabled(False)
        # Change 'Textedit' properties
        self.tedit_entry.setText(self.draftText)
        self.tedit_entry.setReadOnly(False)
        self.tedit_entry.setPlaceholderText("What happened today?")
        self.tedit_entry.setFocus()
        cursor = self.tedit_entry.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.tedit_entry.setTextCursor(cursor)
        # Toggle add mode
        self.mode = "add"
        # Change 'ScrollBar' properties
        self.sbar_entry.setEnabled(False)
        # Change 'Add' button properties
        self.pbtn_read.setText("Read")
        self.pbtn_read.setShortcut(QtGui.QKeySequence("CTRL+R"))
        self.pbtn_read.setToolTip(f"Read entries of the journal ({self.pbtn_read.shortcut().toString()})")
        self.Reconnect(self.pbtn_read.clicked, self.ButtonRead, self.ButtonAdd)
        # Change 'Edit' button properties
        self.pbtn_submit.setText("Submit")
        self.pbtn_submit.setShortcut(QtGui.QKeySequence("CTRL+S"))
        self.pbtn_submit.setToolTip(f"Submit entry to the journal ({self.pbtn_submit.shortcut().toString()})")
        self.Reconnect(self.pbtn_submit.clicked, self.ButtonSubmit, self.ButtonEdit)

    def SlideEntry(self):
        sPos = self.sbar_entry.sliderPosition()
        date = self.keys[sPos]
        self.tedit_entry.setText(self.jrn.GetEntries(date, settings['COLOR_PRIMARY'], "read"))
        self.dateEdit.setDate(self.StrToQDate(date))

    def RandomizeSliderPos(self):
        pos = randint(0, len(self.keys) - 1)
        self.lastReadDate = self.keys[pos]
        self.sbar_entry.setSliderPosition(pos)

    @staticmethod
    def Reconnect(signal, newHandler=None, oldHandler=None):
        try:
            if oldHandler is not None:
                while True:
                    signal.disconnect(oldHandler)
            else:
                signal.disconnect()
        except TypeError:
            pass
        if newHandler is not None:
            signal.connect(newHandler)

    def SaveDraft(self):
        # If in add mode, save unsubmitted entry on value change
        if self.mode == "add":
            draft = self.tedit_entry.toPlainText()
            draft = draft.replace("<", "&lt;")
            draft = draft.replace(">", "&gt;")
            self.draftText = draft

    def CheckUnsubmittedEntry(self):
        if self.draftText.split() != []:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Closing Journal")
            dlg.setText(f"Entry isn't submitted and will be lost. Proceed?")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            dlg.setIconPixmap(QtGui.QPixmap("./images/warning.png"))
            dlg.setDefaultButton(QtWidgets.QMessageBox.No)
            return dlg.exec_()

    def SaveEditDraft(self):
        # If in edit mode, save unsaved edited entry on value change
        if self.mode == "edit":
            draft = self.tedit_entry.toPlainText()
            draft = draft.replace("<", "&lt;")
            draft = draft.replace(">", "&gt;")
            self.draftEditText = draft

    def CheckUnsubmittedEdit(self):
        if self.draftEditText.strip() != self.entriesOfToday.strip():
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Closing Journal")
            dlg.setText(f"Changes aren't saved and will be lost. Proceed?")
            dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            dlg.setIconPixmap(QtGui.QPixmap("./images/warning.png"))
            dlg.setDefaultButton(QtWidgets.QMessageBox.No)
            return dlg.exec_()

    @staticmethod
    def StrToQDate(timeString):
        return QtCore.QDate.fromString(timeString, "yyyy-MM-dd")

    def OnQDateChange(self):
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        if date in self.keys:
            self.lastValidDate = date
        else:
            date = self.GetNextValidDate(date)
            self.lastValidDate = date
        index = self.keys.index(date)
        self.sbar_entry.setSliderPosition(index)
        if date == self.jrn.date:
            self.pbtn_submit.setEnabled(True)
        else:
            self.pbtn_submit.setEnabled(False)

    def GetNextValidDate(self, date):
        date = dt.datetime.strptime(date, "%Y-%m-%d")
        isGreater = date > dt.datetime.strptime(self.lastValidDate, "%Y-%m-%d")
        if isGreater:
            while str(date)[:10] not in self.keys:
                date += dt.timedelta(1)
            return str(date)[:10]
        else:
            while str(date)[:10] not in self.keys:
                date -= dt.timedelta(1)
            return str(date)[:10]


class SettingsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.InitUI()

    def InitUI(self):
        # Create layouts
        widget_main = QtWidgets.QWidget()
        vbox_main = QtWidgets.QVBoxLayout()
        hbox_title = QtWidgets.QHBoxLayout()
        scrollArea_settings = QtWidgets.QScrollArea()

        # Create title 'Settings'
        self.lbl_settings = QtWidgets.QLabel("Settings")
        self.lbl_settings.setStyleSheet(f"font-size: {settings['FONT_SIZE_PRIMARY']}px; font-weight: bold; font-style: italic;")

        # Tool button for returning to Journals Window
        self.tbtn_toJournalsWindow = QtWidgets.QToolButton()
        self.tbtn_toJournalsWindow.setText("...")
        self.tbtn_toJournalsWindow.setMinimumHeight(40)
        self.tbtn_toJournalsWindow.setCursor(QtCore.Qt.PointingHandCursor)
        self.tbtn_toJournalsWindow.setShortcut(QtGui.QKeySequence("ESC"))
        self.tbtn_toJournalsWindow.setToolTip(f"Return to the journals window ({self.tbtn_toJournalsWindow.shortcut().toString()})")

        # 'Restore Default Settings' button
        self.pbtn_defaultSettings = QtWidgets.QPushButton("Restore")
        self.pbtn_defaultSettings.setMinimumSize(120, 60)
        self.pbtn_defaultSettings.setCursor(QtCore.Qt.PointingHandCursor)
        self.pbtn_defaultSettings.setShortcut(QtGui.QKeySequence("CTRL+D"))
        self.pbtn_defaultSettings.setToolTip(f"Restore default settings ({self.pbtn_defaultSettings.shortcut().toString()})")

        # Form layout for settings
        groupBox_settings = QtWidgets.QGroupBox()
        form_settings = QtWidgets.QFormLayout()
        # Setting: FONT
        self.cmbox_font = QtWidgets.QFontComboBox()
        self.cmbox_font.setMaximumWidth(220)
        self.cmbox_font.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Font:  ", self.cmbox_font)
        # Setting: FONT-SIZE-PRIMARY
        self.spbox_fontSizePrimary = QtWidgets.QSpinBox()
        self.spbox_fontSizePrimary.setMaximumWidth(100)
        self.spbox_fontSizePrimary.setMinimum(30)
        self.spbox_fontSizePrimary.setMaximum(96)
        self.spbox_fontSizePrimary.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Primary Font Size:  ", self.spbox_fontSizePrimary)
        # Setting: FONT-SIZE-SECONDARY
        self.spbox_fontSizeSecondary = QtWidgets.QSpinBox()
        self.spbox_fontSizeSecondary.setMaximumWidth(100)
        self.spbox_fontSizeSecondary.setMinimum(20)
        self.spbox_fontSizeSecondary.setMaximum(64)
        self.spbox_fontSizeSecondary.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Secondary Font Size:  ", self.spbox_fontSizeSecondary)
        # Setting: COLOR-PRIMARY
        self.pbtn_colorPrimary = QtWidgets.QPushButton()
        self.pbtn_colorPrimary.setMaximumWidth(200)
        self.pbtn_colorPrimary.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Primary Color:  ", self.pbtn_colorPrimary)
        # Setting: COLOR-SECONDARY
        self.pbtn_colorSecondary = QtWidgets.QPushButton()
        self.pbtn_colorSecondary.setMaximumWidth(200)
        self.pbtn_colorSecondary.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Secondary Color:  ", self.pbtn_colorSecondary)
        # Setting: COLOR_BG_PRIMARY
        self.pbtn_colorBgPrimary = QtWidgets.QPushButton()
        self.pbtn_colorBgPrimary.setMaximumWidth(200)
        self.pbtn_colorBgPrimary.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Primary Background Color:  ", self.pbtn_colorBgPrimary)
        # Setting: COLOR_BG_SECONDARY
        self.pbtn_colorBgSecondary = QtWidgets.QPushButton()
        self.pbtn_colorBgSecondary.setMaximumWidth(200)
        self.pbtn_colorBgSecondary.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Secondary Background Color:  ", self.pbtn_colorBgSecondary)
        # Setting: COLOR_BG_BUTTON
        self.pbtn_colorBgButton = QtWidgets.QPushButton()
        self.pbtn_colorBgButton.setMaximumWidth(200)
        self.pbtn_colorBgButton.setCursor(QtCore.Qt.PointingHandCursor)
        form_settings.addRow("Button Background Color:  ", self.pbtn_colorBgButton)

        groupBox_settings.setLayout(form_settings)
        scrollArea_settings.setWidgetResizable(True)
        scrollArea_settings.setWidget(groupBox_settings)
        self.UpdateFormSettings()

        # hbox_title assignment
        hbox_title.addWidget(self.lbl_settings)
        hbox_title.addWidget(self.tbtn_toJournalsWindow)
        hbox_title.addStretch()
        hbox_title.addWidget(self.pbtn_defaultSettings)

        # vbox_main assignment
        vbox_main.addLayout(hbox_title)
        vbox_main.addWidget(scrollArea_settings)

        # Central widget assignment
        widget_main.setLayout(vbox_main)
        self.setCentralWidget(widget_main)

    def UpdateFormSettings(self):
        self.cmbox_font.setCurrentFont(QtGui.QFont(settings["FONT"]))
        self.spbox_fontSizePrimary.setValue(settings["FONT_SIZE_PRIMARY"])
        self.spbox_fontSizeSecondary.setValue(settings["FONT_SIZE_SECONDARY"])
        self.pbtn_colorPrimary.setStyleSheet(f"background-color: {settings['COLOR_PRIMARY']};")
        self.pbtn_colorSecondary.setStyleSheet(f"background-color: {settings['COLOR_SECONDARY']};")
        self.pbtn_colorBgPrimary.setStyleSheet(f"background-color: {settings['COLOR_BG_PRIMARY']};")
        self.pbtn_colorBgSecondary.setStyleSheet(f"background-color: {settings['COLOR_BG_SECONDARY']};")
        self.pbtn_colorBgButton.setStyleSheet(f"background-color: {settings['COLOR_BG_BUTTON']};")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = JournalsWindow()
    sys.exit(app.exec_())
