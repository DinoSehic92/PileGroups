import pyfiles
import sys
import numpy as np
import win32api,win32con,win32process

import qdarktheme
import pyqtgraph as pg

from PySide6.QtWidgets import ( QDialog,QApplication,QVBoxLayout,QGroupBox,QLabel,QLineEdit,QPushButton,QHBoxLayout,QGridLayout,
                                QListWidget,QTableWidget,QHeaderView,QProgressBar,QTableWidgetItem,QCheckBox, QComboBox, QSpinBox, QSpacerItem,QSizePolicy)

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
        self.set_default_input()   


    #def write_input(self):
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



    def set_default_input(self):

        self.nPiles.setValue(6)
        self.nVertPiles.setValue(0)
        self.incl_inp.setValue(4)
        self.sdirPiles.setValue(2)
        self.plen_inp.setValue(7)

        self.col_up.setValue(1)
        self.col_down.setValue(4)
        self.coli_box.setChecked(True)

        self.nMax.setText("25")
        self.nMin.setText("-1000")

        self.slab_h_inp.setText("10")
        self.slab_w_inp.setText("4")
        self.edge_d_inp.setText("0.5")

        self.p_spacing_inp.setText("0.8")
        self.p_columns_inp.setValue(2)
        self.p_rows_inp.setValue(2)

        self.path_inp.setText("C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases4.xlsx")

        self.show_plot      = False

        self.xvec           = [1.6, 1.6, 1.6, 1.6, 1.6, 0.8, 0.8, 0.8, 0.8, 0.8]
        self.yvec           = [4.6, 3.8, 3.0, 2.2, 1.4, 4.6, 3.8, 3.0, 2.2, 1.4]

        self.NmaxLim        =  99999999999999999
        self.NminLim        = -99999999999999999


    def read_input(self):

        npiles          = int(self.nPiles.text())
        nvert           = int(self.nVertPiles.text())
        singdir         = int(self.sdirPiles.text())
        plen            = int(self.plen_inp.text())
        incl            = int(self.incl_inp.text())
        path            = str(self.path_inp.text())

        self.slab_h     = float(self.slab_h_inp.text())
        self.slab_w     = float(self.slab_w_inp.text())
        self.edge_d     = float(self.edge_d_inp.text())

        self.p_spacing  = float(self.p_spacing_inp.text())
        self.p_columns  = int(self.p_columns_inp.text())
        self.p_rows     = int(self.p_rows_inp.text())

        coli_check = self.coli_box.isChecked()
        if coli_check == True:
            col_up      = int(self.col_up.text())
            col_down    = int(self.col_down.text())
            self.colision = np.arange(-col_up,col_down+1,1)
        else:
            self.colision = [0]

        self.method         = self.methodCombo.currentIndex()

        pyfiles.PileOptModel.defineSettings(pg_data,self.xvec,self.yvec,npiles,nvert,singdir,plen,incl,path,self.NmaxLim,self.NminLim,self.p_spacing)
    
        
    def draft_pilegrid(self):

        self.read_input()

        self.xvec   = []
        self.yvec   = []
        xstart      = self.slab_w*0.5 - self.edge_d
        ystart      = self.slab_h*0.5 - self.edge_d
        
        for i in range(self.p_columns):
            for j in range(self.p_rows):
                xval = xstart - i*self.p_spacing
                yval = ystart - j*self.p_spacing
                if xval > 0 and yval > 0:
                    self.xvec.append(xval)
                    self.yvec.append(yval)
                else:
                    self.status.setText('Error in pilegrid data...')
                    self.xvec = [0]
                    self.yvec = [0]
                    return
        self.status.setText('Pilegrid set')
        self.view_pilegrid()

    def remove_pilegrid(self):

        nr = int(self.grid_remove_val.text())-1
        try:
            self.grid_remove_val.clear()
            self.xvec.pop(nr)
            self.yvec.pop(nr)
            self.status.setText('Pileposition removed')
            self.view_pilegrid()
        except: 
            self.status.setText('Error when removing pile')

        

    def apply_filter(self):
        self.NmaxLim        = int(self.nMax.text())
        self.NminLim        = int(self.nMin.text())

        self.clear_button.setDisabled(False)
        self.filter_button.setDisabled(False)
        
        self.filter_case_list()


    def clear_filter(self):
        self.NmaxLim        = 99999999999999999
        self.NminLim        = -99999999999999999

        self.clear_button.setDisabled(True)
        self.filter_button.setDisabled(False)

        self.filter_case_list()
            

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
            self.pos_per.setText(str(pg_data.pos_per))
            self.rot_per.setText(str(pg_data.rot_per))
            self.inc_per.setText(str(pg_data.inc_per))
        


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
        self.write_button.setDisabled(False)
        self.grid_gen.setDisabled(False)
        self.grid_view.setDisabled(False)

    def set_running_status(self):
        self.configButton.setDisabled(True)  
        self.runButton.setDisabled(True)    
        self.pauseButton.setDisabled(False)   
        self.resumeButton.setDisabled(True)  
        self.stopButton.setDisabled(False) 
        self.write_button.setDisabled(True)
        self.grid_gen.setDisabled(True)
        self.grid_view.setDisabled(True)

    def set_paused_status(self):
        self.configButton.setDisabled(True)  
        self.runButton.setDisabled(True)    
        self.pauseButton.setDisabled(True)   
        self.resumeButton.setDisabled(False)  
        self.stopButton.setDisabled(False) 
        self.write_button.setDisabled(False)
        self.grid_gen.setDisabled(True)
        self.grid_view.setDisabled(True)

    def show_plot_val(self):
        self.show_plot = True
        self.update_current_config()

    def hide_plot_val(self):
        self.show_plot = False
        self.update_current_config()


    def update_current_config(self):
            rowValue = self.configList.currentItem().text().replace('Config ','')
            bpoint = rowValue.index(":")
            self.currentConfig = int(rowValue[:bpoint])

            self.set_current_config()
            self.update_pile_reaction_list()
            self.plot_config(self.currentConfig)

            if self.show_plot == True:
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
            colorTag = 'orange'
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

        fxfyvek = []
        fxfzvek = []
        fyfzvek = []
        mxfzvek = []
        myfzvek = []

        for lc in pg_data.lc:
            fxfyvek.append(lc[0]/lc[1])
            fxfzvek.append(lc[0]/lc[2])
            fyfzvek.append(lc[1]/lc[2])
            mxfzvek.append(lc[3]/lc[2])
            myfzvek.append(lc[4]/lc[2])

        self.fxfypos.setText(str(round(max(fxfyvek),2)))
        self.fxfyneg.setText(str(round(min(fxfyvek),2)))
        self.fxfzmax.setText(str(round(max(fxfzvek),2)))
        self.fxfzmin.setText(str(round(min(fxfzvek),2)))
        self.fyfzmax.setText(str(round(max(fyfzvek),2)))
        self.fyfzmin.setText(str(round(min(fyfzvek),2)))
        self.mxfzmax.setText(str(round(max(mxfzvek),2)))
        self.mxfzmin.setText(str(round(min(mxfzvek),2)))
        self.myfzmax.setText(str(round(max(myfzvek),2)))
        self.myfzmin.setText(str(round(min(myfzvek),2)))


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
        
    def view_pilegrid(self):
        
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

        for i in range(len(self.xvec)):
            colorTag = 'orange'
            text = pg.TextItem(str(i+1), color=colorTag,anchor=(0,0))
            text.setPos(self.xvec[i],self.yvec[i])
            self.view_area.addItem(text)

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
        area1.setMaximumWidth(550); area1.setMinimumWidth(550); area1.setMinimumHeight(100)
        layout1 = QGridLayout()

        layout1.addWidget(QLabel("Nr LC"),0,0);         self.nr_lcs         = QLabel("-");     layout1.addWidget(self.nr_lcs,0,1);          self.nr_lcs.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fz/n"),1,0);          self.pileEstimate   = QLabel("-");     layout1.addWidget(self.pileEstimate,1,1);    self.pileEstimate.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fx/Fy+"),2,0);        self.fxfypos        = QLabel("-");     layout1.addWidget(self.fxfypos,2,1);         self.fxfypos.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fx/Fy-"),3,0);        self.fxfyneg        = QLabel("-");     layout1.addWidget(self.fxfyneg,3,1);         self.fxfyneg.setMinimumWidth(40)

        layout1.addWidget(QLabel("Fx+"),0,2);           self.fxpos          = QLabel("-");     layout1.addWidget(self.fxpos,0,3);           self.fxpos.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fx-"),1,2);           self.fxneg          = QLabel("-");     layout1.addWidget(self.fxneg,1,3);           self.fxneg.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fx/Fz-"),2,2);        self.fxfzmax        = QLabel("-");     layout1.addWidget(self.fxfzmax,2,3);         self.fxfzmax.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fx/Fz-"),3,2);        self.fxfzmin        = QLabel("-");     layout1.addWidget(self.fxfzmin,3,3);         self.fxfzmin.setMinimumWidth(40)

        layout1.addWidget(QLabel("Fy+"),0,4);           self.fypos          = QLabel("-");     layout1.addWidget(self.fypos,0,5);           self.fypos.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fy-"),1,4);           self.fyneg          = QLabel("-");     layout1.addWidget(self.fyneg,1,5);           self.fyneg.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fy/Fz+"),2,4);        self.fyfzmax        = QLabel("-");     layout1.addWidget(self.fyfzmax,2,5);         self.fyfzmax.setMinimumWidth(40)
        layout1.addWidget(QLabel("Fy/Fz-"),3,4);        self.fyfzmin        = QLabel("-");     layout1.addWidget(self.fyfzmin,3,5);         self.fyfzmin.setMinimumWidth(40)
    
        layout1.addWidget(QLabel("Mx+"),0,6);           self.mxpos          = QLabel("-");     layout1.addWidget(self.mxpos,0,7);           self.mxpos.setMinimumWidth(40)
        layout1.addWidget(QLabel("Mx-"),1,6);           self.mxneg          = QLabel("-");     layout1.addWidget(self.mxneg,1,7);           self.mxneg.setMinimumWidth(40)
        layout1.addWidget(QLabel("Mx/Vz+"),2,6);        self.mxfzmax        = QLabel("-");     layout1.addWidget(self.mxfzmax,2,7);         self.mxfzmax.setMinimumWidth(40)
        layout1.addWidget(QLabel("Mx/Vz-"),3,6);        self.mxfzmin        = QLabel("-");     layout1.addWidget(self.mxfzmin,3,7);         self.mxfzmin.setMinimumWidth(40)

        layout1.addWidget(QLabel("My+"),0,8);           self.mypos          = QLabel("-");     layout1.addWidget(self.mypos,0,9);           self.mypos.setMinimumWidth(40)
        layout1.addWidget(QLabel("My-"),1,8);           self.myneg          = QLabel("-");     layout1.addWidget(self.myneg,1,9);           self.myneg.setMinimumWidth(40)
        layout1.addWidget(QLabel("My/Fz+"),2,8);        self.myfzmax        = QLabel("-");     layout1.addWidget(self.myfzmax,2,9);         self.myfzmax.setMinimumWidth(40)
        layout1.addWidget(QLabel("My/Fz-"),3,8);        self.myfzmin        = QLabel("-");     layout1.addWidget(self.myfzmin,3,9);         self.myfzmin.setMinimumWidth(40)


        area2 = QGroupBox("Run")

        layout2     = QVBoxLayout()

        buttonRow   = QHBoxLayout()
        self.lcButton            = QPushButton("Load check")               ; self.lcButton.clicked.connect(self.loadcase_analysis)
        self.configButton        = QPushButton("Config")                   ; self.configButton.clicked.connect(self.run_config)
        self.runButton           = QPushButton("Run")                      ; self.runButton.clicked.connect(self.run_infl)
        self.pauseButton         = QPushButton("Pause")                    ; self.pauseButton.clicked.connect(self.pause_worker)
        self.resumeButton        = QPushButton("Resume")                   ; self.resumeButton.clicked.connect(self.resume_worker)
        self.stopButton          = QPushButton("Stop")                     ; self.stopButton.clicked.connect(self.stop_worker)


        buttonRow.addWidget(self.lcButton)
        buttonRow.addWidget(self.configButton)
        buttonRow.addWidget(self.runButton)

        buttonRow.addWidget(self.pauseButton)
        buttonRow.addWidget(self.resumeButton)
        buttonRow.addWidget(self.stopButton)

        pathRow                 = QHBoxLayout()
        line_label              = QLabel("Path")
        self.path_inp           = QLineEdit()

        pathRow.addWidget(line_label)
        pathRow.addWidget(self.path_inp,1)

        layout2.addLayout(buttonRow)
        layout2.addLayout(pathRow)

        area1.setLayout(layout1)
        area2.setLayout(layout2)



        self.input_area.addWidget(area2)
        self.input_area.addWidget(area1)

    def create_settings_area(self):
        self.settings_area      = QHBoxLayout()

        area1                   = QGroupBox("Pile input")
        layout1                 = QGridLayout()

        layout1.addWidget(QLabel("Nr of piles"),0,0);                self.nPiles = QSpinBox();           layout1.addWidget(self.nPiles,0,1);          
        layout1.addWidget(QLabel("Nr vertical"),1,0);                self.nVertPiles = QSpinBox();       layout1.addWidget(self.nVertPiles,1,1)
        layout1.addWidget(QLabel("Inclination"),2,0);                self.incl_inp = QSpinBox();         layout1.addWidget(self.incl_inp,2,1)

        layout1.addWidget(QLabel("Nr single dir"),0,2);              self.sdirPiles = QSpinBox();        layout1.addWidget(self.sdirPiles,0,3)
        layout1.addWidget(QLabel("Pile length"),1,2);                self.plen_inp = QSpinBox();         layout1.addWidget(self.plen_inp,1,3)

        layout1.addWidget(QLabel("Collision up"),0,4);               self.col_up = QSpinBox();           layout1.addWidget(self.col_up,0,5)
        layout1.addWidget(QLabel("Collision down"),1,4);             self.col_down = QSpinBox();         layout1.addWidget(self.col_down,1,5)
        layout1.addWidget(QLabel("Apply check"),2,4);                self.coli_box = QCheckBox();        layout1.addWidget(self.coli_box,2,5)

        area2                   = QGroupBox("Slab and pilegrid input")
        layout2                 = QGridLayout()

        layout2.addWidget(QLabel("Height"),0,0);                    self.slab_h_inp = QLineEdit();       layout2.addWidget(self.slab_h_inp,0,1)      #;   self.h_slab.setMaximumWidth(40)
        layout2.addWidget(QLabel("Width"),1,0);                     self.slab_w_inp = QLineEdit();       layout2.addWidget(self.slab_w_inp,1,1)      #;   self.w_slab.setMaximumWidth(40)
        layout2.addWidget(QLabel("Edge dist"),2,0);                 self.edge_d_inp = QLineEdit();       layout2.addWidget(self.edge_d_inp,2,1)      #;   self.edge_d.setMaximumWidth(40)
