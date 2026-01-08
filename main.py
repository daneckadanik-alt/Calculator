import sys
# Сброс конфига Kivy, чтобы не тянул старые файлы
from kivy.config import Config
Config.set('kivy', 'global_kv_file', 'None')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand') # Убираем красные точки

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

# =============================================================================
# KV LANGUAGE (ДИЗАЙН)
# =============================================================================
KV_LAYOUT = """
#:import utils kivy.utils

# --- ДИСПЛЕЙ (ТЕКСТОВОЕ ПОЛЕ) ---
<AutoSizingDisplay>:
    multiline: False
    readonly: True
    halign: 'right'
    valign: 'bottom'
    background_color: 0, 0, 0, 0     # Прозрачный фон
    foreground_color: 1, 1, 1, 1     # Белый текст
    cursor_color: 0, 0, 0, 0         # Скрытый курсор
    background_normal: ''            # Убираем картинки фона
    background_active: ''
    padding: [20, 0, 20, 0]          # Отступы

# --- КНОПКА (ТЕКСТ + НАЖАТИЕ) ---
# Мы не используем стандартный Button, чтобы не было квадратов
<CalcButton>:
    font_size: '32sp'
    color: self.text_color
    halign: 'center'
    valign: 'center'
    
    # Рисуем кнопку сами
    canvas.before:
        Color:
            rgba: self.current_bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2,]  # Делает кнопку идеально круглой/овальной

# --- ГЛАВНЫЙ ЭКРАН ---
<MainWidget>:
    orientation: 'vertical'
    
    # Черный фон всего приложения
    canvas.before:
        Color:
            rgba: utils.get_color_from_hex('#000000')
        Rectangle:
            pos: self.pos
            size: self.size

    # 1. Дисплей (сверху)
    BoxLayout:
        size_hint_y: 0.3
        padding: [0, 0, 0, 20] # Отступ снизу
        
        AutoSizingDisplay:
            id: display
            text: root.display_text
            # Центрирование текста по вертикали
            padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]

    # 2. Кнопки (снизу)
    GridLayout:
        size_hint_y: 0.7
        cols: 4
        spacing: 15          # Расстояние между кнопками
        padding: [15, 0, 15, 15] # Отступы от краев экрана

        # --- РЯД 1 ---
        CalcButton:
            text: 'C'
            bg_hex: '#A5A5A5'      # Светло-серый
            text_hex: '#000000'    # Черный текст
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '('
            bg_hex: '#A5A5A5'
            text_hex: '#000000'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: ')'
            bg_hex: '#A5A5A5'
            text_hex: '#000000'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '/'
            bg_hex: '#32D74B'      # Зеленый
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)

        # --- РЯД 2 ---
        CalcButton:
            text: '7'
            bg_hex: '#333333'      # Темно-серый
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '8'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '9'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '*'
            bg_hex: '#32D74B'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)

        # --- РЯД 3 ---
        CalcButton:
            text: '4'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '5'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '6'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '-'
            bg_hex: '#32D74B'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)

        # --- РЯД 4 ---
        CalcButton:
            text: '1'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '2'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '3'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '+'
            bg_hex: '#32D74B'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)

        # --- РЯД 5 ---
        CalcButton:
            text: '.'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '0'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '<'
            bg_hex: '#333333'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
        CalcButton:
            text: '='
            bg_hex: '#32D74B'
            text_hex: '#FFFFFF'
            on_press: root.on_button_press(self.text)
"""

# =============================================================================
# LOGIC
# =============================================================================

class AutoSizingDisplay(TextInput):
    """Дисплей, который сам уменьшает шрифт, чтобы текст влез."""
    def on_text(self, instance, value):
        l = len(value)
        if l < 7: self.font_size = '80sp'
        elif l < 10: self.font_size = '60sp'
        elif l < 13: self.font_size = '45sp'
        elif l < 15: self.font_size = '35sp'
        else: self.font_size = '25sp'

class CalcButton(ButtonBehavior, Label):
    """
    Чистая кнопка без стандартной графики Kivy.
    """
    bg_hex = StringProperty('#333333')
    text_hex = StringProperty('#FFFFFF')
    
    current_bg_color = ListProperty([0,0,0,0])
    text_color = ListProperty([1,1,1,1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ждем загрузки KV, потом конвертируем HEX цвета в RGBA
        from kivy.clock import Clock
        Clock.schedule_once(self.init_colors, 0)

    def init_colors(self, dt):
        self.current_bg_color = get_color_from_hex(self.bg_hex)
        self.text_color = get_color_from_hex(self.text_hex)

    def on_press(self):
        # Эффект нажатия (делаем цвет светлее)
        base = get_color_from_hex(self.bg_hex)
        highlight = [min(c + 0.2, 1.0) for c in base[:3]] + [base[3]]
        self.current_bg_color = highlight

    def on_release(self):
        # Возврат цвета
        base = get_color_from_hex(self.bg_hex)
        anim = Animation(current_bg_color=base, duration=0.2)
        anim.start(self)

class MainWidget(BoxLayout):
    display_text = StringProperty("0")
    _last_was_result = False

    def on_button_press(self, text):
        current = self.display_text
        
        if text == "C":
            self.display_text = "0"
            self._last_was_result = False
        
        elif text == "<":
            if current == "Error" or len(current) == 1:
                self.display_text = "0"
            else:
                self.display_text = current[:-1]
        
        elif text == "=":
            try:
                # Безопасная замена символов
                expr = current.replace('×', '*').replace('÷', '/')
                # Проверка на допустимые символы
                if not set(expr).issubset(set("0123456789+-*/.() ")):
                    raise ValueError
                
                # Вычисление
                res = eval(expr, {"__builtins__": None}, {})
                
                # Форматирование результата
                if isinstance(res, float):
                    if res.is_integer():
                        res = int(res)
                    else:
                        res = round(res, 8)
                
                res_str = str(res)
                # Если число огромное, режем или используем e-нотацию
                if len(res_str) > 15:
                     res_str = "{:.5e}".format(res) if isinstance(res, float) else res_str[:15]

                self.display_text = res_str
                self._last_was_result = True
            except:
                self.display_text = "Error"
        
        else:
            # Ввод цифр и знаков
            if current == "Error":
                current = "0"
            
            if self._last_was_result:
                if text in "+-*/":
                    self._last_was_result = False
                else:
                    current = "0"
                    self._last_was_result = False
            
            if current == "0" and text not in "+-*/).":
                self.display_text = text
            else:
                if len(current) < 20: # Лимит символов
                    self.display_text += text

class SimpleCalcApp(App):
    def build(self):
        Builder.load_string(KV_LAYOUT)
        return MainWidget()

if __name__ == "__main__":
    SimpleCalcApp().run()