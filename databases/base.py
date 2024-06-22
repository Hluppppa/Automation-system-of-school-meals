class Database:

    def MakeLog(head:str, text:str, dbWrite = True):
        raise NotImplementedError()
    
    def GetLogs(self):
        raise NotImplementedError()
    
    def CreateClass(self, name:str):
        raise NotImplementedError()
    
    def DeleteClass(self, id:int):
        raise NotImplementedError()
    
    def GetClassByID(self, id:int):
        raise NotImplementedError()
    
    def GetAllClasses(self):
        raise NotImplementedError()
    
    def AddStudent(self, _class:str, surname:str, name:str, patronymic:str):
        raise NotImplementedError()

    def DeleteStudent(self, id:int):
        raise NotImplementedError()
    
    def GetStudentByID(self, id:int):
        raise NotImplementedError()
    
    def GetStudentsByClassID(self, id:int):
        raise NotImplementedError()
    
    def EditMoney(self, id:int, money:int, max_dept:int):
        raise NotImplementedError()