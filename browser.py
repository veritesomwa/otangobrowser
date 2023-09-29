import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit, QTabBar, QLabel,
    QVBoxLayout, QHBoxLayout, QStackedLayout, QFrame, QShortcut, QKeySequenceEdit
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView

class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()
        self.setFocus(True)

class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1080, 720)
        self.setWindowTitle("Otango Browser")
        self.setWindowIcon(QIcon("menu.png"))
        self.tabs = []  # List to store web view objects and tab data
        self.tab_count = 0
        self.CreateApp()

    def CreateApp(self):
        # Main Layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Tabbar container
        self.tabbarContainer = QWidget()
        self.tabbarContainerLayout = QHBoxLayout()
        self.tabbarContainer.setObjectName("tabbarContainer")

        # Tabbar
        self.tabbar = QTabBar(tabsClosable=True, movable=True)
        self.tabbar.setExpanding(False)
        self.tabbar.setElideMode(Qt.ElideLeft)
        self.tabbar.tabCloseRequested.connect(self.closeTab)
        self.tabbar.tabBarClicked.connect(self.SwitchTab)
        self.tabbar.setObjectName("TabBar")

        self.btnAddTab = QPushButton()
        self.btnAddTab.setIcon(QIcon("icons/ic_add_black_24px.svg"))
        self.btnAddTab.clicked.connect(self.AddTab)
        self.btnAddTab.setObjectName("btnAddTab")

        self.tabbarContainerLayout.addWidget(self.tabbar)
        self.tabbarContainerLayout.addStretch(1)
        self.tabbarContainerLayout.addWidget(self.btnAddTab)
        self.tabbarContainer.setLayout(self.tabbarContainerLayout)

        # Toolbar
        self.toolbar = QWidget()
        self.toolbar_layout = QHBoxLayout()
        self.toolbar.setLayout(self.toolbar_layout)

        # Tools
        self.btnBack = QPushButton()
        self.btnBack.setObjectName("btnControl")
        self.btnBack.setIcon(QIcon("icons/ic_keyboard_arrow_left_black_24px.svg"))
        self.btnBack.clicked.connect(self.goBack)
        self.btnForward = QPushButton()
        self.btnForward.setObjectName("btnControl")
        self.btnForward.setIcon(QIcon("icons/ic_keyboard_arrow_right_black_24px.svg"))
        self.btnForward.clicked.connect(self.goForward)
        self.btnRefresh = QPushButton()
        self.btnRefresh.setObjectName("btnControl")
        self.btnRefresh.setIcon(QIcon("icons/ic_refresh_black_24px.svg"))
        self.btnRefresh.clicked.connect(self.refresh)

        self.addressbar = AddressBar()
        self.addressbar.returnPressed.connect(self.BrowseTo)

        self.menu = QPushButton()
        self.menu.setIcon(QIcon("icons/menu.png"))

        self.toolbar_layout.addWidget(self.btnBack)
        self.toolbar_layout.addWidget(self.btnForward)
        self.toolbar_layout.addWidget(self.btnRefresh)
        self.toolbar_layout.addWidget(self.addressbar)
        self.toolbar_layout.addWidget(self.menu)

        # Container
        self.container = QWidget()
        self.container_layout = QStackedLayout()
        self.container.setLayout(self.container_layout)

        self.layout.addWidget(self.tabbarContainer)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        self.AddTab()

        self.show()

    def AddTab(self):
        i = self.tab_count

        self.tabs.append(QWidget())
        self.tabs[i].setObjectName("tab" + str(i))
        self.tabs[i].layout = QHBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)

        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl().fromUserInput("http://www.google.com"))
        self.tabs[i].content.titleChanged.connect(lambda: self.getTitle(i))
        self.tabs[i].content.iconChanged.connect(lambda: self.getIcon(i))
        self.tabs[i].content.urlChanged.connect(lambda: self.updateAddressbar(i))

        self.tabs[i].layout.addWidget(self.tabs[i].content)
        self.tabs[i].setLayout(self.tabs[i].layout)

        self.container_layout.addWidget(self.tabs[i])
        self.container_layout.setCurrentWidget(self.tabs[i])
        self.container_layout.setCurrentIndex(i)

        self.tabbar.addTab("New Tab")
        self.tabbar.setCurrentIndex(i)
        self.tabbar.setTabData(i, "tab" + str(i))

        self.tab_count += 1

    def closeTab(self, i):
        tab_data = self.tabbar.tabData(i)
        tab_content = self.findChild(QWidget, tab_data)
        if tab_content is not None:
            # Get the current index before removing the tab
            current_index = self.tabbar.currentIndex()
            self.container_layout.removeWidget(tab_content)
            tab_content.deleteLater()  # Delete the web view widget
            self.tabs.pop(i)  # Remove the object from the list

            self.tabbar.removeTab(i)
            self.tab_count -= 1

            # If the current tab was closed, switch to the previous tab
            if i == current_index:
                if current_index > 0:
                    self.tabbar.setCurrentIndex(current_index - 1)
                    self.SwitchTab(current_index - 1)
                elif self.tab_count > 0:
                    self.tabbar.setCurrentIndex(0)
                    self.SwitchTab(0)
                else:
                    # No more tabs left, add a new tab
                    self.AddTab()

    def SwitchTab(self, i):
        if self.tabs[i]:
            self.container_layout.setCurrentWidget(self.tabs[i])
            url = self.tabs[i].content.url()
            self.addressbar.setText(url.toString())

    def getTitle(self, i):
        tab_data = self.tabbar.tabData(i)
        tab_content = self.findChild(QWidget, tab_data)
        title = tab_content.content.title()
        self.tabbar.setTabText(i, title)

    def getIcon(self, i):
        tab_data = self.tabbar.tabData(i)
        tab_content = self.findChild(QWidget, tab_data)
        icon = tab_content.content.icon()
        self.tabbar.setTabIcon(i, icon)

    def updateAddressbar(self, i, url=None):
        if url is None:
            tab_data = self.tabbar.tabData(i)
            tab_content = self.findChild(QWidget, tab_data)
            url = tab_content.content.url()
        self.addressbar.setText(url.toString())

    def goBack(self):
        i = self.tabbar.currentIndex()
        if i >= 0:
            tab_content = self.tabs[i].content
            if tab_content.history().canGoBack():
                tab_content.back()

    def goForward(self):
        i = self.tabbar.currentIndex()
        if i >= 0:
            tab_content = self.tabs[i].content
            if tab_content.history().canGoForward():
                tab_content.forward()

    def refresh(self):
        i = self.tabbar.currentIndex()
        if i >= 0:
            tab_content = self.tabs[i].content
            tab_content.reload()

    def BrowseTo(self):
        text = self.addressbar.text()
        url = ""
        if 'http' not in text:
            if '.' not in text:
                if 'localhost' in text:
                    url = 'http://' + text
                else:
                    url = 'http://google.com/search?q=' + text
            else:
                url = 'http://' + text
        else:
            url = text

        i = self.tabbar.currentIndex()
        self.object = self.findChild(QWidget, self.tabbar.tabData(i))
        self.object.content.load(QUrl.fromUserInput(url))

    def showURLTooltip(self, url):
        # Show the URL as a tooltip when the mouse hovers over the content
        self.addressbar.setToolTip(url)

    def hideURLTooltip(self):
        # Hide the tooltip when the mouse hovers out
        self.addressbar.setToolTip('')

    def mouseMoveEvent(self, event):
        # Get the current tab index and the URL of the web view
        current_index = self.tabbar.currentIndex()
        if current_index >= 0:
            tab_data = self.tabbar.tabData(current_index)
            tab_content = self.findChild(QWidget, tab_data)
            url = tab_content.content.url().toString()

            # Show the URL as a tooltip when the mouse hovers over the content
            self.showURLTooltip(url)

    def leaveEvent(self, event):
        # Hide the tooltip when the mouse leaves the application
        self.hideURLTooltip()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("material.css") as style:
        app.setStyleSheet(style.read())
    window = App()
    sys.exit(app.exec_())
