# -*- coding: utf-8 -*-
"""
Created on Tue Nov 01 20:13:34 2016

@author: tharrison

matplotlibify converts eagle log file plots into a python script that
generates a matplotlib plot ready for Tim's thesis!

"""

import os
import traits.api as traits
import traitsui.api as traitsui
import plotObjects.logFilePlot
import logFilePlots
import logging
import shutil

logger=logging.getLogger("LogFilePlots.Matplotlibify")

class PlotProperties(traits.HasTraits):
    """when doing a dual or later maybe multiple combined log File plots,
    there are often many parameters i want to repeat for each log file plot
    by making a class it reduce repetition in Matplotlibify"""
    logFilePlot = traits.Instance(plotObjects.logFilePlot.LogFilePlot)#gives access to most of the required attributes
    xAxisLabel = traits.String("")
    yAxisLabel = traits.String("")
    setXLimitsBool = traits.Bool(False)
    setYLimitsBool = traits.Bool(False)
    xMin = traits.Float
    xMax = traits.Float
    yMin = traits.Float
    yMax = traits.Float
    scaleXBool = traits.Bool(False)
    scaleYBool = traits.Bool(False)
    scaleX = traits.Float(1.0)    
    scaleY = traits.Float(1.0)
    offsetX = traits.Float(0.0)
    offsetY = traits.Float(0.0)
    plotFormatString = traits.String
    plotErrorBars = traits.Bool(True)
    legendReplacements = traits.Dict(key_trait=traits.String, value_trait=traits.String)
    useFitFile = traits.Bool(False, desc='select to choose a fit file to use with the same series. will draw all fits')
    fitFile = traits.File
    
    
    labelsGroup = traitsui.VGroup(traitsui.HGroup(traitsui.Item("xAxisLabel"), traitsui.Item("yAxisLabel")))
    limitsGroup = traitsui.VGroup(traitsui.Item("setXLimitsBool", label="set x limits?"),traitsui.Item("setYLimitsBool", label="set y limits?"),
                                  traitsui.HGroup(traitsui.Item("xMin", label="x min", visible_when="setXLimitsBool" ),traitsui.Item("xMax", label="x max", visible_when="setXLimitsBool"),
                                                  traitsui.Item("yMin", label="y min", visible_when="setYLimitsBool"),traitsui.Item("yMax", label="y max", visible_when="setYLimitsBool")))
    scalingGroup = traitsui.VGroup( traitsui.HGroup(traitsui.Item('scaleXBool', label='scale x?'),traitsui.Item('scaleX',visible_when="scaleXBool"),traitsui.Item('offsetX',visible_when="scaleXBool")),
                                    traitsui.HGroup(traitsui.Item('scaleYBool', label='scale y?'),traitsui.Item('scaleY',visible_when="scaleYBool"),traitsui.Item('offsetY',visible_when="scaleYBool")))
    generalGroup = traitsui.VGroup(
                                 traitsui.Item("plotErrorBars", label="show error bars:"),
                                 traitsui.Item("legendReplacements"),
                                 traitsui.Item('plotFormatString', label="format string")
                                 )
    fitGroup = traitsui.HGroup(traitsui.Item('useFitFile',label='use fit file?'),traitsui.Item('fitFile',show_label=False, visible_when='useFitFile'),visible_when='logFilePlot.fitLogFileBool')
    
    fullGroup = traitsui.VGroup(labelsGroup,limitsGroup,scalingGroup,generalGroup,fitGroup, show_border=True, label='object.logFilePlot.logFilePlotsTabName')

    traits_view = traitsui.View(fullGroup , kind='live')

    def __init__(self,logFilePlot, **traitsDict):
        self.logFilePlot=logFilePlot
        super(PlotProperties, self).__init__(**traitsDict)
    
    def _xAxisLabel_default(self):
        return self.logFilePlot.xAxis
    
    def _yAxisLabel_default(self):
        return self.logFilePlot.yAxis
        
    def _legendReplacements_default(self):
        return {_:_ for _ in self.logFilePlot.parseSeries()}
        
    def _fitFile_default(self):
        return self.logFilePlot.logFile
        
    def _plotFormatString_default(self):
        if self.logFilePlot.mode =="XY Scatter":
            return "o"
        else:
            return "-o"
            
    def _xMin_default(self):
        return self.logFilePlot.firstPlot.x_axis.mapper.range.low
    def _xMax_default(self):
        return self.logFilePlot.firstPlot.x_axis.mapper.range.high
    def _yMin_default(self):
        return self.logFilePlot.firstPlot.y_axis.mapper.range.low    
    def _yMax_default(self):
        return self.logFilePlot.firstPlot.y_axis.mapper.range.high
    
    def getFitFunction(self):
        """if fitting defined then it returns the string of the fitting function. Otherwise
        returns None"""
        if self.logFilePlot.fitLogFileBool:
            return self.logFilePlot.logFilePlotFitterReference.model
        else:
            return None
            
    def geFitFunctionSource(self, identifier=''):
        if self.logFilePlot.fitLogFileBool:
            source=self.logFilePlot.logFilePlotFitterReference.model_.definitionString
            name = (source.split('def '))[1].split('(')[0]
            if '2' in identifier:
                replacement = 'fitFunction2'
            else:
                replacement = 'fitFunction'
            return source.replace(name, replacement)
        else:
            return None
            
    def getFittedParameters(self):
        """returns a dictionary of parameter names --> fitted values  """
        if self.logFilePlot.fitLogFileBool:
            return {_.name:_.calculatedValue for _ in self.logFilePlot.logFilePlotFitterReference.parametersList }
        else:
            return None
            
    def getReplacementStringsSpecific(self, identifier = ""):
        """generates the replacement strings that are specific to a log file plot.
        indentifier is used inside key to make it unique to that lfp and should have the format
        {{lfp.mode}}. Identifier must include the . character"""
        return {'{{%smode}}'%identifier:self.logFilePlot.mode,'{{%serrorBarMode}}'%identifier:self.logFilePlot.errorBarMode,
        '{{%slogFile}}'%identifier:self.logFilePlot.logFile,'{{%sxAxis}}'%identifier:self.logFilePlot.xAxis,'{{%syAxis}}'%identifier:self.logFilePlot.yAxis,
        '{{%saggregateAxis}}'%identifier:self.logFilePlot.aggregateAxis,'{{%sseries}}'%identifier:self.logFilePlot.series,'{{%sfiterYs}}'%identifier:self.logFilePlot.filterYs,
        '{{%sfilterMinYs}}'%identifier:self.logFilePlot.filterMinYs,'{{%sfilterMaxYs}}'%identifier:self.logFilePlot.filterMaxYs,'{{%sfilterXs}}'%identifier:self.logFilePlot.filterXs,
        '{{%sfilterMinXs}}'%identifier:self.logFilePlot.filterMinXs,'{{%sfilterMaxXs}}'%identifier:self.logFilePlot.filterMaxXs,'{{%sfilterNaN}}'%identifier:self.logFilePlot.filterNaN,
        '{{%sfilterSpecific}}'%identifier:self.logFilePlot.filterSpecific,'{{%sfilterSpecificString}}'%identifier:self.logFilePlot.filterSpecificString,
        '{{%sxLogScale}}'%identifier:self.logFilePlot.xLogScale,'{{%syLogScale}}'%identifier:self.logFilePlot.yLogScale,'{{%sinterpretAsTimeAxis}}'%identifier:self.logFilePlot.interpretAsTimeAxis,
        '{{%sisFitted}}'%identifier:self.logFilePlot.fitLogFileBool,'{{%sfitFunction}}'%identifier:self.getFitFunction(), 
        '{{%sfitValues}}'%identifier:self.getFittedParameters(),'{{%sfitFunctionSource}}'%identifier:self.geFitFunctionSource(identifier),
        '{{%suseFitFile}}'%identifier:self.useFitFile,'{{%sfitFile}}'%identifier:self.fitFile,
        '{{%sxAxisLabel}}'%identifier:self.xAxisLabel , '{{%syAxisLabel}}'%identifier:self.yAxisLabel,
        '{{%slegendReplacements}}'%identifier:self.legendReplacements,
        '{{%ssetXLimitsBool}}'%identifier:self.setXLimitsBool,'{{%ssetYLimitsBool}}'%identifier:self.setYLimitsBool,
        '{{%sxlimits}}'%identifier:(self.xMin,self.xMax),'{{%sylimits}}'%identifier:(self.yMin,self.yMax), 
        '{{%sscaleXBool}}'%identifier:self.scaleXBool,'{{%sscaleYBool}}'%identifier:self.scaleYBool,
        '{{%sscaleX}}'%identifier:self.scaleX,'{{%sscaleY}}'%identifier:self.scaleY,'{{%soffsetX}}'%identifier:self.offsetX,'{{%soffsetY}}'%identifier:self.offsetY,
        '{{%splotErrorBars}}'%identifier:self.plotErrorBars,'{{%splotFormatString}}'%identifier:self.plotFormatString}

