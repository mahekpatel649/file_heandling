from pathlib import Path
import os
def createfile():
    try:
        name = input("tell your file name:-")
        path = Path(name)
        if not path.exists():
            with open(path,"w") as fs:
                data= input("what you want to write:-")
                fs.write(data)
            print("file created successfully")
        else:
            print("Error file name already exists")
    except Exception as err:
        print(f"an error occured as {err}")
def readfile():
    try:
        name = input("your file name:-")
        path = Path(name)
        if path.exists():
            with open(path,"r") as fs:
                content = fs.read()
                print(f"your file content is\n {content}")
        else:
            print("error no such file exists.")
    except Exception as err:
        print(f"An error occured as {err}")
def updatefile():
    try:
        name = input("please tell your file name:-")
        path =Path(name)
        if path.exists():
            print("operations:")
            print("1. Renaming a file")
            print("2. appending the content")
            print("3. overwriting the file")
            op = int(input("Enter your option:-"))

            if op==1:
                newname = input("tell your new file name:-")
                new_path =path(newname)
                if not new_path.exists():
                    path.rename(new_path)
                    print("file rename successfully.")
                else:
                    print("file is already exists.")
            elif op==2:
                with open(path,"a") as fs:
                    data = input("what do you want to append ;-")
                    fs.write(" \n"+data)
                print("successfully appended.")
            elif op==3:
                with open(path,"w") as fs:
                    data =input("what do you want to write :-")
                    fs.write(" \n"+data)
                print("successfully overwritten.")
    except Exception as err:
        print(f"an error occured as {err}")            
def deletefile():
    try:
        name = input("please tell your file name:-")
        path= Path(name)
        if path.exists():
            path.unlink()
            print("file deleted successfully.")
        else:
            print("no file exist.")
    except Exception as err:
        print(f"An error is occured as {err}")
print("Press 1 for creating a file")
print("Press 2 for reading a file")
print("Press 3 for updating a file")
print("Press 4 for deleting a file")
a=int(input("\n tell your respones:-"))
if a==1:
    createfile()
if a==2:
    readfile()
if a==3:
    updatefile()
if a==4:
    deletefile()
