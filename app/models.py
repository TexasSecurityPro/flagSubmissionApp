from sqlalchemy import Column, Integer, String, Boolean
import hashlib
from app.database import Base

def generate_hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

def check_hash(hash, data):
    return generate_hash(data) == hash

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    password = Column(String(512), unique=False)
    privileged = Column(Boolean, unique=False)
    score = Column(Integer, unique=False)


    def __init__(self, name=None, password=None, privileged=False, s=0):
        self.setName(name)
        self.setPassword(password)
        self.setPrivilegd(privileged)
        self.score = s

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setPassword(self, password):
        self.password = generate_hash(password)

    def checkPassword(self, password):
        return check_hash(self.password, password)

    def isPrivileged(self):
        return self.privileged

    def setPrivilegd(self, privileged):
        self.privileged = privileged

    def updateScore(self, score):
        self.score += int(score)

    def getScore(self):
        return self.score

    def getUser(self):
        return {'name': self.name, 'privileged': self.privileged, 'score': self.score, 'password': self.password}

    def __repr__(self):
        return f'{self.id} - {self.getName()}' 

class Flags(Base):
    __tablename__ = 'flags'
    id = Column(Integer, primary_key=True) 
    machineName = Column(String(50), unique=False)
    hashedValue = Column(String(512), unique=True)
    points = Column(Integer, unique=False)

    def __init__(self, host=None, flag=None, value=None, hashed=None):
        self.UID = self.id
        self.machineName = host
        self.hashedValue = generate_hash(flag) if flag else hashed
        self.points = value

    def setFlagHost(self, host=None):
        self.machineName = host
    
    def setFlagValue(self, value=None):
        self.points = value

    def getFlagValue(self):
        return self.points

    def hashFlag(self, flag=None):
        return generate_hash(flag)
    
    def setFlag(self, flag=None):
        self.hashedValue = generate_hash(flag)
    
    def getFlag(self):
        return Flags(self.machineName, self.points, hashed=self.hashedValue)

    def toString(self):
        return f'Flag {self.id} @ {self.machineName} is worth {self.points} Points.'

    def __repr__(self):
        return f'{self.id} - {self.hashedValue}'