
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import pickle
import socket
import threading
import mysql.connector
HEADER_LENGTH = 10

LARGE_FONT = ("verdana", 13,"bold")

HOST = "0.0.0.0"
PORT = 65336
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

#define sever name and database name
SEVER_NAME="localhost"
DATABASE_NAME='p2p'
USERNAME = "root"
PASSWORD = "ryzevn13"
#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SEARCH = "search"
LIST = "listall"
LISTROOM = "listroom"
LISTFRIEND = "listfriend"
CONNECT = "connect"
HOSTROOM = "hostroom"
DELETEROOM = "removeroom"
CONNECTROOM = "connectroom"


Live_Account=[] #store address, port online account
ID=[] #store online username
Ad=[]
room=[]

def get_client_data(server):
    try:
        header_length = server.recv(HEADER_LENGTH)
        message_length = int(header_length.decode(FORMAT).strip())
        data_res = server.recv(message_length)
        data_res = pickle.loads(data_res)
        return data_res
    except:
        return 'disconnected'

def send_text(sending_socket, text):
    sending_socket.sendall(bytes(text,encoding=FORMAT))

#create listen socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)




def Insert_New_Account(user,password):
    db,cursor=ConnectToDB()
    cursor.execute( "insert into user(username,password) values(%s,%s);",(user,password))
    db.commit()


def check_clientSignUp(username):
    if username == "admin":
        return 0
    db, cursor=ConnectToDB()
    cursor.execute("select username from user")
    for row in cursor:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            return 0
    return 1



def Check_LiveAccount(username):
    for row in Live_Account:
        parse= row.find("-")
        parse_check= row[(parse+1):]
        if parse_check== username:
            return False
    return True

def Remove_LiveAccount(conn, message):
    username = message["username"]
    try:
        if(username in Live_Account):
            Live_Account.remove(username)    
            ID.remove(username) 
            conn.sendall("REMOVED".encode(FORMAT))
        print(Live_Account)
        print(ID)
    except:
        conn.sendall("FAIL#REMOVED".encode(FORMAT))

       
def check_clientLogIn(username, password):
    db, cursor=ConnectToDB()
    cursor.execute("select username from user where username=(%s)", (username, ))
    if Check_LiveAccount(username) == False:
        return 0
    
    # check if admin logged in
    if username == "admin" and password == "database":
        return 1
    
    for row in cursor:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            cursor.execute("select password from user where username=(%s)",(username, ))
            parse= str(cursor.fetchone())
            parse_check =parse[2:]
            parse= parse_check.find("'")
            parse_check= parse_check[:parse]
            if password== parse_check:
                return 1
    return 2


def clientSignUp(sck, addr, message):

    user = message["username"]
    pswd = message["password"]
    
    print("username:--" + user +"--")
    print("password:--" + pswd +"--")


    #a = input("accepting...")
    accepted = check_clientSignUp(user)
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))

    if accepted:
        Insert_New_Account(user, pswd)
        # add client sign up address to live account
        ID.append(user)
        Live_Account.append(user)
        db, cursor=ConnectToDB()
        print(message["ip"])
        print(message["port"])
        cursor.execute("update user set conn_ip = %s, conn_port = %s where username = %s", (message["ip"], message["port"], user))
        db.commit()

    print("end-logIn()")
    print("")

def clientLogIn(sck, message):
    user = message["username"]
    pswd = message["password"]
    print("username:--" + user +"--")
    print("password:--" + pswd +"--")
    
    accepted = check_clientLogIn(user, pswd)
    print("accept:", accepted)
    sck.send(str(accepted).encode(FORMAT))
    
    if accepted == 1:
        ID.append(user)
        Live_Account.append(user)
        db, cursor=ConnectToDB()
        print(message["ip"])
        print(message["port"])
        cursor.execute("update user set conn_ip = %s, conn_port = %s where username = %s", (message["ip"], message["port"], user))
        db.commit()
        # sck.send("LOGIN#OKE".encode(FORMAT))

    print(ID)
    print("end-logIn()")
    print("")


def findUser(id):
    if id in ID:
        return True
    return False

 
