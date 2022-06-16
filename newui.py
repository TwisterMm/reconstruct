#!/usr/bin/python3
import os
import subprocess
import tkinter as tk
from tkinter.filedialog import askopenfilename

import open3d as o3d
from os import makedirs
from os.path import exists

class UiApp:
    def __init__(self, master=None):
        # build ui
        self.toplevel1 = tk.Tk() if master is None else tk.Toplevel(master)
        self.frame1 = tk.Frame(self.toplevel1)
        self.buttonCapture = tk.Button(self.frame1)
        self.buttonCapture.configure(
            anchor="n", compound="bottom", default="normal", justify="center"
        )
        self.buttonCapture.configure(relief="raised", text="Capture")
        self.buttonCapture.place(anchor="nw", relx="0.18", rely="0.14", x="0", y="0")
        self.buttonCapture.configure(command=self.startScanning)
        self.buttonIntegration = tk.Button(self.frame1)
        self.buttonIntegration.configure(
            default="normal", justify="left", relief="raised", text="Integration"
        )
        self.buttonIntegration.place(
            anchor="nw", relx="0.18", rely="0.34", x="0", y="0"
        )
        self.buttonIntegration.configure(command=self.integrateScene)
        self.filepathEntry = tk.Entry(self.frame1)
        self.filepathEntry.configure(
            exportselection="true", takefocus=True, validate="none"
        )
        _text_ = """File Path"""
        self.filepathEntry.delete("0", "end")
        self.filepathEntry.insert("0", _text_)
        self.filepathEntry.place(anchor="nw", relx="0.49", rely="0.8", x="0", y="0")
        self.buttonBrowse = tk.Button(self.frame1)
        self.buttonBrowse.configure(
            anchor="n", compound="left", font="TkDefaultFont", justify="right"
        )
        self.buttonBrowse.configure(text="Browse")
        self.buttonBrowse.place(anchor="n", relx="0.19", rely="0.77", x="0", y="0")
        self.buttonBrowse.configure(command=self.displayPLY)
        self.pipeline = tk.Label(self.frame1)
        self.pipeline.configure(state="normal", text="Capture pipelines")
        self.pipeline.place(anchor="n", relx="0.26", x="0", y="0")
        self.preview = tk.Label(self.frame1)
        self.preview.configure(
            justify="left", relief="flat", takefocus=False, text="Preview PLY\n"
        )
        self.preview.place(anchor="n", relx="0.18", rely="0.60", x="0", y="0")
        self.buttonDelete = tk.Button(self.frame1)
        self.buttonDelete.configure(justify="left", text="Delete Instace")
        self.buttonDelete.place(relx="0.68", rely="0.14", x="0", y="0")
        self.buttonDelete.configure(command=self.deleteLastScan)
        self.frame1.configure(height="200", width="300")
        self.frame1.pack(side="top")
        self.toplevel1.configure(
            height="200", relief="raised", takefocus=True, width="300"
        )

        # Main widget
        self.mainwindow = self.toplevel1


    def run(self):
        self.mainwindow.mainloop()

    def startScanning(self):
        subprocess.run(['python', 'sensors/realsense_recorder.py', '--record_imgs'], text=True, stdout=True) 

    def integrateScene(self):
        path = "/dataset/realsense/scan"
        files = next(os.walk(path))[2]
        scan_count = len(files)
        # scan_count = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
        # print("Integrating...")
        subprocess.run(['python', 'run_system.py', 'config/realsense.json', '--register', '--refine', '--integrate'],stdout=True, text=True)
        old_name = os.path.join("dataset/realsense/scene","integrated.ply")
        new_name = os.path.join("dataset/realsense/scene", "integrated" + str(scan_count-1) + ".ply")
        os.rename(old_name,new_name)
        ply_name = "dataset/realsense/scene/integrated" + str(scan_count-1) + ".ply"
        pcd_read = o3d.io.read_point_cloud(ply_name)
        o3d.visualization.draw(pcd_read)
        print("File saved to: " + str(new_name))

    def displayPLY(self):
        ply_name = askopenfilename(title = "Select file",filetypes = (("PLY Files","*.ply"),))     
        pcd_read = o3d.io.read_point_cloud(ply_name)
        o3d.visualization.draw(pcd_read)

    def deleteLastScan(self):
        #check file path exist
        #make file path if not exist
        path = "dataset/realsense/scan"
        if not exists(path):
            makedirs(path)
        scan_count = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

        # read latest file number

        # 
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

if __name__ == "__main__":
    app = UiApp()
    app.run()
