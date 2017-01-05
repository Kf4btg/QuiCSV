from pathlib import PurePath
# import csv

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings, QSize
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtGui import QIcon, QKeySequence


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._currfile = None
        self._display_name = ""
        # self._modified = False

        self.tableview = QtWidgets.QTableWidget(self)

        self.setCentralWidget(self.tableview)

        self._create_actions()
        self._create_menus()
        self._create_toolbars()

        self.read_settings()

    @property
    def modified(self):
        return self.isWindowModified()

    @modified.setter
    def modified(self, value):
        self.setWindowModified(value)

    def new(self):
        if self.check_modified():
            self._set_document("", True)

    def open(self):
        if self.check_modified():
            filename, _ = QtWidgets.QFileDialog(
                ).getOpenFileName(self, filter="Comma Separated Values files [csv] (*.csv);;"
                                               "All files (*)")

            if filename:
                self._load(filename)

    def save(self):
        print("save()")

    def saveas(self):
        print("saveas()")

    # @property
    # def is_modified(self):
    #     return self._modified

    def check_modified(self):
        """
        If the environment has unsaved modifications, ask the user if
        they would like to save their changes before continuing.
        """
        if self._currfile is not None and self.isWindowModified():
          reply = QMessageBox.warning(self, "MyApplication",
              "Do you want to save your changes?",
              QMessageBox.Cancel|QMessageBox.Discard|QMessageBox.Save)

          if reply == QMessageBox.Save:
              return self.save()
          if reply == QMessageBox.Cancel:
              return False
        return True

    def _load(self, filename):
        """Parse and display the given file in the table view"""

        print(f"load({filename})")

        self._set_document(filename)

    def _set_document(self, filename, set_modified=False):
        self._currfile = filename
        self.modified = set_modified

        if self._currfile:
            self._display_name = PurePath(filename).name
        else:
            self._display_name = "untitled.csv"

        self.setWindowTitle(f"{self._display_name}[*]")

    # region setup

    # noinspection PyArgumentList
    def _create_actions(self):
        qks=QKeySequence
        icon=QIcon().fromTheme

        ## main actions

        self.action_new = QAction(icon("document-new"),
                                  "&New", self,
                                  shortcut=qks.New,
                                  triggered=self.new)

        self.action_open = QAction(icon("document-open"),
                                   "&Open...", self,
                                   shortcut=qks.Open,
                                   triggered=self.open)

        self.action_save = QAction(icon("document-save"),
                                   "&Save", self,
                                   shortcut=qks.Save,
                                   triggered=self.save)

        self.action_saveas = QAction(icon("document-save-as"),
                                     "Save &As...", self,
                                     shortcut=qks.SaveAs,
                                     triggered=self.saveas)

        self.action_quit = QAction(icon("application-exit"),
                                   "&Quit", self,
                                   shortcut=qks.Quit,
                                   triggered=self.close)

        ## edit actions

        self.action_copy = QAction(icon("edit-copy"),
                                   "&Copy", self,
                                   shortcut=qks.Copy,
                                   triggered=dummy)

        self.action_cut = QAction(icon("edit-cut"),
                                  "Cu&t", self,
                                  shortcut=qks.Cut,
                                  triggered=dummy)

        self.action_paste = QAction(icon("edit-paste"),
                                    "&Paste", self,
                                    shortcut=qks.Paste,
                                    triggered=dummy)

        ## disable some actions at application start

        for a in (self.action_save, self.action_saveas,
                  self.action_copy, self.action_cut, self.action_paste):
            a.setEnabled(False)

    def _create_menus(self):
        self.menu_file : QtWidgets.QMenu = self.menuBar().addMenu("&File")
        self.menu_edit : QtWidgets.QMenu = self.menuBar().addMenu("&Edit")

        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_saveas)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_quit)

        self.menu_edit.addAction(self.action_cut)
        self.menu_edit.addAction(self.action_copy)
        self.menu_edit.addAction(self.action_paste)

    def _create_toolbars(self):
        self.toolbar_file : QtWidgets.QToolBar = self.addToolBar("File")
        self.toolbar_edit : QtWidgets.QToolBar = self.addToolBar("Edit")

        self.toolbar_file.addAction(self.action_new)
        self.toolbar_file.addAction(self.action_open)
        self.toolbar_file.addAction(self.action_save)

        self.toolbar_edit.addAction(self.action_cut)
        self.toolbar_edit.addAction(self.action_copy)
        self.toolbar_edit.addAction(self.action_paste)


    def read_settings(self):
        settings = QSettings("kf4btg", "CSVedit")
        pos = settings.value("pos")
        size = settings.value("size", QSize(800,500))

        self.resize(size)
        if pos:
            self.move(pos)

    def write_settings(self):
        settings = QSettings("kf4btg", "CSVedit")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    # endregion

    def closeEvent(self, event):
        """
        Override closeEvent to check for unsaved documents and
        to write application settings.
        """
        if self.check_modified():
            self.write_settings()
            event.accept()
        else:
            event.ignore()

def dummy():
    print("triggered")

def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    app=QApplication(sys.argv)
    app.setApplicationDisplayName("CSVedit")
    mw=MainWindow()
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
