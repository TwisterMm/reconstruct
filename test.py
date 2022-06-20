import glob
import os.path
import ntpath

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

folder_path = r"dataset/realsense/color"
file_type = r"/*.jpg"
files = glob.glob(folder_path + file_type)
# max_file = max(files, key=os.path.getctime)
directory = [f for f in os.listdir(folder_path)if os.path.isfile(os.path.join(folder_path, f))]
print(directory)
# for f in files:
#     file_name, _ = ntpath.splitext(f)
#     print(file_name)


