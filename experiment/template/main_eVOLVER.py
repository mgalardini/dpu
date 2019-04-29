from tkinter import *
from tkinter.ttk import *
import eVOLVER_module
import time
import pickle
import os.path
import custom_script
import smtplib

#### Where the GUI is called and widgets are placed
class make_GUI:

    def __init__(self, master):
        master.wm_title(custom_script.GUI_NAME)
        note = Notebook(master)
        home = Frame(note)
        note.add(home, text = "Home")

        save_path = os.path.dirname(os.path.realpath(__file__))
        tabArray = [ ]

        for x in vials:
            newTab = Frame(note)
            note.add(newTab, text = "{0}".format(x))
            tabArray.append(newTab)

        self.quitButton = Button(home, text="Pause Measuring / Stop Pumps", command=stop_exp)
        self.quitButton.pack(side=BOTTOM)

        self.printButton = Button(home, text="Start / Measure now", command=start_exp)
        self.printButton.pack(side=BOTTOM)

        note.pack(fill=BOTH, expand=YES)


## Task done by pressing printButton
def start_exp():
    stop_exp()
    eVOLVER_module.restart_chemo()
    update_eVOLVER()

def stop_exp():
    global run_exp
    try:
        run_exp
    except NameError:
        print("Name Error")
    else:
        print("Experiment Stopped!")
        root.after_cancel(run_exp)
    #stop all pumps, including chemostat commands
    eVOLVER_module.stop_all_pumps()

#### Updates Temperature and OD values (repeated every 10 seconds)
def update_eVOLVER():
    global OD_data, temp_data
    ##Read and record OD
    elapsed_time = round((time.time() - start_time)/3600,4)
    print("Time: {0} Hours".format(elapsed_time))
    OD_data, temp_data = eVOLVER_module.read_data(vials)
    skip = False
    if OD_data is not None and temp_data is not None:
        if OD_data == 'empty':
            print("Data Empty! Skipping data log...")
        else:
            for x in vials:
                OD_data[x] = OD_data[x] - OD_initial[x]
        eVOLVER_module.parse_data(OD_data, elapsed_time, vials, 'OD')
        eVOLVER_module.parse_data(temp_data, elapsed_time, vials, 'temp')

        #Make decision
        custom_functions(elapsed_time)

        #Save Variables
        global run_exp
        eVOLVER_module.save_var(start_time, OD_initial)
    run_exp = root.after(1000,update_eVOLVER)


#### Custom Script
def custom_functions(elapsed_time):
    global OD_data, temp_data
    if OD_data == 'empty':
        print("UDP Empty, did not execute program!")
    else:
        ###load script from another python file
        if custom_script.OPERATION_MODE == 'turbidostat':
            custom_script.turbidostat(OD_data, temp_data, vials, elapsed_time)
        if custom_script.OPERATION_MODE == 'chemostat':
            custom_script.chemostat(OD_data, temp_data, vials, elapsed_time)


#### Runs if this is main script
if __name__ == '__main__':
    vials = range(0,16)
    start_time, OD_initial = eVOLVER_module.initialize_exp(vials)
    root=Tk()
    make_GUI(root)
    update_eVOLVER()
    root.mainloop()
