import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os

class Character:
    def __init__(self,title, name, hp, atk, defense, speed, image_path=None):
        self.title = title
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.speed = speed
        self.image_path = image_path

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)

class BattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("角色戰鬥模擬器")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)

        self.characters = []
        self.setup_characters()

        self.attacker_var = tk.StringVar()
        self.defender_var = tk.StringVar()
        self.attacker_var.trace("w", self.update_attacker_display)
        self.defender_var.trace("w", self.update_defender_display)

        self.set_background("background.jpg")
        self.setup_styles()
        self.create_widgets()
    
        self.root.bind("<Configure>", self.resize_background)

    def set_background(self, path):
        if os.path.exists(path):
            self.bg_image_raw = Image.open(path)  # 原始大圖
            w, h = self.root.winfo_width(), self.root.winfo_height()
            bg_resized = self.bg_image_raw.resize((w, h))
            self.bg_image = ImageTk.PhotoImage(bg_resized)
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def resize_background(self, event):
        if hasattr(self, "bg_image_raw"):
            w, h = event.width, event.height
            bg_resized = self.bg_image_raw.resize((w, h))
            self.bg_image = ImageTk.PhotoImage(bg_resized)
            self.bg_label.configure(image=self.bg_image)

    def setup_characters(self):
        stats = {
            "海盜": ("pirate",100, 30, 10, 15),
            "法師": ("mage",80, 40, 5, 25),
            "弓箭手": ("bow", 90, 25, 8, 30),
            "精靈": ("Elf", 85, 35, 6, 35),
            "騎士": ("knight", 110, 20, 15, 10),
            "獵人": ("hunter", 95, 15, 12, 20)
        }

        for title ,(name,hp, atk, defense, speed) in stats.items():
            path = f"{name}.jpeg"
            self.characters.append(Character(title,name, hp, atk, defense, speed, image_path=path))

        self.turn_order = sorted(self.characters, key=lambda c: -c.speed)
        self.current_turn_index = 0

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 20), padding=12)
        style.configure("TLabel", background="#ffffff", font=("Helvetica", 20))
        style.configure("red.Horizontal.TProgressbar", foreground="red", background="red", thickness=14)
    
    def create_widgets(self):
        # 整個畫面分成上中下三個區塊
        self.top_frame = tk.Frame(self.root, bg="#ffffff")
        self.top_frame.pack(pady=20)

        self.middle_frame = tk.Frame(self.root, bg="#ffffff")
        self.middle_frame.pack(pady=20)

        self.bottom_frame = tk.Frame(self.root, bg="#ffffff")
        self.bottom_frame.pack(pady=10)

        # --- 上方：攻擊方、按鈕、防守方 ---
        self.attacker_img = tk.Label(self.top_frame, bg="#ffffff")
        self.attacker_img.grid(row=0, column=0, padx=40)

        self.attack_button = ttk.Button(self.top_frame, text="⚔️ 攻擊", command=self.attack)
        self.attack_button.grid(row=0, column=1, padx=40)

        self.defender_img = tk.Label(self.top_frame, bg="#ffffff")
        self.defender_img.grid(row=0, column=2, padx=40)

        # --- 上方：血條和數值 ---
        self.attacker_bar = ttk.Progressbar(self.top_frame, style="red.Horizontal.TProgressbar", length=200)
        self.attacker_bar.grid(row=1, column=0, pady=5)

        self.defender_bar = ttk.Progressbar(self.top_frame, style="red.Horizontal.TProgressbar", length=200)
        self.defender_bar.grid(row=1, column=2, pady=5)

        self.attacker_stats = tk.Label(self.top_frame, bg="#ffffff", font=("Helvetica", 14))
        self.attacker_stats.grid(row=2, column=0, pady=5)

        self.defender_stats = tk.Label(self.top_frame, bg="#ffffff", font=("Helvetica", 14))
        self.defender_stats.grid(row=2, column=2, pady=5)

        # --- 中間：攻擊方角色列 ---
        tk.Label(self.middle_frame, text="選擇攻擊方", bg="#e0f7fa", font=("Helvetica", 16)).pack(pady=5)
        self.attacker_selection_frame = tk.Frame(self.middle_frame, bg="#e0f7fa")
        self.attacker_selection_frame.pack(pady=10)

        # --- 中間：防守方角色列 ---
        tk.Label(self.middle_frame, text="選擇防守方", bg="#ffebee", font=("Helvetica", 16)).pack(pady=20)
        self.defender_selection_frame = tk.Frame(self.middle_frame, bg="#ffebee")
        self.defender_selection_frame.pack(pady=10)

        # --- 下方：狀態版和戰鬥紀錄 ---
        self.status_label = tk.Label(self.bottom_frame, bg="#ffffff", font=("Courier", 14), justify="left")
        self.status_label.pack(pady=10)

        self.log = tk.Text(self.bottom_frame, height=10, width=100, font=("Courier", 12), bg="#f5f5f5")
        self.log.pack()

        self.update_status_board()
        self.attacker_var.set(self.turn_order[self.current_turn_index].name)

        self.create_attack_selection()
        self.create_defend_selection()

    def create_attack_selection(self):
        for widget in self.attacker_selection_frame.winfo_children():
            widget.destroy()

        max_cols = 6
        for idx, char in enumerate(self.characters):
            img = Image.open(char.image_path).resize((100, 100))
            if not char.is_alive():
                img = img.convert("LA")
            img = self.make_rounded(img, 20)
            photo = ImageTk.PhotoImage(img)

            btn = tk.Button(self.attacker_selection_frame, image=photo, command=lambda c=char: self.set_attacker(c))
            btn.image = photo
            btn.grid(row=idx // max_cols, column=idx % max_cols, padx=5, pady=5)

    def create_defend_selection(self):
        for widget in self.defender_selection_frame.winfo_children():
            widget.destroy()

        max_cols = 6
        for idx, char in enumerate(self.characters):
            img = Image.open(char.image_path).resize((100, 100))
            if not char.is_alive():
                img = img.convert("LA")
            img = self.make_rounded(img, 20)
            photo = ImageTk.PhotoImage(img)

            btn = tk.Button(self.defender_selection_frame, image=photo, command=lambda c=char: self.set_defender(c))
            btn.image = photo
            btn.grid(row=idx // max_cols, column=idx % max_cols, padx=5, pady=5)

    def set_attacker(self, char):
        if char.is_alive():
            self.attacker_var.set(char.name)
            self.update_attacker_display()

    def set_defender(self, char):
        if char.is_alive():
            self.defender_var.set(char.name)
            self.update_defender_display()

    def update_attacker_display(self, *args):
        self.update_character_display(self.attacker_var.get(), self.attacker_img, self.attacker_bar, self.attacker_stats)

    def update_defender_display(self, *args):
        self.update_character_display(self.defender_var.get(), self.defender_img, self.defender_bar, self.defender_stats)

    def update_character_display(self, name, image_label, health_bar, stats_label):
        char = next((c for c in self.characters if c.name == name), None)
        if char and os.path.exists(char.image_path):
            img = Image.open(char.image_path).resize((200, 200))
            if not char.is_alive():
                img = img.convert("LA")
            rounded = self.make_rounded(img, 40)
            photo = ImageTk.PhotoImage(rounded)
            image_label.configure(image=photo)
            image_label.image = photo
        if char:
            percent = int((char.hp / char.max_hp) * 100)
            self.animate_health_bar(health_bar, percent)
            stats_label.config(
                text=f"HP: {char.hp}/{char.max_hp}\nATK: {char.atk}\nDEF: {char.defense}\nSPD: {char.speed}"
            )

    def animate_health_bar(self, bar, target_value):
        current_value = bar["value"]
        step = 1 if target_value > current_value else -1

        def update():
            nonlocal current_value
            if current_value != target_value:
                current_value += step
                bar["value"] = current_value
                self.root.after(10, update)
            else:
                bar["value"] = target_value

        update()

    def make_rounded(self, img, radius):
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
        img.putalpha(mask)
        return img

    def update_status_board(self):
        status_text = "【所有角色狀態】\n"
        for c in self.characters:
            status_text += f"{c.name:4} ➤ HP: {c.hp:3}/{c.max_hp:3} | ATK: {c.atk:2} | DEF: {c.defense:2} | SPD: {c.speed:2}\n"
        self.status_label.config(text=status_text)

    def attack(self):
        attacker = self.turn_order[self.current_turn_index]
        attacker_name = attacker.name
        selected_attacker = self.attacker_var.get()
        selected_defender = self.defender_var.get()

        if selected_attacker != attacker_name:
            messagebox.showwarning("錯誤", f"輪到 {attacker_name} 攻擊，請選擇他為攻擊者。")
            return

        defender = next((c for c in self.characters if c.name == selected_defender), None)

        if not defender or attacker == defender:
            messagebox.showerror("錯誤", "請選擇不同角色作為目標")
            return

        if not attacker.is_alive():
            self.log.insert(tk.END, f"{attacker.name} 無法攻擊，已經倒下。\n")
            return
        if not defender.is_alive():
            self.log.insert(tk.END, f"{defender.name} 已經倒下，無法被攻擊。\n")
            return

        damage = max(0, attacker.atk - defender.defense)
        defender.take_damage(damage)

        self.log.insert(tk.END, f"{attacker.name} 攻擊 {defender.name}，造成 {damage} 傷害。\n")
        self.log.see(tk.END)

        self.update_attacker_display()
        self.update_defender_display()
        self.update_status_board()

        self.create_attack_selection()
        self.create_defend_selection()

        if all(not c.is_alive() or c == attacker for c in self.characters):
            self.log.insert(tk.END, f"\n🏆 {attacker.name} 是最後的勝利者！\n")
            return

        self.next_turn()

    def next_turn(self):
        while True:
            self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
            next_char = self.turn_order[self.current_turn_index]
            if next_char.is_alive():
                self.attacker_var.set(next_char.name)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = BattleApp(root)
    root.mainloop()
