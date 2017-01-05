from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QFormLayout, QDialogButtonBox


class CSVFormatDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: remember last choice for all fields

        self._defaults = {
            "delim": ",",
            "qchar": "\"",
            "ignore_space": False
        }

        self.delimiter = self._defaults["delim"]

        # TODO: allow and handle setting the quote char to balanced characters, like "{}" or "<<>>"
        # ( this will require a custom dialect sublcass...and probably a custom reader/writer, too)
        self.quotechar = self._defaults["qchar"]

        self._setup_UI()


    def _setup_UI(self):
        self._layout = QFormLayout(self)

        # make arranging the fields easier
        linecount = 0

        ## delimeter label and field
        self._lbl_delim = QLabel(self,
                                 text="Delimeter",
                                 toolTip = "Set the field delimeter for the file")

        self._fld_delim = QLineEdit(self,
                                   text=self._defaults["delim"])

        self._layout.setWidget(linecount, QFormLayout.LabelRole, self._lbl_delim)
        self._layout.setWidget(linecount, QFormLayout.FieldRole, self._fld_delim)
        self._lbl_delim.setBuddy(self._fld_delim)

        linecount+=1

        ## quotechar label and field
        self._lbl_qchar = QLabel(self,
                                 text="Quote",
                                 toolTip = "Set the quote character for the file")

        self._fld_qchar = QLineEdit(self,
                                   text=self._defaults["qchar"])

        self._layout.setWidget(linecount, QFormLayout.LabelRole, self._lbl_qchar)
        self._layout.setWidget(linecount, QFormLayout.FieldRole, self._fld_qchar)
        self._lbl_qchar.setBuddy(self._fld_qchar)

        linecount+=1

        ## button box
        self._buttonBox = QDialogButtonBox(self)
        self._buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self._layout.setWidget(linecount, QFormLayout.SpanningRole,
                                  self._buttonBox)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)


    def accept(self):

        self.delimiter = self._fld_delim.text() or self._defaults["delim"]
        self.quotechar = self._fld_qchar.text() or self._defaults["delim"]

        super().accept()




