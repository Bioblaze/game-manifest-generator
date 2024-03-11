import sys, os, json, threading, time, argparse, hashlib, datetime
from pathlib import Path
from os import listdir;
from os.path import isfile, join; 
from timeit import default_timer as timer

#constants
max_threads = 0; directory_to_scan = ""; lock = threading.Lock(); debug = False; export = False
parser = argparse.ArgumentParser(description="Checksum Scanner Tool", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--threads", type=int, help="Maximum threads to run.", required=True)
parser.add_argument("-dir", "--directory", help="Full path of the directory to scan.", required=True)
parser.add_argument("-d", "--debug", help="Enable debugging.", action="store_true")
parser.add_argument("-b", "--build", help="Add a build to the manifest.", type=str, required=True)
parser.add_argument("-e", "--export", help="Exports the output. If not, just prints the checksum. Must provide manifest filename", type=str, required=True)
parser.add_argument("-o", "--output_folder", help="Writes the export into a specific folder", type=str, required=True)
parser.add_argument("-base", "--base_path", help="Base Directory from CDN to file", type=str, required=True)
parser.add_argument("-cdn", "--cdn", help="CDN url", type=str, required=True)
args = parser.parse_args()

def IsVersionProvided():
    return args.build is not None
    
def IsExportProvided():
    return args.export is not None
        
def GetVersion():
    return args.build

def GetManifestName():
    return args.export

def GetBasePath():
    return args.base_path

def GetCDNUrl():
    return args.cdn

def EnsureOutputFolderExists():
    """
    Checks if the output folder specified by the --output_folder argument exists, and creates it if it doesn't.
    If no output folder was specified, this function does nothing.
    """
    output_folder = args.output_folder
    if output_folder:  # Check if the output folder argument was provided
        if not os.path.exists(output_folder):  # Check if the folder exists
            os.makedirs(output_folder)  # Create the folder if it doesn't exist
            print(f"The output folder '{output_folder}' did not exist and has been created.")
        else:
            print(f"The output folder '{output_folder}' already exists.")
    else:
        print("No output folder was specified.")


def GetOutputFolder():
    """
    Retrieves the output folder path from the command line arguments.

    Returns:
        str: The path of the output folder specified by the --output_folder argument.
             Returns None if the argument was not provided.
    """
    EnsureOutputFolderExists()
    return args.output_folder


def GenerateBuild():
    print(IsVersionProvided())
    if IsVersionProvided():
        current_datetime = datetime.datetime.now(datetime.timezone.utc)
        # build_number = f"{GetVersion()}{'_'}{current_datetime.strftime('%Y%m%d%H%M%S')}"
        build_number = GetVersion()
        return build_number
        
def ThreadManager():
    global max_threads
    while True: 
        if threading.active_count() >= max_threads:
            time.sleep(1)

class Logger:
    def Success(text):
        with lock:
            print(f'(+) {text}')
    
    def Error(text):
        with lock:
            print(f'(-) {text}')
    
    def Info(text):
        with lock:
            print(f'(!) {text}')
    
    def Debug(text):
        with lock:
            print(f'[DEBUG] (*) {text}')
    
class Changer(object):
    def __init__(self):
        self.total = 0;
        self.files = [];
        self.task_thread = [];

    def GetFileSize(self, size):
        if size < 1024:
            return { 'total': size, 'number': size, 'type': 'bytes' }
        elif size < pow(1024,2):
            return { 'total': size, 'number': round(size/1024, 2), 'type': 'KB' }
        elif size < pow(1024,3):
            return { 'total': size, 'number': round(size/(pow(1024,2)), 2), 'type': 'MB' }
        elif size < pow(1024,4):
            return { 'total': size, 'number': round(size/(pow(1024,3)), 2), 'type': 'GB' }
        
    def generate_checksum(self, filePath):
        global directory_to_scan
        FiveMB = 5 * 1024 * 1024
        fileName = '/' + os.path.relpath(filePath).replace('\\', '/')
        fileSize = self.GetFileSize(Path(filePath).stat().st_size)
        start = timer()
        with open(filePath, 'rb') as file:
            file.seek(0, 2)
            file_size = file.tell()

            if file_size > FiveMB:
                file.seek(-FiveMB, 2)
                data = file.read(FiveMB)
            else:
                file.seek(0)
                data = file.read()

        sha256 = hashlib.sha256()
        sha256.update(data)
        end = timer()
        # Now 'fileName' holds just the name of the file, without the path
        self.files.append({ 'path': os.path.relpath(filePath, directory_to_scan), 'file': os.path.basename(fileName), 'size': fileSize, 'checksum': str(sha256.hexdigest()), 'processing_time': end - start})
        return True

    def GetAllFiles(self):
        global directory_to_scan
        file_list = []
        for root, dirs, files in os.walk(directory_to_scan):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory_to_scan)
                file_list.append(full_path)
        return file_list
    
    def StartTool(self):
        global directory_to_scan, export
        export = IsExportProvided()
        allFiles = self.GetAllFiles()
        self.total = len(allFiles)
        
        for file in allFiles:
            self.task_thread.append(threading.Thread(target=self.generate_checksum, args=[file]))
        
        for t in self.task_thread:
            if not t.is_alive():
                t.start()

        for t in self.task_thread:
            t.join()
        time.sleep(3)

        if export:
            build__number = GenerateBuild()
            outputJson = {
                'build_number': build__number,
                'total': self.total,
                'cdn': GetCDNUrl(),
                #'main_dir': directory_to_scan.replace('\\', '/'),
                'base_path': GetBasePath().replace('\\', '/'),
                'files': self.files
            }
            manifest__name = GetManifestName()
            
            output_folder = args.output_folder  # Retrieve the output folder
            if output_folder:  # If an output folder is set
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)  # Ensure the folder exists
                output_path = os.path.join(output_folder, f'{manifest__name}.json')
            else:
                output_path = f'{manifest__name}.json'
            
            # Use output_path which now conditionally includes the output folder
            open(output_path, 'w').close()
            with open(output_path, 'w', encoding='utf-8') as o:
                json.dump(outputJson, o, ensure_ascii=False, indent=4)
            Logger.Success(f'Successfully read checksum of {self.total} files. Output saved to {output_path}')
        else:
            for readFile in self.files:
                print(f'--\nfilename: {readFile["name"]}\nfilesize: {readFile["size"]}\nchecksum: {readFile["checksum"]}\nprocessing time: {readFile["processing_time"]}\n--\n')
            Logger.Success(f'Successfully read checksum of {self.total} files.')
        os._exit(0)

def ChecksumScanner():
    global max_threads, directory_to_scan, args, export, debug
    
    max_threads = args.threads
    directory_to_scan = args.directory
    debug = args.debug
    export = args.export
    
    client = Changer()
    client.StartTool()

if __name__ == "__main__":
    threading.Thread(target=ThreadManager).start()
    threading.Thread(target=ChecksumScanner).start()