def clientConn(sck, message):

    #connect request from sender to receiver (username)
     
    username = message["username"]
    sender = message["sender"]
    is_online =  findUser(username)
    response = {}
    if is_online == False :
        response["reply"] = "nouser"
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        
        sck.send(msg)
        
        return 
    else :
        
        #gui address voi port cua user nay
        db, cursor=ConnectToDB()
        cursor.execute("select conn_ip from user where username= %s ",(username, ))
        parse= str(cursor.fetchone())
        parse_check =parse[2:]
        parse= parse_check.find("'")
        conn_ip = parse_check[:parse]
        cursor.execute("select conn_port from user where username= %s ",(username, ))
        parse= str(cursor.fetchone())
        parse_check =parse[2:]
        parse= parse_check.find("'")
        conn_port = parse_check[:parse]
        #check friend khi connect
        cursor.execute("select * from friend_list where username=(%s) and user_friend=(%s)", (sender, username ))
        is_friend = False
        
        for row in cursor:
            is_friend = True
        #add friend khi connect
        if not(is_friend):
            cursor.execute( "insert into friend_list(username,user_friend) values(%s,%s);",(sender,username))
            db.commit()
            cursor.execute( "insert into friend_list(username,user_friend) values(%s,%s);",(username,sender))
            db.commit()

        #response
        response["reply"] = "oke"
        response["conn_ip"] = conn_ip
        response["conn_port"] = str(conn_port)
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        sck.send(msg)
        
def addRoom(sck, message):
    username = message["username"]
    
    if not any(item["username"] == username for item in room):
        room_listen_host = message["listen_host"]
        room_listen_port = message["listen_port"]
        host_room = {}
        host_room["username"] = username
        host_room["listen_host"] = room_listen_host
        host_room["listen_port"] = room_listen_port
        room.append(host_room)
        print(room)
        sck.sendall("ROOM#CREATED".encode(FORMAT))
    else:
        sck.sendall("ROOM#EXISTS".encode(FORMAT))
    
def removeRoom(sck, message):
    username = message["username"]
    
    if not any(item["username"] == username for item in room):
        sck.sendall("ROOM#DONT#EXIST".encode(FORMAT))
    else:
        room[:] = [d for d in room if d.get('username') != username]
        sck.sendall("ROOM#REMOVED".encode(FORMAT))


def connectRoom(sck, message):
    username = message["username"]
    
    is_online = True
    
    if not any(item["username"] == username for item in room):
        is_online = False
        
    response = {}
    if is_online == False :
        response["reply"] = "noroom"
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        
        sck.send(msg)
        
        return 
    else:
        conn_ip = ""
        conn_port = 0
        for item in room:
            if item['username'] == username:
                conn_ip = item['listen_host']
                conn_port = item['listen_port']
                break
            else:
                my_item = None
        print(conn_ip)
        print(conn_port)
        response["reply"] = "oke"
        response["conn_ip"] = conn_ip
        response["conn_port"] = str(conn_port)
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        sck.send(msg)
    
def showRoom(sck, message):
    try:
        room_list = []
        for item in room:
            room_list.append(item["username"])
            
        response = {}
        response["reply"] = "oke"
        response["room_online"] = room_list
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        sck.send(msg)
    except:
        response = {}
        response["reply"] = "fail"
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        sck.send(msg)
    
def showFriend(sck, message):
    try:
        user = message["username"]
        friend_list = []
        db, cursor=ConnectToDB()
        cursor.execute("select user_friend from friend_list where username=(%s) ",(user, ))
        for row in cursor:
            parse=str(row)
            parse_check =parse[2:]
            parse= parse_check.find("'")
            res= parse_check[:parse]
            friend_list.append(res)
        print(friend_list)
        online_friend_list = []
        
        for friend in friend_list:
            if friend in Live_Account:
                online_friend_list.append(friend)
        
        print(online_friend_list)
        
        response = {}
        response["reply"] = "oke"
        response["friend_online"] = online_friend_list
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        sck.send(msg)
    except:
        response = {}
        response["reply"] = "fail"
        
        msg = pickle.dumps(response)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        sck.send(msg)
    
# Specify this function before interpreting
def ConnectToDB():
    server = SEVER_NAME
    database = DATABASE_NAME
    username = USERNAME
    password = PASSWORD 
    cnxn = mysql.connector.connect(
        host=server,
        database=database,
        user=username,
        passwd=password
        )
    cursor = cnxn.cursor()
    return cnxn, cursor

