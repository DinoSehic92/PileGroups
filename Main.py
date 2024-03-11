import pyfiles
import sys
import numpy as np
import win32api,win32con,win32process

import qdarktheme
import pyqtgraph as pg

from PySide6.QtWidgets import QDialog,QApplication,QVBoxLayout,QGroupBox,QLabel,QLineEdit,QPushButton,QHBoxLayout,QGridLayout,QListWidget,QTableWidget,QHeaderView,QProgressBar,QTableWidgetItem,QCheckBox, QComboBox
from PySide6.QtCore import Qt, QThreadPool, Signal, Slot, QObject, QTimer

pg_data = pyfiles.PileOptModel()


class Signals(QObject):
    completed = Signal()
    progress = Signal()
    stop = Signal()
    check = Signal()


class MainWindow(QDialog):

    def __init__(self):
        super().__init__()

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)
        print("High prio set")

 
        self.drawUI()
        self.write_input()   


    def write_input(self):
        #self.nPiles.setText("8")
        #self.nVertPiles.setText("0")
        #self.incl.setText("4")
        #self.sdirPiles.setText("3")
        #self.plen.setText("7")
#
        #self.nMax.setText("0")
        #self.nMin.setText("-2400")
        #self.nFilter.setChecked(True)
#
        #self.col_up.setText("2")
        #self.col_down.setText("2")
        #self.coli_box.setChecked(True)
#
        #self.h_slab.setText("9")
        #self.w_slab.setText("6")
        #self.pile_dist.setText("1.0")
#
        #self.path.setText("C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases.xlsx")
