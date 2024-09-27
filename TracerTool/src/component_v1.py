import  re
import copy
from .color_builder import Colors, ColorBuilder, ColorBuildenPlainText
import numpy as np
from enum import Enum, auto

class Component:
    class CompType(Enum):
        CONTROLLER = auto()
        SWITCH = auto()
    
    MAIN_OUT_COLOR = [Colors.BLUE]
    SHORT_SIZE = 10
    
    def __init__(self, name, expr, id, num_of_components, use_color=False):
        self.id = id
        self.name = str(name)
        # self.v_clock = {i: 0 for i in range(num_of_components)}
        self.v_clock = np.zeros(num_of_components, dtype=int)
        
        if name.startswith("C"):
            self.type = Component.CompType.CONTROLLER
        else:
            self.type = Component.CompType.SWITCH
        
        self.use_color = use_color
        self.expr = expr
        
        self.full_text_representation = None
        self.had_change = False
        self.routes = self.find_routes(self.expr)
        self.next_valid, _ = self.get_valid_options()
        pass

    def clone(self):
        return copy.deepcopy(self)

    def clone_new_id(self, new_id):
        new_obj = copy.deepcopy(self)
        new_obj.id = new_id
        return new_obj

    # find possible execution branches
    def find_routes(self, expr):
        options = {}
        i = 0
        temp = ""
        depth = 0
        # split expression bt the 'o+'
        parts = re.split(r'o\+', expr)
        for part in parts:
            part = part.strip()
            ob = part.count('(')
            cb = part.count(')')
            diff = ob - cb
            # if the amount of brackets is different that meanse the 'o+' is part of the inner expression
            # and not on the top, so we same that part to temp
            
            if not ob == cb or depth > 0:
                temp += (' o+ ' if temp else '') + part
                depth += diff
            elif ob == cb and depth == 0:
                temp = part
            
            # when the depth is 0, one possible execution branch is found
            if depth == 0:
                options[i] = temp
                i += 1
                temp = ""
        return options
    
    # update brach validity based on received message (meta)
    def update_valid_options(self, meta=None):
        self.next_valid, receive_opts_ids = self.get_valid_options(meta)
        return receive_opts_ids
    
    # check brach execution for validity (wheter it can execute)
    def get_valid_options(self, meta=None):
        valid = {}
        
        routes_to_check = self.routes
        receive_msgs_keys = []
        
        for key, opt in routes_to_check.items():
            term = opt.split(';')[0].strip()
            rest = ';'.join(opt.split(';')[1:]).strip()
            # if the route contains branching (o+), and the term (part before ';') is not self contained,
            # meaning uneven number of brackets, we have reached the branching point
            if 'o+' in rest and term.count('(') > term.count(')'):
                exp = opt.strip()
                if exp.startswith('(') and exp.endswith(')'):
                    exp = exp[1:-1].strip()
                additional_routes = self.find_routes(exp)
                self.routes = additional_routes
                return self.get_valid_options()
                             
            # exctract the full expression (term + rest) if it is in brackets
            if rest.endswith(')') and term.startswith('('):
                ob_term = term.count('(')
                cb_term = term.count(')')
                if ob_term > cb_term:
                    term = term[1:].strip()
                    rest = rest[:-1].strip()
            
            # term is a packet manipulation
            if term.startswith('\"') and term.endswith('\"'):
                valid[key] = (term, rest)
                
            # term is a communication initiation
            elif term.startswith('(') and term.endswith(')') and '!' in term:
                term = term[1:-1]
                arr = term.split('!')
                if len(arr) != 2:
                    raise RuntimeError(f'Component {self.name} had issues with reading this as send {term}')
                valid[key] = (term, rest)
                
            # the execution branch is over
            elif term == 'bot' and len(rest) == 0:
                continue
                
            # term is a communication receiving
            elif meta is not None:
                # sender_id = meta[0][0]
                # sender_clk = meta[0][1]
                received_msg = meta[1]
                
                # such term will always be in brackets
                term = term[1:-1]
                arr = term.split('?')
                if len(arr) != 2:
                    raise RuntimeError(f'Component {self.name} had issues with reading this as receive {term}')
                expected_msg = (arr[0].strip(), arr[1].strip())
                
                if expected_msg == received_msg:
                    valid[key] = (term, (meta, rest))
                    receive_msgs_keys.append(key)
            
        return valid, receive_msgs_keys

    # take step by opt id
    def take_step_by_id(self, opt_id):
        term = self.next_valid[opt_id][0]
        rest = self.next_valid[opt_id][1]
        clone, taken_step, sending = self.take_step(opt_id, term, rest)
        pass
        return clone, taken_step, sending
    
    # take step parameterized
    def take_step(self, key, term, rest):
        def update_clock_receive(sender_clk, component_clk):
            n = np.where(sender_clk > component_clk, sender_clk, component_clk)
            return n
        
        clone = self.clone()
        clone.routes = {key: rest}
        
        sending = None
        
        # packet manipulation
        if term.startswith('\"') and term.endswith('\"'):
            clone.v_clock[clone.id] += 1
            clone.update_valid_options()
            
        # communication initiation
        elif '!' in term:
            clone.v_clock[clone.id] += 1
            arr = term.split('!')
            chn = arr[0].strip()
            msg = arr[1].strip()
            sending = (chn, msg)
            clone.update_valid_options()
            
        # communication receiving
        elif '?' in term:
            meta, actual_rest = rest
            sender_info = meta[0]
            received_msg = meta[1]
            sender_id, sender_clk, sender_name = sender_info
            clone.v_clock = update_clock_receive(sender_clk, clone.v_clock)
            clone.v_clock[clone.id] += 1
            clone.routes[key] = actual_rest
            clone.update_valid_options()
            
        else:
            raise RuntimeError(f'component {self.name} (id:{self.id}) could not determine what to do with term {term} while taking a step')
        taken_step = term
        return clone, taken_step, sending
        

