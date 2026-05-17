#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DayZ MODtypes.xml Generator
Утилита для автоматического создания файла MODtypes.xml,
который работает в паре с ванильным types.xml для сервера DayZ Standalone.

Автор: AI Assistant
Версия: 1.0
"""

import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
import argparse
from datetime import datetime
from pathlib import Path


class DayZTypesGenerator:
    """Генератор файлов типов для модов DayZ."""
    
    # Стандартные категории предметов DayZ
    DEFAULT_CATEGORIES = {
        'weapons': 'Weapons',
        'magazines': 'Magazines',
        'clothing': 'Clothing',
        'gear': 'Gear',
        'food': 'Food',
        'drinks': 'Drinks',
        'tools': 'Tools',
        'medical': 'Medical',
        'building': 'Building',
        'vehicles': 'Vehicles',
        'parts': 'Parts',
        'misc': 'Misc'
    }
    
    def __init__(self, output_dir='.', mod_name='MOD'):
        """
        Инициализация генератора.
        
        Args:
            output_dir: Директория для выходного файла
            mod_name: Название мода для заголовка
        """
        self.output_dir = Path(output_dir)
        self.mod_name = mod_name
        self.items = []
        self.presets = {}
        
    def add_item(self, class_name, category='misc', count_min=1, count_max=1, 
                 lifetime=3888000, usage='0.05', chance='1.0', 
                 tag=None, value='0', map=None):
        """
        Добавить предмет в список генерации.
        
        Args:
            class_name: Имя класса предмета (например: 'AKM_F')
            category: Категория предмета
            count_min: Минимальное количество в стаке
            count_max: Максимальное количество в стаке
            lifetime: Время жизни предмета в секундах (по умолчанию 45 дней)
            usage: Частота использования (0.0-1.0)
            chance: Шанс появления (0.0-1.0)
            tag: Тег предмета (None для автоопределения)
            value: Значение предмета
            map: Карта для спавна (None для всех карт)
        """
        if tag is None:
            tag = self._autodetect_tag(class_name)
            
        item = {
            'name': class_name,
            'category': category,
            'count_min': count_min,
            'count_max': count_max,
            'lifetime': lifetime,
            'usage': usage,
            'chance': chance,
            'tag': tag,
            'value': value,
            'map': map
        }
        self.items.append(item)
        return self
        
    def _autodetect_tag(self, class_name):
        """Автоопределение тега по имени класса."""
        name_lower = class_name.lower()
        
        if any(x in name_lower for x in ['ammo', 'magazine', 'mag']):
            return 'magazines'
        elif any(x in name_lower for x in ['rifle', 'shotgun', 'pistol', 'sniper', 'ak', 'm4', 'ar15']):
            return 'weapons'
        elif any(x in name_lower for x in ['shirt', 'pants', 'jacket', 'coat', 'hat', 'boots', 'shoes']):
            return 'clothes'
        elif any(x in name_lower for x in ['backpack', 'bag', 'vest', 'pouch']):
            return 'bags'
        elif any(x in name_lower for x in ['bandage', 'medic', 'vitamin', 'antibiotic', 'syringe']):
            return 'medic'
        elif any(x in name_lower for x in ['can', 'bottle', 'water', 'soda', 'juice']):
            return 'food'
        elif any(x in name_lower for x in ['apple', 'bread', 'meat', 'fish', 'tomato', 'potato']):
            return 'food'
        elif any(x in name_lower for x in ['knife', 'axe', 'hatchet', 'shovel', 'pickaxe', 'hammer']):
            return 'tools'
        elif any(x in name_lower for x in ['fence', 'gate', 'watchtower', 'rampart']):
            return 'building'
        else:
            return 'floor'
    
    def add_preset(self, preset_name, items_list):
        """
        Добавить пресет группы предметов.
        
        Args:
            preset_name: Название пресета
            items_list: Список словарей предметов
        """
        self.presets[preset_name] = items_list
        
    def load_from_file(self, filepath, file_format='json'):
        """
        Загрузить предметы из файла конфигурации.
        
        Args:
            filepath: Путь к файлу
            file_format: Формат файла ('json', 'csv', 'xml')
        """
        import json
        import csv
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Файл не найден: {filepath}")
            
        if file_format == 'json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        self.add_item(**item)
                elif isinstance(data, dict) and 'items' in data:
                    for item in data['items']:
                        self.add_item(**item)
                        
        elif file_format == 'csv':
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.add_item(
                        class_name=row.get('className', row.get('name', '')),
                        category=row.get('category', 'misc'),
                        count_min=int(row.get('countMin', 1)),
                        count_max=int(row.get('countMax', 1)),
                        lifetime=int(row.get('lifetime', 3888000)),
                        usage=row.get('usage', '0.05'),
                        chance=row.get('chance', '1.0')
                    )
                    
        return self
    
    def generate_xml(self, indent=2):
        """
        Сгенерировать XML содержимое для MODtypes.xml.
        
        Args:
            indent: Количество пробелов для отступов
            
        Returns:
            Строка с XML содержимым
        """
        # Создаем корневой элемент
        root = ET.Element('file')
        root.set('version', '111')
        
        # Добавляем комментарий
        comment = ET.Comment(f"""
    MODtypes.xml - Generated by DayZ MODtypes Generator
    Mod: {self.mod_name}
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Этот файл предназначен для работы вместе с ванильным types.xml.
    Разместите его в папке миссии или мода и убедитесь что он загружается после types.xml.
