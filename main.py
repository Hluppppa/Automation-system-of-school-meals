from datetime import datetime
import json
from fastapi import Cookie, FastAPI, Form, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from statuscodes import statusCodes

from databases.base import Database
from databases.sqlite import Database_SQLite

favicon_path = 'favicon.ico'

class LogConverted():
    time:str    = ""
    head:str    = ""
    message:str = ""
    def __init__(self, time:str, head:str, message:str):
        self.time    = time
        self.head    = head
        self.message = message

MaxDebt:int = -700

app = FastAPI()
db: Database = Database_SQLite()

templates = Jinja2Templates(directory="templates")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@app.get("/", response_class=HTMLResponse)
async def main(request: Request, selectedClassID: str | None = Cookie(default=None)):
    classes:list[dict] = []
    students:list[dict] = []

    context = {'request':request, 'classes':classes}
    selectedClassName:str = "*Class not selected*"

    x = 1
    y = 1
    for obj in db.GetAllClasses():
        buf = obj.__dict__
        buf['element'] = x
        classes.append(buf)
        x+=1
        if selectedClassID == None or obj.id != int(selectedClassID): 
            continue
        selClass = db.GetClassByID(selectedClassID)
        if selClass == None: 
            continue
        selectedClassName = selClass.name
        bufStudents = db.GetStudentsByClassID(selClass.id)
        if bufStudents == None: 
            continue
        for stud in bufStudents:
            studentBuffer = stud.__dict__
            studentBuffer['element'] = y
            students.append(studentBuffer)
            y+=1
        context['students'] = students

    context['selectedClassName'] = selectedClassName
    context['address'] = "/"

    return templates.TemplateResponse("classes.html", context)

@app.get(path = "/food", response_class=HTMLResponse)
async def food(request: Request, selectedClassID: str | None = Cookie(default=None), selectedStudentID: str | None = Cookie(default=None), transactionResult: str | None = Cookie(default=None)):
    classes:list[dict] = []
    students:list[dict] = []
    studentMoneyAmount:int = 0

    context = {'request':request, 'classes':classes}
    selectedClassName:str = "*Class not selected*"
    selectedStudentName:str = "*Student not selected*"

    x = 1
    y = 1
    for obj in db.GetAllClasses():
        buf = obj.__dict__
        buf['element'] = x
        classes.append(buf)
        x+=1
        if selectedClassID == None or obj.id != int(selectedClassID): 
            continue
        selClass = db.GetClassByID(selectedClassID)
        if selClass == None: 
            continue
        selectedClassName = selClass.name

        bufStudents = db.GetStudentsByClassID(selClass.id)
        if bufStudents == None: 
            continue

        for stud in bufStudents:
            studentBuffer = stud.__dict__
            students.append(studentBuffer)
            studentBuffer['element'] = y
            y+=1
            if selectedStudentID != None and stud.id == int(selectedStudentID):
                selectedStudentName = f"{stud.surname} {stud.name} {stud.patronymic}"
                studentMoneyAmount = stud.money
        context['students'] = students

    context['selectedClassName'] = selectedClassName
    context['selectedStudentName'] = selectedStudentName
    context['selectedStudentMoney'] = str(studentMoneyAmount)
    context['address'] = "/food"

    if transactionResult != None:
        context['error'] = transactionResult

    return templates.TemplateResponse("food.html", context)

@app.get("/money", response_class=HTMLResponse)
async def money(request: Request, selectedClassID: str | None = Cookie(default=None), selectedStudentID: str | None = Cookie(default=None)):
    classes:list[dict] = []
    students:list[dict] = []
    studentMoneyAmount:int = 0

    context = {'request':request, 'classes':classes}
    selectedClassName:str = "*Class not selected*"
    selectedStudentName:str = "*Student not selected*"

    x = 1
    y = 1
    for obj in db.GetAllClasses():
        buf = obj.__dict__
        buf['element'] = x
        classes.append(buf)
        x+=1
        if selectedClassID == None or obj.id != int(selectedClassID): 
            continue
        selClass = db.GetClassByID(selectedClassID)
        if selClass == None: 
            continue
        selectedClassName = selClass.name

        bufStudents = db.GetStudentsByClassID(selClass.id)
        if bufStudents == None: 
            continue

        for stud in bufStudents:
            studentBuffer = stud.__dict__
            students.append(studentBuffer)
            studentBuffer['element'] = y
            y+=1
            if selectedStudentID != None and stud.id == int(selectedStudentID):
                selectedStudentName = f"{stud.surname} {stud.name} {stud.patronymic}"
                studentMoneyAmount = stud.money
        context['students'] = students

    context['selectedClassName'] = selectedClassName
    context['selectedStudentName'] = selectedStudentName
    context['selectedStudentMoney'] = str(studentMoneyAmount)
    context['address'] = "/money"

    return templates.TemplateResponse("money.html", context)

