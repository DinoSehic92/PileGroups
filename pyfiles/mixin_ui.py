from PySide6.QtWidgets import ( QDialog,QVBoxLayout,QGroupBox,QLabel,QLineEdit,QPushButton,QHBoxLayout,QGridLayout,
                                QListWidget,QProgressBar,QCheckBox,QComboBox,QSpinBox)

from PySide6.QtCore import Qt

import pyqtgraph as pg


class UIMixin:

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
        self.configButton        = QPushButton("Config")                   ; self.configButton.clicked.connect(self.init_config_run)
        self.runButton           = QPushButton("Run")                      ; self.runButton.clicked.connect(self.init_influence_run)
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

        layout1.addWidget(QLabel("Nr of piles"),0,0);                self.nPiles_inp = QSpinBox();           layout1.addWidget(self.nPiles_inp,0,1);          
        layout1.addWidget(QLabel("Nr vertical"),1,0);                self.nVertPiles_inp = QSpinBox();       layout1.addWidget(self.nVertPiles_inp,1,1)
        layout1.addWidget(QLabel("Inclination"),2,0);                self.incl_inp = QSpinBox();         layout1.addWidget(self.incl_inp,2,1)

        layout1.addWidget(QLabel("Nr single dir"),0,2);              self.sdirPiles_inp = QSpinBox();    layout1.addWidget(self.sdirPiles_inp,0,3)
        layout1.addWidget(QLabel("Pile length"),1,2);                self.plen_inp = QSpinBox();         layout1.addWidget(self.plen_inp,1,3)

        layout1.addWidget(QLabel("Collision up"),0,4);               self.col_up_inp = QSpinBox();       layout1.addWidget(self.col_up_inp,0,5)
        layout1.addWidget(QLabel("Collision down"),1,4);             self.col_down_inp = QSpinBox();     layout1.addWidget(self.col_down_inp,1,5)
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

        layout4.addWidget(QLabel("Possible"),0,0);                  self.pos_conf_line = QLineEdit("-");     layout4.addWidget(self.pos_conf_line,0,1)    #;   self.pos_conf.setMaximumWidth(60)
        layout4.addWidget(QLabel("Saved"),1,0);                     self.tot_conf_line = QLineEdit("-");     layout4.addWidget(self.tot_conf_line,1,1)    #;   self.tot_conf.setMaximumWidth(60)
        layout4.addWidget(QLabel("Solved"),2,0);                    self.fil_conf_line = QLineEdit("-");     layout4.addWidget(self.fil_conf_line,2,1)    #;   self.fil_conf.setMaximumWidth(60)
