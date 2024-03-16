import sys
import numpy as np

import qdarktheme
import pyqtgraph as pg

from PySide6.QtWidgets import QDialog,QApplication
from PySide6.QtCore import QThreadPool, Signal, Slot, QObject

from pyfiles.mixin_ui import UIMixin
from pyfiles.mixin_util import UtilMixin
from pyfiles.mixin_solver import SolverMixin


class Signals(QObject):
    completed   = Signal()
    progress    = Signal()
    stop        = Signal()
    check       = Signal()


class MainWindow(QDialog,UIMixin,UtilMixin,SolverMixin):

    def __init__(self):
        super().__init__()

        self.signal = Signals()

        self.drawUI()
        self.read_input_file(1)
        self.set_new_input()

## PILEGRID ## ------------------------------------------------------------------------------------------------------------------------------

    def draft_pilegrid(self): # Generate new pilegrid from input

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

    def remove_pilegrid(self): # Remove single pile from pilegrid

        nr = int(self.grid_remove_val.text())-1
        try:
            self.grid_remove_val.clear()
            self.xvec.pop(nr)
            self.yvec.pop(nr)
            self.status.setText('Pileposition removed')
            self.view_pilegrid()
        except: 
            self.status.setText('Error when removing pile')

    def view_pilegrid(self): # Plot current pilegrid
        
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

            
## CONFIG RUN ## ------------------------------------------------------------------------------------------------------------------------------

    def run_config(self): # Initiate config worker
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
    def worker_config(self): # Config worker
        self.genPileConfigs()
        self.signal.completed.emit()


    def show_config(self): # Config worker at completion
        if self.running == True:
            self.progress_bar.setValue(100)
            self.stop_timer()
            self.status.setText('Config analysis complete!')
            self.set_ready_status()
            self.pos_conf_line.setText(str(self.nTotCfg))
            self.tot_conf_line.setText(str(self.nSavedCfg))
            self.fil_conf_line.setText("-")
            self.pos_per_line.setText(str(self.pos_per))
            self.rot_per_line.setText(str(self.rot_per))
            self.inc_per_line.setText(str(self.inc_per))


## INFL RUN ## ------------------------------------------------------------------------------------------------------------------------------

    def run_infl(self): # Initiated influence run worker

        if hasattr(self, 'nSavedCfg') == False:
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

        self.signal     = Signals()
        self.threadpool = QThreadPool()
        self.threadpool.start(self.worker_infl)

        self.progress_val = 0
        self.progress_bar.setValue(0)

        self.signal.progress.connect(self.update_progress_bar)
        self.signal.check.connect(self.add_case_to_list)
        self.signal.completed.connect(self.infl_run_at_completion)


    @Slot()
    def worker_infl(self): # Influence worker
        self.pileInfluenceRun()


    def infl_run_at_completion(self): # At influence worker completion
        self.stop_timer()
        self.status.setText('Influence analysis complete!')
        self.progress_bar.setValue(100)
        self.set_ready_status()


