from tkinter import *
import time
user_input = ""





class GUI():
    def __init__(self):
        def shutdownbutton():
            global user_input
            user_input = "shutdown"
            print(user_input)
            quit(self)

        def gameclosebutton():
            global user_input
            user_input = "close"
            print(user_input)
            quit(self)

        def quit(self):
            self.root.destroy()

        self.root = Tk()
        button1 = Button(self.root, text="Shutdown computer", padx=30,pady=50,command=shutdownbutton)
        button2 = Button(self.root, text="Close down game     ",padx=30,pady=50,command=gameclosebutton)
        button1.grid(row=1, column=0)
        button2.grid(row=2, column=0)
        window = Label(self.root, text="SeedingScript")
        window.mainloop()




guistart = GUI()
while True:
    print("yadadad")
    time.sleep(5)