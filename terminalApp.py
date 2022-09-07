# Create a multithreaded terminal application that runs a socket server and accepts connections on port 8939.
# I now understand the importance of adding comments to my code.
# I applogize to anyone trying to read, understand, and update this code in the future.
import traceback
class flagApp:
    import socket
    import select
    from app.models import Users, Flags
    from app.database import init_db, db_session

    def startDB(self):
        self.init_db
        print('Database initialized')

    def addUser(self, username, password):
        newUser = self.Users(username, password)
        self.updateDB(newUser, 'User added')

    def addAdmin(self, username, password):
        newAdmin = self.Users(username, password, True)
        self.updateDB(newAdmin, 'Admin added')

    def checkUser(self, username, password):
        user = self.db_session.query(self.Users).filter_by(name=username).first()
        return False if user is None else bool(user.checkPassword(password))

    def addFlag(self, host, flag, points):
        newFlag = self.Flags(host, flag, points)
        self.updateDB(newFlag, 'Flag added')

    def updateDB(self, arg0, arg1):
        self.db_session.add(arg0)
        self.db_session.commit()
        print(arg1)

    def checkFlag(self, flag, hashed=False):
        flags = self.db_session.query(self.Flags).all()
        if hashed:
            return any(f is not None and f.hashedValue == flag for f in flags)
        hashedFlag = self.Flags.hashFlag(self.Flags, flag)
        return any(f is not None and f.hashedValue == hashedFlag for f in flags)

    def getFlagPoints(self, method=1, flagID=None):
        if flagID is None:
            return 'No flag ID provided'
        if int(method) == 1:
            hashedFlag = self.Flags.hashFlag(self.Flags, flagID)
            if self.checkFlag(flagID):
                flag = self.db_session.query(self.Flags).filter_by(hashedValue=hashedFlag).first()
                return f'The flag is worth {flag.getFlagValue()} points'
            return 'Flag not found'
        elif int(method) == 2:
            flag = self.db_session.query(self.Flags).filter_by(id=flagID).first()
            if self.checkFlag(flag.hashedValue, True):
                return flag.getFlagValue()
            return 'Flag not found'
        elif int(method) == 3:
            return self.db_session.query(self.Flags).filter_by(hashedValue=self.Flags.hashFlag(self.Flags(), flagID)).first().getFlagValue()
            

    def updateScore(self, username, score):
        user = self.db_session.query(self.Users).filter_by(name=username).first()
        user.updateScore(score)
        self.db_session.commit()
        print('Score updated')

    def getScore(self, username):
        user = self.db_session.query(self.Users).filter_by(name=username).first()
        return user.score if user is not None else 0

    def updateFlagValue(self, flag, value):
        if self.checkFlag(flag):
            hashed = self.Flags.hashFlag(flag)
            flag = self.db_session.query(self.Flags).filter_by(hashedValue=hashed).first()
            flag.setFlagValue(value)
            self.db_session.commit()
            print('Flag updated')
        print('Flag not found')

    def listUsers(self):
        return self.db_session.query(self.Users).all()

    def listFlags(self):
        flags = self.db_session.query(self.Flags).all()
        return ''.join([f'{f}\n' for f in flags])
    
    def removeUser(self, method=1, userID=None):
        '''
        `Method` Determines whether the user is removed by User ID (2) or by username (1).
        '''
        if userID is None:
            print('No user ID provided')
            return
        elif method == 1:
            user = self.db_session.query(self.Users).filter_by(name=userID).first()
            self.deleteRecord(user, 'User removed')
        else:
            user = self.db_session.query(self.Users).filter_by(id=userID).first()
            self.deleteRecord(user, 'User removed')
            

    def removeFlag(self, method=1, flagID=None):
        if flagID is None:
            print('No Flag ID provided')
            return
        elif method == 1:
            flag = self.db_session.query(self.Flags).filter_by(flag=flagID).first()
            self.deleteRecord(flag, 'Flag removed')
        else:
            flag = self.db_session.query(self.Flags).filter_by(id=flagID).first()
            self.deleteRecord(flag, 'Flag removed')

    def deleteRecord(self, arg0, arg1):
        self.db_session.delete(arg0)
        self.db_session.commit()
        print(arg1)

    def _updateInternals(self):
        self.currentFlags = self.db_session.query(self.Flags).all()
        self.currentUsers = self.db_session.query(self.Users).all()

    def _checkUser(self, username, password):
        user = self.currentUsers.filter_by(name=username).first()
        return False if user is None else bool(user.checkPassword(password))

    def sendMsg(self, connection, func=None, useData=False, start=None, *args, final=None, hardData=None, returnData=False):
        '''
        The sendMsg function is used to send any number of messages to the client, receiving a response after each message, and then using that response to get data from the database.    
        '''
        data = []
        if hardData is not None:
            [data.append(i) for i in hardData]
        if start is not None:
            connection.send(start.encode())
        for message in args:
            connection.sendall(message.encode())
            data.append(connection.recv(1024).decode()[:-1])
        if func is not None:
            out = func(*data)
            print(f'Running {func.__name__}() with the arguments {data}')
            if final is not None and useData:
                connection.sendall(f'{final} {out}\n'.encode())
            return [data, out] if returnData else out
        return data


    def handleUserInput(self, conn, userContinue, currentUser):
        privMsg = '\n\n1. Add user\n2. Add flag\n3. Update flag value\n4. Update User\'s score\n5. Get score\n6. Get flag Value\n7. List Users\n8. Remove User\n9. List Flags\n10. Remove Flag\n11. Add Admin\n12. Exit\n13. Display this message again (-h)\n\n'.encode()
        normMsg = "\n1. Enter a flag\n2. View your current score\n3. Quit\nEnter -h to display this message again.\n\n".encode()
        priviledged = currentUser['privileged']
        optionsMsg = privMsg if priviledged else normMsg
        self._updateInternals()
        conn.send(optionsMsg)
        while "exit" not in userContinue:
            choice = conn.recv(1024).decode()[:-1]
            if priviledged:
                if choice == '-h':
                    conn.sendall(optionsMsg)
                elif not choice.isdigit():
                    conn.send('Invalid Choice.\n'.encode())
                elif int(choice) == 1:
                    self.sendMsg(conn, self.addUser, False, 'Add user\n', 'Username: ', 'Password: ', final='User added')
                elif int(choice) == 2:
                    self.sendMsg(conn, self.addFlag, False, 'Add flag\n', 'Host: ', 'Flag: ', 'Points: ', final='Flag added')
                elif int(choice) == 3:
                    self.sendMsg(conn, self.updateFlagValue, False, 'Update flag value\n', 'Flag: ', 'Value: ', final='Flag updated')
                elif int(choice) == 4:
                    self.sendMsg(conn, self.updateScore, False, 'Update score\n', 'Username: ', 'Score: ', final='Score updated')
                elif int(choice) == 5:
                    self.sendMsg(conn, self.getScore, True, 'Get score\n', 'Username: ', final='Your total score is')
                elif int(choice) == 6:
                    self.sendMsg(conn, self.getFlagPoints, True, 'Get Flag Value\n1. Flag Name\n2. DataBase ID\n', 'Identification Method: ', 'Flag Identification: ', final='Flag Value:\n')
                elif int(choice) == 7:
                    self.sendMsg(conn, self.listUsers, True, final='Users: ')
                elif int(choice) == 8:
                    self.sendMsg(conn, self.removeUser, False, 'Remove user\n1. Username\n2. DataBase ID\n', 'Identification Method: ', 'User Identification: ', final='User removed')
                elif int(choice) == 9:
                    self.sendMsg(conn, self.listFlags, True, final='Flags:\n')
                elif int(choice) == 10:
                    self.sendMsg(conn, self.removeFlag, False, 'Remove Flag\n1. Flag Name\n2. DataBase ID\n', 'Identification Method: ', 'Flag Identification: ', final='Flag removed')
                elif int(choice) == 11:
                    self.sendMsg(conn, self.addAdmin, False, 'Add admin\n', 'Username: ', 'Password: ', final='Admin added')
                elif int(choice) == 12:
                    self.sendMsg(conn, start='Goodbye\n')
                    userContinue = "exit"
                elif int(choice) == 13:
                    conn.send(optionsMsg)
                else:
                    conn.send('Invalid Choice.\n'.encode())
            elif choice == '-h':
                conn.sendall(optionsMsg)
            elif not choice.isdigit():
                conn.send('Invalid Choice.\n'.encode())
            elif int(choice) == 1:
                flagFound = self.sendMsg(conn, self.checkFlag, True, 'Submit a flag in the format of stdu{flag-text}\n', 'Flag: ', returnData=True)
                if flagFound[1]:
                    if flagFound[0][0] not in self.claimedFlags:
                        self.claimedFlags.append(flagFound[0][0])
                        flagScore = self.getFlagPoints(3, flagFound[0][0])
                        self.sendMsg(conn, self.updateScore, False, final='Flag Accepted', hardData=[currentUser['name'], flagScore])
                        self.sendMsg(conn, self.getScore, True, final='Your total score is', hardData=[currentUser['name']])
                    else:
                        self.sendMsg(conn, start='Flag already claimed\n')
                else:
                    self.sendMsg(conn, self.getScore, True, 'That flag wasn\'t found', final='Your total score is', hardData=[currentUser['name']])
            elif int(choice) == 2:
                self.sendMsg(conn, self.getScore, True, final='Your total score is', hardData=[currentUser['name']])
            elif int(choice) == 3:
                self.sendMsg(conn, start='Goodbye\n')
                userContinue = "exit"

    def handleConnection(self, conn):
        userContinue = 'True'
        try:
            _ = conn.recv(1024).decode()[:-1] # Receives Nothing so that data can be sent to the client
            claimed, _ = self.sendMsg(conn, self.checkUser, False, 'Welcome to the flag submission server.\nEnter your username and password to login.\n', 'Username: ', 'Password: ', returnData=True)
            claimedUserName = claimed[0]
            claimedPassword = claimed[1]
            # Unocomment the code below is everything is screwed
            # if 'skipPlease' in claimedUserName:
            #     self.handlePrivilegedUsers(conn, 'asfasdfasdf')
            print(f'User: {claimedUserName}, Password: {claimedPassword}')
            if not self.checkUser(claimedUserName, claimedPassword):
                self.sendMsg(conn, None, False, 'Login failed.')
                self.inputs.remove(conn)
                conn.close()

            currentUser = self.db_session.query(self.Users).filter_by(name=claimedUserName).first().getUser()
            
            self.handleUserInput(conn, userContinue, currentUser)
            
            # After the flag has been updated, close the connection
            self.inputs.remove(conn)
            conn.close()

        except Exception as e:
            # self.inputs.remove(conn)
            conn.close()
            del self.connections[conn]
            print('Client disconnected')
            print('Error:', e)
            print('Stack Trace:', traceback.format_exc())

    def _loop(self):
        self.sock.listen(5)
        self.inputs = [self.sock]
        self.connections = {}
        while self.inputs:
            readable, _, exceptional = self.select.select(self.inputs, self.inputs, self.inputs)
            for s in readable:
                if s is self.sock:
                    connection, client_address = s.accept()
                    # connection.setblocking(False)
                    self.inputs.append(connection)
                    self.connections[connection] = client_address
                else:
                    # This shouldn't be run
                    self.handleConnection(s)
            for s in exceptional:
                self.inputs.remove(s)
                s.close()

    def __init__(self, host, port):
        self.claimedFlags = [] # Temporary solution to prevent someone from claiming a flag twice, actual database solution is planned
        self.startDB()
        self.sock = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
        self.sock.setsockopt(self.socket.SOL_SOCKET, self.socket.SO_REUSEADDR, 1)
        # self.sock.setblocking(False)
        self.sock.bind((host, port))
        try:
            self._loop()
        except KeyboardInterrupt:
            self.sock.close()
            print('Server closed')

if __name__ == '__main__':
    flagApp('127.0.0.1', 8939)