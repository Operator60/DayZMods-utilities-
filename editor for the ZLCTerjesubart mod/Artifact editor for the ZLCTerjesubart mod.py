import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import copy
import random
import re
import csv

# Импортируем систему локализации
from localization import _, localizer, LOCALE_RU

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

# Профессиональные описания эффектов из локализации
EFFECT_DESCRIPTIONS = {
    "health": _("effect_health"),
    "blood": _("effect_blood"),
    "shock": _("effect_shock"),
    "water": _("effect_water"),
    "energy": _("effect_energy"),
    "stamina": _("effect_stamina"),
    "sleeping": _("effect_sleeping"),
    "mind": _("effect_mind"),
    "pain": _("effect_pain"),
    "contusion": _("effect_contusion"),
    "hematomas": _("effect_hematomas"),
    "lightBleeding": _("effect_lightBleeding"),
    "heavyBleeding": _("effect_heavyBleeding"),
    "bulletWounds": _("effect_bulletWounds"),
    "viscera": _("effect_viscera"),
    "sepsis": _("effect_sepsis"),
    "zombieVirus": _("effect_zombieVirus"),
    "influenza": _("effect_influenza"),
    "poison": _("effect_poison"),
    "biohazard": _("effect_biohazard"),
    "rabies": _("effect_rabies"),
    "overdose": _("effect_overdose"),
    "immunity": _("effect_immunity"),
    "radiation": _("effect_radiation"),
    "temperature": _("effect_temperature"),
    "brokenLeg": _("effect_brokenLeg"),
    "jumpHeight": _("effect_jumpHeight"),
    "meleeDamage": _("effect_meleeDamage"),
}

# Ключевые слова для парсинга описаний артефактов (лорных текстов)
# Связывает эффекты с возможными упоминаниями в описании
EFFECT_KEYWORDS = {
    "health": ["здоров", "жизн", "hp", "health", "леч", "восстановлен", "регенер"],
    "blood": ["кров", "blood", "гемоглобин", "плазм"],
    "shock": ["шок", "shock", "болев", "боль", "pain"],
    "water": ["вод", "water", "влажн", "жажд", "пить"],
    "energy": ["энерг", "energy", "калори", "сытост", "еда"],
    "stamina": ["стамина", "вынослив", "stamina", "устал", "бег", "спринт"],
    "sleeping": ["сон", "sleep", "бодр", "устал", "бессон"],
    "mind": ["рассуд", "психик", "mind", "ментальн", "разум", "глуп", "интеллект"],
    "pain": ["боль", "pain", "боле", "страдан"],
    "contusion": ["контуз", "потрясен", "мозг", "голова", "оглуш"],
    "hematomas": ["гематом", "синяк", "ушиб", "кровоподтек"],
    "lightBleeding": ["лёгк кровотеч", "слаб кровотеч", "легк кровоточ"],
    "heavyBleeding": ["сильн кровотеч", "тяжел кровотеч", "кровав"],
    "bulletWounds": ["пулев", "ранен", "пуля", "прострел"],
    "viscera": ["орган", "внутренн", "живот", "печен", "почек", "сердц"],
    "sepsis": ["сепсис", "заражен", "инфекц", "гниени"],
    "zombieVirus": ["зомби", "вирус", "инфекци", "мутаци", "мертвец"],
    "influenza": ["грипп", "простуд", "болезн", "температур", "кашель", "насморк"],
    "poison": ["отрав", "яд", "токсин", "поison"],
    "biohazard": ["био", "радиацион", "химическ", "загрязнен", "опасн"],
    "rabies": ["бешенств", "собак", "животн", "вирус бешен"],
    "overdose": ["передоз", "препарат", "лекарств", "таблетк", "аптечк"],
    "immunity": ["иммун", "защит", "сопротивл", "резист"],
    "radiation": ["радиаци", "излучен", "рад", "дозиметр", "рентген"],
    "temperature": ["температур", "тепл", "холод", "градус", "термо"],
    "brokenLeg": ["сломан ног", "перелом", "костыл", "ходьб", "бег"],
    "jumpHeight": ["прыжк", "прыгать", "высот", "подпрыг"],
    "meleeDamage": ["урон ближн", " melee", "атак", "удар", "поврежден"],
}

class ArtifactManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(_("app_title"))
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Настройка стиля для более современного вида
        self.setup_styles()
        
        # Конфигурация для масштабирования главного окна
        self.root.grid_rowconfigure(2, weight=1)  # Treeview расширяется
        self.root.grid_columnconfigure(0, weight=1)
        
        self.file_path = None
        self.main_data = {"ticktime": 1.0, "radiusticktime": 1.0, "artifacts": []}
        self.current_index = -1
        
        self.setup_ui()
        self.status_var = tk.StringVar()
        self.status_var.set(_("status_ready"))
        ttk.Label(root, textvariable=self.status_var, justify=tk.LEFT, anchor="w").pack(fill="x", padx=5, pady=(0, 5))

    def setup_styles(self):
        """Настройка профессионального стиля интерфейса"""
        style = ttk.Style()
        
        # Устанавливаем современную тему если доступна
        available_themes = style.theme_names()
        if "vista" in available_themes:
            style.theme_use("vista")
        elif "clam" in available_themes:
            style.theme_use("clam")
        
        # Настраиваем цвета и шрифты
        style.configure("TButton", padding=8, font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("TLabelframe", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook.Tab", padding=[12, 8], font=("Segoe UI", 10))

    def setup_ui(self):
        # Верхняя панель кнопок с локализованными надписями
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text=_("btn_load_json"), command=self.load_json).pack(side="left", padx=2)
        ttk.Button(btn_frame, text=_("btn_save_json"), command=self.save_json).pack(side="left", padx=2)
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(btn_frame, text=_("btn_add"), command=lambda: self.open_editor(None)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text=_("btn_edit"), command=self.edit_selected).pack(side="left", padx=2)
        ttk.Button(btn_frame, text=_("btn_delete"), command=self.delete_selected).pack(side="left", padx=2)
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(btn_frame, text=_("btn_refresh"), command=self.refresh_tree).pack(side="left", padx=2)
        ttk.Button(btn_frame, text=_("btn_import_csv"), command=self.import_csv).pack(side="left", padx=2)
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(btn_frame, text=_("btn_bulk_edit"), command=self.open_bulk_editor).pack(side="left", padx=2)

        # Поиск по класснейму
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text=_("search_label")).pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_tree(self.search_var.get()))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_frame, text=_("search_clear"), command=lambda: self.search_var.set("")).pack(side="left", padx=5)

        # Список артефактов - используем pack с expand для масштабирования
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("idx", "className", "workH", "workI", "area", "posE", "negE")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            header_texts = {
                "idx": _("tree_header_idx"),
                "className": _("tree_header_classname"),
                "workH": _("tree_header_work_hands"),
                "workI": _("tree_header_work_inventory"),
                "area": _("tree_header_area_radius"),
                "posE": _("tree_header_positive_effects"),
                "negE": _("tree_header_negative_effects")
            }
            self.tree.heading(col, text=header_texts[col])
            # Увеличиваем ширину колонки className и делаем её растягиваемой
            if col == "className":
                self.tree.column(col, width=300, minwidth=150)
            else:
                self.tree.column(col, width=80, minwidth=60)
            
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
                raise ValueError(_("error_structure"))
                
            self.file_path = path
            self.main_data = data
            self.refresh_tree()
            self.status_var.set(_("status_loaded").format(
                filename=os.path.basename(path),
                count=len(self.main_data['artifacts'])
            ))
        except Exception as e:
            messagebox.showerror(_("error_load_title"), str(e))

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
            self.status_var.set(_("status_saved").format(filename=os.path.basename(self.file_path)))
            messagebox.showinfo(_("success_save_title"), _("success_save_message"))
        except Exception as e:
            messagebox.showerror(_("error_save_title"), f"{_('error_save_title')}:\n{str(e)}")

    def _normalize_effect_keys(self, d):
        """Добавляет отсутствующие ключи, чтобы избежать ошибок DayZ"""
        for k in DEFAULT_EFFECT_KEYS:
            if k not in d:
                d[k] = 0.0

    def _parse_description_to_effects(self, description_text):
        """
        Парсит лорное описание артефакта и извлекает числовые значения эффектов.
        Возвращает словарь с найденными эффектами и их значениями.
        
        Args:
            description_text: Текстовое описание артефакта из CSV
            
        Returns:
            dict: Словарь {effect_key: value} с найденными значениями
        """
        found_effects = {}
        text_lower = description_text.lower()
        
        # Регулярное выражение для поиска чисел (включая отрицательные и дробные)
        number_pattern = r'[-+]?\d*\.?\d+'
        
        # Для каждого эффекта ищем ключевые слова и числа рядом с ними
        for effect_key, keywords in EFFECT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Находим позицию ключевого слова
                    pos = text_lower.find(keyword)
                    
                    # Ищем число в окрестности ключевого слова (±100 символов)
                    start = max(0, pos - 100)
                    end = min(len(text_lower), pos + 100)
                    context = text_lower[start:end]
                    
                    # Находим все числа в контексте
                    numbers = re.findall(number_pattern, context)
                    
                    if numbers:
                        # Берём первое найденное число
                        try:
                            value = float(numbers[0])
                            
                            # Определяем знак эффекта по контексту
                            # Ключевые слова для положительных эффектов
                            positive_words = ["увелич", "повыш", "улучш", "усил", "восстанов", "леч", "защит", "бонус", "плюс", "+"]
                            # Ключевые слова для отрицательных эффектов
                            negative_words = ["уменьш", "пониж", "ухудш", "ослаб", "поврежд", "разруш", "минус", "-", "сниж"]
                            
                            is_positive = any(word in context for word in positive_words)
                            is_negative = any(word in context for word in negative_words)
                            
                            # Если найдены маркеры отрицательного эффекта, делаем число отрицательным
                            if is_negative and not is_positive and value > 0:
                                value = -value
                            # Если явный положительный эффект, убеждаемся что положительный
                            elif is_positive and value < 0:
                                value = abs(value)
                            
                            # Сохраняем значение (перезаписываем если уже было)
                            found_effects[effect_key] = round(value, 2)
                            
                        except ValueError:
                            continue
                    
                    # Нашли хотя бы одно совпадение по ключевому слову - переходим к следующему эффекту
                    break
        
        return found_effects

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
            title = _("editor_title_new")
        else:
            editor_data = copy.deepcopy(self.main_data["artifacts"][index])
            self.current_index = index
            self._edit_mode = "edit"
            title = _("editor_title_edit").format(index=index+1)
            
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("1000x750")
        win.minsize(900, 650)
        
        # Конфигурация для масштабирования окна редактора
        win.grid_rowconfigure(3, weight=1)  # Notebook расширяется
        win.grid_columnconfigure(0, weight=1)
        
        # Основные поля с локализованными заголовками
        ttk.Label(win, text=_("editor_main_params"), style="Header.TLabel").pack(anchor="w", padx=15, pady=(15,5))
        fields = [
            ("className", _("editor_field_classname"), False),
            ("workInHands", _("editor_field_work_hands"), True),
            ("workInInventory", _("editor_field_work_inventory"), True),
            ("workInArea", _("editor_field_work_area"), True),
            ("areaRadius", _("editor_field_area_radius"), False),
            ("areaPowerMode", _("editor_field_area_power"), False)
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
            
        # Вкладки для эффектов - с expand=True для масштабирования
        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        eff_entries = {}
        for eff_type, title_key in [
            ("positiveEffects", "tab_positive_effects"),
            ("negativeEffects", "tab_negative_effects")
        ]:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=_(title_key))
            
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
            
            # Заголовки таблицы - фиксированная ширина для колонок
            ttk.Label(inner_frame, text=_("table_header_effect"), font=("Segoe UI", 10, "bold"), width=25, anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(inner_frame, text=_("table_header_value"), font=("Segoe UI", 10, "bold"), width=15, anchor="center").grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(inner_frame, text=_("table_header_description"), font=("Segoe UI", 10, "bold"), width=50, anchor="w").grid(row=0, column=2, padx=5, pady=5, sticky="w")
            
            effect_entries = {}
            
            for row, effect_key in enumerate(DEFAULT_EFFECT_KEYS, start=1):
                ttk.Label(inner_frame, text=effect_key, width=25, anchor="w").grid(row=row, column=0, padx=5, pady=2, sticky="w")
                entry = ttk.Entry(inner_frame, width=15)
                val = editor_data.get(eff_type, {}).get(effect_key, 0.0)
                entry.insert(0, str(val))
                entry.grid(row=row, column=1, padx=5, pady=2, sticky="w")
                effect_entries[effect_key] = entry
                
                desc = EFFECT_DESCRIPTIONS.get(effect_key, "")
                # Перенос длинных описаний
                ttk.Label(inner_frame, text=desc, width=50, anchor="nw", foreground="gray", wraplength=400).grid(row=row, column=2, padx=5, pady=2, sticky="w")
            
            eff_entries[eff_type] = effect_entries
        
        def apply_changes():
            try:
                new_data = {}
                for key, wgt in forms.items():
                    val = wgt.get().strip()
                    if not val:
                        raise ValueError(_("error_field_empty").format(field=key))
                    if key.startswith("work"):
                        if val not in ("0", "1"):
                            raise ValueError(_("error_field_binary").format(field=key))
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
                            raise ValueError(_("error_effect_empty").format(effect=effect_key, section=eff_type))
                        try:
                            val = float(val_str)
                        except ValueError:
                            raise ValueError(_("error_field_number").format(effect=effect_key, value=val_str))
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
                self.status_var.set(_("status_changes_applied"))
                
            except Exception as e:
                messagebox.showerror(_("error_validation_title"), f"{_('error_validation_title')}\n{str(e)}")

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", padx=15, pady=15)
        
        # Кнопка для заполнения из описания CSV
        def fill_from_csv_description():
            self._open_csv_parser_dialog(win, forms, eff_entries)
        
        ttk.Button(btn_frame, text=_("btn_fill_from_csv"), command=fill_from_csv_description).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=_("btn_apply"), command=apply_changes).pack(side="right", padx=5)
        ttk.Button(btn_frame, text=_("btn_cancel"), command=win.destroy).pack(side="right", padx=5)

    def _open_csv_parser_dialog(self, editor_win, forms, eff_entries):
        """
        Открывает диалог выбора CSV файла и заполняет эффекты на основе описания.
        Работает как для одиночного редактора, так и для массовой настройки.
        """
        csv_path = filedialog.askopenfilename(
            title=_("csv_select_title"),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.file_path) if self.file_path else "."
        )
        
        if not csv_path:
            return
        
        class_name = forms.get("className", {}).get().strip() if hasattr(forms.get("className"), "get") else ""
        if not class_name:
            messagebox.showerror(_("error_validation_title"), _("error_classname_empty"))
            return
        
        try:
            description_text = None
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=",")
                
                # Ищем колонку с класснеймом и описанием
                classname_col = None
                desc_col = None
                
                if reader.fieldnames:
                    for col in reader.fieldnames:
                        col_lower = col.lower().strip()
                        if "класснейм" in col_lower or "class" in col_lower or "key" in col_lower:
                            classname_col = col
                        if "описание" in col_lower or "desc" in col_lower:
                            desc_col = col
                
                if not classname_col or not desc_col:
                    # Пробуем найти по позиции (первая - класснейм, вторая - описание)
                    if len(reader.fieldnames) >= 2:
                        classname_col = reader.fieldnames[0]
                        desc_col = reader.fieldnames[1]
                    else:
                        raise ValueError(_("csv_error_no_columns"))
                
                # Ищем артефакт по класснейму
                for row in reader:
                    if row.get(classname_col, "").strip() == class_name:
                        description_text = row.get(desc_col, "")
                        break
            
            if not description_text:
                messagebox.showwarning(_("warning_csv_not_found"), _("warning_csv_not_found").format(classname=class_name))
                return
            
            # Парсим описание
            found_effects = self._parse_description_to_effects(description_text)
            
            if not found_effects:
                messagebox.showinfo(_("info_no_effects_found"), _("info_no_effects_found"))
                return
            
            # Формируем сообщение о найденных эффектах
            preview_text = _("csv_found_effects").format(count=len(found_effects)) + "\n\n"
            for eff_key, value in sorted(found_effects.items()):
                eff_name = EFFECT_DESCRIPTIONS.get(eff_key, eff_key)
                sign = "+" if value >= 0 else ""
                preview_text += f"{eff_key} ({eff_name}): {sign}{value}\n"
            
            preview_text += "\n" + _("csv_apply_confirmation")
            
            result = messagebox.askyesno(_("csv_preview_title"), preview_text, icon=messagebox.INFO)
            
            if result:
                # Заполняем только пустые поля (со значением 0)
                filled_count = 0
                for eff_type in ["positiveEffects", "negativeEffects"]:
                    entries = eff_entries.get(eff_type, {})
                    for eff_key, value in found_effects.items():
                        if eff_key in entries:
                            current_val = entries[eff_key].get().strip()
                            try:
                                if float(current_val) == 0.0:
                                    entries[eff_key].delete(0, tk.END)
                                    entries[eff_key].insert(0, str(value))
                                    filled_count += 1
                            except ValueError:
                                pass
                
                if filled_count > 0:
                    messagebox.showinfo(_("success_csv_fill"), _("success_csv_fill").format(count=filled_count))
                else:
                    messagebox.showinfo(_("info_csv_no_empty"), _("info_csv_no_empty"))
                    
        except Exception as e:
            messagebox.showerror(_("error_csv_parse"), str(e))

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
        classname = self.main_data['artifacts'][idx].get('className', _('unknown_artifact'))
        if messagebox.askyesno(_("warning_confirm_delete"), _("warning_delete_message").format(classname=classname)):
            self.main_data["artifacts"].pop(idx)
            self.refresh_tree()
            self.status_var.set(_("status_artifact_deleted"))

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if len(lines) < 2:
                raise ValueError(_("csv_error_no_header"))
                
            imports = 0
            header = lines[0].split(",")
            cls_idx = next((i for i, h in enumerate(header) if "класснейм" in h.lower() or "classname" in h.lower()), -1)
            desc_idx = next((i for i, h in enumerate(header) if "опиш" in h.lower()), -1)
            
            if cls_idx == -1: raise ValueError(_("csv_error_no_classname"))
            
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
            messagebox.showinfo(_("success_import_title"), _("success_import_message").format(count=imports))
            
        except Exception as e:
            messagebox.showerror(_("error_import_title"), str(e))

    def open_bulk_editor(self):
        """Окно массовой настройки эффектов для выбранных артефактов"""
        if not self.main_data["artifacts"]:
            messagebox.showinfo(_("warning_no_artifacts"), _("warning_no_artifacts"))
            return
            
        win = tk.Toplevel(self.root)
        win.title(_("bulk_title"))
        win.geometry("1100x800")
        win.minsize(950, 700)
        
        # Конфигурация для масштабирования
        win.grid_rowconfigure(2, weight=1)  # Блок с эффектами расширяется
        win.grid_columnconfigure(0, weight=1)
        
        # Инструкция
        ttk.Label(win, text=_("bulk_instruction"), 
                  font=("Segoe UI", 11)).pack(pady=10)
        
        # === БЛОК 1: Выбор артефактов ===
        art_frame = ttk.LabelFrame(win, text=_("bulk_step_1"), padding=10)
        art_frame.pack(fill="x", padx=10, pady=5)
        
        # Список с чекбоксами для артефактов - фиксированная высота
        art_canvas = tk.Canvas(art_frame, height=120)
        art_scrollbar = ttk.Scrollbar(art_frame, orient="vertical", command=art_canvas.yview)
        art_inner = ttk.Frame(art_canvas)
        
        art_inner.bind("<Configure>", lambda e: art_canvas.configure(scrollregion=art_canvas.bbox("all")))
        art_canvas.create_window((0, 0), window=art_inner, anchor="nw")
        art_canvas.configure(yscrollcommand=art_scrollbar.set)
        
        art_canvas.pack(side="left", fill="both", expand=True)
        art_scrollbar.pack(side="right", fill="y")
        
        art_checkboxes = {}
        for i, art in enumerate(self.main_data["artifacts"]):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(art_inner, text=f"{art.get('className', _('unknown_artifact'))} (#{i+1})", variable=var)
            cb.grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
            art_checkboxes[i] = var
        
        # Кнопки выбора всех/снятия всех
        art_btn_frame = ttk.Frame(art_frame)
        art_btn_frame.pack(fill="x", pady=(5,0))
        ttk.Button(art_btn_frame, text=_("bulk_select_all"), 
                   command=lambda: [v.set(True) for v in art_checkboxes.values()]).pack(side="left", padx=5)
        ttk.Button(art_btn_frame, text=_("bulk_deselect_all"), 
                   command=lambda: [v.set(False) for v in art_checkboxes.values()]).pack(side="left", padx=5)
        
        # === БЛОК 2: Выбор эффектов ===
        eff_frame = ttk.LabelFrame(win, text=_("bulk_step_2"), padding=10)
        eff_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Вкладки для позитивных/негативных
        eff_notebook = ttk.Notebook(eff_frame)
        eff_notebook.pack(fill="both", expand=True)
        
        effect_checkboxes = {"positiveEffects": {}, "negativeEffects": {}}
        
        for eff_type, title_key in [("positiveEffects", "tab_positive_effects"), ("negativeEffects", "tab_negative_effects")]:
            frame = ttk.Frame(eff_notebook)
            eff_notebook.add(frame, text=_(title_key))
            
            # Canvas с прокруткой - заполняет всё доступное пространство
            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            inner = ttk.Frame(canvas)
            
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Чекбоксы эффектов в 2 колонки с описаниями
            for row, effect_key in enumerate(DEFAULT_EFFECT_KEYS):
                var = tk.BooleanVar()
                desc = EFFECT_DESCRIPTIONS.get(effect_key, effect_key)
                cb = ttk.Checkbutton(inner, text=f"{effect_key} - {desc}", variable=var)
                cb.grid(row=row//2, column=row%2, sticky="w", padx=5, pady=2)
                effect_checkboxes[eff_type][effect_key] = var
            
            # Кнопки выбрать все/снять все
            btn_f = ttk.Frame(frame)
            btn_f.pack(fill="x", pady=(5,0))
            ttk.Button(btn_f, text=_("bulk_select_effects_all"), 
                       command=lambda t=eff_type: [v.set(True) for v in effect_checkboxes[t].values()]).pack(side="left", padx=5)
            ttk.Button(btn_f, text=_("bulk_select_effects_none"), 
                       command=lambda t=eff_type: [v.set(False) for v in effect_checkboxes[t].values()]).pack(side="left", padx=5)
        
        # === БЛОК 3: Диапазоны значений ===
        range_frame = ttk.LabelFrame(win, text=_("bulk_step_3"), padding=10)
        range_frame.pack(fill="x", padx=10, pady=5)
        
        range_entries = {}
        for eff_type, label_key in [("positiveEffects", "bulk_range_positive"), ("negativeEffects", "bulk_range_negative")]:
            frm = ttk.Frame(range_frame)
            frm.pack(fill="x", pady=2)
            ttk.Label(frm, text=_(label_key), width=25, anchor="e").pack(side="left")
            
            min_entry = ttk.Entry(frm, width=10)
            min_entry.insert(0, "-10.0")
            min_entry.pack(side="left", padx=5)
            
            ttk.Label(frm, text=_("bulk_range_to")).pack(side="left", padx=5)
            
            max_entry = ttk.Entry(frm, width=10)
            max_entry.insert(0, "10.0")
            max_entry.pack(side="left", padx=5)
            
            range_entries[eff_type] = {"min": min_entry, "max": max_entry}
        
        # === БЛОК 4: Дополнительные опции ===
        opt_frame = ttk.LabelFrame(win, text=_("bulk_step_4"), padding=10)
        opt_frame.pack(fill="x", padx=10, pady=5)
        
        skip_zero_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text=_("bulk_opt_skip_zero"), 
                        variable=skip_zero_var).pack(anchor="w")
        
        overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text=_("bulk_opt_overwrite"), 
                        variable=overwrite_var).pack(anchor="w")
        
        # Опция заполнения из CSV описания для всех выбранных артефактов
        csv_fill_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt_frame, text=_("bulk_opt_csv_fill"), 
                        variable=csv_fill_var).pack(anchor="w")
        
        # === КНОПКИ ДЕЙСТВИЯ ===
        action_frame = ttk.Frame(win)
        action_frame.pack(fill="x", padx=10, pady=15)
        
        def apply_bulk():
            # Если включена опция заполнения из CSV
            if csv_fill_var.get():
                self._apply_csv_to_bulk(art_checkboxes, win=win)
                return
            
            # Сбор выбранных артефактов
            selected_indices = [i for i, var in art_checkboxes.items() if var.get()]
            if not selected_indices:
                messagebox.showwarning(_("warning_select_bulk_artifact"), _("warning_select_bulk_artifact"))
                return
            
            # Сбор выбранных эффектов
            selected_effects = {"positiveEffects": [], "negativeEffects": []}
            for eff_type in ["positiveEffects", "negativeEffects"]:
                for eff_key, var in effect_checkboxes[eff_type].items():
                    if var.get():
                        selected_effects[eff_type].append(eff_key)
            
            if not any(selected_effects.values()):
                messagebox.showwarning(_("warning_select_bulk_effect"), _("warning_select_bulk_effect"))
                return
            
            # Парсинг диапазонов
            try:
                ranges = {}
                for eff_type in ["positiveEffects", "negativeEffects"]:
                    min_val = float(range_entries[eff_type]["min"].get().strip())
                    max_val = float(range_entries[eff_type]["max"].get().strip())
                    if min_val > max_val:
                        raise ValueError(_("error_min_max").format(section=eff_type))
                    ranges[eff_type] = (min_val, max_val)
            except ValueError as e:
                messagebox.showerror(_("error_validation_title"), f"{_('error_invalid_range').format(error=str(e))}")
                return
            
            # Применение изменений
            modified_count = 0
            for idx in selected_indices:
                art = self.main_data["artifacts"][idx]
                
                for eff_type in ["positiveEffects", "negativeEffects"]:
                    if eff_type not in art:
                        art[eff_type] = make_template_dict(0.0)
                    
                    for eff_key in selected_effects[eff_type]:
                        # Проверка: перезаписывать или только пустые
                        current_val = art[eff_type].get(eff_key, 0.0)
                        if not overwrite_var.get() and current_val != 0.0:
                            continue
                        
                        # Генерация случайного значения
                        min_v, max_v = ranges[eff_type]
                        random_val = round(random.uniform(min_v, max_v), 2)
                        
                        # Пропуск нуля если опция включена
                        if skip_zero_var.get() and random_val == 0.0:
                            continue
                        
                        art[eff_type][eff_key] = random_val
                        modified_count += 1
                
                # Обновляем combined effects
                combined_effects = make_template_dict(0.0)
                for k in DEFAULT_EFFECT_KEYS:
                    pos_val = art.get("positiveEffects", {}).get(k, 0.0)
                    neg_val = art.get("negativeEffects", {}).get(k, 0.0)
                    combined_effects[k] = pos_val + neg_val
                art["effects"] = combined_effects
            
            self.refresh_tree()
            messagebox.showinfo(_("success_bulk_title"), _("success_bulk_message").format(
                modified=modified_count,
                artifacts=len(selected_indices)
            ))
            win.destroy()
        
        ttk.Button(action_frame, text=_("bulk_btn_apply"), command=apply_bulk).pack(side="right", padx=5)
        ttk.Button(action_frame, text=_("bulk_btn_cancel"), command=win.destroy).pack(side="right", padx=5)

    def _apply_csv_to_bulk(self, art_checkboxes, win):
        """
        Массовое заполнение эффектов из CSV файла для выбранных артефактов.
        
        Args:
            art_checkboxes: Словарь {index: BooleanVar} с выбранными артефактами
            win: Окно массового редактора
        """
        # Выбор CSV файла
        csv_path = filedialog.askopenfilename(
            title=_("csv_select_title"),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.file_path) if self.file_path else "."
        )
        
        if not csv_path:
            return
        
        selected_indices = [i for i, var in art_checkboxes.items() if var.get()]
        if not selected_indices:
            messagebox.showwarning(_("warning_select_bulk_artifact"), _("warning_select_bulk_artifact"))
            return
        
        try:
            # Читаем CSV файл и строим словарь {classname: description}
            csv_data = {}
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=",")
                
                # Ищем колонки
                classname_col = None
                desc_col = None
                
                if reader.fieldnames:
                    for col in reader.fieldnames:
                        col_lower = col.lower().strip()
                        if "класснейм" in col_lower or "class" in col_lower or "key" in col_lower:
                            classname_col = col
                        if "описание" in col_lower or "desc" in col_lower:
                            desc_col = col
                    
                    if not classname_col or not desc_col:
                        if len(reader.fieldnames) >= 2:
                            classname_col = reader.fieldnames[0]
                            desc_col = reader.fieldnames[1]
                        else:
                            raise ValueError(_("csv_error_no_columns"))
                    
                    # Загружаем данные
                    for row in reader:
                        cn = row.get(classname_col, "").strip()
                        desc = row.get(desc_col, "")
                        if cn:
                            csv_data[cn] = desc
            
            if not csv_data:
                messagebox.showerror(_("error_csv_empty"), _("error_csv_empty"))
                return
            
            # Обрабатываем выбранные артефакты
            total_modified = 0
            total_artifacts = 0
            
            for idx in selected_indices:
                art = self.main_data["artifacts"][idx]
                class_name = art.get("className", "")
                
                if class_name not in csv_data:
                    continue
                
                description_text = csv_data[class_name]
                found_effects = self._parse_description_to_effects(description_text)
                
                if not found_effects:
                    continue
                
                total_artifacts += 1
                
                # Применяем найденные эффекты (только к пустым полям)
                for eff_type in ["positiveEffects", "negativeEffects"]:
                    if eff_type not in art:
                        art[eff_type] = make_template_dict(0.0)
                    
                    for eff_key, value in found_effects.items():
                        current_val = art[eff_type].get(eff_key, 0.0)
                        if current_val == 0.0:
                            art[eff_type][eff_key] = value
                            total_modified += 1
                
                # Обновляем combined effects
                combined_effects = make_template_dict(0.0)
                for k in DEFAULT_EFFECT_KEYS:
                    pos_val = art.get("positiveEffects", {}).get(k, 0.0)
                    neg_val = art.get("negativeEffects", {}).get(k, 0.0)
                    combined_effects[k] = pos_val + neg_val
                art["effects"] = combined_effects
            
            self.refresh_tree()
            
            messagebox.showinfo(_("success_bulk_csv_title"), _("success_bulk_csv_message").format(
                modified=total_modified,
                artifacts=total_artifacts
            ))
            
            win.destroy()
            
        except Exception as e:
            messagebox.showerror(_("error_csv_parse"), str(e))

if __name__ == "__main__":
    root = tk.Tk()
    
    # Настройка иконки (если есть)
    try:
        root.iconbitmap(default="")  # Можно добавить свою иконку
    except:
        pass
    
    app = ArtifactManagerApp(root)
    root.mainloop()