""")
        root.insert(0, comment)
        
        # Группа types
        types_elem = ET.SubElement(root, 'types')
        
        # Добавляем элементы
        for item in self.items:
            type_elem = ET.SubElement(types_elem, 'type')
            type_elem.set('name', item['name'])
            
            # Параметры
            params = {
                'count_min': str(item['count_min']),
                'count_max': str(item['count_max']),
                'lifetime': str(item['lifetime']),
                'usage': item['usage'],
                'chance': item['chance'],
                'tag': item['tag'],
                'value': str(item['value'])
            }
            
            for param_name, param_value in params.items():
                param_elem = ET.SubElement(type_elem, param_name)
                param_elem.text = param_value
                
            # Map (если указан)
            if item['map']:
                map_elem = ET.SubElement(type_elem, 'map')
                map_elem.set('name', item['map'])
                
        # Пресеты (если есть)
        if self.presets:
            presets_elem = ET.SubElement(root, 'presets')
            for preset_name, preset_items in self.presets.items():
                preset_elem = ET.SubElement(presets_elem, 'preset')
                preset_elem.set('name', preset_name)
                for pitem in preset_items:
                    pi_elem = ET.SubElement(preset_elem, 'item')
                    pi_elem.set('name', pitem.get('name', ''))
                    pi_elem.set('count', str(pitem.get('count', 1)))
                    pi_elem.set('chance', str(pitem.get('chance', '1.0')))
        
        # Форматируем XML
        xml_str = ET.tostring(root, encoding='unicode')
        
        # Красивое форматирование
        try:
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent=' ' * indent, encoding=None)
            # Убираем лишнюю декларацию если есть дубликат
            lines = pretty_xml.split('\n')
            if lines[0].startswith('<?xml') and len(lines) > 1:
                # Оставляем только одну декларацию
                pretty_xml = '\n'.join(lines[0:1] + [l for l in lines[1:] if l.strip()])
        except:
            pretty_xml = xml_str
            
        return pretty_xml
    
    def save_to_file(self, filename='MODtypes.xml'):
        """
        Сохранить сгенерированный XML в файл.
        
        Args:
            filename: Имя выходного файла
            
        Returns:
            Путь к сохраненному файлу
        """
        output_path = self.output_dir / filename
        
        xml_content = self.generate_xml()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
            
        print(f"✓ Файл успешно создан: {output_path}")
        print(f"  Количество предметов: {len(self.items)}")
        print(f"  Количество пресетов: {len(self.presets)}")
        
        return output_path
    
    def scan_mission_folder(self, mission_path):
        """
        Сканировать папку миссии на наличие конфигов мода.
        
        Args:
            mission_path: Путь к папке миссии
            
        Returns:
            Список найденных предметов из конфига мода
        """
        mission_path = Path(mission_path)
        found_items = []
        
        # Ищем cfgspawnabletypes.xml
        spawnable_path = mission_path / 'cfgspawnabletypes.xml'
        if spawnable_path.exists():
            try:
                tree = ET.parse(spawnable_path)
                root = tree.getroot()
                for child in root.iter():
                    if child.tag == 'children' or 'name' in child.attrib:
                        name = child.attrib.get('name', '')
                        if name and name not in found_items:
                            found_items.append(name)
            except Exception as e:
                print(f"⚠ Ошибка чтения cfgspawnabletypes.xml: {e}")
        
        # Ищем другие XML файлы мода
        for xml_file in mission_path.glob('*.xml'):
            if xml_file.name not in ['types.xml', 'MODtypes.xml', 'economy.xml']:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    # Пытаемся найти имена классов
                    for elem in root.iter():
                        name = elem.attrib.get('name', '')
                        class_name = elem.attrib.get('className', '')
                        if name and name not in found_items:
                            found_items.append(name)
                        if class_name and class_name not in found_items:
                            found_items.append(class_name)
                except:
                    continue
                    
        return found_items


def create_sample_config():
    """Создать пример конфигурации для демонстрации."""
    sample_items = [
        # Оружие
        {'class_name': 'AKM_F', 'category': 'weapons', 'count_min': 1, 'count_max': 1, 
         'usage': '0.10', 'chance': '0.50'},
        {'class_name': 'M4A1', 'category': 'weapons', 'count_min': 1, 'count_max': 1,
         'usage': '0.08', 'chance': '0.40'},
         
        # Магазины
        {'class_name': 'AMag_762x39', 'category': 'magazines', 'count_min': 5, 'count_max': 10,
         'usage': '0.20', 'chance': '0.70'},
        {'class_name': 'AMag_556x45', 'category': 'magazines', 'count_min': 5, 'count_max': 10,
         'usage': '0.20', 'chance': '0.70'},
         
        # Одежда
        {'class_name': 'TShirt_Grey', 'category': 'clothing', 'count_min': 1, 'count_max': 1,
         'usage': '0.30', 'chance': '0.80'},
        {'class_name': 'Jeans_Blue', 'category': 'clothing', 'count_min': 1, 'count_max': 1,
         'usage': '0.30', 'chance': '0.80'},
         
        # Рюкзаки
        {'class_name': 'MountainBag_Red', 'category': 'gear', 'count_min': 1, 'count_max': 1,
         'usage': '0.15', 'chance': '0.60'},
         
        # Еда
        {'class_name': 'Apple', 'category': 'food', 'count_min': 1, 'count_max': 3,
         'usage': '0.50', 'chance': '0.90'},
        {'class_name': 'CanBakedBeans', 'category': 'food', 'count_min': 1, 'count_max': 2,
         'usage': '0.40', 'chance': '0.85'},
         
        # Медицина
        {'class_name': 'BandageDressing', 'category': 'medical', 'count_min': 1, 'count_max': 3,
         'usage': '0.35', 'chance': '0.75'},
        {'class_name': 'Epinephrine', 'category': 'medical', 'count_min': 1, 'count_max': 1,
         'usage': '0.10', 'chance': '0.30'},
         
        # Инструменты
        {'class_name': 'CombatKnife', 'category': 'tools', 'count_min': 1, 'count_max': 1,
         'usage': '0.20', 'chance': '0.65'},
        {'class_name': 'WoodenLog', 'category': 'building', 'count_min': 1, 'count_max': 5,
         'usage': '0.60', 'chance': '0.95'},
    ]
    return sample_items


def main():
    """Основная функция программы."""
    parser = argparse.ArgumentParser(
        description='DayZ MODtypes.xml Generator - Утилита для создания файла типов предметов мода',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --output MODtypes.xml
  %(prog)s --config items.json --output mymod_types.xml
  %(prog)s --sample --output sample_types.xml
  %(prog)s --scan ./mission_folder --output MODtypes.xml
  
Структура JSON конфига:
  [
    {"className": "AKM_F", "category": "weapons", "countMin": 1, "countMax": 1},
    {"className": "Apple", "category": "food", "countMin": 1, "countMax": 3}
  ]
        """
    )
    
    parser.add_argument('-o', '--output', default='MODtypes.xml',
                       help='Имя выходного файла (по умолчанию: MODtypes.xml)')
    parser.add_argument('-c', '--config', 
                       help='Путь к JSON/CSV файлу конфигурации предметов')
    parser.add_argument('-s', '--sample', action='store_true',
                       help='Сгенерировать пример файла с демо-предметами')
    parser.add_argument('--scan', metavar='PATH',
                       help='Сканировать папку миссии на наличие предметов мода')
    parser.add_argument('--mod-name', default='Custom MOD',
                       help='Название мода для заголовка файла')
    parser.add_argument('--dir', default='.',
                       help='Директория для выходного файла (по умолчанию: текущая)')
    parser.add_argument('--format', choices=['json', 'csv', 'xml'], default='json',
                       help='Формат входного файла конфигурации')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("DayZ MODtypes.xml Generator v1.0")
    print("=" * 60)
    print()
    
    # Создаем генератор
    generator = DayZTypesGenerator(output_dir=args.dir, mod_name=args.mod_name)
    
    # Режим сканирования
    if args.scan:
        print(f"🔍 Сканирование папки миссии: {args.scan}")
        found_items = generator.scan_mission_folder(args.scan)
        if found_items:
            print(f"  Найдено предметов: {len(found_items)}")
            for item in found_items[:10]:
                print(f"    - {item}")
            if len(found_items) > 10:
                print(f"    ... и ещё {len(found_items) - 10}")
            
            # Автоматически добавляем найденные предметы
            for item_name in found_items:
                generator.add_item(class_name=item_name)
        else:
            print("  Предметы не найдены")
    
    # Загрузка из конфига
    if args.config:
        print(f"📄 Загрузка конфигурации: {args.config}")
        try:
            generator.load_from_file(args.config, file_format=args.format)
            print(f"  Загружено предметов: {len(generator.items)}")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            sys.exit(1)
    
    # Генерация примера
    if args.sample:
        print("📋 Генерация примера конфигурации...")
        sample_items = create_sample_config()
        for item in sample_items:
            generator.add_item(**item)
        print(f"  Добавлено демо-предметов: {len(sample_items)}")
    
    # Если ничего не указано, создаем минимальный пример
    if not args.config and not args.scan and not args.sample:
        print("ℹ Используем режим по умолчанию (минимальный пример)...")
        print("   Используйте --help для просмотра всех опций")
        print()
        
        # Минимальный набор для демонстрации
        generator.add_item('AKM_F', category='weapons', chance='0.50')
        generator.add_item('AMag_762x39', category='magazines', count_min=5, count_max=10)
        generator.add_item('Apple', category='food', count_max=3, chance='0.90')
        generator.add_item('BandageDressing', category='medical')
        generator.add_item('TShirt_Grey', category='clothing')
    
    print()
    print("⚙️ Генерация MODtypes.xml...")
    print()
    
    # Сохраняем файл
    try:
        output_path = generator.save_to_file(args.output)
        print()
        print("=" * 60)
        print("✅ Готово!")
        print("=" * 60)
        print()
        print("📁 Расположение файла:", output_path.absolute())
        print()
        print("📝 Инструкция по установке:")
        print("   1. Скопируйте MODtypes.xml в папку вашей миссии")
        print("      Обычно: DayZServer/profiles/Missions/<имя_миссии>.ChernarusPlus/")
        print()
        print("   2. Убедитесь что файл загружается ПОСЛЕ ванильного types.xml")
        print("      В serverDZ.cfg добавьте в economy:" )
        print('         economyType="MODtypes.xml";')
        print()
        print("   3. Или используйте в init.c:")
        print('         GetGame().GetMission().GetEconomy().LoadTypesFromFile("MODtypes.xml");')
        print()
        print("⚠️ Важно: MODtypes.xml должен дополнять types.xml, а не заменять его!")
        print()
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
