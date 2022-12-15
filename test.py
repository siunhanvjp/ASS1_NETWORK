# from tkinter.simpledialog import askstring
# from tkinter.messagebox import showinfo
# name = askstring('Name', 'What is your name?')
# print(type(name))
file = open('upload/alo.txt', "r")
data = file.read()
print(data)
file.close()