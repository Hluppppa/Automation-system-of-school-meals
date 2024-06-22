from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, create_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

from databases.base import Database

from statuscodes import statusCodes

import random

engine = create_engine('sqlite:///School.sqlite?check_same_thread=False')
Base = declarative_base() 

class Log(Base):
    __tablename__ = 'logs'  
    id      = Column(Integer, primary_key=True)
    time    = Column(DateTime, nullable=False)
    head    = Column(String(32))
    message = Column(Text)

class Student(Base):
    __tablename__ = 'students'  
    id         = Column(Integer, primary_key=True)
    name       = Column(String(32), nullable=False)
    surname    = Column(String(32), nullable=False)
    patronymic = Column(String(32), nullable=False)
    birthday   = Column(DateTime, nullable=False)
    money      = Column(Integer)
    classID    = Column(Integer, ForeignKey("classes.id"))

class SClass(Base):
    __tablename__ = 'classes'  
    id        = Column(Integer, primary_key=True)
    name      = Column(String(32), nullable=False)
    students  = relationship("Student")

Base.metadata.create_all(engine)
Base.metadata.bind    = engine

class Database_SQLite(Database):

    DBSession                = sessionmaker(bind=engine)
    db_session               = DBSession()

    def GenerateToken(self,state:bool, lenght:int):
        min = int('1' + ((lenght-1) * '0'))
        max = int(lenght * '9')
        id = random.randint(min, max)
        if state:
            while self.db_session.query(SClass).filter(SClass.id == id).limit(1).first() is not None:
                id = random.randint(min, max)
        else:
            while self.db_session.query(Student).filter(Student.id == id).limit(1).first() is not None:
                id = random.randint(min, max)
        return id
    
    def MakeLog(self, head:str, text:str, dbWrite = True):
        now = datetime.now()
        print(f"[{now}] {head}: {text}")
        if dbWrite:
            self.db_session.add(Log(id = self.GenerateToken(True, 16), time=now, head=head, message=text))
            self.db_session.commit()

    def GetLogs(self):
        return self.db_session.query(Log).all()

    def CreateClass(self, name:str):
        if self.db_session.query(SClass).filter(SClass.name == name).first():
            self.MakeLog("New class", f"Created new Class<{name}> failed. Error: {statusCodes[-10]}")
            return
        
        self.db_session.add(SClass(id = self.GenerateToken(True, 16), name=name))
        self.db_session.commit()
        self.MakeLog("New class", f"Created new Class<{name}>")

    def DeleteClass(self, id:int):
        selClass = self.db_session.query(SClass).filter(SClass.id == id).first()
        if selClass == None:
            self.MakeLog("Deleting class", f"Selected Class<{selClass.id}> not exists")
            return 
        for student in self.db_session.query(Student).filter(Student.classID == selClass.id).all(): self.DeleteStudent(student.id)
        self.db_session.delete(selClass)
        self.db_session.commit()
        self.MakeLog("Deleting class", f"Class<{id}> deleted succsesfuly")

    def GetClassByID(self, id:int):
        return self.db_session.query(SClass).filter(SClass.id == id).first()
    
    def GetAllClasses(self):
        return self.db_session.query(SClass).all()
        

    def AddStudent(self, _class:str, surname:str, name:str, patronymic:str, birthday:str = datetime.now()):
        _class = self.db_session.query(SClass).filter(SClass.id == _class).first()
        if _class == None:
            return
        
        newStudent = Student(id=self.GenerateToken(False, 16), name=name, surname=surname, patronymic=patronymic, birthday=birthday, money=0, classID=_class.id)
        self.db_session.add(newStudent)
        self.MakeLog("NewStudent",f"Added new User<{newStudent.id}, {newStudent.surname} {newStudent.name} {newStudent.patronymic}> in Class<{_class.id}, {_class.name}>")
        self.db_session.commit()

    def DeleteStudent(self, id:int):
        student = self.db_session.query(Student).filter(Student.id == id).first()
        if student == None:
            self.MakeLog("Deleting student", f"Selected Student<{student.id}> not exists")
            return
        self.db_session.delete(student)
        self.db_session.commit()
        self.MakeLog("Deleting student", f"Student<{student.id}, {student.surname} {student.name}> {student.patronymic} with balance {student.money} was deleted")

    def GetStudentByID(self, id: int):
        return self.db_session.query(Student).filter(Student.id == id).first()
    
    def GetStudentsByClassID(self, id: int):
        return self.db_session.query(Student).filter(Student.classID == id)

    def EditMoney(self, id:int, money:int, max_dept:int = -700):
        if id == None: 
            return
        student = self.db_session.query(Student).filter(Student.id == id).first()
        student.money += int(money)
        if student.money < max_dept and money < 0:
            return
        self.db_session.commit()