# ==================================================================================================    
# String methods
    # short string
    def name_clock_str(self):
        t = self.get_builder('', [Colors.WHITE], [Colors.DIM])
        full_clock = self.color_clock(t)
        name = t.apply_style(self.name, styles=[Colors.CLEAR_STYLE])
        t.add_text(f'{name}[{full_clock}]')
        return t.get_text_clear_end()
      
    # long string (name, id, clock, expression(?), options(?))
    def to_str(self, show_expr=False, show_opts=False, rest_len=-1) -> str:
        if self.had_change or self.full_text_representation is None:
            builder = self.get_builder('', self.MAIN_OUT_COLOR)
            self.basic_info(builder)
            
            if show_expr:
                builder.add_line("\nExpr:", styles=[Colors.BOLD])
                builder.add_line(self.format_expression(builder, self.expr, rest_len), [Colors.MAGENTA])
                
            if show_opts:
                builder.add_line("Options:", styles=[Colors.BOLD])
                self.format_options(builder, rest_len)
            
            self.full_text_representation = builder.get_text_clear_end()
            self.had_change = False
            
        return self.full_text_representation
    
    # shortcut to full long string
    def to_full_str(self, rest_len=-1) -> str:
        return str(self.to_str(show_expr=True, show_opts=True, rest_len=rest_len))

 
# ==================================================================================================      
# String helpers
    # retrieve current builder (to print in same style)
    def get_builder(self, text='', colors=None, styles=None):
        if self.use_color:
            builder = ColorBuilder(str(text), colors, styles)
        else:
            builder = ColorBuildenPlainText(str(text))
        return builder
    
    # get colored vector clock
    def color_clock(self, builder=None):        
        if builder is None:
            builder = self.get_builder('', [Colors.WHITE], [Colors.DIM])
            
        style = builder.primary_style
            
        my_clock = builder.apply_style(self.v_clock[self.id], [Colors.RED], [Colors.BOLD])
        full_clock = ", ".join([f"{my_clock}{style}" if key == self.id else str(value) for key, value in enumerate(self.v_clock)])
        return full_clock
    
    # color ';' and 'o+'
    def mark_ops(self, exp):
        if True:
            exp = f'{Colors.BG_YELLOW};{Colors.CLEAR_BG_COLOR}'.join(exp.split(';'))
            exp = f'{Colors.BG_CYAN}o+{Colors.CLEAR_BG_COLOR}'.join(exp.split('o+'))
        return exp   
    
    # component's basic information (name, id, clock)
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
        pass
    
    # same as with expression before, but for formattedoptions
    def format_options(self, builder=None, rest_len=-1) -> str:
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
        pass
    
    # get full of shortened expression if rest_len is set to positive number
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
    
    # get full formated expression
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
    
    def __str__(self):
        return self.name_clock_str()