class Matplotlibify(traits.HasTraits):
    logFilePlotReference = traits.Instance(logFilePlots.plotObjects.logFilePlot.LogFilePlot)
    plotPropertiesList = traits.List(PlotProperties)
    logFilePlot1 = traits.Any()
    logFilePlot2 = traits.Any()
    logFilePlotsReference = traits.Instance(logFilePlots.LogFilePlots)#refernce to logFilePlots object
    isPriviliged = traits.Bool(False)
    hardCodeLegendBool = traits.Bool(False, desc="click if you want to write your own legend otherwise it will generate legend based on series and legend replacement dict")
    hardCodeLegendString = traits.String("", desc="comma seperated string for each legend entry")
    #xLim = traits.Tuple()
    replacementStrings = {}
    savedPrintsDirectory = traits.Directory(os.path.join("\\\\ursa","AQOGroupFolder","Experiment Humphry","Data", "savedPrints"))
    showWaterMark = traits.Bool(True)
    
    matplotlibifyMode = traits.Enum("default","dual plot")
    generatePlotScriptButton = traits.Button("generate plot")
    showPlotButton = traits.Button("show")
    #templatesFolder = os.path.join( os.path.expanduser('~'),"Google Drive","Thesis","python scripts","matplotlibify")
    templatesFolder = os.path.join("\\\\ursa","AQOGroupFolder","Experiment Humphry","Experiment Control And Software","LogFilePlots","matplotlibify","templates")
    templateFile = traits.File(os.path.join(templatesFolder,"matplotlibifyDefaultTemplate.py"))    
    generatedScriptLocation = traits.File(os.path.join(os.path.expanduser('~'),"Google Drive","Thesis","python scripts","matplotlibify", "debug.py"))
    saveToOneNote = traits.Button("Save to OneNote")
    printButton = traits.Button("print")
    dualPlotMode = traits.Enum('sharedXY','sharedX','sharedY', 'stacked','stackedX','stackedY')
    logLibrarianReference = None
    
    secondPlotGroup = traitsui.VGroup(traitsui.Item("matplotlibifyMode", label="mode"),
                                      traitsui.HGroup(traitsui.Item("logFilePlot1", visible_when="matplotlibifyMode=='dual plot'"), 
                                      traitsui.Item("logFilePlot2", visible_when="matplotlibifyMode=='dual plot'"),
                                      traitsui.Item('dualPlotMode', visible_when="matplotlibifyMode=='dual plot'",show_label=False) ),
                                      )
    plotPropertiesGroup = traitsui.Item("plotPropertiesList", editor=traitsui.ListEditor(style="custom"), show_label=False,resizable=True)    
    
    generalGroup = traitsui.VGroup(
                                 traitsui.Item("showWaterMark", label="show watermark"),
                                 traitsui.HGroup(
                                   traitsui.Item("hardCodeLegendBool",label="hard code legend?"),traitsui.Item("hardCodeLegendString", show_label=False, visible_when="hardCodeLegendBool")
                                   ),
                                 traitsui.Item("templateFile"),
                                 traitsui.Item("generatedScriptLocation", visible_when='isPriviliged'),
                                 traitsui.Item('generatePlotScriptButton', visible_when='isPriviliged'),
                                 traitsui.Item('showPlotButton'),
                                 traitsui.Item('saveToOneNote', enabled_when='True'), # was deactivated for some time, probably there was an error, I try to debug this now
                                 traitsui.Item('printButton')
                                 )
    
    traits_view = traitsui.View( secondPlotGroup,
                                 plotPropertiesGroup,
                                 generalGroup,
                                 resizable=True, kind='live')
     
    def __init__(self, **traitsDict):
        super(Matplotlibify, self).__init__(**traitsDict)        
        self.plotPropertiesList = [PlotProperties(self.logFilePlotReference)]
        self.generateReplacementStrings()
        self.add_trait("logFilePlot1",traits.Trait(self.logFilePlotReference.logFilePlotsTabName,{lfp.logFilePlotsTabName:lfp for lfp in self.logFilePlotsReference.lfps}))
        self.add_trait("logFilePlot2",traits.Trait(self.logFilePlotReference.logFilePlotsTabName,{lfp.logFilePlotsTabName:lfp for lfp in self.logFilePlotsReference.lfps}))
        
    def generateReplacementStrings(self):
        self.replacementStrings = {}
        if self.matplotlibifyMode == 'default':
            specific = self.plotPropertiesList[0].getReplacementStringsSpecific(identifier = "")
            generic = self.getGlobalReplacementStrings()
            self.replacementStrings.update(specific)
            self.replacementStrings.update(generic)

        elif self.matplotlibifyMode == 'dual plot':
            specific1 = self.plotPropertiesList[0].getReplacementStringsSpecific(identifier = "lfp1.")
            specific2 = self.plotPropertiesList[1].getReplacementStringsSpecific(identifier = "lfp2.")
            generic = self.getGlobalReplacementStrings()
            self.replacementStrings.update(specific1)
            self.replacementStrings.update(specific2)
            self.replacementStrings.update(generic)
        
        for key in self.replacementStrings.keys():#wrap strings in double quotes
            logger.info("%s = %s" % (self.replacementStrings[key],type(self.replacementStrings[key])))
            if isinstance(self.replacementStrings[key],(str,unicode)):
                if self.replacementStrings[key].startswith("def "):
                    continue#if it is a function definition then dont wrap in quotes!
                else:
                    self.replacementStrings[key] = unicode(self.wrapInQuotes(self.replacementStrings[key]))


    def getGlobalReplacementStrings(self, identifier=""):
        """generates the replacement strings that are specific to a log file plot """
        return {
        '{{%shardCodeLegendBool}}'%identifier:self.hardCodeLegendBool,'{{%shardCodeLegendString}}'%identifier:self.hardCodeLegendString,
        '{{%smatplotlibifyMode}}'%identifier:self.matplotlibifyMode,
        '{{%sshowWaterMark}}'%identifier:self.showWaterMark,
        '{{%sdualPlotMode}}'%identifier:self.dualPlotMode
        }
        
    def wrapInQuotes(self, string):
        return '"%s"' % string
    
    def _isPriviliged_default(self):
        if os.path.exists( os.path.join("C:","Users","tharrison","Google Drive","Thesis","python scripts","matplotlibify")):
            return True
        else:
            return False
        
    def _generatedScriptLocation_default(self):
        root = os.path.join("C:","Users","tharrison","Google Drive","Thesis","python scripts","matplotlibify")
        head,tail = os.path.split(self.logFilePlotReference.logFile)
        matplotlibifyName = os.path.splitext(tail)[0]+"-%s-vs-%s" % (self.plotPropertiesList[0]._yAxisLabel_default() ,self.plotPropertiesList[0]._xAxisLabel_default() )
        baseName = os.path.join(root, matplotlibifyName )
        filename = baseName+".py"
        c=0
        while os.path.exists(filename+".py"):
            filename=baseName+"-%s.py" % c
            c+=1
        return filename
    
    def replace_all(self,text, replacementDictionary):
        for placeholder, new in replacementDictionary.iteritems():
            text = text.replace(placeholder, str(new))
        return text
        
    def _generatePlotScriptButton_fired(self):
        self.writePlotScriptToFile(self.generatedScriptLocation)

    def writePlotScriptToFile(self,path):
        """writes the script that generates the plot to the path """
        logger.info("attempting to generate matplotlib script...")
        self.generateReplacementStrings()
        with open(self.templateFile, "rb") as template:
            text = self.replace_all(template.read(), self.replacementStrings)
        with open(self.generatedScriptLocation,"wb") as output:
            output.write(text)
        logger.info("succesfully generated matplotlib script at location %s "% self.generatedScriptLocation)
        
    def autoSavePlotWithMatplotlib(self, path):
        """runs the script with an appended plt.save() and plt.close("all")"""
        logger.info("attempting to save matplotlib plot...")
        self.generateReplacementStrings()
        with open(self.templateFile, "rb") as template:
            text = self.replace_all(template.read(), self.replacementStrings)
        ns = {}
        saveCode = "\n\nplt.savefig(r'%s', dpi=300)\nplt.close('all')" % path
        logger.info("executing save statement:%s" % saveCode)
        text+=saveCode
        exec text in ns
        logger.info("exec completed succesfully...")
            
    def _showPlotButton_fired(self):
        logger.info("attempting to show matplotlib plot...")
        self.generateReplacementStrings()
        with open(self.templateFile, "rb") as template:
            text = self.replace_all(template.read(), self.replacementStrings)
        ns = {}
        exec text in ns
        logger.info("exec completed succesfully...")
        
    def _saveToOneNote_fired(self):
        """calls the lfp function to save the file in the log folder and then
        save it to oneNote. THis way there is no oneNote code in matplotlibify"""
        if self.logLibrarianReference is None:
            self.logFilePlotReference.savePlotAsImage(self)
        else:
            self.logFilePlotReference.savePlotAsImage(self,self.logLibrarianReference)
        
    def _matplotlibifyMode_changed(self):
        """change default template depending on whether or not this is a double axis plot """
        if self.matplotlibifyMode == "default":
            self.templateFile = os.path.join(self.templatesFolder,"matplotlibifyDefaultTemplate.py")
            self.plotPropertiesList = [PlotProperties(self.logFilePlotReference)]
        elif self.matplotlibifyMode == "dual plot":
            self.templateFile = os.path.join(self.templatesFolder,"matplotlibifyDualPlotTemplate.py")
            if len(self.plotPropertiesList)>1:
                self.plotPropertiesList[1] = PlotProperties(self.logFilePlot2_) #or should it be logFilePlot2_???
                logger.info("chanigng second element of plot properties list")
            elif len(self.plotPropertiesList)==1:
                self.plotPropertiesList.append(PlotProperties(self.logFilePlot2_))
                logger.info("appending to plot properties list")
            else:
                logger.error("there only be 1 or 2 elements in plot properties but found %s elements" % len(self.plotPropertiesList))

    def _logFilePlot1_changed(self):
        """logFilePlot1 changed so update plotPropertiesList """
        logger.info("logFilePlot1 changed. updating plotPropertiesList")
        self.plotPropertiesList[0] =PlotProperties(self.logFilePlot1_)
    
    def _logFilePlot2_changed(self):
        logger.info("logFilePlot2 changed. updating plotPropertiesList")
        self.plotPropertiesList[1] =PlotProperties(self.logFilePlot2_)
    

    def dualPlotModeUpdates(self):
        """called when either _logFilePlot1 or _logFilePLot2 change """
        if (self.logFilePlot1_.xAxis == self.logFilePlot2_.xAxis):#Twin X 2 y axes mode
            if self.logFilePlot1_.yAxis == self.logFilePlot2_.yAxis:
                self.dualPlotMode = 'sharedXY'
            else:
                self.dualPlotMode = 'sharedX'
        elif self.logFilePlot1_.yAxis == self.logFilePlot2_.yAxis:
            self.dualPlotMode = 'sharedY'
        else:
            self.dualPlotMode = 'stacked'

    def _printButton_fired(self):
        """uses windows built in print image functionality to send png of plot to printer """
        logFolder,tail = os.path.split(self.logFilePlotReference.logFile )
        #logName = tail.strip(".csv")+" - "+str(self.selectedLFP.xAxis)+" vs "+str(self.selectedLFP.yAxis)
        imageFileName = os.path.join(logFolder, "temporary_print.png")
        self.logFilePlotReference.savePlotAsImage(self, name=imageFileName, oneNote=False)
        logger.info("attempting to use windows native printing dialog")
        os.startfile(os.path.normpath(imageFileName), "print")
        logger.info("saving to savedPrints folder")
        head,tail = os.path.split(self._generatedScriptLocation_default())
        tail=tail.replace(".py",".png")
        dst = os.path.join(self.savedPrintsDirectory,tail)
        shutil.copyfile(os.path.normpath(imageFileName),dst)
        logger.info("saved to savedPrints folder")