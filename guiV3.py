from tkinter import Tk, Label, Button, Menu
import os
import open3d as o3d
from os.path import exists
import subprocess

from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror
from sensors.realsense_helper import get_profiles


def btnCapture():
    showinfo(title="Start Scanning",
             message="Please connect intel realsense device, scanning will start taking images")
    colour_frames, depth_frames = get_profiles()
    if colour_frames and depth_frames:
        subprocess.run(['python', 'sensors/realsense_recorder.py',
                       '--record_imgs'], text=True, stdout=True)
    else:
        showerror(title="Camera not available",
                  message="Please connect intel realsense device before proceed")


def btnIntegrate():
    path = "dataset/realsense/scan"
    scan_count = len([f for f in os.listdir(
        path)if os.path.isfile(os.path.join(path, f))])
    print("Integrating...")
    subprocess.run(['python', 'run_system.py', 'config/realsense.json', '--make',
                   '--register', '--refine', '--integrate'], stdout=True, text=True)
    old_name = os.path.join("dataset/realsense/scene", "integrated.ply")
    new_name = os.path.join("dataset/realsense/scene",
                            "integrated" + str(scan_count-1) + ".ply")
    os.rename(old_name, new_name)
    ply_name = "dataset/realsense/scene/integrated" + \
        str(scan_count-1) + ".ply"
    pcd_read = o3d.io.read_point_cloud(ply_name)
    o3d.visualization.draw(pcd_read)
    print("File saved to: " + str(new_name))


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
        title="Select file", filetypes=(("PLY Files", "*.ply"),))
    if ply_name:
        pcd_read = o3d.io.read_point_cloud(ply_name)
        o3d.visualization.draw(pcd_read)


if __name__ == "__main__":
    root = Tk()

    # main window
    root.geometry('428x268')
    root.configure(background='#F0F8FF')
    root.title('3D room scanning')

    menubar = Menu(root, background='#F0F8FF', foreground='black',
                   activebackground='white', activeforeground='black')
    about = Menu(menubar, tearoff=0, background='#F0F8FF', foreground='black')
    about.add_command(label="Program Info")
    about.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="About", menu=about)

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

    Button(root, text='Exit', bg='#FF4C4C', width=5, height=2, font=(
        'arial', 12, 'normal'), command=root.quit).place(x=310, y=164)

    # drawing the widgets
    root.config(menu=menubar)
    root.mainloop()
