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

        aboutMenu = Menu(menu)
        menu.add_cascade(label="About", command=self.about)

        helpMenu = Menu(menu)
        menu.add_cascade(label="Help", command=self.help)

        self.text = StringVar()
        self.text.set("Welcome to the Application")
        label1= Label(root, textvariable = self.text, bg = "lightgray", font=("Helvetica", 14, "bold"), justify=LEFT, wraplength = 500).place(x=10, y=50)

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
##        print(img[len(img)-1])
        kmeans_btn = Button(root, text = "K-Means", width=40, command = lambda:self.classification(root.filename,'kmeans')).pack(anchor=N)
        iso_btn = Button(root, text = "Iso-Cluster", width=40, command = lambda:self.classification(root.filename,'iso')).pack(anchor=S)

    wd = os.chdir(os.path.dirname(os.path.abspath(__file__)))
##    print(wd)
##    print("Working directory")

    def classification(self, file, alg):
        if(alg == 'kmeans'):            
            print("Your selection is K-means Classification")
        else:
            print("Your selection is Iso-Cluster Classification")
        report = os.getcwd() + "\\Data\\Result\\Report.txt"
        if os.path.isfile(report):
            print("Deleting old Report")
            os.remove(report)
        with datasource.open_dataset(file) as dataset:
            cc = dataset.chan_count
            print("Available Channels: ")
            print(cc)

        if(alg == 'kmeans'):            
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
            pcimod(file=file, pciop='add', pcival=[1, 0, 0, 0, 0, 0])
            Report.clear()
            enableDefaultReport(report)
            print("Applying K-Means Classification")
            kcluster=kclus( file, dbic, dboc, mask, numclus, seedfile, maxiter, movethrs)
            print("K-Means Classification is successful")
        else:
            file	=	file            # input file
            dbic	=	list(range(1,cc+1,1))   # input channels
            dboc	=	[cc+1]	# output channel
            print(dboc)
            mask	=	[]	# process entire image
            numclus	=	[5]	# requested number of clusters
            maxclus	=	[7]	# at most 20 clusters
            minclus	=	[5]	# at least 5 clusters
            seedfile	=	''	#  automatically generate seeds
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
            pcimod(file=file, pciop='add', pcival=[1, 0, 0, 0, 0, 0])
            Report.clear()
            enableDefaultReport(report)
            print("Applying Iso-cluster Classification")
            isoclus( file, dbic, dboc, mask, numclus, maxclus, minclus, seedfile, maxiter,\
                     movethrs, siggen, samprm, stdv, lump, maxpair, backval, nsam )
            print("Iso-Cluster Classification is successful")

        pcimod(file = file, pciop = 'add', pcival = [1])
##        root.status.set("Running fmo")
        print("Applying MOD filter")
        kfmo=fmo(file = file, dbic = [cc+1], dboc = [cc + 2])
        print("MOD filter is successfully applied")
        pcimod(file = file, pciop = 'add', pcival = [1])
##        root.status.set("Running sieve")
        print("Applying SIEVE filter")
        ksieve=sieve(file = file, dbic = [cc+1], dboc = [cc + 3] , sthresh = [32])
        print("SIEVE filter is successfully applied")
##      Split and insert directory name  
        split_file=file.split("/")
        split_file.insert(-1,"Result")
        join_result = "\\".join(split_file)
##        Split by .
        dot_result = join_result.split(".")
##        print(dot_result)
##        print("dot result")
##        join .shp at last
        shp_result = dot_result[0]+".shp"

        current_file_path, ext = os.path.splitext(str(file))
        current_file = current_file_path.split("/")[-1]
##        print(current_file)
##        print("current file")
##      Delete previously generated shapefiles
        prev_files = glob.glob(os.getcwd()+"\\Data\\Result\\"+"*")
##        print(prev_files)
##        print("previous files")
        for prev_file in prev_files:
            prev_file_name, format = os.path.splitext(str(os.path.basename(prev_file)))
##            print(prev_file_name)
##            print(" prev file names")
            if(current_file in prev_file_name):
                print("DELETING: "+str(prev_file))
                os.remove(prev_file)
                print("Successfully DELETED: "+str(prev_file))
  
##        if(os.path.exists("../Data/Result/"+dot_result[0])):
##            print("inside if ......")
##            os.remove(shp_result)
##            print("shp is deleted...")
        print("Exporting to shapefile")
        ras2poly(fili=file, dbic=[cc + 3], filo = shp_result, smoothv="Yes", ftype="SHP", foptions="")
        print("Shapefile is successfully created")

    def about(self):
##        print("about")
        self.text.set("Unsupervised Classification: \n\nThis applicaiton is created by Mr. Janak Parajuli \nas a part of a final project of Image Processing")
        # label1= Label(root, text = "Unsupervised Classification ", bg = "antiquewhite3", font=("Helvetica", 18, "bold")).place(x=90, y=50)
        # label2 = Label(root, text = "This applicaiton is created by Mr. Janak Parajuli \nas a part of a final project of Image Processing", font=("Helvetica", 14), bg = "lightgray").place(x=40, y=90)

    def help(self):
        print("help")
        self.text.set("Guidelines for Classification \n\n \
        Step 1: Click Image menu \n\
        Step2: Select pix file \n\
        Step3: Select either k-means or iso algorithm \n \
        Step4: You will get classification report, classified image and shapefiles in Result folder")
        # label1= Label(root, text = "Guidelines for Classification ", bg = "antiquewhite3", font=("Helvetica", 18, "bold")).place(x=40, y=20)
        # label2 = Label(root, text = "Step 1: Click Image menu ", font=("Helvetica", 14), bg = "lightgray").place(x=40, y=60)
        # label3 = Label(root, text = "Step2: Select pix file", font=("Helvetica", 14), bg = "lightgray").place(x=40, y=100)
        # label4 = Label(root, text = "Step3: Select either k-means or iso algorithm", font=("Helvetica", 14), bg = "lightgray").place(x=40, y=140)
        # label5 = Label(root, text = "Step4: You will get classification report, classified \nimage and shapefiles in Result folder", font=("Helvetica", 14), bg = "lightgray").place(x=40, y=180)


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
