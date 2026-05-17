import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import copy
import re
import csv
import random

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

# Словарь ключевых слов для каждого эффекта (русский и английский)
EFFECT_KEYWORDS = {
    "health": ["здоровье", "health", "жизнь", "hp", "восстанавливает здоровье", "лечит"],
    "blood": ["кровь", "blood", "кровопотеря", "bleed"],
    "shock": ["шок", "shock", "болевой шок"],
    "water": ["вода", "water", "жажда", "гидратация", "пить"],
    "energy": ["энергия", "energy", "калории", "еда"],
    "stamina": ["выносливость", "stamina", "усталость", "энергия бег"],
    "sleeping": ["сон", "sleep", "усталость сон", "бессонница"],
    "mind": ["рассудок", "mind", " sanity", "психика", "интеллект"],
    "pain": ["боль", "pain", "обезбол", "анальгетик"],
    "contusion": ["контузия", "contusion", "травма голова"],
    "hematomas": ["гематома", "hematoma", "синяк", "кровоподтек"],
    "lightBleeding": ["лёгкое кровотечение", "легкое кровотечение", "light bleeding", "минимальное кровотечение"],
    "heavyBleeding": ["сильное кровотечение", "heavy bleeding", "обильное кровотечение", "серьезное кровотечение"],
    "bulletWounds": ["пулевое ранение", "bullet wound", "пуля", "огнестрел"],
    "viscera": ["внутренности", "viscera", "органы", "желудок", "кишечник"],
    "sepsis": ["сепсис", "sepsis", "заражение кровь", "инфекция кровь"],
    "zombieVirus": ["вирус зомби", "zombie virus", "инфекция зомби", "вирусная инфекция"],
    "influenza": ["грипп", "influenza", "простуда", "болезнь респиратор"],
    "poison": ["отравление", "poison", "токсин", "яд"],
    "biohazard": ["биоугроза", "biohazard", "биологическая опасность", "радиационное заражение"],
    "rabies": ["бешенство", "rabies", "вирус бешенства"],
    "overdose": ["передозировка", "overdose", "наркотический"],
    "immunity": ["иммунитет", "immunity", "сопротивляемость", "защита болезнь"],
    "radiation": ["радиация", "radiation", "радиоактивный", "излучение"],
    "temperature": ["температура", "temperature", "тепло", "холод", "жара"],
    "brokenLeg": ["сломанная нога", "broken leg", "перелом ноги", "травма ноги"],
    "jumpHeight": ["прыжок", "jump", "высота прыжка", "прыгучесть"],
    "meleeDamage": ["урон ближнего боя", "melee damage", "ближний бой", "атака рукопашная"]
}

# Слова указывающие на положительный эффект
POSITIVE_WORDS = [
    "увелич", "повыш", "улучш", "восстанавлив", "леч", "защ", 
    "усил", "boost", "increase", "restore", "heal", "protect",
    "снижа", "уменьш", "предотвращ", "block", "reduce", "prevent",
    "抵抗", "сопротивл"
]

