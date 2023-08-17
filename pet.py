import tkinter as tk
import time
import random
import json

class pet():
    def __init__(self):
        self.window = tk.Tk()

        self.moveleft = [tk.PhotoImage(file='duck-left.gif', format='gif -index %i' % (i)) for i in range(10)]
        self.moveright = [tk.PhotoImage(file='duck-right.gif', format='gif -index %i' % (i)) for i in range(10)]
        self.frame_index = 0
        self.img = self.moveleft[self.frame_index]
        self.timestamp = time.time()
        self.window.config(background='black')
        self.window.wm_attributes('-transparentcolor', 'black')
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.label = tk.Label(self.window, bd=0, bg='black')
        
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        self.x = self.screen_width // 2 - 64
        self.y = self.screen_height - 128

        self.window.geometry('128x128+{}+{}'.format(str(self.x), str(self.y)))
        self.label.configure(image=self.img)
        self.label.pack()

        self.dir = random.choice([-1, 1])

        with open('config.json', 'r') as f:
            config = json.load(f)

        self.min_direction_change_delay = config["min_direction_change_delay"]
        self.max_direction_change_delay = config["max_direction_change_delay"]
        self.min_pause_duration = config["min_pause_duration"]
        self.max_pause_duration = config["max_pause_duration"]
        self.jump_height = config["jump_height"]
        self.jump_speed = config["jump_speed"]
        self.jump_probability = config["jump_probability"]
        self.is_jumping = False
        self.jump_target_y = 0

        self.delay_before_direction_change = random.uniform(self.min_direction_change_delay, self.max_direction_change_delay)
        self.pause_duration = random.uniform(self.min_pause_duration, self.max_pause_duration)

        self.label.bind("<Button-1>", self.on_mouse_press)
        self.label.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.label.bind("<B1-Motion>", self.on_mouse_drag)

        self.is_grabbed = False

        self.window.after(0, self.update)
        self.window.mainloop()

    def changetime(self, direction):
        if time.time() > self.timestamp + 0.05:
            self.timestamp = time.time()
            self.frame_index = (self.frame_index + 1) % 5
            self.img = direction[self.frame_index]

    def changedir(self):
        self.dir = -(self.dir)
        self.delay_before_direction_change = random.uniform(self.min_direction_change_delay, self.max_direction_change_delay)
        self.pause_duration = random.uniform(self.min_pause_duration, self.max_pause_duration)

    def go(self):
        self.x = self.x + self.dir
        if self.dir < 0:
            direction = self.moveleft
        else:
            direction = self.moveright
        self.changetime(direction)

    def update(self):
        if self.is_grabbed:
            self.move_to(self.window.winfo_pointerx() - self.grab_offset_x, self.window.winfo_pointery() - self.grab_offset_y)
            self.label.place(x=self.x, y=self.y)
            if self.is_jumping:
                self.fall()
        else:
            if self.pause_duration > 0:
                self.pause_duration -= 0.01
                self.window.geometry('128x128+{}+{}'.format(str(self.x), str(self.y)))
                self.label.configure(image=self.img)
                self.label.pack()
                self.window.after(10, self.update)
                return
            else:
                self.delay_before_direction_change -= 0.01
                if self.delay_before_direction_change <= 0:
                    self.changedir()

                if random.random() < self.jump_probability:
                    self.jump()

                self.go()
                if self.x <= 0 or self.x >= (self.screen_width - 128):
                    self.changedir()

        self.window.geometry('128x128+{}+{}'.format(str(self.x), str(self.y)))
        self.label.configure(image=self.img)
        self.label.pack()
        self.window.after(10, self.update)
        self.window.lift()

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_start_y = self.y
            self.jump_target_y = self.y - self.jump_height
            self.jump_frames = int(self.jump_height / self.jump_speed)
            self.jump_frame_count = 0
            self.continue_jump()

    def continue_jump(self):
        if self.jump_frame_count < self.jump_frames:
            self.jump_frame_count += 1
            self.y = self.jump_start_y - int(self.jump_frame_count * self.jump_speed)
            self.label.pack()
            self.window.after(10, self.continue_jump)
        else:
            self.fall()  # Commence la chute après le saut complet


    def fall(self):
        if self.is_jumping and self.y < self.jump_start_y:
            self.y = min(self.y + int(self.jump_speed), self.jump_start_y)
            self.label.pack()
            self.window.after(10, self.fall)
        else:
            self.is_jumping = False

    def on_mouse_press(self, event):
        label_x = self.x
        label_y = self.y
        self.window.config(cursor="plus")
    
        if (
            label_x <= event.x_root <= label_x + 128 and
            label_y <= event.y_root <= label_y + 128
        ):
            self.is_grabbed = True
            self.grab_offset_x = event.x_root - label_x
            self.grab_offset_y = event.y_root - label_y

    def on_mouse_release(self, event):
        if self.is_grabbed:
            self.is_grabbed = False
            if self.y > self.jump_target_y:
                self.jump()
            else:
                self.is_jumping = True  # Pour forcer la chute immédiate si le pet est en dessous de la hauteur de saut
                self.window.config(cursor="arrow")
                self.fall()

    def on_mouse_drag(self, event):
        if self.is_grabbed:
            self.move_to(event.x_root - self.grab_offset_x, event.y_root - self.grab_offset_y)

    def move_to(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.label.place(x=self.x, y=self.y)

pet()