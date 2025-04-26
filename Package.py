import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os

class Character:
    def __init__(self, name, hp, atk, defense, speed, image_path=None):
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
        self.root.geometry("1400x900")  # 視窗大小可以自訂，例如 1400x900
        self.root.resizable(True, True)  # 允許使用者縮放視窗

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.characters = []
        self.setup_characters()

        self.attacker_var = tk.StringVar()
        self.defender_var = tk.StringVar()
        self.attacker_var.trace("w", self.update_attacker_display)
        self.defender_var.trace("w", self.update_defender_display)

        self.set_background("C:/Users/bingh/Desktop/包裝/background.jpg")
        self.setup_styles()
        self.create_widgets()

        self.root.bind("<Configure>", self.on_resize)

    def set_background(self, path):
        if os.path.exists(path):
            self.bg_image_raw = Image.open(path)
            bg_resized = self.bg_image_raw.resize((self.screen_width, self.screen_height))
            self.bg_image = ImageTk.PhotoImage(bg_resized)
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 20), padding=12)
        style.configure("TLabel", background="#ffffff", font=("Helvetica", 20))
        style.configure("red.Horizontal.TProgressbar", foreground="red", background="red", thickness=14)

    def setup_characters(self):
        stats = {
            "海盜": (100, 30, 10, 15),
            "法師": (80, 40, 5, 25),
            "弓箭手": (90, 25, 8, 30),
            "精靈": (85, 35, 6, 35),
            "騎士": (110, 20, 15, 10),
            "獵人": (95, 15, 12, 20)
        }

        for name, (hp, atk, defense, speed) in stats.items():
            path = f"C:/Users/bingh/Desktop/包裝/{name}.jpeg"
            self.characters.append(Character(name, hp, atk, defense, speed, image_path=path))

        self.turn_order = sorted(self.characters, key=lambda c: -c.speed)
        self.current_turn_index = 0

    def create_widgets(self):
        padding = 40

        ttk.Label(self.root, text="攻擊者").place(x=padding, y=10)
        self.attacker_menu = ttk.OptionMenu(self.root, self.attacker_var, None, *[c.name for c in self.characters])

        ttk.Label(self.root, text="目標").place(x=self.screen_width - 300, y=10)
        self.defender_menu = ttk.OptionMenu(self.root, self.defender_var, None, *[c.name for c in self.characters])

        self.attack_button = ttk.Button(self.root, text="⚔️ 攻擊", command=self.attack)

        self.attacker_img = tk.Label(self.root, bg="#ffffff")
        self.attacker_bar = ttk.Progressbar(self.root, style="red.Horizontal.TProgressbar")
        self.attacker_stats = tk.Label(self.root, bg="#ffffff", font=("Helvetica", 18), justify="left")

        self.defender_img = tk.Label(self.root, bg="#ffffff")
        self.defender_bar = ttk.Progressbar(self.root, style="red.Horizontal.TProgressbar")
        self.defender_stats = tk.Label(self.root, bg="#ffffff", font=("Helvetica", 18), justify="left")

        self.status_label = tk.Label(self.root, bg="#ffffff", font=("Helvetica", 18), justify="left", anchor="nw")
        self.log = tk.Text(self.root, height=12, width=110, font=("Courier", 16), bg="#fbfbfd")

        self.update_status_board()
        self.attacker_var.set(self.turn_order[self.current_turn_index].name)


    def update_attacker_display(self, *args):
        self.update_character_display(self.attacker_var.get(), self.attacker_img, self.attacker_bar, self.attacker_stats)

    def update_defender_display(self, *args):
        self.update_character_display(self.defender_var.get(), self.defender_img, self.defender_bar, self.defender_stats)

    def update_character_display(self, name, image_label, health_bar, stats_label):
        char = next((c for c in self.characters if c.name == name), None)
        if char and os.path.exists(char.image_path):
            img = Image.open(char.image_path).resize((250, 250))
            rounded = self.make_rounded(img, 40)
            photo = ImageTk.PhotoImage(rounded)
            image_label.configure(image=photo)
            image_label.image = photo
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
            
    def on_resize(self, event):
        w = event.width
        h = event.height

        padding = 40
        img_size = int(min(w, h) * 0.15)  # 角色圖大小隨畫面比例

        # 攻擊者
        self.attacker_img.place(x=padding, y=padding, width=img_size, height=img_size)
        self.attacker_bar.place(x=padding, y=padding + img_size + 10, width=img_size)
        self.attacker_stats.place(x=padding, y=padding + img_size + 30)

        # 防守者
        self.defender_img.place(x=w - img_size - padding, y=padding, width=img_size, height=img_size)
        self.defender_bar.place(x=w - img_size - padding, y=padding + img_size + 10, width=img_size)
        self.defender_stats.place(x=w - img_size - padding, y=padding + img_size + 30)

        # 選單和按鈕
        self.attacker_menu.place(x=padding + 160, y=10)
        self.defender_menu.place(x=w - 200, y=10)
        self.attack_button.place(x=w // 2 - 60, y=50)

        # 狀態欄
        self.status_label.place(x=w // 2 - 300, y=h - 480)

        # 戰鬥紀錄 log
        self.log.place(x=w // 2 - 450, y=h - 300)

        # 背景圖大小也重新設定
        if hasattr(self, "bg_image_raw"):
            bg_resized = self.bg_image_raw.resize((w, h))
            self.bg_image = ImageTk.PhotoImage(bg_resized)
            self.bg_label.configure(image=self.bg_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = BattleApp(root)
    root.mainloop()

