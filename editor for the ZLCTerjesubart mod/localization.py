# -*- coding: utf-8 -*-
"""
Система локализации для редактора артефактов DayZ
Профессиональный перевод на русский язык
"""

LOCALE_RU = {
    # === ЗАГОЛОВОК И ОСНОВНЫЕ ЭЛЕМЕНТЫ ===
    "app_title": "DayZ Artifacts Manager — Редактор артефактов",
    "status_ready": "Готово. Выберите или создайте файл .json",
    "status_loaded": "Загружено: {filename} | Артефактов: {count}",
    "status_saved": "Сохранено: {filename}",
    "status_changes_applied": "Изменения применены в память. Нажмите 💾 Сохранить.",
    "status_artifact_deleted": "Артефакт удалён. Не забудьте сохранить!",
    
    # === КНОПКИ ГЛАВНОГО ОКНА ===
    "btn_load_json": "📂 Загрузить ARTIFACTS.JSON",
    "btn_save_json": "💾 Сохранить изменения",
    "btn_add": "➕ Добавить артефакт",
    "btn_edit": "✏️ Редактировать",
    "btn_delete": "🗑️ Удалить",
    "btn_refresh": "🔄 Обновить список",
    "btn_import_csv": "📄 Импорт из CSV (класснеймы)",
    "btn_bulk_edit": "🎲 Массовая настройка эффектов",
    
    # === ПОИСК ===
    "search_label": "🔍 Поиск артефакта по класснейму:",
    "search_clear": "✕ Очистить",
    "search_placeholder": "Введите название артефакта...",
    
    # === ЗАГОЛОВКИ ТАБЛИЦЫ ===
    "tree_header_idx": "#",
    "tree_header_classname": "Класснейм артефакта",
    "tree_header_work_hands": "В руке",
    "tree_header_work_inventory": "В инвентаре",
    "tree_header_area_radius": "Зона (м)",
    "tree_header_positive_effects": "Позитивных",
    "tree_header_negative_effects": "Негативных",
    
    # === РЕДАКТОР АРТЕФАКТА ===
    "editor_title_new": "✨ Редактор артефакта (Новый)",
    "editor_title_edit": "✏️ Редактор артефакта #{index}",
    "editor_main_params": "📋 Основные параметры артефакта",
    "editor_field_classname": "Класснейм (уникальный ключ)",
    "editor_field_work_hands": "Работает в руке (1/0)",
    "editor_field_work_inventory": "Работает в инвентаре (1/0)",
    "editor_field_work_area": "Работает в зоне аномалии (1/0)",
    "editor_field_area_radius": "Радиус аномалии (метров)",
    "editor_field_area_power": "Мощность зоны аномалии",
    
    # === ВКЛАДКИ ЭФФЕКТОВ ===
    "tab_positive_effects": "✅ Позитивные эффекты",
    "tab_negative_effects": "❌ Негативные эффекты",
    "table_header_effect": "Эффект",
    "table_header_value": "Значение",
    "table_header_description": "Описание эффекта",
    
    # === ОПИСАНИЯ ЭФФЕКТОВ ===
    "effect_health": "Здоровье персонажа",
    "effect_blood": "Уровень крови",
    "effect_shock": "Шок (болевой)",
    "effect_water": "Уровень воды в организме",
    "effect_energy": "Энергия персонажа",
    "effect_stamina": "Выносливость",
    "effect_sleeping": "Сонливость / бодрость",
    "effect_mind": "Психическое здоровье (рассудок)",
    "effect_pain": "Болевые ощущения",
    "effect_contusion": "Контузия (потрясение мозга)",
    "effect_hematomas": "Гематомы (синяки)",
    "effect_lightBleeding": "Лёгкое кровотечение",
    "effect_heavyBleeding": "Сильное кровотечение",
    "effect_bulletWounds": "Пулевые ранения",
    "effect_viscera": "Состояние внутренних органов",
    "effect_sepsis": "Сепсис (заражение крови)",
    "effect_zombieVirus": "Вирус зомби",
    "effect_influenza": "Грипп / простуда",
    "effect_poison": "Отравление",
    "effect_biohazard": "Биологическая угроза",
    "effect_rabies": "Бешенство",
    "effect_overdose": "Передозировка препаратами",
    "effect_immunity": "Иммунитет к болезням",
    "effect_radiation": "Радиационное облучение",
    "effect_temperature": "Температура тела",
    "effect_brokenLeg": "Сломанная нога",
    "effect_jumpHeight": "Высота прыжка",
    "effect_meleeDamage": "Урон ближнего боя",
    
    # === КНОПКИ РЕДАКТОРА ===
    "btn_apply": "✅ Применить изменения",
    "btn_cancel": "❌ Отмена",
    "btn_save_template": "📄 Заполнить шаблоном (нули)",
    "btn_parse_description": "📖 Заполнить из описания (CSV)",
    
    # === ПАРСИНГ ОПИСАНИЯ ===
    "select_csv_for_parsing": "Выберите CSV файл с описаниями артефактов",
    "parse_description_not_found": "Описание для артефакта '{class_name}' не найдено в CSV файле.",
    "parse_description_no_values": "Не удалось извлечь числовые значения эффектов из описания артефакта '{class_name}'.",
    "parse_preview_title": "Найдены следующие значения для артефакта '{class_name}':",
    "parse_preview_question": "Заполнить пустые поля этими значениями?",
    "parse_preview_title_short": "Предпросмотр значений из описания",
    "parse_description_success": "Успешно заполнено эффектов: {count}",
    "error_parsing_title": "Ошибка при парсинге описания",
    "info_title": "Информация",
    "success_title": "Успешно",
    
    # === МАССОВАЯ НАСТРОЙКА ===
    "bulk_title": "🎲 Массовая настройка эффектов артефактов",
    "bulk_instruction": "Выберите артефакты, эффекты и диапазоны значений для случайной генерации",
    "bulk_step_1": "1️⃣ Выберите артефакты для настройки",
    "bulk_step_2": "2️⃣ Выберите эффекты для рандомизации",
    "bulk_step_3": "3️⃣ Диапазон значений (минимум — максимум)",
    "bulk_step_4": "🔧 Дополнительные опции",
    
    "bulk_select_all": "✅ Выбрать все",
    "bulk_deselect_all": "❌ Снять все",
    "bulk_select_effects_all": "✅ Все эффекты",
    "bulk_select_effects_none": "❌ Никакие",
    
    "bulk_range_positive": "Позитивные эффекты:",
    "bulk_range_negative": "Негативные эффекты:",
    "bulk_range_to": "до",
    
    "bulk_opt_skip_zero": "Не устанавливать нулевые значения (пропускать, если выпало 0)",
    "bulk_opt_overwrite": "Перезаписать существующие эффекты (иначе только пустые)",
    
    "bulk_btn_apply": "🎲 Применить случайные значения",
    "bulk_btn_cancel": "❌ Отмена",
    
    # === СООБЩЕНИЯ ОБ ОШИБКАХ ===
    "error_load_title": "❌ Ошибка загрузки файла",
    "error_save_title": "❌ Ошибка сохранения файла",
    "error_validation_title": "⚠️ Ошибка валидации данных",
    "error_import_title": "❌ Ошибка импорта CSV",
    "error_structure": "Неверная структура файла. Отсутствует ключ 'artifacts'.",
    "error_field_empty": "Поле '{field}' не может быть пустым",
    "error_field_binary": "Поле '{field}' должно быть 0 или 1",
    "error_field_number": "Неверное числовое значение для эффекта '{effect}': {value}",
    "error_effect_empty": "Поле эффекта '{effect}' в разделе '{section}' не может быть пустым. Введите 0, если эффект не нужен.",
    "error_min_max": "Минимум не может быть больше максимума для {section}",
    "error_invalid_range": "Неверный диапазон значений: {error}",
    
    # === ПРЕДУПРЕЖДЕНИЯ ===
    "warning_no_artifacts": "⚠️ Сначала загрузите файл с артефактами.",
    "warning_select_artifact": "⚠️ Сначала выделите артефакт в списке.",
    "warning_select_bulk_artifact": "⚠️ Выберите хотя бы один артефакт!",
    "warning_select_bulk_effect": "⚠️ Выберите хотя бы один эффект!",
    "warning_empty_text": "⚠️ Текстовое поле пустое.",
    "warning_confirm_delete": "Подтверждение удаления",
    "warning_delete_message": "Удалить артефакт '{classname}'?\n\nЭто действие нельзя отменить!",
    
    # === УСПЕШНЫЕ ОПЕРАЦИИ ===
    "success_save_title": "✅ Успешно сохранено!",
    "success_save_message": "Файл успешно сохранён! Теперь можно запускать мод.",
    "success_validation_title": "✅ Проверка пройдена",
    "success_validation_message": "Формат JSON корректен.",
    "success_import_title": "✅ Импорт завершён",
    "success_import_message": "Добавлено новых артефактов: {count}\n\nТеперь откройте ✏️ Редактировать и заполните эффекты.",
    "success_bulk_title": "✅ Готово!",
    "success_bulk_message": "Изменено эффектов: {modified}\nАртефактов затронуто: {artifacts}\n\nНе забудьте сохранить файл! 💾",
    
    # === CSV ИМПОРТ ===
    "csv_error_no_header": "CSV файл пуст или не содержит заголовков",
    "csv_error_no_classname": "Не найден столбец с класснеймом (class_name или classname)",
    
    # === РАЗНОЕ ===
    "unknown_artifact": "Неизвестный артефакт",
    "artifact_index": "Артефакт #{index}",
    "positive_effects_short": "Позитив",
    "negative_effects_short": "Негатив",
    "area_radius_short": "Зона м",
}

