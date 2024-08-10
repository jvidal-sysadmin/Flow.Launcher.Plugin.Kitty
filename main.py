#encoding=utf8
import json
import os,sys
import glob
import re
import subprocess
import urllib.parse
from os import listdir
from os.path import isfile, join

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))

from flowlauncher import FlowLauncher

class Kitty(FlowLauncher):
    def load_session(self,kitty_path):
        session_path = os.path.join(kitty_path,"Sessions")
        files = [urllib.parse.unquote(f) for f in listdir(session_path) if isfile(join(session_path,f))]
        return files
    
    def load_session_recursive(self, kitty_path, exclude_regex=None):
        sessions = []
        session_path = os.path.join(kitty_path,"Sessions")

        for file in glob.iglob(session_path + os.sep + '**' + os.sep + '*', recursive=True):
            if not re.search(exclude_regex, file):
                if (os.path.isfile(file)):
                    session_file_name = urllib.parse.unquote(file)
                    sessions.append(session_file_name)

        return sessions

    def query(self,query):
        with open(os.path.join(os.path.dirname(__file__),"config.json"), "r") as content_file:
            config = json.loads(content_file.read())

        kitty_folder_path = os.path.expandvars(config["kitty_path"])
        exclude_regex     = config["exclude_regex"]
        kitty_path        = self.find_kitty_path(kitty_folder_path)
        sessions          = self.load_session_recursive(kitty_folder_path, exclude_regex)
        # sessions          = self.load_session(kitty_folder_path)
        query_response = []

        for session in sessions:
            if query in session:
                query_response.append(
                    {
                        "Title": os.path.basename(session),
                        "IcoPath": "kitty.png",
                        "JsonRPCAction": {
                            "method": "open_session",
                            "parameters": [kitty_path.replace("\\","\\\\"), session]
                        }
                    }
                )
        return query_response

    def open_session(self,kitty_path,session_name):
        subprocess.call('{} -kload "{}"'.format(kitty_path,session_name))

    def find_kitty_path(self,kitty_folder_path):
        """Returns the full path to the user's kitty executable"""

        exe_names = ['kitty.exe', 'kitty_portable.exe']
        for exe_name in exe_names:
            attempted_kitty_exe = os.path.join(kitty_folder_path,exe_name)
            if isfile(attempted_kitty_exe):
                return attempted_kitty_exe

        raise Exception("Could not find Kitty executable in %s" % kitty_folder_path)

if __name__ == "__main__":
    Kitty()