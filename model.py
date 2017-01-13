import csv
from collections import OrderedDict

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

class BadSniffException(Exception):
    """Raised when the csv sniffer fails to determine the dialect of a file"""


class CSVTableModel(QAbstractTableModel):

    # return the field data for any of these roles in data():
    _dataroles=(Qt.DisplayRole, Qt.EditRole)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._currfile = None

        # set to True if the header names are included in the file
        self._has_header = False

        self._headers = []
        # list of ordered-dicts
        self._data=[]



    # region overrides

    def rowCount(self, parent=QModelIndex()):
        if not self._currfile or parent.isValid():
            # from Qt docs:
            ## Note:: When implementing a table based model, rowCount()
            ## should return 0 when the parent is valid.
            return 0

        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        if not self._currfile or parent.isValid():
            return 0

        return len(self._headers)

    def flags(self, index):
        """Allow editing the table fields"""

        if index.isValid():
            return super().flags(index) | Qt.ItemIsEditable
        return super().flags(index)

    def data(self, index, role=Qt.DisplayRole):
        """

        :param QModelIndex index:
        :param role:
        :return:
        """

        if role in self._dataroles:
            row, col = index.row(), index.column()

            # XXX: so...should we just use a simple 2d-array and access all data by indices? Or should we use keys for the columns to allow the user to easily move columns around while editing?
            # let's try the keys for now

            val = self._data[row][self._headers[col]]

            return "" if val is None else val

    def setData(self, index, value, role=Qt.EditRole):

        if role == Qt.EditRole:
            row, col = index.row(), index.column()

            # turn empty strings into `None`
            self._data[row][self._headers[col]] = None if not value else value

            self.dataChanged.emit(index, index)
            return True

        return super().setData(index, value, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                try:
                    return self._headers[section]
                except IndexError:
                    # if for some reason the index is wrong, just
                    # pass through and allow the column number to be
                    # returned
                    pass

            # just return the row number for the vertical header
            return section + 1
        return super().headerData(section, orientation, role)

    # TODO: figure out how to allow changing the headers without having to modify the keys of EVERY SINGLE ROW (OrderedDict) in the model

    # def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
    #     """
    #     Allow renaming the headers
    #
    #     :param int section:
    #     :param int orientation:
    #     :param Any value:
    #     :param int role:
    #     :return: True if the data was successfully changed
    #     """
    #
    #     if role==Qt.EditRole and orientation == Qt.Horizontal:
    #         self._headers[]



    # endregion

    @staticmethod
    def sniff(sample, delims):
        """Determine the dialect of a csv file"""
        sniffer = csv.Sniffer()
        if delims:
            dialect = sniffer.sniff(sample, delims)
        else:
            dialect = sniffer.sniff(sample)
        has_header = sniffer.has_header(sample)

        return dialect, has_header



    def load_csv(self, csvfile, delims=None):
        """Load a csv file into memory to back the model"""

        # XXX: should we actually load the entire file into memory? What's the alternative?

        try:

            with open(csvfile, newline='') as f:
                self.beginResetModel()

                self._currfile = csvfile
                self._data = []
                self._headers = []

                ## determine dialect and header

                # sample the first 1Kb of the file
                sample = f.read(1024)

                try:
                    dialect, self._has_header = self.sniff(sample, delims)
                except csv.Error as csve:
                    print("CSVerror:", csve)
                    if csve.args[0] == "Could not determine delimiter":
                        raise BadSniffException
                        # print("Could not determine delimeter")
                        # try again with standard delims;
                        # "aligned" files might sometimes cause this
                        # issue, though often it's due to using
                        # odd "quote" characters (like balanced braces
                        # { ... } ) to contain arbitrary text--possibly
                        # including the delimeter, any number of times.
                        # This latter scenario is far more difficult to
                        # deal with.
                        # XXX: this is stupid, sniff() already tries 'standard delims'
                        # dialect, self._has_header = self.sniff(sample, ',;')
                    else:
                        raise
                f.seek(0)

                # sniffer = csv.Sniffer()
                # if delims:
                #     dialect = sniffer.sniff(sample, delims)
                # else:
                #     dialect = sniffer.sniff(sample)
                # self._has_header = sniffer.has_header(sample)

                # f.seek(0)
                if self._has_header:
                    # reader = csv.DictReader(f, dialect=dialect)
                    reader = csv.DictReader(f)
                    print("DictReader")

                    # copy the header names
                    self._headers = list(reader.fieldnames)

                    # TODO: handle "restval", ie scenarios where some rows are too long or too short
                    for row in reader:
                        self._data.append(row)

                else:
                    # todo: allow manually specifying the first row as a header if the sniffer fails to sniff it
                    # reader = csv.reader(f, dialect=dialect)
                    reader = csv.reader(f)
                    print("reader")

                    try:
                        first_row = next(reader)
                        # create generic header names
                        self._headers = ["Column {}".format(i+1) for i in range(len(first_row))]

                        # XXX: should we skip blank rows? If not, we could end up with a dict full of Nones
                        self._data=[OrderedDict(zip(self._headers, first_row))]

                        for row in reader:
                            self._data.append(OrderedDict(zip(self._headers, row)))

                    except StopIteration:
                        # no data
                        pass

                self.endResetModel()


        except IOError as e:
            print(f"IOError: could not load {csvfile}")
            print(e)

    def load_csv_manual(self, csvfile, custom_dialect, header=False, skip=0):
        """Load a csv file into memory to back the model"""

        try:

            with open(csvfile, newline='') as f:
                self.beginResetModel()

                self._currfile = csvfile
                self._data = []
                self._headers = []

                # skip lines if requested
                if skip > 0:
                    for _ in range(skip):
                        f.readline()

                if header:
                    reader = csv.DictReader(f, dialect=custom_dialect)
                    # reader = csv.DictReader(f)
                    print("DictReader")

                    # copy the header names
                    self._headers = list(reader.fieldnames)

                    # TODO: handle "restval", ie scenarios where some rows are too long or too short
                    for row in reader:
                        self._data.append(row)

                else:
                    # todo: allow manually specifying the first row as a header if the sniffer fails to sniff it
                    reader = csv.reader(f, dialect=custom_dialect)
                    # reader = csv.reader(f)
                    print("reader")

                    try:
                        first_row = next(reader)
                        # create generic header names
                        self._headers = ["Column {}".format(i+1) for i in range(len(first_row))]

                        # XXX: should we skip blank rows? If not, we could end up with a dict full of Nones
                        self._data=[OrderedDict(zip(self._headers, first_row))]

                        for row in reader:
                            self._data.append(OrderedDict(zip(self._headers, row)))

                    except StopIteration:
                        # no data
                        pass

                self.endResetModel()


        except IOError as e:
            print(f"IOError: could not load {csvfile}")
            print(e)