# Слова указывающие на отрицательный эффект
NEGATIVE_WORDS = [
    "уменьш", "сниж", "ухудш", "поврежд", "травм", "разруш",
    "decrease", "damage", "worsen", "harm", "destroy",
    "вызыв", "причин", "опасн", "cause", "danger"
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

def parse_description_to_effects(description_text):
    """
    Парсит лорное описание артефакта и извлекает значения эффектов.
    Возвращает словарь с найденными эффектами для positiveEffects и negativeEffects.
    """
    if not description_text:
        return {"positiveEffects": {}, "negativeEffects": {}}
    
    text_lower = description_text.lower()
    result = {"positiveEffects": {}, "negativeEffects": {}}
    
    # Находим все числа в тексте (включая отрицательные и дробные)
    numbers = re.findall(r'[-+]?\d*\.?\d+', text_lower)
    
    for effect_key, keywords in EFFECT_KEYWORDS.items():
        found_value = None
        is_positive = None
        
        # Ищем ключевые слова эффекта в тексте
        for keyword in keywords:
            if keyword in text_lower:
                # Определяем контекст (позитивный или негативный эффект)
                context_start = max(0, text_lower.find(keyword) - 50)
                context_end = min(len(text_lower), text_lower.find(keyword) + 100)
                context = text_lower[context_start:context_end]
                
                # Проверяем на позитивность
                for pos_word in POSITIVE_WORDS:
                    if pos_word in context:
                        is_positive = True
                        break
                
                # Проверяем на негативность
                if is_positive is None:
                    for neg_word in NEGATIVE_WORDS:
                        if neg_word in context:
                            is_positive = False
                            break
                
                # Если не определили по контексту, пытаемся определить по смыслу эффекта
                if is_positive is None:
                    # По умолчанию считаем некоторые эффекты позитивными
                    if effect_key in ["health", "blood", "energy", "stamina", "immunity", "radiation"]:
                        # Нужно проверить контекст лучше
                        if any(word in context for word in ["повыш", "увелич", "восстанавлив", "защ"]):
                            is_positive = True
                        elif any(word in context for word in ["сниж", "уменьш", "ухудш", "потер"]):
                            is_positive = False
                        else:
                            # По умолчанию - позитивно если это восстановление
                            is_positive = True
                    else:
                        # Для негативных эффектов по умолчанию
                        is_positive = False
                
                # Пытаемся найти число рядом с ключевым словом
                keyword_pos = text_lower.find(keyword)
                # Ищем число в радиусе 30 символов от ключевого слова
                search_start = max(0, keyword_pos - 30)
                search_end = min(len(text_lower), keyword_pos + len(keyword) + 30)
                search_area = text_lower[search_start:search_end]
                
                nearby_numbers = re.findall(r'[-+]?\d*\.?\d+', search_area)
                if nearby_numbers:
                    # Берём первое найденное число
                    try:
                        found_value = float(nearby_numbers[0])
                    except ValueError:
                        pass
                break
        
        # Если нашли значение, добавляем в результат
        if found_value is not None and is_positive is not None:
            target_dict = result["positiveEffects"] if is_positive else result["negativeEffects"]
            target_dict[effect_key] = found_value
    
    return result


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
        ttk.Separator(btn_frame, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(btn_frame, text="🎲 Массовая настройка", command=self.open_mass_editor).pack(side="left", padx=2)

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
        
        # Кнопка для заполнения из описания CSV
        btn_frame_top = ttk.Frame(win)
        btn_frame_top.pack(fill="x", padx=15, pady=5)
        
        def fill_from_csv_description():
            """Заполняет эффекты на основе описания из CSV файла"""
            class_name = forms["className"].get().strip()
            if not class_name:
                messagebox.showwarning("Предупреждение", "Сначала введите класснейм артефакта")
                return
            
            # Ищем CSV файл с описаниями
            csv_files = [
                os.path.join(os.path.dirname(self.file_path) if self.file_path else ".", "Арты (Шаблон) .csv"),
                os.path.join(os.getcwd(), "Арты (Шаблон) .csv"),
            ]
            
            csv_path = None
            for path in csv_files:
                if os.path.exists(path):
                    csv_path = path
                    break
            
            if not csv_path:
                csv_path = filedialog.askopenfilename(
                    title="Выберите CSV файл с описаниями артефактов",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
            
            if not csv_path:
                return
            
            try:
                # Читаем CSV файл
                description_text = None
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Ищем по класснейму
                        key_col = None
                        desc_col = None
                        for col_name in reader.fieldnames:
                            if 'класснейм' in col_name.lower() or 'key' in col_name.lower():
                                key_col = col_name
                            if 'описание' in col_name.lower() or 'desc' in col_name.lower():
                                desc_col = col_name
                        
                        if key_col and desc_col:
                            if row.get(key_col, '').strip() == class_name:
                                description_text = row.get(desc_col, '')
                                break
                
                if not description_text:
                    messagebox.showinfo("Результат", f"Описание для '{class_name}' не найдено в CSV файле")
                    return
                
                # Парсим описание
                parsed_effects = parse_description_to_effects(description_text)
                
                if not parsed_effects["positiveEffects"] and not parsed_effects["negativeEffects"]:
                    messagebox.showinfo("Результат", "Не удалось извлечь эффекты из описания. Возможно, описание не содержит числовых значений или ключевых слов.")
                    return
                
                # Заполняем поля эффектов
                filled_count = 0
                for eff_key, value in parsed_effects["positiveEffects"].items():
                    if eff_key in eff_entries["positiveEffects"]:
                        current_val = eff_entries["positiveEffects"][eff_key].get().strip()
                        if current_val == "0" or current_val == "0.0" or current_val == "":
                            eff_entries["positiveEffects"][eff_key].delete(0, tk.END)
                            eff_entries["positiveEffects"][eff_key].insert(0, str(value))
                            filled_count += 1
                
                for eff_key, value in parsed_effects["negativeEffects"].items():
                    if eff_key in eff_entries["negativeEffects"]:
                        current_val = eff_entries["negativeEffects"][eff_key].get().strip()
                        if current_val == "0" or current_val == "0.0" or current_val == "":
                            eff_entries["negativeEffects"][eff_key].delete(0, tk.END)
                            eff_entries["negativeEffects"][eff_key].insert(0, str(value))
                            filled_count += 1
                
                messagebox.showinfo(
                    "Успех", 
                    f"Найдено эффектов из описания:\n"
                    f"✅ Позитивных: {len(parsed_effects['positiveEffects'])}\n"
                    f"❌ Негативных: {len(parsed_effects['negativeEffects'])}\n"
                    f"📝 Заполнено полей: {filled_count}\n\n"
                    f"Текст описания:\n{description_text[:200]}..." if len(description_text) > 200 else f"\n{description_text}"
                )
                
            except Exception as e:
                messagebox.showerror("Ошибка при чтении CSV", f"Не удалось обработать CSV файл:\n{str(e)}")
        
        ttk.Button(btn_frame_top, text="📖 Заполнить из описания (CSV)", command=fill_from_csv_description).pack(side="left", padx=5)
        ttk.Label(btn_frame_top, text="(заполняет только пустые поля)").pack(side="left", padx=5)
            
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
    
    def open_mass_editor(self):
        """Открывает окно массовой настройки артефактов с рандомизацией и заполнением из описания"""
        if not self.main_data["artifacts"]:
            messagebox.showinfo("Внимание", "Сначала загрузите файл с артефактами")
            return
        
        win = tk.Toplevel(self.root)
        win.title("🎲 Массовая настройка артефактов")
        win.geometry("1200x850")
        win.minsize(1000, 750)
        
        # Блок 1: Выбор артефактов
        art_frame = ttk.LabelFrame(win, text="1️⃣ Выберите артефакты для обработки", padding=10)
        art_frame.pack(fill="x", padx=10, pady=5)
        
        # Список с прокруткой
        art_canvas = tk.Canvas(art_frame, height=150, highlightthickness=0)
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
            cb = ttk.Checkbutton(art_inner, text=f"{art.get('className', '???')} (#{i+1})", variable=var)
            cb.grid(row=i//2, column=i%2, sticky="w", padx=5, pady=2)
            art_checkboxes[i] = var
        
        # Кнопки выбора
        sel_btn_frame = ttk.Frame(art_frame)
        sel_btn_frame.grid(row=(len(art_checkboxes)//2)+1, column=0, columnspan=2, pady=5)
        ttk.Button(sel_btn_frame, text="✅ Выбрать все", command=lambda: [v.set(True) for v in art_checkboxes.values()]).pack(side="left", padx=5)
        ttk.Button(sel_btn_frame, text="❌ Снять все", command=lambda: [v.set(False) for v in art_checkboxes.values()]).pack(side="left", padx=5)
        
        # Блок 2: Режим работы
        mode_frame = ttk.LabelFrame(win, text="2️⃣ Режим работы", padding=10)
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        mode_var = tk.StringVar(value="fill_from_csv")
        ttk.Radiobutton(mode_frame, text="📖 Заполнить из описания CSV (только пустые поля)", variable=mode_var, value="fill_from_csv").pack(anchor="w", padx=10, pady=2)
        ttk.Label(mode_frame, text="   → Автоматически извлечёт эффекты из описания в файле «Арты (Шаблон) .csv»", foreground="gray").pack(anchor="w", padx=30)
        
        ttk.Radiobutton(mode_frame, text="🎲 Сгенерировать случайные значения", variable=mode_var, value="random_gen").pack(anchor="w", padx=10, pady=2)
        
        # Блок 3: Настройка эффектов (для режима рандома)
        rand_frame = ttk.LabelFrame(win, text="3️⃣ Параметры генерации случайных значений", padding=10)
        rand_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Вкладки эффектов
        rand_notebook = ttk.Notebook(rand_frame)
        rand_notebook.pack(fill="both", expand=True)
        
        rand_entries = {"positiveEffects": {}, "negativeEffects": {}}
        
        for eff_type, title in [("positiveEffects", "✅ Позитивные эффекты"), ("negativeEffects", "❌ Негативные эффекты")]:
            frame = ttk.Frame(rand_notebook)
            rand_notebook.add(frame, text=title)
            
            canvas = tk.Canvas(frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            inner = ttk.Frame(canvas)
            inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Заголовки
            ttk.Label(inner, text="Эффект", font=("Arial", 10, "bold"), width=20).grid(row=0, column=0, padx=5, pady=5)
            ttk.Label(inner, text="Включить", font=("Arial", 10, "bold"), width=10).grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(inner, text="Мин", font=("Arial", 10, "bold"), width=10).grid(row=0, column=2, padx=5, pady=5)
            ttk.Label(inner, text="Макс", font=("Arial", 10, "bold"), width=10).grid(row=0, column=3, padx=5, pady=5)
            ttk.Label(inner, text="Описание", font=("Arial", 10, "bold"), width=40).grid(row=0, column=4, padx=5, pady=5)
            
            effect_desc = {
                "health": "Здоровье", "blood": "Кровь", "shock": "Шок",
                "water": "Вода", "energy": "Энергия", "stamina": "Выносливость",
                "sleeping": "Сон", "mind": "Рассудок", "pain": "Боль",
                "contusion": "Контузия", "hematomas": "Гематомы",
                "lightBleeding": "Лёгкое кровотечение", "heavyBleeding": "Сильное кровотечение",
                "bulletWounds": "Пулевые ранения", "viscera": "Внутренности",
                "sepsis": "Сепсис", "zombieVirus": "Вирус зомби", "influenza": "Грипп",
                "poison": "Отравление", "biohazard": "Биоугроза", "rabies": "Бешенство",
                "overdose": "Передозировка", "immunity": "Иммунитет",
                "radiation": "Радиация", "temperature": "Температура",
                "brokenLeg": "Сломанная нога", "jumpHeight": "Высота прыжка",
                "meleeDamage": "Урон ближнего боя"
            }
            
            for row, key in enumerate(DEFAULT_EFFECT_KEYS, start=1):
                enabled_var = tk.BooleanVar(value=False)
                min_entry = ttk.Entry(inner, width=10)
                max_entry = ttk.Entry(inner, width=10)
                
                # Значения по умолчанию
                if eff_type == "positiveEffects":
                    min_entry.insert(0, "0.1")
                    max_entry.insert(0, "1.0")
                else:
                    min_entry.insert(0, "-1.0")
                    max_entry.insert(0, "-0.1")
                
                ttk.Checkbutton(inner, text=key, variable=enabled_var, width=18, anchor="w").grid(row=row, column=0, padx=5, pady=1, sticky="w")
                ttk.Checkbutton(inner, variable=enabled_var).grid(row=row, column=1, padx=5, pady=1)
                min_entry.grid(row=row, column=2, padx=5, pady=1)
                max_entry.grid(row=row, column=3, padx=5, pady=1)
                ttk.Label(inner, text=effect_desc.get(key, ""), width=35, foreground="gray").grid(row=row, column=4, padx=5, pady=1, sticky="w")
                
                rand_entries[eff_type][key] = {"enabled": enabled_var, "min": min_entry, "max": max_entry}
        
        # Опции
        opt_frame = ttk.Frame(rand_frame)
        opt_frame.pack(fill="x", padx=5, pady=10)
        
        skip_zero_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_frame, text="⏭️ Пропускать нулевые значения (не перезаписывать существующие)", variable=skip_zero_var).pack(anchor="w", padx=10, pady=2)
        
        # Кнопки действий
        action_frame = ttk.Frame(win)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        def apply_mass_action():
            selected_indices = [i for i, var in art_checkboxes.items() if var.get()]
            
            if not selected_indices:
                messagebox.showwarning("Внимание", "Выберите хотя бы один артефакт")
                return
            
            mode = mode_var.get()
            updated_count = 0
            
            try:
                if mode == "fill_from_csv":
                    # Заполнение из CSV описания
                    csv_path = None
                    possible_paths = [
                        os.path.join(os.path.dirname(self.file_path) if self.file_path else ".", "Арты (Шаблон) .csv"),
                        os.path.join(os.getcwd(), "Арты (Шаблон) .csv"),
                    ]
                    for p in possible_paths:
                        if os.path.exists(p):
                            csv_path = p
                            break
                    
                    if not csv_path:
                        csv_path = filedialog.askopenfilename(
                            title="Выберите CSV файл с описаниями",
                            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                        )
                    
                    if not csv_path:
                        return
                    
                    # Читаем CSV
                    descriptions = {}
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            key_col = next((c for c in reader.fieldnames if 'класснейм' in c.lower() or 'key' in c.lower()), None)
                            desc_col = next((c for c in reader.fieldnames if 'описание' in c.lower() or 'desc' in c.lower()), None)
                            
                            if key_col and desc_col:
                                descriptions[row.get(key_col, '').strip()] = row.get(desc_col, '')
                    
                    # Обрабатываем выбранные артефакты
                    for idx in selected_indices:
                        art = self.main_data["artifacts"][idx]
                        class_name = art.get("className", "")
                        
                        if class_name not in descriptions:
                            continue
                        
                        parsed = parse_description_to_effects(descriptions[class_name])
                        
                        # Применяем только к пустым полям
                        for eff_type in ["positiveEffects", "negativeEffects"]:
                            for key, value in parsed.get(eff_type, {}).items():
                                current = art.get(eff_type, {}).get(key, 0.0)
                                if current == 0.0 or current == 0:
                                    if eff_type not in art:
                                        art[eff_type] = make_template_dict(0.0)
                                    art[eff_type][key] = value
                                    updated_count += 1
                
                elif mode == "random_gen":
                    # Генерация случайных значений
                    ranges = {}
                    for eff_type in ["positiveEffects", "negativeEffects"]:
                        ranges[eff_type] = {}
                        for key, widgets in rand_entries[eff_type].items():
                            if widgets["enabled"].get():
                                try:
                                    min_val = float(widgets["min"].get())
                                    max_val = float(widgets["max"].get())
                                    if min_val > max_val:
                                        raise ValueError("Мин больше макс")
                                    ranges[eff_type][key] = (min_val, max_val)
                                except ValueError:
                                    messagebox.showerror("Ошибка", f"Неверный диапазон для {key}: {widgets['min'].get()} - {widgets['max'].get()}")
                                    return
                    
                    if not any(ranges.values()):
                        messagebox.showwarning("Внимание", "Выберите хотя бы один эффект для генерации")
                        return
                    
                    # Применяем к артефактам
                    for idx in selected_indices:
                        art = self.main_data["artifacts"][idx]
                        
                        for eff_type in ["positiveEffects", "negativeEffects"]:
                            if eff_type not in art:
                                art[eff_type] = make_template_dict(0.0)
                            
                            for key, (min_v, max_v) in ranges.get(eff_type, {}).items():
                                if skip_zero_var.get():
                                    current = art.get(eff_type, {}).get(key, 0.0)
                                    if current != 0.0 and current != 0:
                                        continue
                                
                                # Генерируем случайное значение
                                value = round(random.uniform(min_v, max_v), 2)
                                art[eff_type][key] = value
                                updated_count += 1
                
                # Обновляем combined effects
                for idx in selected_indices:
                    art = self.main_data["artifacts"][idx]
                    combined = make_template_dict(0.0)
                    for k in DEFAULT_EFFECT_KEYS:
                        pos = art.get("positiveEffects", {}).get(k, 0.0)
                        neg = art.get("negativeEffects", {}).get(k, 0.0)
                        combined[k] = pos + neg
                    art["effects"] = combined
                
                self.refresh_tree()
                messagebox.showinfo("Успех", f"Обработано артефактов: {len(selected_indices)}\nИзменено полей: {updated_count}\n\nНе забудьте сохранить файл! 💾")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка при обработке:\n{str(e)}")
        
        ttk.Button(action_frame, text="🚀 Применить ко всем выбранным", command=apply_mass_action, style="Accent.TButton").pack(side="right", padx=5)
        ttk.Button(action_frame, text="❌ Отмена", command=win.destroy).pack(side="right", padx=5)


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