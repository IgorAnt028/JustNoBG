import copy
import re
import sys
from tkinter import Tk, Canvas, ttk
import tkinter.filedialog as fd
from PIL import Image, ImageDraw, ImageTk
import numpy as np

# Константы
WINDOW_WIDTH = 520
WINDOW_HEIGHT = 400
CANVAS_SIZE = 400
BUTTON_X = 410
THRESH_VALUE = 100
POINT_SIZE = 2

# Цвета и пороги
BG_COLOR = "#f0f0f0"
TRANSPARENT = (0, 0, 0, 0)
POINT_COLOR = "red"
STATUS_COLOR = "green"
WHITE_COLOR = (255, 255, 255, 255)
COLOR_SIMILARITY_THRESHOLD = 30  # Порог схожести с белым цветом

print(sys.argv)


class Window:
    """
    Главное окно приложения для удаления фона изображений.
    
    Attributes:
        window (Tk): Основное окно приложения
        points (list): Список точек для удаления фона
        history (list): История изменений изображения
        imgs (list): Список путей к изображениям
        index (int): Текущий индекс изображения
        history_index (int): Текущий индекс в истории изменений
    """
    
    def __init__(self, imgs=None):
        """
        Инициализация окна приложения.
        
        Args:
            imgs (list, optional): Список путей к изображениям. По умолчанию None.
        """
        self.window = Tk()
        self.window.title("JustNoBG")
        
        ttk.Style().configure(".", font=('Helvetica', 11), padding=8)
        
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.resizable(False, False)
        
        self.points = []
        self.history = []
        self.imgs = imgs or []
        
        self.size = [0, 0]
        self.index = 0
        self.history_index = 0
        
        self._init_ui()
        self._setup_bindings()
        
        if self.imgs:
            self._setup_image_controls()
            
        self.window.mainloop()
        
    def _init_ui(self):
        """Инициализация элементов интерфейса."""
        self.canvas = Canvas(bg=BG_COLOR, width=CANVAS_SIZE, height=CANVAS_SIZE)
        
        self._create_buttons()
        
    def _create_buttons(self):
        """Создание и размещение кнопок."""
        self.btn_remove = ttk.Button(text="Remove", command=self.remove_button)
        self.btn_remove.place(x=BUTTON_X, y=125)
        
        self.btn_open = ttk.Button(text="Open", command=self.open_files)
        self.btn_open.place(x=BUTTON_X, y=10)
        
        self.btn_next = ttk.Button(text="Next", command=self.next_image)
        self.btn_next.place(x=-100, y=-100)
        
        self.btn_ctrl_z = ttk.Button(text="Undo", command=self.ctrl_z)
        self.btn_ctrl_z.place(x=-100, y=-100)
        
        self.btn_ctrl_y = ttk.Button(text="Redo", command=self.ctrl_y)
        self.btn_ctrl_y.place(x=-100, y=-100)
        
        self.btn_save = ttk.Button(text="Save", command=self.save_img)
        self.btn_save.place(x=-100, y=-100)

        if len(self.imgs) > 0:
            self.btn_save.place(x=410, y=210)

            if len(self.imgs) > 1:
                self.btn_next.place(x=410, y=155)
            self.open_image(0)

    def _setup_bindings(self):
        """Настройка обработчиков событий."""
        self.window.bind('<Button-1>', self.create_point)
        
    def _setup_image_controls(self):
        """Настройка элементов управления изображением."""
        self.btn_save.place(x=BUTTON_X, y=210)
        if len(self.imgs) > 1:
            self.btn_next.place(x=BUTTON_X, y=155)
        self.open_image(0)

    def update_image(self):
        """Обновление отображения изображения на холсте."""
        self._resize_image()
        self._update_canvas()
        self._update_history_controls()
        self.window.update()
        
    def _resize_image(self):
        """Изменение размера изображения для отображения."""
        if self.img.size[0] > self.img.size[1]:
            new_height = round(self.img.size[1] / (self.img.size[0] / CANVAS_SIZE))
            self.img = self.img.resize((CANVAS_SIZE, new_height))
        else:
            new_width = round(self.img.size[0] / (self.img.size[1] / CANVAS_SIZE))
            self.img = self.img.resize((new_width, CANVAS_SIZE))
            
    def _update_canvas(self):
        """Обновление холста с изображением."""
        self.canvas.delete("all")
        photo = ImageTk.PhotoImage(self.img, master=self.window)
        self.canvas.create_image(0, 0, anchor='nw', image=photo)
        self.canvas.grid(row=1, column=1)
        self.canvas.image = photo
        
    def _update_history_controls(self):
        """Обновление кнопок истории."""
        if len(self.history) > 1:
            self.btn_ctrl_z.place(x=BUTTON_X, y=280)
            self.btn_ctrl_y.place(x=BUTTON_X, y=320)
        print(f"История изменений: {len(self.history)} элементов")

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

    def remove_button(self):
        """Удаление фона изображения."""
        self._show_progress_indicator()
        self._remove_background()
        self._crop_image()
        self._update_history()
        self.update_image()
        
    def _show_progress_indicator(self):
        """Отображение индикатора прогресса."""
        self.canvas.create_oval(460, 130, 470, 140, fill=STATUS_COLOR)
        
    def _remove_background(self):
        """Удаление фона на основе выбранных точек и автоматическое удаление белого фона."""
        # Сначала удаляем фон по выбранным точкам
        for pos in self.points:
            seed = (pos[0], pos[1])
            ImageDraw.floodfill(self.img, seed, TRANSPARENT, thresh=THRESH_VALUE)
        
        # Затем удаляем белый фон
        self._remove_white_background()
        
    def _remove_white_background(self):
        """Удаление белого фона из изображения."""
        # Конвертируем изображение в массив numpy для быстрой обработки
        img_array = np.array(self.img)
        
        # Создаем маску для белых пикселей
        r, g, b, a = img_array.T
        white_areas = (r > 255 - COLOR_SIMILARITY_THRESHOLD) & \
                     (g > 255 - COLOR_SIMILARITY_THRESHOLD) & \
                     (b > 255 - COLOR_SIMILARITY_THRESHOLD)
        
        # Устанавливаем прозрачность для белых областей
        img_array[white_areas.T] = TRANSPARENT
        
        # Обновляем изображение
        self.img = Image.fromarray(img_array)
        
    def _crop_image(self):
        """Обрезка изображения по границам непрозрачной области."""
        pixels = self.img.load()
        bounds = self._find_content_bounds(pixels)
        self.img = self.img.crop(bounds)
        
    def _find_content_bounds(self, pixels):
        """
        Поиск границ содержимого изображения.
        
        Args:
            pixels: Пиксели изображения
            
        Returns:
            tuple: Границы (left, top, right, bottom)
        """
        pos = [0, 0, 0, 0]
        
        # Поиск левой границы
        for x in range(self.img.size[0]):
            if any(pixels[x, y] != TRANSPARENT for y in range(self.img.size[1])):
                pos[0] = max(0, x - 1)
                break
                
        # Поиск верхней границы
        for y in range(self.img.size[1]):
            if any(pixels[x, y] != TRANSPARENT for x in range(self.img.size[0])):
                pos[1] = max(0, y - 1)
                break
                
        # Поиск правой границы
        for x in range(self.img.size[0] - 1, -1, -1):
            if any(pixels[x, y] != TRANSPARENT for y in range(self.img.size[1])):
                pos[2] = min(self.img.size[0], x + 1)
                break
                
        # Поиск нижней границы
        for y in range(self.img.size[1] - 1, -1, -1):
            if any(pixels[x, y] != TRANSPARENT for x in range(self.img.size[0])):
                pos[3] = min(self.img.size[1], y + 1)
                break
                
        return tuple(pos)
        
    def _update_history(self):
        """Обновление истории изменений."""
        self.history = self.history[:self.history_index + 1]
        self.history.append(copy.deepcopy(self.img))
        self.history_index += 1


