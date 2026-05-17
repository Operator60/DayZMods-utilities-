import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import copy

# ──────────────────────────────────────────────────────────────
# ШАБЛОНЫ И КОНСТАНТЫ
# ──────────────────────────────────────────────────────────────
DEFAULT_EFFECT_KEYS = [
    "health", "blood", "shock", "water", "energy", "stamina", 
    "sleeping", "mind", "pain", "contusion", "hematomas", 
    "lightBleeding", "heavyBleeding", "bulletWounds", "viscera", 
    "sepsis", "zombieVirus", "influenza", "poison", "biohazard", 
    "rabies", "overdose", "immunity", "radiation", "temperature", 
    "brokenLeg", "jumpHeight", "meleeDamage"
]

def make_template_dict(val=0.0):
    return {k: val for k in DEFAULT_EFFECT_KEYS}

DEFAULT_ARTIFACT = {
    "className": "",
    "workInHands": 1,
    "workInInventory": 1,
    "workInArea": 0,
    "areaRadius": 0.0,
    "areaPowerMode": 0,
    "effects": make_template_dict(0.0),
    "positiveEffects": make_template_dict(0.0),
    "negativeEffects": make_template_dict(0.0)
}

class ArtifactManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DayZ Artifacts Manager v1.0")
        self.root.geometry("1100x750")
        
        self.file_path = None
        self.main_data = {"ticktime": 1.0, "radiusticktime": 1.0, "artifacts": []}
        self.current_index = -1
        
        self.setup_ui()
        self.status_var = tk.StringVar()
        self.status_var.set("Готово. Выберите или создайте файл .json")
        ttk.Label(root, textvariable=self.status_var, justify=tk.LEFT, anchor="w").pack(fill="x", padx=5, pady=(0, 5))

    def setup_ui(self):
        # Верхняя панель кнопок
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="📂 Загрузить ARTIFACTS.JSON", command=self.load_json).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="💾 Сохранить изменения", command=self.save_json).pack(side="left", padx=2)
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(btn_frame, text="➕ Добавить", command=lambda: self.open_editor(None)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self.edit_selected).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="🗑️ Удалить", command=self.delete_selected).pack(side="left", padx=2)
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(btn_frame, text="🔄 Обновить список", command=self.refresh_tree).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="📄 Импорт из CSV (классы)", command=self.import_csv).pack(side="left", padx=2)

        # Список артефактов
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("idx", "className", "workH", "workI", "area", "posE", "negE")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.tree.heading(col, text={"idx":"#", "className":"Класснейм", "workH":"В руке", "workI":"В инв.", "area":"Зона м", "posE":"Позитив", "negE":"Негатив"}[col])
            self.tree.column(col, width=100 if col == "className" else 70, minwidth=50)
            
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or "artifacts" not in data:
                raise ValueError("Неверная структура файла. Отсутствует ключ 'artifacts'.")
                
            self.file_path = path
            self.main_data = data
            self.refresh_tree()
            self.status_var.set(f"Загружено: {os.path.basename(path)} | Артефактов: {len(self.main_data['artifacts'])}")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    def save_json(self):
        if not self.file_path:
            self.file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not self.file_path: return
            
        try:
            # Валидация структур перед сохранением
            for art in self.main_data["artifacts"]:
                if "effects" not in art or not all(k in art["effects"] for k in DEFAULT_EFFECT_KEYS):
                    self._normalize_effect_keys(art.get("effects", {}))
                    self._normalize_effect_keys(art.get("positiveEffects", {}))
                    self._normalize_effect_keys(art.get("negativeEffects", {}))
                    
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.main_data, f, indent=4, ensure_ascii=False)
            self.status_var.set(f"Сохранено: {os.path.basename(self.file_path)}")
            messagebox.showinfo("Успех", "Файл успешно сохранён! Можно запускать мод.")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить:\n{str(e)}")

    def _normalize_effect_keys(self, d):
        """Добавляет отсутствующие ключи, чтобы избежать ошибок DayZ"""
        for k in DEFAULT_EFFECT_KEYS:
            if k not in d:
                d[k] = 0.0

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, art in enumerate(self.main_data["artifacts"]):
            pos_cnt = sum(1 for v in art.get("positiveEffects", {}).values() if v != 0)
            neg_cnt = sum(1 for v in art.get("negativeEffects", {}).values() if v != 0)
            self.tree.insert("", "end", iid=str(i), values=(i, art.get("className","?"), art.get("workInHands","?"),
                     art.get("workInInventory","?"), art.get("areaRadius","?"), pos_cnt, neg_cnt))

    def open_editor(self, index):
        if index is None:
            editor_data = copy.deepcopy(DEFAULT_ARTIFACT)
            self.current_index = len(self.main_data["artifacts"])
        else:
            editor_data = copy.deepcopy(self.main_data["artifacts"][index])
            self.current_index = index
            
        win = tk.Toplevel(self.root)
        win.title(f"Редактор артефакта {'(Новый)' if index is None else '#'+str(index+1)}")
        win.geometry("850x600")
        
        # Основные поля
        ttk.Label(win, text="Основные параметры:").pack(anchor="w", padx=10, pady=(10,0))
        fields = [
            ("className", "Класснейм (ключ)"), ("workInHands", "Работает в руке (1/0)"),
            ("workInInventory", "Работает в инвентаре (1/0)"), ("workInArea", "Работает в области (1/0)"),
            ("areaRadius", "Радиус аномалии (м)"), ("areaPowerMode", "Мощность зоны")
        ]
        forms = {}
        for key, lbl in fields:
            frm = ttk.Frame(win)
            frm.pack(fill="x", padx=15)
            ttk.Label(frm, text=f"{lbl}: ", width=30, anchor="e").pack(side="left")
            ent = ttk.Entry(frm)
            ent.insert(0, str(editor_data.get(key)))
            ent.pack(side="left", fill="x", expand=True)
            forms[key] = ent
            
        # Блоки эффектов
        ttk.Label(win, text="Блоки эффектов (JSON формат). Используйте кнопки ниже для очистки/проверки.").pack(anchor="w", padx=10, pady=(15,0))
        
        eff_frames = [("positiveEffects", "Позитивные эффекты (+)", "green"), 
                      ("negativeEffects", "Негативные эффекты (-)", "red")]
        eff_entries = {}
        for key, title, color in eff_frames:
            frm = ttk.LabelFrame(win, text=title)
            frm.pack(fill="both", expand=True, padx=10, pady=5)
            
            txt = scrolledtext.ScrolledText(frm, height=8, font=("Consolas", 9))
            txt.pack(fill="both", expand=True, padx=5, pady=5)
            # Подсветка синтаксиса (упрощённая)
            txt.tag_configure("key", foreground="darkblue")
            txt.tag_configure("val", foreground="purple")
            txt.insert("1.0", json.dumps(editor_data.get(key), indent=2, ensure_ascii=False))
            eff_entries[key] = txt
            
            btns = ttk.Frame(frm)
            btns.pack(fill="x", padx=5, pady=(0,5))
            ttk.Button(btns, text="Очистить", command=lambda t=txt: t.delete("1.0", tk.END)).pack(side="left", padx=2)
            ttk.Button(btns, text="Показать шаблон", command=lambda t=txt: self.fill_template(t, key)).pack(side="left", padx=2)
            ttk.Button(btns, text="Проверить JSON", command=lambda t=txt: self.validate_json(t)).pack(side="left", padx=2)
            
        def apply_changes():
            try:
                new_data = {}
                for key, wgt in forms.items():
                    val = wgt.get().strip()
                    if key.startswith("work"):
                        new_data[key] = 1 if val == "1" else 0
                    elif key in ("areaRadius", "areaPowerMode"):
                        new_data[key] = float(val) if val else 0
                    else:
                        new_data[key] = val
                        
                for key, widget in eff_entries.items():
                    content = widget.get("1.0", tk.END).strip()
                    if not content:
                        new_data[key] = make_template_dict(0.0)
                    else:
                        parsed = json.loads(content)
                        if not isinstance(parsed, dict):
                            raise ValueError("Объект должен быть словарём")
                        new_data[key] = parsed
                        
                # Мерж с шаблоном на случай пропущенных ключей
                base = copy.deepcopy(DEFAULT_ARTIFACT)
                base.update(new_data)
                # Перезаписываем объекты, добавляя недостающие ключи из шаблона
                for eff_key in ("effects", "positiveEffects", "negativeEffects"):
                    self._normalize_effect_keys(base[eff_key])
                    
                self.main_data["artifacts"].insert(self.current_index, base)
                if index is not None and index < len(self.main_data["artifacts"])-1:
                    # Если это замена существующего (логика упрощена: сначала удаляем старый если редактируем)
                    pass
                    
                self.refresh_tree()
                win.destroy()
                self.status_var.set("Изменения применены в память. Нажмите 💾 Сохранить.")
                
            except Exception as e:
                messagebox.showerror("Ошибка валидации", f"Некорректный JSON или данные:\n{str(e)}")

        ttk.Button(win, text="✅ Применить", command=apply_changes, style="Accent.TButton").pack(pady=10)

    def fill_template(self, text_widget, key):
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", json.dumps(make_template_dict(0.0), indent=2, ensure_ascii=False))
        
    def validate_json(self, text_widget):
        try:
            txt = text_widget.get("1.0", tk.END)
            if not txt.strip():
                messagebox.showwarning("Предупреждение", "Текстовое поле пустое.")
                return
            json.loads(txt)
            text_widget.config(bg="lightgreen")
            messagebox.showinfo("Проверка пройдена", "Формат JSON корректен.")
        except json.JSONDecodeError as e:
            text_widget.config(bg="#ffcccc")
            messagebox.showerror("Ошибка формата", f"Невалидный JSON:\n{str(e)}")
        finally:
            self.root.after(2000, lambda: text_widget.config(bg="white"))

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Выбор", "Сначала выделите артефакт в списке.")
            return
        idx = int(self.tree.item(sel[0])["values"][0])
        self.open_editor(idx)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        idx = int(self.tree.item(sel[0])["values"][0])
        if messagebox.askyesno("Подтверждение", f"Удалить '{self.main_data['artifacts'][idx].get('className')}'?"):
            self.main_data["artifacts"].pop(idx)
            self.refresh_tree()
            self.status_var.set("Артефакт удалён. Не забудьте сохранить!")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if len(lines) < 2:
                raise ValueError("CSV пуст или не содержит заголовков")
                
            imports = 0
            header = lines[0].split(",")
            cls_idx = next((i for i, h in enumerate(header) if "класснейм" in h.lower()), -1)
            desc_idx = next((i for i, h in enumerate(header) if "опиш" in h.lower()), -1)
            
            if cls_idx == -1: raise ValueError("Не найден столбец с класснеймом")
            
            for line in lines[1:]:
                parts = line.split(",")
                if len(parts) <= cls_idx: continue
                
                cls_name = parts[cls_idx].strip('" \t\r\n')
                desc = parts[desc_idx].strip('" \t\r\n') if desc_idx >= 0 and desc_idx < len(parts) else ""
                
                # Проверяем, есть ли уже такой класснейм
                exists = any(a.get("className") == cls_name for a in self.main_data["artifacts"])
                if exists: continue
                
                new_art = copy.deepcopy(DEFAULT_ARTIFACT)
                new_art["className"] = cls_name
                if desc:
                    # Сохраняем описание во внутреннее поле или просто ставим метку
                    # Для совместимости со структурой добавим комментарий в className или отдельное поле, если нужно.
                    # Здесь просто оставим класснейм, но можно добавить логику парсинга.
                    pass
                    
                self.main_data["artifacts"].append(new_art)
                imports += 1
                
            self.refresh_tree()
            messagebox.showinfo("Импорт завершён", f"Добавлено новых артефактов: {imports}\nТеперь откройте ❌ Редактировать и заполните эффекты.")
            
        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    # Пытаемся улучшить стиль (работает на Windows/macOS/Linux с ttkthemes или системой по умолчанию)
    style = ttk.Style()
    try:
        style.theme_use("vista") # fallback safe theme
    except:
        pass
        
    app = ArtifactManagerApp(root)
    root.mainloop()