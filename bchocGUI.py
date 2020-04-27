# Blockchain Chain of Custody GUI
# Jeremy Lacsa
# TODO:
# Fix run() so that commands are run correctly through bchoc.py
# Ensure output is saved to commandLineOutput
# Perform above tasks on init and verify

from tkinter import Tk, Frame, Label, Button, simpledialog, messagebox
import os
import bchoc

# global parameters
BACKGROUND_COLOR = "#fdf6e3"  # Solarized background color
ACCENT_COLOR = "#eee8d5"  # Solarized background highlights color
FONT_COLOR = "#657b83"  # Solarized body font color
BIG_FONT = "Calibri Bold"
SMALL_FONT = "Calibri"
FONT_SIZE = 14

# command line variables
# global userInput  # this is the user's command to be sent to bchoc.py
# global commandLineOutput  # this is the output from bchoc.py

# main window
window = Tk()
window.title("Blockchain Chain of Custody")
window.geometry("350x325")
window.configure(bg=BACKGROUND_COLOR)

# setup grid
mainFrame = Frame(window, bg=BACKGROUND_COLOR)
mainFrame.grid(row=0, column=0)
mainFrame.grid_rowconfigure(0, weight=1)
mainFrame.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# main prompt
prompt1 = Label(
    window,
    text="Choose a Command:",
    font=(BIG_FONT, FONT_SIZE * 2),
    bg=BACKGROUND_COLOR,
)
prompt1.grid(row=0, column=0, columnspan=2)
bottomPad = Label(window, text=" ", font=(BIG_FONT, FONT_SIZE * 2), bg=BACKGROUND_COLOR)
bottomPad.grid(row=5, column=0, columnspan=2)

# open bchoc.py, run command, save output
def run():
    global commandLineOutput  # this is the output from bchoc.py

    # open bchoc.py and run the command "userInput"
    os.system("python bchoc.py")
    # os.system('%s' % userInput)  # should theoretically run the command within bchoc.py

    # save the output as commandLineOutput
    commandLineOutput = "placeholder"

    # retrieve bchoc.py command line output, display results
    messagebox.showinfo(
        "Command Output",
        'Your input\n"%s"\nreturned the following output: \n\n%s'
        % (userInput, commandLineOutput),
    )


# ---- Button Click Events ----
# handles sending user input to backend, display output from command line
def addClicked():
    global userInput  # need to declare within the function
    userInput = simpledialog.askstring(
        "Add",
        "Command Description:\nAdd a new checkout entry to the chain of custody for the given evidence item. Checkout actions may only be performed on evidence items that have already been added to the blockchain.\n\nFormat:\n-c case_id -i item_id [-i item_id ...]",
        parent=window,
    )

    if userInput is not None:
        # append necessary command to user input
        userInput = "bchoc add " + userInput

        # send command to bchoc.py
        run()

    else:
        messagebox.showinfo("Error", "No command found. Try again.")

    # flush userInput
    del userInput


def removeClicked():
    global userInput  # need to declare within the function
    
    userInput = simpledialog.askstring(
        "Remove",
        "Command Description:\nPrevents any further action from being taken on the evidence item specified. The specified item must have a state of CHECKEDIN for the action to succeed.\n\nFormat:\n-i item_id -y reason [-o owner]",
        parent=window,
    )

    if userInput is not None:
        # append necessary command to user input
        userInput = "bchoc remove " + userInput

        # send command to bchoc.py
        run()

    else:
        messagebox.showinfo("Error", "No command found. Try again.")

    # flush userInput
    del userInput


def checkoutClicked():
    global userInput  # need to declare within the function

    userInput = simpledialog.askstring(
        "Checkout",
        "Command Description: \n\nAdd a new checkout entry to the chain of custody for the given evidence item.\nCheckout actions may only be performed on evidence items that have already been added to the blockchain.\n\nEnter the item id to be checked out:",
        parent=window,
    )

    if userInput is not None:
        # append necessary command to user input
        userInput = "bchoc checkout -i " + userInput

        # send command to bchoc.py
        run()

    else:
        messagebox.showinfo("Error", "No command found. Try again.")

    # flush userInput
    del userInput


