import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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

        # Поиск по класснейму
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="🔍 Поиск:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_tree(self.search_var.get()))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_frame, text="✕ Очистить", command=lambda: self.search_var.set("")).pack(side="left", padx=5)

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
        
        # Хранилище для фильтрации
        self._all_artifacts_data = []

    def filter_tree(self, search_term):
        """Фильтрация списка артефактов по класснейму"""
        search_term = search_term.lower().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            # Показываем все
            for i, art in enumerate(self.main_data["artifacts"]):
                pos_cnt = sum(1 for v in art.get("positiveEffects", {}).values() if v != 0)
                neg_cnt = sum(1 for v in art.get("negativeEffects", {}).values() if v != 0)
                self.tree.insert("", "end", iid=str(i), values=(i, art.get("className","?"), art.get("workInHands","?"),
                         art.get("workInInventory","?"), art.get("areaRadius","?"), pos_cnt, neg_cnt))
        else:
            # Фильтруем по класснейму
            for i, art in enumerate(self.main_data["artifacts"]):
                class_name = art.get("className", "").lower()
                if search_term in class_name:
                    pos_cnt = sum(1 for v in art.get("positiveEffects", {}).values() if v != 0)
                    neg_cnt = sum(1 for v in art.get("negativeEffects", {}).values() if v != 0)
                    self.tree.insert("", "end", iid=str(i), values=(i, art.get("className","?"), art.get("workInHands","?"),
                             art.get("workInInventory","?"), art.get("areaRadius","?"), pos_cnt, neg_cnt))

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
            self._edit_mode = "new"
        else:
            editor_data = copy.deepcopy(self.main_data["artifacts"][index])
            self.current_index = index
            self._edit_mode = "edit"
            
        win = tk.Toplevel(self.root)
        win.title(f"Редактор артефакта {'(Новый)' if index is None else '#'+str(index+1)}")
        win.geometry("950x700")
        
        # Основные поля
        ttk.Label(win, text="Основные параметры:", font=("Arial", 11, "bold")).pack(anchor="w", padx=15, pady=(15,5))
        fields = [
            ("className", "Класснейм (ключ)", False),
            ("workInHands", "Работает в руке (1/0)", True),
            ("workInInventory", "Работает в инвентаре (1/0)", True),
            ("workInArea", "Работает в области (1/0)", True),
            ("areaRadius", "Радиус аномалии (м)", False),
            ("areaPowerMode", "Мощность зоны", False)
        ]
        forms = {}
        for key, lbl, is_binary in fields:
            frm = ttk.Frame(win)
            frm.pack(fill="x", padx=20, pady=2)
            ttk.Label(frm, text=f"{lbl}: ", width=32, anchor="e").pack(side="left")
            ent = ttk.Entry(frm, width=15)
            ent.insert(0, str(editor_data.get(key)))
            ent.pack(side="left", padx=5)
            forms[key] = ent
            
        # Вкладки для эффектов
        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        eff_entries = {}
        for eff_type, title, color in [
            ("positiveEffects", "✅ Позитивные эффекты", "green"),
            ("negativeEffects", "❌ Негативные эффекты", "red")
        ]:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=title)
            
            # Создаём canvas с прокруткой для таблицы эффектов
            canvas = tk.Canvas(frame, highlightthickness=0)
            scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            inner_frame = ttk.Frame(canvas)
            
            inner_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_y.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_y.pack(side="right", fill="y")
            
            # Заголовки таблицы
            ttk.Label(inner_frame, text="Эффект", font=("Arial", 10, "bold"), width=20, anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(inner_frame, text="Значение", font=("Arial", 10, "bold"), width=15, anchor="center").grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(inner_frame, text="Описание", font=("Arial", 10, "bold"), width=40, anchor="w").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            effect_entries = {}
            effect_descriptions = {
                "health": "Здоровье", "blood": "Кровь", "shock": "Шок",
                "water": "Вода", "energy": "Энергия", "stamina": "Выносливость",
                "sleeping": "Сон", "mind": "Рассудок", "pain": "Боль",
                "contusion": "Контузия", "hematomas": "Гематомы",
                "lightBleeding": "Лёгкое кровотечение", "heavyBleeding": "Сильное кровотечение",
                "bulletWounds": "Пулевые ранения", "viscera": "Внутренности",
                "sepsis": "Сепсис", "zombieVirus": "Вирус зомби", "influenza": "Грипп",
                "poison": "Отравление", "biohazard": "Биоугроза", "rabies": "Бешенство",
                "overdose": "Передозировка", "immunity": "Иммунитет",
                "radiation": "Радиация", "temperature": "Температура тела",
                "brokenLeg": "Сломанная нога", "jumpHeight": "Высота прыжка",
                "meleeDamage": "Урон ближнего боя"
            }
            
            for row, effect_key in enumerate(DEFAULT_EFFECT_KEYS, start=1):
                ttk.Label(inner_frame, text=effect_key, width=20, anchor="w").grid(row=row, column=0, padx=5, pady=2, sticky="w")
                entry = ttk.Entry(inner_frame, width=15)
                val = editor_data.get(eff_type, {}).get(effect_key, 0.0)
                entry.insert(0, str(val))
                entry.grid(row=row, column=1, padx=5, pady=2)
                effect_entries[effect_key] = entry
                
                desc = effect_descriptions.get(effect_key, "")
                ttk.Label(inner_frame, text=desc, width=40, anchor="w", foreground="gray").grid(row=row, column=2, padx=5, pady=2, sticky="w")
            
            eff_entries[eff_type] = effect_entries
        
        def apply_changes():
            try:
                new_data = {}
                for key, wgt in forms.items():
                    val = wgt.get().strip()
                    if not val:
                        raise ValueError(f"Поле '{key}' не может быть пустым")
                    if key.startswith("work"):
                        if val not in ("0", "1"):
                            raise ValueError(f"Поле '{key}' должно быть 0 или 1")
                        new_data[key] = int(val)
                    elif key in ("areaRadius", "areaPowerMode"):
                        new_data[key] = float(val)
                    else:
                        new_data[key] = val
                        
                # Собираем эффекты из таблицы
                for eff_type in ("positiveEffects", "negativeEffects"):
                    effects_dict = {}
                    for effect_key, entry_widget in eff_entries[eff_type].items():
                        val_str = entry_widget.get().strip()
                        if not val_str:
                            raise ValueError(f"Поле эффекта '{effect_key}' в разделе '{eff_type}' не может быть пустым. Введите 0 если эффект не нужен.")
                        try:
                            val = float(val_str)
                        except ValueError:
                            raise ValueError(f"Неверное числовое значение для эффекта '{effect_key}': {val_str}")
                        effects_dict[effect_key] = val
                    new_data[eff_type] = effects_dict
                
                # Добавляем effects как объединение positive и negative (для совместимости)
                combined_effects = make_template_dict(0.0)
                for k in DEFAULT_EFFECT_KEYS:
                    pos_val = new_data["positiveEffects"].get(k, 0.0)
                    neg_val = new_data["negativeEffects"].get(k, 0.0)
                    combined_effects[k] = pos_val + neg_val
                new_data["effects"] = combined_effects
                
                # Мерж с шаблоном на случай пропущенных ключей
                base = copy.deepcopy(DEFAULT_ARTIFACT)
                base.update(new_data)
                # Перезаписываем объекты, добавляя недостающие ключи из шаблона
                for eff_key in ("effects", "positiveEffects", "negativeEffects"):
                    self._normalize_effect_keys(base[eff_key])
                    
                if self._edit_mode == "new":
                    self.main_data["artifacts"].append(base)
                else:
                    self.main_data["artifacts"][self.current_index] = base
                    
                self.refresh_tree()
                win.destroy()
                self.status_var.set("Изменения применены в память. Нажмите 💾 Сохранить.")
                
            except Exception as e:
                messagebox.showerror("Ошибка валидации", f"Проверьте введённые данные:\n{str(e)}")

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", padx=15, pady=15)
        ttk.Button(btn_frame, text="✅ Применить", command=apply_changes).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=win.destroy).pack(side="right", padx=5)

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