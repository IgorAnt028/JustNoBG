from PIL import Image, ImageDraw, ImageTk
import re
import sys
import math

import tkinter
import tkinter.filedialog as fd


class Window:
    def __init__(self):
        self.window = tkinter.Tk()

        self.window.geometry("475x400")
        self.window.minsize(475, 400)
        self.window.maxsize(475, 400)

        self.points = []
        self.imgs = []
        self.size = [0, 0]
        self.index = 0

        self.canvas = tkinter.Canvas(bg="#f0f0f0", width=400, height=400)

        btn = tkinter.Button(text="Result", command=self.remove_button)
        btn.place(x=410, y=125)

        btn = tkinter.Button(text="Open", command=self.open_files)
        btn.place(x=410, y=10)

        self.btn_next = tkinter.Button(text="Next", command=self.next_image)
        self.btn_next.place(x=410, y=155)

        self.window.bind('<Button-1>', self.create_point)

        self.window.mainloop()

    def new_image(self, url=None):
        if url is not None:
            pass

        if self.img.size[0] > self.img.size[1]:
            self.img = self.img.resize((400, round(self.img.size[1] / (self.img.size[0] / 400))))
        else:
            self.img = self.img.resize((round(self.img.size[0] / (self.img.size[1] / 400)), 400))

        self.canvas.delete("all")
        pht = ImageTk.PhotoImage(self.img, master=self.window)
        self.canvas.create_image(0, 0, anchor='nw', image=pht)
        self.canvas.grid(row=1, column=1)
        self.canvas.image = pht

        self.window.update()

    def next_image(self, ):
        self.index += 1
        self.img = Image.open(self.imgs[self.index]).convert('RGBA')
        self.size = [self.img.size[0], self.img.size[1]]

        self.new_image()

        if self.index + 1 >= len(self.imgs):
            self.btn_next.destroy()

        self.window.update()

    def create_point(self, event):
        x, y = event.x_root - self.window.winfo_x() - 8, event.y_root - self.window.winfo_y() - 31

        if x <= 400 and y <= 400:
            self.points.append([x, y])
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="red")

    def open_files(self, ):
        self.imgs = fd.askopenfilenames()

        if len(self.imgs) > 0:
            if len(self.imgs) > 1:
                self.btn_next = tkinter.Button(text="Next", command=self.next_image)
                self.btn_next.place(x=410, y=155)

            self.img = Image.open(self.imgs[0]).convert('RGBA')

            if self.img.size[0] > self.img.size[1]:
                self.img = self.img.resize((400, math.ceil(self.img.size[1] / (self.img.size[0] / 400))))
            else:
                self.img = self.img.resize((math.ceil(self.img.size[0] / (self.img.size[1] / 400)), 400))

            self.new_image()

    def remove_button(self, ):
        # Green circle
        self.canvas.create_oval(460, 130, 470, 140, fill="green")

        # BG removing
        rep_value = (0, 0, 0, 0)
        for pos in self.points:
            seed = (pos[0], pos[1])
            ImageDraw.floodfill(self.img, seed, rep_value, thresh=100)

        # Crop
        pixels = self.img.load()
        pos = [0, 0, 0, 0]

        # Green circle
        self.canvas.create_oval(460, 160, 470, 170, fill="green")

        # X
        for x in range(self.img.size[0]):
            if pos[0] != 0:
                break

            for y in range(self.img.size[1]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[0] = x - 1

        # Y
        for y in range(self.img.size[1]):
            if pos[1] != 0:
                break

            for x in range(self.img.size[0]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[1] = y - 1

        # -X
        for x in range(self.img.size[0] - 1, 1, -1):
            if pos[2] != 0:
                break

            for y in range(self.img.size[1] - 1, 1, -1):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[2] = x + 1

        # -Y
        for y in range(self.img.size[1] - 1, 1, -1):
            if pos[3] != 0:
                break

            for x in range(self.img.size[0] - 1, 1, -1):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[3] = y + 1

        self.img = self.img.crop((pos[0], pos[1], pos[2], pos[3]))
        self.img.resize(([self.img.size[0], self.img.size[1]]))
        self.img.save("new_" + re.sub(r"^.*/", "", self.imgs[self.index]))
        self.new_image()


window = Window()
