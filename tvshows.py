import codecs
import math
import os
import rarfile
import re
import shutil
import sys

configFile = codecs.open("config", "r", "utf-8")

rarTool = configFile.readline().rstrip()
regexExt = configFile.readline().rstrip()
sourceDir = configFile.readline().rstrip()
destDir = configFile.readline().rstrip()

configFile.close()

rarfile.UNRAR_TOOL = rarTool

'''
rarfile.UNRAR_TOOL = "C:\Program Files\WinRAR\winrar.exe"
regexExt = '.*\.avi|.*\.mkv|.*\.mp4'
sourceDir = 'O:\\Shit\\RSS'
destDir = 'O:\\Þættir'
'''

def main():
    print(rarTool)
    print(regexExt)
    print(sourceDir)
    print(destDir)

    enterSetup = len(sys.argv) > 1 and sys.argv[1] == "-s"
    hasSetup = validatePath(rarTool) or validateRegexExt(regexExt) or validatePath(sourceDir) or validatePath(destDir)
    
    if(enterSetup or not hasSetup):
        setup()
    
    files = os.listdir(sourceDir)

    for f in files:
        info = getShowInfo(f)
        name = info[0]

        if(info[1] is ''):
            print('Illegal name:', f)
            continue
        
        season = 'Season ' + str(int(info[1]))

        src = makePath(sourceDir, f)
        dest = makePath(destDir, name, season)

        # If we find a file, copy it if we don't find it in the destination
        if(os.path.isfile(src)):
            if(os.path.exists(makePath(dest, f))):
                continue

            copyFile(src, dest)          
            continue

        # No need to extract what has already been extracted
        if(os.path.isfile(makePath(sourceDir, f, '.done'))):
            print('Already processed:', makePath(sourceDir, f))
            continue

        # Try to extract, if it fails, search for a single file and copy
        if(extractFiles(src, dest) is False):
            localfiles = os.listdir(src)
            if(len(localfiles) is 0):
                continue

            filename = ''
            i = 0
            while(i < len(localfiles)):
                if(os.path.isdir(localfiles[i])):
                   continue

                res = re.match(regexExt, localfiles[i])
                if(res is not None):
                   filename = res.group()
                   break
                   
                i += 1

            if(filename is ''):
                print('No suitable file found in', src)
                continue
            
            if(os.path.exists(makePath(dest, filename))):
                continue
            
            copyFile(makePath(src, filename), dest)

# Returns [show-name, season-number, episode-number]
# of a properly formatted directory-name
def getShowInfo(dirname):

    showName = re.split('S\d+E\d+|\d{3,4}', dirname, re.IGNORECASE)[0]
    showName = showName.replace('.', ' ').strip()

    res1 = re.search('S\d+E\d+', dirname, re.IGNORECASE)
    res2 = re.search('\d{3,4}', dirname)

    if(res1 is not None):
        SE = res1.group().split('S')[1].split('E')
        season = SE[0]
        episode = SE[1]
    elif(res2 is not None):
        se = res2.group()
        season = math.floor(int(se)/100)
        episode = int(se) % 100

    return [showName, season, episode]

# source: Directory containing archives
# dest: Destination directory
def extractFiles(source, dest):
    filepath = source
    myrarfile = ''
    
    if(os.path.exists(source) is not True):
       print('Source not found')
       return

    if(os.path.isdir(source) is not True):
        print('Source is not a directory')
        return
    
    files = os.listdir(source)

    for f in files:
        res = re.match('.*\.rar', f)
        if(res is not None):
            myrarfile = str(res.group())
            break

    if(myrarfile is ''):
        print('No archive found in', filepath)
        return False
    else:
        filepath += '\\' + myrarfile

    try:
        rf = rarfile.RarFile(filepath)
    except:
        print('Invalid .rar file:', source)
        return False

    file = rf.namelist()[0]

    if(os.path.exists(makePath(dest, file))):
        print('File', file, 'exists, skipping')
        markDone(source)
        return

    try:
        print('Extracting', file, 'to', makePath(dest, file))
        rf.extract(file, dest)
    except:
        print('Error extracting', file)

    markDone(source)
    
# source: Full path to file
# dest: Destination directory
def copyFile(source, dest):
    if(not os.path.exists(dest)):
        mkdir(dest)

    splits = source.split('\\')
    filename = splits[len(splits)-1]
        
    print('Copying file', filename, 'to', dest)
    shutil.copyfile(source, makePath(dest, filename))
    
# filepath: Directory containing archives to mark
def markDone(filepath):
    donefile = open(makePath(filepath, '.done'), 'w+')
    donefile.close()
    

def makePath(root, *args):
    path = root
    
    i = 0
    while i < len(args):
        path += '\\' + args[i]
        i += 1
    
    return path


def mkdir(path):
    folders = path.split('\\')
    newpath = makePath(folders[0])

    i = 1
    while(i < len(folders)):
        newpath = makePath(newpath, folders[i])
        if(os.path.exists(newpath) is False):
            os.mkdir(newpath)

        i += 1

def validateRegexExt(ext):
    #TODO: May want to implement a more thorough check
    return ext is not ""

def validatePath(path):
    #TODO: May want to implement a more thorough check
    return path is not ""

def setup():
    print("Setup mode")

    rarToolInput = input("Enter RarTool path (currently " + rarTool +"): ")
    regexExtInput = input("Enter a regex to look for (currently " + regexExt + "): ")
    sourceDirInput = input("Enter a source directory (currently " + sourceDir + "): ")
    destDirInput = input("Enter a destination directory (currently " + destDir + "): ")

    #configFile = codecs.open("config", "a+")

main()
