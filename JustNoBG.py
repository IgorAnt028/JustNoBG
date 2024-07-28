import copy

from PIL import Image, ImageDraw, ImageTk
import re
import sys
import math

import tkinter
import tkinter.filedialog as fd

print(sys.argv)


class Window:
    def __init__(self, imgs=None):
        if imgs is None:
            imgs = []
        self.window = tkinter.Tk()

        self.window.geometry("475x400")
        self.window.minsize(475, 400)
        self.window.maxsize(475, 400)

        self.points = []
        self.history = []
        self.imgs = imgs

        self.size = [0, 0]
        self.index = 0
        self.history_index = 0

        self.canvas = tkinter.Canvas(bg="#f0f0f0", width=400, height=400)

        btn = tkinter.Button(text="Result", command=self.remove_button)
        btn.place(x=410, y=125)

        btn = tkinter.Button(text="Open", command=self.open_files)
        btn.place(x=410, y=10)

        self.btn_next = tkinter.Button(text="Next", command=self.next_image)
        self.btn_next.place(x=-100, y=-100)

        self.btn_ctrl_z = tkinter.Button(text="Undo", command=self.ctrl_z)
        self.btn_ctrl_z.place(x=-100, y=-100)

        self.btn_ctrl_y = tkinter.Button(text="Redo", command=self.ctrl_y)
        self.btn_ctrl_y.place(x=-100, y=-100)

        self.btn_save = tkinter.Button(text="Save", command=self.save_img)
        self.btn_save.place(x=-100, y=-100)

        if len(imgs) > 0:
            self.btn_save.place(x=410, y=210)

            if len(imgs) > 1:
                self.btn_next.place(x=410, y=155)
            self.open_image(0)

        self.window.bind('<Button-1>', self.create_point)

        self.window.mainloop()

    def update_image(self):
        # image resize
        if self.img.size[0] > self.img.size[1]:
            self.img = self.img.resize((400, round(self.img.size[1] / (self.img.size[0] / 400))))
        else:
            self.img = self.img.resize((round(self.img.size[0] / (self.img.size[1] / 400)), 400))

        self.canvas.delete("all")
        pht = ImageTk.PhotoImage(self.img, master=self.window)
        self.canvas.create_image(0, 0, anchor='nw', image=pht)
        self.canvas.grid(row=1, column=1)
        self.canvas.image = pht

        if len(self.history) > 1:
            self.btn_ctrl_z.place(x=410, y=280)
            self.btn_ctrl_y.place(x=410, y=320)

        print(self.history)

        self.window.update()

    def open_image(self, index):
        self.img = Image.open(self.imgs[index]).convert('RGBA')
        self.size = [self.img.size[0], self.img.size[1]]

        self.history_index = 0
        self.history = [copy.deepcopy(self.img)]

        self.btn_ctrl_z.place(x=-100, y=-100)
        self.btn_ctrl_y.place(x=-100, y=-100)

        self.update_image()

    def next_image(self, ):
        # Open the next image
        self.index += 1

        self.open_image(self.index)

        if self.index + 1 >= len(self.imgs):
            self.btn_next.place(x=-100, y=-100)

        self.window.update()

    def save_img(self, ):
        # Save image
        self.img.resize(([self.img.size[0], self.img.size[1]]))
        self.img.save(re.sub(r"^.*[/\\]", "", self.imgs[self.index]))
        print(re.sub(r"^.*[/\\]", "", self.imgs[self.index]))

    def ctrl_z(self, ):
        # Undo
        if self.history_index > 0:
            self.history_index -= 1

            self.img = self.history[self.history_index].convert('RGBA')
            self.size = [self.img.size[0], self.img.size[1]]

            self.update_image()

    def ctrl_y(self, ):
        # Redo
        if self.history_index < len(self.history) - 1:
            self.history_index += 1

            self.img = self.history[self.history_index].convert('RGBA')
            self.size = [self.img.size[0], self.img.size[1]]

            self.update_image()

    def create_point(self, event):
        print(self.imgs)
        x, y = event.x_root - self.window.winfo_x() - 8, event.y_root - self.window.winfo_y() - 31

        if x <= 400 and y <= 400:
            self.points.append([x, y])
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="red")

    def open_files(self, ):
        # files open
        self.imgs = fd.askopenfilenames()
        self.index = 0

        # Place the new image
        if len(self.imgs) > 0:

            # Enabling the save button
            self.btn_save.place(x=410, y=210)

            # Enabling the next button
            if len(self.imgs) > 1:
                self.btn_next.place(x=410, y=155)

            self.open_image(self.index)

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

        # Crop image
        self.img = self.img.crop((pos[0], pos[1], pos[2], pos[3]))

        # Save the image in history
        self.history = self.history[:self.history_index + 1]
        self.history.append(copy.deepcopy(self.img))
        self.history_index += 1
        self.update_image()


if len(sys.argv) > 1:
    if sys.argv[1] == "--with_interface":
        window = Window(sys.argv[2:])
    else:
        for url in sys.argv[1:]:
            img = Image.open(url).convert('RGBA')

            # save old image
            img.save("old_" + re.sub(r"^.*[/\\]", "", url))

            # BG removing
            rep_value = (0, 0, 0, 0)
            seed = (0, 0)
            ImageDraw.floodfill(img, seed, rep_value, thresh=100)

            seed = (img.size[0] - 1, 0)
            ImageDraw.floodfill(img, seed, rep_value, thresh=100)

            seed = (0, img.size[1] - 1)
            ImageDraw.floodfill(img, seed, rep_value, thresh=100)

            seed = (img.size[0] - 1, img.size[1] - 1)
            ImageDraw.floodfill(img, seed, rep_value, thresh=100)

            # Crop
            pixels = img.load()
            pos = [0, 0, 0, 0]

            # X
            for x in range(img.size[0]):
                if pos[0] != 0:
                    break

                for y in range(img.size[1]):
                    if pixels[x, y] != (0, 0, 0, 0):
                        pos[0] = x - 1

            # Y
            for y in range(img.size[1]):
                if pos[1] != 0:
                    break

                for x in range(img.size[0]):
                    if pixels[x, y] != (0, 0, 0, 0):
                        pos[1] = y - 1

            # -X
            for x in range(img.size[0] - 1, 1, -1):
                if pos[2] != 0:
                    break

                for y in range(img.size[1] - 1, 1, -1):
                    if pixels[x, y] != (0, 0, 0, 0):
                        pos[2] = x + 1

            # -Y
            for y in range(img.size[1] - 1, 1, -1):
                if pos[3] != 0:
                    break

                for x in range(img.size[0] - 1, 1, -1):
                    if pixels[x, y] != (0, 0, 0, 0):
                        pos[3] = y + 1

            # save image
            img.crop((pos[0], pos[1], pos[2], pos[3])).save(re.sub(r"^.*\\", "", url))
else:
    window = Window()
