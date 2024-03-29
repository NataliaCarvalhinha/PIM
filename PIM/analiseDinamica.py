import variablesPIM as variables
import createFileInput
import PIMRun
import PIMTrajectory
import validationPIM
import warnings
import os
import multiprocessing
from pathlib import Path


warnings.filterwarnings('ignore')

def dataSearch():
    """
    This function searches for data to carry out the simulation inside the directory specified in the variablePIM.py file.

    Parameters: None.

    Return: A list of files to run.

    Raises: None.

    Example:

        filesToRun = dataSearch()
        print(filesToRun)
    """
    
    # Create an empty list to store the files to run
    filesToRun = []
    
    # Convert variables.directorystr to a Path object
    directory_path = Path(variables.directorystr)

    # List all files in the directory
    for file in directory_path.iterdir():
        if file.is_file() and file.name.startswith("filesRun") and file.name.endswith(".txt"):
            with file.open() as readFile:
                lines = readFile.readlines()
                filesToRun.extend(lines)

    readFile = open(directory_path.joinpath('filesRun'))
    filesToRun = readFile.readlines()
    readFile.close()
    print(filesToRun)
    return filesToRun

def continueIntegration ():
    """
    This function prompts the user to decide whether to proceed with the integration process or not. It will keep asking for input until the user enters either "yes" or "no".

    Parameters: This function doesn't take any parameters.

    Return: This function doesn't return anything.

    Raises: This function doesn't raise any exceptions.

    Example:

        Would you like to proceed with the integration? (yes/no) maybe
        Please, type yes or no
        Would you like to proceed with the integration? (yes/no) YES
    """
    while True:
        user_input = input('Would you like to proceed with the integration? (yes/no) ')

        if user_input.upper() == 'NO':
            print("Process closed. To proceed with the integration, just restart the program.")
            exit()
        elif user_input.upper() == 'YES':
            return
        else:
            print('Please, type yes or no')

def askForDir():
    """
    This function asks the user to input the name of a .txt file containing a list of meteors (directories) to be analyzed, 
    and a separator character between the name, date, and time of each meteor. It then reads the file, parses the data, and 
    returns a list of directories, a list of dates, and a list of options.

    Parameters: None

    Raises: None

    Returns:

        directoriesList: a list of directory names to be analyzed.
        dateList: a list of dates for each directory to be analyzed, where each date is a list containing integers for the year, month, day, hour, minute, and second.
        optionList: a list of integers representing options for each directory to be analyzed.

    Example:

        Insert the .txt file containing the list of meteors (directories) to be analyzed: meteors
        Insert the separator character between the name, data and horary: |
        ['meteor1', 'meteor2'], [[2022, 5, 1, 12, 0, 0], [2022, 5, 2, 18, 0, 0]], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    directoriesFile = input("Insert the .txt file containing the list of meteors (directories) to be analyzed:  ")
    separator = input("Insert the separator character between the name, data and horary: ")
    """
    directoriesFile = 'meteors'
    separator =';'

    try:
        data = validationPIM.fileToList(directoriesFile+'.txt')
        
        if not data:
            print("Error: The file is empty or could not be read.")
            return  

        data = [i.split(separator) for i in data]
        
        directoriesList = [i[0] for i in data]
        
        dateList = [
            [
                int(component) if component.isdigit() else component 
                for component in (i[1].replace('/', ' ').replace(':', ' ').split())
            ] 
            for i in data
        ]
        
        options = [i[2] for i in data]
        optionList = [int(option) for option in options]
                
    except Exception as e:
        print("Error: unable to access meteor information. Please review the file. ")
        return 
    
    print(directoriesList, dateList, optionList)
    return directoriesList, dateList, optionList
    
def verificationFiles(directoriesFiles, directoryName):
    filesRun = "filesRun.txt"
    standardFile = "standard.txt"
    xlsExtension = ".xls"

    if not validationPIM.check_directory_existence(directoryName):
        print(f"The directory '{directoryName}' doesn't exist or is not a directory. So, we don't have the files with essential information.")
        exit()

    os.chdir(directoryName)
    print(os.getcwd())

    for directory in directoriesFiles:
        if not validationPIM.check_directory_existence(directory) or not os.path.isdir(directory):
            print(f"The directory '{directory}' doesn't exist or is not a directory.")
            return False

        meteorFiles = [f for f in os.listdir(directory)]
   
        if not validationPIM.hasExtension(meteorFiles,".xls"):
            return False
        
        if not "filesRun.txt" in meteorFiles:
            return False
        
        if not "standard.txt" in meteorFiles:
            return False

    return True

def readFileToList(fileIncomplete, directory):
    try:
        baseDirectory = Path(directory).resolve()
        fileComplete = baseDirectory / fileIncomplete
        
        with open(fileComplete, 'r') as file:
            lines = [line.strip() for line in file.readlines()]
            updatedFiles = []
            for line in lines:
                file_path = baseDirectory.joinpath(line)
                updatedFiles.append(str(file_path))
            return updatedFiles[1:-1]
           
    except FileNotFoundError as e:
        print(f"Error: {e}. The file '{fileComplete}' was not found.")
        return []
    except Exception as e:
        print(f"Error: {e}. An unexpected error occurred while reading the file.")
        return []

def runInParallel(argsList):
    # Create a process pool
    pool = multiprocessing.Pool()

    # Use the pool's map method to apply the function to the arguments in parallel
    pool.map(PIMRun.PIMRun, argsList)

    # Close the pool after completion
    pool.close()
    pool.join()

def runInSeq(argsList, directory):
    for file in argsList:
        path = os.path.join(directoryName, directory)
        PIMRun.PIMRun(file, path)

def startIntegration(directoriesList, directoryName): 
    for directory in directoriesList:
        file = 'filesRun.txt'
        filesList = readFileToList(file, directory)        
        runInSeq(filesList, directory)
        
##########################################################################################################


directoriesList,dateList,optionList = askForDir()

directoryName = 'Meteors' #input(f"Enter the name of the folder where the meteors folders should be verified: ")


if verificationFiles(directoriesList, directoryName):
    pass
else: 
    print("We haven't verified the existence of your initial files. We will create them from the .XML files.")
    createFileInput.multiCreate(directoriesList,dateList,optionList, directoryName)

continueIntegration ()


startIntegration(directoriesList, directoryName)
 
