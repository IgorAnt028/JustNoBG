from PIL import Image, ImageDraw, ImageTk
import re
import sys

import tkinter
import tkinter.filedialog as fd

def main():
    window = tkinter.Tk()

    window.geometry("475x300")
    window.minsize(475, 300)
    window.maxsize(475, 300)

    window.iconbitmap(default=r"C:\Users\Razi\Documents\Coding\JustNoBG\icon.ico")

    # img = Image.open(r"C:\Users\Razi\Documents\Coding\JustNoBG\JustNoBG\test.png").convert('RGBA')
    imgs = []

    points = []

    def new_image(url=None):
        if url is not None:
            pass

        canvas.delete("all")
        pht = ImageTk.PhotoImage(img, master=window)
        canvas.create_image(0, 0, anchor='nw', image=pht)
        canvas.grid(row=1, column=1)
        canvas.image = pht

        window.update()

    def next_image():
        canvas.delete("all")

        pht = ImageTk.PhotoImage(img, master=window)
        canvas.create_image(0, 0, anchor='nw', image=pht)
        canvas.grid(row=1, column=1)
        canvas.image = pht

        window.update()

    def create_point(event):
        x, y = event.x_root - window.winfo_x() - 8, event.y_root - window.winfo_y() - 31

        if x <= 400 and y <= 400:
            points.append([x, y])
            canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="red")

    def open_files():
        imgs = fd.askopenfilenames()

        img = Image.open(imgs[0]).convert('RGBA')

        if img.size[0] > img.size[1]:
            img = img.resize((400, int(img.size[1] / (img.size[0] / 400))))
        else:
            img = img.resize((int(img.size[0] / (img.size[1] / 400)), 400))

    def remove_button():
        # Green circle
        canvas.create_oval(460, 130, 470, 140, fill="green")

        # BG removing
        rep_value = (0, 0, 0, 0)
        for pos in points:
            seed = (pos[0], pos[1])
            ImageDraw.floodfill(img, seed, rep_value, thresh=100)

        # Crop
        pixels = img.load()
        pos = [0, 0, 0, 0]

        # Green circle
        canvas.create_oval(460, 160, 470, 170, fill="green")

        # X
        for x in range(img.size[0]):
            if pos[0] != 0:
                break

            for y in range(img.size[1]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[0] = x

        # Y
        for y in range(img.size[1]):
            if pos[1] != 0:
                break

            for x in range(img.size[0]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[1] = y

        # -X
        for x in range(img.size[0] - 1, 1, -1):
            if pos[2] != 0:
                break

            for y in range(img.size[1] - 1, 1, -1):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[2] = x

        # -Y
        for y in range(img.size[1] - 1, 1, -1):
            if pos[3] != 0:
                break

            for x in range(img.size[0] - 1, 1, -1):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[3] = y

        img.crop((pos[0], pos[1], pos[2], pos[3])).save(re.sub(r"^.*\\", "", "ok.png"))
        new_image()

    btn = tkinter.Button(text="Result", command=remove_button)
    btn.place(x=410, y=125)

    btn = tkinter.Button(text="Next", command=next_image)
    btn.place(x=410, y=155)

    btn = tkinter.Button(text="Open", command=open_files)
    btn.place(x=410, y=10)

    window.bind('<Button-1>', create_point)

    window.mainloop()


if len(sys.argv) > 0:
    main()