#
        layout4.addWidget(QLabel("Position"),0,2);                  self.pos_per_line = QLineEdit("-");      layout4.addWidget(self.pos_per_line,0,3)     #;   self.pos_per.setMaximumWidth(60)
        layout4.addWidget(QLabel("Rotation"),1,2);                  self.rot_per_line = QLineEdit("-");      layout4.addWidget(self.rot_per_line,1,3)     #;   self.rot_per.setMaximumWidth(60)
        layout4.addWidget(QLabel("Inclination"),2,2);               self.inc_per_line = QLineEdit("-");      layout4.addWidget(self.inc_per_line,2,3)     #;   self.inc_per.setMaximumWidth(60)

        area5                   = QGroupBox("Settings")
        layout5                 = QGridLayout()                

        layout5.addWidget(QLabel("Solver"),0,0);                    self.methodCombo = QComboBox();     layout5.addWidget(self.methodCombo,0,1)    
        layout5.addWidget(QLabel("Priority"),1,0);                  self.prioCombo = QComboBox();       layout5.addWidget(self.prioCombo,1,1)      
        layout5.addWidget(QLabel("Theme"),2,0);                     self.themeColor = QComboBox();      layout5.addWidget(self.themeColor,2,1)     

        self.methodCombo.addItems(["FEM","PK54"]);                  self.methodCombo.setCurrentIndex(0)
        self.prioCombo.addItems(["0","1","2","3"]);                 self.prioCombo.setCurrentIndex(2) 
        self.themeColor.addItems(["Dark", "Light"]);                self.themeColor.setCurrentIndex(0)
        self.themeColor.activated.connect(self.swich_color_mode);   


        self.pos_conf_line.setReadOnly(True)
        self.tot_conf_line.setReadOnly(True)
        self.fil_conf_line.setReadOnly(True)
        self.pos_per_line.setReadOnly(True)
        self.rot_per_line.setReadOnly(True)
        self.inc_per_line.setReadOnly(True)

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

        pilegrid_area       = QGroupBox('Pile grid')            ; pilegrid_area.setFixedWidth(170)#; pilegrid_area.setFixedHeight(120)
        pilegrid_layout     = QVBoxLayout()
        pilegrid_sublayout  = QHBoxLayout()

        filter_area         = QGroupBox('Config filter')        ; filter_area.setFixedWidth(170)#; filter_area.setFixedHeight(150)
        filter_sublayout    = QGridLayout()
        
        plotMod_area        = QGroupBox('Plot values')          ; plotMod_area.setFixedWidth(170)#; plotMod_area.setFixedHeight(150)
        plotMod_layout      = QVBoxLayout()
        plotMod_sublayout   = QGridLayout()

        inputFile_area        = QGroupBox('Input file')         ; plotMod_area.setFixedWidth(170)#; plotMod_area.setFixedHeight(100)
        inputFile_layout      = QVBoxLayout()
        inputFile_sublayout1  = QHBoxLayout()

        resultFile_area        = QGroupBox('Result file')       ; plotMod_area.setFixedWidth(170)#; plotMod_area.setFixedHeight(100)
        resultFile_layout      = QVBoxLayout()
        resultFile_sublayout1  = QHBoxLayout()

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

        filter_sublayout.addWidget(QLabel("Max"),0,0);  self.nMax = QLineEdit();    filter_sublayout.addWidget(self.nMax,1,0);  filter_sublayout.addWidget(self.filter_button,2,0);   
        filter_sublayout.addWidget(QLabel("Min"),0,1);  self.nMin = QLineEdit();    filter_sublayout.addWidget(self.nMin,1,1);  filter_sublayout.addWidget(self.clear_button,2,1)  
                                                           
        # PlotMod area
        self.show_button = QPushButton("Show")                            
        self.show_button.clicked.connect(self.show_plot_val)
        self.hide_button = QPushButton("Hide")                            
        self.hide_button.clicked.connect(self.hide_plot_val)
        self.reaction_selection = QComboBox()
        self.reaction_selection.addItems(['Max','Min','Nr'])
        self.write_button = QPushButton("Write output")                            
        self.write_button.clicked.connect(self.write_current_config)

        plotMod_sublayout.addWidget(QLabel("Plot view"),0,0);   plotMod_sublayout.addWidget(self.reaction_selection,0,1)
        plotMod_sublayout.addWidget(self.show_button,1,0);      plotMod_sublayout.addWidget(self.hide_button,1,1)
        

        plotMod_layout.addLayout(plotMod_sublayout)
        plotMod_layout.addWidget(self.write_button)


        # Input File area
        self.inp_save_btn = QPushButton("Save");    self.inp_save_btn.clicked.connect(self.write_input_file)
        self.inp_load_btn = QPushButton("Load");    self.inp_load_btn.clicked.connect(self.read_input_file)
        self.inp_file_path = QLineEdit(); 

        inputFile_sublayout1.addWidget(self.inp_save_btn)
        inputFile_sublayout1.addWidget(self.inp_load_btn)
        inputFile_layout.addLayout(inputFile_sublayout1)
        inputFile_layout.addWidget(self.inp_file_path)
        inputFile_area.setLayout(inputFile_layout)

        # Result File area
        self.res_save_btn = QPushButton("Save");    self.res_save_btn.clicked.connect(self.write_result_file)
        self.res_load_btn = QPushButton("Load");    self.res_load_btn.clicked.connect(self.read_result_file)
        self.res_file_path = QLineEdit(); 

        resultFile_sublayout1.addWidget(self.res_save_btn)
        resultFile_sublayout1.addWidget(self.res_load_btn)
        resultFile_layout.addLayout(resultFile_sublayout1)
        resultFile_layout.addWidget(self.res_file_path)
        resultFile_area.setLayout(resultFile_layout)


    
        filter_area.setLayout(filter_sublayout)
        pilegrid_area.setLayout(pilegrid_layout)
        plotMod_area.setLayout(plotMod_layout)

        aux_area.addWidget(pilegrid_area,22)
        aux_area.addWidget(filter_area,20)
        aux_area.addWidget(plotMod_area,22)
        aux_area.addWidget(inputFile_area,18)
        aux_area.addWidget(resultFile_area,18)

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
        self.status             = QLineEdit("");    self.status.setReadOnly(True);           self.status.setMaximumWidth(200);      self.status.setStyleSheet("color: orange; font: italic")#; self.status.setStyleSheet("font: italic")
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

