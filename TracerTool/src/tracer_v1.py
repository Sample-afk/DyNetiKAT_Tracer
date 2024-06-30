from .color_builder import Colors, ColorBuilder, ColorBuildenPlainText, ColorBuilderNoOutput
from collections import deque
import os

import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout


class TracerTool:
    next_node_id = 0
    START_NODE_COL = 'lightgreen'
    REGULAR_NODE_COL = 'skyblue'
    RACE_CONDITION_COL = 'lightcoral'
    RCFG_NODE_COL = 'moccasin'
    TEXT_SEPARATOR = '@_@'
    
    class GraphInfo:
        def __init__(self, G, node_names, node_colors, edge_names, ratio_dict=None) -> None:
            self.graph = G
            self.node_names = node_names
            self.node_colors = node_colors
            self.edge_names = edge_names
            self.ratio_dict = ratio_dict
    
    class Step:
        def __init__(self, performer, step, receiver=None) -> None:
            self.performer = performer
            self.taken_step = step
            self.receiver = receiver
            
        def __str__(self) -> str:
            rec = f' -> {self.receiver.name}' if self.receiver is not None else ''
            s = f'[{self.performer.name}{rec}] {self.taken_step}'
            return s
    
    class Node:
        def __init__(self, components, parent=None, prev_step='', level=1, use_color=False) -> None:
            self.parent = parent
            self.level = level
            self.use_color = use_color
            
            id = TracerTool.next_node_id
            TracerTool.next_node_id += 1            
            self.id = id
            self.color = TracerTool.REGULAR_NODE_COL
            
            self.main_components = components
            self.children = {}
            
            if self.parent is None:
                trace_txt = ''
            else:
                trace_txt = prev_step if parent.prev_steps_txt == '' else f'{parent.prev_steps_txt} ; {prev_step}'
            self.prev_steps_txt = trace_txt
            
        def generate_children(self):
            res = {}
            
            for comp_id, component in self.main_components.items():
                for key, (term, rest) in component.next_valid.items():
                    clone, step, sending = component.take_step(key, term, rest)
                    new_childred = self.generate_child(clone, step, sending)
                    for new_child, step_obj in new_childred:
                        res[new_child] = step_obj
            
            self.children = res
            pass
        
        def generate_child(self, performer, step, sending):
            new_components = self.main_components.copy()
            id = performer.id
            new_components[id] = performer
            
            if sending:
                res = []
                meta = ((performer.id, performer.v_clock, performer.name), sending)
                
                for id, comp in new_components.items():
                    if comp is not performer:
                        # Because we can't revert a component, to check validity we need to clone and then check
                        possible_receiver = comp.clone()
                        receive_options = possible_receiver.update_valid_options(meta)
                        
                        # If at least one option is to receive msg in question
                        if len(receive_options) > 0:                            
                            for receive_key in receive_options:
                                # Create a copy of new components, in case multiple components can receive the message
                                local_new_componetns = new_components.copy()
                                receiver, step_receive, sending_receive = possible_receiver.take_step_by_opt_id(receive_key)
                                
                                local_new_componetns[id] = receiver
                                rcfg_step = f'rcfg{sending}'
                                child = TracerTool.Node(local_new_componetns, self, rcfg_step, self.level + 1, self.use_color)
                                step_obj = TracerTool.Step(performer, rcfg_step, receiver)
                                child.color = TracerTool.RCFG_NODE_COL
                                res.append((child, step_obj))
                return res
            else:
                child = TracerTool.Node(new_components, self, step, self.level + 1, self.use_color)
                step_obj = TracerTool.Step(performer, step)
                return [(child, step_obj)]
            
        def more_info(self, checked=[], show_components=False, current=None):
            # t = Colors('', [Colors.CYAN])
            if self.use_color:
                builder = ColorBuilder('', [Colors.CYAN])
            else:
                builder = ColorBuildenPlainText('')
            builder.add_text(f'Node ({self.id}):\t')
            builder.add_line(self.convert_to_str(color=True))
            builder.add_text("Trace:\t")
            builder.add_line(self.prev_steps_txt, styles=[Colors.BOLD])
            builder.add_line("Possible steps:")
            strings = []
            step_max_len = -1
            colors = Colors.ALL_COLORS[1:]
            for i, (node, step_obj) in enumerate(self.children.items()):
                col = colors[i % len(colors)]
                style = [Colors.UNDERLINE] if node is current else []
                if i in checked:
                    style.append(Colors.STRIKETHROUGH)
                # if not style:
                #     style = style2
                
                step_txt = builder.apply_style(f'{i}) {builder.apply_style(step_obj, styles=style)}    ', col)
                step_txt_len = len(f'{i}) {step_obj}    ')
                step_max_len = step_txt_len if step_txt_len > step_max_len else step_max_len
                
                # print(step_txt)
                
                meta = (step_txt, node, col)
                strings.append(meta)
                # t.add_line(f'{step_txt}\t\t-->\t{node}', styles=style)
                
            for step_txt, node, col in strings:
                padding_len = step_max_len - len(step_txt)
                padded_text = f'{step_txt}{" " * padding_len}-->\t{node.convert_to_str(color=True)} (id: {node.id})'
                builder.add_text(padded_text, [Colors.WHITE])
                builder.add_line()
                # print(t.get_text())
                
            if show_components:
                builder.add_line()
                builder.add_line('Current components:')
                for i, c in self.main_components.items():
                    if i > 0:
                        builder.add_line('*/*/*/*/*/*/*/*/*/*/*/*/')
                    builder.add_line(c)
            # t.print()
            return builder.get_text_clear_end()
        
        def convert_to_str(self, color=False) -> str:
            temp = []
            for id, c in self.main_components.items():
                if color:
                    s = c.name_clock_str()
                else:
                    s = f'{c.name}{list(c.v_clock.values())}'
                temp.append(s)
            s = ' || '.join(temp)
            return s
        
        def __str__(self) -> str:
            return self.convert_to_str()
    
    def __init__(self, components, output_folder='', show_steps=False, use_color=False) -> None:
        self.prog_to_trace = components
        self.output_folder = output_folder
        self.show_steps = show_steps
        self.use_color = use_color
        self.last_traces = None
        
    def get_builder(self, text='', colors=None, styles=None):
        if self.show_steps:
            if self.use_color:
                builder = ColorBuilder(str(text), colors, styles)
            else:
                builder = ColorBuildenPlainText(str(text))
        else:
            builder = ColorBuilderNoOutput(text, colors, styles)
        return builder
        
    def create_start_node(self):
        self.next_node_id = 0
        TracerTool.next_node_id = 0
        start_node = self.Node(self.prog_to_trace, use_color=self.use_color)
        start_node.color = self.START_NODE_COL
        self.start_node = start_node
        
    def format_traces(self, color_builder=None, long=False, color=True):
        if self.last_traces is None:
            return 'Call \'TracerTool.call_trace()\' first'
        
        res = []
        # t = self.get_builder('')
        # t = copy.deepcopy(color_builder)
        if self.use_color:
            t = ColorBuilder()
        else:
            t = ColorBuildenPlainText()
            
        for last_node, traces in self.last_traces:
            short_trc, long_trc = traces
            trace = long_trc if long else short_trc
            s = self.format_trace(trace, long, color)
            res.append(s)
            pass
            
        for i, trc in enumerate(res):
            t.add_line(f'Trace {i}:')
            t.add_line(trc)
            t.add_line()
        
        if color:
            s = t.get_and_reset_text_keep_col()
        else:
            s = t.get_text_clear_end()
        return s
    
    def format_trace(self, trace, long=False, color=True):
        if self.use_color:
            t = ColorBuilder()
        else:
            t = ColorBuildenPlainText()
        colors = Colors.ALL_COLORS[1:]
        trace_array = list(trace)
        if long:
            arr = trace_array[0].split(self.TEXT_SEPARATOR)
            prog = t.apply_style(arr[0], styles=[Colors.DIM])
            nid = t.apply_style(arr[1], [Colors.MAGENTA], [Colors.DIM])
            t.add_line(f'{prog} {nid};')
            trace_array = trace_array [1:]
            
        for i, trc in enumerate(trace_array):
            col = colors[i % len(colors)] if color else []
                
            if long:
                arr = trc.split(self.TEXT_SEPARATOR)
                step = t.apply_style(arr[0], col)
                prog = t.apply_style(arr[1], styles=[Colors.DIM])
                nid = t.apply_style(arr[2], [Colors.MAGENTA], [Colors.DIM])
                t.add_line(f'{step} {prog} {nid};')
            else:
                t.add_text(f'{trc};', col)
                
        # if color:
        #     s = t.get_and_reset_text_keep_col()
        # else:
        #     s = t.get_text_clear_end()
        return t.get_and_reset_text_keep_col()
        
    def call_trace(self, get_only_races=False):
        self.create_start_node()
        traces = self.trace(self.start_node, get_only_races)
        self.last_traces = traces
        pass
    
    def check_clocks(self, node):
        comp_list = list(node.main_components.values())
        for i, component1 in enumerate(comp_list):
            clock1 = list(component1.v_clock.values())
            for component2 in comp_list[i+1:]:
                clock2 = list(component2.v_clock.values())
                lesser = False
                greater = False
                for clk1, clk2 in zip(clock1, clock2):
                    if clk1 > clk2:
                        greater = True
                    elif clk1 < clk2:
                        lesser = True
                        
                    if greater and lesser:
                        return False
        return True
    
    def trace(self, node, get_only_races=False, level=0):
        t = self.get_builder('', [Colors.YELLOW], [Colors.DIM])
            
        # print('-=-=-=-=-=-=-=-=-=-=-=-=-CALLED TRACE-=-=-=-=-=-=-=-=-=-=-=-=-')
        t.add_line('\n-=-=-=-=-=-=-=-=-=-=-=-=-CALLED TRACE-=-=-=-=-=-=-=-=-=-=-=-=-', styles=[Colors.BOLD])
        txt_level = t.apply_style(level, [Colors.BLUE])
        t.add_line(f'level: {txt_level}')
        
        if node is None:
            return None
        if not isinstance(node, TracerTool.Node):
            raise RuntimeError("Improprer call of trace (possibly in recursion)")
        
        cloks_ok = self.check_clocks(node)
        if not cloks_ok:
            node.color = self.RACE_CONDITION_COL
            
        # Generate children if clocks are ok or we want not only race conditions
        if cloks_ok or not get_only_races:
            node.generate_children()
        
        # self.make_and_save_graph()
        pass
    
        if len(node.children) == 0:
            is_race = False if cloks_ok else True
            t.add_line(node.more_info(show_components=True), styles=[Colors.CLEAR_STYLE])
            t.add_line('Reached no further options, making trace...')
            obj = node
            trace = deque()
            trace_w_performers = deque()
            while obj.parent is not None:
                parent = obj.parent
                step = parent.children[obj]
                trace.appendleft(step.taken_step)
                trace_w_performers.appendleft(f'{str(step)}{self.TEXT_SEPARATOR}{{{obj}}}{self.TEXT_SEPARATOR}nid:{obj.id}')
                obj = obj.parent
            t.add_line("!!!!!CREATED NEW TRACE!!!!!", [Colors.RED], [Colors.BOLD])
            if is_race:
                t.add_line("!#!#!#!#!#!#! RACE !#!#!#!#!#!#!", [Colors.RED], [Colors.BOLD])
            t.add_line("Short")
            t.add_line(' ; '.join(list(trace)), [Colors.GREEN], {Colors.CLEAR_STYLE})
            
            trace_w_performers.appendleft(f'{{{obj}}}{self.TEXT_SEPARATOR}nid:{obj.id}')
            t.add_line("Long")
            t.add_line(' ;\n'.join(list(trace_w_performers)), [Colors.GREEN], [Colors.CLEAR_STYLE])
            txt_level = t.apply_style(level, [Colors.BLUE])
            t.add_line(f'level: {txt_level}')
            t.add_line('======================exit level========================', styles=[Colors.BOLD])
            t.print()
            pass
            ret_obj = []
            if get_only_races:
                if not cloks_ok:
                    ret_obj = [(node, (trace, trace_w_performers))]
            else:
                ret_obj = [(node, (trace, trace_w_performers))]
            return ret_obj
            
        res = []
        checked = []
        for i, (child_node, step) in enumerate(node.children.items()):
            t.add_line(node.more_info(checked=checked, show_components=True, current=child_node), styles=[Colors.CLEAR_STYLE])
            t.add_line('Calling trace for step:')
            t.add_line(f'{i}) {step}', styles=[Colors.CLEAR_STYLE])
            t.print()
            pass
            x = self.trace(child_node, get_only_races, level + 1)
            res.extend(x)
            checked.append(i)
            t.add_line(f'level: {txt_level}')
            pass
        t.add_line(node.more_info(checked=checked, current=child_node), styles=[Colors.CLEAR_STYLE])
        t.add_line(f'level: {txt_level}')
        t.add_line('======================exit level========================', styles=[Colors.BOLD])
        if level > 0:
            t.print()
        else:
            print(t.get_text_clear_end())
        pass
        return res
        
    
    def make_race_only_graph(self):
        traces = self.last_traces
        set_of_nodes = set([obj for obj, _ in traces])
        
        g_nodes = []
        g_edges = []
        g_custom_labels = {}
        g_edge_labels = {}
        g_node_colors = []
        
        g_ratio_dict = {}
        
        if len(traces) > 0:
            while len(set_of_nodes) > 1 or not list(set_of_nodes)[0].level == 1:
                parent_set = set()
                for node in set_of_nodes:
                    parent = node.parent
                    if parent is None:
                        continue
                    parent_set.add(parent)
                    parent_id = str(parent.id)
                                
                    lvl = node.level
                    g_ratio_dict[lvl] = g_ratio_dict[lvl] + 1 if lvl in g_ratio_dict else 1
                    
                    node_name = f'{node.id}\n{str(node)}'
                    node_id = str(node.id)
                    
                    if node_id not in g_nodes:
                        g_nodes.append(node_id)
                        g_node_colors.append(node.color)
                        g_custom_labels[node_id] = node_name
                    
                    step = parent.children[node]
                    edge = (parent_id, node_id)
                    edge_label = str(step)
                    g_edges.append(edge)
                    g_edge_labels[edge] = edge_label
                    pass
                set_of_nodes = parent_set
        
        # Add start node
        node = self.start_node
        st_node_name = f'{node.id}\n{str(node)}'
        st_node_id = str(node.id)
        
        g_nodes.append(st_node_id)
        g_node_colors.append(node.color)
        g_custom_labels[st_node_id] = st_node_name
        g_ratio_dict[1] = 1
                
        G = nx.DiGraph()
        
        G.add_nodes_from(list(g_nodes))
        G.add_edges_from(g_edges)   
        
        g_info = self.GraphInfo(G, g_custom_labels, g_node_colors, 
                                g_edge_labels, g_ratio_dict)
        self.graph_info = g_info

        pass
    
        return G, g_custom_labels, g_edge_labels
        
    
    def make_graph(self):
        def add_children_from(local_node, level=1):
            node_id = str(local_node.id)
            level += 1
            for child, step in local_node.children.items():
                ratio_dict[level] = ratio_dict[level] + 1 if level in ratio_dict else 1
                child_name = f'{child.id}\n{str(child)}'
                child_id = str(child.id)
                nodes.append(child_id)
                node_colors.append(child.color)
                custom_labels[child_id] = child_name
                
                edge = (node_id, child_id)
                edge_label = str(step)
                edges.append(edge)
                edge_labels[edge] = edge_label
                add_children_from(child, level)
            pass
        
        
        # G = nx.DiGraph()
        
        nodes = []
        edges = []
        custom_labels = {}
        edge_labels = {}
        node_colors = []
        
        node = self.start_node
        node_name = f'{node.id}\n{str(node)}'
        node_id = str(node.id)
        # node_id = node_name
        
        nodes.append(node_id)
        node_colors.append(node.color)
        custom_labels[node_id] = node_name
        
        ratio_dict = {1: 1}
        add_children_from(node)
        
        G = nx.DiGraph()
        # G = nx.balanced_tree(branching_factor, depth)
        
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        
        g_info = self.GraphInfo(G, custom_labels, node_colors, edge_labels, ratio_dict)
        self.graph_info = g_info

        return G, custom_labels, edge_labels
        
    def save_graph(self, filename='TRACE.png'):
        g_inf = self.graph_info
        G = g_inf.graph
        node_labels = g_inf.node_names
        edge_labels = g_inf.edge_names
        node_colors = g_inf.node_colors
        ratio_dict = g_inf.ratio_dict
        
        node_size = 11000
        font_size = 10
        label_size = 8.5
        
        # pos = nx.spring_layout(G)
        # pos = graphviz_layout(G, prog="twopi")
        pos = graphviz_layout(G, prog="dot")
        # pos = graphviz_layout(G, prog="circo")
        
        if ratio_dict is None:
            num_nodes = len(G.nodes)
            size_mult = 3.5
            fig_size = (num_nodes * 2 * size_mult, num_nodes * 1.5 * size_mult)
        else:
            y = max(ratio_dict.keys())
            x = max(ratio_dict.values())
            y_mult = 2.2
            x_mult = 2.35
            padding = 5 
            a = x * x_mult + padding
            b = y * y_mult + padding 
            # b = 2
            fig_size = (a, b)
        
        
        plt.figure(figsize=fig_size)
        # plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.999, bottom=0.001)
        

        nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=node_colors)
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color="gray", style='dashed', width=2)

        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=font_size, font_color="black", font_weight="bold")
        # nx.draw_networkx_edge_labels(G, pos, label_pos=1, edge_labels=edge_labels, font_color='red', font_size=10, font_weight='bold')
        
        # Manually adjust edge label positions
        i = 0
        center_y_deviation = [-7, 0, 7, 14]
        for edge, label in edge_labels.items():
            x = (pos[edge[1]][0])
            y = (pos[edge[1]][1] + pos[edge[0]][1]) / 2 - 8
            dev = center_y_deviation[i]
            y += dev
            i = i + 1 if i + 1 < len(center_y_deviation) else 0
            plt.text(x, y, label, color='white', fontsize=label_size,
                     ha='center', va='center',
                     bbox=dict(facecolor='black', alpha=0.6))

        # plt.title("Trace")
        plt.axis('off')  # Turn off the axis

        # Save the figure
        x = os.path.join(self.output_folder, filename)
        plt.savefig(x)
        plt.close()
        
    def make_and_save_graph(self, filename='TRACE_gen.png'):
        self.make_graph()
        self.save_graph(filename)
        
    def make_and_save_race_graph(self, filename='TRACE_RACE_gen.png'):
        self.make_race_only_graph()
        self.save_graph(filename)