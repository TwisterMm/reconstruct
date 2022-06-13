# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 21:39:43 2022

@author: Yung How
"""

import os.path, os
import open3d as o3d
import cv2 as cv
import subprocess
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
#subprocess.check_output(["python", "sensors/realsense_recorder.py", '--record_imgs"])
'''
path = 'dataset/realsense/color'
num_files = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
print (num_files)
'''
path = "dataset/realsense/scan"

def startScanning():
    valid_cams = []
    has_cam = False
    for i in range(8):
        cap = cv.VideoCapture(i)
        if cap.isOpened():
            has_cam = True
        else:
            valid_cams.append(i)
    if (has_cam):
        path = "dataset/realsense/scan"
        scan_count = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
        print("Starting scan, instance " + str(scan_count) + "...")
        result = subprocess.run(['python', 'sensors/realsense_recorder.py', '--record_imgs'], capture_output=True, text=True)
        print(result.stdout)
    else:
        print("No camera is detected")

def deleteLastScan():
    scan_count = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
    if (scan_count >0):
        read_file = open("dataset/realsense/scan/scan" + str(scan_count - 1) + ".txt", "r")
        lines = read_file.readlines()
        start_frame = lines[0][0] + lines[0][1] + lines[0][2]+ lines[0][3] + lines[0][4] +lines[0][5]
        end_frame = lines[1][0] + lines[1][1] + lines[1][2] + lines[1][3] + lines[1][4] + lines[1][5]
        read_file.close()
    
        toDelete = int(end_frame) - int(start_frame)
        for x in range(0,toDelete):
            currentDepth = int(start_frame) + x
            if (0 <= currentDepth < 10):
                deleteDepth = "00000" + str(currentDepth)
            elif (10 <= currentDepth < 100):
                deleteDepth = "0000" + str(currentDepth)
            elif (100 <= currentDepth < 1000):
                deleteDepth = "000" + str(currentDepth)
            elif (1000 <= currentDepth < 10000):
                deleteDepth = "00" + str(currentDepth)
            elif (10000 <= currentDepth < 100000):
                deleteDepth = "0" + str(currentDepth)
            elif (100000 <= currentDepth <= 999999):
                deleteDepth = str(currentDepth)
            os.remove("dataset/realsense/depth/" + deleteDepth + ".png")
            os.remove("dataset/realsense/color/" + deleteDepth + ".jpg")
        os.remove("dataset/realsense/scan/scan" + str(scan_count-1) + ".txt")
        print("Scan" + str(scan_count-1) + " deleted...")
        if (os.path.exists("dataset/realsense/scene/integrated" + str(scan_count-1) + ".ply")):
            os.remove("dataset/realsense/scene/integrated" + str(scan_count-1) + ".ply")
            print("Scene" + str(scan_count-1) + " deleted...")
    else:
        print("No scan found, nothing is deleted")
        
def makeFragment():
    scan_count = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
    if(scan_count > 0):
        print("Making fragment...")
        result = subprocess.run(['python', 'run_system.py', 'config/realsense.json', '--make'], capture_output=True, text=True)
        print(result.stdout)
        integrateScene()
    else:
        print("No scannings are made yet, please start scanning first")

def integrateScene():
    scan_count = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
    print("Integrating...")
    result = subprocess.run(['python', 'run_system.py', 'config/realsense.json', '--register', '--refine', '--integrate'], capture_output=True, text=True)
    print(result.stdout)
    old_name = os.path.join("dataset/realsense/scene","integrated.ply")
    new_name = os.path.join("dataset/realsense/scene", "integrated" + str(scan_count-1) + ".ply")
    os.rename(old_name,new_name)
    ply_name = "dataset/realsense/scene/integrated" + str(scan_count-1) + ".ply"
    pcd_read = o3d.io.read_point_cloud(ply_name)
    o3d.visualization.draw(pcd_read)
    print("File saved to: " + str(new_name))
    
def displayPLY():
    imageRoot = tk.Tk()
    imageRoot.withdraw()
    ply_name = askopenfilename(title = "Select file",filetypes = (("PLY Files","*.ply"),))
    if (ply_name=="" or ply_name[-4:]!=".ply"):
        print("Invalid file, try again")
    else:
        pcd_read = o3d.io.read_point_cloud(ply_name)
        o3d.visualization.draw(pcd_read)
        

root = Tk()
root.title("3D Interior Scanning")
scanButton = Button(root, text="Start scanning(Instance continuation)", command=startScanning).pack()

integrateButton = Button(root, text="Start integrating", command=makeFragment).pack()

deleteButton = Button(root, text="Delete last scan instance(including integration)", command=deleteLastScan).pack()

displayButton = Button(root, text="Display PLY file", command=displayPLY).pack()

quitButton = Button(root, text="Quit", command=root.destroy).pack()




root.mainloop()



    