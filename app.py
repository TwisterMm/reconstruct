from flask import Flask, Response, render_template
import subprocess
from sensors.realsense_helper import get_profiles
app = Flask(__name__)

def startScanning(): 
        
        colour_frames, depth_frames = get_profiles()
        if colour_frames and depth_frames:
            subprocess.run(['python', 'sensors/realsense_recorder.py', '--record_imgs'], text=True, stdout=True) 
        else:
            print("scanning fail")
            


@app.route('/')
def index():    
    return startScanning()



if __name__ == "__main__":
    app.run(debug=True)