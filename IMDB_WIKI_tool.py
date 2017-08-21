from Tkinter import *
from tkFileDialog import *
from PIL import Image, ImageTk
from datetime import date
import scipy.io as sio
import tkMessageBox
import cv2
import numpy as np
import os
import glob
import re
import ast

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def files(path):
    filelist=[]
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            filelist.append(file)
    return filelist


class LabelTool():
    def __init__(self,master):
#frame#
        self.parent = master
        w, h = self.parent.winfo_screenwidth(), self.parent.winfo_screenheight()
        self.parent.geometry("%dx%d+0+0" % (w, h))
        self.parent.title("LabelTool")
   #frame action#
        self.parent.bind("<Button-4>", self.zoom)
        self.parent.bind("<Button-5>", self.zoom)
   #frame action#
        self.leftctrPanel=Frame(self.parent)
        self.leftctrPanel.pack(side=LEFT)
        self.mainFrame=Frame(self.parent,width=1500,height=1000)
        self.mainFrame.pack(side=LEFT)
        self.inputPanel=Frame(self.parent)
        self.inputPanel.pack(side=LEFT)
        self.dobFrame=Frame(self.inputPanel)
        self.dobFrame.grid(row=0,column=0,columnspan=2)
#Toolbar#
        self.mainmenu=Menu(self.parent)
        self.parent.config(menu=self.mainmenu)

        self.fileMenu=Menu(self.mainmenu)
        self.saveMenu=Menu(self.mainmenu)
        self.mainmenu.add_cascade(label="file",menu=self.fileMenu)
        self.mainmenu.add_cascade(label="edit",menu=self.saveMenu)
        self.fileMenu.add_command(label="Open",command=self._ask_file)
        self.fileMenu.add_command(label="Open Dir",command=self._ask_directory)
#Button# 
        self.prevBtn=Button(self.leftctrPanel,text="<<Prev",bg="red",fg="white",command=self.prevImage)
        self.nextBtn=Button(self.leftctrPanel,text="Next>>",bg="green",fg="black",command=self.nextImage)
        self.prevBtn.pack(padx = 5, pady = 3)
        self.nextBtn.pack(padx = 5, pady = 3)
#Textbox & Label#
        #self.dobLabel=Label(self.inputPanel,text="dob:")
        self.dobLabel=Label(self.dobFrame,text="dob:")
        self.photo_takenLabel=Label(self.inputPanel,text="photo_taken:")

        self.genderLabel=Label(self.inputPanel,text="gender:")
        self.nameLabel=Label(self.inputPanel,text="name:")
        self.face_scoreLabel=Label(self.inputPanel,text="face_score:")
        self.second_face_scoreLabel=Label(self.inputPanel,text="second_face_score:")
        self.dobYTextbox=Entry(self.dobFrame,width=7)
        self.dobMTextbox=Entry(self.dobFrame,width=7)
        self.dobDTextbox=Entry(self.dobFrame,width=7)
        self.photo_takenTextbox=Entry(self.inputPanel)

        self.genderTextbox=Entry(self.inputPanel)
        self.nameTextbox=Entry(self.inputPanel)
        self.face_scoreTextbox=Entry(self.inputPanel)
        self.second_face_scoreTextbox=Entry(self.inputPanel)
        self.dobLabel.pack(side=LEFT)
        self.photo_takenLabel.grid(row=1,sticky=E)

        self.genderLabel.grid(row=2,sticky=E)
        self.nameLabel.grid(row=3,sticky=E)
        self.face_scoreLabel.grid(row=4,sticky=E)
        self.second_face_scoreLabel.grid(row=5,sticky=E)

        self.dobYTextbox.pack(side=LEFT)
        self.dobMTextbox.pack(side=LEFT)
        self.dobDTextbox.pack(side=LEFT)
        #self.dobDTextbox.pack(row=0,column=3)
        self.photo_takenTextbox.grid(row=1,column=1)

        self.genderTextbox.grid(row=2,column=1)
        self.nameTextbox.grid(row=3,column=1)
        self.face_scoreTextbox.grid(row=4,column=1)
        self.second_face_scoreTextbox.grid(row=5,column=1)
