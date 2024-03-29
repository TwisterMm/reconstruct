import json
from tkinter import Tk, Label, Button, Menu
import os
import open3d as o3d
from os.path import exists
import subprocess

from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror
from sensors.realsense_helper import get_profiles

import pyrealsense2 as rs
import ctypes

def isDeviceConnected():
    ctx = rs.context()
    devices = ctx.query_devices()
    if devices:
        return True
    else:
        return False

def btnCapture():
    showinfo(title="Start Scanning",
             message="Please connect intel realsense device, scanning will start taking images")
    if(isDeviceConnected()):
        subprocess.run(['python', 'sensors/realsense_recorder.py',
                       '--record_imgs'], text=True, stdout=True)
    else:
        showerror(title="Camera not available",
                  message="Please connect to intel realsense device before proceed")

def btnIntegrate():
    try:
        config_path = ply_name = askopenfilename(
            title="Select file", filetypes=(("json file", "*.json"),),initialdir="config/")
        config = json.load(open(config_path))
        path = config['path_dataset']
        scan_count = len([f for f in os.listdir(
            path)if os.path.isfile(os.path.join(path, f))])        
        subprocess.run(['python', 'run_system.py', f'{config_path}', '--make',
                    '--register', '--refine', '--integrate'], stdout=True, text=True)
        old_name = os.path.join(path + "/scene", "integrated.ply")
        if(os.path.isfile(old_name)):
            new_name = os.path.join(path + "/scene",
                                    "integrated" + str(scan_count-1) + ".ply")
            os.rename(old_name, new_name)
        else:
            new_name = old_name

        # read integrated file
        ply_name = path + "/scene/integrated" + \
            str(scan_count-1) + ".ply"
        pcd_read = o3d.io.read_point_cloud(ply_name)
        o3d.visualization.draw(pcd_read)
    except FileNotFoundError:
        showerror(title="File not found",
                  message="Make sure the path contains the dataset")
    # rename integrated file
    

def btnDelete():
    path = "dataset/realsense/scan"
    if exists(path):
        scan_count = len([f for f in os.listdir(
            path)if os.path.isfile(os.path.join(path, f))])
        if(scan_count > 0):
            read_file = open(
                f"dataset/realsense/scan/scan{scan_count - 1}.txt", "r")
            lines = read_file.readlines()
            start_frame = lines[0].split()[0]
            end_frame = lines[1].split()[0]
            read_file.close()

            toDelete = int(end_frame) - int(start_frame)
            current_image_num = int(start_frame)
            for _ in range(toDelete):
                try:
                    delete_image_name = str(current_image_num).zfill(6)
                    os.remove("dataset/realsense/depth/" +
                              delete_image_name + ".png")
                    os.remove("dataset/realsense/color/" +
                              delete_image_name + ".jpg")
                    current_image_num += 1
                except FileNotFoundError:
                    continue

            os.remove("dataset/realsense/scan/scan" +
                      str(scan_count-1) + ".txt")
            print(f"Scan{scan_count-1} deleted...")
            print(f"Delete from {start_frame} to {end_frame}")

            try:
                os.remove("dataset/realsense/scene/integrated" +
                          str(scan_count-1) + ".ply")
                print("Scene" + str(scan_count-1) + " deleted...")
            except FileNotFoundError:
                print("Integrated file not found")
        else:
            print("No scan found, nothing is deleted")

def btnBrowse():
    ply_name = askopenfilename(
        title="Select file", filetypes=(("PLY Files", "*.ply"),), initialdir="dataset/realsense/scene/")
    if ply_name:
        pcd_read = o3d.io.read_point_cloud(ply_name)
        o3d.visualization.draw(pcd_read)
    
def startViewer():
    try:
        if(isDeviceConnected):
            os.system('python capture.py')
        else:
            showerror(title="Camera not available",
                  message="Please connect intel realsense device before proceed")        
    except RuntimeError:
        pass

def aboutInfo():
    showinfo(title="About",
             message="Prototype version V3.0.0\n3D room scanning based on open3D reconstruction system")

if __name__ == "__main__":
    try: # >= win 8.1
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except: # win 8.0 or less
        ctypes.windll.user32.SetProcessDPIAware()
    root = Tk()

    # main window
    root.geometry('600x400')
    root.configure(background='#F0F8FF')
    root.title('3D room scanning')

    menubar = Menu(root, background='#F0F8FF', foreground='black',
                   activebackground='white', activeforeground='black')
    about = Menu(menubar, tearoff=0, background='#F0F8FF', foreground='black')
    about.add_command(label="Program Info", command=aboutInfo)
    about.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="About", menu=about)

    viewer = Menu(menubar, tearoff=0, background='#F0F8FF', foreground='black')
    viewer.add_command(label="Live Stream Viewer", command=startViewer)
    menubar.add_cascade(label="Viewer", menu=viewer)

    # pipeline
    Label(root, text='Pipeline', bg='#F0F8FF', font=(
        'Times', 14, 'bold')).place(x=20, y=4)
    Button(root, text='Capture', bg='#AEEEEE', font=(
        'arial', 12, 'normal'), command=btnCapture).place(x=50, y=54)
    Button(root, text='Integrate', bg='#AEEEEE', font=(
        'arial', 12, 'normal'), command=btnIntegrate).place(x=180, y=54)
    Button(root, text='Delete', bg='#AEEEEE', font=(
        'arial', 12, 'normal'), command=btnDelete).place(x=310, y=54)

    # preview
    Label(root, text='Preview', bg='#F0F8FF', font=(
        'Times', 14, 'bold')).place(x=20, y=124)

    Button(root, text='Browse', bg='#AEEEEE', font=(
        'arial', 12, 'normal'), command=btnBrowse).place(x=50, y=164)
    
    Label(root, text='', bg='#F0F8FF', font=(
        'arial', 12, 'bold')).place(x=20, y=124)

    Button(root, text='Exit', bg='#FF4C4C', width=5, height=2, font=(
        'arial', 12, 'normal'), command=root.quit).place(x=310, y=164)

    # drawing the widgets
    root.config(menu=menubar)
    root.mainloop()
