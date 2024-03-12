import pyfiles
import sys
import numpy as np
import win32api,win32con,win32process

import qdarktheme
import pyqtgraph as pg

from PySide6.QtWidgets import ( QDialog,QApplication,QVBoxLayout,QGroupBox,QLabel,QLineEdit,QPushButton,QHBoxLayout,QGridLayout,
                                QListWidget,QTableWidget,QHeaderView,QProgressBar,QTableWidgetItem,QCheckBox, QComboBox, QSpinBox)

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
        #Test
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


        self.nPiles.setValue(6)
        self.nVertPiles.setValue(0)
        self.incl.setValue(4)
        self.sdirPiles.setValue(2)
        self.plen.setValue(7)

        self.col_up.setValue(1)
        self.col_down.setValue(4)
        self.coli_box.setChecked(True)

        self.nMax.setText("25")
        self.nMin.setText("-1000")
        self.nFilter.setChecked(False)

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
        
        self.method = self.methodCombo.currentIndex()


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
        pyfiles.PileOptModel.pileInfluenceRun(pg_data,self.signal,self.prio,self.method)

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

    def loadcase_analysis(self):
        self.read_input()
        self.nr_lcs.setText(str(pg_data.nrVal))

        val = min(pg_data.lc[:,2])/pg_data.npiles
        self.pileEstimate.setText(str(round(val)))

        self.fxpos.setText(str(round(max(pg_data.lc[:,0]))))
        self.fxneg.setText(str(round(min(pg_data.lc[:,0]))))
        self.fypos.setText(str(round(max(pg_data.lc[:,1]))))
        self.fyneg.setText(str(round(min(pg_data.lc[:,1]))))

        self.mxpos.setText(str(round(max(pg_data.lc[:,3]))))
        self.mxneg.setText(str(round(min(pg_data.lc[:,3]))))
        self.mypos.setText(str(round(max(pg_data.lc[:,4]))))
        self.myneg.setText(str(round(min(pg_data.lc[:,4]))))



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
        
        colormode = self.themeColor.currentIndex()
        if colormode == 0: 
            self.dark_mode == True
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
            self.plotpen = 'white'
        if colormode == 1:
            self.dark_mode == False
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
            self.plotpen = 'black'
        
        self.view_area.plotItem.clear()
        self.view_area.setBackground(None)
        

    def create_input_area(self):
        self.input_area     = QHBoxLayout()

        area1 = QGroupBox("LC analysis")
        area1.setMaximumWidth(400); area1.setMinimumHeight(100)
        layout1 = QGridLayout()

        layout1.addWidget(QLabel("Nr LC"),0,0);         self.nr_lcs         = QLabel("-");     layout1.addWidget(self.nr_lcs,0,1);          self.nr_lcs.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fz/n"),1,0);          self.pileEstimate   = QLabel("-");     layout1.addWidget(self.pileEstimate,1,1);    self.pileEstimate.setMinimumWidth(40)

        layout1.addWidget(QLabel("Fx+"),0,2);           self.fxpos          = QLabel("-");     layout1.addWidget(self.fxpos,0,3);           self.fxpos.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fx-"),1,2);           self.fxneg          = QLabel("-");     layout1.addWidget(self.fxneg,1,3);           self.fxneg.setMinimumWidth(40)

        layout1.addWidget(QLabel("Fy+"),0,4);           self.fypos          = QLabel("-");     layout1.addWidget(self.fypos,0,5);           self.fypos.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fy-"),1,4);           self.fyneg          = QLabel("-");     layout1.addWidget(self.fyneg,1,5);           self.fyneg.setMinimumWidth(40)
    
        layout1.addWidget(QLabel("Mx+"),0,6);           self.mxpos          = QLabel("-");     layout1.addWidget(self.mxpos,0,7);           self.mxpos.setMinimumWidth(40)
        layout1.addWidget(QLabel("Mx-"),1,6);           self.mxneg          = QLabel("-");     layout1.addWidget(self.mxneg,1,7);           self.mxneg.setMinimumWidth(40)
    
        layout1.addWidget(QLabel("My+"),0,8);           self.mypos          = QLabel("-");     layout1.addWidget(self.mypos,0,9);           self.mypos.setMinimumWidth(40)
        layout1.addWidget(QLabel("My-"),1,8);           self.myneg          = QLabel("-");     layout1.addWidget(self.myneg,1,9);           self.myneg.setMinimumWidth(40)

        area2 = QGroupBox("Run")

        layout2     = QVBoxLayout()

        buttonRow   = QHBoxLayout()
        self.lcButton            = QPushButton("LC Analysis")              ; self.lcButton.clicked.connect(self.loadcase_analysis)
        self.configButton        = QPushButton("Config")                   ; self.configButton.clicked.connect(self.run_config)
        self.runButton           = QPushButton("Run")                      ; self.runButton.clicked.connect(self.run_infl)
        self.pauseButton         = QPushButton("Pause")                    ; self.pauseButton.clicked.connect(self.pause_worker)
        self.resumeButton        = QPushButton("Resume")                   ; self.resumeButton.clicked.connect(self.resume_worker)
        self.stopButton          = QPushButton("Stop")                     ; self.stopButton.clicked.connect(self.stop_worker)
        self.singleButton        = QPushButton("Single Run")               ; self.singleButton.clicked.connect(self.run_single)


        buttonRow.addWidget(self.lcButton)
        buttonRow.addWidget(self.configButton)
        buttonRow.addWidget(self.runButton)

        buttonRow.addWidget(self.pauseButton)
        buttonRow.addWidget(self.resumeButton)
        buttonRow.addWidget(self.stopButton)
        buttonRow.addWidget(self.singleButton)

        pathRow     = QHBoxLayout()
        
        line_label               = QLabel("Path")
        self.path                = QLineEdit()

        pathRow.addWidget(line_label)
        pathRow.addWidget(self.path,1)

        layout2.addLayout(buttonRow)
        layout2.addLayout(pathRow)

        area1.setLayout(layout1)
        area2.setLayout(layout2)



        self.input_area.addWidget(area2)
        self.input_area.addWidget(area1)

    def create_settings_area(self):
        self.settings_area = QHBoxLayout()

        area1   = QGroupBox("Pile input")
        area1.setMaximumWidth(400)
        layout1 = QGridLayout()

        layout1.addWidget(QLabel("Nr of piles"),0,0);                self.nPiles = QSpinBox();           layout1.addWidget(self.nPiles,0,1);          
        layout1.addWidget(QLabel("Nr vertical"),1,0);                self.nVertPiles = QSpinBox();       layout1.addWidget(self.nVertPiles,1,1)
        layout1.addWidget(QLabel("Inclination"),2,0);                self.incl = QSpinBox();             layout1.addWidget(self.incl,2,1)

        layout1.addWidget(QLabel("Nr single dir"),0,2);              self.sdirPiles = QSpinBox();        layout1.addWidget(self.sdirPiles,0,3)
        layout1.addWidget(QLabel("Pile length"),1,2);                self.plen = QSpinBox();             layout1.addWidget(self.plen,1,3)

        layout1.addWidget(QLabel("Collision up"),0,4);               self.col_up = QSpinBox();           layout1.addWidget(self.col_up,0,5)
        layout1.addWidget(QLabel("Collision down"),1,4);             self.col_down = QSpinBox();         layout1.addWidget(self.col_down,1,5)
        layout1.addWidget(QLabel("Apply check"),2,4);                self.coli_box = QCheckBox();        layout1.addWidget(self.coli_box,2,5)

        area2   = QGroupBox("Slab and pilegrid input")
        layout2 = QGridLayout()

        layout2.addWidget(QLabel("Height"),0,0);                    self.h_slab = QLineEdit("-");       layout2.addWidget(self.h_slab,0,1)      ;   self.h_slab.setMaximumWidth(40)
        layout2.addWidget(QLabel("Width"),1,0);                     self.w_slab = QLineEdit("-");       layout2.addWidget(self.w_slab,1,1)      ;   self.w_slab.setMaximumWidth(40)
        layout2.addWidget(QLabel("Edge dist"),2,0);                 self.edge_d = QLineEdit("-");       layout2.addWidget(self.edge_d,2,1)      ;   self.edge_d.setMaximumWidth(40)

        layout2.addWidget(QLabel("Spacing"),0,3);                   self.pile_dist = QLineEdit("-");    layout2.addWidget(self.pile_dist,0,4)   ;   self.pile_dist.setMaximumWidth(40)
        layout2.addWidget(QLabel("Rows"),1,3);                      self.p_rows = QLineEdit("-");       layout2.addWidget(self.p_rows,1,4)      ;   self.p_rows.setMaximumWidth(40)
        layout2.addWidget(QLabel("Columns"),2,3);                   self.p_columns = QLineEdit("-");    layout2.addWidget(self.p_columns,2,4)   ;   self.p_columns.setMaximumWidth(40)

        area3   = QGroupBox("Reaction filter")
        layout3 = QGridLayout()

        layout3.addWidget(QLabel("Max"),0,0);                       self.nMax = QLineEdit();            layout3.addWidget(self.nMax,0,1)        ;    self.nMax.setMaximumWidth(60)
        layout3.addWidget(QLabel("Min"),1,0);                       self.nMin = QLineEdit();            layout3.addWidget(self.nMin,1,1)        ;    self.nMin.setMaximumWidth(60)
        layout3.addWidget(QLabel("Apply"),2,0);                     self.nFilter = QCheckBox();         layout3.addWidget(self.nFilter,2,1) 
        
        area4   = QGroupBox("Configurations")
        layout4 = QGridLayout()

        layout4.addWidget(QLabel("Possible"),0,0);                  self.pos_conf = QLineEdit("-");     layout4.addWidget(self.pos_conf,0,1)
        layout4.addWidget(QLabel("Saved"),1,0);                     self.tot_conf = QLineEdit("-");     layout4.addWidget(self.tot_conf,1,1)
        layout4.addWidget(QLabel("Solved"),2,0);                    self.fil_conf = QLineEdit("-");     layout4.addWidget(self.fil_conf,2,1)

        area5   = QGroupBox("Settings")
        layout5 = QGridLayout()                

        layout5.addWidget(QLabel("Solver"),0,0);                    self.methodCombo = QComboBox();     layout5.addWidget(self.methodCombo,0,1)
        layout5.addWidget(QLabel("Priority"),1,0);                  self.prioCombo = QComboBox();       layout5.addWidget(self.prioCombo,1,1)
        layout5.addWidget(QLabel("Theme"),2,0);                     self.themeColor = QComboBox();      layout5.addWidget(self.themeColor,2,1)

        self.methodCombo.addItems(["FEM","PK54"]);                  self.methodCombo.setCurrentIndex(0)
        self.prioCombo.addItems(["0","1","2","3"]);                 self.prioCombo.setCurrentIndex(2) 

        self.themeColor.addItems(["Dark", "Light"]);                self.themeColor.setCurrentIndex(0)
        self.themeColor.activated.connect(self.swich_color_mode);   


        self.pos_conf.setReadOnly(True)
        self.tot_conf.setReadOnly(True)
        self.fil_conf.setReadOnly(True)

        area1.setLayout(layout1);   self.settings_area.addWidget(area1)
        area2.setLayout(layout2);   self.settings_area.addWidget(area2)
        area3.setLayout(layout3);   self.settings_area.addWidget(area3)
        area4.setLayout(layout4);   self.settings_area.addWidget(area4,1)
        area5.setLayout(layout5);   self.settings_area.addWidget(area5,1)


    def create_result_area(self):

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
        self.progress_area      = QGroupBox("Progress")
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
        main_layout.addLayout(self.input_area)
        main_layout.addLayout(self.settings_area)
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