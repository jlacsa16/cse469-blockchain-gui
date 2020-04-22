from tkinter import *
from tkinter import messagebox

# global parameters
BACKGROUND_COLOR = 'steel blue'
BIG_FONT = "Arial Bold"
SMALL_FONT = "Arial"
FONT_SIZE = 14

# main window
window = Tk()
window.title("Blockchain Chain of Custody")
window.geometry("550x275")
window.configure(bg=BACKGROUND_COLOR)

# main prompt
prompt1 = Label(window, text="Choose a command:", font=(BIG_FONT, FONT_SIZE), justify=LEFT, bg=BACKGROUND_COLOR)
prompt1.grid(column=0, row=0)

# list of commands
prompt2 = Label(window, text="add -c case_id -i item_id [-i item_id ...]\ncheckout -i item_id\ncheckin -i item_id\nlog [-r] [-n num_entries] [-c case_id] [-i item_id]\nremove -i item_id -y reason [-o owner]\ninit\nverify", font=(SMALL_FONT, FONT_SIZE), justify=LEFT, bg=BACKGROUND_COLOR)
prompt2.grid(column=0, row=1)

# user input entry
userInputBox = Entry(window, width=30, font=(SMALL_FONT, FONT_SIZE))
userInputBox.grid(column=0, row=2)
userInputBox.focus()

# handles click of Run button, userInput gets sent to backend, display output from command sent
def runClicked():
    userInput = userInputBox.get()

    if userInput != "":
        messagebox.showinfo('Command Output','Your input returned the following output: \n\nINSERT OUTPUT HERE')
    else:
        messagebox.showinfo('Error','No command found. Try again.')

    # flush user input for next iteration
    del userInput

    # clear userInputBox
    userInputBox.delete(0, END)
    
# run button
run = Button(window, text="Run", font=(BIG_FONT, FONT_SIZE), command=runClicked)
run.grid(column=1, row=2)

def helpClicked():
    messagebox.showinfo('Help','Command Descriptions: \n\nINSERT HERE')

# help button
help = Button(window, text="Help", font=(BIG_FONT, FONT_SIZE), command=helpClicked)
help.grid(column=2, row=2)

# run the GUI
window.mainloop()