def handle_client(conn, addr):

    while True:
        message = get_client_data(conn)
        if message == "disconnected":
            break
        message["status"] = 1 #mark as read
        print(message)
        
        option = message["option"]
            
        if option == LOGIN:
            clientLogIn(conn, message)
            
        elif option == SIGNUP:
            clientSignUp(conn, addr, message)
        
        elif option == CONNECT:
            clientConn(conn, message)

        elif option == LOGOUT:
            Remove_LiveAccount(conn, message)
            
        elif option == HOSTROOM:
            addRoom(conn, message)
            
        elif option == DELETEROOM:
            removeRoom(conn, message)
            
        elif option == CONNECTROOM:
            connectRoom(conn, message)
        
        elif option == LISTROOM:
            showRoom(conn, message)

        elif option == LISTFRIEND:
            showFriend(conn, message)
    print(Live_Account)
    print("end-thread")


def runServer():
    try:
        print(HOST)
        print("Waiting for Client")

        while True:
            print("prepare thread for 1 client")
            conn, addr = s.accept()
            print(conn)
            print(addr)

            clientThread = threading.Thread(target=handle_client, args=(conn,addr))
            clientThread.daemon = True 
            clientThread.start()

            #handle_client(conn, addr)
            print("new thread for client created")

        
    except KeyboardInterrupt:
        print("error")
        s.close()
    finally:
        s.close()
        print("end")
 

# defind GUI-app class
class ChatApp_Admin(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #self.iconbitmap('soccer-ball.ico')
        self.title("Chat server")
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage,HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)


    def showFrame(self, container):
        
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("500x350")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def logIn(self,curFrame):

        user = curFrame.entry_user.get()
        pswd = curFrame.entry_pswd.get()

        if pswd == "":
            curFrame.label_notice["text"] = "password cannot be empty"
            return 

        if user == "admin" and pswd == "server":
            self.showFrame(HomePage)
            curFrame.label_notice["text"] = ""
        else:
            curFrame.label_notice["text"] = "invalid username or password"

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        
        label_title = tk.Label(self, text="\nLOG IN FOR SEVER\n", font=LARGE_FONT,fg='#20639b',bg="bisque2").grid(row=0,column=1)

        label_user = tk.Label(self, text="\tUSERNAME ",fg='#20639b',bg="bisque2",font='verdana 10 bold').grid(row=1,column=0)
        label_pswd = tk.Label(self, text="\tPASSWORD ",fg='#20639b',bg="bisque2",font='verdana 10 bold').grid(row=2,column=0)

        self.label_notice = tk.Label(self,text="",bg="bisque2",fg='red')
        self.entry_user = tk.Entry(self,width=30,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=30,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN",bg="#20639b",fg='floral white',command=lambda: controller.logIn(self))

        button_log.grid(row=4,column=1)
        button_log.configure(width=10)
        self.label_notice.grid(row=3,column=1)
        self.entry_pswd.grid(row=2,column=1)
        self.entry_user.grid(row=1,column=1)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.configure(bg="bisque2")
        label_title = tk.Label(self, text="\n ACTIVE ACCOUNT ON SEVER\n", font=LARGE_FONT,fg='#20639b',bg="bisque2").pack()
        
        self.conent =tk.Frame(self)
        self.data = tk.Listbox(self.conent, height = 10, 
                  width = 40, 
                  bg='floral white',
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg='#20639b')
        
        button_log = tk.Button(self,text="REFRESH",bg="#20639b",fg='floral white',command=self.Update_Client)
        button_back = tk.Button(self, text="LOG OUT",bg="#20639b",fg='floral white' ,command=lambda: controller.showFrame(StartPage))
        button_log.pack(side= BOTTOM)
        button_log.configure(width=10)
        button_back.pack(side=BOTTOM)
        button_back.configure(width=10)
        
        self.conent.pack_configure()
        self.scroll= tk.Scrollbar(self.conent)
        self.scroll.pack(side = RIGHT, fill= BOTH)
        self.data.config(yscrollcommand = self.scroll.set)
        
        self.scroll.config(command = self.data.yview)
        self.data.pack()
        
    def Update_Client(self):
        self.data.delete(0,len(Live_Account))
        for i in range(len(Live_Account)):
            self.data.insert(i,Live_Account[i])
    


sThread = threading.Thread(target=runServer)
sThread.daemon = True 
sThread.start()
print(socket.gethostname())
        
app = ChatApp_Admin()
app.mainloop()