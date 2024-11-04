import time
import threading
import eel
import random
eel.init('web')
# Function to run in a separate thread
def running_method():
    eel.sleep(5)
    while True:
        random_value = random.randint(0, 100)  # Generate a random integer between 0 and 100
        print(f"Sending value: {random_value}")
        eel.updateValue(random_value)  # Call the JavaScript function
        time.sleep(1)

# Function to start eel in a non-blocking way
def start_eel():
    
    print("Loaded assets")
    eel.start('index.html', mode='chrome',)  # Start eel in blocking mode here

# Start eel in a separate thread
eel_thread = threading.Thread(target=start_eel)
eel_thread.start()

# Start the main running thread
running_thread = threading.Thread(target=running_method)
running_thread.start()

# Optionally, you can join threads if you want the main program to wait
running_thread.join()
eel_thread.join()