#
        #xvec        = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5, 0.5, 1.5, 2.5, "", "", "", "", "", "", "", ""]
        #yvec        = [2, 3, 4, 2, 3, 4, 2, 3, 4, 1, 1, 1, "", "", "", "", "", "", "", ""]


        self.nPiles.setText("6")
        self.nVertPiles.setText("0")
        self.incl.setText("4")
        self.sdirPiles.setText("2")
        self.plen.setText("7")

        self.nMax.setText("25")
        self.nMin.setText("-1000")
        self.nFilter.setChecked(False)

        self.col_up.setText("1")
        self.col_down.setText("4")
        self.coli_box.setChecked(True)

        self.h_slab.setText("10")
        self.w_slab.setText("4")
        self.pile_dist.setText("0.8")

        self.path.setText("C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases4.xlsx")

        xvec        = [1.6, 1.6, 1.6, 1.6, 1.6, 0.8, 0.8, 0.8, 0.8, 0.8, "", "", "", "", "", "", "", "", "", ""]
        yvec        = [4.6, 3.8, 3.0, 2.2, 1.4, 4.6, 3.8, 3.0, 2.2, 1.4, "", "", "", "", "", "", "", "", "", ""]


        for i in range(len(xvec)):
            xval = QTableWidgetItem(str(xvec[i])); xval.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            yval = QTableWidgetItem(str(yvec[i])); yval.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.input_table.setItem(i,0,xval)
            self.input_table.setItem(i,1,yval)

    def read_input(self):

        npiles          = int(self.nPiles.text())
        nvert           = int(self.nVertPiles.text())
        singdir         = int(self.sdirPiles.text())
        plen            = int(self.plen.text())
        incl            = int(self.incl.text())
        path            = str(self.path.text())
        self.slab_h     = float(self.h_slab.text())
        self.slab_w     = float(self.w_slab.text())
        self.pile_d     = float(self.pile_dist.text())

        self.check_filter()

        coli_check = self.coli_box.isChecked()
        if coli_check == True:
            col_up      = int(self.col_up.text())
            col_down    = int(self.col_down.text())
            self.colision = np.arange(-col_up,col_down+1,1)
        else:
            self.colision = [0]

        self.read_pptable()

        pyfiles.PileOptModel.defineSettings(pg_data,self.xvec,self.yvec,npiles,nvert,singdir,plen,incl,path,self.NmaxLim,self.NminLim,self.pile_d)
        
        self.nr_lcs.setText(str(pg_data.nrVal))


    def read_pptable(self):
        self.xvec        = []
        self.yvec        = []
        
        for i in range(20):
            try:
                xval = float(self.input_table.item(i,0).text())
                yval = float(self.input_table.item(i,1).text())
                self.xvec.append(xval)
                self.yvec.append(yval)
            except:
                pass

    def check_filter(self):
        n_filter = self.nFilter.isChecked()

        if n_filter == True:
            self.NmaxLim        = int(self.nMax.text())
            self.NminLim        = int(self.nMin.text())
        else:
            self.NmaxLim        = 99999999999999999
            self.NminLim        = -99999999999999999
            

    def check_pplace(self):
        if pg_data.running == True:
            return
        
        self.read_pptable()

        self.pile_d     = float(self.pile_dist.text())
        ncoords         = len(self.xvec)

        Errors          = False

        # Checks in mm as int
        for i in range(ncoords):
            xstep = int(1000*self.xvec[0])-int(1000*self.xvec[i])
            ystep = int(1000*self.yvec[0])-int(1000*self.yvec[i])

            if xstep % int(1000*self.pile_d) != 0:
                print('xError, pile: ' + str(i))
                Errors = True

            if ystep % int(1000*self.pile_d) != 0:
                print('yError, pile: ' + str(i))
                Errors = True

        if Errors == False:
            self.status.setText('No errors in pile positions')
        else:
            self.status.setText('Errors detected in pile positions')
            

    def run_config(self):
        try: 
            self.read_input()
        except:
            self.status.setText('Error in input data')
            return
        self.prio = int(self.prioCombo.currentText())
        self.status.setText('Running Config analysis...')
        self.set_running_status()
        self.init_timer()

        self.worker = self.worker_config
        self.signal = Signals()
        self.threadpool = QThreadPool()
        self.threadpool.start(self.worker)

        self.progress_val = 0
        self.progress_bar.setValue(0)
        self.signal.completed.connect(self.show_config)
        self.signal.progress.connect(self.update_progress_bar)


    @Slot()
    def worker_config(self):
        pyfiles.PileOptModel.genPileConfigs(pg_data,self.colision,self.signal,self.prio)
        self.signal.completed.emit()


    def show_config(self):
        if pg_data.running == True:
            self.progress_bar.setValue(100)
            self.stop_timer()
            self.status.setText('Config analysis complete!')
            self.set_ready_status()
            self.pos_conf.setText(str(pg_data.totConfigs))
            self.tot_conf.setText(str(pg_data.nrConfigs))
            self.fil_conf.setText("-")
        


    def update_progress_bar(self):
        self.progress_val = self.progress_val + 1 
        self.progress_bar.setValue(self.progress_val)
        estimate = self.t0/(0.01*self.progress_val)
        self.estimTime.setText(str(round(estimate)))


    def run_infl(self):

        if hasattr(pg_data, 'nrConfigs') == False:
            self.status.setText('No configs found')
            return
        self.prio = int(self.prioCombo.currentText())
        self.set_running_status()

        self.configList.clear()
        self.read_input()
        self.status.setText('Running Influence analysis...')

        self.inflNmax = []
        self.inflNmin = []
        
        self.runningConfig = 0

        self.init_timer()

        self.worker     = self.worker_infl
        self.signal     = Signals()
        self.threadpool = QThreadPool()
        self.threadpool.start(self.worker)

        self.progress_val = 0
        self.progress_bar.setValue(0)

        self.signal.progress.connect(self.update_progress_bar)
        self.signal.check.connect(self.add_case_to_list)
        self.signal.completed.connect(self.infl_run_at_completion)

    def infl_run_at_completion(self):
        self.stop_timer()
        self.status.setText('Influence analysis complete!')
        self.progress_bar.setValue(100)
        self.set_ready_status()

    def init_timer(self):
        self.runningTIme.clear()
        self.estimTime.clear()
        self.timer = QTimer()
        self.t0 = 0
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self):
        self.t0 = self.t0 + 1
        self.runningTIme.setText(str(self.t0))

    def stop_timer(self):
        self.timer.stop()

    @Slot()
    def worker_infl(self):
        pyfiles.PileOptModel.pileInfluenceRun(pg_data,self.signal,self.prio)

    def pause_worker(self):
        if pg_data.running == True:
            print('Run paused...')
            pg_data.pause = True
            self.status.setText('Run paused...')
            self.timer.stop()
            self.set_paused_status()

    def resume_worker(self):
        if pg_data.running == True:
            print('Run resumed...')
            pg_data.pause = False
            self.status.setText('Run resumed!')
            self.timer.start(1000) 
            self.set_running_status()


    def stop_worker(self):
        if pg_data.running == True:
            print('Run aborted...')
            pg_data.running = False
            pg_data.pause = False
            self.status.setText('Influence analysis aborted!')
            self.timer.stop()  
            self.set_ready_status()

    def set_ready_status(self):
        self.configButton.setDisabled(False)  
        self.runButton.setDisabled(False)    
        self.pauseButton.setDisabled(True)   
        self.resumeButton.setDisabled(True)  
        self.stopButton.setDisabled(True) 
        self.singleButton.setDisabled(False) 
        self.colorButton.setDisabled(False) 
        self.write_button.setDisabled(False)
        self.draft_pplace_btn.setDisabled(False)
        self.check_pplace_btn.setDisabled(False)
        self.readState = True

    def set_running_status(self):
        self.configButton.setDisabled(True)  
        self.runButton.setDisabled(True)    
        self.pauseButton.setDisabled(False)   
        self.resumeButton.setDisabled(True)  
        self.stopButton.setDisabled(False) 
        self.singleButton.setDisabled(True) 
        self.colorButton.setDisabled(False) 
        self.write_button.setDisabled(True)
        self.draft_pplace_btn.setDisabled(True)
        self.check_pplace_btn.setDisabled(True)
        self.readState = False

    def set_paused_status(self):
        self.configButton.setDisabled(True)  
        self.runButton.setDisabled(True)    
        self.pauseButton.setDisabled(True)   
        self.resumeButton.setDisabled(False)  
        self.stopButton.setDisabled(False) 
        self.singleButton.setDisabled(True) 
        self.colorButton.setDisabled(False) 
        self.write_button.setDisabled(False)
        self.draft_pplace_btn.setDisabled(True)
        self.check_pplace_btn.setDisabled(True)
        self.readState = True

    def run_single(self):
        self.read_input()
        self.case_singlerun = int(self.currentConfigLab.text())

        pyfiles.PileOptModel.SingleRun(pg_data,self.case_singlerun)
        pyfiles.PileOptModel.returnPileGroup(pg_data)

        self.currentNmaxLab.setText(str(pg_data.nmax_single))
        self.currentNminLab.setText(str(pg_data.nmin_single))


    def update_current_config(self):
        if self.readState == True:
            rowValue = self.configList.currentItem().text().replace('Config ','')
            bpoint = rowValue.index(":")
            self.currentConfig = int(rowValue[:bpoint])

            self.set_current_config()
            self.update_pile_reaction_list()
            self.plot_config(self.currentConfig)

            if self.reaction_selection.currentText() == 'Max':
                self.reaction_plot_max()
            if self.reaction_selection.currentText() == 'Min':
                self.reaction_plot_min()
            if self.reaction_selection.currentText() == 'Nr':
                self.pilenr_plot()
    

    def set_current_config(self):

        self.currentNmax = pg_data.nMaxPileConfig[self.currentConfig]
        self.currentNmin = pg_data.nMinPileConfig[self.currentConfig]

        self.currentConfigLab.setText(str(self.currentConfig))
        self.currentNmaxLab.setText(str(round(max(self.currentNmax))))
        self.currentNminLab.setText(str(round(min(self.currentNmin))))


    def update_pile_reaction_list(self):

        self.reactionList.clear()
        for i in range(pg_data.npiles):
            self.reactionList.addItems(["Pile " + str(i+1) + ":  " + str(round(self.currentNmax[i])) + " | " + str(round(self.currentNmin[i]))])
        

    def add_case_to_list(self):

        Nmax = max(pg_data.nMaxPileConfig[self.runningConfig])
        Nmin = min(pg_data.nMinPileConfig[self.runningConfig])

        self.fil_conf.setText(str(pg_data.numberSolvedConfigs))
        self.inflNmax.append(Nmax)
        self.inflNmin.append(Nmin)

        if Nmax < self.NmaxLim and Nmin > self.NminLim:
            self.configList.addItems(["Config " + str(self.runningConfig) + ":  " + str(round(Nmax)) + " | " + str(round(Nmin))])
            self.caseNmax.setText(str(round(np.min(self.inflNmax))))
            self.caseNmin.setText(str(round(np.max(self.inflNmin))))
        
        self.runningConfig = self.runningConfig + 1

    def filter_case_list(self):
    
        inflNmax = []
        inflNmin = []

        self.configList.clear()
        self.check_filter()

        for i in range(pg_data.numberSolvedConfigs):
            Nmax = max(pg_data.nMaxPileConfig[i])
            Nmin = min(pg_data.nMinPileConfig[i])

            if Nmax < self.NmaxLim and Nmin > self.NminLim:
                inflNmax.append(Nmax)
                inflNmin.append(Nmin)
                self.configList.addItems(["Config " + str(i) + ":  " + str(round(Nmax)) + " | " + str(round(Nmin))])

        try:
            self.caseNmax.setText(str(round(min(inflNmax))))
            self.caseNmin.setText(str(round(max(inflNmin))))
        except:
            self.caseNmax.setText("-")
            self.caseNmin.setText("-")

    def reaction_plot_max(self):
        self.plot_config(self.currentConfig)
        
        for i in range(pg_data.npiles):
            colorTag = 'g'
            if self.currentNmax[i] > 0:
                colorTag = 'r'
            text = pg.TextItem(str(round(self.currentNmax[i])), color=colorTag,anchor=(0,0))
            text.setPos(pg_data.x1vec[i],pg_data.y1vec[i])
            self.view_area.addItem(text)
    
    def reaction_plot_min(self):
        self.plot_config(self.currentConfig)
        
        for i in range(pg_data.npiles):
            colorTag = 'g'
            if self.currentNmin[i] > 0:
                colorTag = 'r'
            text = pg.TextItem(str(round(self.currentNmin[i])), color=colorTag,anchor=(0,0))
            text.setPos(pg_data.x1vec[i],pg_data.y1vec[i])
            self.view_area.addItem(text)

    def pilenr_plot(self):
        self.plot_config(self.currentConfig)
        
        for i in range(pg_data.npiles):
            colorTag = 'c'
            text = pg.TextItem(str(i+1), color=colorTag,anchor=(0,0))
            text.setPos(pg_data.x1vec[i],pg_data.y1vec[i])
            self.view_area.addItem(text)

    def write_current_config(self):
        try:
            filename = str("Config " + str(self.currentConfig) + ".txt")
            f = open(filename, "w")
            f.write("dir" + "\t")
            f.write("x" + "\t")
            f.write("y" + "\t")
            f.write("y" + "\t")
            f.write("incl" + "\t")
            f.write("len" + "\t")
            f.write("\n")
            for i in range(pg_data.npiles):
                f.write(str(pg_data.bearing[i]) + "\t")
                f.write(str(pg_data.x1vec[i]) + "\t")
                f.write(str(pg_data.y1vec[i]) + "\t")
                f.write(str(0) + "\t")
                f.write(str(pg_data.incl[i]) + "\t")
                f.write(str(pg_data.pLen) + "\t")
                f.write("\n")

            self.status.setText('Current config written to file!')
            
        except:
            self.status.setText('No Configs to write...')


    def plot_config(self,nr):
        pyfiles.PileOptModel.pileExpand(pg_data,nr) 
        self.view_area.plotItem.clear()

        valrange=max(np.max(pg_data.x1vec),np.max(pg_data.y1vec),self.slab_h*0.5,self.slab_w*0.5)
        self.view_area.setXRange(-valrange,valrange, padding=0.05)
        self.view_area.setYRange(-valrange,valrange, padding=0.05)
        self.view_area.setBackground(None)

        plt = self.view_area.plotItem.plot(pg_data.x1vec,pg_data.y1vec,pen=None,symbol='o',symbolPen = self.plotpen, color=self.plotpen, symbolBrush=None)
    
        h = self.slab_h*0.5; y_draft = [h,h,-h,-h,h]
        w = self.slab_w*0.5; x_draft = [w,-w,-w,w,w]

        plt = self.view_area.plotItem.plot(x_draft,y_draft,pen=self.plotpen,symbol=None, color=self.plotpen)

        fak = 0.3

        for i in range(len(pg_data.x1vec)):

            if pg_data.incl[i] == 0:
                x2 = pg_data.x1vec[i]
                y2 = pg_data.y1vec[i]
            else:
                x2 = pg_data.x1vec[i] + np.cos(np.radians(pg_data.bearing[i]))*fak
                y2 = pg_data.y1vec[i] + np.sin(np.radians(pg_data.bearing[i]))*fak

            plt.setSymbolSize(15)
            plt = self.view_area.plotItem.plot([pg_data.x1vec[i],x2],[pg_data.y1vec[i],y2],pen=self.plotpen, color=self.plotpen)

            paxis_y = [-(self.slab_h*0.5+0.5), (self.slab_h*0.5+0.5)]
            paxis_x = [-(self.slab_w*0.5+0.5), (self.slab_w*0.5+0.5)]

            plt = self.view_area.plotItem.plot([paxis_x[0],paxis_x[1]],[0,0], pen='gray', color='gray')
            plt = self.view_area.plotItem.plot([0,0],[paxis_y[0],paxis_y[1]], pen='gray', color='gray')
        
    def draft_pplace(self):
        
        self.status.setText('Drafting possible pile positions!')
        self.read_input()
        self.view_area.plotItem.clear()

        valrange=max(np.max(self.xvec),np.max(self.yvec))
        self.view_area.setXRange(-valrange,valrange, padding=0.1)
        self.view_area.setYRange(-valrange,valrange, padding=0.1)
        self.view_area.setBackground(None)

        h = self.slab_h*0.5; y_draft = [h,h,-h,-h,h]
        w = self.slab_w*0.5; x_draft = [w,-w,-w,w,w]

        plt = self.view_area.plotItem.plot(x_draft,y_draft,pen=self.plotpen,symbol=None, color=self.plotpen)
        plt = self.view_area.plotItem.plot(self.xvec,self.yvec,pen=None,symbol="x", symbolPen=self.plotpen, color=self.plotpen, symbolBrush=self.plotpen)

        paxis_y = [-(self.slab_h*0.5+0.5), (self.slab_h*0.5+0.5)]
        paxis_x = [-(self.slab_w*0.5+0.5), (self.slab_w*0.5+0.5)]

        plt = self.view_area.plotItem.plot([paxis_x[0],paxis_x[1]],[0,0], pen='gray', color='gray')
        plt = self.view_area.plotItem.plot([0,0],[paxis_y[0],paxis_y[1]], pen='gray', color='gray')

    def swich_color_mode(self):
        self.dark_mode = not self.dark_mode
        app = QApplication.instance()
        if self.dark_mode == True:
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
            self.plotpen = 'white'
        else:
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
            self.plotpen = 'black'
        
        self.view_area.plotItem.clear()
        self.view_area.setBackground(None)
        

    def create_input_area(self):
        self.input_area     = QGroupBox()

        line_label               = QLabel("Path")
        self.path                = QLineEdit()
        nrLc_label               = QLabel("Nr LC: ")
        self.nr_lcs              = QLineEdit("-")
        self.configButton        = QPushButton("Config")                   ; self.configButton.clicked.connect(self.run_config)
        self.runButton           = QPushButton("Run")                      ; self.runButton.clicked.connect(self.run_infl)
        self.pauseButton         = QPushButton("Pause")                    ; self.pauseButton.clicked.connect(self.pause_worker)
        self.resumeButton        = QPushButton("Resume")                   ; self.resumeButton.clicked.connect(self.resume_worker)
        self.stopButton          = QPushButton("Stop")                     ; self.stopButton.clicked.connect(self.stop_worker)
        self.singleButton        = QPushButton("Single Run")               ; self.singleButton.clicked.connect(self.run_single)
        self.colorButton         = QPushButton("Colormode")                ; self.colorButton.clicked.connect(self.swich_color_mode)
        self.prioLabel           = QLabel("Priority")
        self.prioCombo           = QComboBox()                             ; self.prioCombo.addItems(["0","1","2","3"]); self.prioCombo.setCurrentIndex(2)

        layout                   = QHBoxLayout()

        layout.addWidget(line_label)
        layout.addWidget(self.path,1)
        layout.addWidget(nrLc_label)
        layout.addWidget(self.nr_lcs)
        layout.addWidget(self.configButton)
        layout.addWidget(self.runButton)
        layout.addWidget(self.pauseButton)
        layout.addWidget(self.resumeButton)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.singleButton)
        layout.addWidget(self.colorButton)
        layout.addWidget(self.prioLabel)
        layout.addWidget(self.prioCombo)

        self.configButton.setMinimumHeight(25);      self.configButton.setMinimumWidth(70)
        self.runButton.setMinimumHeight(25);         self.runButton.setMinimumWidth(70)
        self.pauseButton.setMinimumHeight(25);       self.pauseButton.setMinimumWidth(70)
        self.stopButton.setMinimumHeight(25);        self.stopButton.setMinimumWidth(70)
        self.resumeButton.setMinimumHeight(25);      self.resumeButton.setMinimumWidth(70)
        self.nr_lcs.setMinimumHeight(25);            self.nr_lcs.setMaximumWidth(35)

        self.input_area.setLayout(layout)

    def create_settings_area(self):
        self.settings_area = QGroupBox()

        layout = QGridLayout()

        layout.addWidget(QLabel("Number of piles"),0,0);            self.nPiles = QLineEdit();          layout.addWidget(self.nPiles,0,1)
        layout.addWidget(QLabel("Vertical Piles"),1,0);             self.nVertPiles = QLineEdit();      layout.addWidget(self.nVertPiles,1,1)
        layout.addWidget(QLabel("Pile inclination"),2,0);           self.incl = QLineEdit();            layout.addWidget(self.incl,2,1)

        layout.addWidget(QLabel("Single dir piles"),0,2);           self.sdirPiles = QLineEdit();       layout.addWidget(self.sdirPiles,0,3)
        layout.addWidget(QLabel("Pile lenght"),1,2);                self.plen = QLineEdit();            layout.addWidget(self.plen,1,3)

        layout.addWidget(QLabel("Max pile reaction"),0,4);          self.nMax = QLineEdit();            layout.addWidget(self.nMax,0,5)
        layout.addWidget(QLabel("Min pile reaction"),1,4);          self.nMin = QLineEdit();            layout.addWidget(self.nMin,1,5)
        layout.addWidget(QLabel("Apply reaction filter"),2,4);      self.nFilter = QCheckBox();         layout.addWidget(self.nFilter,2,5)

        layout.addWidget(QLabel("Collision check up"),0,6);         self.col_up = QLineEdit();          layout.addWidget(self.col_up,0,7)
        layout.addWidget(QLabel("Collision check down"),1,6);       self.col_down = QLineEdit();        layout.addWidget(self.col_down,1,7)
        layout.addWidget(QLabel("Apply colision check"),2,6);       self.coli_box = QCheckBox();        layout.addWidget(self.coli_box,2,7)

        layout.addWidget(QLabel("Saved Configs"),0,8);              self.tot_conf = QLineEdit("-");     layout.addWidget(self.tot_conf,0,9)
        layout.addWidget(QLabel("Possible configs"),1,8);           self.pos_conf = QLineEdit("-");     layout.addWidget(self.pos_conf,1,9)
        layout.addWidget(QLabel("Solved configs"),2,8);             self.fil_conf = QLineEdit("-");     layout.addWidget(self.fil_conf,2,9)

        layout.addWidget(QLabel("Pile Dist"),0,10);                 self.pile_dist = QLineEdit("-");    layout.addWidget(self.pile_dist,0,11)
        layout.addWidget(QLabel("Height"),1,10);                    self.h_slab = QLineEdit("-");       layout.addWidget(self.h_slab,1,11)
        layout.addWidget(QLabel("Width"),2,10);                     self.w_slab = QLineEdit("-");       layout.addWidget(self.w_slab,2,11)

        self.pos_conf.setMinimumWidth(60)
        self.nMax.setMinimumWidth(60)

        self.pos_conf.setReadOnly(True)
        self.tot_conf.setReadOnly(True)
        self.fil_conf.setReadOnly(True)
        self.nr_lcs.setReadOnly(True)

        self.settings_area.setLayout(layout)


    def create_result_area(self):
        #qdarktheme.setup_theme(corner_shape="sharp") # förmodlign inte
        #qdarktheme.setup_theme(custom_colors={"primary": "#D0BCFF"})
        self.result_area    = QGroupBox()
        result_layout       = QHBoxLayout()

        plot_layout         = QHBoxLayout()
        self.view_area      = pg.PlotWidget()

        config_area         = QGroupBox('Configurations')
        config_layout       = QVBoxLayout()
        pile_text_layout    = QGridLayout()
        self.configList     = QListWidget()
        buttonLayout        = QHBoxLayout()

        pile_area           = QGroupBox('Pile reactions')
        pile_layout         = QVBoxLayout()
        pile_react_layout   = QGridLayout()
        self.reactionList   = QListWidget()

        pplace_area         = QGroupBox('Possible pile placements')
        pplace_layout       = QVBoxLayout()
        pplace_btn_layout   = QHBoxLayout()
        self.input_table    = QTableWidget()


        # configure view areas and layouts
        self.view_area.setBackground(None)
        self.reactionList.setFixedWidth(150)
        
        self.input_table.setFixedWidth(150)
        self.input_table.setFixedWidth(150)
        self.input_table.setRowCount(20)
        self.input_table.setColumnCount(2)
        self.input_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.input_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        for i in range(20):
            self.input_table.verticalHeader().setSectionResizeMode(i,QHeaderView.Stretch)


        # Pile configures area
        self.configList.setFixedWidth(150)
        self.configList.clicked.connect(self.update_current_config)
        pile_text_layout.addWidget(QLabel("MinMax"),0,0); self.caseNmax = QLabel("0");                 pile_text_layout.addWidget(self.caseNmax,0,1);              pile_text_layout.addWidget(QLabel("kN"),0,2)
        pile_text_layout.addWidget(QLabel("MaxMin"),1,0); self.caseNmin = QLabel("0");                 pile_text_layout.addWidget(self.caseNmin,1,1);              pile_text_layout.addWidget(QLabel("kN"),1,2)
        self.filter_button = QPushButton("Filter")                            
        self.filter_button.clicked.connect(self.filter_case_list)
        self.write_button = QPushButton("Write")                            
        self.write_button.clicked.connect(self.write_current_config)
        buttonLayout.addWidget(self.filter_button)
        buttonLayout.addWidget(self.write_button)
        config_layout.addLayout(pile_text_layout)
        config_layout.addWidget(self.configList)
        config_layout.addLayout(buttonLayout)

        config_area.setLayout(config_layout)

        # Pile reactions area
        pile_react_layout.addWidget(QLabel("Case"),0,0);     self.currentConfigLab = QLabel("0");    pile_react_layout.addWidget(self.currentConfigLab,0,1)
        pile_react_layout.addWidget(QLabel("Max"),1,0);      self.currentNmaxLab = QLabel("0");      pile_react_layout.addWidget(self.currentNmaxLab,1,1);        pile_react_layout.addWidget(QLabel("kN"),1,2)
        pile_react_layout.addWidget(QLabel("Min"),2,0);      self.currentNminLab = QLabel("0");      pile_react_layout.addWidget(self.currentNminLab,2,1);        pile_react_layout.addWidget(QLabel("kN"),2,2)
        self.reaction_selection = QComboBox()
        self.reaction_selection.addItems(['None','Max','Min','Nr'])

        pile_layout.addLayout(pile_react_layout)
        pile_layout.addWidget(self.reactionList)
        plot_layout.addWidget(QLabel("Plot View"))
        plot_layout.addWidget(self.reaction_selection)
        pile_layout.addLayout(plot_layout)

        pile_area.setLayout(pile_layout)

        # Pile placement area
        self.draft_pplace_btn = QPushButton("Draft")
        self.draft_pplace_btn.clicked.connect(self.draft_pplace)
        self.check_pplace_btn = QPushButton("Check")
        self.check_pplace_btn.clicked.connect(self.check_pplace)
        pplace_btn_layout.addWidget(self.draft_pplace_btn)
        pplace_btn_layout.addWidget(self.check_pplace_btn)
        pplace_layout.addWidget(self.input_table)
        pplace_layout.addLayout(pplace_btn_layout)

        pplace_area.setLayout(pplace_layout)

        # Add view-, config-, pile-, and pplace-area to result layout
        result_layout.addWidget(self.view_area,1)
        result_layout.addWidget(config_area)
        result_layout.addWidget(pile_area)
        result_layout.addWidget(pplace_area)

        self.result_area.setLayout(result_layout)

    def create_progress_area(self):

        runningLabel            = QLabel("Running [s]: ")
        estimLabel              = QLabel("Estim [s]: ")
        statusLabel             = QLabel("Status: ")


        self.runningTIme        = QLineEdit("-");   self.runningTIme.setReadOnly(True);      self.runningTIme.setMaximumWidth(50)
        self.estimTime          = QLineEdit("-");   self.estimTime.setReadOnly(True);        self.estimTime.setMaximumWidth(50)
        self.status             = QLineEdit("");   self.status.setReadOnly(True);           self.status.setMaximumWidth(200);      self.status.setStyleSheet("color: orange; font: italic")#; self.status.setStyleSheet("font: italic")
        self.progress_area      = QGroupBox("")
        progress_layout         = QHBoxLayout()
        self.progress_bar       = QProgressBar()

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(runningLabel)
        progress_layout.addWidget(self.runningTIme)
        progress_layout.addWidget(estimLabel)
        progress_layout.addWidget(self.estimTime)
        progress_layout.addWidget(statusLabel)
        progress_layout.addWidget(self.status)
        
        self.progress_area.setLayout(progress_layout)

    def drawUI(self):
        self.dark_mode = True
        self.plotpen = 'white'
        self.create_input_area()
        self.create_settings_area()
        self.create_result_area()
        self.create_progress_area()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.input_area)
        main_layout.addWidget(self.settings_area)
        main_layout.addWidget(self.result_area,1)
        main_layout.addWidget(self.progress_area)

        mainWindow = QDialog()
        self.setLayout(main_layout)
        self.setWindowTitle("Pile Optimization")
        self.resize(1100,880)
        self.set_ready_status()


if __name__ == '__main__':
    qdarktheme.enable_hi_dpi() #Test
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))

    window = MainWindow()
    sys.exit(window.exec())


# nuitka --standalone --plugin-enable=pyside6 Main.py  
# pyinstaller --onefile Main.py