# Английская локализация (для будущего расширения)
LOCALE_EN = {
    "app_title": "DayZ Artifacts Manager — Artifact Editor",
    "status_ready": "Ready. Select or create a .json file",
    "status_loaded": "Loaded: {filename} | Artifacts: {count}",
    "status_saved": "Saved: {filename}",
    "status_changes_applied": "Changes applied to memory. Click 💾 Save.",
    "status_artifact_deleted": "Artifact deleted. Don't forget to save!",
    
    "btn_load_json": "📂 Load ARTIFACTS.JSON",
    "btn_save_json": "💾 Save Changes",
    "btn_add": "➕ Add Artifact",
    "btn_edit": "✏️ Edit",
    "btn_delete": "🗑️ Delete",
    "btn_refresh": "🔄 Refresh List",
    "btn_import_csv": "📄 Import from CSV (classnames)",
    "btn_bulk_edit": "🎲 Bulk Effects Setup",
    
    "search_label": "🔍 Search artifact by classname:",
    "search_clear": "✕ Clear",
    "search_placeholder": "Enter artifact name...",
    
    "tree_header_idx": "#",
    "tree_header_classname": "Artifact Classname",
    "tree_header_work_hands": "In Hands",
    "tree_header_work_inventory": "In Inventory",
    "tree_header_area_radius": "Zone (m)",
    "tree_header_positive_effects": "Positive",
    "tree_header_negative_effects": "Negative",
}


class Localization:
    """Класс управления локализацией приложения"""
    
    def __init__(self, language="ru"):
        self.current_language = language
        self.locales = {
            "ru": LOCALE_RU,
            "en": LOCALE_EN,
        }
    
    def get(self, key, **kwargs):
        """
        Получить переведённую строку
        
        Args:
            key: Ключ строки в словаре локализации
            **kwargs: Параметры для форматирования строки
            
        Returns:
            Переведённая строка с подставленными параметрами
        """
        locale = self.locales.get(self.current_language, LOCALE_RU)
        text = locale.get(key, f"MISSING:{key}")
        
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass  # Если параметров нет в строке, возвращаем как есть
        
        return text
    
    def set_language(self, language):
        """Установить текущий язык"""
        if language in self.locales:
            self.current_language = language
    
    def get_effect_description(self, effect_key):
        """Получить описание эффекта на текущем языке"""
        key = f"effect_{effect_key}"
        return self.get(key)


# Глобальный экземпляр локализации
localizer = Localization("ru")


def _(key, **kwargs):
    """Удобная функция для получения переведённых строк"""
    return localizer.get(key, **kwargs)
