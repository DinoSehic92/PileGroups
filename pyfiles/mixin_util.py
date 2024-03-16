import numpy as np
import pickle as pkl
import pylightxl as xl

from PySide6.QtCore import QTimer

class UtilMixin:

## AUX RUN ## ------------------------------------------------------------------------------------------------------------------------------

    def update_progress_bar(self):  # Update progress bar by 1 percent
        self.progress_val = self.progress_val + 1 
        self.progress_bar.setValue(self.progress_val)
        estimate = self.t0/(0.01*self.progress_val)
        self.estimTime.setText(str(round(estimate)))

    def init_timer(self): # Starts timer 
        self.runningTIme.clear()
        self.estimTime.clear()
        self.timer = QTimer()
        self.t0 = 0
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self): # Updates value in list widget runningTime
        self.t0 = self.t0 + 1
        self.runningTIme.setText(str(self.t0))

    def stop_timer(self): # Stop timer
        self.timer.stop()

    def pause_worker(self): # Pause worker
        if self.running == True:
            print('Run paused...')
            self.pause = True
            self.status.setText('Run paused...')
            self.timer.stop()
            self.set_paused_status()

    def resume_worker(self): # Resume worker
        if self.running == True:
            print('Run resumed...')
            self.pause = False
            self.status.setText('Run resumed!')
            self.timer.start(1000) 
            self.set_running_status()

    def stop_worker(self): # Stop worker
        if self.running == True:
            print('Run aborted...')
            self.running = False
            self.pause = False
            self.status.setText('Influence analysis aborted!')
            self.timer.stop()  
            self.set_ready_status()

## INPUT ## ------------------------------------------------------------------------------------------------------------------------------

    def set_new_input(self): # Writes new input data to UI
        self.nPiles_inp.setValue(self.npiles)
        self.nVertPiles_inp.setValue(self.nvert)
        self.incl_inp.setValue(self.incl)
        self.sdirPiles_inp.setValue(self.singdir)
        self.plen_inp.setValue(self.plen)

        self.col_up_inp.setValue(self.col_up)
        self.col_down_inp.setValue(self.col_down)
        self.coli_box.setChecked(True)

        self.nMax.setText("25")
        self.nMin.setText("-1000")

        self.slab_h_inp.setText(str(self.slab_h))
        self.slab_w_inp.setText(str(self.slab_w))
        self.edge_d_inp.setText(str(self.edge_d))

        self.p_spacing_inp.setText(str(self.p_spacing))
        self.p_columns_inp.setValue(self.p_columns)
        self.p_rows_inp.setValue(self.p_rows)
        self.path_inp.setText(str(self.path))

        self.methodCombo.setCurrentIndex(1)

        self.npiles_tot     = 4*self.npiles

        self.show_plot      = False
        self.NmaxLim        =  99999999999999999
        self.NminLim        = -99999999999999999


    def read_input(self): # Reads input data from UI

        self.npiles         = int(self.nPiles_inp.text())
        self.nvert          = int(self.nVertPiles_inp.text())
        self.singdir        = int(self.sdirPiles_inp.text())
        self.plen           = int(self.plen_inp.text())
        self.incl           = int(self.incl_inp.text())
        self.path           = str(self.path_inp.text())
        self.npiles_tot     = 4*self.npiles

        self.slab_h         = float(self.slab_h_inp.text())
        self.slab_w         = float(self.slab_w_inp.text())
        self.edge_d         = float(self.edge_d_inp.text())
        self.p_spacing      = float(self.p_spacing_inp.text())
        self.p_columns      = int(self.p_columns_inp.text())
        self.p_rows         = int(self.p_rows_inp.text())

        coli_check = self.coli_box.isChecked()
        if coli_check == True:
            self.col_up     = int(self.col_up_inp.text())
            self.col_down   = int(self.col_down_inp.text())
            self.colision   = np.arange(-self.col_up,self.col_down+1,1)
        else:
            self.colision   = [0]

        self.method         = self.methodCombo.currentIndex()

    def read_loadcases(self): # Read loadcases 
        print("- Reading loadcases...")
        # Läser av excelark och genererar matris med samtliga lastfall
        wb = xl.readxl(self.path)
        sheet = wb.ws(ws='Sheet1')

        self.lc_temp =[] # Temporary list for storage before knowing number of loadcases

        for i in range(999):
            FX = sheet.index(row=4+i, col=3)
            FY = sheet.index(row=4+i, col=4)
            FZ = sheet.index(row=4+i, col=5)
            MX = sheet.index(row=4+i, col=6)
            MY = sheet.index(row=4+i, col=7)
            MZ = sheet.index(row=4+i, col=8)

            if FX != '':
                self.lc_temp.append([FX, FY, FZ, MX, MY, MZ])
            else:
                break

        self.nrVal = i

        # Consolidating list into a set size array
        self.lc = np.zeros((self.nrVal,6))
        for i in range(self.nrVal): 
            self.lc[i,:] = self.lc_temp[i]