def process_image_without_interface(image_path):
    """
    Обработка изображения без графического интерфейса.
    
    Args:
        image_path (str): Путь к изображению
    """
    img = Image.open(image_path).convert('RGBA')
    
    # Сохранение оригинала
    backup_path = "old_" + re.sub(r"^.*[/\\]", "", image_path)
    img.save(backup_path)
    
    # Удаление белого фона
    img_array = np.array(img)
    r, g, b, a = img_array.T
    white_areas = (r > 255 - COLOR_SIMILARITY_THRESHOLD) & \
                 (g > 255 - COLOR_SIMILARITY_THRESHOLD) & \
                 (b > 255 - COLOR_SIMILARITY_THRESHOLD)
    img_array[white_areas.T] = TRANSPARENT
    img = Image.fromarray(img_array)
    
    # Удаление фона из углов
    for seed in [(0, 0), (img.size[0]-1, 0), (0, img.size[1]-1), (img.size[0]-1, img.size[1]-1)]:
        ImageDraw.floodfill(img, seed, TRANSPARENT, thresh=THRESH_VALUE)
    
    # Обрезка изображения
    pixels = img.load()
    bounds = find_content_bounds(img, pixels)
    img = img.crop(bounds)
    
    # Сохранение результата
    output_path = re.sub(r"^.*[/\\]", "", image_path)
    img.save(output_path)

def find_content_bounds(img, pixels):
    """
    Поиск границ содержимого изображения.
    
    Args:
        img (Image): Изображение
        pixels: Пиксели изображения
        
    Returns:
        tuple: Границы (left, top, right, bottom)
    """
    pos = [0, 0, 0, 0]
    
    # Поиск левой границы
    for x in range(img.size[0]):
        if any(pixels[x, y] != TRANSPARENT for y in range(img.size[1])):
            pos[0] = max(0, x - 1)
            break
            
    # Поиск верхней границы
    for y in range(img.size[1]):
        if any(pixels[x, y] != TRANSPARENT for x in range(img.size[0])):
            pos[1] = max(0, y - 1)
            break
            
    # Поиск правой границы
    for x in range(img.size[0] - 1, -1, -1):
        if any(pixels[x, y] != TRANSPARENT for y in range(img.size[1])):
            pos[2] = min(img.size[0], x + 1)
            break
            
    # Поиск нижней границы
    for y in range(img.size[1] - 1, -1, -1):
        if any(pixels[x, y] != TRANSPARENT for x in range(img.size[0])):
            pos[3] = min(img.size[1], y + 1)
            break
            
    return tuple(pos)

def main():
    """Основная функция программы."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--with_interface":
            Window(sys.argv[2:])
        else:
            for image_path in sys.argv[1:]:
                process_image_without_interface(image_path)
    else:
        Window()

if __name__ == "__main__":
    main()
