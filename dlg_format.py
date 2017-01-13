from PyQt5.QtCore import Qt, QAbstractListModel
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QFormLayout, QDialogButtonBox, QCheckBox, QComboBox, QSpinBox
import csv

_fields = ["delim", "qchar", "echar", "lineterm", "quoting", "dblquote", "skipspace", "header", "skiplines"]

# display text for QUOTE enum
_quoting = {
    csv.QUOTE_ALL : "All fields",
    csv.QUOTE_NONNUMERIC :"Non-numeric fields",
    csv.QUOTE_MINIMAL :"Only when required",
    csv.QUOTE_NONE :"None"
}

_params = {
    "delim": {
        "label": "Delimiter",
        "tip": "The field delimeter for the file",
        "type": str,
        "default": ","
    },
    "qchar": {
        "label":"Quote",
        "tip":"The quoting character for the file",
        "type": str,
        "default":'"'
    },
    "echar": {
        "label": "Escape",
        "tip": "Used to escape other special characters",
        "type": str,
        "default":"" # None
    },
    "lineterm": {
        "label": "Line End",
        "tip": "Format of the file's line terminator",
        "type": [str],
        "choices": [r'\r', r'\n', r'\r\n'],
        "default": r"\r\n"
    },
    "quoting": {
        "label":"Quoting",
        "tip":"Quoting Policy for the file",
        "type": [int],
        "choices": [csv.QUOTE_NONE, csv.QUOTE_MINIMAL, csv.QUOTE_NONNUMERIC, csv.QUOTE_ALL],
        "transdict":_quoting, # dict used to translate val->text for display
        "default": csv.QUOTE_MINIMAL
    },
    "dblquote": {
        "label": "Double Quote",
        "tip": "Can the quote character quote itself",
        "type": bool,
        "default": True
    },
    "skipspace": {
        "label": "Skip Space",
        "tip": "Ignore space immediately following a delimiter",
        "type": bool,
        "default": False
    },
    "header": {
        "label": "Header",
        "tip": "Use the first row of the file as the header",
        "type": bool,
        "default": False
    },
    "skiplines": {
        "label": "Skip",
        "tip": "Ignore this many lines at the beginning of the file",
        "type": int,
        "default": 0,
        "min": 0,
        "max": 99
    }

}

class CSVFormatDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: remember last choice for all fields

        # self._defaults = {
        #     "delim": ',',
        #     "qchar": '"',
        #     "escchar": None, # None disables escaping
        #     "lineterm": r'\r\n', # only matters for writer
        #     "quoting": csv.QUOTE_MINIMAL,
        #     "dblquote": True,
        #     "ignore_space": False # skipinitialspace
        # }

        self.setWindowTitle("Load CSV")

        # escape character is only used by writer if quoting==QUOTE_NONE
        # (for delim) or doublequote==False (for quotechar). Removes
        # special meaning from chars when reading.

        # self.delimiter = self._defaults["delim"]

        # TODO: allow and handle setting the quote char to balanced characters, like "{}" or "<<>>"
        # ( this will require a custom dialect sublcass...and probably a custom reader/writer, too)
        # self.quotechar = self._defaults["qchar"]

        self._labels = dict.fromkeys(_fields)
        self._fields = dict.fromkeys(_fields)

        self.mdialect = None
        self.header = False
        self.skiplines = 0

        self._setup_UI()


    def _setup_UI(self):
        self._layout = QFormLayout(self)

        labels = self._labels
        fields = self._fields

        # make arranging the fields easier
        linecount = 0

        for f in _fields:
            labels[f] = QLabel(self,
                               text=_params[f]["label"],
                               toolTip=_params[f]["tip"])

            self._layout.setWidget(linecount, QFormLayout.LabelRole, labels[f])

            t = _params[f]["type"]

            if isinstance(t, list):
                # means we have a 'choices' array
                t=t[0]
                cbox = QComboBox(self)

                # the default really should be in the list of choices...
                assert _params[f]["default"] in _params[f]["choices"]

                if t is str:
                    cbox.addItems(_params[f]["choices"])

                    # set the box to show the default
                    cbox.setCurrentIndex(cbox.findText(_params[f]["default"]))
                else:
                    # need to translate from data values to text
                    trans = _params[f]["transdict"]

                    for c in _params[f]["choices"]:
                        cbox.addItem(trans[c], c)

                    cbox.setCurrentIndex(cbox.findData(_params[f]["default"]))

                # store the combobox w/ the rest of our fields
                fields[f] = cbox


            else:
                if t is str:
                    fields[f] = QLineEdit(self,
                                          text=_params[f]["default"])

                elif t is bool:
                    fields[f] = QCheckBox(self)
                    fields[f].setChecked(_params[f]["default"])

                # maybetodo?: handle other types
                elif t is int:
                    fields[f] = QSpinBox(self,
                                  minimum = _params[f]["min"],
                                  maximum = _params[f]["max"])

                else:
                    raise TypeError(f"Invalid field type: {t}")

            self._layout.setWidget(linecount,
                                   QFormLayout.FieldRole,
                                   fields[f])
            labels[f].setBuddy(fields[f])

            linecount += 1

        ## button box
        self._buttonBox = QDialogButtonBox(self)
        self._buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self._layout.setWidget(linecount, QFormLayout.SpanningRole,
                                  self._buttonBox)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)


    def accept(self):

        # self.delimiter = self._fld_delim.text() or self._defaults["delim"]
        # self.quotechar = self._fld_qchar.text() or self._defaults["qchar"]

        # create custom dialect from adjusted properties

        class mdialect(csv.Dialect):
            _name = "manual_dialect"
            # all other dialects have this hardcoded to this:
            lineterminator = '\r\n'

            # quoting = csv.QUOTE_MINIMAL
            # escapechar = ''   ????

            @classmethod
            def tostring(cls):
                return f"""Dialect(delimiter={cls.delimiter!r},
                 quotechar={cls.quotechar!r},
                 escapechar={cls.escapechar!r},
                 lineterminator={cls.lineterminator!r},
                 quoting={cls.quoting},
                 doublequote={cls.doublequote},
                 skipinitialspace={cls.skipinitialspace})"""


        mdialect.delimiter =  self._fields["delim"].text()
        # _csv.reader won't accept a quotechar of ''
        mdialect.quotechar = self._fields["qchar"].text() or '"'
        mdialect.escapechar = self._fields["echar"].text() or None
        mdialect.quoting = self._fields["quoting"].currentData()
        mdialect.doublequote = self._fields["dblquote"].isChecked()
        mdialect.skipinitialspace = self._fields["skipspace"].isChecked()


        # TODO: allow saving a custom-defined dialect for easy selection later
        self.mdialect = mdialect

        self.header = self._fields["header"].isChecked()
        self.skiplines = self._fields["skiplines"].value()

        super().accept()




#_fields = ["delim", "qchar", "echar", "lineterm", "quoting", "dblquote", "skipspace"]
