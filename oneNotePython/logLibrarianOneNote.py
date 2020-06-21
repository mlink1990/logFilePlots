# -*- coding: utf-8 -*-
"""
Created on Sat Mar 05 17:15:06 2016

@author: tharrison
"""

import traits.api as traits
import traitsui.api as traitsui
import os
import logging
import csv
import json
import eagleLogsOneNote
import datetime

logger=logging.getLogger("LogFilePlots.logFilePlot")

class EntryBlock(traits.HasTraits):
    
    fieldName = traits.String("fieldName",desc = "describes what the information to be entered in the text block is referring to")
    textBlock = traits.String()
    
    traits_view = traitsui.View(traitsui.VGroup(
                    traitsui.Item("fieldName",show_label=False, style="readonly"),
                    traitsui.Item("textBlock",show_label=False, style="custom"),
                    show_border=True, label="information"
                        ))
    
    def __init__(self, **traitsDict):
        """user supplies arguments in init to supply class attributes defined above """
        super(EntryBlock,self).__init__(**traitsDict)
    
    def clearTextBlock(self):
        self.textBlock = ""

class AxisSelector(traits.HasTraits):
    """here we select what axes the user should use when plotting this data """
    masterList = traits.List
    masterListWithNone =  traits.List
    xAxis = traits.Enum(values="masterList")
    yAxis = traits.Enum(values="masterList")
    series = traits.Enum(values="masterListWithNone")
    
    traits_view=traitsui.View(traitsui.VGroup(traitsui.Item("xAxis",label="x axis"),traitsui.Item("yAxis",label="y axis"),
                                  traitsui.Item("series",label="series"),show_border=True, label="axes selection"))
    
    def __init__(self, **traitsDict):
        """allows user to select which axes are useful for plotting in this log"""
        super(AxisSelector, self).__init__(**traitsDict)
    
    
    def _masterList_default(self):
        """gets the header row of log file which are interpreted as the column
        names that can be plotted."""
        logger.info("updating master list of axis choices")
        logger.debug("comment file = %s" % self.logFile)
        logger.debug( "comment file = %s" % self.logFile)
        if not os.path.exists(self.logFile):
            return []
        try:
            with open(self.logFile) as csvfile:
                headerReader = csv.reader(csvfile)
                headerRow=headerReader.next()
            return headerRow
        except IOError:
            return []
            
    def _masterListWithNone_default(self):
        return ["None"]+self._masterList_default()
        

class Librarian(traits.HasTraits):
    """Librarian provides a way of writing useful information into the 
    log folder for eagle logs. It is designed to make the information inside
    an eagle log easier to come back to. It mainly writes default strings into
    the comments file in the log folder"""
    
    sectionNames =  traits.List(traits.Str)
    sectionName = traits.Enum(values="sectionNames",desc="Investigation this eagle Log is for. Corresponds to tab in OneNote")
    
    importance = traits.Range(1,3,1)
    availableUsers = traits.List(traits.Str) # loaded from json file
    user = traits.Enum(values='availableUsers')
    keywords = traits.String('')
    writeToOneNoteButton = traits.Button("save")
    refreshInformation = traits.Button("refresh")
    # saveImage = traits.Button("save plot") # removed, because there is the same functionality as the button of the Matplotlibify dialog
    axisList = AxisSelector()
    purposeBlock = EntryBlock(fieldName="What is the purpose of this log?")
    resultsBlock = EntryBlock(fieldName = "Explain what the data shows (important parameters that change, does it make sense etc.)?")
    commentsBlock = EntryBlock(fieldName = "Anything Else?")
    matplotlibifyReference = traits.Any()#
    logFilePlotReference = traits.Any()#traits.Instance(plotObjects.logFilePlot.LogFilePlot)#gives access to most of the required attributes
    logFilePlotsReference = traits.Any()#traits.Instance(logFilePlots.LogFilePlots)#refernce to logFilePlots object