##
        layout2.addWidget(QLabel("Spacing"),0,3);                   self.p_spacing_inp = QLineEdit();    layout2.addWidget(self.p_spacing_inp,0,4)   #;   self.pile_dist.setMaximumWidth(40)
        layout2.addWidget(QLabel("Rows"),1,3);                      self.p_rows_inp = QSpinBox();        layout2.addWidget(self.p_rows_inp,1,4)      #;   self.p_rows.setMaximumWidth(40)
        layout2.addWidget(QLabel("Columns"),2,3);                   self.p_columns_inp = QSpinBox();     layout2.addWidget(self.p_columns_inp,2,4)   #;   self.p_columns.setMaximumWidth(40)
        
        area4                   = QGroupBox("Configurations")
        layout4                 = QGridLayout()

        layout4.addWidget(QLabel("Possible"),0,0);                  self.pos_conf = QLineEdit("-");     layout4.addWidget(self.pos_conf,0,1)    #;   self.pos_conf.setMaximumWidth(60)
        layout4.addWidget(QLabel("Saved"),1,0);                     self.tot_conf = QLineEdit("-");     layout4.addWidget(self.tot_conf,1,1)    #;   self.tot_conf.setMaximumWidth(60)
        layout4.addWidget(QLabel("Solved"),2,0);                    self.fil_conf = QLineEdit("-");     layout4.addWidget(self.fil_conf,2,1)    #;   self.fil_conf.setMaximumWidth(60)
