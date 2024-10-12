import logging

from knowledge_enum import DebugLevels

def permissive_noop(*args, **kwargs):
    pass

class KnowledgeLogger():
    def __init__(self, debugLevel, logFile):
        self.logger = logging.getLogger('KnowledgeLogger')
        self.logger.setLevel(logging.DEBUG)

        # Pass-through calls
        passthrough_names = ['debug','info','warning','error','critical']
        for func in passthrough_names:
            setattr(self, func, getattr(self.logger, func))
        if debugLevel == DebugLevels.OFF:
            # Disable EVERYTHING and return
            self.logger._srcfile = None
            logging.logThreads = False
            logging.logProcesses = False
            logging.logMultiprocessing = False
            logging.logAsyncioTasks = False
            self.logger.addHandler(logging.NullHandler())
            return

        # Custom formatter to add to handles
        fileHandler = logging.FileHandler(logFile)
        consoleHandler = logging.StreamHandler()
        logFormat = logging.Formatter('[%(asctime)s] [%(name)s; %(levelname)s] %(filename)s:%(funcName)s() @ Line %(lineno)d: %(message)s')
        fileHandler.setFormatter(logFormat)
        fileHandler.setLevel(logging.INFO)

        match debugLevel:
            case DebugLevels.LOGGED:
                # We rely on the logfile for information, console should
                # receive uncaught Exceptions or Warnings rather than log
                # notices
                consoleFormat = logging.Formatter('%(filename)s:%(funcName)s() @ Line %(lineno)d: %(message)s')
                consoleHandler.setLevel(logging.CRITICAL)
            case DebugLevels.DEBUG:
                # Witness logs on the console as well
                consoleFormat = logging.Formatter('[%(name)s; %(levelname)s] %(filename)s:%(funcName)s() @ Line %(lineno)d: %(message)s')
                consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(consoleFormat)

        self.logger.addHandler(fileHandler)
        self.logger.addHandler(consoleHandler)

