# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 09:43:51 2016

@author: tharrison

This creates a GUI that just instantiates many logFilePlots and
no experiment eagle or physics tabs. This is useful for when you just want to plot 
many logs
"""
try:
    from traits.etsconfig.api import ETSConfig
    ETSConfig.toolkit = 'qt4'
except ValueError as e:
    print "Error loading QT4. QT4 is required for Image Plot Analyser"
    print "error was: "+ str(e.message)
    pass

import traits.api as traits
import traitsui.api as traitsui
import traitsui.menu as traitsmenu
from traitsui.menu import OKButton, CancelButton

import plotObjects.logFilePlot
import plotObjects.autoRefreshDialog
import pyface
import os.path
import logging
from pyface.api import FileDialog,OK
import fastFileEditor
import csv
import pandas

from pyface.timer.api import Timer

logger = logging.getLogger("LogFilePlots.LogFilePlots")

class LogFilePlots(traits.HasTraits):
    """just a several tabbed view of several log file plot objects"""
    
    lfps = traits.List(plotObjects.logFilePlot.LogFilePlot)#list of possible fits    
    selectedLFP = traits.Instance(plotObjects.logFilePlot.LogFilePlot)
    #logFilePlotGroup = traitsui.Group(traitsui.Item("logFilePlotObject", editor = traitsui.InstanceEditor(), style="custom", show_label=False),label="Log File Plotter")
    logFilePlotsGroup = traitsui.Group(traitsui.Item('lfps',style="custom",editor=traitsui.ListEditor(use_notebook=True, deletable=True,selected="selectedLFP",export = 'DockWindowShell', page_name=".logFilePlotsTabName"),label="logFilePlots", show_label=False), springy=True)
    
    autoRefreshTimer = traits.Instance(Timer)    
    autoRefreshDialog = traits.Instance(plotObjects.autoRefreshDialog.AutoRefreshDialog)
    
    #for saving and loading
    default_directory = os.path.join('N:', os.sep, 'Data', 'eagleLogs')
    file_wildcard = traits.String("CSV Master Settings (*.csv)|All files|*")
    
    menubar = traitsmenu.MenuBar( traitsmenu.Menu(traitsui.Action(name='Add Log File Plot', action='_add_lfp'),
                                  traitsui.Action(name='Clone selected', action='_add_with_current_lfp'),
                                  traitsui.Action(name='Print current', action='_print_current'),
                                  traitsui.Action(name='Auto refresh', action='_autoRefresh_dialog'),
                                  traitsui.Action(name='Matplotlibify', action='_matplotlibify_dialog'),
                                  traitsui.Action(name='Save as', action='_save_as_settings'),
                                  traitsui.Action(name='Load as', action='_open_settings'),
                                  name="Menu"),
                                    )
    statusBarString = traits.String()
    
    traits_view = traitsui.View(logFilePlotsGroup,title = "Log File Plots",
                               statusbar = "statusBarString",icon=pyface.image_resource.ImageResource( os.path.join( 'icons', 'eagles.ico' )),
                       resizable=True, menubar=menubar)    
    
    def __init__(self, N, **traitsDict):
        """N is initial number of logFilePlots """
        super(traits.HasTraits,self).__init__(**traitsDict)
        self.lfps = [plotObjects.logFilePlot.LogFilePlot() for c in range(0,N)]
        self.selectedLFP = self.lfps[0]
        for lfp,counter in zip(self.lfps, range(0,N)):
            lfp.logFilePlotsBool=True
            lfp.logFilePlotsTabName = "log file plot "+str(counter)
            lfp.logFilePlotsReference = self
        
    def _add_lfp(self):
        """called from menu. adds a new logfileplot to list and hence to gui in case you run out """
        new = plotObjects.logFilePlot.LogFilePlot()
        new.logFilePlotsBool = True
        new.logFilePlotsReference = self
        self.lfps.append(new)
        
    def _add_with_current_lfp(self):
        """called from menu. adds a new logfileplot to list and hence to gui in case you run out """
        cloneTraits = ["logFile","mode","masterList","xAxis","yAxis","aggregateAxis","series","xLogScale","yLogScale",
                       "interpretAsTimeAxis","filterYs","filterMinYs","filterMaxYs","filterXs","filterMinXs",
                       "filterMaxXs","filterNaN","logFilePlotsBool"]
        new = self.selectedLFP.clone_traits(traits=cloneTraits,copy="deep")
        new.logFilePlotsReference = self
        new.__init__()                    
        self.lfps.append(new)
        
    def _print_current(self):
        """opens matplotlibify that allows user to save to one note or print the image """
        self.selectedLFP._savePlotButton_fired()
    
    def _autoRefresh_dialog(self):
        """when user clicks autorefresh in the menu this function calls the dialog 
        after user hits ok, it makes the choices of how to setup or stop the timer"""
        logger.info("auto refresh dialog called")
        if self.autoRefreshDialog is None:
            self.autoRefreshDialog = plotObjects.autoRefreshDialog.AutoRefreshDialog()
        self.autoRefreshDialog.configure_traits()
        logger.info("dialog edit traits finished")
        if self.autoRefreshDialog.autoRefreshBool:
            if self.autoRefreshTimer is not None:
                self.autoRefreshTimer.stop()
            self.selectedLFP.autoRefreshObject = self.autoRefreshDialog#this gives it all the info it needs
            self.autoRefreshTimer = Timer(self.autoRefreshDialog.minutes*60.0*1000.0, self.selectedLFP.autoRefresh)
            logger.info("started auto refresh timer to autorefresh")
        else:
            self.selectedLFP.autoRefreshObject = None
            logger.info("stopping auto refresh")
            if self.autoRefreshTimer is not None:
                self.autoRefreshTimer.stop()
                
    def _matplotlibify_dialog(self):
        import matplotlibify.matplotlibify
        dialog = matplotlibify.matplotlibify.Matplotlibify(logFilePlotReference =self.selectedLFP,logFilePlotsReference=self )
        dialog.configure_traits()
    
    def _save_settings(self, settingsFile):
        logger.debug("_save_settings call saving settings")
        with open(settingsFile, 'wb') as sfile:
            writer = csv.writer(sfile)
            writer.writerow([-1,'N', len(self.lfps)])
            c=0
            lfp_traits =['mode','logFilePlotBool','fitLogFileBool','autoFitWithRefresh','softRefresh',
                        'errorBarMode','logFile','xAxis' ,'yAxis','aggregateAxis','masterList','series',
                        'xLogScale','yLogScale','interpretAsTimeAxis','filterYs','filterMinYs','filterMaxYs',
                        'filterXs','filterMinXs','filterMaxXs','filterNaN','filterSpecific','filterSpecificString',
                        'filterVariableSelector','logFilePlotsBool','logFilePlotsTabName']
            
            for lfp in self.lfps:
                for trait in lfp_traits:
                    try:
                        writer.writerow([c, trait, getattr(lfp,trait), type(getattr(lfp,trait))])
                    except Exception as e:
                        logger.error( e.message)
                c+=1
            
    def _load_settings(self, settingsFile):
        load_df = pandas.read_csv(settingsFile,na_filter=False,header=None,names=['lfp_idx','variable','value','type'])
        global_settings_df = load_df[load_df['lfp_idx']==-1]
        N = int(global_settings_df[global_settings_df['variable']=='N'].value[0])
        self.__init__(N)
        for idx in range(0,N):
            df = load_df[load_df['lfp_idx']==idx]
            traits = list(df.variable.values)
            values = list(df.value.values)
            types = list(df.type.values)
            traitsDict = {trait:(value,type_val) for (trait,value,type_val) in zip(traits,values,types)}
            logger.info("loading lfp %G"%idx)
            logger.info("dictionary %s" % traitsDict)
            self.lfps[idx].load_settings(traitsDict)
            
            
    def _save_as_settings(self):
        """Called when user presses save as in Menu bar """
        dialog = FileDialog(action="save as",default_directory=self.default_directory, wildcard=self.file_wildcard)
        dialog.open()
        if dialog.return_code == OK:
            self.settingsFile = dialog.path
            if self.settingsFile[-4:]!=".csv":
                self.settingsFile+=".csv"
            self._save_settings(self.settingsFile)
            
    def _open_settings(self):
        logger.debug("_open_settings call . Opening a settings file")
        dialog = FileDialog(action="open",default_directory=self.default_directory, wildcard=self.file_wildcard)
        dialog.open()
        if dialog.return_code == OK:
            self.settingsFile = dialog.path
            self._load_settings(self.settingsFile)
            
if __name__=="__main__":
    if os.name == 'nt':
        import ctypes
        logger.debug("changing to use a seperate process (Windows 7 only)")
        gui = LogFilePlots(8)
        myappid = str(gui) # arbitrary string        
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
        except:
            logger.error("Failed to start a seperate process. This will only work on Windows 7 or later. Are you running on XP? If so everything works but can't create a new process window")
            pass
    
    gui.configure_traits()