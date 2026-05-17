#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DayZ MODtypes Generator with GUI
Утилита для создания модульных файлов типов предметов для DayZ Standalone сервера.
Работает в паре с cfgeconomycore.xml для разделения ванильных и модовых предметов.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import csv


class DayZItem:
    """Класс представляющий предмет DayZ"""
    
    def __init__(self, name: str):
        self.name = name
        self.nominal = 0
        self.min = 0
        self.quantmin = 0
        self.quantmax = 0
        self.max = 0
        self.restock_min = 0
        self.restock_max = 0
        self.category_main = "weapons"
        self.category_sub = ""
        self.usage_flags = []
        self.tag = ""
        self.flags = []
        
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "nominal": self.nominal,
            "min": self.min,
            "quantmin": self.quantmin,
            "quantmax": self.quantmax,
            "max": self.max,
            "restock_min": self.restock_min,
            "restock_max": self.restock_max,
            "category_main": self.category_main,
            "category_sub": self.category_sub,
            "usage_flags": self.usage_flags,
            "tag": self.tag,
            "flags": self.flags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DayZItem':
        item = cls(data["name"])
        item.nominal = data.get("nominal", 0)
        item.min = data.get("min", 0)
        item.quantmin = data.get("quantmin", 0)
        item.quantmax = data.get("quantmax", 0)
        item.max = data.get("max", 0)
        item.restock_min = data.get("restock_min", 0)
        item.restock_max = data.get("restock_max", 0)
        item.category_main = data.get("category_main", "weapons")
        item.category_sub = data.get("category_sub", "")
        item.usage_flags = data.get("usage_flags", [])
        item.tag = data.get("tag", "")
        item.flags = data.get("flags", [])
        return item
    
    def guess_category(self):
        """Автоматическое определение категории по имени предмета"""
        name_lower = self.name.lower()
        
        # Оружие
        if any(w in name_lower for w in ["rifle", "pistol", "shotgun", "sniper", "ammo", "magazine"]):
            self.category_main = "weapons"
            self.category_sub = "rifles" if "rifle" in name_lower else "pistols" if "pistol" in name_lower else "ammo"
        # Еда
        elif any(w in name_lower for w in ["can", "food", "meat", "fish", "fruit", "vegetable", "bread", "cake"]):
            self.category_main = "food"
            self.category_sub = "cookedfood" if "cook" in name_lower or "can" in name_lower else "rawfood"
        # Напитки
        elif any(w in name_lower for w in ["bottle", "can", "water", "soda", "juice", "beer", "vodka"]):
            self.category_main = "food"
            self.category_sub = "drink"
        # Одежда
        elif any(w in name_lower for w in ["shirt", "pants", "jacket", "coat", "hat", "boots", "shoes", "gloves"]):
            self.category_main = "clothes"
            self.category_sub = "headgear" if "hat" in name_lower or "cap" in name_lower else "footwear" if "boot" in name_lower or "shoe" in name_lower else "tops"
        # Инструменты
        elif any(w in name_lower for w in ["axe", "hatchet", "shovel", "hammer", "knife", "tool", "wrench", "pliers"]):
            self.category_main = "tools"
            self.category_sub = "handtools"
        # Медицина
        elif any(w in name_lower for w in ["bandage", "epinephrine", "morphine", "antibiotic", "vitamin", "blood", "saline"]):
            self.category_main = "medic"
            self.category_sub = ""
        # Транспорт/части
        elif any(w in name_lower for w in ["wheel", "engine", "sparkplug", "battery", "car", "helicopter"]):
            self.category_main = "vehiclesparts"
            self.category_sub = ""
        # Строительство
        elif any(w in name_lower for w in ["fence", "gate", "wall", "lock", "basebuilding"]):
            self.category_main = "containers"
            self.category_sub = ""
        # Разное
        else:
            self.category_main = "misc"
            self.category_sub = ""
    
    def guess_tag(self):
        """Автоматическое определение тега по имени предмета"""
        name_lower = self.name.lower()
        
        if any(w in name_lower for w in ["weapon", "rifle", "pistol", "shotgun"]):
            self.tag = "shelves"
        elif any(w in name_lower for w in ["food", "can", "bread", "meat"]):
            self.tag = "shelves"
        elif any(w in name_lower for w in ["clothes", "shirt", "pants", "jacket"]):
            self.tag = "hangers"
        elif any(w in name_lower for w in ["tool", "axe", "shovel", "hammer"]):
            self.tag = "shelves"
        elif any(w in name_lower for w in ["medic", "bandage", "pill"]):
            self.tag = "shelves"
        else:
            self.tag = "floor"


