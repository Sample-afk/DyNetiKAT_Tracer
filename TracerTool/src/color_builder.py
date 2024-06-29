class Colors:
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[39m'
    ALL_COLORS = [BLACK, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE]

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_RESET = '\033[49m'
    ALL_BG_COLORS = [BG_BLACK, BG_RED, BG_GREEN, BG_BLUE, BG_YELLOW, BG_MAGENTA, BG_CYAN, BG_WHITE]
    
        
        # '\x1b[37m'
        
        # '\x1b[39m \x1b[49m\ x1b[22m__ \x1b[31m__ \x1b[1m____0____\x1b[39m \x1b[49m \x1b[22m__ \x1b[37m__'

    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    NORMAL_STYLES= [BOLD, DIM]
    
    # Not quite styles
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'
    PROBLEMATIC_STYLES = [ITALIC, UNDERLINE, BLINK, REVERSE, HIDDEN, STRIKETHROUGH]
    
    # Clear codes
    CLEAR_COLOR = '\033[39m'
    CLEAR_BG_COLOR = '\033[49m'
    CLEAR_COLORS = CLEAR_COLOR + CLEAR_BG_COLOR
    CLEAR_STYLE = '\033[22m'
    CLEAR_ALL = '\033[0m'

class ColorBuilder(Colors):
    
    @staticmethod
    def arr_to_str(arr) -> str:
        res = ''
        if arr:
            for s in arr:
                res += s
        return res
    
    def __init__(self, text='', colors=None, styles=None):      
        # GIVE COLORS IN SAME ORDER AS IN __init__ FOR EFFICIENCY 
        self.primary_color = ColorBuilder.arr_to_str(colors) if colors else '' 
        self.primary_style = ColorBuilder.arr_to_str(styles) if styles else ''
        
        self.primary_style_is_problematic = any(style in self.primary_style for style in ColorBuilder.PROBLEMATIC_STYLES)
            
        self.text = self.apply_style(f'{self.primary_color}{self.primary_style}{text}')
        

    def add_line(self, text='', colors=None, styles=None, new_line=False) -> None:
        self.add_text(text, colors, styles, new_line)
        self.text += '\n'
        return self
    
    def add_text(self, text, colors=None, styles=None, new_line=False) -> None:
        formated_txt = self.apply_style(text, colors, styles)
        
        if self.text == self.primary_color or self.text == self.primary_style or self.text == self.primary_color + self.primary_style:
            self.text += formated_txt
        elif new_line:
            self.text += f'\n{formated_txt}'
        else:
            if self.text and self.text.endswith('\n'):
                self.text += formated_txt
            else:
                self.text += f' {formated_txt}'
        return self
    
    def apply_style(self, text, colors=None, styles=None) -> str:
        # GIVE COLORS IN SAME ORDER AS IN __init__ FOR EFFICIENCY 
        txt_col = ColorBuilder.arr_to_str(colors) if colors else self.primary_color
        txt_style = ColorBuilder.arr_to_str(styles) if styles else self.primary_style
        
        beg_clear = ''
        beg_color = ''
        beg_style = ''
        
        end_clear = ''
        end_color = ''
        end_style = ''
        
        custom_color = True if txt_col != self.primary_color else False
        custom_style = True if txt_style != self.primary_style else False
        
        if custom_color:
            beg_clear = ColorBuilder.CLEAR_COLORS
            beg_color = txt_col
            end_clear = ColorBuilder.CLEAR_COLORS
            end_color = self.primary_color
        
        if custom_style:
            beg_style = txt_style
            if self.primary_style_is_problematic:
                beg_clear = ColorBuilder.CLEAR_ALL
                beg_color = self.primary_color if not custom_color else beg_color
            else:
                beg_clear += ColorBuilder.CLEAR_STYLE
            
            current_problematic = any(style in txt_style for style in ColorBuilder.PROBLEMATIC_STYLES)
            if current_problematic:
                end_clear = ColorBuilder.CLEAR_ALL
                end_color = self.primary_color
            else:
                end_clear += ColorBuilder.CLEAR_STYLE
            end_style = self.primary_style
            
        if str(text).endswith(ColorBuilder.CLEAR_ALL):
            end_color += self.primary_color
            end_style += self.primary_style
                              
        
        txt_beg = beg_clear + beg_color + beg_style
        txt_end = end_clear + end_color + end_style
        return f'{txt_beg}{text}{txt_end}'
        
    def get_text_clear_end(self) -> str:
        return self.text + ColorBuilder.CLEAR_ALL
    
    def get_and_reset_text_keep_col(self) -> str:
        t = self.text
        self.text = self.apply_style(f'{self.primary_color}{self.primary_style}')
        return t
        
    def print(self):
        print(self.get_and_reset_text_keep_col())
        
    
    def __str__(self) -> str:
        return self.get_text_clear_end()


class ColorBuildenPlainText(ColorBuilder):
    def __init__(self, text=''):
        super().__init__(text, None, None)
        
    def apply_style(self, text, colors=None, styles=None) -> str:
        return str(text)
    
    def get_text_clear_end(self) -> str:
        return str(self.text)
        

class ColorBuilderNoOutput(ColorBuilder):
    def add_line(self, text='', colors=None, styles=None, new_line=False) -> None:
        pass
    
    def add_text(self, text, colors=None, styles=None, new_line=False) -> None:
        pass
    
    def apply_style(self, text, colors=None, styles=None) -> str:
        return ''
    
    def get_text_clear_end(self) -> str:
        return ''
    
    def get_and_reset_text_keep_col(self) -> str:
        return ''
    
    def print(self):
        pass