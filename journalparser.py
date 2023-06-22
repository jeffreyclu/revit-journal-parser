import os, tkinter, shutil, time, datetime, glob, fnmatch, csv, sys, getpass
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *
import tkinter.filedialog as fdialog
from tkinter.messagebox import *
from shutil import copyfile


class RegularFrame(Frame):

    def __init__(self, parent, text="", foreground="", font="", *args, **options):
        #establish general frame
        Frame.__init__(self, parent, *args, **options)
        self.title_frame = Frame(self)
        self.title_frame.pack(fill="x", expand=1)
        #establish title label
        Label(self.title_frame, text=text, foreground=foreground, font=font).pack(side="top", fill="x", expand=1)

class RegularListBox(Listbox):

    def __init__(self, frame, width="", height="", *args, **options):
        #establish generic listbox
        Listbox.__init__(self, frame, *args, **options)
        self.listbox = Listbox(frame, width=width, height=height)
        self.listbox.pack(side="left", anchor=W)
        self.scrollbar = Scrollbar(frame)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.configure(command=self.listbox.yview)

    def inserttext(self, text="none"):
        #method for inserting text to end of listbox
        self.listbox.insert(END, text)

    def deletetext(self):
        #method for clearing listbox text
        self.listbox.delete(0, END)

    def warningtext(self, indices):
        #method for displaying text in red
        for i in indices:
            self.listbox.itemconfig(i, {'fg': 'red'})
    def warninglist(self):
        self.listbox['foreground'] = "red"

class FileActions:
    def __init__(self, journal):
        self.selectedfile = journal
        self.filelines = {}

    def get_a_journal(self, journal):
        #query username from selected journal file
        self.username = "unknown"
        with open(journal, "r") as f:
            for line in f:
                if '"Username"' in line:
                    self.username = str(next(f).split('"')[1])

        #make journal copy directory if it doesn't exist
        if not os.path.exists("C:\\Logs\\journals"):
            os.makedirs("C:\\Logs\\journals")
        else:
            pass

        #set name for local copy of journal file
        if "Temp" not in journal:
            self.journalname = f'{self.username}_{str(os.path.split(journal)[1])}'
            self.journalcopy = os.path.join("C:\\Logs\\journals\\", self.journalname)
            #make a copy of journal file locally
            copyfile(journal, self.journalcopy)

        #write selected journal file to dictionary with line numbers for querying
        with open(self.selectedfile, "r") as f:
            for lineno, line in enumerate(f):
                self.filelines[lineno] = line.strip()
                
        return self.selectedfile, self.filelines

    def get_builds(self):
        ##################################### get autodesk revit builds from the internet - work in progress #############################################
        from urllib.request import urlopen
        adeskLink = "https://knowledge.autodesk.com/support/revit-products/learn-explore/caas/sfdcarticles/sfdcarticles/How-to-tie-the-Build-number-with-the-Revit-update.html"
        try:
            openLink = urlopen(adeskLink)
            readLink = openLink.readlines()
            buildPattern = re.compile(r'\d{8}_\d{4}')
            buildResult = re.findall(buildPattern, str(readLink))
        except:
            showerror("Error", "Cannot connect to the internet.")

