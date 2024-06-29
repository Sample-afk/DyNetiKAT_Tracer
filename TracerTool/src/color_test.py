from color_builder import ColorBuilder

class TestColorBuilder():

    def test_example_0(self):
        print()
        builder = ColorBuilder("START")
        builder.add_text('bold', styles=[ColorBuilder.BOLD])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        builder = ColorBuilder("START", styles=[ColorBuilder.BOLD])
        builder.add_text('clear', styles=[ColorBuilder.CLEAR_STYLE])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        print()

    def test_example_1(self):
        print()
        builder = ColorBuilder("START")
        builder.add_text('red', colors=[ColorBuilder.RED])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        builder = ColorBuilder("START", colors=[ColorBuilder.RED])
        builder.add_text('clear', colors=[ColorBuilder.CLEAR_COLOR])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        print()

    def test_example_2(self):
        builder = ColorBuilder("START", colors=[ColorBuilder.BG_BLUE])
        builder.add_text('clear_bg', colors=[ColorBuilder.CLEAR_BG_COLOR])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        builder = ColorBuilder("START")
        builder.add_text('blue_bg', colors=[ColorBuilder.BG_BLUE])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        print()
        
    def test_example_3(self):
        builder = ColorBuilder("START", colors=[ColorBuilder.BG_CYAN])
        builder.add_text('added', colors=[ColorBuilder.CYAN])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        builder = ColorBuilder("START", colors=[ColorBuilder.CYAN])
        builder.add_text('added', colors=[ColorBuilder.BG_CYAN])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        print()
        
    def test_example_4(self):
        builder = ColorBuilder("START", colors=[ColorBuilder.BLUE])
        builder.add_text('added', styles=[ColorBuilder.BOLD])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        builder = ColorBuilder("START", colors=[ColorBuilder.BLUE], styles=[ColorBuilder.BOLD])
        builder.add_text('added', styles=[ColorBuilder.CLEAR_STYLE])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        print()
        
    def test_example_5(self):
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_bold", styles=[ColorBuilder.BOLD])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\t\tC_bold", colors=[ColorBuilder.BOLD])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN], styles=[ColorBuilder.ITALIC])
        builder.add_text("S_DIM", styles=[ColorBuilder.DIM])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\t\tC_DIM", colors=[ColorBuilder.DIM])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_DIM", styles=[ColorBuilder.DIM])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\t\tC_DIM", colors=[ColorBuilder.DIM])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_ITALIC", styles=[ColorBuilder.ITALIC])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\t\tC_ITALIC", colors=[ColorBuilder.ITALIC])
        builder.add_text("FINISH")
        a = builder.get_text_clear_end()
        print(a)
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN], styles=[ColorBuilder.BOLD])
        builder.add_text("S_ITALIC", styles=[ColorBuilder.ITALIC])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\t\tC_ITALIC", colors=[ColorBuilder.ITALIC])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        pass
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_UNDERLINE", styles=[ColorBuilder.UNDERLINE])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\tC_UNDERLINE", colors=[ColorBuilder.UNDERLINE])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_BLINK", styles=[ColorBuilder.BLINK])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\t\tC_BLINK", colors=[ColorBuilder.BLINK])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_REVERSE", styles=[ColorBuilder.REVERSE])
        builder.add_text("PLAIN")
        builder.add_text("S_REVERSE_again", styles=[ColorBuilder.REVERSE])
        builder.add_text("PLAIN")
        builder.add_text("\tC_REVERSE", colors=[ColorBuilder.REVERSE])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_HIDDEN", styles=[ColorBuilder.HIDDEN])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\t\tC_HIDDEN", colors=[ColorBuilder.HIDDEN])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_STRIKETHROUGH", styles=[ColorBuilder.STRIKETHROUGH])
        builder.add_text("PLAIN")
        builder.add_text("\t\t\tC_STRIKETHROUGH", colors=[ColorBuilder.STRIKETHROUGH])
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.GREEN])
        builder.add_text("S_STRIKETHROUGH", colors=[ColorBuilder.RED], styles=[ColorBuilder.STRIKETHROUGH])
        builder.add_text("PLAIN")
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        
        builder = ColorBuilder("START", colors=[ColorBuilder.BG_GREEN])
        builder.add_text("S_STRIKETHROUGH", colors=[ColorBuilder.RED], styles=[ColorBuilder.STRIKETHROUGH])
        builder.add_text("PLAIN")
        builder.add_text("FINISH")
        print(builder.get_text_clear_end())
        print()

    def test_example_6(self):
        COLOR_NAMES = ['BLACK\t\t', 'RED\t\t', 'GREEN\t\t', 
                       'BLUE\t\t', 'YELLOW\t\t', 
                       'MAGENTA\t\t', 'CYAN\t\t', 'WHITE\t\t']
        STYLES = ColorBuilder.NORMAL_STYLES
        builder = ColorBuilder("Colors:\n")
        builder.add_text('PLAIN\t\t')
        builder.add_text('BOLD\t\t', styles=[ColorBuilder.BOLD])
        builder.add_text('DIM\t\t', styles=[ColorBuilder.DIM])
        builder.add_line('BOTH\t\t', styles=STYLES)
        
        def prt_combo(name, color, bg=False):
            name = f'bg_{name[:-1]}' if bg or name.startswith('MAGENTA') else name
            name = f'{name}\t' if name.startswith('bg_RED') else name
            builder.add_text(f'{name}', [color])
            for st in STYLES:
                builder.add_text(f'{name}', [color], [st])
            builder.add_line(f'{name}', [color], STYLES)
            
        
        for c, bg_c, name in zip(ColorBuilder.ALL_COLORS, ColorBuilder.ALL_BG_COLORS, COLOR_NAMES):
            prt_combo(name, c)
            prt_combo(name, bg_c, True)
        builder.add_text("FINISH", new_line=True)
        print(builder.get_text_clear_end())
        print()

if __name__ == '__main__':
    t = TestColorBuilder()
    t.test_example_0()
    t.test_example_1()
    t.test_example_2()
    t.test_example_3()
    t.test_example_4()
    t.test_example_5()
    t.test_example_6()
    pass