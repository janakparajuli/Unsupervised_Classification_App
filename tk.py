import os, glob
from tkinter import *
##from tkinter import tk
from tkinter import filedialog
from pci.kclus import kclus
from pci.isoclus import *
from pci.api import datasource
from pci.pcimod import pcimod
from pci.fmo import *
from pci.sieve import *
from pci.ras2poly import *
from pci.nspio import Report, enableDefaultReport



class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
         # widget can take all window
        self.pack(fill=BOTH, expand=1)

        menu = Menu(self.master)
        self.master.config(menu=menu)

        fileMenu = Menu(menu)
##        fileMenu.add_command(label="Item")
##        fileMenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="Image", command = self.chooseImage)

##        classifyMenu = Menu(menu)
##        classifyMenu.add_command(label="K-Means", command = self.k_means_classification)
##        classifyMenu.add_command(label="Iso-Cluster", command = self.iso_classification)
##        menu.add_cascade(label="Classify", menu=classifyMenu)

        aboutMenu = Menu(menu)
        menu.add_cascade(label="About", command=self.about)

        helpMenu = Menu(menu)
        menu.add_cascade(label="Help", command=self.help)

        exitMenu = Menu(menu)
        menu.add_cascade(label="Exit", command = self.exitProgram)

    def exitProgram(self):
        exit()

    def chooseImage(self):
##        print("File is clicked")
        root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select .pix file only",filetypes = (("pix files","*.pix"),("all files","*.*")))
##        print(root.filename)
        img = root.filename.split("/")
        Label(root, text = "You selected: "+img[len(img)-1], width=40).pack()
##        root.status = "Hello "#+StringVar()
        print(img[len(img)-1])
        kmeans_btn = Button(root, text = "K-Means", width=40, command = lambda:self.k_means_classification(root.filename)).pack(anchor=N)
        iso_btn = Button(root, text = "Iso-Cluster", width=40, command = lambda:self.iso_classification(root.filename)).pack(anchor=S)

    wd = os.chdir(os.path.dirname(os.path.abspath(__file__)))
##    print(wd)
    print("Working directory")

    def iso_classification(self, file):
        print("Iso Cluster Classification")
        report = os.getcwd() + "\\Data\\Result\\Report.txt"
        if os.path.isfile(report):
            print("Deleting old Report")
            os.remove(report)
        with datasource.open_dataset(file) as dataset:
            cc_iso = dataset.chan_count
            print(cc_iso)
            print(" channels available")
        file	=	file            # input file
        dbic	=	list(range(1,cc_iso+1,1))   # input channels
        dboc	=	[cc_iso+1]	# output channel
        print(dboc)
        mask	=	[]	# process entire image
        numclus	=	[5]	# requested number of clusters
##        maxiter	=	[20]	# no more than 20 iterations
##        movethrs	=	[0.01]

##        file	=	"irvine.pix"	# input file
##        dbic	=	[1,2,3,4,5]	# input channels
##        dboc	=	[9]	# output channel
##        mask	=	[]	# process entire channel
##        numclus	=	[5]	# request 5 clusters
        maxclus	=	[5]	# at most 20 clusters
        minclus	=	[5]	# at least 5 clusters
        seedfile	=	''	#  automatically generate seeds
##        seedfile	= "" 	# automatically generate seeds
        maxiter	=	[5]	# no more than 20 iterations
        movethrs	=	[0.01]
        siggen	=	"NO"	# no signature generation
        samprm	=	[5]
        stdv	=	[10.0]
        lump	=	[1.0]
        maxpair	=	[5]	# no more than 5 cluster center pairs
        # clumped in one iteration
        backval	=	[]	# no background value
        nsam	=	[]	# default number of samples

        

        print("The file is: "+root.filename)
##        enableDefaultReport(prev_report)
        pcimod(file=file, pciop='add', pcival=[0, 0, 1, 0, 0, 0])
        Report.clear()
        enableDefaultReport(report)
        isoclus( file, dbic, dboc, mask, numclus, maxclus, minclus, seedfile, maxiter,\
                 movethrs, siggen, samprm, stdv, lump, maxpair, backval, nsam )
        print("kclus is done")
        pcimod(file = file, pciop = 'add', pcival = [1])
##        root.status.set("Running fmo")
        kfmo=fmo(file = file, dbic = [cc_iso+1], dboc = [cc_iso + 2])
        print("fmo is done")
        pcimod(file = file, pciop = 'add', pcival = [1])
##        root.status.set("Running sieve")
        ksieve=sieve(file = file, dbic = [cc_iso+2], dboc = [cc_iso + 3] , sthresh = [32])
        print("sieve is done")
##      Split and insert directory name  
        split_file=file.split("/")
        split_file.insert(-1,"Result")
        join_result = "\\".join(split_file)
##        Split by .
        dot_result = join_result.split(".")
        print(dot_result)
        print("dot result")
##        join .shp at last
        shp_result = dot_result[0]+".shp"

        current_file_path, ext = os.path.splitext(str(file))
        current_file = current_file_path.split("/")[-1]
        print(current_file)
        print("current file")
