import socket
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk 
from tkinter.ttk import *
import threading
from datetime import datetime
import pickle
import time
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo

HOST = "127.0.0.1"
PORT = 65200
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"
LARGE_FONT = ("verdana", 13,"bold")
HEADER_LENGTH = 10

#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SEARCH = "search"
INDENTIFY = "identify"
ADMIN_USERNAME = 'admin'
ADMIN_PSWD = 'database'
CONNECT = "connect"
CHAT = "chat"
CHATROOM = 'chatroom'
FRIEND = "friend"
HOSTROOM = "hostroom"
DELETEROOM = "removeroom"
CONNECTROOM = "connectroom"
LISTROOM = "listroom"
LISTFRIEND = "listfriend"
#GUI intialize

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

  
username = []
is_connect = []
is_room_connect = []
room_member = []

LISTEN_HOST = socket.gethostbyname(socket.gethostname())
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.bind((LISTEN_HOST, 0))
LISTEN_PORT = listen_socket.getsockname()[1]
listen_socket.listen(5)

def check_delete_room():
    try:
        if(len(username) > 0):
            message = {}
            message["option"] = DELETEROOM
            message["username"] = username[0]
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        
            client.send(msg)
            msg = client.recv(1024).decode(FORMAT)
    except:
        print("SERVER DISCONNECTED")