## INPUT/RESULT FILE ## ------------------------------------------------------------------------------------------------------------------------------

    def write_input_file(self): # Write current input data to save file
        self.read_input()
        filename            = str(self.inp_file_path.text())
        self.inputPath      = str("InputFile_" + filename) + ".pkl"
        inputData           = [self.npiles, self.nvert, self.singdir, self.plen, self.incl, self.path, self.slab_h, self.slab_w, self.edge_d, self.p_spacing, self.p_columns, self.p_rows, self.colision, self.method, self.xvec, self.yvec, self.col_up, self.col_down] 

        with open(self.inputPath, "wb") as f:
            for input in inputData:
                pkl.dump(input,f)

    def read_input_file(self,mode): # Read input data save file 
        if mode == 0:
            filename            = str(self.inp_file_path.text())
            self.inputPath      = str("InputFile_" + filename) + ".pkl"

        if mode == 1:
            self.inputPath = "InputFile_startup.pkl"

        inputData           = []
        with open(self.inputPath, "rb") as f:
            for i in range(18):
                inputData.append(pkl.load(f))

        [self.npiles, self.nvert, self.singdir, self.plen, self.incl, self.path, self.slab_h, self.slab_w, self.edge_d, self.p_spacing, self.p_columns, self.p_rows, self.colision, self.method, self.xvec, self.yvec, self.col_up, self.col_down] = inputData

        self.set_new_input()

    def write_result_file(self): # Writes result save file
        filename            = str(self.res_file_path.text())
        self.inputPath      = str("OutputFile_" + filename) + ".pkl"

        inputData           = [self.npiles, self.nvert, self.singdir, self.plen, self.incl, self.path, self.slab_h, self.slab_w, self.edge_d, self.p_spacing, self.p_columns, self.p_rows, self.colision, self.method, self.xvec, self.yvec, self.col_up, self.col_down] 
        resultData          = [self.bearing_arr, self.incl_arr, self.xvec_arr, self.yvec_arr, self.nTotCfg, self.nSavedCfg, self.nSolvedCfg, self.pos_per, self.rot_per, self.inc_per, self.nMaxPileConfig, self.nMinPileConfig] 


        with open(self.inputPath, "wb") as f:

            for input in inputData:
                pkl.dump(input,f)

            for input in resultData:
                pkl.dump(input,f)

    def read_result_file(self,mode): # Reads result save file

        filename            = str(self.res_file_path.text())
        self.inputPath      = str("OutputFile_" + filename) + ".pkl"
        inputData           = []
        resultData          = []

        with open(self.inputPath, "rb") as f:
            for i in range(18):
                inputData.append(pkl.load(f))
            for i in range(12):
                resultData.append(pkl.load(f))

        [self.bearing_arr, self.incl_arr, self.xvec_arr, self.yvec_arr, self.nTotCfg, self.nSavedCfg, self.nSolvedCfg,self.pos_per, self.rot_per, self.inc_per, self.nMaxPileConfig, self.nMinPileConfig]  = resultData
        [self.npiles, self.nvert, self.singdir, self.plen, self.incl, self.path, self.slab_h, self.slab_w, self.edge_d, self.p_spacing, self.p_columns, self.p_rows, self.colision, self.method, self.xvec, self.yvec, self.col_up, self.col_down] = inputData

        self.pos_conf_line.setText(str(self.nTotCfg))
        self.tot_conf_line.setText(str(self.nSavedCfg))
        self.fil_conf_line.setText(str(self.nSolvedCfg))
        self.pos_per_line.setText(str(self.pos_per))
        self.rot_per_line.setText(str(self.rot_per))
        self.inc_per_line.setText(str(self.inc_per))

        self.status.setText('Results fetched from file ' + str(filename))

        self.set_new_input()
        self.filter_case_list()

