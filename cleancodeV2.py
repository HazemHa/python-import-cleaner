from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional
import os
import re
import subprocess
from pathlib import Path
import fileinput


class Handler(ABC):
    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, request) -> Optional[str]:
        pass


class AbstractHandler(Handler):

    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        # Returning a handler from here will let us link handlers in a
        # convenient way like this:
        # monkey.set_next(squirrel).set_next(dog)
        return handler

    @abstractmethod
    def handle(self, request: Any) -> str:
        if self._next_handler:
            return self._next_handler.handle(request)

        return None


class DebugHandler(AbstractHandler):
    DebugLevel = False

    def handle(self, request: Any) -> str:
        if("Traceback" in str(request)):
            self.DebugLevel = True
        if(self.DebugLevel):
            result = super().handle(request)
            if(result):
                # we save the excpetion in full cache and handle it.
                # TRUE -> COMPLETE
                # ERROR -> UN-COMPLETE
                self.DebugLevel = False
                return True


class FileAndLineFinder(AbstractHandler):
    cache = []

    def handle(self, request: Any) -> str:
        # here the flag where you can know the end of error message it's depend on the programming lanague or the Exception
        if("Error" in str(request)):
            return super().handle(self.cache)
        else:
            self.cache.append(request)


class ErrorFinder(AbstractHandler):
    def handle(self, request: Any) -> str:
        if(len(request) > 0):
            importError = request[-1].decode()
            fileANdLinePathError = request[-2].decode()
            return super().handle([importError, fileANdLinePathError])
        else:
            print("the cache is empty , Please check the flag of end of Exception")
            return False


class RegexHandler(AbstractHandler):
    def handle(self, request: Any) -> str:

        isAvailablePathAndLine = False
        isAvailablePath = False
        isAvailableLine = False
        isAvailableErrorMessage = False
        errorMessage = ""

        if(len(request[1]) > 0):
            currentElement = str(request[1]).split(",")
            forFilePath = currentElement[0]
            forLineNumber = currentElement[1]
            isAvailablePathAndLine = True
            print("forFilePath :", forFilePath)

            file_path_results = list(re.finditer(
                regex_file_path, forFilePath))

            if(len(file_path_results) > 0):
                print(f"SCRIPT PATH : {file_path_results[0].group()}\n")
                isAvailablePath = True

            line_number_results = list(re.finditer(
                regex_line_number, forLineNumber))
            if(len(line_number_results) > 0):
                print(f"ERROR IN LINE : {line_number_results[0].group()}\n")
                isAvailableLine = True

            # extract import error by regex and get the last one
            importError_results = list(re.finditer(
                regex_extract_error, str(request[0])))

            if(len(importError_results) > 0):
                errorMessage = importError_results[0].group()
                isAvailableErrorMessage = True
            else:
                isAvailableErrorMessage = True
                errorMessage = request[0]

            if(isAvailablePathAndLine and isAvailablePath and isAvailableLine and isAvailableErrorMessage):
                data = {'path': Path(file_path_results[0].group()),
                        'line': int(line_number_results[0].group(
                        )), 'message': errorMessage}

                return super().handle(data)

        else:
            print(
                "no information about the path or line check the sequence of error message ")
            return False


class ModifyFileHandler(AbstractHandler):
    def handle(self, request: Any) -> str:
        currentScript = open(request['path'].absolute(), "r+b")
        # read entire content of file into memory
        s_content = currentScript.readlines()
        currentErrorInFile = s_content[request['line']-1].decode()
        errorImport = request['message']+"\n"
        # IF YOU REMOVE THIS CONDATION YOU WILL  COMMENT ALL OF YOU CODE :)
        # HIGHLY NOT RECOMMEND :(
        if(errorImport == currentErrorInFile):
            s_content[request['line']-1] = f"#{errorImport}".encode()
            # return pointer to top of file so we can re-write the content with replaced string
            currentScript.seek(0)
            # clear file content
            currentScript.truncate()
            # re-write the content with the updated content
            for line in s_content:
                currentScript.write(line)
            # close file
            currentScript.close()
            return True
        else:

            print("CURRENT LINE : ", errorImport)
            print("the error inside script mismatch with regex compiler message")
            return False


def checkMissingFile(handler: Handler) -> None:
    process = subprocess.Popen(['python3.8', 'index.py'],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # print(output.strip())
            result = handler.handle(output)
            if(result):
                print("the script has modified ")
                process.terminate()
                checkMissingFile(startDebuging)


if __name__ == "__main__":
    startDebuging = DebugHandler()
    fileLineFinder = FileAndLineFinder()
    errorFinder = ErrorFinder()
    regexHandler = RegexHandler()
    modifyFile = ModifyFileHandler()

    startDebuging.set_next(fileLineFinder).set_next(
        errorFinder).set_next(regexHandler).set_next(modifyFile)

    print("Chain: startDebuging > fileLineFinder > errorFinder > modifyFile")
    regex_file_path = r"(\/.*\.[\w:]+)|([\w:]+\.\w+)"
    regex_line_number = r"\d+"
    regex_extract_error = r"from \w+\.\w+ import \w+"
    checkMissingFile(startDebuging)