#    notebooks = traits.Enum(values = "notebookNames") # we could let user select from a range of notebooks
#    notebookNames = traits.List
    notebookName = traits.String("Investigations")
    
    logName = traits.String("")
    xAxis = traits.String("")
    yAxis = traits.String("")

    traits_view = traitsui.View(
        traitsui.VGroup(
            traitsui.HGroup(traitsui.Item("sectionName",label="investigation"),traitsui.Item("user",label="user")),
            traitsui.Item("importance",label="importance",style='custom'),
            traitsui.Item("logName",show_label=False, style="readonly"),            
            traitsui.Item("keywords",label='keywords'),            
            traitsui.Item("axisList",show_label=False, editor=traitsui.InstanceEditor(),style='custom'),
            traitsui.Item("purposeBlock",show_label=False, editor=traitsui.InstanceEditor(),style='custom'),
            traitsui.Item("resultsBlock",show_label=False, editor=traitsui.InstanceEditor(),style='custom'),
            traitsui.Item("commentsBlock",show_label=False, editor=traitsui.InstanceEditor(),style='custom'),
            traitsui.Item("matplotlibifyReference",show_label=False, editor=traitsui.InstanceEditor(),style='custom'),
            traitsui.HGroup(
                # traitsui.Item("saveImage",show_label=False), # see above why commented
                traitsui.Item("writeToOneNoteButton",show_label=False),
                traitsui.Item("refreshInformation",show_label=False)
            ),
        )  , resizable=True  , kind ="live", title="Eagle OneNote", width=300, height=500
    )    
    
    def __init__(self, **traitsDict):
        """Librarian object requires the log folder it is referring to. If a .csv
        file is given as logFolder argument it will use parent folder as the 
        logFolder"""
        super(Librarian, self).__init__(**traitsDict)
        if os.path.isfile(self.logFolder):
            self.logFolder = os.path.split(self.logFolder)[0]
        else:
            logger.debug("found these in %s: %s" %(self.logFolder, os.listdir(self.logFolder) ))
        # load global settings
        filename = os.path.join("config","librarian.json")
        with open(filename, 'r') as f:
            settings = json.load( f )
            self.availableUsers = settings["users"]
        import matplotlibify.matplotlibify
        self.matplotlibifyReference = matplotlibify.matplotlibify.Matplotlibify(logFilePlotReference=self.logFilePlotReference,logFilePlotsReference=self.logFilePlotsReference, logLibrarianReference=self)
        self.matplotlibifyReference.templatesFolder = os.path.join("\\\\ursa","AQOGroupFolder","Experiment Humphry","Experiment Control And Software","LogFilePlots","matplotlibify","templates")
        self.matplotlibifyReference.templateFile = os.path.join(self.matplotlibifyReference.templatesFolder,"matplotlibifyDefaultTemplate.py")
        self.matplotlibifyReference.generatedScriptLocation = os.path.join(self.matplotlibifyReference.templatesFolder)
        self.logName = os.path.split(self.logFolder)[1]
        self.logFile = os.path.join(self.logFolder, os.path.split(self.logFolder)[1]+".csv")
        self.axisList.logFile = self.logFile#needs a copy so it can calculate valid values
        self.axisList.masterList = self.axisList._masterList_default()
        self.axisList.masterListWithNone = self.axisList._masterListWithNone_default() 
        if self.xAxis != "":
            self.axisList.xAxis = self.xAxis
        if self.yAxis != "":
            self.axisList.yAxis = self.yAxis
        
        self.eagleOneNote = eagleLogsOneNote.EagleLogOneNote(notebookName = self.notebookName, sectionName = self.sectionName)
        self.sectionNames = self._sectionNames_default()
        self.setupLogPage()

        # load local settings
        filename = os.path.join(self.logFolder,"logFilePlotSettings","librarian.json")
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                settings = json.load( f )
                self.sectionName = settings["section"]

    def setupLogPage(self):
        """setup logPage object and change text boxes in GUI accordingly """
        logPage = self.eagleOneNote.setPage(self.logName)
