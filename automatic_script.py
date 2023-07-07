import subprocess
import  tkinter as tk
from tkinter import filedialog
from PIL import Image
from datetime import datetime
import time
import sys
import match_and_log as log
import requests
from pprint import pprint


# ******************************************
#            Important Notes
# ******************************************
# Enter folder's location FIRST
# Example: cd  C:\Users\luigi\Desktop\LPR_Pipeline
# Change folder path to the same location
# Docker Command (in PowerShell): docker run --gpus all --rm -t -p 8080:8080 -v license:/license -e LICENSE_KEY=P4JTAk4w7L -e TOKEN=09c47b071dbfa9c262e86be7f544e540356e371b platerecognizer/alpr-gpu:latest
#
# If running for this first time, run the following commands before:
# 1) pip install -r requirements.txt
# 2) python setup.py develop --no_cuda_ext

def plate_recognizer(path):
    # Make sure Docker image is running in PowerShell
    region = ['us'] # Change to your country
    with open(path, 'rb') as fp:
        response = requests.post(
            'http://localhost:8080/v1/plate-reader/',
            data=dict(regions=region),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': 'Token 09c47b071dbfa9c262e86be7f544e540356e371b'})
    
    json_response = response.json()
    #pprint(json_response) # For debugging purposes

    # Check if "results" is an empty list
    if len(json_response['results']) == 0:
        print("Results is an empty list")
        return ("", 0, 0)
    else:
    # Access the desired properties
        processing_time_ms = json_response['processing_time']
        processing_time_sec = processing_time_ms / 1000
        confidence = json_response['results'][0]['dscore']
        plate = json_response['results'][0]['plate']

        # Print the values
        print("Processing Time:", processing_time_sec)
        print("Confidence:", confidence)
        print("Plate:", plate)
        return (plate, confidence, processing_time_sec)



# Absolute folder path (Change accordingly)
# Luigi's: 'C:/Users/luigi/Desktop/LPR_Pipeline'
# Aymen's: 'C:/Users/Kaynat/OneDrive/Desktop/LPR_Pipeline'
folder_path = 'C:/Users/Kaynat/OneDrive/Desktop/LPR_Pipeline'

# Argument Parsing
n = len(sys.argv)
print("Total arguments passed:", n)

# Argument length checking
if(n == 1):
    print("No path (argument) selected. Bye.")
    sys.exit()

if(n > 2):
    print("Too many arguments. Bye.")
    sys.exit()
 
# Arguments passed
print("\nName of Python script:", sys.argv[0])
print("\nArguments passed: ", sys.argv[1])

# Automatic Pipeline
# User selects image from folder
root = tk.Tk()
root.withdraw()
# file_path = filedialog.askopenfilename()
file_path = sys.argv[1]
try:
    im = Image.open(file_path)
except FileNotFoundError:
    print("FileNotFoundError. Bye!")
    sys.exit()
except TypeError:
    print("TypeError. Bye!")
    sys.exit()
except ValueError:
    print("ValueError. Bye!")
    sys.exit()
    
#print(file_path) # For debugging purposes
#im.show() # Display image before deblurring

# Saves current date and time
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

# ********************************************
# ***** Preprocessing: Deblurring ************
# ********************************************
st = time.time()
string_to_edit = 'python ./basicsr/demo.py -opt options/test/REDS/NAFNet-width64.yml --input_path image_path --output_path ./Output_Images/TEST_img.jpg'
command = string_to_edit.replace('image_path', file_path)
results = subprocess.run(command, cwd=folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#output = results.stdout.decode("utf-8") # For debugging purposes
#print(output)


# ****************************************
# *********** Plate Recognizer ***********
# ****************************************
lpr_path = folder_path + "/Output_Images/TEST_img.jpg"
lpr_result = plate_recognizer(lpr_path)

plate = lpr_result[0]
confidence = lpr_result[1]
processing_time = lpr_result[2]

zone =  1 # DELETE LATER

if(plate == "" or confidence == 0):
    display_string = "No plate identified (Sensor Triggered)" + " " + formatted_datetime
    print(display_string)
    identification_failure_log = open("IdentificationFailure.txt", "a")
    identification_failure_log.write(display_string)
    identification_failure_log.close()
else:
    display_string = plate + " " + formatted_datetime
    print("Identified License plate: ", display_string)
    detection_info = {
        "plate": plate,
        "zone": zone,
        "lastSeen": formatted_datetime
    }   
    log.match_and_log(detection_info)

# get the end and execution time
et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds\n')

