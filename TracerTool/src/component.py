import  re
import copy
from .color_builder import Colors, ColorBuilder, ColorBuildenPlainText

class Component:
    MAIN_OUT_COLOR = [Colors.BLUE]
    SHORT_SIZE = 10
    
    def __init__(self, maude, unfold_depth, model_path, name, id, num_of_components, use_color=False):
        self.id = id
        self.maude = maude
        self.unfold_depth = unfold_depth
        self.model_path = model_path
        self.name = name.strip()
        self.v_clock = {i: 0 for i in range(num_of_components)}
        
        # self.must_finish_opt_ids = []
        self.use_color = use_color
        # self.heard_msgs = []
        
        cmd = f'red pi{{{unfold_depth}}}({self.name}).'
        out, err = maude.execute(model_path, cmd)
        if err:
            raise RuntimeError(err)        
        self.expr = out
        self.routes = self.find_routes(self.expr)
        self.next_valid, _ = self.get_valid_options()
        pass
        
    def find_routes(self, expr):
        options = {}
        i = 0
        temp = ""
        depth = 0
        parts = re.split(r'o\+', expr)
        # parts = re.split(r'\s+o\+\s+(?![^()]*\))', expr)
        for part in parts:
            part = part.strip()
            # print(part)
            ob = part.count('(')
            cb = part.count(')')
            diff = ob - cb
            # print(f"(: {ob};\n): {cb};\ndiff: {diff}")
            
            if not ob == cb or depth > 0:
                temp += (' o+ ' if temp else '') + part
                depth += diff
            elif ob == cb and depth == 0:
                temp = part
            
            if depth == 0:
                options[i] = temp
                i += 1
                temp = ""
                
            # # ------------------------------------------------------------------------
            # if diff == 0:
            #     if depth1 == 0:
            #         options.append(part)
            #         temp1 = ""
            #     else:
            #         temp1 += (' o+ ' if temp1 else '') + part
            # elif ob > cb:
            #     temp1 += (' o+ ' if temp1 else '') + part
            #     depth1 += diff
            # elif cb > ob:
            #     temp1 += (' o+ ' if temp1 else '') + part
            #     depth1 += diff
                
            # print()
            pass
        # print()
        return options
    
    def update_valid_options(self, meta=None):
        # heard_size = -1
        # if meta is not None:
        #     # self.heard_msgs.append(meta)
        #     heard_size = len(self.heard_msgs)
        self.next_valid, receive_opts_ids = self.get_valid_options(meta)
        # if len(receive_opts_ids) > 0:
        #     print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        #     print(self)
        #     print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        #     pass
        return receive_opts_ids
            # self.next_valid, msg_id = self.get_valid_options(meta)
            # print(self)
            # self.
    
    def get_valid_options(self, meta=None):
        valid = {}
        # key_to_del = set()    
        receive_msgs_keys = []
        
        # if len(self.must_finish_opt_ids) != 0:
        #     routes_to_check = {}
        #     for key, opt in self.routes.items():
        #         if key in self.must_finish_opt_ids:
        #             routes_to_check[key] = self.routes[key]
        #     if all(value == 'bot' for value in routes_to_check):
        #         routes_to_check = self.routes
        # else:
        #     routes_to_check = self.routes
        routes_to_check = self.routes
        
        for key, opt in routes_to_check.items():
            term = opt.split(';')[0].strip()
            rest = ';'.join(opt.split(';')[1:]).strip()
            if 'o+' in rest and term.count('(') > term.count(')'):
                exp = opt.strip()
                if exp.startswith('(') and exp.endswith(')'):
                    exp = exp[1:-1].strip()
                additional_routes = self.find_routes(exp)
                self.routes = additional_routes
                # self.update_valid_options()
                return self.get_valid_options()
                
            # print(f't: {term}\nr: {rest}\n')                
            
            if rest.endswith(')') and term.startswith('('):
                ob_term = term.count('(')
                cb_term = term.count(')')
                if ob_term > cb_term:
                    term = term[1:].strip()
                    rest = rest[:-1].strip()
                    # print(f'UPDATED:\nt: {term}\nr: {rest}\n')
            
            if term.startswith('\"') and term.endswith('\"'):
                valid[key] = (term, rest)
                
            elif term.startswith('(') and term.endswith(')') and '!' in term:
                term = term[1:-1]
                arr = term.split('!')
                if len(arr) != 2:
                    raise RuntimeError(f'Component {self.name} had issues with reading this as send {term}')
                valid[key] = (term, rest)
                
            elif term == 'bot' and len(rest) == 0:
                continue
                
            # elif term.startswith('(') and term.endswith(')') and '?' in term and len(self.heard_msgs) != 0:
            elif meta is not None:
                sender_id = meta[0][0]
                sender_clk = meta[0][1]
                received_msg = meta[1]
                
                term = term[1:-1]
                arr = term.split('?')
                if len(arr) != 2:
                    raise RuntimeError(f'Component {self.name} had issues with reading this as receive {term}')
                expected_msg = (arr[0].strip(), arr[1].strip())
                
                if expected_msg == received_msg:
                    valid[key] = (term, (meta, rest))
                    receive_msgs_keys.append(key)
            
                # index_to_remove = None
                # for i, (meta, msg) in enumerate(self.heard_msgs):
                #     if expected_msg == msg:
                #         valid[key] = (term, (meta, rest))
                #         index_to_remove = i
                #         msg_key = key
                #         break
                # if isinstance(index_to_remove, int):
                #     del self.heard_msgs[i]
                pass
                
                
                
            # if used_channel:
            #     if term.startswith('(') and term.endswith(')') and '?' in term:
            #         term = term[1:-1]
            #         arr = term.split('?')
            #         if len(arr) != 2:
            #             raise RuntimeError(f'Component {self.name} had issues with reading this as send {term}')
            #         expected_chn = arr[0].strip()
            #         expected_msg = arr[1].strip()
            #         used_channel = used_channel.strip()
            #         sent_msg = sent_msg.strip()
            #         if used_channel == expected_chn and sent_msg == expected_msg:
            #             if not meta:
            #                 raise RuntimeError(f'Component {self.name} had issues with reading this as send {term} because id & clock were {meta}')
            #             valid[key] = (term, (meta, rest))
            #             print(valid[key])
            
        # for k in key_to_del:
        #     del self.routes[k]
        # print(f'\nValid routes for \'{self.name}\' (ch: \'{used_channel}\'; msg:\'{sent_msg}\'):')
        # for k, v in valid.items():
        #     # print(f'{k}) {Component.format_expression(v)}')
        #     e = v[1][1] if isinstance(v[1], tuple) else v[1]
        #     print(f'{k}) {v[0]}\n{Component.format_expression(e)}')
        return valid, receive_msgs_keys
    
    def clone(self):
        return copy.deepcopy(self)
    
    def take_step_by_opt_id(self, opt_id):
        term = self.next_valid[opt_id][0]
        rest = self.next_valid[opt_id][1]
        # print('COMPLETE TRANSFER')
        # print(f'\nbef: {self}')
        clone, taken_step, sending = self.take_step(opt_id, term, rest)
        # print(f'\naft: {clone}')
        # print('*+*++*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*++*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+')
        pass
        return clone, taken_step, sending
    
    def take_step(self, key, term, rest):
        # print(self)
        clone = self.clone()
        
        
        clone.routes = {key: rest}
        # if rest != 'bot':
        #     clone.routes = {key: rest}
        # else:
        #     clone.routes[key] = rest
        
        
        # clone.must_finish_opt_ids.append(key)
        sending = None
        # print(clone)
        if term.startswith('\"') and term.endswith('\"'):
            clone.v_clock[clone.id] += 1
            # clone.next_valid = clone.get_valid_options()
            clone.update_valid_options()
        elif '!' in term:
            clone.v_clock[clone.id] += 1
            arr = term.split('!')
            chn = arr[0].strip()
            msg = arr[1].strip()
            sending = (chn, msg)
            # clone.next_valid = clone.get_valid_options()
            clone.update_valid_options()
        elif '?' in term:
            clone.v_clock[clone.id] += 1
            meta, actual_rest = rest
            sender_info = meta[0]
            received_msg = meta[1]
            sender_id, sender_clk, sender_name = sender_info
            clone.v_clock[sender_id] = sender_clk[sender_id]
            clone.routes[key] = actual_rest
            clone.update_valid_options()
        else:
            pass
        taken_step = term
        # print(clone)
        return clone, taken_step, sending
    
    def get_builder(self, text='', colors=None, styles=None):
        if self.use_color:
            builder = ColorBuilder(str(text), colors, styles)
        else:
            builder = ColorBuildenPlainText(str(text))
        return builder
    
    def name_clock_str(self):
        t = self.get_builder('', [Colors.WHITE], [Colors.DIM])
        full_clock = self.color_clock(t)
        name = t.apply_style(self.name, styles=[Colors.CLEAR_STYLE])
        # full_clock = t.apply_style(f'[{full_clock}]', styles=[Colors.DIM])
        t.add_text(f'{name}[{full_clock}]')
        return t.get_text_clear_end()
        # t.add_text
        
    def color_clock(self, builder=None):        
        if builder is None:
            builder = self.get_builder('', [Colors.WHITE], [Colors.DIM])
            
        style = builder.primary_style
            
        my_clock = builder.apply_style(self.v_clock[self.id], [Colors.RED], [Colors.BOLD])
        full_clock = ", ".join([f"{my_clock}{style}" if key == self.id else str(value) for key, value in self.v_clock.items()])
        # full_clock = builder.apply_style(full_clock, styles=[Colors.DIM])
        return full_clock
    
    def format_full_expression(self, expr):
        DELIM_1 = '; ('
        DELIM_2 = 'o+'
        DELIM_3 = 'bot)'
        
        def choose_ind(d1, d2, d3):
            fail1 = True if d1 == -1 else False
            fail2 = True if d2 == -1 else False
            fail3 = True if d3 == -1 else False
            
            if fail1 and fail2 and fail3:
                return -1, None
            
            if fail2 and fail3:
                return d1, DELIM_1
            if fail1 and fail3:
                return d2, DELIM_2
            if fail1 and fail2:
                return d3, DELIM_3
            
            if not fail1 and not fail2 and not fail3:
                minimum = min(min(d1, d2), d3)
            elif fail1:
                minimum = min(d2, d3)
            elif fail2:
                minimum = min(d1, d3)
            elif fail3:
                minimum = min(d1, d2)
                
            if minimum == d1:
                return d1, DELIM_1
            elif minimum == d2:
                return d2, DELIM_2
            elif minimum == d3:
                return d3, DELIM_3
            
            return -1, None
            
        def find_index(ind, start):
            return expr.find(ind, start)
            
        start = 0
        indent = 0
        formatted_expr = ''
        
        ind1 = find_index(DELIM_1, start)
        ind2 = find_index(DELIM_2, start)
        ind3 = find_index(DELIM_3, start)
        if ind1 == -1 and ind2 == -1:
            return expr
        
        if expr.startswith('( ') or expr.startswith('(('):
            formatted_expr = '(\n'
            indent += 1
            start += 1
        
        while start < len(expr):
            cur_ind, cur_del = choose_ind(ind1, ind2, ind3)
            if cur_ind == -1:
                formatted_expr += expr[start:].strip()
                break
            tabs = '\t' * indent
            upto = cur_ind
            if cur_del == DELIM_1:
                upto += 1
            elif cur_del == DELIM_3:
                upto += 3
                
            expr_part = expr[start:upto].strip()
            formatted_expr += f'{tabs}{expr_part}\n'
            # print(formatted_expr)
            # print()
            start = cur_ind + len(cur_del)
            
            if cur_del == DELIM_1:
                ind1 = find_index(DELIM_1, start)
                formatted_expr += f'{tabs}(\n'
                indent += 1
            elif cur_del == DELIM_2:
                ind2 = find_index(DELIM_2, start)
                temp = f'{tabs}o+\n'
                # if indent == 0:
                #     temp = f"\n{temp}\n"
                formatted_expr += temp
            elif cur_del == DELIM_3:
                ind3 = find_index(DELIM_3, start)
                rest = expr[upto:]
                while rest.startswith(')'):
                    indent -= 1
                    tabs = '\t' * indent
                    formatted_expr += f'{tabs})\n'
                    rest = rest[1:]
                    start += 1
                formatted_expr = formatted_expr[:-1]
        return formatted_expr.strip()
    
    def format_expression(self, builder, expr, rest_len=-1):
        if rest_len == -1:
            formatted_expr = self.format_full_expression(expr)
            if self.use_color:
                formatted_expr = self.mark_ops(formatted_expr)
        else:
            arr = expr.split(';')
            term = arr[0]
            term_txt = f'{term};'
            if len(arr) > 1:
                if arr[1].strip() == 'bot':
                    formatted_expr = f'{term_txt} {arr[1]}'
                else:
                    term_len = len(term) + 2
                    rest_txt = f'{expr[term_len:term_len + rest_len]}'
                    rest_txt = builder.apply_style(rest_txt, styles=[Colors.DIM])
                        
                    formatted_expr = f'{term_txt} {rest_txt}...'
        return formatted_expr
    
    def basic_info(self, builder=None) -> str:
        isolated = False
        if builder is None:
            builder = self.get_builder('', self.MAIN_OUT_COLOR)
            isolated = True
            
        name = builder.apply_style(self.name, [Colors.GREEN])
        builder.add_text(f'Component: {name}', styles=[Colors.BOLD])
        
        id = builder.apply_style(self.id, [Colors.RED], [Colors.BOLD])
        builder.add_text(f'\t(id: {id})')
        
        builder.add_text("\nClock:", styles=[Colors.BOLD])
        full_clock = self.color_clock(builder)
        builder.add_text(full_clock)
        if isolated:
            return str(builder.get_text_clear_end())
        return "\'basic_info\' SHOULD NOT BE RETURNING (provided builder)"
    
    def mark_ops(self, exp):
        if True:
            exp = f'{Colors.BG_YELLOW};{Colors.CLEAR_BG_COLOR}'.join(exp.split(';'))
            exp = f'{Colors.BG_CYAN}o+{Colors.CLEAR_BG_COLOR}'.join(exp.split('o+'))
        return exp   
    
    def formatted_expr(self, builder=None, rest_len=-1) -> str:
        isolated = False
        if builder is None:
            builder = self.get_builder('', self.MAIN_OUT_COLOR)
            isolated = True
            
        formatted_expr = self.format_expression(builder, self.expr, rest_len)
            
        if isolated:
            builder.add_text(formatted_expr)
            return str(builder.get_text_clear_end())
        return formatted_expr
    
    def formatted_options(self, builder=None, rest_len=-1) -> str:
        isolated = False
        if builder is None:
            builder = self.get_builder('', self.MAIN_OUT_COLOR)
            isolated = True
            
        for key, val in self.routes.items():
            ob = val.count('(')
            cb = val.count(')')
            
            e = val[1] if isinstance(val, tuple) else val
            e = self.format_expression(builder, e, rest_len)
            if self.use_color:
                e = self.mark_ops(e)
            stl = Colors.BOLD if key in self.next_valid.keys() else Colors.DIM
            val_txt = builder.apply_style(e, styles=[stl])
            
            builder.add_text(f'{builder.apply_style(f"[{ob - cb}] {key}", [Colors.GREEN], [Colors.BOLD])}\n{val_txt}\n')
            
        if isolated:
            return str(builder.get_text_clear_end())
        return ''
        
    def to_str(self, show_expr=False, show_opts=False, rest_len=-1) -> str:
        builder = self.get_builder('', self.MAIN_OUT_COLOR)
        self.basic_info(builder)
        
        if show_expr:
            builder.add_line("\nExpr:", styles=[Colors.BOLD])
            builder.add_line(self.formatted_expr(builder, rest_len), [Colors.MAGENTA])
            
        if show_opts:
            builder.add_line("Options:", styles=[Colors.BOLD])
            self.formatted_options(builder, rest_len)
            
            
        return builder.get_text_clear_end()
    
    def to_full_str(self, rest_len=-1) -> str:
        return str(self.to_str(show_expr=True, show_opts=True, rest_len=rest_len))
    
    # def to_str_full_old(self) -> str:
    #     def mark_ops(exp):
    #         if True:
    #             exp = f'{Colors.BG_YELLOW};{Colors.CLEAR_BG_COLOR}'.join(exp.split(';'))
    #             exp = f'{Colors.BG_CYAN}o+{Colors.CLEAR_BG_COLOR}'.join(exp.split('o+'))
    #         return exp        
        
        
    #     t = ColorBuilder('', colors=[Colors.BLUE])
    #     name = t.apply_style(self.name, [Colors.GREEN])
    #     t.add_text(f'Component: {name}', styles=[Colors.BOLD])
        
    #     id = t.apply_style(self.id, [Colors.RED], [Colors.BOLD])
    #     t.add_text(f'\t(id: {id})')
        
    #     t.add_text("\nClock:", styles=[Colors.BOLD])
    #     # my_clock = t.apply_style(self.v_clock[self.id], [CB.RED], [CB.BOLD])
    #     # full_clock = ", ".join([f"{my_clock}" if key == self.id else str(value) for key, value in self.v_clock.items()])
    #     full_clock = self.color_clock(t)
    #     t.add_text(full_clock)
        
    #     t.add_text("\nExpr:", styles=[Colors.BOLD])
    #     formatted_expr = self.format_full_expression(self.expr)
    #     expr = t.apply_style(formatted_expr, [Colors.MAGENTA])
    #     expr = mark_ops(expr)
    #     t.add_text(f'\n{expr}')
        
    #     t.add_text("\nOptions:\n", styles=[Colors.BOLD])
    #     for key, val in self.routes.items():
    #         ob = val.count('(')
    #         cb = val.count(')')
            
    #         e = val[1] if isinstance(val, tuple) else val
    #         val_marked = mark_ops(self.format_full_expression(e))
    #         stl = Colors.BOLD if key in self.next_valid.keys() else Colors.DIM
    #         val_txt = t.apply_style(val_marked, styles=[stl])
            
    #         t.add_text(f'{t.apply_style(f"[{ob - cb}] {key}", [Colors.GREEN], [Colors.BOLD])}\n{val_txt}\n')
        
    #     # t.add_text('\n')
    #     return t.get_text_clear_end()
        
    
    def __str__(self):
        return self.name_clock_str()