#Panel(Canvas)#
        self.mainPanel = Canvas(self.mainFrame)
        self.mainPanel.pack()

#Logic#
        self.current=1
        self.total=1
        self.open_dir=None
        self.open_file=None
        self.imageList=[]
        self.open_file
        self.annotationList=[] 
        self.dobList=[]
        self.photo_takenList=[]
        self.genderList=[]
        #self.nameList=[]
        self.face_scoreList=[]
        self.second_face_scoreList=[]
        #self.full_pathList=[]
        #self.full_pathSet=set()
#zoom logic#
        self.scale=1.0
        self.orig_img=None
        self.tkimg = None
        self.tkimg_id = None
#Opencv(face recognition)#
        self.face_cascade = cv2.CascadeClassifier('/home/milliontech/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
#save before exit#
        self.parent.protocol("WM_DELETE_WINDOW", self.save_before_close)

    def nextImage(self):
        if self.current==self.total:
            self.save_annotation()
        if self.current < self.total:
            self.save_annotation()
            self.current += 1
            face_scores_list=self.loadImage()
            self.loaddefault(face_scores_list)

    def prevImage(self):
        if self.current > 1:
            self.current -= 1
            face_scores_list=self.loadImage()
            self.loaddefault(face_scores_list)

    def _ask_directory(self):
        contentList=[]
        self.current=1
        self.open_dir = askdirectory()
#### direct access to the image folder and then save .mat file at the parent folder
        #self.imageList=sorted(glob.glob(os.path.join(self.open_dir, '*.jpg')),key=numericalSort)
        #if len(files(os.path.dirname(self.open_dir)))>0:
            #tkMessageBox.showinfo('Untidy way of storing dataset', "It is advised to store the image folder with a folder such that the annotation .mat file is contained in that folder instead of hidden among a lot of files of your computer")
#### 

        for root, dirs, files_loop in os.walk(self.open_dir):
            for dir in dirs:
                self.imageList+=sorted(glob.glob(os.path.join(root ,dir, '*.jpg')),key=numericalSort)
                contentList+=glob.glob(os.path.join(root ,dir, '*'))
        if len(self.imageList)!=len(contentList):tkMessageBox.showinfo("Possible unsupported image(or files) type",'It is detected that folders contain file which is not in jpg format. Notice that file which is not in jpg format(including image file) will not be read by this program')
        if len(files(self.open_dir))>1:
            tkMessageBox.showinfo('Untidy way of storing dataset', "It is advised to store the image folder with a folder such that the annotation .mat file is contained in that folder instead of hidden among a lot of files of your computer")
        if len(glob.glob(os.path.join(self.open_dir, '*.mat')))>1:
            tkMessageBox.showinfo('Too many matfile', "There are more 1 .mat file. Annotation record CAN'T be loaded")
        if len(self.imageList) == 0:
            print 'No .jpg images found in the specified dir!'
        if len(glob.glob(os.path.join(self.open_dir, '*.mat')))==1:
            self.load_mat_file()
        self.total=len(self.imageList)
        face_scores_list=self.loadImage()
        self.loaddefault(face_scores_list)

    def _ask_file(self):
        self.open_file=askopenfilename()

    def loadImage(self):
        imagepath = self.imageList[self.current-1]
        #self.orig_img=Image.open(os.path.join(self.open_dir,imagepath))
        self.orig_img,face_scores_list=self.face_score_function(imagepath)
        self.parent.tkimg=self.tkimg=ImageTk.PhotoImage(self.orig_img)

        self.mainPanel.config(width = 900, height = 700)
        self.img_id=self.mainPanel.create_image((0, 0), image = self.tkimg,anchor=NW)
        print (imagepath)
        return face_scores_list


    def zoom(self,event):
        if event.num == 4:
            self.scale *= 1.1
        elif event.num == 5:
            self.scale *= 0.9
        self.redraw(event.x, event.y)

    def redraw(self, x=0, y=0):
        if self.img_id:
            self.mainPanel.delete(self.img_id)
        iw, ih = self.orig_img.size
        size = int(iw * self.scale), int(ih * self.scale)
        self.tkimg = ImageTk.PhotoImage(self.orig_img.resize(size))
        self.img_id = self.mainPanel.create_image(x, y, image=self.tkimg)

    def save_annotation(self):
        annotation=dict()
        error=0
        dobY=self.dobYTextbox.get()
        dobM=self.dobMTextbox.get()
        dobD=self.dobDTextbox.get()
        photo_taken=self.photo_takenTextbox.get()
        gender=self.genderTextbox.get()
        name=self.nameTextbox.get()
        face_score=self.face_scoreTextbox.get()
        second_face_score=self.second_face_scoreTextbox.get()
        dob=date.toordinal(date(int(dobY),int(dobM),int(dobD)))+366

        annotation['dob']=dob
        annotation['photo_taken']=photo_taken
        annotation['full_path']=os.path.relpath(self.imageList[self.current-1],self.open_dir)
        annotation['gender']=gender
        annotation['name']=name
        annotation['face_score']=face_score
        annotation['second_face_score']=second_face_score
        for exist_annotation in self.annotationList:
            #if (exist_annotation['full_path']==self.imageList[self.current-1]):
            if (exist_annotation['full_path']==os.path.relpath(self.imageList[self.current-1],self.open_dir)):
                error=error+1
                exist_annotation['dob']=dob
                exist_annotation['photo_taken']=photo_taken
                exist_annotation['full_path']=os.path.relpath(self.imageList[self.current-1],self.open_dir)
                exist_annotation['gender']=gender
                exist_annotation['name']=name
                exist_annotation['face_score']=face_score
                exist_annotation['second_face_score']=second_face_score
        if error==0:
            self.annotationList.append(annotation)
        if error>1:print("multiple full_path, possible corrupted file")
        print(self.annotationList)

    def loaddefault(self,face_scores_list):
        if len(face_scores_list)==0:
            self.face_scoreTextbox.delete(0,END)
            self.second_face_scoreTextbox.delete(0,END)
            self.face_scoreTextbox.insert(0,np.nan)
            self.second_face_scoreTextbox.insert(0,np.nan)
        if len(face_scores_list)==1:
            self.face_scoreTextbox.delete(0,END)
            self.second_face_scoreTextbox.delete(0,END)
            self.face_scoreTextbox.insert(0,face_scores_list[0][0])
            self.second_face_scoreTextbox.insert(0,np.nan)
        if len(face_scores_list)==2:
            self.face_scoreTextbox.delete(0,END)
            self.second_face_scoreTextbox.delete(0,END)
            self.face_scoreTextbox.insert(0,sorted(face_scores_list,reverse=True)[0][0])
            self.second_face_scoreTextbox.insert(0,sorted(face_scores_list,reverse=True)[1][0])
        if len(face_scores_list)>2:
            self.face_scoreTextbox.delete(0,END)
            self.second_face_scoreTextbox.delete(0,END)
            self.face_scoreTextbox.insert(0,sorted(face_scores_list,reverse=True)[0][0])
            self.second_face_scoreTextbox.insert(0,sorted(face_scores_list,reverse=True)[1][0])
            print("There are more than 2 faces!!")
        for annotation in self.annotationList:
            if (annotation['full_path']==os.path.relpath(self.imageList[self.current-1],self.open_dir)):
                self.dobYTextbox.delete(0,END)
                self.dobMTextbox.delete(0,END)
                self.dobDTextbox.delete(0,END)
                self.photo_takenTextbox.delete(0,END)
                self.genderTextbox.delete(0,END)
                self.nameTextbox.delete(0,END)
                self.face_scoreTextbox.delete(0,END)
                self.second_face_scoreTextbox.delete(0,END)
                self.dobYTextbox.insert(0,date.fromordinal(max(int(annotation['dob']) - 366, 1)).year)
                self.dobMTextbox.insert(0,date.fromordinal(max(int(annotation['dob']) - 366, 1)).month)
                self.dobDTextbox.insert(0,date.fromordinal(max(int(annotation['dob']) - 366, 1)).day)
                self.photo_takenTextbox.insert(0,annotation['photo_taken'])
                self.genderTextbox.insert(0,annotation['gender'])
                self.nameTextbox.insert(0,annotation['name'])
                self.face_scoreTextbox.insert(0,annotation['face_score'])
                self.second_face_scoreTextbox.insert(0,annotation['second_face_score'])

    def face_score_function(self,imagepath):
        img_cv = cv2.imread(os.path.join(self.open_dir,imagepath))
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces= self.face_cascade.detectMultiScale3(gray,scaleFactor=1.3,minNeighbors=3,minSize=(30, 30),outputRejectLevels=True)
        faces_c=0
        rects = faces[0]
        neighbours = np.array(faces[1]).tolist()
        weights = np.array(faces[2]).tolist()
        for (x,y,w,h) in rects:
            cv2.rectangle(img_cv,(x,y),(x+w,y+h),(255,0,0),2)
            cv2.putText(img_cv,str(weights[faces_c][0]),(x,y),0,0.6, (255,0,0),6//3)
            faces_c+=1
        img_pil= cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img=Image.fromarray(img_pil)
	return img,weights

    def save_mat_file(self):
        save_counter=0
        full_pathList=np.zeros((len(self.annotationList),),dtype=np.object)
        nameList=np.zeros((len(self.annotationList),),dtype=np.object)
        for annotation_output in self.annotationList:
            self.dobList.append(annotation_output['dob'])
            self.photo_takenList.append(annotation_output['photo_taken'])
            self.genderList.append(annotation_output['gender'])
            nameList[save_counter]=annotation_output['name']
            self.face_scoreList.append(annotation_output['face_score'])
            self.second_face_scoreList.append(annotation_output['second_face_score'])
            full_pathList[save_counter]=annotation_output['full_path']
            save_counter+=1
        photo={'dob':np.float64(self.dobList),'photo_taken':np.float64(self.photo_takenList),'full_path':full_pathList,'gender':np.float64(self.genderList),'name':nameList,'face_score':np.float64(self.face_scoreList),'second_face_score':np.float64(self.second_face_scoreList)}
        path_to_mat_file=self.open_dir+"/"+"photo.mat"
        sio.savemat(path_to_mat_file, {'photo': photo})####################change the name of struct in there##############################

    def save_before_close(self):
        if (self.current>1):
            self.save_annotation()
        self.parent.destroy()

    def load_mat_file(self):
        loadedmat=sio.loadmat(glob.glob(os.path.join(self.open_dir, '*.mat'))[0])
        full_path = loadedmat['photo'][0, 0]["full_path"][0].tolist()
        dob = loadedmat['photo'][0, 0]["dob"][0].tolist()  # Matlab serial date number
        gender = loadedmat['photo'][0, 0]["gender"][0].tolist()
        name = loadedmat['photo'][0, 0]["name"][0].tolist()
        photo_taken = loadedmat['photo'][0, 0]["photo_taken"][0].tolist()  # year
        face_score = loadedmat['photo'][0, 0]["face_score"][0].tolist()
        second_face_score = loadedmat['photo'][0, 0]["second_face_score"][0].tolist()
        name=[str(x) for x in name]
        name = [eval(x) for x in name]
        name = [x[0] if len(x)>0 else "" for x in name]
        name = [x.encode('ascii','ignore') for x in name]
        full_path=[str(x) for x in full_path]
        full_path = [eval(x) for x in full_path]
        full_path = [x[0] for x in full_path]
        full_path = [x.encode('ascii','ignore') for x in full_path]
        for input_loop_c in range(len(dob)):
            InputAnnotation=dict()
            InputAnnotation['dob']=int(dob[input_loop_c])
            InputAnnotation['photo_taken']=int(photo_taken[input_loop_c])
            InputAnnotation['full_path']=full_path[input_loop_c]
            InputAnnotation['gender']=int(gender[input_loop_c])
            InputAnnotation['name']=name[input_loop_c]
            InputAnnotation['face_score']=face_score[input_loop_c]
            InputAnnotation['second_face_score']=second_face_score[input_loop_c]
            self.annotationList.append(InputAnnotation)

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
    tool.save_mat_file()