#
        layout4.addWidget(QLabel("Position"),0,2);                  self.pos_per = QLineEdit("-");      layout4.addWidget(self.pos_per,0,3)     #;   self.pos_per.setMaximumWidth(60)
        layout4.addWidget(QLabel("Rotation"),1,2);                  self.rot_per = QLineEdit("-");      layout4.addWidget(self.rot_per,1,3)     #;   self.rot_per.setMaximumWidth(60)
        layout4.addWidget(QLabel("Inclination"),2,2);               self.inc_per = QLineEdit("-");      layout4.addWidget(self.inc_per,2,3)     #;   self.inc_per.setMaximumWidth(60)

        area5                   = QGroupBox("Settings")
        layout5                 = QGridLayout()                

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
        self.pos_per.setReadOnly(True)
        self.rot_per.setReadOnly(True)
        self.inc_per.setReadOnly(True)

        area1.setLayout(layout1);   self.settings_area.addWidget(area1,40)
        area2.setLayout(layout2);   self.settings_area.addWidget(area2,20)
        area4.setLayout(layout4);   self.settings_area.addWidget(area4,25)
        area5.setLayout(layout5);   self.settings_area.addWidget(area5,15)


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

        aux_area            = QVBoxLayout()   
        aux_area.setAlignment(Qt.AlignTop)   

        pilegrid_area       = QGroupBox('Pile grid')        ; pilegrid_area.setFixedWidth(150); pilegrid_area.setFixedHeight(120)
        pilegrid_layout     = QVBoxLayout()
        pilegrid_sublayout  = QHBoxLayout()

        filter_area         = QGroupBox('Config filter')    ; filter_area.setFixedWidth(150); filter_area.setFixedHeight(150)
        filter_layout       = QVBoxLayout()
        filter_sublayout    = QGridLayout()
        
        plotMod_area        = QGroupBox('Plot values')      ; plotMod_area.setFixedWidth(150); plotMod_area.setFixedHeight(150)
        plotMod_layout      = QVBoxLayout()
        plotMod_sublayout   = QHBoxLayout()


        # configure view areas and layouts
        self.view_area.setBackground(None)
        self.reactionList.setFixedWidth(150)
        
        # Pile configures area
        self.configList.setFixedWidth(150)
        self.configList.clicked.connect(self.update_current_config)
        pile_text_layout.addWidget(QLabel("MinMax"),0,0); self.caseNmax = QLabel("0");                 pile_text_layout.addWidget(self.caseNmax,0,1);              pile_text_layout.addWidget(QLabel("kN"),0,2)
        pile_text_layout.addWidget(QLabel("MaxMin"),1,0); self.caseNmin = QLabel("0");                 pile_text_layout.addWidget(self.caseNmin,1,1);              pile_text_layout.addWidget(QLabel("kN"),1,2)
        config_layout.addLayout(pile_text_layout)
        config_layout.addWidget(self.configList)
        config_layout.addLayout(buttonLayout)

        config_area.setLayout(config_layout)

        # Pile reactions area
        pile_react_layout.addWidget(QLabel("Case"),0,0);     self.currentConfigLab = QLabel("0");    pile_react_layout.addWidget(self.currentConfigLab,0,1)
        pile_react_layout.addWidget(QLabel("Max"),1,0);      self.currentNmaxLab = QLabel("0");      pile_react_layout.addWidget(self.currentNmaxLab,1,1);        pile_react_layout.addWidget(QLabel("kN"),1,2)
        pile_react_layout.addWidget(QLabel("Min"),2,0);      self.currentNminLab = QLabel("0");      pile_react_layout.addWidget(self.currentNminLab,2,1);        pile_react_layout.addWidget(QLabel("kN"),2,2)

        pile_layout.addLayout(pile_react_layout)
        pile_layout.addWidget(self.reactionList)
        pile_layout.addLayout(plot_layout)

        pile_area.setLayout(pile_layout)

        # Pile grid area
        self.grid_view = QPushButton("View")
        self.grid_view.clicked.connect(self.view_pilegrid) # Show, dont modify
        self.grid_gen = QPushButton("New grid")
        self.grid_gen.clicked.connect(self.draft_pilegrid) # Generate new grid and show
        self.grid_remove = QPushButton("Remove")
        self.grid_remove.clicked.connect(self.remove_pilegrid) # Generate new grid and show
        self.grid_remove_val = QLineEdit("")

        pilegrid_sublayout.addWidget(self.grid_remove)
        pilegrid_sublayout.addWidget(self.grid_remove_val)

        pilegrid_layout.addWidget(self.grid_view,0)
        pilegrid_layout.addWidget(self.grid_gen,1)
        pilegrid_layout.addLayout(pilegrid_sublayout,2)

        # Filter area
        self.filter_button = QPushButton("Filter")                            
        self.filter_button.clicked.connect(self.apply_filter)
        self.clear_button = QPushButton("Clear")                            
        self.clear_button.clicked.connect(self.clear_filter) # upd config without filter
        self.clear_button.setDisabled(True)

        filter_sublayout.addWidget(QLabel("Max"),0,0);                       self.nMax = QLineEdit();            filter_sublayout.addWidget(self.nMax,1,0) 
        filter_sublayout.addWidget(QLabel("Min"),0,1);                       self.nMin = QLineEdit();            filter_sublayout.addWidget(self.nMin,1,1) 

        filter_layout.addLayout(filter_sublayout)
        filter_layout.addWidget(self.filter_button)
        filter_layout.addWidget(self.clear_button)


        # PlotMod area
        self.show_button = QPushButton("Show")                            
        self.show_button.clicked.connect(self.show_plot_val)
        self.hide_button = QPushButton("Hide")                            
        self.hide_button.clicked.connect(self.hide_plot_val)
        self.reaction_selection = QComboBox()
        self.reaction_selection.addItems(['Max','Min','Nr'])
        self.write_button = QPushButton("Write output")                            
        self.write_button.clicked.connect(self.write_current_config)

        plotMod_sublayout.addWidget(QLabel("Plot view"))
        plotMod_sublayout.addWidget(self.reaction_selection)

        plotMod_layout.addLayout(plotMod_sublayout)
        plotMod_layout.addWidget(self.show_button)
        plotMod_layout.addWidget(self.hide_button)
        plotMod_layout.addWidget(self.write_button)
    
        filter_area.setLayout(filter_layout)
        pilegrid_area.setLayout(pilegrid_layout)
        plotMod_area.setLayout(plotMod_layout)

        aux_area.addWidget(pilegrid_area)
        aux_area.addWidget(filter_area)
        aux_area.addWidget(plotMod_area)

        # Add view-, config-, pile-, and pplace-area to result layout
        result_layout.addWidget(self.view_area,1)
        result_layout.addWidget(config_area)
        result_layout.addWidget(pile_area)
        result_layout.addLayout(aux_area)

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