from tkinter import *
import math
import tkinter.font as tkfont

#structure of the calculator
root = Tk()
root.title("Calculator")
root.configure(padx=5, pady=5, bg="#a3c8e6")

frame = Frame(root, bg="#a3c8e6")
frame.pack(expand=True)

answer=""
prev_button=""
entryWidth=20
#font styles
entryFont = tkfont.Font(family="Arial", size=20)
calcFont = tkfont.Font(family="Arial", size=18)


#entry field
e = Entry(frame, width=entryWidth, borderwidth=5, relief="flat", font=entryFont, justify="right")
e.grid(row=0, column=0, columnspan=5, padx=10, pady=20)

def isFoatConvertible(string):
    try:
        float(string)
        return True
    except:
        return False


#Functions for number buttons
def buttonClick(number):
    if e.get()=="Error": e.delete(0, END)
    current = e.get()
    e.delete(0, END)
    e.insert(0, str(current)+str(number))

#functions for operation buttons
def add():
    global answer, prev_button
    if e.get()=="Error": e.delete(0, END)
    if e.get()=="":
        e.insert(0, "+")
        return
    try:
        int(e.get()[-1])
        current = str(e.get())
        e.delete(0, END)
        e.insert(0, (current+"+"))
    except:
        e.delete(0, END)
        e.insert(0, "Error")

def sub():
    global answer, prev_button
    if e.get()=="Error": e.delete(0, END)
    if e.get()=="":
        e.insert(0, "+")
        return
    try:
        int(e.get()[-1])
        current = str(e.get())
        e.delete(0, END)
        e.insert(0, (current+"-"))
    except:
        e.delete(0, END)
        e.insert(0, "Error")

def mul():
    global answer, prev_button
    if e.get()=="": 
        e.insert(0, "Error")
        return
    try:
        int(e.get()[-1])
        current = str(e.get())
        e.delete(0, END)
        e.insert(0, (current+"*"))
    except:
        e.delete(0, END)
        e.insert(0, "Error")
    
def div():
    global answer, prev_button
    if e.get()=="":
        e.insert(0, "Error")
        return
    try:
        int(e.get()[-1])
        current = str(e.get())
        e.delete(0, END)
        e.insert(0, (current+"/"))
    except:
        e.delete(0, END)
        e.insert(0, "Error")

#functions for action buttons
def clear(event=None):
    global answer
    e.delete(0, END)
    answer=""

def backspace():
    global answer
    if e.get()=="Error":
        e.delete(0, END)
        return
    current = str(e.get())
    e.delete(0, END)
    e.insert(0, current[0:-1])

def sign():
    try:
        current = str(e.get())
        e.delete(0, END)
        e.insert(0, current[1:] if float(current)<0 else "-"+current)
    except:
        e.delete(0, END)
        e.insert(0, "Error")

def point():
    if e.get()=="":
        e.insert(0, "0.")
        return
    try:
        eval(e.get()+"0.0")
        if e.get()[-1] in [str(num) for num in range(0, 10)]:
            new = e.get()+"."
            e.delete(0, END)
            e.insert(0, new)
        else:
            new = e.get()+"0."
            e.delete(0, END)
            e.insert(0, new)
    except:
        e.delete(0, END)
        e.insert(0, "Error")


def eq(event=None):
    try:
        eval(e.get())
        final = eval(e.get())
        e.delete(0, END)
        e.insert(0, round(final, entryWidth-10))
    except:
        try: 
            eval(e.get()[:-1])
            final = eval(e.get()[:-1])
            e.delete(0, END)
            e.insert(0, final)
        except:
            e.delete(0, END)
            e.insert(0, "Error")
e.bind("<Return>", eq)
e.bind("<Delete>", clear)

#number buttons
button_1 = Button(frame, width=6, height=1, pady=10, text="1",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432", command=lambda:buttonClick(1))
button_2 = Button(frame, width=6, height=1, pady=10, text="2",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(2))
button_3 = Button(frame, width=6, height=1, pady=10, text="3",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(3))

button_4 = Button(frame, width=6, height=1, pady=10, text="4",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(4))
button_5 = Button(frame, width=6, height=1, pady=10, text="5",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(5))
button_6 = Button(frame, width=6, height=1, pady=10, text="6",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(6))

button_7 = Button(frame, width=6, height=1, pady=10, text="7",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(7))
button_8 = Button(frame, width=6, height=1, pady=10, text="8",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(8))
button_9 = Button(frame, width=6, height=1, pady=10, text="9",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(9))

button_0 = Button(frame, width=6, height=1, pady=10, text="0",relief="flat", bg="#33b876",activebackground="#55da98",  font=calcFont, fg="#006321", activeforeground="#007432",command=lambda:buttonClick(0))

#operation buttons
button_add = Button(frame, width=6, height=1, pady=10, text="+", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=add)
button_sub = Button(frame, width=6, height=1, pady=10, text="-", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=sub)
button_mul = Button(frame, width=6, height=1, pady=10, text="×", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=mul)
button_div = Button(frame, width=6, height=1, pady=10, text="÷", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=div)

button_eq = Button(frame, width=6, height=1, pady=10, text="=", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=eq)


#action buttons
button_clr = Button(frame, width=12, padx=6, height=1, pady=10, text="Clear", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=clear)
button_bsp = Button(frame, width=6, height=1, pady=10, text="←", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=backspace)
button_sign = Button(frame, width=6, height=1, pady=10, text="(-)", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=sign)
button_point = Button(frame, width=6, height=1, pady=10, text=".", relief="flat", bg="#33b876", activebackground="#55da98", font=calcFont, fg="#006321", command=point)

#grid for number buttons 
button_1.grid(row=4, column=0)
button_2.grid(row=4, column=1)
button_3.grid(row=4, column=2)

button_4.grid(row=3, column=0)
button_5.grid(row=3, column=1)
button_6.grid(row=3, column=2)

button_7.grid(row=2, column=0)
button_8.grid(row=2, column=1)
button_9.grid(row=2, column=2)

button_0.grid(row=5, column=1)

#grid for operation buttons
button_add.grid(row=4, column=3)
button_sub.grid(row=3, column=3)
button_mul.grid(row=2, column=3)
button_div.grid(row=1, column=3)

button_eq.grid(row=5, column=3)

#grid for action buttons
button_clr.grid(row=1, column=0, columnspan=2)
button_bsp.grid(row=1, column=2)
button_sign.grid(row=5, column=0)
button_point.grid(row=5, column=2)


frame.grid_columnconfigure(0, weight=0)
frame.grid_columnconfigure(1, weight=0)
frame.grid_columnconfigure(2, weight=0)
frame.grid_columnconfigure(3, weight=0)
frame.grid_columnconfigure(4, weight=0)

root.mainloop()