import pyfiles
import time
import numpy as np

import sys

from PySide6.QtWidgets import (QApplication, QComboBox, QDialog,
                               QDialogButtonBox, QGridLayout, QGroupBox,
                               QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QMenu, QMenuBar, QPushButton, QSpinBox,
                               QTextEdit, QVBoxLayout, QListWidget, QTableWidget,QTableWidgetItem)
from PySide6.QtGui import QColor

import qdarktheme
import unreal_stylesheet

import pyqtgraph as pg


pgo = pyfiles.PileOptModel()

class Dialog(QDialog):
    num_grid_rows = 3
    num_buttons = 2
    def __init__(self):
        super().__init__()
 

        self.drawUI()
        self.write_input()
   


    def read_input(self):
        # Initialize settings
        path        = "C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases.xlsx"
        nrVal       = 136  # 60,136, 640

        xvec        = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5]
        yvec        = [2, 3, 4, 2, 3, 4, 2, 3, 4]

        npiles      = 8
        incl        = 4
        nvert       = 0
        singdir     = 3
        plen        = 9

        Nmax        = 0
        Nmin        = -2400
        
        pyfiles.PileOptModel.defineSettings(pgo,xvec,yvec,npiles,nvert,singdir,plen,incl,path,nrVal,Nmax,Nmin)

    # Run analysis
    def run_infl(self):
        self.read_input()

        pyfiles.PileOptModel.genPileConfigs(pgo)
        pyfiles.PileOptModel.readLoadCases(pgo)
        pyfiles.PileOptModel.pileInfluenceRun(pgo)

        self.update_list()

        #pyfiles.PileOptModel.plotPileGroup(pgo)
    
    def write_input(self):
        self.nPiles.setText("8")
        self.nVertPiles.setText("0")
        self.incl.setText("4")
        self.sdirPiles.setText("3")
        self.plen.setText("7")
        self.nMax.setText("0")
        self.nMin.setText("-2400")

        self.path.setText("C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases.xlsx")

    def read_input(self):

        npiles      = int(self.nPiles.text())
        nvert       = int(self.nVertPiles.text())
        singdir     = int(self.sdirPiles.text())
        plen        = int(self.plen.text())
        incl        = int(self.incl.text())
        Nmax        = int(self.nMax.text())
        Nmin        = int(self.nMin.text())

        path        = str(self.path.text())

        nrVal       = 136

        xvec        = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5]
        yvec        = [2, 3, 4, 2, 3, 4, 2, 3, 4]

        pyfiles.PileOptModel.defineSettings(pgo,xvec,yvec,npiles,nvert,singdir,plen,incl,path,nrVal,Nmax,Nmin)

    def create_input_area(self):
        self.input_area = QGroupBox("Indata")

        line_label = QLabel("Sökväg")
        self.path = QLineEdit()
        runButton = QPushButton("Influence Run"); runButton.clicked.connect(self.run_infl)
        auxButton = QPushButton("Aux Button")   ; runButton.clicked.connect(self.update_plot)

        layout   = QHBoxLayout()

        layout.addWidget(line_label)
        layout.addWidget(self.path,1)
        layout.addWidget(runButton)
        layout.addWidget(auxButton)

        self.input_area.setLayout(layout)

    def create_settings_area(self):
        self.settings_area = QGroupBox("Settings")

        layout = QGridLayout()

        layout.addWidget(QLabel("Number of piles"),0,0);            self.nPiles = QLineEdit();      layout.addWidget(self.nPiles,0,1)
        layout.addWidget(QLabel("Number of vertical Piles"),1,0);   self.nVertPiles = QLineEdit();  layout.addWidget(self.nVertPiles,1,1)
        layout.addWidget(QLabel("Pile inclination"),2,0);           self.incl = QLineEdit();        layout.addWidget(self.incl,2,1)

        layout.addWidget(QLabel("Number of sing dir piles"),0,2);   self.sdirPiles = QLineEdit();   layout.addWidget(self.sdirPiles,0,3)
        layout.addWidget(QLabel("Pile lenght"),1,2);                self.plen = QLineEdit();        layout.addWidget(self.plen,1,3)

        layout.addWidget(QLabel("Max pile reaction"),0,4);          self.nMax = QLineEdit();        layout.addWidget(self.nMax,0,5)
        layout.addWidget(QLabel("Min pile reaction"),1,4);          self.nMin = QLineEdit();        layout.addWidget(self.nMin,1,5)


        self.settings_area.setLayout(layout)


    def create_result_area(self):
        self.result_area = QGroupBox("Result area")

        self.view_area = pg.PlotWidget()
        self.view_area.setBackground(None)

        self.configList = QListWidget()
        self.configList.setFixedWidth(200)
        self.configList.clicked.connect(self.update_plot)

        self.input_table = QTableWidget()
        self.input_table.setFixedWidth(245)
        
        self.input_table.setRowCount(20)
        self.input_table.setColumnCount(2)

        #self.input_table.setColumnWidth(int(1),int(20))


        layout = QHBoxLayout()
        
        layout.addWidget(self.view_area,1)
        layout.setSpacing(20)
        layout.addWidget(self.configList)
        layout.setSpacing(20)
        layout.addWidget(self.input_table)

        self.result_area.setLayout(layout)

    def update_plot(self):
        nr = self.configList.currentRow()
        self.plot_config(nr)

    def update_list(self):
        self.configList.clear()

        for i in range(len(pgo.configStore)):
            self.configList.addItems(["Config " + str(pgo.configStore[i]) + ":  " + str(pgo.Nmaxstore[i]) + " | " + str(pgo.Nminstore[i])])
            
    def plot_config(self,nr):
        print('Update plot...')
        pyfiles.PileOptModel.pileExpand(pgo,nr) 
        self.view_area.plotItem.clear()
        #self.view_area.plotItem.setFixedHeight(400)
        #self.view_area.plotItem.setFixedWidth(400)

        self.view_area.setXRange(-4,4, padding=0.1)
        self.view_area.setYRange(-4,4, padding=0.1)
        self.view_area.setBackground(None)

        plt = self.view_area.plotItem.plot(pgo.x1vec,pgo.y1vec,pen=None,symbol='o',symbolPen = 'w', color='w', symbolBrush='black')

        fak = 0.3

        for i in range(len(pgo.x1vec)):

            if pgo.incl[i] == 0:
                x2 = pgo.x1vec[i]
                y2 = pgo.y1vec[i]
            else:
                x2 = pgo.x1vec[i] + np.cos(np.radians(pgo.bearing[i]))*fak
                y2 = pgo.y1vec[i] + np.sin(np.radians(pgo.bearing[i]))*fak

            plt.setSymbolSize(15)
            plt = self.view_area.plotItem.plot([pgo.x1vec[i],x2],[pgo.y1vec[i],y2],pen="w", color="w")

        

    def drawUI(self):

        #qdarktheme.setup_theme("dark")
        unreal_stylesheet.setup()

        self.create_input_area()
        self.create_settings_area()
        self.create_result_area()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.input_area)
        main_layout.addWidget(self.settings_area)
        main_layout.addWidget(self.result_area,1)

        self.setLayout(main_layout)

        self.setWindowTitle("Pile Optimization")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec())