from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os as os
import glob

def convertPng(image):
    image.load()
    background = Image.new("RGB", image.size, (0, 0, 0))
    background.paste(image, mask=image.split()[3])
    return background

def cropImage(image):
    obj = np.asarray(image).nonzero()
    xmin, ymin, xmax, ymax = np.min(obj[1]), np.min(obj[0]), np.max(obj[1]), np.max(obj[0])
    crop = image.crop((xmin, ymin, xmax, ymax))
    return crop

class MainApplication:    
    def __init__(self, root):
        self.scale=1.0
        self.root=root
        root.bind('<Left>', lambda event, arg=-1:self.move(event, arg))
        root.bind('<Right>', lambda event, arg=1:self.move(event, arg))
        root.bind('<Up>', lambda event, arg=-2:self.move(event, arg))
        root.bind('<Down>', lambda event, arg=2:self.move(event, arg))
        root.geometry("600x500")
        root.title("Tile Object Placer (TOP)")
        self.topFrame = tk.Frame(root, width=600, height=400)
        self.topFrame.pack(side="top", fill="x")

        self.btnFrame = tk.Frame(root)
        self.btnFrame.columnconfigure(0, weight=1)
        self.btnFrame.columnconfigure(1, weight=1)
        self.btnFrame.columnconfigure(2, weight=1)
        self.btnFrame.columnconfigure(3, weight=1)

        self.canvas = tk.Canvas(self.topFrame, width= 357, height= 357)
        self.canvas.bind('<B1-Motion>', self.dragMove)
        #self.canvas.bind("<MouseWheel>",self.zoom)
        #self.canvas.config(scrollregion=self.canvas.bbox(all))
        
        #frame = Image.open("Frame.png")
        self.grid = Image.open("Grid.png")
        #self.grid.paste(frame, (153, 241), frame)
        self.background=ImageTk.PhotoImage(self.grid)
        self.photoImage=self.background
        self.canvas.create_image(5,5,anchor="nw",image=self.background)
        self.canvas.pack()

        self.loadBtn = tk.Button(self.btnFrame, text="Load", command=self.getDirectory)
        self.saveBtn = tk.Button(self.btnFrame, text="Save", command=self.saveImage)
        self.nextBtn = tk.Button(self.btnFrame, text="Next image", command=self.nextImage)
        self.prevBtn = tk.Button(self.btnFrame, text="Previous image", command=self.prevImage)

        self.loadBtn.grid(row=0, column=1, sticky="news")
        self.saveBtn.grid(row=0, column=2, sticky="news")
        self.nextBtn.grid(row=0, column=3, sticky="news")
        self.prevBtn.grid(row=0, column=0, sticky="news")

        self.btnFrame.pack(side="bottom", fill='x')

        self.imageW=357
        self.imageH=357

        self.midx=0
        self.midy=0
        
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

        self.canvas.delete(self.photoImage)
        self.photoImage=ImageTk.PhotoImage(self.image)
        self.canvas.create_image(self.midx,self.midy,image=self.photoImage)

    def dragMove(self, event):
        self.canvas.delete(self.photoImage)
        self.photoImage=ImageTk.PhotoImage(self.image)
        self.canvas.create_image(event.x,event.y,image=self.photoImage)
        
        self.midx=event.x
        self.midy=event.y
        
        imgx = self.image.width/2
        left = event.x-imgx
        right = 357-event.x-imgx

        self.offsetx=min(left, right)
        self.offsety = int(357-event.y-self.image.height/2)
        self.alignLeft = left == self.offsetx
        
        self.imageW=int(357-2*self.offsetx)
        self.imageH = self.image.height+self.offsety

    def getDirectory(self):
        self.loadDirectory(filedialog.askdirectory())

    def loadDirectory(self, directory):
        self.index = 0
        self.images = glob.glob(directory+"/*.png")
        self.drawImage(self.images[self.index])

    def nextImage(self):
       maxImg = len(self.images)-1
       self.index+=1
       if self.index>maxImg:
           self.index=maxImg
       self.drawImage(self.images[self.index])

    def prevImage(self):
       self.index-=1
       if self.index<0:
           self.index=0
       self.drawImage(self.images[self.index])

    def drawImage(self, path):
        self.path = path
        self.image = cropImage(Image.open(path))
        self.canvas.delete(self.photoImage)        
        self.photoImage=ImageTk.PhotoImage(self.image)
        self.canvas.create_image(5,5,anchor="nw",image=self.photoImage)
        self.midx=int(self.image.width/2+5)
        self.midy=int(self.image.height/2+5)

    def saveImage(self):    
       # print(self.offsetx,self.offsety, self.alignLeft)
        offx = 0
        if not self.alignLeft:
            offx = int((self.imageW+357)/2-self.offsetx-self.image.width)-1
        bg=Image.new("RGB", (self.imageW, self.imageH), (0, 0, 0))
        #print(offx)
        bg.paste(self.image, (offx, 0), self.image)
        bg.save(self.path.replace("png","bmp"))

##    def zoom(self,event):
##        if event.num == 4:
##            self.scale *= 2
##        elif event.num == 5:
##            self.scale *= 0.5
##        if self.scale<1.0:
##            self.scale=1.0
##        self.redraw(event.x, event.y)
##
##    def redraw(self, x=0, y=0):
##        self.canvas.delete(self.background)
##        self.canvas.delete(self.photoImage)
##
##        iw, ih = self.grid.size
##        size = int(iw * self.scale), int(ih * self.scale)
##        self.grid=self.grid.resize(size)
##        self.background = ImageTk.PhotoImage(self.grid.resize(size))
##        self.canvas.create_image(x, y, image=self.background)
##
##        iw, ih = self.image.size
##        size = int(iw * self.scale), int(ih * self.scale)
##        self.photoImage = ImageTk.PhotoImage(self.image.resize(size))
##        self.canvas.create_image(x, y, image=self.photoImage)
##
##        # tell the canvas to scale up/down the vector objects as well
##        self.canvas.scale(all, x, y, self.scale, self.scale)


    
if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("icon.ico")
    MainApplication(root)
    root.mainloop()
    

##def do_zoom(event):
##    x = canvas.canvasx(event.x)
##    y = canvas.canvasy(event.y)
##    factor = 1.001 ** event.delta
##    canvas.scale(tk.ALL, x, y, factor, factor)
##    canvas.pack()

##root = tk.Tk()
##
##
##
##png = Image.open("Shelves 002.png")
##
##convert = convertPng(png)
##crop = cropImage(png)
##
##background = Image.new("RGB", (45,111), (0, 0, 0))
##
##xoffset = 0
##yoffset = 0
##
##background.paste(png, (xoffset, yoffset))
##grid.paste(crop, (153+xoffset, 241+yoffset), crop)
##
##grid.save("gridtest.png")


