import csv
import sys
from PySide import QtGui, QtCore, QtWebKit
from urllib import urlopen

from sgmllib import SGMLParser


class PCBPainter(QtGui.QDialog):
    def __init__(self, parent):
        super(PCBPainter, self).__init__(parent)

        self.imglabel = QtGui.QLabel()

        vb = QtGui.QVBoxLayout()
        vb.addWidget(self.imglabel)

        openpb = QtGui.QPushButton("Set PCB Image")
        openpb.clicked.connect(self.set_image)

        self.timerFocus = QtCore.QTimer()
        self.timerFocus.setSingleShot(True)
        self.timerFocus.timeout.connect(self.clearfocus)

        self.pcbwidth = QtGui.QDoubleSpinBox()
        self.pcbwidth.setMinimum(0)
        self.pcbwidth.setMaximum(100000)
        self.pcbwidth.valueChanged.connect(self.clearfocusdelay)
        self.pcbheight = QtGui.QDoubleSpinBox()
        self.pcbheight.setMinimum(0)
        self.pcbheight.setMaximum(100000)
        self.pcbheight.valueChanged.connect(self.clearfocusdelay)

        buttongrid = QtGui.QHBoxLayout()
        buttongrid.addWidget(openpb)
        buttongrid.addSpacing(5)
        buttongrid.addWidget(QtGui.QLabel("PCB Width (PnP file units): "))
        buttongrid.addWidget(self.pcbwidth)
        buttongrid.addSpacing(5)
        buttongrid.addWidget(QtGui.QLabel("PCB Height (PnP file units):"))
        buttongrid.addWidget(self.pcbheight)
        buttongrid.addStretch(5)

        vb.addLayout(buttongrid)

        self.setLayout(vb)

        self.image_path = ""

    def xy_to_draw(self, x, y, mirror):

        self.reload_base()

        boardwidth = self.pcbwidth.value()
        boardheight = self.pcbheight.value()

        try:
            scale_x = float(self.base.width()) / float(boardwidth)
            scale_y = float(self.base.height()) / float(boardheight)
        except ZeroDivisionError:
            QtGui.QMessageBox.warning("Division by Zero", "Division by zero - did you set board height & width in image?")
            raise

        x = x * scale_x
        y = y * scale_y

        #Y taken from wrong side normally
        y = self.base.height() - y

        if mirror:
            x = self.base.width() - x

        center = QtCore.QPoint(x, y)

        painter = QtGui.QPainter()
        painter.begin(self.base)
        painter.setBrush(QtCore.Qt.red)
        painter.drawEllipse(center, 5, 5)
        painter.end()

        self.redraw()

    def reload_base(self):
        self.base = QtGui.QImage(self.image_path)

    def redraw(self):
        self.imglabel.setPixmap(QtGui.QPixmap.fromImage(self.base))

    def set_image(self):
        filename, filter = QtGui.QFileDialog.getOpenFileName(parent=self, caption='Select PCB Image', dir='.',
                                                             filter='PCB Image (*.png)')

        if filename:
            self.image_path = filename
            self.reload_base()
            self.redraw()

    def clearfocusdelay(self):
        """"After 5 seconds clear focus, used to avoid accidently writing stuff here with scan gun"""
        self.timerFocus.start(5000)

    def clearfocus(self):
        self.pcbwidth.clearFocus()
        self.pcbheight.clearFocus()

class MeatBagWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MeatBagWindow, self).__init__()
        self.setWindowTitle("Meat Bag Pick-n-Place v0.0000000001")

        self.efilter = filterObj(self)
        self.installEventFilter(self.efilter)

        self.initLayout()
        self.initMenus()
        self.getSettings()
        self.show()

        self.webView = QtWebKit.QWebView()
        self.webView.loadFinished.connect(self.lookupdone)

        self.last_keys = ""
        self.timerScan = QtCore.QTimer()
        self.timerScan.setSingleShot(True)
        self.timerScan.timeout.connect(self.timesUp)

        self.timerScanLineEdit = QtCore.QTimer()
        self.timerScanLineEdit.setSingleShot(True)
        self.timerScanLineEdit.timeout.connect(self.scanline_changed_dly)

        self.build_side = 0

        self.cur_placement = None

    def getSettings(self):
        """Configure settings. Eventually ask user, for now configure in source."""
        self.col_layer = 2
        self.col_x = 4
        self.col_y = 5
        self.col_pn = 8
        self.col_des = 0

        #Starting data row (row=0 is often header)
        self.row_start = 1
        
    def initLayout(self):
        mainLayout = QtGui.QVBoxLayout()

        ###Main parts table
        self.table = QtGui.QTableWidget()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.installEventFilter(self.efilter)

        ###Build Configuration
        gbBuildSetup = QtGui.QGroupBox()
        gbBuildSetup.setTitle("Build Settings")
        buildLayout = QtGui.QGridLayout()

        #Top/Bottom Selection
        cbSide = QtGui.QComboBox()
        cbSide.addItem("Top")
        cbSide.addItem("Bottom")
        cbSide.activated.connect(self.sideSelectionChanged)
        cbSide.installEventFilter(self.efilter)
        
        buildLayout.addWidget(cbSide, 0, 0)
        gbBuildSetup.setLayout(buildLayout)


        ###Part Display
        gbPart = QtGui.QGroupBox()
        gbPart.setTitle("Part Info")

        self.topDes = QtGui.QLineEdit()
        self.topDes.setReadOnly(True)
        self.botDes = QtGui.QLineEdit()
        self.botDes.setReadOnly(True)

        partLayout = QtGui.QGridLayout()

        label_cur = QtGui.QLabel("Current Placement:")
        f = label_cur.font()
        f.setPointSize(12)
        label_cur.setFont(f)
        partLayout.addWidget(label_cur, 0, 0)

        self.place = QtGui.QLineEdit()
        f = self.place.font()
        f.setPointSize(12)
        self.place.setFont(f)
        self.place.setReadOnly(True)
        partLayout.addWidget(self.place, 0, 1)

        partLayout.addWidget(QtGui.QLabel("Top-Side Designators:"), 2, 0)
        partLayout.addWidget(QtGui.QLabel("Bot-Side Designators:"), 3, 0)
        partLayout.addWidget(self.topDes, 2, 1)
        partLayout.addWidget(self.botDes, 3, 1)

        gbPart.setLayout(partLayout)

        ### Debug Stuff

        gbDebug = QtGui.QGroupBox()
        gbDebug.setTitle("Part Number Info")

        self.scanLine = QtGui.QPlainTextEdit()
        self.scanLine.setFixedHeight(40)
        self.scanLine.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.scanLine.textChanged.connect(self.scanline_changed)

        debugLayout = QtGui.QHBoxLayout()
        debugLayout.addWidget(QtGui.QLabel("Scan Output (or paste P/N here):"))
        debugLayout.addWidget(self.scanLine)

        gbDebug.setLayout(debugLayout)

        ### Rest of Stuff
        window = QtGui.QWidget()
        window.setLayout(mainLayout)

        self.pcbpainter = PCBPainter(window)
        self.pcbpainter.show()
        self.pcbpainter.installEventFilter(self.efilter)
        
        mainLayout.addWidget(self.table)
        mainLayout.addWidget(gbBuildSetup)
        mainLayout.addWidget(gbPart)
        mainLayout.addWidget(gbDebug)

        self.setCentralWidget(window)

    def initMenus(self):
        self.openAct = QtGui.QAction("&Open...", self,
                shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.openFile)

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)

    def isTopLayer(self, row):
        """Check if a given row (0-based index) is top-side or bottom-side part"""
        tb = self.table.item(row, self.col_layer).text()

        if tb.lower().startswith("top"):
            return True
        elif tb.lower().startswith("bot"):
            return False
        else:
            raise ValueError("Unknown layer for row %d" % row)

    def sideSelectionChanged(self, indx):
        """User changed build side"""
        self.build_side = indx
        self.recolourTable()

    def openFile(self):
        """Open new CSV PnP file"""

        filename, filter = QtGui.QFileDialog.getOpenFileName(parent=self, caption='Select PnP file', dir='.', filter='CSV files (*.csv)')

        if not filename:
            return

        ppdata = []
        
        with open(filename, "rb") as csvfile:
            ppfile = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in ppfile:
                if len(row) < 4:
                    print("Skipped line: " + ' '.join(row))
                else:
                    ppdata.append(row)

        self.table.clear()
        numRows = len(ppdata)
        numCols = len(ppdata[0]) + 1
        self.table.setRowCount(numRows)
        self.table.setColumnCount(numCols)
        for r in range(0, numRows):
            for c in range(0, numCols - 1):
                try:
                    self.table.setItem(r, c, QtGui.QTableWidgetItem(ppdata[r][c]))
                except IndexError:
                    self.table.setItem(r, c, QtGui.QTableWidgetItem("???"))

            checkitem = QtGui.QTableWidgetItem()
            checkitem.setCheckState(QtCore.Qt.Unchecked)
            self.table.setItem(r, numCols-1, checkitem)

        self.recolourTable()

        #Rebuild local database of part numbers to speed up search
        self.pdb = []
        for r in range(0, numRows):
            self.pdb.append(ppdata[r][self.col_pn])

    def recolourTable(self):
        """Redo the table colour stuff"""
        rowcnt = self.table.rowCount()
        colcnt = self.table.columnCount()

        for r in range(self.row_start, rowcnt):
            try:
                placed = self.table.item(r, colcnt-1).checkState() == QtCore.Qt.Checked
                if placed:
                    alpha = 5
                else:
                    alpha = 120
                if self.isTopLayer(r):
                    bgc = QtGui.QColor(255, 0, 0, alpha)
                else:
                    bgc = QtGui.QColor(0, 0, 255, alpha)
            except ValueError:
                bgc = QtCore.Qt.lightGray

            for c in range(0, colcnt):

                self.table.item(r, c).setBackground(bgc)

    def key_pressed(self, key):
        self.last_keys += key
        self.timerScan.start(100)

    def timesUp(self, _=None):
        """A timer is used to detect end of scan (so no newline on scanner is assumed)"""

        scan = self.last_keys
        self.last_keys = ""

        if scan == " ":
            #User is moving between items
            last_place = self.cur_placement

            try:
                self.table.item(last_place, self.table.columnCount()-1).setCheckState(QtCore.Qt.Checked)
            except TypeError:
                pass

            self.find_next_placement()
            self.recolourTable()
            return


        #Remove line endings etc
        scan = scan.strip()

        #This triggers scan stuff
        self.scanLine.setPlainText(scan)


    def process_new_scan(self, scan):
        """Process a new barcode scan, convert to manufacture PN"""
        if len(scan) < 5:
            print "Scan probably too short, ignoring"
            return

        self.topDes.setText("")
        self.botDes.setText("")

        #Check if we match already
        self.process_new_pn(scan, update_placement=False)

        if len(self.topDesList) > 0 or len(self.botDesList) > 0:
            self.find_next_placement()
            return

        #Failed - try web lookup

        if scan[0] == '[' and scan[1] == ')':
            # DIGIKEY
            if len(scan) > 30:
                pn_start = scan.split('1P')[1]
                pn = pn_start.split('K1K5')[0]
                self.process_new_pn(pn)
            else:
                internal_pn = scan[0:7]
                qty = int(scan[10:16])

                print("Old-style barcode, attempting lookup")
                sock = urlopen(
                    'https://www.digikey.com/product-detail/en/keystone-electronics/4245C/36-4245C-ND/' + internal_pn)
                data = sock.read()
                raise NotImplementedError("Old-style barcode not implemented")

                #TODO: If you need to fix this, hack around following code to get actual PN not supplier one
                # data = data.split(" ")
                digikey_pn = data.split('content="sku:')[1].split("-ND")[0] + "-ND"
                # print "%s: %d"%(digikey_pn, qty)
        else:
            # MOUSER???
            print("Maybe Mouser? Trying lookup - WAITING FOR WEBPAGE NOW")
            #Use webview as need JS
            self.webView.load(QtCore.QUrl('https://ca.mouser.com/search/ProductDetail.aspx?R=' + scan))

    def lookupdone(self, _=None):
        """Called when website loaded"""
        html = self.webView.page().mainFrame().toHtml()

        #Decode website type - try mouser first
        try:
            pn = html.split('<div id="divManufacturerPartNum">')[1].split("</div>")[0]
            pn = pn.split('<h1>')[1].split('</h1>')[0]
            print "Found PN: " + pn
            self.process_new_pn(pn)
        except IndexError:
            print "Failed to find PN in returned site."

    def process_new_pn(self, pn, update_placement=True):
        """Given a manufactures PN, find all likely matches"""
        matchlist = []

        #Shitty match for shitty programs
        for i in range(0, len(self.pdb)):
            if (len(self.pdb[i]) > 4 and self.pdb[i] in pn) or pn in self.pdb[i]:
                matchlist.append(i)

        self.topDesList = []
        self.botDesList = []
        topDesStr = ""
        botDesStr = ""

        for r in matchlist:
            if self.isTopLayer(r):
                self.topDesList.append(r)
                topDesStr += self.table.item(r, self.col_des).text() + ", "
            else:
                self.botDesList.append(r)
                botDesStr += self.table.item(r, self.col_des).text() + ", "

        self.topDes.setText(topDesStr)
        self.botDes.setText(botDesStr)

        if update_placement:
            self.find_next_placement()

    def find_next_placement(self):
        """Check the list for unplaced part on active layer"""
        self.cur_placement = None

        if self.build_side == 0:
            parts = self.topDesList
        else:
            parts = self.botDesList

        last_col = self.table.columnCount() - 1

        for p in parts:
            if self.table.item(p, last_col).checkState() == QtCore.Qt.Unchecked:
                #Next placement is 'p'
                self.cur_placement = p
                self.table.scrollToItem(self.table.item(p, 0))
                break

        self.update_placement()

    def update_placement(self):
        """Using variable self.cur_placement, update display to show location, name, etc."""

        if self.cur_placement is not None:
            self.place.setText(self.table.item(self.cur_placement, self.col_des).text())

            self.pcbpainter.xy_to_draw(float(self.table.item(self.cur_placement, self.col_x).text()),
                                       float(self.table.item(self.cur_placement, self.col_y).text()),
                                       self.isTopLayer(self.cur_placement) == False)

        else:
            if len(self.topDesList) == 0 and len(self.botDesList) == 0:
                self.place.setText("Not Found")
            else:
                self.place.setText("Done")


    def scanline_changed(self):
        self.timerScanLineEdit.start(100)

    def scanline_changed_dly(self):
        self.process_new_scan(self.scanLine.toPlainText())
        self.scanLine.clearFocus()



class filterObj(QtCore.QObject):
    def __init__(self, windowObj):
        QtCore.QObject.__init__(self)
        self.windowObj = windowObj

    def eventFilter(self, obj, event):
        if (event.type() == QtCore.QEvent.KeyPress):
            key = event.text()

            self.windowObj.key_pressed(key)
            return True
        else:
            return False



        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = MeatBagWindow()
    app.exec_()


if __name__ == '__main__':
    main()