def checkinClicked():
    global userInput  # need to declare within the function

    userInput = simpledialog.askstring(
        "Checkin",
        "Command Description: \n\nAdd a new checkin entry to the chain of custody for the given evidence item.\nCheckin actions may only be performed on evidence items that have already been added to the blockchain.\n\nEnter the item id to be checked in:",
        parent=window,
    )

    if userInput is not None:
        # append necessary command to user input
        userInput = "bchoc checkin -i " + userInput

        # send command to bchoc.py
        run()

    else:
        messagebox.showinfo("Error", "No command found. Try again.")

    # flush userInput
    del userInput


def logClicked():
    global userInput  # need to declare within the functions

    userInput = simpledialog.askstring(
        "Log",
        "Command Description: \n\nDisplay the blockchain entries giving the oldest first (unless -r is given).\n\nFormat:\n[-r] [-n num_entries] [-c case_id] [-i item_id]",
        parent=window,
    )

    if userInput is not None:
        # append necessary command to user input
        userInput = "bchoc log " + userInput

        # send command to bchoc.py
        run()

    else:
        messagebox.showinfo("Error", "No command found. Try again.")

    # flush userInput
    del userInput


def initClicked():
    global userInput  # need to declare within the function

    global commandLineOutput  # this is the output from bchoc.py

    userInput = "bchoc init"

    messagebox.showinfo(
        "Command Output",
        'Command Description: \n\nSanity check. Only starts up and checks for the initial block.'
    )

    run()

    # flush userInput
    del userInput


def verifyClicked():
    global userInput  # need to declare within the function

    global commandLineOutput  # this is the output from bchoc.py

    userInput = "bchoc verify"

    messagebox.showinfo(
        "Command Output",
        'Command Description: \n\nParse the blockchain and validate all entries.'
    )

    run()

    # flush userInput
    del userInput


def helpClicked():
    messagebox.showinfo(
        "Help: Argument Flags",
        "Argument Flags:\n\n-i item_id:\nSpecifies the evidence item’s identifier. When used with log only blocks with the given item_id are returned. The item ID must be unique within the blockchain. This means you cannot re-add an evidence item once the remove action has been performed on it.\n\n-r, --reverse:\nReverses the order of the block entries to show the most recent entries first.\n\n-n num_entries:\nWhen used with log, shows num_entries number of block entries.\n\n-y reason, --why reason:\nReason for the removal of the evidence item. Must be one of: DISPOSED, DESTROYED, or RELEASED. If the reason given is RELEASED, -o must also be given.\n\n-o owner:\nInformation about the lawful owner to whom the evidence was released.",
        parent=window,
    )


# ---- End of Button Click Events ----

# ---- Buttons ----

# add button
add = Button(window, text="Add", font=(BIG_FONT, FONT_SIZE), command=addClicked)
add.grid(row=1, column=0, sticky="NEWS")

# remove button
remove = Button(
    window, text="Remove", font=(BIG_FONT, FONT_SIZE), command=removeClicked
)
remove.grid(row=1, column=1, sticky="NEWS")

# checkout button
checkout = Button(
    window, text="Checkout", font=(BIG_FONT, FONT_SIZE), command=checkoutClicked
)
checkout.grid(row=2, column=0, sticky="NEWS")

# checkin button
checkin = Button(
    window, text="Checkin", font=(BIG_FONT, FONT_SIZE), command=checkinClicked
)
checkin.grid(row=2, column=1, sticky="NEWS")

# log button
log = Button(window, text="Log", font=(BIG_FONT, FONT_SIZE), command=logClicked)
log.grid(row=3, column=0, sticky="NEWS")

# init button
init = Button(window, text="Init", font=(BIG_FONT, FONT_SIZE), command=initClicked)
init.grid(row=3, column=1, sticky="NEWS")

# verify button
verify = Button(
    window, text="Verify", font=(BIG_FONT, FONT_SIZE), command=verifyClicked
)
verify.grid(row=4, column=0, sticky="NEWS")

# help button
help = Button(
    window, text="Help: Argument Flags", font=(BIG_FONT, FONT_SIZE), command=helpClicked
)
help.grid(row=4, column=1, sticky="NEWS")

# ---- End of Buttons ----

# run the GUI
window.mainloop()

# ---- END OF GUI ----
