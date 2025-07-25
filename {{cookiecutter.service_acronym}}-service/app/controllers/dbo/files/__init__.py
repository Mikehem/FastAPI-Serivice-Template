#noqa
import os

global G_L1_Labels

_files_directory = os.path.join(os.getcwd(), "app/controller/dbo/files")

def filedata_list(filepath):
    data = []
    file =  open(filepath, "r")
    data = list(file)
    return data

G_L1_Labels = filedata_list(filepath=os.path.join(_files_directory, "L1_Labels.txt"))