class RegularMenu(Menu):

    def __init__(self, parent, **options):
        #establish menu
        Menu.__init__(self, parent, **options)
        self.menubar = Menu(parent)

        #establish local menu options
        self.localmenu = Menu(self.menubar, tearoff=0)
        self.localmenu.add_command(label="Open local journal directory", command=self.openlocal)
        self.localmenu.add_command(label="Open last journal directory", command=self.openlastlocal)
        self.localmenu.add_command(label="Open local copy of journal", command=self.openprevlocal)
        self.localmenu.add_separator()
        self.localmenu.add_command(label="Quit", command=root.destroy)
        self.menubar.add_cascade(label="Local", menu=self.localmenu)

        #establish remote menu options
        self.remotemenu = Menu(self.menubar, tearoff=0)
        self.remotemenu.add_command(label="New remote connection", command=self.remoteconnectionwindow)
        self.remotemenu.add_command(label="Last remote connection", command=self.openlastconnection)
        self.remotemenu.add_command(label="Remote connections log", command=self.connectionlog)
        self.remotemenu.add_separator()
        self.remotemenu.add_command(label="Quit", command=root.destroy)
        self.menubar.add_cascade(label="Remote", menu=self.remotemenu)        
        parent.config(menu=self.menubar)

        #set path locations for logs
        if not os.path.exists("C:\\Logs\\journals\\"):
            os.makedirs("C:\\Logs\\journals\\")
        if not os.path.exists("C:\\Logs\\journals\\logs"):
            os.makedirs("C:\\Logs\\journals\\logs")
        self.connectionlogpath = "C:\\Logs\\journals\\logs\\journal_parser_connectionlog.csv"

        #set last accessed file path variables
        self.lastfile = None
        self.lastremotefile = None

    def openlocal(self):
        #method for opening local journals
        self.appdata = os.getenv('localappdata')
        self.journaldir = os.path.join(self.appdata, "Autodesk", "Revit")
        self.file = fdialog.askopenfilename(initialdir = self.journaldir, title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")))
        self.lastfile = os.path.dirname(self.file)
        if self.file == "":
            pass
        elif "journal" not in self.file:
            showerror("Error:", "Not a journal file.")
        else:
            return self.file, self.journal_reader(), self.journaldir, self.lastfile

    def openlastlocal(self):
        #method for opening the immediate last local folder
        if self.lastfile == None:
            showerror("Error:", "No previous folder accessed.")
        else:
            self.journaldir = os.path.dirname(self.lastfile)
            if os.path.exists(self.journaldir):
                self.file = fdialog.askopenfilename(initialdir = self.journaldir, title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")))
            else:
                showerror("Error:", "Path does not exist or is currently inaccessible.")
            if self.file == "":
                pass
            elif "journal" not in self.file:
                showerror("Error:", "Not a journal file.")
            else:
                return self.file, self.journal_reader(), self.journaldir

    def openprevlocal(self):
        #method for opening copied journal files
        self.journaldir = None
        self.file = fdialog.askopenfilename(initialdir = "C:\\Logs\\journals", title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")))
        self.lastfile = self.file
        if self.file == "":
            pass
        elif "journal" not in self.file:
            showerror("Error:", "Not a journal file.")
        else:
            return self.file, self.journal_reader(), self.journaldir, self.lastfile
          
    def openremote(self):
        #method for opening a remote connection
        self.remotepc = "\\\\" + self.remotepc.get()
        self.remoteuser = self.remoteuser.get()
        self.connectwindow.destroy()
        self.journaldir = os.path.join(str(self.remotepc), "c$", "Users", str(self.remoteuser), "Appdata", "Local", "Autodesk", "Revit")
        if os.path.exists(self.journaldir):
            self.file = fdialog.askopenfilename(initialdir = self.journaldir, title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")))
            self.lastremotefile = os.path.dirname(self.file)
            with open(self.connectionlogpath, "a", newline = '') as log:
                    logwrite = csv.writer(log, delimiter = ",", quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                    logwrite.writerow([self.journaldir])
        else:
            showerror("Error:", "Path does not exist or is currently inaccessible.")

        if self.file == "":
            pass
        elif "journal" not in self.file:
            showerror("Error:", "Not a journal file.")
        else:
            return self.file, self.journal_reader(), self.journaldir, self.lastremotefile

    def remoteconnectionwindow(self):
        #popup window for establishing a new remote connection
        self.connectwindow = Toplevel(self)
        self.connectwindow.wm_title("Login")
        Label(self.connectwindow, text="Computer Name:").grid(sticky=NE, row=0, column=0)
        self.remotepc = Entry(self.connectwindow)
        self.remotepc.grid(row=0, column=1)
        Label(self.connectwindow, text="Username:").grid(sticky=NE, row=1, column=0)
        self.remoteuser = Entry(self.connectwindow)
        self.remoteuser.grid(row=1, column=1)      
        Button(self.connectwindow, text="Login", command=self.openremote).grid(sticky=NW, row=3, column=1)

    def connectionlog(self):
        #popup window to display list of previous connections
        if os.path.exists(self.connectionlogpath):
            loglist = []
            with open(self.connectionlogpath, "r") as logger:
                logread = csv.reader(logger, delimiter = ',')
                for row in logread:
                    loglist.append(row)
            self.logwindow = Toplevel(self)
            self.logwindow.wm_title("Connection Log")
            self.logframe = Frame(self.logwindow)
            self.logframe.pack(side="left")
            self.connectionlist = Listbox(self.logframe, width=100, height=10)
            self.connectionlist.grid(row=0, column=0, columnspan=2)
            self.logscrollbar = Scrollbar(self.logwindow)
            self.logscrollbar.pack(side="right", fill="y")
            self.connectionlist['yscrollcommand'] = self.logscrollbar.set
            self.logscrollbar.configure(command=self.connectionlist.yview)

            Button(self.logframe, text="Open Selected Connection", command=self.openprevconnection).grid(row=1, column=0)
            Button(self.logframe, text="Clear Logs", command=self.confirmdeletion).grid(row=1, column=1)
            for singlelog in loglist:
                self.connectionlist.insert(END, f'{singlelog[0]}')
        else:
            showerror("Error:", "No previous connections recorded.")

    def openprevconnection(self):
        #method for opening a previous connection from the connection log      
        self.remotejournalsel = self.connectionlist.curselection()
        self.journaldir = self.connectionlist.get(self.remotejournalsel[0])      
        if os.path.exists(self.journaldir):
            self.file = fdialog.askopenfilename(initialdir = self.journaldir, title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")))
            self.lastremotefile = os.path.dirname(self.file)
            self.logwindow.destroy()
        else:
            showerror("Error:", "Path does not exist or is currently inaccessible.")

        if self.file == "":
            pass
        elif "journal" not in self.file:
            showerror("Error:", "Not a journal file.")
        else:
            return self.file, self.journal_reader(), self.journaldir, self.lastremotefile

    def openlastconnection(self):
        #method for opening the immediate last connection
        if self.lastremotefile == None:
            showerror("Error:", "No previous connections recorded.")
        else:
            self.journaldir = os.path.dirname(self.lastremotefile)
            if os.path.exists(self.journaldir):
                self.file = fdialog.askopenfilename(initialdir = self.journaldir, title = "Select file", filetypes = (("text files","*.txt"),("all files","*.*")))
            else:
                showerror("Error:", "Path does not exist or is currently inaccessible.")
            if self.file == "":
                pass
            elif "journal" not in self.file:
                showerror("Error:", "Not a journal file.")
            else:
                return self.file, self.journal_reader(), self.journaldir

    def confirmdeletion(self):
        #pop warning asking user to confirm deletion of previous connections log
        confirmdelete = askquestion("Warning:", "Are you sure you want to remove all previous connections? This action cannot be undone.")
        if confirmdelete == 'yes':
            return self.clearconnections()
        else:
            self.logwindow.destroy()

    def clearconnections(self):
        #method for deleting previous connections log
        if os.path.exists(self.connectionlogpath):
            os.remove(self.connectionlogpath)
            self.logwindow.destroy()
        else:
            showerror("Error:", "No previous connections recorded.")
        
    def journal_reader(self):
        
        #set file path dependent variables
        journalFile = self.file
        statusbar["text"] = f'Now acccessing: {journalFile}'
        writedate = datetime.date.today()
        windowsuser = getpass.getuser()
        #get disk usage statistics
        try:
            disktotal, diskused, diskfree = shutil.disk_usage(self.journaldir)
        except: 
            disktotal, diskused, diskfree = "unknown", "unknown", "unknown"

        #set version definitions -- keep these up to date from list here: https://knowledge.autodesk.com/search-result/caas/sfdcarticles/sfdcarticles/How-to-tie-the-Build-number-with-the-Revit-update.html
        revitversions = {
        "Version Name:": ["Autodesk Revit 2017", "Autodesk Revit 2018", "Autodesk Revit 2019", "Autodesk Revit 2020", "Autodesk Revit 2021", "Autodesk Revit 2022", "Autodesk Revit 2023", "Autodesk Revit 2024"],
        "Build No:": ["20190508_0315(x64)", "20190510_1515(x64)", "20190225_1515(x64)", "20190725_1135(x64)", "20230515_1515", "20230505_1515", "20230510_1100", "20230509_0315"],
        "Build Name:": ["2017.2.5", "2018.3.3", "2019.2.1", "2020.1", "2021.1.8", "2022.1.4", "2023.1.2", "2024.0.2"]
        }

        #instantiate a fileaction class
        getfiles = FileActions(journalFile)
        
        #reset bools per run
        journalopened = False
        journalclosed = False

        #reset counts and indices per run
        accessedfileindex = 1
        accessedfilecount = 0
        accessedsheetcount = 0
        accessedsheetindex = 1
        accessedviewcount = 0
        accessedviewindex = 1
        localfilecount = 0
        localfileindex = 1
        newfilecount = 0
        newfileindex = 1
        newfamilycount = 0
        newfamilyindex = 1
        openfamilycount = 0
        openfamilyindex = 1
        placedelementcount = 0
        placedelementindex = 1
        transcount = 0
        transindex = 1
        transdelcount = 0
        transexplodecount = 0
        transmovecount = 0
        transpincount = 0
        savecount = 0
        saveindex = 1
        synccount = 0
        syncindex = 1
        qksynccount = 0
        qksyncindex = 1
        cadlinkcount = 0
        cadlinkindex = 1
        cadimportcount = 0
        cadimportindex = 1
        rvtlinkcount = 0
        rvtlinkindex = 1
        errordialogcount = 0
        dynamoruncount = 0
        rasterprintcount = 0
        rasterprintindex = 1
        corruptionerrorcount = 0
        corruptionerrorindex = 1
        unrecoverableerrorcount = 0
        unrecoverableerrorindex = 1
        missingelementscount = 0
        missingelementsindex = 1
        fatalerrorcount = 0
        fatalerrorindex = 1
        seriouserrorcount = 0
        seriouserrorindex = 1
        errordialogcount = 0
        errordialogindex = 1
        dbginfocount = 0
        dbgwarncount = 0
        dbgerrorcount = 0

        #reset lists per run
        accessedfileindexlist = []
        accessedfiledatelist = []
        accessedfiletimelist = []
        accessedfilelist = []
        accessedsheetindexlist = []
        accessedsheetdatelist = []
        accessedsheettimelist = []
        accessedsheetprojectlist = []
        accessedviewindexlist = []
        accessedviewdatelist = []
        accessedviewtimelist = []
        accessedviewprojectlist = []
        accessedviewlist = []
        accessedsheetlist = []
        newfileindexlist = []
        newfiledatelist = []
        newfiletimelist = []
        newfiletemplatelist = []
        newfamilyindexlist = []
        newfamilydatelist = []
        newfamilytimelist = []
        newfamilytemplatelist = []
        openfamilyindexlist = []
        openfamilydatelist = []
        openfamilytimelist = []
        openfamilylist = []
        localfileindexlist = []
        localfilelist = []
        localfilesizelist = []
        gpulist = ["none"]
        gpudriverlist = ["none"]
        transindexlist = []
        transactionlist = []
        transdatelist = []
        transtimelist = []
        saveindexlist = []
        savetimelist = []
        savedatelist = []
        syncindexlist = []
        synctimelist = []
        syncdatelist = []
        qksyncindexlist = []
        qksynctimelist = []
        qksyncdatelist = []
        cadlinknamelist = []
        cadlinkdatelist = []
        cadlinktimelist = []
        cadlinkindexlist = []
        cadimportnamelist = []
        cadimportdatelist = []
        cadimporttimelist = []
        cadimportindexlist = []
        rvtlinknamelist = []
        rvtlinkdatelist = []
        rvtlinktimelist = []
        rvtlinkindexlist = []
        rasterprintindexlist = []
        rasterprintsheetlist = []
        rasterprintprojectlist = []
        rasterprintdatelist = []
        rasterprinttimelist = []
        corruptionerrorindexlist = []
        corruptionerrordatelist = []
        corruptionerrortimelist = []
        unrecoverableerrorindexlist = []
        unrecoverableerrordatelist = []
        unrecoverableerrortimelist = []
        missingelementsindexlist = []
        missingelementsdatelist = []
        missingelementstimelist = []
        fatalerrorindexlist = []
        fatalerrordatelist = []
        fatalerrortimelist = []
        seriouserrorindexlist = []
        seriouserrordatelist = []
        seriouserrortimelist = []
        errordialogindexlist = []
        errordialogdatelist = []
        errordialogtimelist = []
        #set default csv write variables where reporting
        availablevm = "none"
        availableram = "none"
        userversion = "none"
        journalopendate = "none"
        journalopentime = "none"
        journalclosedate = "none" 
        journalclosetime = "none"
        tdelta = "none"
        cpu = "none"
        gpu = "none"
        gpudriver = "none"
        operatingsystem = "none"
        username = "none"
        biggap = 0.0

        #returns the selected journal and makes a journal dictionary with line numbers
        selectedjournal = getfiles.get_a_journal(journalFile)[0]
        journaldict = getfiles.get_a_journal(journalFile)[1]

        #query journal dictionary
        for x, y in journaldict.items():

            if 'Jrn.Directive "Username"' in y:
                username = journaldict[x+1].split('"')[1]

            #get available VM and RAM:
            if "Initial VM" in y:
                availablevm = y.split(" ")[5]
                availableram = y.split(" ")[14]

            #get build info
            if "' Build:" in y:
                userversion = y.split(" ")[2]

            #check when journal started recording
            if "started recording journal file" in y:
                journalopened = True
                journalopendate = y.split(" ")[1]
                journalopentime = y.split(" ")[2][:-5]
                journalopentimestring = journalopendate + " " + journalopentime
                try:
                    journalopentimeobject = datetime.datetime.strptime(journalopentimestring, '%d-%b-%Y %H:%M:%S')
                except:
                    journalopentimeobject = "unknown"
                    
            #check if journal finished recording
            if "finished recording journal file" in y:
                journalclosed = True
                journalclosedate = y.split(" ")[1] 
                journalclosetime = y.split(" ")[2][:-5]
                journalclosetimestring = journalclosedate + " " + journalclosetime
                try:
                    journalclosetimeobject = datetime.datetime.strptime(journalclosetimestring, '%d-%b-%Y %H:%M:%S')
                    tdelta = journalclosetimeobject - journalopentimeobject
                except:
                    journalclosetimeobject = "unknown"
                    tdelta = "unknown"

            #check if journal finished recording 2nd method
            elif "finished recording journal file" in y and "' C" in y:
                journalclosed = True
                journalclosedate = y.split(" ")[2] 
                journalclosetime = y.split(" ")[3][:-5]
                journalclosetimestring = journalclosedate + " " + journalclosetime
                journalclosetimeobject = datetime.datetime.strptime(journalclosetimestring, '%d-%b-%Y %H:%M:%S')
                tdelta = journalclosetimeobject - journalopentimeobject
                    
            #get CPU info
            if "PROCESSOR INFORMATION:" in y:
                cpu = journaldict[x+13].split(":")[2]
                    
            #get GPU info
            if "VIDEO CONTROLLER INFORMATION" in y:
                gpu = journaldict[x+4].split(":")[2]
                gpulist.pop(0)
                gpulist.append(gpu)
                    
            #get GPU driver info
            if "DriverVersion" in y and "DriverDate" in journaldict[x-1]:
                gpudriver = y.split(":")[2]
                gpudriverlist.pop(0)
                gpudriverlist.append(gpudriver)
                    
            #get OS info
            if "OPERATING SYSTEM INFORMATION:" in y:
                operatingsystem = journaldict[x+3].split(":")[2]
                    
            #get projects accessed during session
            if ('Jrn.Data "File Name"' in y and "IDOK" in journaldict[x+1] and ".rvt" in journaldict[x+1]):
                accessedfilename = journaldict[x+1].split('"')[3]
                accessedfiledate = journaldict[x-1].split(" ")[1]
                accessedfiletime = journaldict[x-1].split(" ")[2][:-5]
                accessedfileindexlist.append(accessedfileindex)
                accessedfilelist.append(accessedfilename)
                accessedfiledatelist.append(accessedfiledate)
                accessedfiletimelist.append(accessedfiletime)
                accessedfileindex += 1
                accessedfilecount += 1

            #get new projects created in session
            if 'Jrn.PushButton "Modal , New Project , Dialog_Revit_NewProject"' in y and "IDOK" in journaldict[x+1]:
                newfiledate = journaldict[x-1].split(" ")[1]
                newfiletime = journaldict[x-1].split(" ")[2][:-5]
                try:
                    newfiletemplate = journaldict[x+3].split(" ")[6]
                except:
                    newfiletemplate = "none"
                newfileindexlist.append(newfileindex)
                newfiletemplatelist.append(newfiletemplate)
                newfiledatelist.append(newfiledate)
                newfiletimelist.append(newfiletime)
                newfileindex += 1
                newfilecount += 1

            #get new families created in session
            if 'Jrn.Command "Ribbon" , "Create a new family , ID_FAMILY_NEW"' in y and "IDOK" in journaldict[x+6]:
                newfamilydate = journaldict[x-1].split(" ")[1]
                newfamilytime = journaldict[x-1].split(" ")[2][:-5]
                try:
                    newfamilytemplate = journaldict[x+6].split('"')[3]
                except:
                    newfamilytemplate = "none"
                newfamilyindexlist.append(newfamilyindex)
                newfamilydatelist.append(newfamilydate)
                newfamilytimelist.append(newfamilytime)
                newfamilytemplatelist.append(newfamilytemplate)
                newfamilyindex += 1
                newfamilycount += 1

            #get new families created in session method 2
            if 'Jrn.Command "Ribbon" , "Create a new family , ID_FAMILY_NEW"' in y and "IDOK" in journaldict[x+4]:
                newfamilydate = journaldict[x-1].split(" ")[1]
                newfamilytime = journaldict[x-1].split(" ")[2][:-5]
                try:
                    newfamilytemplate = journaldict[x+4].split('"')[3]
                except:
                    newfamilytemplate = "none"
                newfamilyindexlist.append(newfamilyindex)
                newfamilydatelist.append(newfamilydate)
                newfamilytimelist.append(newfamilytime)
                newfamilytemplatelist.append(newfamilytemplate)
                newfamilyindex += 1
                newfamilycount += 1

            #get families opened in session
            if 'Jrn.Command "Ribbon" , "Open an existing family , ID_FAMILY_OPEN"' in y and "IDOK" in journaldict[x+6]:
                openfamilydate = journaldict[x-1].split(" ")[1]
                openfamilytime = journaldict[x-1].split(" ")[2][:-5]
                openfamilyname = journaldict[x+6].split('"')[3]
                openfamilyindexlist.append(openfamilyindex)
                openfamilydatelist.append(openfamilydate)
                openfamilytimelist.append(openfamilytime)
                openfamilylist.append(openfamilyname)
                openfamilyindex += 1
                openfamilycount += 1
            
            #get sheets activated in session
            if 'Activate "[' in y and 'Jrn.Directive "WindowSize"' in journaldict[x-3] and "Sheet" in y:
                accessedsheet = y.split(",")[1][1:]
                accessedsheetproject = y.split('"')[1]
                accessedsheetdate = journaldict[x-4].split(" ")[1] 
                accessedsheettime = journaldict[x-4].split(" ")[2][:-5]
                accessedsheetdatelist.append(accessedsheetdate)
                accessedsheettimelist.append(accessedsheettime)
                accessedsheetindexlist.append(accessedsheetindex)
                accessedsheetprojectlist.append(accessedsheetproject)
                accessedsheetlist.append(accessedsheet)
                accessedsheetindex +=1
                accessedsheetcount +=1
           
            #get views accessed in session    
            if 'Activate "[' in y and 'Jrn.Directive "WindowSize"' in journaldict[x-3] and "Sheet" not in y:
                accessedview = y.split(",")[1][1:]
                accessedviewproject = y.split('"')[1]
                accessedviewdate = journaldict[x-4].split(" ")[1]
                accessedviewtime = journaldict[x-4].split(" ")[2][:-5]
                accessedviewlist.append(accessedview)
                accessedviewprojectlist.append(accessedviewproject)
                accessedviewdatelist.append(accessedviewdate)
                accessedviewtimelist.append(accessedviewtime)
                accessedviewindexlist.append(accessedviewindex)
                accessedviewindex += 1
                accessedviewcount += 1

            #get local model file size info    
            if "fileSizeOnOpen" in y and "Open:Local" in journaldict[x-1]:
                localfilesize = y.split(':')[2] 
                localfile = journaldict[x-1].split('"')[1]
                localfilelist.append(localfile)
                localfilesizelist.append(localfilesize)
                localfileindexlist.append(localfileindex)
                localfileindex += 1
                localfilecount += 1

            #get journal command data
            if 'Jrn.Command' in y and "'C" in journaldict[x-1]:
                commanddatatype = y.split[","][0].split['"'][1]
                commanddata = y.split[","][1]
                commanddatadate = journaldict[x-1].split(" ")[1]
                commanddatatime = journaldict[x-1].split(" ")[2][:-5]
                commandindexlist.append(commandindex)
                commanddatalist.append(commanddata)
                commandtypelist.append(commanddatatype)
                
            #get transaction data
            if 'Jrn.Data "Transaction Successful"' in y:
                transaction = journaldict[x+1].split('"')[1]
                transdate = journaldict[x-1].split(" ")[1]
                transtime = journaldict[x-1].split(" ")[2][:-5]
                transactionlist.append(transaction)                  
                transindexlist.append(transindex)
                transdatelist.append(transdate)
                transtimelist.append(transtime)
                transindex += 1
                transcount += 1
            
            #get number of items placed during session
            if "[Modify | Place" in y:
                placedelementcount += 1
                
            #get sync data
            if "Jrn.PushButton" in y and "Synchronize with Central" in y:
                syncdate = journaldict[x-1].split(" ")[1]
                synctime = journaldict[x-1].split(" ")[2][:-5]
                syncindexlist.append(syncindex)
                synctimelist.append(synctime)
                syncdatelist.append(syncdate)
                syncindex += 1
                synccount += 1

            #get quick sync data
            if "Jrn.Command" in y and "Save the active project back to the Central Model" in y:
                qksyncdate = journaldict[x-1].split(" ")[1]
                qksynctime = journaldict[x-1].split(" ")[2][:-5]
                qksyncindexlist.append(qksyncindex)
                qksynctimelist.append(qksynctime)
                qksyncdatelist.append(qksyncdate)
                qksyncindex += 1
                qksynccount += 1

            #get save data
            if 'Jrn.Command "Ribbon"' in y and "ID_REVIT_FILE_SAVE" in y:               
                savedate = journaldict[x-1].split(" ")[1]
                savetime = journaldict[x-1].split(" ")[2][:-5]
                saveindexlist.append(saveindex)
                savetimelist.append(savetime)
                savedatelist.append(savedate)
                saveindex += 1
                savecount += 1
                    
            #get CAD link data
            if 'Jrn.Command "Ribbon" , " , ID_FILE_CADFORMAT_LINK"' in y and "IDOK" in journaldict[x+6]:
                cadlinkdate = journaldict[x+4].split(" ")[1]
                cadlinktime = journaldict[x+4].split(" ")[2][:-5]
                cadlinkname = journaldict[x+9].split('"')[1]
                cadlinkindexlist.append(cadlinkindex)
                cadlinknamelist.append(cadlinkname)
                cadlinkdatelist.append(cadlinkdate)
                cadlinktimelist.append(cadlinktime)
                cadlinkcount += 1
                cadlinkindex += 1

            #get CAD link data method 2
            if 'Jrn.Command "Ribbon" , " , ID_FILE_CADFORMAT_LINK"' in y and "IDOK" in journaldict[x+4]:
                cadlinkdate = journaldict[x+2].split(" ")[1]
                cadlinktime = journaldict[x+2].split(" ")[2][:-5]
                cadlinkname = journaldict[x+7].split('"')[1]
                cadlinkindexlist.append(cadlinkindex)
                cadlinknamelist.append(cadlinkname)
                cadlinkdatelist.append(cadlinkdate)
                cadlinktimelist.append(cadlinktime)
                cadlinkcount += 1
                cadlinkindex += 1
                     
            #get CAD import data
            if 'Jrn.Command "Ribbon" , "Import vector data from other programs , ID_FILE_IMPORT"' in y and "IDOK" in journaldict[x+6]:
                cadimportdate = journaldict[x+4].split(" ")[1]
                cadimporttime = journaldict[x+4].split(" ")[2][:-5]
                cadimportname = journaldict[x+9].split('"')[1]
                cadimportindexlist.append(cadimportindex)
                cadimportnamelist.append(cadimportname)
                cadimportdatelist.append(cadimportdate)
                cadimporttimelist.append(cadimporttime)
                cadimportcount += 1
                cadimportindex += 1

            #get CAD import data method 2
            if 'Jrn.Command "Ribbon" , "Import vector data from other programs , ID_FILE_IMPORT"' in y and "IDOK" in journaldict[x+4]:
                cadimportdate = journaldict[x+2].split(" ")[1]
                cadimporttime = journaldict[x+2].split(" ")[2][:-5]
                cadimportname = journaldict[x+7].split('"')[1]
                cadimportindexlist.append(cadimportindex)
                cadimportnamelist.append(cadimportname)
                cadimportdatelist.append(cadimportdate)
                cadimporttimelist.append(cadimporttime)
                cadimportcount += 1
                cadimportindex += 1

            #get RVT link data
            if 'Jrn.Command "Ribbon" , "Link another Revit project , ID_RVTDOC_LINK"' in y and "IDOK" in journaldict[x+6]:
                rvtlinkdate = journaldict[x+4].split(" ")[1]
                rvtlinktime = journaldict[x+4].split(" ")[2][:-5]
                rvtlinkname = journaldict[x+6].split('"')[3]
                rvtlinkindexlist.append(rvtlinkindex)
                rvtlinknamelist.append(rvtlinkname)
                rvtlinkdatelist.append(rvtlinkdate)
                rvtlinktimelist.append(rvtlinktime)
                rvtlinkcount += 1
                rvtlinkindex += 1
                
            #get RVT link data method 2    
            if 'Jrn.Command "Ribbon" , "Link another Revit project , ID_RVTDOC_LINK"' in y and "IDOK" in journaldict[x+4]: 
                rvtlinkdate = journaldict[x+2].split(" ")[1]
                rvtlinktime = journaldict[x+2].split(" ")[2][:-5]
                rvtlinkname = journaldict[x+5].split('"')[3]
                rvtlinkindexlist.append(rvtlinkindex)
                rvtlinknamelist.append(rvtlinkname)
                rvtlinkdatelist.append(rvtlinkdate)
                rvtlinktimelist.append(rvtlinktime)
                rvtlinkcount += 1
                rvtlinkindex += 1
          
            #get unrecoverable error instances
            if ', "An unrecoverable error has occurred.  The program will now be terminated.  All of your data has been recently saved, so there is no need to create recovery files."' in y:
                unrecoverableerrordate = journaldict[x-2].split(" ")[1]
                unrecoverableerrortime = journaldict[x-2].split(" ")[2][:-5]
                unrecoverableerrorindexlist.append(unrecoverableerrorindex)
                unrecoverableerrordatelist.append(unrecoverableerrordate)
                unrecoverableerrortimelist.append(unrecoverableerrortime)
                unrecoverableerrorcount += 1
                unrecoverableerrorindex += 1

            #get corrupt central model errors:
            if ', "You cannot synchronize to central until the model is repaired.",  _' in y :
                corruptionerrordate = journaldict[x-2].split(" ")[1]
                corruptionerrortime = journaldict[x-2].split(" ")[2][:-5]
                corruptionerrorindexlist.append(corruptionerrorindex)
                corruptionerrordatelist.append(corruptionerrordate)
                corruptionerrortimelist.append(corruptionerrortime)
                corruptionerrorcount += 1
                corruptionerrorindex += 1

            #get missing elements instances
            if 'is missing many elements, and it cannot be opened.",  _' in y:
                missingelementsdate = journaldict[x-2].split(" ")[1]
                missingelementstime = journaldict[x-2].split(" ")[2][:-5]
                missingelementsindexlist.append(missingelementsindex)
                missingelementsdatelist.append(missingelementsdate)
                missingelementstimelist.append(missingelementstime)
                missingelementscount += 1
                missingelementsindex += 1

            #get fatal error instances
            if "fatal error" in y and "'H" in journaldict[x-2]:
                fatalerrordate = journaldict[x-2].split(" ")[1]
                fatalerrortime = journaldict[x-2].split(" ")[2][:-5]
                fatalerrorindexlist.append(fatalerrorindex)
                fatalerrordatelist.append(fatalerrordate)
                fatalerrortimelist.append(fatalerrortime)
                fatalerrorcount += 1
                fatalerrorindex += 1

            #get serious error warning
            if 'A serious error has occurred. The current action has been cancelled' in y and "Jrn.Data" in journaldict[x-1]:
                seriouserrordate = journaldict[x-2].split(" ")[1]
                seriouserrortime = journaldict[x-2].split(" ")[2][:-5]
                seriouserrorindexlist.append(seriouserrorindex)
                seriouserrordatelist.append(seriouserrordate)
                seriouserrortimelist.append(seriouserrortime)
                seriouserrorcount += 1
                seriouserrorindex += 1

            #get minor error dialog data
            if 'Jrn.Data "Error dialog"' in y and "'H" in journaldict[x-1]:
                errordialogdate = journaldict[x-1].split(" ")[1]
                errordialogtime = journaldict[x-1].split(" ")[2][:-5]
                errordialogindexlist.append(errordialogindex)
                errordialogdatelist.append(errordialogdate)
                errordialogtimelist.append(errordialogtime)
                errordialogcount += 1
                errordialogindex += 1

            #get raster printing warnings
            if 'TaskDialog "Revit will use raster printing' in y and 'Jrn.Directive "ProjToPage"' in journaldict[x+7]:
                rasterprintdate = journaldict[x+6].split(" ")[1]
                rasterprinttime = journaldict[x+6].split(" ")[2][:-5]
                rasterprintsheet = journaldict[x+8].split('"')[3]
                rasterprintproject = journaldict[x+8].split('"')[1]
                rasterprintindexlist.append(rasterprintindex)
                rasterprintsheetlist.append(rasterprintsheet)
                rasterprintprojectlist.append(rasterprintproject)
                rasterprintdatelist.append(rasterprintdate)
                rasterprinttimelist.append(rasterprinttime)
                rasterprintcount += 1
                rasterprintindex += 1

            #get raster printing warnings method 2
            if 'TaskDialog "Revit will use raster printing' in y and 'Jrn.Directive "ProjToPage"' in journaldict[x+5]:
                rasterprintdate = journaldict[x+4].split(" ")[1]
                rasterprinttime = journaldict[x+4].split(" ")[2][:-5]
                rasterprintsheet = journaldict[x+6].split('"')[3]
                rasterprintproject = journaldict[x+6].split('"')[1]
                rasterprintindexlist.append(rasterprintindex)
                rasterprintsheetlist.append(rasterprintsheet)
                rasterprintprojectlist.append(rasterprintproject)
                rasterprintdatelist.append(rasterprintdate)
                rasterprinttimelist.append(rasterprinttime)
                rasterprintcount += 1
                rasterprintindex += 1

            #get DBG_INFOs
            if "DBG_INFO" in y:
                dbginfocount += 1

            #get DBG_WARNs
            if "DBG_WARN" in y:
                dbgwarncount += 1

            #get DBG_ERRORs
            if "DBG_ERROR" in y:
                dbgerrorcount += 1

            #get BIG_GAPs
            if "BIG_GAP" in y:
                biggap += float(y.split('!')[0][1:])
        
        #query transaction data for keywords
        for trans in transactionlist:
            if "Delete Selection" in trans:
                transdelcount += 1
            if "Explode" in trans:
                transexplodecount += 1
            if "Drag" in trans:
                transmovecount += 1
            if "Nudge" in trans:
                transmovecount += 1
            if "Toggle Pin" in trans:
                transpincount += 1
            if "Dynamo" in trans:
                dynamoruncount += 1

        #display basic info
        f1awarnings = []
        f1alistbox.deletetext()
        if disktotal != "unknown":
            f1alistbox.inserttext(f'Total disk space: {int(disktotal)/8**10:.2f} GB, Used: {int(diskused)/8**10:.2f} GB, Free: {int(diskfree)/8**10:.2f} GB')
            if int(diskfree)/8**10 < 50:
                f1awarnings.append(0)
        else:
            f1alistbox.inserttext(f'Total disk space: {disktotal} GB, Used: {diskused} GB, Free: {diskfree} GB')
        f1alistbox.inserttext(f'Available VM: {int(availablevm)/2**10:.2f} GB, Available RAM: {int(availableram)/2**10:.2f} GB')
        if int(availableram)/2**10 < 10:
            f1awarnings.append(1)
        f1alistbox.inserttext(f'Revit username is: {username}')
        f1alistbox.inserttext(f'Windows username is: {windowsuser}')
        if journalopened != False:
            f1alistbox.inserttext(f'Journal opened on: {journalopendate} at {journalopentime}')
        elif journalopened == False:
            f1alistbox.inserttext(f'Journal not opened.')
            f1awarnings.append(4)
        if journalclosed != False:
            f1alistbox.inserttext(f'Journal closed on: {journalclosedate} at {journalclosetime}')
            f1alistbox.inserttext(f'Total session time: {tdelta} ')
        elif journalclosed == False:
            f1alistbox.inserttext(f'Journal not closed.')
            f1awarnings.append(5)
            f1alistbox.inserttext(f'Total session time unknown.')
            f1awarnings.append(6)
        if userversion in revitversions["Build No:"]:
            f1alistbox.inserttext(f'Revit is up to date. Version detected: {userversion}')
        elif userversion not in revitversions["Build No:"]:
            f1alistbox.inserttext(f'REVIT IS OUT OF DATE. VERSION DETECTED: {userversion}')
            f1awarnings.append(7)
        f1alistbox.inserttext(f'CPU:  {cpu}')
        for gpu, driver in zip(gpulist, gpudriverlist):
            f1alistbox.inserttext(f'GPU:  {gpu} with driver version: {driver}')
        f1alistbox.inserttext(f'OS: {operatingsystem}')
        f1alistbox.warningtext(f1awarnings)

        #display project access info
        f2alistbox.deletetext()
        if accessedfilecount > 0:
            f2alistbox.inserttext(f'Total projects accessed: {accessedfilecount}')
            for a, b, c, d in zip(accessedfileindexlist, accessedfilelist, accessedfiledatelist, accessedfiletimelist):
                f2alistbox.inserttext(f'{str(a)}. {b} on {c} at {d}')
        else:
            f2alistbox.inserttext(f'No projects accessed in session.')

        #display file size of local models
        f2blistbox.deletetext()
        if localfilecount > 0:
            f2blistbox.inserttext(f'Local models with filesize information: {localfilecount}')
            for a, b, c in zip(localfileindexlist, localfilelist, localfilesizelist):
                f2blistbox.inserttext(f'{str(a)}. {b} with size: {c}')
        else:
            f2blistbox.inserttext(f'Local model file size not available.')

        #display new projects created
        f2clistbox.deletetext()
        if newfilecount > 0:
            f2clistbox.inserttext(f'Total number of new projects created: {newfilecount}')
            for a, b, c, d in zip(newfileindexlist, newfiledatelist, newfiletimelist, newfiletemplatelist):
                f2clistbox.inserttext(f'{str(a)}. on {b} at {c} with template {d}')
        else:
            f2clistbox.inserttext("No new projects created in session.")

        #display sheets accessed count
        f3alistbox.deletetext()
        if accessedsheetcount > 0:
            f3alistbox.inserttext(f'Total number of sheets accessed: {accessedsheetcount}')
            for a, b, c, d, e in zip(accessedsheetindexlist, accessedsheetlist, accessedsheetprojectlist, accessedsheetdatelist, accessedsheettimelist):
                f3alistbox.inserttext(f'{str(a)}. {b} in: {c} on {d} at {e}')
        else:
            f3alistbox.inserttext(f'No sheets accessed in session.')

        #display views accessed count
        f3blistbox.deletetext()
        if accessedviewcount > 0:
            f3blistbox.inserttext(f'Total number of views accessed: {accessedviewcount}')
            for a, b, c, d, e in zip(accessedviewindexlist, accessedviewlist, accessedviewprojectlist, accessedviewdatelist, accessedviewtimelist):
                f3blistbox.inserttext(f'{str(a)}. {b} in: {c} on {d} at {e}')
        else:
            f3blistbox.inserttext(f'No views accessed in session.')

        #display transactions count
        f4awarnings = []
        f4alistbox.deletetext()
        f4blistbox.deletetext()
        if transcount > 0:
            f4alistbox.inserttext(f'Total number of transactions recorded in session: {transcount}')
            for a, b, c, d in zip(transindexlist, transactionlist, transdatelist, transtimelist):
                f4blistbox.inserttext(f'{str(a)}. {b} on {c} at {d}')
        else:
            f4alistbox.inserttext(f'No transactions recorded in session.')
            f4blistbox.inserttext(f'No transactions recorded in session.')

        #display deleted transactions count
        if transdelcount > 0:
            f4alistbox.inserttext(f'Total number of deletion transactions: {transdelcount}')
        else:
            f4alistbox.inserttext(f'No deletion transactions recorded in session.')

        #display placed elements count
        if placedelementcount > 0:
            f4alistbox.inserttext(f'Total number of elements placed: {placedelementcount}')
        else:
            f4alistbox.inserttext(f'No elements placed in session.')
        
        #display pin toggle count
        if transpincount > 0:
            f4alistbox.inserttext(f'Total number of pin toggles: {transpincount}')
            f4awarnings.append(3)
        else:
            f4alistbox.inserttext(f'No pin toggles recorded in session.')

        #display manual element move actions count
        if transmovecount > 0:
            f4alistbox.inserttext(f'Total number of manual element move actions: {transmovecount}')
        else:
            f4alistbox.inserttext(f'No manual element move actions recorded in session.')

        #display dynamo run count
        if dynamoruncount > 0:
            f4alistbox.inserttext(f'Total number of dynamo runs: {dynamoruncount}')
            f4awarnings.append(5)
        else:
            f4alistbox.inserttext(f'No dynamo runs recorded in session.')

        f4alistbox.warningtext(f4awarnings)

        #display synchronization count
        f5alistbox.deletetext()
        if synccount > 0:
            f5alistbox.inserttext(f'Total number of full sync attempts: {synccount}')
            for a, b, c in zip(syncindexlist, syncdatelist, synctimelist):
                f5alistbox.inserttext(f'{str(a)}. {b} on {c}')
        else:
            f5alistbox.inserttext(f'No full sync attempts recorded in session.')

        #display quick synchronization count
        f5blistbox.deletetext()
        if qksynccount > 0:
            f5blistbox.inserttext(f'Total number of quick sync attempts: {qksynccount}')
            for a, b, c in zip(qksyncindexlist, qksyncdatelist, qksynctimelist):
                f5blistbox.inserttext(f'{str(a)}. {b} at {c}')
        else:
            f5blistbox.inserttext(f'No quick sync attempts recorded in session.')

        #display save count
        f5clistbox.deletetext()
        if savecount > 0:
            f5clistbox.inserttext(f'Total number of document saves: {savecount}')
            for a, b, c in zip(saveindexlist, savedatelist, savetimelist):
                f5clistbox.inserttext(f'{str(a)}. {b} at {c}')
        else:
            f5clistbox.inserttext(f'No document saves recorded in session.')

        #display CAD link count
        f6alistbox.deletetext()
        if cadlinkcount > 0:
            f6alistbox.inserttext(f'Total number of CAD link attempts: {cadlinkcount}')
            for a, b, c, d in zip(cadlinkindexlist, cadlinknamelist, cadlinkdatelist, cadlinktimelist):
                f6alistbox.inserttext(f'{str(a)}. {b} on {c} at {d}')
        else:
            f6alistbox.inserttext(f'No CAD link attempts recorded in session.')

        #display CAD import count
        f6blistbox.deletetext()
        if cadimportcount > 0:
            f6blistbox.inserttext(f'Total number of CAD import attempts: {cadimportcount}')
            for a, b, c, d in zip(cadimportindexlist, cadimportnamelist, cadimportdatelist, cadimporttimelist):
                f6blistbox.inserttext(f'{str(a)}. {b} on {c} at {d}')
        else:
            f6blistbox.inserttext(f'No CAD import attempts recorded in session.')

        #display RVT link count
        f6clistbox.deletetext()
        if rvtlinkcount > 0:
            f6clistbox.inserttext(f'Total number of RVT link attempts: {rvtlinkcount}')
            for a, b, c, d in zip(rvtlinkindexlist, rvtlinknamelist, rvtlinkdatelist, rvtlinktimelist):
                f6clistbox.inserttext(f'{str(a)}. {b} on {c} at {d}')
        else:
            f6clistbox.inserttext(f'No RVT link attempts recorded in session.')

        #display explode actions count
        f6dlistbox.deletetext()
        if transexplodecount > 0:
            f6dlistbox.inserttext(f'Total number of explode actions: {transexplodecount}')
            f6dlistbox.warninglist()
        else:
            f6dlistbox.inserttext(f'No explode actions recorded in session.')

        #display unrecoverable error
        f7alistbox.deletetext()
        if unrecoverableerrorcount > 0:
            f7alistbox.inserttext(f'Total number of unrecoverable errors detected: {unrecoverableerrorcount}')
            for a, b, c in zip(unrecoverableerrorindexlist, unrecoverableerrordatelist, unrecoverableerrortimelist):
                f7alistbox.inserttext(f'{str(a)}. Unrecoverable error detected on {b} at {c}')
                f7alistbox.warninglist()
        else:
            f7alistbox.inserttext(f'No unrecoverable errors detected.')

        #display corruption error
        f7blistbox.deletetext()
        if corruptionerrorcount > 0:
            f7blistbox.inserttext(f'Total number of corruption errors detected: {corruptionerrorcount}')
            for a, b, c in zip(corruptionerrorindexlist, corruptionerrordatelist, corruptionerrortimelist):
                f7blistbox.inserttext(f'{str(a)}. Corruption error detected on {b} at {c}')
                f7blistbox.warninglist()
        else:
            f7blistbox.inserttext(f'No corruption errors detected.')

        #display missing elements error
        f7clistbox.deletetext()
        if missingelementscount > 0:
            f7clistbox.inserttext(f'Total number of missing element errors detected: {missingelementscount}')
            for a, b, c in zip(missingelementsindexlist, missingelementsdatelist, missingelementstimelist):
                f7clistbox.inserttext(f'{str(a)}. Missing elements error detected on {b} at {c}')
                f7clistbox.warninglist()
        else:
            f7clistbox.inserttext(f'No missing elements errors detected.')

        #display fatal error
        f7dlistbox.deletetext()
        if fatalerrorcount > 0:
            f7dlistbox.inserttext(f'Total number of fatal errors detected: {fatalerrorcount}')
            for a, b, c in zip(fatalerrorindexlist, fatalerrordatelist, fatalerrortimelist):
                f7dlistbox.inserttext(f'{str(a)}. Fatal error detected on {b} at {c}')
                f7dlistbox.warninglist()
        else:
            f7dlistbox.inserttext(f'No fatal errors detected.')

        #display serious error
        f8alistbox.deletetext()
        if seriouserrorcount > 0:
            f8alistbox.inserttext(f'Total number of serious errors detected: {seriouserrorcount}')
            for a, b, c in zip(seriouserrorindexlist, seriouserrordatelist, seriouserrortimelist):
                f8alistbox.inserttext(f'{str(a)}. Serious error detected on {b} at {c}')
                f8alistbox.warninglist()
        else:
            f8alistbox.inserttext(f'No serious errors detected.')

        #display minor warning dialogs
        f8blistbox.deletetext()
        if errordialogcount > 0:
            f8blistbox.inserttext(f'Total number of minor error dialogs detected: {errordialogcount}')
            for a, b, c in zip(errordialogindexlist, errordialogdatelist, errordialogtimelist):
                f8blistbox.inserttext(f'{str(a)}. Minor error dialog detected on {b} at {c}')
                f8blistbox.warninglist()
        else:
            f8blistbox.inserttext(f'No minor error dialogs detected.')

        #display raster print warnings
        f8clistbox.deletetext()
        if rasterprintcount > 0:
            f8clistbox.inserttext(f'Raster print warnings detected: {rasterprintcount}')
            for a, b, c, d, e in zip(rasterprintindexlist, rasterprintsheetlist, rasterprintprojectlist, rasterprintdatelist, rasterprinttimelist):
                f8clistbox.inserttext(f'{str(a)}. {b} in {c} on {d} at {e}')
                f8clistbox.warninglist()
        else:
            f8clistbox.inserttext(f'No raster print warnings detected.')

        #display and calculate transaction to sync ratio
        f5dlabel['foreground'] = "black"
        f5elabel['foreground'] = "black"
        f5dlabel['text'] = f'{transcount} transactions / {synccount} syncs'

        if transcount == 0 and synccount == 0:
            tps = 0
            f5elabel['text'] = f'={tps} transactions per sync (TPS).'

        if transcount > 0 and synccount == 0:
            tps = transcount
            if tps < 100:
                f5elabel['text'] = f'={tps} transactions per sync (TPS). \nTPS is within acceptable range for session.'
            if tps > 100:
                f5elabel['text'] = f'={tps} transactions per sync (TPS). \nTPS exceeds 100. Remind user to sync often.'
                f5elabel['foreground'] = "red"

        if transcount > 0 and synccount > 0:
            tps = transcount/synccount
            if tps < 100:
                f5elabel['text'] = f'={tps:.2f} transactions per sync (TPS). \nTPS is within acceptable range for session.'
            if tps > 100:
                f5elabel['text'] = f'={tps:.2f} transactions per sync (TPS). \nTPS exceeds 100. Remind user to sync often.'
                f5elabel['foreground'] = "red"

        if transcount == 0 and synccount > 0:
            tps = 0
            f5elabel['text'] = f'={tps} transactions per sync (TPS).'

        #display dbg stuff
        f8dlistbox.deletetext()
        if dbginfocount > 0:
            f8dlistbox.inserttext(f'Total number of DBG_INFO detected: {dbginfocount}')
        else:
            f8dlistbox.inserttext(f'No DBG_INFO detected.')
        if dbgwarncount > 0:
            f8dlistbox.inserttext(f'Total number of DBG_WARN detected: {dbgwarncount}')
        else:
            f8dlistbox.inserttext(f'No DBG_WARN detected.')
        if dbgerrorcount > 0:
            f8dlistbox.inserttext(f'Total number of DBG_ERROR detected: {dbgerrorcount}')
        else:
            f8dlistbox.inserttext(f'No DBG_ERROR detected.')
        f8dlistbox.inserttext(f'Total BIG_GAPs time: {biggap:.2f} seconds.')

###################################### tkinter loop below ##########################################           
if __name__ == "__main__":
       
    root = Tk()

    #set menubar
    menubar = RegularMenu(root)
    
    #set statusbar
    statusbar = Label(root, text='')
    statusbar.grid(row=4, column=0, columnspan=3, sticky=NW, padx=(10,10), pady=(10,10))
          
    #GUI layout
    f1 = RegularFrame(root, text="Basic User Info", foreground="blue", font=("Helvetica", 16))
    f1.grid(row=0, column=0, columnspan=2, sticky=NW, padx=(10,10), pady=(10,10))

    f1a = RegularFrame(f1, text="Session info", foreground="black", font=("Helvetica", 10))
    f1a.pack(anchor=NW)
    f1alistbox = RegularListBox(f1a, 90, 15)
        
    f2 = RegularFrame(root, text="File Access Statistics", foreground="blue", font=("Helvetica", 16))
    f2.grid(row=0, column=2, columnspan=3, sticky=NW, padx=(10,10), pady=(10,10))

    f2a = RegularFrame(f2, text="Projects Accessed", foreground="black", font=("Helvetica", 10))
    f2a.pack(anchor=NW)
    f2alistbox = RegularListBox(f2a, 180, 4)
    
    f2b = RegularFrame(f2, text="Local Models With Filesize Information", foreground="black", font=("Helvetica", 10))
    f2b.pack(anchor=NW)
    f2blistbox = RegularListBox(f2b, 180, 4)
    
    f2c = RegularFrame(f2, text="New Projects Created in Session", foreground="black", font=("Helvetica", 10))
    f2c.pack(anchor=NW)
    f2clistbox = RegularListBox(f2c, 180, 4)
     
    f3 = RegularFrame(root, text="Sheet and View Statistics", foreground="blue", font=("Helvetica", 16))
    f3.grid(row=2, column=2, columnspan=2, sticky=NW, padx=(10,10), pady=(10,10))

    f3a = RegularFrame(f3, text="Sheets Accessed", foreground="black", font=("Helvetica", 10))
    f3a.pack(anchor=NW)
    f3alistbox = RegularListBox(f3a, 180, 6)

    f3b = RegularFrame(f3, text="Views Accessed", foreground="black", font=("Helvetica", 10))
    f3b.pack(anchor=NW)
    f3blistbox = RegularListBox(f3b, 180, 5)
    
    f4 = RegularFrame(root, text="Document Transaction Statistics", foreground="blue", font=("Helvetica", 16))
    f4.grid(row=2, column=0, columnspan=2, sticky=NW, padx=(10,10), pady=(10,10))

    f4a = RegularFrame(f4, text="Document Transactions", foreground="black", font=("Helvetica", 10))
    f4a.pack(anchor=NW)
    f4alistbox = RegularListBox(f4a, 90, 6)

    f4b = RegularFrame(f4, text="Transaction List", foreground="black", font=("Helvetica", 10))
    f4b.pack(anchor=NW)
    f4blistbox = RegularListBox(f4b, 90, 5)

    f5 = RegularFrame(root, text="Sync and Save Statistics", foreground="blue", font=("Helvetica", 16))
    f5.grid(row=3, column=0, columnspan=1, sticky=NW, padx=(10,10), pady=(10,10))

    f5a = RegularFrame(f5, text="Full Sync Attempts", foreground="black", font=("Helvetica", 10))
    f5a.pack(anchor=NW)
    f5alistbox = RegularListBox(f5a, 40, 4)
  
    f5b = RegularFrame(f5, text="Quick Sync Attempts", foreground="black", font=("Helvetica", 10))
    f5b.pack(anchor=NW)
    f5blistbox = RegularListBox(f5b, 40, 4)

    f5c = RegularFrame(f5, text="Document Saves", foreground="black", font=("Helvetica", 10))
    f5c.pack(anchor=NW)
    f5clistbox = RegularListBox(f5c, 40, 4)

    f5d = RegularFrame(f5, text="", foreground="black", font=("Helvetica", 10))
    f5d.pack(anchor=NW)
    f5dlabel = Label(f5d, text="")
    f5dlabel.pack(anchor=NW)

    f5e = RegularFrame(f5, text="", foreground="black", font=("Helvetica", 10))
    f5e.pack(anchor=NW)
    f5elabel = Label(f5d, text="")
    f5elabel.pack(anchor=NW)

    f6 = RegularFrame(root, text="Import and Link Statistics", foreground="blue", font=("Helvetica", 16))
    f6.grid(row=3, column=1, columnspan=1, sticky=NE, padx=(10,10), pady=(10,10))

    f6a = RegularFrame(f6, text="CAD Link Attempts", foreground="black", font=("Helvetica", 10))
    f6a.pack(anchor=NE)
    f6alistbox = RegularListBox(f6a, 40, height=4)

    f6b = RegularFrame(f6, text="CAD Import Attempts", foreground="black", font=("Helvetica", 10))
    f6b.pack(anchor=NE)
    f6blistbox = RegularListBox(f6b, 40, 4)

    f6c = RegularFrame(f6, text="Revit Link Attempts", foreground="black", font=("Helvetica", 10))
    f6c.pack(anchor=NE)
    f6clistbox = RegularListBox(f6c, 40, 4)

    f6d = RegularFrame(f6, text="CAD Explode Attempts", foreground="black", font=("Helvetica", 10))
    f6d.pack(anchor=NE)
    f6dlistbox = RegularListBox(f6d, 40, 4)

    f7 = RegularFrame(root, text="Errors Detected", foreground="blue", font=("Helvetica", 16))
    f7.grid(row=3, column=2, columnspan=1, sticky=NW, padx=(10,10), pady=(10,10))

    f7a = RegularFrame(f7, text="Unrecoverable Errors", foreground="black", font=("Helvetica", 10))
    f7a.pack(anchor=NW)
    f7alistbox = RegularListBox(f7a, 85, 4)

    f7b = RegularFrame(f7, text="Corruption Errors", foreground="black", font=("Helvetica", 10))
    f7b.pack(anchor=NW)
    f7blistbox = RegularListBox(f7b, 85, 4)

    f7c = RegularFrame(f7, text="Missing Elements Errors", foreground="black", font=("Helvetica", 10))
    f7c.pack(anchor=NW)
    f7clistbox = RegularListBox(f7c, 85, 4)

    f7d = RegularFrame(f7, text="Fatal Errors", foreground="black", font=("Helvetica", 10))
    f7d.pack(anchor=NE)
    f7dlistbox = RegularListBox(f7d, 85, 4)

    f8 = RegularFrame(root, text="", foreground="blue", font=("Helvetica", 16))
    f8.grid(row=3, column=3, columnspan=1, sticky=NE, padx=(10,10), pady=(10,10))

    f8a = RegularFrame(f8, text="Serious Errors", foreground="black", font=("Helvetica", 10))
    f8a.pack(anchor=NE)
    f8alistbox = RegularListBox(f8a, 85, 4)

    f8b = RegularFrame(f8, text="Minor Error Dialogs", foreground="black", font=("Helvetica", 10))
    f8b.pack(anchor=NE)
    f8blistbox = RegularListBox(f8b, 85, 4)

    f8c = RegularFrame(f8, text="Raster Print Warnings", foreground="black", font=("Helvetica", 10))
    f8c.pack(anchor=NE)
    f8clistbox = RegularListBox(f8c, 85, 4)

    f8d = RegularFrame(f8, text="Debug Information", foreground="black", font=("Helvetica", 10))
    f8d.pack(anchor=NE)
    f8dlistbox = RegularListBox(f8d, 85, 4)
    
    #run the tkinter loop
    root.mainloop()