class MissionConfig:
    """Конфигурация миссии DayZ"""
    
    def __init__(self):
        self.mission_path = ""
        self.mod_name = "CustomMod"
        self.custom_types_folder = "CustomTypes"
        self.items: List[DayZItem] = []
        
    def get_cfgeconomycore_path(self) -> str:
        return os.path.join(self.mission_path, "cfgeconomycore.xml")
    
    def get_custom_types_path(self) -> str:
        return os.path.join(self.mission_path, self.custom_types_folder)
    
    def get_mod_types_path(self) -> str:
        return os.path.join(self.get_custom_types_path(), f"{self.mod_name}_types.xml")


class DayZGeneratorApp:
    """Основное GUI приложение"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DayZ MODtypes Generator")
        self.root.geometry("900x700")
        
        self.config = MissionConfig()
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной контейнер с отступами
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        row = 0
        
        # === Секция 1: Путь к миссии ===
        path_frame = ttk.LabelFrame(main_frame, text="📁 Путь к миссии", padding="5")
        path_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_frame, text="Папка миссии:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Button(path_frame, text="Обзор...", command=self.browse_mission).grid(row=0, column=2, padx=5)
        
        row += 1
        
        # === Секция 2: Настройки мода ===
        mod_frame = ttk.LabelFrame(main_frame, text="⚙️ Настройки мода", padding="5")
        mod_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        mod_frame.columnconfigure(1, weight=1)
        
        ttk.Label(mod_frame, text="Название мода:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.mod_name_var = tk.StringVar(value="MyMod")
        ttk.Entry(mod_frame, textvariable=self.mod_name_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(mod_frame, text="Папка типов:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.folder_var = tk.StringVar(value="CustomTypes")
        ttk.Entry(mod_frame, textvariable=self.folder_var, width=20).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        
        # === Секция 3: Управление предметами ===
        items_frame = ttk.LabelFrame(main_frame, text="🎒 Предметы мода", padding="5")
        items_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(1, weight=1)
        
        # Кнопки управления
        btn_frame = ttk.Frame(items_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(btn_frame, text="➕ Добавить", command=self.add_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=self.edit_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Удалить", command=self.delete_item).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📥 Импорт JSON", command=self.import_json).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📤 Экспорт JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✨ Авто-заполнить", command=self.auto_guess).pack(side=tk.LEFT, padx=2)
        
        # Таблица предметов
        columns = ("name", "nominal", "min", "max", "category", "tag")
        self.tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("name", text="Название предмета")
        self.tree.heading("nominal", text="Nominal")
        self.tree.heading("min", text="Min")
        self.tree.heading("max", text="Max")
        self.tree.heading("category", text="Категория")
        self.tree.heading("tag", text="Тег")
        
        self.tree.column("name", width=200)
        self.tree.column("nominal", width=60)
        self.tree.column("min", width=60)
        self.tree.column("max", width=60)
        self.tree.column("category", width=120)
        self.tree.column("tag", width=80)
        
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        row += 1
        
        # === Секция 4: Лог операций ===
        log_frame = ttk.LabelFrame(main_frame, text="📋 Журнал операций", padding="5")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row += 1
        
        # === Секция 5: Кнопки генерации ===
        gen_frame = ttk.Frame(main_frame)
        gen_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(gen_frame, text="🔄 Обновить cfgeconomycore.xml", command=self.update_cfgeconomycore).pack(side=tk.LEFT, padx=5)
        ttk.Button(gen_frame, text="💾 Создать MODtypes.xml", command=self.generate_modtypes).pack(side=tk.LEFT, padx=5)
        ttk.Button(gen_frame, text="🚀 Выполнить всё", command=self.run_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(gen_frame, text="❌ Очистить список", command=self.clear_items).pack(side=tk.RIGHT, padx=5)
        
        # Привязка двойного клика для редактирования
        self.tree.bind("<Double-1>", lambda e: self.edit_item())
        
        self.log("Приложение готово к работе!")
        self.log("Выберите папку миссии и добавьте предметы.")
        
    def log(self, message: str):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
        self.log_text.see(tk.END)
        
    def get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
        
    def browse_mission(self):
        """Выбор папки миссии"""
        folder = filedialog.askdirectory(title="Выберите папку миссии (mpmissions/...)")
        if folder:
            self.path_var.set(folder)
            self.config.mission_path = folder
            self.log(f"Папка миссии выбрана: {folder}")
            
    def add_item(self):
        """Добавление нового предмета"""
        dialog = ItemDialog(self.root, "Добавить предмет")
        if dialog.result:
            item = DayZItem.from_dict(dialog.result)
            self.config.items.append(item)
            self.refresh_tree()
            self.log(f"Добавлен предмет: {item.name}")
            
    def edit_item(self):
        """Редактирование выбранного предмета"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите предмет для редактирования")
            return
            
        index = self.tree.index(selection[0])
        if 0 <= index < len(self.config.items):
            item = self.config.items[index]
            dialog = ItemDialog(self.root, "Редактировать предмет", item.to_dict())
            if dialog.result:
                self.config.items[index] = DayZItem.from_dict(dialog.result)
                self.refresh_tree()
                self.log(f"Обновлен предмет: {item.name}")
                
    def delete_item(self):
        """Удаление выбранного предмета"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите предмет для удаления")
            return
            
        index = self.tree.index(selection[0])
        if 0 <= index < len(self.config.items):
            item = self.config.items[index]
            if messagebox.askyesno("Подтверждение", f"Удалить предмет {item.name}?"):
                del self.config.items[index]
                self.refresh_tree()
                self.log(f"Удален предмет: {item.name}")
                
    def refresh_tree(self):
        """Обновление таблицы предметов"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for item in self.config.items:
            category = f"{item.category_main}" + (f"/{item.category_sub}" if item.category_sub else "")
            self.tree.insert("", tk.END, values=(
                item.name,
                item.nominal,
                item.min,
                item.max,
                category,
                item.tag
            ))
            
    def auto_guess(self):
        """Автозаполнение категорий и тегов"""
        for item in self.config.items:
            item.guess_category()
            item.guess_tag()
        self.refresh_tree()
        self.log("Выполнено автозаполнение категорий и тегов")
        
    def clear_items(self):
        """Очистка списка предметов"""
        if messagebox.askyesno("Подтверждение", "Очистить весь список предметов?"):
            self.config.items.clear()
            self.refresh_tree()
            self.log("Список предметов очищен")
            
    def import_json(self):
        """Импорт предметов из JSON файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    count = 0
                    for item_data in data:
                        if "name" in item_data:
                            item = DayZItem.from_dict(item_data)
                            self.config.items.append(item)
                            count += 1
                            
                    self.refresh_tree()
                    self.log(f"Импортировано {count} предметов из {file_path}")
                else:
                    messagebox.showerror("Ошибка", "Неверный формат JSON. Ожидается список предметов.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при импорте: {str(e)}")
                
    def export_json(self):
        """Экспорт предметов в JSON файл"""
        if not self.config.items:
            messagebox.showwarning("Внимание", "Список предметов пуст")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить JSON файл",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                data = [item.to_dict() for item in self.config.items]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.log(f"Экспортировано {len(data)} предметов в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
                
    def update_cfgeconomycore(self):
        """Обновление или создание cfgeconomycore.xml"""
        if not self.config.mission_path:
            messagebox.showerror("Ошибка", "Сначала выберите папку миссии")
            return
            
        try:
            cfg_path = self.config.get_cfgeconomycore_path()
            
            # Создаем папку CustomTypes если не существует
            custom_types_path = self.config.get_custom_types_path()
            os.makedirs(custom_types_path, exist_ok=True)
            self.log(f"Папка типов создана/проверена: {custom_types_path}")
            
            # Проверяем существующий файл
            if os.path.exists(cfg_path):
                tree = ET.parse(cfg_path)
                root = tree.getroot()
            else:
                # Создаем новый файл с базовой структурой
                root = ET.Element("economycore")
                tree = ET.ElementTree(root)
                
            # Ищем или создаем наш ce блок
            ce_block = None
            for ce in root.findall("ce"):
                if ce.get("folder") == self.config.custom_types_folder:
                    ce_block = ce
                    break
                    
            if ce_block is None:
                ce_block = ET.SubElement(root, "ce")
                ce_block.set("folder", self.config.custom_types_folder)
                
            # Проверяем наличие нашего файла types
            file_exists = False
            target_filename = f"{self.config.mod_name}_types.xml"
            
            for file_elem in ce_block.findall("file"):
                if file_elem.get("name") == target_filename and file_elem.get("type") == "types":
                    file_exists = True
                    break
                    
            if not file_exists:
                file_elem = ET.SubElement(ce_block, "file")
                file_elem.set("name", target_filename)
                file_elem.set("type", "types")
                self.log(f"Добавлена ссылка на {target_filename} в cfgeconomycore.xml")
            else:
                self.log(f"Ссылка на {target_filename} уже существует в cfgeconomycore.xml")
                
            # Сохраняем файл с красивым форматированием
            self.save_xml_pretty(cfg_path, tree)
            self.log(f"cfgeconomycore.xml обновлен: {cfg_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении cfgeconomycore.xml: {str(e)}")
            self.log(f"ОШИБКА: {str(e)}")
            
    def generate_modtypes(self):
        """Генерация MODtypes.xml файла"""
        if not self.config.mission_path:
            messagebox.showerror("Ошибка", "Сначала выберите папку миссии")
            return
            
        if not self.config.items:
            messagebox.showwarning("Внимание", "Список предметов пуст. Добавьте предметы перед генерацией.")
            return
            
        try:
            # Создаем структуру XML
            root = ET.Element("types")
            root.set("version", "111")
            
            # Добавляем каждый предмет
            for item in self.config.items:
                type_elem = ET.SubElement(root, "type")
                type_elem.set("name", item.name)
                
                flags_elem = ET.SubElement(type_elem, "flags")
                
                # Nominal
                nominal = ET.SubElement(flags_elem, "nominal")
                nominal.set("min", str(item.nominal))
                
                # Min
                min_elem = ET.SubElement(flags_elem, "min")
                min_elem.set("min", str(item.min))
                
                # Quantmin
                quantmin = ET.SubElement(flags_elem, "quantmin")
                quantmin.set("min", str(item.quantmin))
                
                # Quantmax
                quantmax = ET.SubElement(flags_elem, "quantmax")
                quantmax.set("min", str(item.quantmax))
                
                # Max
                max_elem = ET.SubElement(flags_elem, "max")
                max_elem.set("min", str(item.max))
                
                # Restock
                restock = ET.SubElement(flags_elem, "restock")
                restock.set("min", str(item.restock_min))
                restock.set("max", str(item.restock_max))
                
                # Category
                category = ET.SubElement(flags_elem, "category")
                category.set("main", item.category_main)
                if item.category_sub:
                    category.set("sub", item.category_sub)
                    
                # Usage flags
                if item.usage_flags:
                    usage = ET.SubElement(flags_elem, "usageflags")
                    for flag in item.usage_flags:
                        usage_elem = ET.SubElement(usage, "usage")
                        usage_elem.set("flag", flag)
                        
                # Tag
                if item.tag:
                    tag_elem = ET.SubElement(flags_elem, "tag")
                    tag_elem.set("name", item.tag)
                    
            # Сохраняем файл
            output_path = self.config.get_mod_types_path()
            self.save_xml_pretty(output_path, ET.ElementTree(root))
            
            self.log(f"✅ MODtypes.xml создан: {output_path}")
            messagebox.showinfo("Успех", f"Файл {self.config.mod_name}_types.xml успешно создан!\n\nПуть: {output_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании MODtypes.xml: {str(e)}")
            self.log(f"ОШИБКА: {str(e)}")
            
    def save_xml_pretty(self, filepath: str, tree: ET.ElementTree):
        """Сохранение XML с красивым форматированием"""
        xml_str = ET.tostring(tree.getroot(), encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="    ", encoding=None)
        
        # Удаляем лишнюю первую строку если она дублируется
        lines = pretty_xml.split('\n')
        if lines[0].startswith('<?xml') and len(lines) > 1 and lines[1].startswith('<?xml'):
            lines = lines[1:]
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            
    def run_all(self):
        """Выполнение всех шагов"""
        self.log("=" * 50)
        self.log("Запуск полного процесса генерации...")
        self.update_cfgeconomycore()
        self.generate_modtypes()
        self.log("=" * 50)
        self.log("✅ Процесс завершен!")


class ItemDialog:
    """Диалоговое окно для добавления/редактирования предмета"""
    
    def __init__(self, parent, title: str, data: Optional[dict] = None):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.geometry("500x550")
        self.dialog.resizable(False, False)
        
        frame = ttk.Frame(self.dialog, padding="15")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Название предмета
        ttk.Label(frame, text="Название предмета *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=data.get("name", "") if data else "")
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Параметры спавна
        params_frame = ttk.LabelFrame(frame, text="Параметры спавна", padding="5")
        params_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)
        
        # Nominal
        ttk.Label(params_frame, text="Nominal:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.nominal_var = tk.IntVar(value=data.get("nominal", 0) if data else 0)
        ttk.Spinbox(params_frame, from_=0, to=1000, textvariable=self.nominal_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Min
        ttk.Label(params_frame, text="Min:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.min_var = tk.IntVar(value=data.get("min", 0) if data else 0)
        ttk.Spinbox(params_frame, from_=0, to=1000, textvariable=self.min_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Quantmin
        ttk.Label(params_frame, text="Quantmin:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.quantmin_var = tk.IntVar(value=data.get("quantmin", 0) if data else 0)
        ttk.Spinbox(params_frame, from_=0, to=100, textvariable=self.quantmin_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Quantmax
        ttk.Label(params_frame, text="Quantmax:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.quantmax_var = tk.IntVar(value=data.get("quantmax", 0) if data else 0)
        ttk.Spinbox(params_frame, from_=0, to=100, textvariable=self.quantmax_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Max
        ttk.Label(params_frame, text="Max:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.max_var = tk.IntVar(value=data.get("max", 0) if data else 0)
        ttk.Spinbox(params_frame, from_=0, to=1000, textvariable=self.max_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Restock min/max
        ttk.Label(params_frame, text="Restock min:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        self.restock_min_var = tk.IntVar(value=data.get("restock_min", 0) if data else 0)
        ttk.Spinbox(params_frame, from_=0, to=3600, textvariable=self.restock_min_var, width=10).grid(row=2, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(params_frame, text="Restock max:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.restock_max_var = tk.IntVar(value=data.get("restock_max", 0) if data else 0)
        ttk.Spinbox(params_frame, from_=0, to=3600, textvariable=self.restock_max_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        
        # Категории
        cat_frame = ttk.LabelFrame(frame, text="Категории", padding="5")
        cat_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        cat_frame.columnconfigure(1, weight=1)
        
        ttk.Label(cat_frame, text="Основная:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.cat_main_var = tk.StringVar(value=data.get("category_main", "weapons") if data else "weapons")
        categories = ["weapons", "food", "clothes", "tools", "medic", "containers", "vehiclesparts", "misc"]
        ttk.Combobox(cat_frame, textvariable=self.cat_main_var, values=categories, width=20, state="readonly").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(cat_frame, text="Подкатегория:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.cat_sub_var = tk.StringVar(value=data.get("category_sub", "") if data else "")
        ttk.Entry(cat_frame, textvariable=self.cat_sub_var, width=20).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        
        # Тег
        ttk.Label(frame, text="Тег размещения:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tag_var = tk.StringVar(value=data.get("tag", "floor") if data else "floor")
        tags = ["floor", "shelves", "hangers", "ground"]
        ttk.Combobox(frame, textvariable=self.tag_var, values=tags, width=37, state="readonly").grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Usage flags (текстовое поле для ввода через запятую)
        ttk.Label(frame, text="Usage flags (через запятую):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.usage_var = tk.StringVar(value=", ".join(data.get("usage_flags", [])) if data and data.get("usage_flags") else "")
        ttk.Entry(frame, textvariable=self.usage_var, width=40).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="✅ OK", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="🎯 Авто", command=self.auto_fill).pack(side=tk.RIGHT, padx=10)
        
        self.dialog.wait_window()
        
    def auto_fill(self):
        """Автозаполнение категорий и тега"""
        name = self.name_var.get().strip()
        if name:
            item = DayZItem(name)
            item.guess_category()
            item.guess_tag()
            self.cat_main_var.set(item.category_main)
            self.cat_sub_var.set(item.category_sub)
            self.tag_var.set(item.tag)
            
    def on_ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Название предмета обязательно!")
            return
            
        usage_flags = [f.strip() for f in self.usage_var.get().split(",") if f.strip()]
        
        self.result = {
            "name": name,
            "nominal": self.nominal_var.get(),
            "min": self.min_var.get(),
            "quantmin": self.quantmin_var.get(),
            "quantmax": self.quantmax_var.get(),
            "max": self.max_var.get(),
            "restock_min": self.restock_min_var.get(),
            "restock_max": self.restock_max_var.get(),
            "category_main": self.cat_main_var.get(),
            "category_sub": self.cat_sub_var.get(),
            "usage_flags": usage_flags,
            "tag": self.tag_var.get()
        }
        self.dialog.destroy()
        
    def on_cancel(self):
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = DayZGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