#        
#        except Exception as e:
#            logger.error("failed to created an EagleOneNote Instance. This could happen for many reasons. E.g. OneNote not installed or most likely, the registry is not correct. See known bug and fix in source code of onenotepython module:%s" % e.message)
        if logPage is not None:#page exists
            self.purposeBlock.textBlock = self.eagleOneNote.getOutlineText("purpose")
            self.resultsBlock.textBlock = self.eagleOneNote.getOutlineText("results")
            self.commentsBlock.textBlock = self.eagleOneNote.getOutlineText("comments")
            xAxis,yAxis,series = self.eagleOneNote.getParametersOutlineValues()
            try:
                self.axisList.xAxis,self.axisList.yAxis,self.axisList.series = xAxis,yAxis,series
            except Exception as e:
                logger.error("error when trying to read analysis parameters: %s" % e.message)
            self.pageExists = True
        else:
            self.pageExists = False
            self.purposeBlock.textBlock = ""
            self.resultsBlock.textBlock = ""
            self.commentsBlock.textBlock = ""
            #could also reset axis list but it isn't really necessary
        
    def isUserInputGood(self):
        """runs a bunch of checks and provides a warning if user has written a bad eagle log.
        Returns True if the user has written a good eagle log and false if they havent"""
        issueStrings = []
        if self.axisList.series == "None":
            issueStrings.append("You have no Series selected, are there really no series for this log? If there are multiple series note this down in the Comments box.")
        if len(self.purposeBlock.textBlock)<200:
            issueStrings.append("The purpose text of your librarian is less than 200 characters. This is too short! Describe the measurement so that you could remember what you are doing in 2 years time.")
        if len(self.resultsBlock.textBlock)<200:
            issueStrings.append("The results text of your librarian is less than 200 characters. This is too short! Describe the results so that you can understand what was learnt in 2 years time. If this doesn't need to be long why do you need to save the log?")
        numberOfIssues = len(issueStrings)
        if numberOfIssues == 0:
            return True
        else:
            finalString = "There are issues with your Eagle Log\nPlease check the below points. If you are happy to continue press OK, otherwise press cancel and correct these issues.\n"
            finalString+= "u\n\u2022".join(issueStrings)
            return traitsui.error(message=finalString)

    def _sectionNames_default(self):
        """returns the the list of section (tab) names in the oneNote """
        if hasattr(self, "eagleOneNote"):
            return self.eagleOneNote.getSectionNames()
        else:
            return ['General']
            
    def _sectionName_changed(self):
        purposeBlockTemp = self.purposeBlock
        resultsBlockTemp = self.resultsBlock
        commentsBlocktemp = self.commentsBlock
        if hasattr(self, "eagleOneNote"):
            self.eagleOneNote.sectionName=self.sectionName
            self.eagleOneNote.eagleLogPages = self.eagleOneNote.notebook.getPagesfromSectionName(self.sectionName)
            self.setupLogPage()
        self.purposeBlock = purposeBlockTemp 
        self.resultsBlock = resultsBlockTemp
        self.commentsBlock = commentsBlocktemp
    
    def _writeToOneNoteButton_fired(self):
        """writes content of librarian to one note page """
        isGoodLibrarian = self.isUserInputGood()#False and they clicked cancel so just return
        if not isGoodLibrarian:
            return
        if not self.pageExists:
            self.eagleOneNote.createNewEagleLogPage(self.logName, refresh=True, setCurrent=True)
            self.pageExists = True
        self.eagleOneNote.setOutline("purpose", self.purposeBlock.textBlock,rewrite=False)
        self.eagleOneNote.setOutline("results", self.resultsBlock.textBlock,rewrite=False)
        automatic_comments = self._generate_automatic_additional_comments()
        self.eagleOneNote.setOutline("comments", automatic_comments+self.commentsBlock.textBlock,rewrite=False)
        self.eagleOneNote.setDataOutline(self.logName, rewrite=False)
        self.eagleOneNote.setParametersOutline(self.axisList.xAxis, self.axisList.yAxis, self.axisList.series, rewrite=False)
        self.eagleOneNote.currentPage.rewritePage()
        #now to get resizing done well we want to completely repull the XML and data
        #brute force method:
        self.eagleOneNote = eagleLogsOneNote.EagleLogOneNote(notebookName = self.notebookName, sectionName = self.sectionName)
        logPage = self.eagleOneNote.setPage(self.logName)#this sets current page of eagleOneNote
        self.eagleOneNote.organiseOutlineSizes()
        self.saveLocalSettings()


    def saveImageToFile(self,name=None,oneNote=True):
        if name is None:#use automatic location
            logFolder,tail = os.path.split(self.logFile)
            #logName = tail.strip(".csv")+" - "+str(self.xAxis)+" vs "+str(self.yAxis)
            logName =str(self.xAxis)+" vs "+str(self.yAxis)
            filename = datetime.datetime.today().strftime("%Y-%m-%dT%H%M%S")+"-"+logName+".png"
            imageFileName =os.path.join(logFolder, filename)
        else:
            imageFileName = name
    
        logger.info("saving image: %s" % imageFileName)
        self.matplotlibifyReference.autoSavePlotWithMatplotlib(imageFileName)
        
        if oneNote:
            try:
                logger.info("attempting to save image to oneNote page")
                logName =  tail.replace(".csv","")#this is what the name of the page should be in oneNote
                eagleOneNote = eagleLogsOneNote.EagleLogOneNote(notebookName =self.notebookName, sectionName =self.sectionName)
                logPage = eagleOneNote.setPage(logName)
                if logPage is None:
                    logger.info("saving image to one note . page doesn't exist. creating page")
                    eagleOneNote.createNewEagleLogPage(logName, refresh=True, setCurrent=True)
                logger.debug("attempting to save image")
                eagleOneNote.addImageToPlotOutline(imageFileName, (6.3*300,3.87*300),rewrite=True)
                if self.fitLogFileBool and self.fitPlot is not None and self.logFilePlotFitterReference.isFitted:
                    #these conditions mean that we have the fit data we can write to one note with the image!
                    logger.info("also writing fit data to one note")
                    eagleOneNote.setOutline("plots", eagleOneNote.getOutlineText("plots")+self.logFilePlotFitterReference.modelFitResult.fit_report())
                eagleOneNote.currentPage.rewritePage()
                #now to get resizing done well we want to completely repull the XML and data
                #brute force method:
                eagleOneNote = eagleLogsOneNote.EagleLogOneNote(notebookName = self.notebookName, sectionName = self.sectionName)
                logPage = eagleOneNote.setPage(logName)
                eagleOneNote.organiseOutlineSizes()
            
            except Exception as e:
                logger.error("failed to save the image to OneNote. error: %s " % e.message)
    
    def _saveImage_fired(self):
        self.logFilePlotReference.savePlotAsImage(self.matplotlibifyReference,self)
        

    def _generate_automatic_additional_comments(self):
        """generates some text that is always added to the beginning of additional comments """
        return "This log was written by %s. Importance ranking is **%s**.\nKeywords: %s" % (self.user, self.importance, self.keywords)
    
    def saveLocalSettings(self):
        filename = os.path.join(self.logFolder,"logFilePlotSettings","librarian.json")
        settings = {
            "section": self.sectionName
        }
        with open(filename, 'w') as f:
            json.dump( settings, f )
        
if __name__=="__main__":
    eb = Librarian(logFolder=r"G:\Experiment Humphry\Experiment Control And Software\experimentEagle\plotObjects\testDebugLog")
    eb.configure_traits()
    