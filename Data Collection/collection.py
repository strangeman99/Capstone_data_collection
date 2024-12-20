import serial
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from datetime import datetime
from multiprocessing import Process, Queue

serial_port = 'COM3'
baud_rate = 115200

# Displays the image
def display_image(image_path):
    img = mpimg.imread(image_path)
    plt.imshow(img)
    plt.axis('off')
    plt.draw()
    plt.pause(0.001)

# Makes a countdown
def countdown(seconds):
    print("Starting in...")
    for i in range(seconds, 0, -1):
        print(f"{i}")
        time.sleep(1)
    print("Go!")

# Read value from the serial port
def readserial(comport, baudrate, duration=1):
    ser = serial.Serial(comport, baudrate, timeout=0.05)  # Adjust timeout as needed
    data_df = pd.DataFrame(columns=['Timestamp', 'xaccel', 'yaccel', 'zaccel', 
                                    'xrot', 'yrot', 'zrot', 'emg1', 'emg2', 
                                    'emg3', 'pulse'])
    data = {
        "xaccel": None, "yaccel": None, "zaccel": None, 
        "xrot": None, "yrot": None, "zrot": None, 
        "emg1": None, "emg2": None, "emg3": None, 
        "pulse": None
    }
    samples = 0

    # Start timer
    start_time = time.time()

    while time.time() - start_time < duration:
        timestamp = datetime.now().strftime('%H:%M:%S.%f')

        line = ser.readline().decode(errors='ignore').strip()
        if line:
            try:
                data_point = float(line.split(" ")[1])
                if line.startswith("xaccel"):
                    data["xaccel"] = data_point
                elif line.startswith("yaccel"):
                    data["yaccel"] = data_point
                elif line.startswith("zaccel"):
                    data["zaccel"] = data_point
                elif line.startswith("xrot"):
                    data["xrot"] = data_point
                elif line.startswith("yrot"):
                    data["yrot"] = data_point
                elif line.startswith("zrot"):
                    data["zrot"] = data_point
                elif line.startswith("emg1"):
                    data["emg1"] = data_point
                elif line.startswith("emg2"):
                    data["emg2"] = data_point
                elif line.startswith("emg3"):
                    data["emg3"] = data_point
                elif line.startswith("pulse"):
                    data["pulse"] = data_point
            except (IndexError, ValueError):
                continue

        # Batch add to dataframe
        if all(data.values()):
            data_df.loc[len(data_df)] = [timestamp, *data.values()]
            data = {key: None for key in data}  # Resetting dictionary
            samples += 1

    ser.close()
    return data_df

def readserial_in_process(queue, comport, baudrate, duration=1):
    data_df = readserial(comport, baudrate, duration)
    queue.put(data_df)

# Data Collection loop
def collection(orientations_per_pos=1):
    serial_port = 'COM3'
    baud_rate = 115200

    # Define the positions and corresponding images
    positions = [0, 1, 2, 3, 12, 13, 23, 123]
    pic_positions = {
        0: "Pictures/pic_0.jpeg",
        1: "Pictures/pic_1.jpeg",
        2: "Pictures/pic_2.jpeg",
        3: "Pictures/pic_3.jpeg",
        12: "Pictures/pic_12.jpeg",
        13: "Pictures/pic_13.jpeg",
        23: "Pictures/pic_23.jpeg",
        123: "Pictures/pic_123.jpeg"
    }

    name = input("Enter User's name and press Enter...\n")

    # Excel writer
    os.makedirs('Data', exist_ok=True)
    writer = pd.ExcelWriter('Data/' + name + '_data.xlsx', engine='xlsxwriter')

    for pos in positions:
        # Display the example image
        display_image(pic_positions[pos])
        print("Please see the image on hand position")

        for ori in range(orientations_per_pos):
            input("Change the orientation of your hand to a random position. Press enter...\n")
            plt.close()

            countdown(3)

            # Using multiprocessing to capture all data
            queue = Queue()
            p = Process(target=readserial_in_process, args=(queue, serial_port, baud_rate, 1))
            p.start()
            p.join()
            
            # Retrieve the data from the queue
            data_df = queue.get()
            data_df['Position'] = pos
            data_df['Orientation'] = ori
            data_df.to_excel(writer, sheet_name=f'Position_{pos}', index=False)

            print("Data collected")

    writer.close()

if __name__ == '__main__':
    orientations_per_pos = 1
    collection(orientations_per_pos)