## WRITE CONFIG ## ------------------------------------------------------------------------------------------------------------------------------

    def write_current_config(self): # Write current pile group config to txt-file
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
            for i in range(self.npiles):
                f.write(str(round(self.bearing[i],2)) + "\t")
                f.write(str(round(self.x1vec[i],2)) + "\t")
                f.write(str(round(self.y1vec[i],2)) + "\t")
                f.write(str(0) + "\t")
                f.write(str(round(self.incl[i],2)) + "\t")
                f.write(str(round(self.pLen,2)) + "\t")
                f.write("\n")

            self.status.setText('Current config written to file!')
            
        except:
            self.status.setText('No Configs to write...')

## LOADCASE ANALYSIS ## ------------------------------------------------------------------------------------------------------------------------------

    def loadcase_analysis(self): # loadcase analysis to show key values in UI
        self.read_input()
        self.read_loadcases()

        self.nr_lcs.setText(str(self.nrVal))

        val = min(self.lc[:,2])/self.npiles
        self.pileEstimate.setText(str(round(val)))

        self.fxpos.setText(str(round(max(self.lc[:,0]))))
        self.fxneg.setText(str(round(min(self.lc[:,0]))))
        self.fypos.setText(str(round(max(self.lc[:,1]))))
        self.fyneg.setText(str(round(min(self.lc[:,1]))))
        self.mxpos.setText(str(round(max(self.lc[:,3]))))
        self.mxneg.setText(str(round(min(self.lc[:,3]))))
        self.mypos.setText(str(round(max(self.lc[:,4]))))
        self.myneg.setText(str(round(min(self.lc[:,4]))))

        fxfyvek = []
        fxfzvek = []
        fyfzvek = []
        mxfzvek = []
        myfzvek = []

        for lc in self.lc:
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

## STATUS METHODS ## ------------------------------------------------------------------------------------------------------------------------------

    def set_ready_status(self): # Disables/Enables UI buttons for status Ready
        self.configButton.setDisabled(False)  
        self.runButton.setDisabled(False)    
        self.pauseButton.setDisabled(True)   
        self.resumeButton.setDisabled(True)  
        self.stopButton.setDisabled(True) 
        self.write_button.setDisabled(False)
        self.grid_gen.setDisabled(False)
        self.grid_view.setDisabled(False)
        self.grid_remove.setDisabled(False)

        self.inp_save_btn.setDisabled(False)
        self.inp_load_btn.setDisabled(False)
        self.res_save_btn.setDisabled(False)
        self.res_load_btn.setDisabled(False)

        self.show_button.setDisabled(False)
        self.hide_button.setDisabled(False)
        self.configList.setDisabled(False)

    def set_running_status(self): # Disables/Enables UI buttons for status Running
        self.configButton.setDisabled(True)  
        self.runButton.setDisabled(True)    
        self.pauseButton.setDisabled(False)   
        self.resumeButton.setDisabled(True)  
        self.stopButton.setDisabled(False) 
        self.write_button.setDisabled(True)
        self.grid_gen.setDisabled(True)
        self.grid_view.setDisabled(True)
        self.grid_remove.setDisabled(True)

        self.inp_save_btn.setDisabled(True)
        self.inp_load_btn.setDisabled(True)
        self.res_save_btn.setDisabled(True)
        self.res_load_btn.setDisabled(True)

        self.show_button.setDisabled(True)
        self.hide_button.setDisabled(True)
        self.configList.setDisabled(True)

    def set_paused_status(self): # Disables/Enables UI buttons for status Paused
        self.configButton.setDisabled(True)  
        self.runButton.setDisabled(True)    
        self.pauseButton.setDisabled(True)   
        self.resumeButton.setDisabled(False)  
        self.stopButton.setDisabled(False) 
        self.write_button.setDisabled(False)
        self.grid_gen.setDisabled(True)
        self.grid_view.setDisabled(True)
        self.grid_remove.setDisabled(True)

        self.inp_save_btn.setDisabled(True)
        self.inp_load_btn.setDisabled(True)
        self.res_save_btn.setDisabled(True)
        self.res_load_btn.setDisabled(True)

        self.show_button.setDisabled(False)
        self.hide_button.setDisabled(False)
        self.configList.setDisabled(False)