class Chat_App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
       
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.LISTEN_HOST = ""
        self.LISTEN_PORT = 0
        self.frames = {}
        for F in (StartPage, HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)
    
    def showFrame(self, container):
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("700x600")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            
            try:
                
                check_delete_room()
                if(len(username) > 0):
                    message = {}
                    message["option"] = LOGOUT
                    message["username"] = username.pop()
                    
                    msg = pickle.dumps(message)
                    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
                    
                    client.send(msg)
                    accepted = client.recv(1024).decode(FORMAT)
                client.close()
            except:
                print("Logout error")
            self.destroy()
            
    def logIn(self,curFrame,sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()
            
            if user == "" or pswd == "":
                curFrame.label_notice = "Fields cannot be empty"
                return 
       
            #notice server for starting log in
            message = {}
            message["option"] = LOGIN
            message["username"] = user
            message["password"] = pswd
            message["ip"] = str(LISTEN_HOST)
            message["port"] = str(LISTEN_PORT)
            
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            
            sck.send(msg)
            accepted = sck.recv(1024). decode(FORMAT)

            print("accepted: "+ accepted)

            if accepted == "1":
                username.append(user)
                self.showFrame(HomePage)
                curFrame.label_notice["text"] = ""
            elif accepted == "2":
                curFrame.label_notice["text"] = "invalid username or password"
            elif  accepted == "0":
                curFrame.label_notice["text"] = "user already logged in"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")

    def signUp(self,curFrame, sck):
        
        try:
        
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()
        
            if user == "" or pswd == "":
                curFrame.label_notice = "Fields cannot be empty"
                return 

            #notice server for starting log in
            
            message = {}
            message["option"] = SIGNUP
            message["username"] = user
            message["password"] = pswd
            message["ip"] = str(LISTEN_HOST)
            message["port"] = str(LISTEN_PORT)
            
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            
            sck.send(msg)
            accepted = sck.recv(1024). decode(FORMAT)
           
            print("accepted: "+ accepted)

            if accepted == "1":
                username.append(user)
                self.showFrame(HomePage)
                curFrame.label_notice["text"] = ""
            else:
                curFrame.label_notice["text"] = "username already exists"

        except:
            curFrame.label_notice["text"] = "Error 404: Server is not responding"
            print("404")
         
    def logout(self,curFrame, sck):
        try:
            check_delete_room()
            
            message = {}
            message["option"] = LOGOUT
            message["username"] = username.pop()
            print(message)
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            
            sck.send(msg)
            accepted = sck.recv(1024).decode(FORMAT)
            
            
            
            if accepted == "REMOVED":
                self.showFrame(StartPage)
        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            



class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")

        label_title = tk.Label(self, text="LOG IN", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        label_user = tk.Label(self, text="username ",fg='#20639b',bg="bisque2",font='verdana 10 ')
        label_pswd = tk.Label(self, text="password ",fg='#20639b',bg="bisque2",font='verdana 10 ')

        self.label_notice = tk.Label(self,text="",bg="bisque2")
        self.entry_user = tk.Entry(self,width=20,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=20,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN", bg="#20639b",fg='floral white',command=lambda: controller.logIn(self, client)) 
        button_log.configure(width=10)
        button_sign = tk.Button(self,text="SIGN UP",bg="#20639b",fg='floral white', command=lambda: controller.signUp(self, client)) 
        button_sign.configure(width=10)
        
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()

        button_log.pack()
        button_sign.pack()



class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        self.room_connect = []
        
        label_title = tk.Label(self, text="HOME PAGE", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        button_back = tk.Button(self, text="Log out",bg="#20639b",fg='#f5ea54', command=lambda: controller.logout(self,client))
        button_list = tk.Button(self, text="List Online Friend", bg="#20639b",fg='#f5ea54',command=self.listFriend)
        button_list_room = tk.Button(self, text="List Online Room",bg="#20639b",fg='#f5ea54', command = self.listRoom)
        button_connect_room = tk.Button(self, text="Connect Room",bg="#20639b",fg='#f5ea54', command=self.connectChatRoom)
        button_host_room = tk.Button(self, text="Host a Room",bg="#20639b",fg='#f5ea54', command=self.hostChatRoom)

        self.entry_search = tk.Entry(self)
        button_search = tk.Button(self, text="Connect",bg="#20639b",fg='#f5ea54', command=self.connectChat)

        label_title.pack(pady=10)

        button_search.configure(width=15)
        button_list.configure(width=15)
        button_back.configure(width=15)
        button_list_room.configure(width=15)
        button_connect_room.configure(width=15)
        button_host_room.configure(width=15)

        self.entry_search.pack()

        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.pack(pady=4)

        button_search.pack(pady=2)
        button_connect_room.pack(pady=2)
        button_host_room.pack(pady=2)
        button_list.pack(pady=2) 
        button_list_room.pack(pady=2)
        button_back.pack(pady=2)

        self.frame_detail = tk.Frame(self, bg="steelblue1")
        
        self.label_score = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)
        self.label_time = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)
        self.label_status = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)

        sThread = threading.Thread(target=self.runListenServer)
        sThread.daemon = True 
        sThread.start()

        self.label_score.pack(pady=5)
        self.label_time.pack(pady=5)
        self.label_status.pack(pady=5)
        


        self.frame_list = tk.Frame(self, bg="tomato")
        
        self.tree = ttk.Treeview(self.frame_list)

        
        self.tree["column"] = ("Name")
        
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Name",  anchor='c', width=240)

        self.tree.heading("0", text="")
        self.tree.heading("Name",  anchor='c', text="Name")
        
        self.tree.pack(pady=20)
        
    
    def listFriend(self):
        try:
            self.frame_detail.pack_forget()
            
            message = {}
            message["option"] = LISTFRIEND
            message["username"] = username[0]
            
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            
            client.send(msg)
            
            response = get_client_data(client)
            print(response)
            
            friends = response["friend_online"]
            
            x = self.tree.get_children()
            for item in x:
                self.tree.delete(item)
            print(friends)
            i = 0
            for friend in friends:
                print(friend)
                self.tree.insert(parent="", index="end", iid=i, 
                        values = (friend,) )
                
                i += 1

            self.frame_list.pack(pady=10)
        except:
            self.label_notice["text"] = "SERVER DISCONNECTED"
    
    def listRoom(self):
        try:
            self.frame_detail.pack_forget()
            
            message = {}
            message["option"] = LISTROOM
            
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            
            client.send(msg)
            
            response = get_client_data(client)
            print(response)
            
            rooms = response["room_online"]
            
            x = self.tree.get_children()
            for item in x:
                self.tree.delete(item)
            print(rooms)
            i = 0
            for room in rooms:
                print(room)
                self.tree.insert(parent="", index="end", iid=i, 
                        values = (room,) )
                
                i += 1

            self.frame_list.pack(pady=10)
        except:
            self.label_notice["text"] = "SERVER DISCONNECTED"
    
    def connect1v1(self, conn, message):
        if messagebox.askokcancel("Connection", "Do you want to connect?"):    
            try:
                conn.sendall("OK#CONNECT".encode(FORMAT))
                self.openChatWindow(conn, message["sender"])
            except:
                print("error")
        else:
            conn.sendall("NO#CONNECT".encode(FORMAT))
            conn.close() 
    
    def connectChatRoom(self):
        self.label_notice["text"] = ""
        id = self.entry_search.get()    
        if (id == ""):
            self.label_notice["text"] = "Field cannot be empty"
            return
        if(id in username):
            self.label_notice["text"] = "Cannot connect to your room"
            return
        if( id in is_room_connect):
            self.label_notice["text"] = "Already has a connection to this room"
            return
        
        message = {}
        message["option"] = CONNECTROOM
        message["username"] = id
        
        msg = pickle.dumps(message)
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
        
        client.send(msg)
        
        response = get_client_data(client)
        print(response)
        reply = response["reply"]
        
        if (reply == "noroom"):
            print("room offline or dont exist")
            self.label_notice["text"] = "Room offline or dont exist"
            return
        else:
            self.label_notice["text"] = "Room is online, Connecting..."
            
            conn_ip = response["conn_ip"]
            conn_port =int(response["conn_port"])
            is_room_connect.append(id)
            print(conn_ip)
            print(conn_port)
                
            client_p2p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (conn_ip, conn_port)
            client_p2p.connect(server_address)
            client_p2p.sendall(username[0].encode(FORMAT)) #register name with room
            self.openChatRoomWindow(client_p2p, id)
        
    
    def openChatRoomWindow(self, room_conn, room_name):
        def inputer():
            msg = chat_box.get()
            chat_box["text"] = ""
            if msg == "":
                label_notice["text"] = "cannot be empty"
            else:
                label_notice["text"] = ""
                try:
                    print(msg)
                    room_conn.sendall(msg.encode(FORMAT))
                    print("send oke")
                except:
                    data.insert(tk.END, 'NO CONNECTION !!')
                chat_box["text"] = ""
        def receiver():
            while True:
                try:
                    print("listening")
                    msg = room_conn.recv(1024).decode(FORMAT) 
                    print(msg)
                except:
                    print("END#CON1")
                if(msg == "CLOSE#ROOM"):
                    data.insert(tk.END, "ROOM SHUTDOWN!!!")
                    room_conn.close()
                    time.sleep(0.5)
                    window.destroy()
                    break
                else:
                    try:
                        data.insert(tk.END, msg)
                    except: 
                        break
                    
                
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                check_delete_room
                window.destroy()
                try: 
                    room_conn.sendall("END#CON".encode(FORMAT))
                    is_room_connect.remove(room_name)
                except:
                    print("close error")
                
                
        window = tk.Toplevel(self)
        window.configure(bg="bisque2")
        label_title = tk.Label(window, text="\n CHAT BOX \n", font=LARGE_FONT,fg='#20639b',bg="bisque2").pack()
        window.protocol("WM_DELETE_WINDOW", on_closing)
        content =tk.Frame(window)
        data = tk.Listbox(content, height = 20, 
                  width = 50, 
                  bg='floral white',
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg='#20639b')
        button_send = tk.Button(window,text="SEND",bg="#20639b",fg='floral white', command=inputer)
        button_back = tk.Button(window, text="QUIT",bg="#20639b",fg='floral white', command=on_closing)
        chat_box = tk.Entry(window)  
        label_notice = tk.Label(window, text="", bg="bisque2" )
        
        
        button_back.configure(width=10)
        button_back.pack(pady=2, side='bottom')
        button_send.configure(width=10)
        button_send.pack(pady=2, side= 'bottom')
        label_notice.pack( side = 'bottom')
        chat_box.pack(pady=2, side= 'bottom')
        
        scroll= tk.Scrollbar(content)
        scroll.pack(side = 'right', fill= 'both')
        data.config(yscrollcommand = scroll.set)
        content.pack_configure()
        scroll.config(command = data.yview)
        data.pack()
        
        data.delete(0, tk.END) 
        data.insert(tk.END, f'Chat room of {room_name} started')
        
        runPeerThread = threading.Thread(target=receiver)
        runPeerThread.daemon = True
        print("start thread")
        runPeerThread.start()
    
    
    def handle_p2p_client(self, conn, addr):
        
        message = get_client_data(conn) #receive from other peer
        if message == "disconnected":
            print("hehe")
        message["status"] = 1 #mark as read
        print(message)
        
        option = message["option"]
            
        if option == CHAT:
            self.connect1v1(conn, message)
            
        elif option == CHATROOM:
            self.connectChatRoom(conn, message) #add later 

    def runListenServer(self):
        try:
            print(LISTEN_HOST)
            print("Waiting for P2P Client")

            while True:
                print("prepare thread for 1 P2P client")
                conn, addr = listen_socket.accept()
                print(conn)
                print(addr)

                clientThread = threading.Thread(target=self.handle_p2p_client, args=(conn,addr))
                clientThread.daemon = True 
                clientThread.start()
                #handle_client(conn, addr)
                print("new thread for client created")

            
        except KeyboardInterrupt:
            print("error")
            listen_socket.close()
        finally:
            listen_socket.close()
            print("end")   


    def hostChatRoom(self): #register room with server
         #create new listen socket for chat room
        try:
            room_listen_host = socket.gethostbyname(socket.gethostname())
            room_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            room_listen_socket.bind((room_listen_host, 0))
            room_listen_port = room_listen_socket.getsockname()[1]
            room_listen_socket.listen(5)
            
            print(room_listen_host)
            print(room_listen_port)
            
            message = {}
            message["option"] = HOSTROOM
            message["username"] = username[0]
            message["listen_host"] = room_listen_host
            message["listen_port"] = room_listen_port
            
            
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            
            client.send(msg)
            
            msg = client.recv(1024).decode(FORMAT)
            print(msg)
            if(msg == "ROOM#EXISTS"):
                room_listen_socket.close()
                self.label_notice["text"] = "Cannot create, already host a room"
                return

            roomThread = threading.Thread(target=self.openHostRoomWindow, args=(room_listen_socket,))
            roomThread.daemon = True 
            roomThread.start()
        except:
            self.label_notice["text"] = "SERVER DISCONNECTED"
        
       
    def openHostRoomWindow(self, host_socket):
        
        def broadcast_msg(msg, sender):
            
            for user in self.room_connect:
                if(user["username"] == sender):
                    user["conn"].sendall(f'You say: {msg}'.encode(FORMAT))
                else:
                    user["conn"].sendall(f'{sender} say: {msg}'.encode(FORMAT))
                    
            if sender == username[0]:
                data.insert(tk.END, f'You say: {msg}')
            else:
                data.insert(tk.END, f'{sender} say: {msg}')
            
        
        def receive_msg(conn, sender):
            while True:
                try:
                    print("listening")
                    msg = conn.recv(1024).decode(FORMAT) 
                    print(msg)
                except:
                    print("END#CON 1")
                    
                if(msg == "END#CON"):
                    broadcast_msg(f'{sender} Disconnected', "SYSTEM")
                    self.room_connect[:] = [d for d in self.room_connect if d.get('username') != sender]
                    conn.close()
                    break
                else:
                    try:
                        broadcast_msg(msg, sender)
                    except: 
                        break
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                try: 
                    for user in self.room_connect:
                        user["conn"].sendall("CLOSE#ROOM".encode(FORMAT))
                    self.room_connect = []
                    # nho xoa room ben server
                    
                    check_delete_room()
                    
                    host_socket.close()
                    window.destroy()
                except:
                    print("close error")
        def inputer():
            msg = chat_box.get()
            chat_box["text"] = ""
            if msg == "":
                label_notice["text"] = "cannot be empty"
            else:
                label_notice["text"] = ""
                broadcast_msg(msg ,username[0])
                            
        window = tk.Toplevel(self)
        window.configure(bg="bisque2")
        label_title = tk.Label(window, text="\n CHAT BOX \n", font=LARGE_FONT,fg='#20639b',bg="bisque2").pack()
        window.protocol("WM_DELETE_WINDOW", on_closing)
        content =tk.Frame(window)
        data = tk.Listbox(content, height = 20, 
                  width = 50, 
                  bg='floral white',
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg='#20639b')
        button_send = tk.Button(window,text="SEND",bg="#20639b",fg='floral white', command=inputer)
        button_back = tk.Button(window, text="QUIT",bg="#20639b",fg='floral white', command=on_closing)
        chat_box = tk.Entry(window)  
        label_notice = tk.Label(window, text="", bg="bisque2" )
        
        
        button_back.configure(width=10)
        button_back.pack(pady=2, side='bottom')
        button_send.configure(width=10)
        button_send.pack(pady=2, side= 'bottom')
        label_notice.pack( side = 'bottom')
        chat_box.pack(pady=2, side= 'bottom')
        
        scroll= tk.Scrollbar(content)
        scroll.pack(side = 'right', fill= 'both')
        data.config(yscrollcommand = scroll.set)
        content.pack_configure()
        scroll.config(command = data.yview)
        data.pack()
        
        data.delete(0, tk.END) 
        self.room_connect = [] # clean the storage
        data.insert(tk.END, f'Chat Room of {username[0]} started')
        
        print(host_socket)
        
        #listen for room connection
        
        print(host_socket)
        print("Hosting Chat room...")
        while True:
            try:
                print("Waiting for connection to Room")
                conn, addr = host_socket.accept()
                print(conn)
                print(addr)
                
                sender = conn.recv(1024).decode(FORMAT) #receive name
                member = {}
                member["username"] = sender
                member["conn"] = conn
                self.room_connect.append(member)
                
                for user in self.room_connect:
                    user["conn"].sendall(f'{sender} joined the room !!!'.encode(FORMAT))
                data.insert(tk.END, f'{sender} joined the room !!!')
                
                memberThread = threading.Thread(target=receive_msg, args=(conn, sender))
                memberThread.daemon = True 
                memberThread.start()
                print("new thread for client created")
            except:
                host_socket.close()
                print("CLOSE ROOM !!!")
                break
    
    def connectChat(self):
        try:
            self.label_notice["text"] = ""
            id = self.entry_search.get()    
            print(username)
            if (id == ""):
                self.label_notice["text"] = "Field cannot be empty"
                return
            if(id in username):
                self.label_notice["text"] = "Cannot connect to urself"
                return
            if( id in is_connect):
                self.label_notice["text"] = "Already has a connection to this account"
                return
            
            message = {}
            message["option"] = CONNECT
            message["username"] = id
            message["sender"] = username[0]
            
            msg = pickle.dumps(message)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            
            client.send(msg)
            
            # self.frame_list.pack_forget()

            response = get_client_data(client)
            print(response)
            reply = response["reply"]
            
            if (reply == "nouser"):
                print("user offline or dont exist")
                self.label_notice["text"] = "User offline or dont exist"
                return
            else:
                self.label_notice["text"] = "User is online, Connecting..."
                
                conn_ip = response["conn_ip"]
                conn_port =int(response["conn_port"])
                
                print(conn_ip)
                print(conn_port)
                    
                client_p2p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (conn_ip, conn_port)
                client_p2p.connect(server_address)
                
                message = {}
                message["option"] = CHAT
                message["sender"] = username[0]
                message["receiver"] = id
                
                msg = pickle.dumps(message)
                msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
                
                client_p2p.send(msg)
                
                
                conn_response = client_p2p.recv(1024).decode(FORMAT)
                print(conn_response)
                if(conn_response == "OK#CONNECT"):
                    user_receiver = id
                    self.openChatWindow(client_p2p, user_receiver)
        except:
            self.label_notice["text"] = "SERVER DISCONNECTED"
            return

    def openChatWindow(self, peer_conn, user_receiver):
        print(peer_conn)
        def inputer():
            msg = chat_box.get()
            chat_box["text"] = ""
            if msg == "":
                label_notice["text"] = "cannot be empty"
            else:
                label_notice["text"] = ""
                
                data.insert(tk.END, f'You say: {msg}')
                try:
                    print(msg)
                    peer_conn.sendall(msg.encode(FORMAT))
                    print("send oke")
                    
                except:
                    data.insert(tk.END, 'NO CONNECTION !!')
                chat_box["text"] = ""
        def receiver():
            while True:
                try:
                    print("listening")
                    msg = peer_conn.recv(1024).decode(FORMAT) 
                    print(msg)
                except:
                    print("END#CON")
                if(msg == "END#CON"):
                    data.insert(tk.END, "CONNECTION IS ENDED!!!")
                    peer_conn.close()
                    print(is_connect)
                    is_connect.remove(user_receiver)
                    print(is_connect)
                    time.sleep(0.5)
                    
                    window.destroy()
                    break
                elif(msg == "#SEND#FILE#"):
                    data.insert(tk.END, "Receiving file...")
                    receive_file()
                    data.insert(tk.END, "File received !!!")
                else:
                    try:
                        data.insert(tk.END, f'{user_receiver} say: {msg}')
                    except: 
                        break
                    
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                check_delete_room
                window.destroy()
                # try: 
                peer_conn.sendall("END#CON".encode(FORMAT))
                is_connect.remove(user_receiver)
                # except:
                    # print("close error")
                
        def send_file():
            name = askstring('File Name', 'What is your file name?(please include the extension)')   
            if(name == None):
                return
            print(name)
            try:
                dir = "upload/" + name
                file = open(dir, "rb")
            except:
                print("Cannot find file")
                data.insert(tk.END, "Cannot find file")
                return
            data_file = file.read()
            peer_conn.sendall("#SEND#FILE#".encode(FORMAT))
            file_msg = {}
            file_msg["name"] = name
            file_msg["data_file"] = data_file
            
            msg = pickle.dumps(file_msg)
            msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", FORMAT) + msg
            data.insert(tk.END, "SENDING FILE...")
            peer_conn.send(msg)
            data.insert(tk.END, "FILE SENT !!!")
            file.close()
          
        def receive_file():
            file_msg = get_client_data(peer_conn)  
            name = file_msg["name"]
            data_file = file_msg["data_file"]
            dir = "download/" + name
            file = open(dir, "wb+")
            file.write(data_file)
            file.close()
            
             
        window = tk.Toplevel(self)
        window.configure(bg="bisque2")
        label_title = tk.Label(window, text="\n CHAT BOX \n", font=LARGE_FONT,fg='#20639b',bg="bisque2").pack()
        window.protocol("WM_DELETE_WINDOW", on_closing)
        content =tk.Frame(window)
        data = tk.Listbox(content, height = 20, 
                  width = 50, 
                  bg='floral white',
                  activestyle = 'dotbox', 
                  font = "Helvetica",
                  fg='#20639b')
        button_send = tk.Button(window,text="SEND",bg="#20639b",fg='floral white', command=inputer)
        button_back = tk.Button(window, text="QUIT",bg="#20639b",fg='floral white', command=on_closing)
        chat_box = tk.Entry(window) 
        button_send_file = tk.Button(window, text="SEND FILE",bg="#20639b",fg='floral white', command=send_file)
        label_notice = tk.Label(window, text="", bg="bisque2" )
        
        
        button_back.configure(width=10)
        button_back.pack(pady=2, side='bottom')
        button_send_file.configure(width=10)
        button_send_file.pack(pady=2, side= 'bottom')
        button_send.configure(width=10)
        button_send.pack(pady=2, side= 'bottom')
        label_notice.pack( side = 'bottom')
        chat_box.pack(pady=2, side= 'bottom')
        
        scroll= tk.Scrollbar(content)
        scroll.pack(side = 'right', fill= 'both')
        data.config(yscrollcommand = scroll.set)
        content.pack_configure()
        scroll.config(command = data.yview)
        data.pack()
        
        data.delete(0, tk.END) 
        data.insert(tk.END, f'Conversation with {user_receiver} started')
        is_connect.append(user_receiver)
        
        runPeerThread = threading.Thread(target=receiver)
        runPeerThread.daemon = True
        print("start thread")
        runPeerThread.start()
        
        
            


#GLOBAL socket initialize -- client for main server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
client.connect(server_address)

app = Chat_App()

#main
try:
    app.mainloop()
except:
    print("Error: server is not responding")
    client.close()

finally:
    client.close()


