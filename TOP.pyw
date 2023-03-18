from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os as os
import glob

def cropImage(image):
    obj = np.asarray(image).nonzero()
    xmin, ymin, xmax, ymax = np.min(obj[1]), np.min(obj[0]), np.max(obj[1]), np.max(obj[0])
    crop = image.crop((xmin, ymin, xmax+1, ymax))
    return crop

class MainApplication:
    canvasx=357
    canvasy=357
    def __init__(self, root, debug):
        #initialize class attributes
        self.root=root
        self.scale=1.0
        self.topFrame = tk.Frame(root, width=600, height=400)
        self.btnFrame = tk.Frame(root)
        self.canvas = tk.Canvas(self.topFrame, width=self.canvasx, height=self.canvasy)
        self.imageW=self.canvasx
        self.imageH=self.canvasy
        self.midx=self.canvasx/2
        self.midy=self.canvasy/2
        self.alignLeft=True
        self.index = 0
        self.debug=debug

        #register events
        root.bind('<Left>', lambda event, arg=-1:self.move(event, arg))
        root.bind('<Right>', lambda event, arg=1:self.move(event, arg))
        root.bind('<Up>', lambda event, arg=-2:self.move(event, arg))
        root.bind('<Down>', lambda event, arg=2:self.move(event, arg))
        self.canvas.bind('<B1-Motion>', self.dragMove)
        
        #application properties
        root.geometry("600x500")
        root.title("Tile Object Placer (TOP)")
        
        #application columns for buttons
        self.btnFrame.columnconfigure(0, weight=1)
        self.btnFrame.columnconfigure(1, weight=1)
        self.btnFrame.columnconfigure(2, weight=1)
        self.btnFrame.columnconfigure(3, weight=1)
        
        #creating base grid cavas
        self.grid = Image.open("Grid.png")
        self.background=ImageTk.PhotoImage(self.grid)
        self.photoImage=self.background
        self.canvas.create_image(5,5,anchor="nw",image=self.background)
        
        #initializing buttons and callbacks
        self.loadBtn = tk.Button(self.btnFrame, text="Load", command=self.getDirectory)
        self.saveBtn = tk.Button(self.btnFrame, text="Save", command=self.saveImage)
        self.nextBtn = tk.Button(self.btnFrame, text="Next image", command=self.nextImage)
        self.prevBtn = tk.Button(self.btnFrame, text="Previous image", command=self.prevImage)

        #draw application
        self.topFrame.pack(side="top", fill="x")
        self.canvas.pack()
        self.loadBtn.grid(row=0, column=1, sticky="news")
        self.saveBtn.grid(row=0, column=2, sticky="news")
        self.nextBtn.grid(row=0, column=3, sticky="news")
        self.prevBtn.grid(row=0, column=0, sticky="news")
        self.btnFrame.pack(side="bottom", fill='x')       

        #initialize application by asking for directory
        self. getDirectory()

    def move(self, event, *arg):
        if arg[0]==1:#right
            self.midx+=1
        elif arg[0]==-1:#left
            self.midx-=1
        elif arg[0]==-2:#up
            self.midy-=1
        elif arg[0]==2:#down
            self.midy+=1

        self.updatePosition()

    def dragMove(self, event):
        #update current image center point coordinates
        self.midx=event.x
        self.midy=event.y
        self.updatePosition()

    def updatePosition(self):
        #calculate offsets from left and right
        imgx=self.image.width/2
        left=self.midx-imgx
        right=self.canvasx-self.midx-imgx
        
        #determine if alignement is left or right (closest side)
        self.offsetx=min(left, right)
        self.offsety=int(self.canvasy-self.midy-self.image.height/2)
        self.alignLeft=(left==self.offsetx)

        #update desired image width and height based on new position
        self.imageW=int(self.canvasx-2*self.offsetx)
        self.imageH=self.image.height+self.offsety

        if self.debug:
            print("Image size: ", self.imageW, self.imageH)
            print("Image mid point: ", self.midx, self.midy)
            print("Image aligns left: ", self.alignLeft)
            
        self.drawImage()

    def getDirectory(self):
        self.loadDirectory(filedialog.askdirectory())

    def loadDirectory(self, directory):
        self.index = 0
        self.images = glob.glob(directory+"/*.png")
        self.redrawImage()

    def nextImage(self):
        maxImg = len(self.images)-1
        self.index+=1
        if self.index>maxImg:
            self.index=maxImg
        self.redrawImage()

    def prevImage(self):
        self.index-=1
        if self.index<0:
            self.index=0
        self.redrawImage()

    def drawImage(self):
        self.canvas.delete(self.photoImage)
        self.photoImage=ImageTk.PhotoImage(self.image)
        self.canvas.create_image(self.midx,self.midy,image=self.photoImage)

    def redrawImage(self):
        self.image=Image.open(self.images[self.index])
        self.image.load()
        self.image=cropImage(self.image)
        self.drawImage()

    def saveImage(self):    
        imgW=max(self.imageW,44)
        imgH=max(self.imageH,88)
        
        offx=max(0, int(imgW-self.image.width-self.canvasx-self.midx-imgW/2))
        offy=max(0, int(imgH-self.image.height-(self.canvasy-self.midy-self.image.height/2)))
        
        if not self.alignLeft:
            offx = int((imgW+self.canvasx)/2-self.offsetx-self.image.width)
            
        if self.debug:
            print("Image offset: ", offx, offy)
        bg=Image.new("RGB", (imgW, imgH), (0, 0, 0))
        bg.paste(self.image, (offx, offy), self.image)
        bg.save(self.images[self.index].replace("png","bmp"))
 
if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("icon.ico")
    MainApplication(root, False)
    root.mainloop()