##      Delete previously generated shapefiles
        prev_files = glob.glob(os.getcwd()+"\\Data\\Result\\"+"*")
        print(prev_files)
        print("previous files")
        for prev_file in prev_files:
            prev_file_name, format = os.path.splitext(str(os.path.basename(prev_file)))
            print(prev_file_name)
            print(" prev file names")
            if(current_file in prev_file_name):
                os.remove(prev_file)
                print("Deleting previous file: "+str(prev_file))
  
        if(os.path.exists("../Data/Result/"+dot_result[0])):
            os.remove(shp_result)
            print("shp is deleted...")
        print("after insert")
        print(shp_result)
        ras2poly(fili=file, dbic=[cc_iso + 3], filo = shp_result, smoothv="Yes", ftype="SHP", foptions="")
        print("ras2poly also done")
        
    def k_means_classification(self, file):
##        Delete previously generated report
        report = os.getcwd() + "\\Data\\Result\\Report.txt"
        if os.path.isfile(report):
            print("Deleting old Report")
            os.remove(report)
      
        print("K means classification")
        with datasource.open_dataset(file) as dataset:
            cc = dataset.chan_count
            print(cc)
            print(" channels available")
        file	=	file
        dbic	=	list(range(1,cc+1,1))	# input channels
        dboc	=	[cc+1]	# output channel
        print(dboc)
        mask	=	[]	# process entire image
        numclus	=	[5]	# requested number of clusters
        seedfile	=	''	#  automatically generate seeds
        maxiter	=	[20]	# no more than 20 iterations
        movethrs	=	[0.01]

        print("The file is: "+root.filename)
##        enableDefaultReport(prev_report)
        pcimod(file=file, pciop='add', pcival=[0, 0, 1, 0, 0, 0])
        Report.clear()
        enableDefaultReport(report)
        kcluster=kclus( file, dbic, dboc, mask, numclus, seedfile, maxiter, movethrs)
        print("kclus is done")
        pcimod(file = file, pciop = 'add', pcival = [1])
##        root.status.set("Running fmo")
        kfmo=fmo(file = file, dbic = [cc+1], dboc = [cc + 2])
        print("fmo is done")
        pcimod(file = file, pciop = 'add', pcival = [1])
##        root.status.set("Running sieve")
        ksieve=sieve(file = file, dbic = [cc+2], dboc = [cc + 3] , sthresh = [32])
        print("sieve is done")
##      Split and insert directory name  
        split_file=file.split("/")
        split_file.insert(-1,"Result")
        join_result = "\\".join(split_file)
##        Split by .
        dot_result = join_result.split(".")
        print(dot_result)
        print("dot result")
##        join .shp at last
        shp_result = dot_result[0]+".shp"

        current_file_path, ext = os.path.splitext(str(file))
        current_file = current_file_path.split("/")[-1]
        print(current_file)
        print("current file")
##      Delete previously generated shapefiles
        prev_files = glob.glob(os.getcwd()+"\\Data\\Result\\"+"*")
        print(prev_files)
        print("previous files")
        for prev_file in prev_files:
            prev_file_name, format = os.path.splitext(str(os.path.basename(prev_file)))
            print(prev_file_name)
            print(" prev file names")
            if(current_file in prev_file_name):
                os.remove(prev_file)
                print("Deleting previous file: "+str(prev_file))
  
        if(os.path.exists("../Data/Result/"+dot_result[0])):
            os.remove(shp_result)
            print("shp is deleted...")
        print("after insert")
        print(shp_result)
        ras2poly(fili=file, dbic=[cc + 3], filo = shp_result, smoothv="Yes", ftype="SHP", foptions="")
        print("ras2poly also done")

    def about(self):
        print("about")
        pix = Canvas(root, width=20, height=15)
        pix.pack()
        photo = PhotoImage(file='../Data/unsup.gif')
##        pix.pack(anchor = W)
##        pix.create_image(10,10,image = photo)
        print(photo)
##        pix.insert(END, '\n')
        pix.create_image(20,20, anchor = W, image=photo)


        text2 = Text(root, height=15, width=38)
        scroll = Scrollbar(root, command=text2.yview)
        text2.configure(yscrollcommand=scroll.set)
        text2.tag_configure('bold_italics', font=('Arial', 10, 'bold', 'italic'))
        text2.tag_configure('big', font=('Verdana', 12, 'bold'))
        text2.tag_configure('color',
                            foreground='#476042',
                            font=('Tempus Sans ITC', 10, 'bold'))
        text2.tag_bind('follow', '<1>', lambda e, t=text2: t.insert(tk.END, "Not now, maybe later!"))
        Label(root, text = "Unsupervised Classification ", width=40).pack()
        text2.insert(END,'\nUnsupervised Classification\n', 'big')
        quote = """
        This applicaiton is created by Mr. Janak Parajuli as a part of a final project of Image Processing
        """
        text2.insert(END, quote, 'color')
##        text2.insert(END, 'follow-up\n', 'follow')
        text2.pack(side=LEFT)
        scroll.pack(side=RIGHT, fill=Y)

    def help(self):
        print("help")

    def add_folder(self):
        add_dir = tkFileDialog.askdirectory(title='Select folder to save results')
        os.makedirs(add_dir)
# initialize tkinter        
root = Tk()
##root.title("Unsupervised Classification")
app = Window(root)

# set window title
root.wm_title("Unsupervised Classification")
root.geometry("475x250")

# show window
root.mainloop()