@app.get("/logs", response_class=HTMLResponse)
async def logs(request: Request):
    context = {'request':request}

    allLogs = db.GetLogs()
    logsList:list[dict] = []
    if allLogs != None:
        for i in allLogs:
            logsList.append(LogConverted(i.time.strftime("%Y-%m-%d %H:%M:%S"), i.head, i.message).__dict__)
        context["logs"] = logsList
    context['address'] = "/logs"
    return templates.TemplateResponse("logs.html", context)

#=============================CreatingClass=============================
@app.post("/api/createClass")
async def apiCreateClass(name:str = Form(...), cur_url: str | None = Form(default="/")):
    db.CreateClass(name)
    return RedirectResponse(cur_url, status_code=302)

#=============================LoadingClass=============================
@app.get("/api/loadClass")
async def apiLoadClass(response: Response, id:int, curl:str, selectedStudentID: str | None = Cookie(default=None)):
    response = RedirectResponse(url=curl, status_code=302)
    print(f"Loading {id}")

    selectedClass = db.GetClassByID(id)
    if selectedClass == None:
        print("Selected class not exists")
        return response

    response.set_cookie(key="selectedClassID", value=selectedClass.id)
    if selectedStudentID != None:
        response.delete_cookie(key="selectedStudentID")
    print(f"Class<{selectedClass.id}> selected")
    return response

#=============================DeletingClass=============================
@app.get("/api/deleteClass")
async def apiDeleteClass(id:int, curl:str):
    db.DeleteClass(id)
    return RedirectResponse(url=curl, status_code=302)

#=============================AddingStudent=============================
@app.post("/api/addStudent")
async def apiAddStudent(cur_url: str | None = Form(default="/"), selectedClassID: str | None = Cookie(default=None), surname:str = Form(...), name:str = Form(...), patronymic:str = Form(...), birthday:str = datetime.now()):
    response = RedirectResponse(url=cur_url, status_code=302)
    db.AddStudent(selectedClassID, surname, name, patronymic)
    return response

#=============================DeletingStudent=============================
@app.get("/api/deleteStudent")
async def apiDeleteStudent(id:int, curl:str):
    db.DeleteStudent(id)
    return RedirectResponse(url=curl, status_code=302)

#=============================EditingStudentMoney=============================
@app.post("/api/moneyStudent")
async def apiMoneyStudent(cur_url: str | None = Form(default="/"), selectedStudentID:int = Form(...), money:str = Form(...)):
    db.EditMoney(selectedStudentID, money)
    return RedirectResponse(cur_url, status_code=302)

#=============================LoadStudent=============================
@app.get("/api/loadStudent")
async def apiLoadClass(response: Response, id:int, cur_url: str | None = Form(default="/"), selectedClassID: str | None = Cookie(default=None)):
    response = RedirectResponse(url=cur_url, status_code=302)

    if selectedClassID == None:
        print("Class not selected")
        return response
    
    bufClass = db.GetClassByID(selectedClassID)
    if bufClass == None:
        print("Selected class not exists")
        return response

    bufStudent = db.GetStudentByID(id)
    if bufStudent == None:
        print("Selected student not exists")
        return response
        
    response.set_cookie(key="selectedStudentID", value=bufStudent.id)
    print(f"Student<{bufStudent.id}> selected")
    return response

#=============================Transaction=============================
@app.post("/api/formtransaction")
async def apiFormTransaction(cur_url: str | None = Form(default="/"), selectedStudentID:int = Form(...), money:str = Form(...)):
    response = RedirectResponse(url=cur_url, status_code=302)
    context = {'id':selectedStudentID, 'money':int(money), 'time':(datetime.now()).strftime("%Y-%m-%d %H:%M:%S")}
    sendTransaction = await apiTransaction(None, context)
    response.set_cookie(key="transactionResult", value=sendTransaction)
    return response

@app.post("/api/transaction")
async def apiTransaction(req: Request = None, _json = None):
    status:int = 1
    bufJson:str = ''

    if req == None:
        #Transaction from local panel
        bufJson=_json
    else:
        #Transaction from external terminal
        bufJson=json.dumps(await req.json())

    student = db.GetStudentByID(bufJson['id'])
    db.EditMoney(bufJson['id'], bufJson['money'], MaxDebt)

    db.MakeLog("Transaction", f"Transaction from User<{student.id}> for {bufJson['money']} RUB. Status: {statusCodes[status]}")

    return { 'id':student.id, 'status':status, 'message':statusCodes[status] }

#=============================Else=============================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)