#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 15:07:12 2016

@author: tharrison
"""

try:
    from traits.etsconfig.api import ETSConfig
    ETSConfig.toolkit = 'qt4'
except ValueError as e:
    print "Error loading QT4. QT4 is required for Log File Plots"
    print "error was: "+ str(e.message)
    pass

import logging
import os
import fastFileEditor

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] [%(threadName)s] [%(name)s] [func=%(funcName)s:line=%(lineno)d] %(message)s")
#see https://docs.python.org/2/library/logging.html#logrecord-attributes for formatting options
logger=logging.getLogger("LogFilePlots")
logger.setLevel(logging.INFO)

if __file__ is None:
    logger.critical("Experiment Eagle was not able to resolve the __file__ attribute. This means it won't be able to find the config and log folders. Are you sure you are starting CSVMaster correctly? Just double click on __init__.py")

configPath = os.path.join( os.path.dirname(__file__), 'config' )
if os.path.exists( configPath ) is False:
    logger.warning("Did not find a folder called config. Attempting to create folder config.")
    # If the config directory does not exist, create it
    os.mkdir( configPath )

logPath = os.path.join( os.path.dirname(__file__), 'log' )
if os.path.exists( logPath ) is False:
    logger.warning("Did not find a folder called log. Attempting to create folder log.")
    # If the log directory does not exist, create it
    os.mkdir( logPath )

#we do not yet need logging to a file
#logFilePath = os.path.join( logPath, 'ExperimentHawk.log' )
#fileHandler = logging.FileHandler( logFilePath )
#fileHandler.setFormatter(logFormatter)
#logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

version = "4.0"
author = "Timothy Harrison"
__version__ = "4.0"
__date__= "2016-12-06"

welcomeString= """Welcome to Log File Plots version %s written by %s. Report bugs to 
%s. See text at beginning of __init__.py for more information.""" % (version, author,author)

if __name__ == '__main__':
    logger.info(welcomeString)
    consoleHandler.flush()
    
    import logFilePlots
    options_dict = {}
    lfps = logFilePlots.LogFilePlots(10)
    
    if os.name == 'nt':
        import ctypes
        logger.debug("changing to use a seperate process (Windows 7 only)")
        myappid = str(lfps) # arbitrary string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            logger.error("Failed to start a seperate process. This will only work on Windows 7 or later. Are you running on XP? If so everything works but can't create a new process window")
            pass
    lfps.configure_traits()