# Blockchain Chain of Custody GUI
# Jeremy Lacsa
# TODO: For some reason, run doesn't work when called by button events, gets "local variable 'userInput' referenced before assignment" error, so code is repeated. Need to center buttons on main menu. Improve prompts.

from tkinter import Tk, Label, Grid, Button, simpledialog, messagebox

# global parameters
BACKGROUND_COLOR = 'steel blue'
BIG_FONT = "Arial Bold"
SMALL_FONT = "Arial"
FONT_SIZE = 14
global userInput # this is the main variable the backend should use

# main window
window = Tk()
window.title("Blockchain Chain of Custody")
window.geometry("400x300")
window.configure(bg=BACKGROUND_COLOR)

# main prompt
prompt1 = Label(window, text="Choose a Command:", font=(BIG_FONT, FONT_SIZE), bg=BACKGROUND_COLOR)
prompt1.grid(row=0, column=0, columnspan = 2, sticky='EW')

# handles sending user input to backend, display output from command line (TODO: DOESN'T WORK)
# def run():
#     if userInput != "" or None:
#         messagebox.showinfo('Command Output','Your input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))
#     else:
#         messagebox.showinfo('Error','No command found. Try again.')

#     # flush userInput
#     del userInput

# ---- Button Click Events ----
# handles sending user input to backend, display output from command line
def addClicked():
    userInput = simpledialog.askstring("Add", "Command Description:\nAdd a new checkout entry to the chain of custody for the given evidence item. Checkout actions may only be performed on evidence items that have already been added to the blockchain.\n\nFormat:\n-c case_id -i item_id [-i item_id ...]", parent=window)
    
    if userInput != None:
        messagebox.showinfo('Command Output','Your input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))
    else:
        messagebox.showinfo('Error','No command found. Try again.')

    # flush userInput
    del userInput

    # run()

def removeClicked():
    userInput = simpledialog.askstring('Remove','Command Description:\nPrevents any further action from being taken on the evidence item specified. The specified item must have a state of CHECKEDIN for the action to succeed.\n\nFormat:\n-i item_id -y reason [-o owner]', parent=window)

    if userInput != None:
        messagebox.showinfo('Command Output','Your input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))
    else:
        messagebox.showinfo('Error','No command found. Try again.')

    # flush userInput
    del userInput

def checkoutClicked():
    userInput = simpledialog.askstring('Checkout','Command Description: \n\nAdd a new checkout entry to the chain of custody for the given evidence item.\nCheckout actions may only be performed on evidence items that have already been added to the blockchain.\n\nEnter the item id to be checked out:', parent=window)

    if userInput != None:
        userInput = "-i " + userInput
        messagebox.showinfo('Command Output','Your input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))
    else:
        messagebox.showinfo('Error','No command found. Try again.')

    # flush userInput
    del userInput

def checkinClicked():
    userInput = simpledialog.askstring('Checkin','Command Description: \n\nAdd a new checkin entry to the chain of custody for the given evidence item.\nCheckin actions may only be performed on evidence items that have already been added to the blockchain.\n\nEnter the item id to be checked in:', parent=window)

    if userInput != None:
        userInput = "-i " + userInput
        messagebox.showinfo('Command Output','Your input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))
    else:
        messagebox.showinfo('Error','No command found. Try again.')

    # flush userInput
    del userInput

def logClicked():
    userInput = simpledialog.askstring('Log','Command Description: \n\nDisplay the blockchain entries giving the oldest first (unless -r is given).\n\nFormat:\n[-r] [-n num_entries] [-c case_id] [-i item_id]', parent=window)

    if userInput != None:
        messagebox.showinfo('Command Output','Your input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))
    else:
        messagebox.showinfo('Error','No command found. Try again.')

    # flush userInput
    del userInput

def initClicked():
    userInput = "init"

    messagebox.showinfo('Command Output','Command Description: \n\nSanity check. Only starts up and checks for the initial block.\n\nYour input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))

    # flush userInput
    del userInput

def verifyClicked():
    userInput = "verify"

    messagebox.showinfo('Command Output','Command Description: \n\nParse the blockchain and validate all entries.\n\nYour input \"%s\" returned the following output: \n\nINSERT OUTPUT HERE' % (userInput))

    # flush userInput
    del userInput

def helpClicked():
    messagebox.showinfo('Help: Argument Flags','Argument Flags:\n\n-i item_id:\nSpecifies the evidence item’s identifier. When used with log only blocks with the given item_id are returned. The item ID must be unique within the blockchain. This means you cannot re-add an evidence item once the remove action has been performed on it.\n\n-r, --reverse:\nReverses the order of the block entries to show the most recent entries first.\n\n-n num_entries:\nWhen used with log, shows num_entries number of block entries.\n\n-y reason, --why reason:\nReason for the removal of the evidence item. Must be one of: DISPOSED, DESTROYED, or RELEASED. If the reason given is RELEASED, -o must also be given.\n\n-o owner:\nInformation about the lawful owner to whom the evidence was released.', parent=window)

# ---- End of Button Click Events ----

# ---- Buttons ----

# add
add = Button(window, text="Add", font=(BIG_FONT, FONT_SIZE), command=addClicked)
add.grid(row=1, column=0)

# remove
remove = Button(window, text="Remove", font=(BIG_FONT, FONT_SIZE), command=removeClicked)
remove.grid(row=1, column=1)

# checkout
checkout = Button(window, text="Checkout", font=(BIG_FONT, FONT_SIZE), command=checkoutClicked)
checkout.grid(row=2, column=0)

# checkin
checkin = Button(window, text="Checkin", font=(BIG_FONT, FONT_SIZE), command=checkinClicked)
checkin.grid(row=2, column=1)

# log
log = Button(window, text="Log", font=(BIG_FONT, FONT_SIZE), command=logClicked)
log.grid(row=3, column=0)

# init
init = Button(window, text="Init", font=(BIG_FONT, FONT_SIZE), command=initClicked)
init.grid(row=3, column=1)

# verify
verify = Button(window, text="Verify", font=(BIG_FONT, FONT_SIZE), command=verifyClicked)
verify.grid(row=4, column=0)

# help button
help = Button(window, text="Help: Argument Flags", font=(BIG_FONT, FONT_SIZE), command=helpClicked)
help.grid(row=4, column=1)

# ---- End of Buttons ----

# run the GUI
window.mainloop()