## PLOT ## ------------------------------------------------------------------------------------------------------------------------------

    def show_plot_val(self): # Connected to show plot val
        self.show_plot = True
        self.update_current_config()


    def hide_plot_val(self): # Connected to hide plot val
        self.show_plot = False
        self.update_current_config()


    def update_current_config(self): # General update for selected config
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


    def plot_config(self,nr): # Plot selected pile config
        self.pileExpand(nr) 
        self.view_area.plotItem.clear()

        valrange=max(np.max(self.x1vec),np.max(self.y1vec),self.slab_h*0.5,self.slab_w*0.5)
        self.view_area.setXRange(-valrange,valrange, padding=0.05)
        self.view_area.setYRange(-valrange,valrange, padding=0.05)
        self.view_area.setBackground(None)

        plt     = self.view_area.plotItem.plot(self.x1vec,self.y1vec,pen=None,symbol='o',symbolPen = self.plotpen, color=self.plotpen, symbolBrush=None)
        h       = self.slab_h*0.5; y_draft = [h,h,-h,-h,h]
        w       = self.slab_w*0.5; x_draft = [w,-w,-w,w,w]
        plt     = self.view_area.plotItem.plot(x_draft,y_draft,pen=self.plotpen,symbol=None, color=self.plotpen)
        fak     = 0.3

        for i in range(len(self.x1vec)):

            if self.inclvek[i] == 0:
                x2 = self.x1vec[i]
                y2 = self.y1vec[i]
            else:
                x2 = self.x1vec[i] + np.cos(np.radians(self.bearing[i]))*fak
                y2 = self.y1vec[i] + np.sin(np.radians(self.bearing[i]))*fak

            plt.setSymbolSize(15)
            plt = self.view_area.plotItem.plot([self.x1vec[i],x2],[self.y1vec[i],y2],pen=self.plotpen, color=self.plotpen)

            paxis_y = [-(self.slab_h*0.5+0.5), (self.slab_h*0.5+0.5)]
            paxis_x = [-(self.slab_w*0.5+0.5), (self.slab_w*0.5+0.5)]

            plt = self.view_area.plotItem.plot([paxis_x[0],paxis_x[1]],[0,0], pen='gray', color='gray')
            plt = self.view_area.plotItem.plot([0,0],[paxis_y[0],paxis_y[1]], pen='gray', color='gray')


    def set_current_config(self): # Sets values of selected config

        self.currentNmax = self.nMaxPileConfig[self.currentConfig]
        self.currentNmin = self.nMinPileConfig[self.currentConfig]

        self.currentConfigLab.setText(str(self.currentConfig))
        self.currentNmaxLab.setText(str(round(max(self.currentNmax))))
        self.currentNminLab.setText(str(round(min(self.currentNmin))))


    def update_pile_reaction_list(self): # Updates pile reaction list for selected config
        self.reactionList.clear()
        for i in range(self.npiles_tot):
            self.reactionList.addItems(["Pile " + str(i+1) + ":  " + str(round(self.currentNmax[i])) + " | " + str(round(self.currentNmin[i]))])
        

    def add_case_to_list(self): # Adds config to configlist while running analysis 
        Nmax = max(self.nMaxPileConfig[self.runningConfig])
        Nmin = min(self.nMinPileConfig[self.runningConfig])

        self.fil_conf_line.setText(str(self.nSolvedCfg))
        self.inflNmax.append(Nmax)
        self.inflNmin.append(Nmin)

        if Nmax < self.NmaxLim and Nmin > self.NminLim:
            self.configList.addItems(["Config " + str(self.runningConfig) + ":  " + str(round(Nmax)) + " | " + str(round(Nmin))])
            self.caseNmax.setText(str(round(np.min(self.inflNmax))))
            self.caseNmin.setText(str(round(np.max(self.inflNmin))))
        self.runningConfig = self.runningConfig + 1


    def reaction_plot_max(self): # Plot max pile reaction forces over selected pile config
        self.plot_config(self.currentConfig)
        for i in range(self.npiles_tot):
            colorTag = 'g'
            if self.currentNmax[i] > 0:
                colorTag = 'r'
            text = pg.TextItem(str(round(self.currentNmax[i])), color=colorTag,anchor=(0,0))
            text.setPos(self.x1vec[i],self.y1vec[i])
            self.view_area.addItem(text)
    

    def reaction_plot_min(self): # Plot min pile reaction forces over selected pile config
        self.plot_config(self.currentConfig)
        for i in range(self.npiles_tot):
            colorTag = 'g'
            if self.currentNmin[i] > 0:
                colorTag = 'r'
            text = pg.TextItem(str(round(self.currentNmin[i])), color=colorTag,anchor=(0,0))
            text.setPos(self.x1vec[i],self.y1vec[i])
            self.view_area.addItem(text)


    def pilenr_plot(self): # Plot pile nr over selected pile config
        self.plot_config(self.currentConfig)
        for i in range(self.npiles_tot):
            colorTag = 'orange'
            text = pg.TextItem(str(i+1), color=colorTag,anchor=(0,0))
            text.setPos(self.x1vec[i],self.y1vec[i])
            self.view_area.addItem(text)

## FILTER ## ------------------------------------------------------------------------------------------------------------------------------
            
    def apply_filter(self): # Connected to apply filter button
        self.NmaxLim        = int(self.nMax.text())
        self.NminLim        = int(self.nMin.text())

        self.clear_button.setDisabled(False)
        self.filter_button.setDisabled(False)
        self.filter_case_list()


    def clear_filter(self): # Connected to clear filter button
        self.NmaxLim        = 99999999999999999
        self.NminLim        = -99999999999999999

        self.clear_button.setDisabled(True)
        self.filter_button.setDisabled(False)
        self.filter_case_list()


    def filter_case_list(self): # Filter config list based on given Nmax/Nmin
    
        inflNmax = []
        inflNmin = []
        self.configList.clear()

        for i in range(self.nSolvedCfg):
            Nmax = max(self.nMaxPileConfig[i])
            Nmin = min(self.nMinPileConfig[i])

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

## AUX METHODS ## ------------------------------------------------------------------------------------------------------------------------------

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


if __name__ == '__main__':
    qdarktheme.enable_hi_dpi() #Test
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))

    window = MainWindow()
    sys.exit(window.exec())


# nuitka --standalone --plugin-enable=pyside6 Main.py  
# pyinstaller --onefile Main.py