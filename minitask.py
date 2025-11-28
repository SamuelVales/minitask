#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniTask - Nástroj pro nahrávání a přehrávání maker
Podobný TinyTask
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import json
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key


class MiniTask:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniTask - Nahrávání a přehrávání maker")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Inicializace proměnných
        self.recording = False
        self.playing = False
        self.actions = []
        self.start_time = None
        self.current_file = None
        self.playback_speed = 1.0
        self.repeat_count = 1
        self.continuous_playback = False
        
        # Controllery pro simulaci
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Listenery
        self.mouse_listener = None
        self.keyboard_listener = None
        
        self.create_widgets()
        self.setup_hotkeys()
        
    def create_widgets(self):
        """Vytvoření grafického rozhraní"""
        # Hlavní frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Nadpis
        title_label = ttk.Label(main_frame, text="MiniTask", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Připraven")
        status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                font=("Arial", 10))
        status_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Tlačítka - horní řada
        button_frame1 = ttk.Frame(main_frame)
        button_frame1.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.record_btn = ttk.Button(button_frame1, text="⏺ Nahrávat (F3)",
                                     command=self.toggle_recording, width=20)
        self.record_btn.grid(row=0, column=0, padx=5)
        
        self.play_btn = ttk.Button(button_frame1, text="▶ Přehrát (F4)",
                                   command=self.play_macro, width=20)
        self.play_btn.grid(row=0, column=1, padx=5)
        
        self.stop_btn = ttk.Button(button_frame1, text="⏹ Stop (ESC)",
                                   command=self.stop_all, width=20, state="disabled")
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        # Tlačítka - střední řada
        button_frame2 = ttk.Frame(main_frame)
        button_frame2.grid(row=3, column=0, columnspan=3, pady=5)
        
        self.save_btn = ttk.Button(button_frame2, text="💾 Uložit",
                                   command=self.save_macro, width=20)
        self.save_btn.grid(row=0, column=0, padx=5)
        
        self.load_btn = ttk.Button(button_frame2, text="📂 Načíst",
                                   command=self.load_macro, width=20)
        self.load_btn.grid(row=0, column=1, padx=5)
        
        self.new_btn = ttk.Button(button_frame2, text="🗎 Nové makro",
                                 command=self.new_macro, width=20)
        self.new_btn.grid(row=0, column=2, padx=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        # Nastavení rychlosti
        speed_frame = ttk.LabelFrame(main_frame, text="Rychlost přehrávání", padding="10")
        speed_frame.grid(row=5, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(speed_frame, text="Pomalejší").grid(row=0, column=0)
        self.speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0,
                                     orient=tk.HORIZONTAL, command=self.update_speed)
        self.speed_scale.set(1.0)
        self.speed_scale.grid(row=0, column=1, padx=10, sticky=(tk.W, tk.E))
        ttk.Label(speed_frame, text="Rychlejší").grid(row=0, column=2)
        
        self.speed_label = ttk.Label(speed_frame, text="1.0x")
        self.speed_label.grid(row=0, column=3, padx=10)
        
        speed_frame.columnconfigure(1, weight=1)
        
        # Nastavení opakování
        repeat_frame = ttk.LabelFrame(main_frame, text="Opakování", padding="10")
        repeat_frame.grid(row=6, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(repeat_frame, text="Počet opakování:").grid(row=0, column=0, padx=5)
        self.repeat_spinbox = ttk.Spinbox(repeat_frame, from_=1, to=1000,
                                         width=10, command=self.update_repeat)
        self.repeat_spinbox.set(1)
        self.repeat_spinbox.grid(row=0, column=1, padx=5)
        
        self.continuous_var = tk.BooleanVar()
        self.continuous_check = ttk.Checkbutton(repeat_frame, text="Nepřetržité opakování",
                                               variable=self.continuous_var,
                                               command=self.update_continuous)
        self.continuous_check.grid(row=0, column=2, padx=20)
        
        # Informační panel
        info_frame = ttk.LabelFrame(main_frame, text="Informace", padding="10")
        info_frame.grid(row=7, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.info_var = tk.StringVar(value="Akcí nahráno: 0 | Soubor: Nový")
        ttk.Label(info_frame, textvariable=self.info_var).grid(row=0, column=0)
        
        # Nápověda
        help_text = "Klávesové zkratky: F3 - Nahrávat | F4 - Přehrát | ESC - Stop"
        ttk.Label(main_frame, text=help_text, font=("Arial", 8),
                 foreground="gray").grid(row=8, column=0, columnspan=3, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        
    def setup_hotkeys(self):
        """Nastavení globálních klávesových zkratek"""
        def on_press(key):
            try:
                if key == keyboard.Key.f3 and not self.playing:
                    self.root.after(0, self.toggle_recording)
                elif key == keyboard.Key.f4:
                    if self.playing:
                        # Pokud už makro běží, zastaví ho
                        self.root.after(0, self.stop_all)
                    elif not self.recording:
                        # Pokud neběží, spustí ho
                        self.root.after(0, self.play_macro)
                elif key == keyboard.Key.esc:
                    self.root.after(0, self.stop_all)
            except:
                pass
        
        # Spustí listener pro horké klávesy v pozadí
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
        
    def toggle_recording(self):
        """Spuštění/zastavení nahrávání"""
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()
            
    def start_recording(self):
        """Spuštění nahrávání"""
        self.recording = True
        self.actions = []
        self.start_time = time.time()
        
        # Aktualizace UI
        self.status_var.set("🔴 Nahrávám...")
        self.record_btn.config(text="⏹ Zastavit nahrávání (F3)")
        self.play_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.save_btn.config(state="disabled")
        self.load_btn.config(state="disabled")
        
        # Spuštění listenerů
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
    def stop_recording(self):
        """Zastavení nahrávání"""
        self.recording = False
        
        # Zastavení listenerů
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Aktualizace UI
        self.status_var.set(f"✓ Nahrávání dokončeno - {len(self.actions)} akcí")
        self.record_btn.config(text="⏺ Nahrávat (F3)")
        self.play_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.save_btn.config(state="normal")
        self.load_btn.config(state="normal")
        self.update_info()
        
    def on_mouse_move(self, x, y):
        """Zaznamenání pohybu myši"""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'type': 'mouse_move',
                'x': x,
                'y': y,
                'time': timestamp
            })
            
    def on_mouse_click(self, x, y, button, pressed):
        """Zaznamenání kliknutí myši"""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'time': timestamp
            })
            
    def on_mouse_scroll(self, x, y, dx, dy):
        """Zaznamenání scrollování"""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'type': 'mouse_scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'time': timestamp
            })
            
    def on_key_press(self, key):
        """Zaznamenání stisknutí klávesy"""
        if self.recording:
            # Ignorovat ESC při nahrávání
            if key == keyboard.Key.esc:
                return
                
            timestamp = time.time() - self.start_time
            try:
                key_char = key.char if hasattr(key, 'char') else str(key)
            except:
                key_char = str(key)
                
            self.actions.append({
                'type': 'key_press',
                'key': key_char,
                'time': timestamp
            })
            
    def on_key_release(self, key):
        """Zaznamenání uvolnění klávesy"""
        if self.recording:
            # Ignorovat ESC při nahrávání
            if key == keyboard.Key.esc:
                return
                
            timestamp = time.time() - self.start_time
            try:
                key_char = key.char if hasattr(key, 'char') else str(key)
            except:
                key_char = str(key)
                
            self.actions.append({
                'type': 'key_release',
                'key': key_char,
                'time': timestamp
            })
            
    def play_macro(self):
        """Přehrání makra"""
        if not self.actions:
            messagebox.showwarning("Varování", "Žádné makro k přehrání!")
            return
            
        if self.playing:
            return
            
        # Spuštění přehrávání v novém vlákně
        play_thread = threading.Thread(target=self._play_macro_thread)
        play_thread.daemon = True
        play_thread.start()
        
    def _play_macro_thread(self):
        """Vlákno pro přehrávání makra"""
        self.playing = True
        
        # Aktualizace UI
        self.root.after(0, lambda: self.status_var.set("▶ Přehrávám..."))
        self.root.after(0, lambda: self.record_btn.config(state="disabled"))
        self.root.after(0, lambda: self.play_btn.config(state="disabled"))
        self.root.after(0, lambda: self.stop_btn.config(state="normal"))
        
        try:
            repeat = int(self.repeat_spinbox.get()) if not self.continuous_playback else -1
            count = 0
            
            while (count < repeat or repeat == -1) and self.playing:
                count += 1
                last_time = 0
                
                for action in self.actions:
                    if not self.playing:
                        break
                        
                    # Čekání podle timestampu
                    wait_time = (action['time'] - last_time) / self.playback_speed
                    time.sleep(max(0, wait_time))
                    last_time = action['time']
                    
                    # Provádění akce
                    self._execute_action(action)
                    
                if self.continuous_playback:
                    # Krátká pauza mezi opakováními
                    time.sleep(0.1)
                    
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Chyba", f"Chyba při přehrávání: {str(e)}"))
        finally:
            self.playing = False
            self.root.after(0, lambda: self.status_var.set("✓ Přehrávání dokončeno"))
            self.root.after(0, lambda: self.record_btn.config(state="normal"))
            self.root.after(0, lambda: self.play_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            
    def _execute_action(self, action):
        """Provedení jedné akce"""
        try:
            if action['type'] == 'mouse_move':
                self.mouse_controller.position = (action['x'], action['y'])
                
            elif action['type'] == 'mouse_click':
                button_map = {
                    'Button.left': Button.left,
                    'Button.right': Button.right,
                    'Button.middle': Button.middle
                }
                button = button_map.get(action['button'], Button.left)
                
                if action['pressed']:
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
                    
            elif action['type'] == 'mouse_scroll':
                self.mouse_controller.scroll(action['dx'], action['dy'])
                
            elif action['type'] == 'key_press':
                key = self._parse_key(action['key'])
                self.keyboard_controller.press(key)
                
            elif action['type'] == 'key_release':
                key = self._parse_key(action['key'])
                self.keyboard_controller.release(key)
                
        except Exception as e:
            print(f"Chyba při provádění akce: {e}")
            
    def _parse_key(self, key_str):
        """Parsování klávesy ze stringu"""
        # Speciální klávesy
        if key_str.startswith('Key.'):
            key_name = key_str.replace('Key.', '')
            try:
                return getattr(Key, key_name)
            except:
                return key_str
        return key_str
        
    def stop_all(self):
        """Zastavení všech operací"""
        if self.recording:
            self.stop_recording()
        if self.playing:
            self.playing = False
            self.status_var.set("⏹ Zastaveno")
            
    def save_macro(self):
        """Uložení makra do souboru"""
        if not self.actions:
            messagebox.showwarning("Varování", "Žádné makro k uložení!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".mtask",
            filetypes=[("MiniTask soubory", "*.mtask"), ("Všechny soubory", "*.*")],
            initialfile="makro.mtask"
        )
        
        if filename:
            try:
                data = {
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'actions': self.actions,
                    'count': len(self.actions)
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                    
                self.current_file = filename
                self.status_var.set(f"✓ Uloženo: {filename}")
                self.update_info()
                messagebox.showinfo("Úspěch", "Makro bylo úspěšně uloženo!")
                
            except Exception as e:
                messagebox.showerror("Chyba", f"Chyba při ukládání: {str(e)}")
                
    def load_macro(self):
        """Načtení makra ze souboru"""
        filename = filedialog.askopenfilename(
            filetypes=[("MiniTask soubory", "*.mtask"), ("Všechny soubory", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.actions = data.get('actions', [])
                self.current_file = filename
                self.status_var.set(f"✓ Načteno: {filename}")
                self.update_info()
                messagebox.showinfo("Úspěch", f"Načteno {len(self.actions)} akcí!")
                
            except Exception as e:
                messagebox.showerror("Chyba", f"Chyba při načítání: {str(e)}")
                
    def new_macro(self):
        """Vytvoření nového makra"""
        if self.actions:
            response = messagebox.askyesno(
                "Potvrzení",
                "Opravdu chcete vytvořit nové makro? Neuložené změny budou ztraceny."
            )
            if not response:
                return
                
        self.actions = []
        self.current_file = None
        self.status_var.set("Nové makro vytvořeno")
        self.update_info()
        
    def update_speed(self, value):
        """Aktualizace rychlosti přehrávání"""
        self.playback_speed = float(value)
        self.speed_label.config(text=f"{self.playback_speed:.1f}x")
        
    def update_repeat(self):
        """Aktualizace počtu opakování"""
        try:
            self.repeat_count = int(self.repeat_spinbox.get())
        except:
            self.repeat_count = 1
            
    def update_continuous(self):
        """Aktualizace nepřetržitého opakování"""
        self.continuous_playback = self.continuous_var.get()
        if self.continuous_playback:
            self.repeat_spinbox.config(state="disabled")
        else:
            self.repeat_spinbox.config(state="normal")
            
    def update_info(self):
        """Aktualizace informačního panelu"""
        file_name = "Nový" if not self.current_file else self.current_file.split('/')[-1].split('\\')[-1]
        self.info_var.set(f"Akcí nahráno: {len(self.actions)} | Soubor: {file_name}")
        
    def on_closing(self):
        """Při zavření aplikace"""
        if self.actions and not self.current_file:
            response = messagebox.askyesnocancel(
                "Uložit změny?",
                "Máte neuložené makro. Chcete ho uložit před ukončením?"
            )
            if response is True:  # Ano
                self.save_macro()
            elif response is None:  # Zrušit
                return
                
        # Zastavení všech listenerů
        self.stop_all()
        if hasattr(self, 'hotkey_listener'):
            self.hotkey_listener.stop()
            
        self.root.destroy()


def main():
    root = tk.Tk()
    app = MiniTask(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
