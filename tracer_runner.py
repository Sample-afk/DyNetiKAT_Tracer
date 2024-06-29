import os
import optparse
import sys

# file reading
import chardet
import re

# core classes
from TracerTool.src.component import Component
from TracerTool.src.tracer_v1 import TracerTool
from TracerTool.src.maude_parser import MaudeComm
from TracerTool.src.color_builder import Colors, ColorBuilder, ColorBuildenPlainText

#helper
from time import perf_counter
from src.python.util import is_exe, generate_outfile

class TracerRunner:
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.file = open(filename, 'w')

        def write(self, message):
            self.terminal.write(message)
            self.file.write(message)

        def flush(self):
            # Needed for compatibility with `sys.stdout`
            self.terminal.flush()
            self.file.flush()

    DEFAULT_UNFOLD_DEPTH = 4
    DEFAULT_OUT_COL = [Colors.WHITE]

    STEP_COL = [Colors.RED]
    STEP_ST = [Colors.BOLD]
    LOG_ST = [Colors.DIM]
    SEP = "+-+-+-+-+-+-+--+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-"
    DEFAULT_LOG_NAME = 'RUN_TRACER_OUT.txt'
    OUT_FOLDER_NAME = 'TracerTool_output'

    direct = os.path.dirname(os.path.realpath(__file__))
    output_folder = os.path.join(direct, OUT_FOLDER_NAME)
    maude_dnk_file = os.path.join(direct, 'src/maude/dnk.maude')
    maude_path = ''
    model_path = ''
    
# inits
    def __init__(self, primary_col=DEFAULT_OUT_COL) -> None:
        self.out_col = primary_col
        opts, args = self.init_parameters()
        self.call_options = opts
        self.call_arguments = args
        
        output_maker = None
        if self.use_color:
            output_maker = ColorBuilder("\n", [Colors.WHITE])
        else:
            output_maker = ColorBuildenPlainText("\n")
        self.color_builder = output_maker
        self.maude = None
        pass

    def init_parameters(self):
        parser = optparse.OptionParser()
        parser.add_option("-f", "--log_filename", type="str", dest="log_filename", default=self.DEFAULT_LOG_NAME,
                        help=f"custom text output filename, default: {self.DEFAULT_LOG_NAME}")
        
        parser.add_option("-u", "--unfold_depth", type="int", dest="unfold_depth", default=self.DEFAULT_UNFOLD_DEPTH,
                        help=f"unfold depth for DNKs \'pi{{*depth*}}(*program*)\', default: {self.DEFAULT_UNFOLD_DEPTH}")
        
        parser.add_option("-c", "--colorful", dest="use_color", action="store_true", default=False,
                          help=f"print output with color")
        
        parser.add_option("-t", "--tracing_steps", dest="show_tracing_steps", action="store_true", default=False,
                          help=f"print tracing steps")
        
        parser.add_option("-g", "--graph_types", choices=["full", "race"], dest="graphs",
                          help="choose types of traces returned \'full\' or \'race\' if ommited, do both")
        (options, args) = parser.parse_args()
        
        if len(args) < 2:
            print("Error: provide the arguments <path_to_maude> <path_to_model_in_maude>.")
            sys.exit()

        if not os.path.exists(args[0]) or not is_exe(args[0]):
            print("Please provide the path to the Maude executable.")
            sys.exit()
            
        if not os.path.exists(args[1]) or not self.is_maude(args[1]):
            print("Please provide the path to the Maude model.")
            sys.exit()
        
        self.maude_path = args[0]
        self.model_path = args[1]
        
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        log_filename = options.log_filename
        log_file = os.path.join(self.output_folder, log_filename)
        sys.stdout = self.Logger(log_file)
        
        self.unfold_depth = options.unfold_depth
        self.use_color = options.use_color
        self.show_tracing_steps = options.show_tracing_steps
        self.graph_type = options.graphs
            
        return options, args
        
# helpers        
    def is_maude(self, path):
        return os.path.isfile(path) and len(path) > 6 and path[-6:] == ".maude"
    
    def get_encoding_and_content(self, f_path):
        # Does not work when called from get_init_st?
        e = None
        c = None
        with open(f_path, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
            content = rawdata.decode(encoding, errors='replace') 
            e = encoding
            c = content
        return e, c
        
    def report_step_time(self, time, step_txt, cb):
        time = cb.apply_style('{:.2f}'.format(time), [Colors.GREEN])
        cb.add_text(step_txt, self.STEP_COL, [Colors.DIM], new_line=True)
        cb.add_line(f'done in {time} secondes')
        cb.add_line(self.SEP, [Colors.GREEN], [Colors.DIM])

# main parts
    # step 1
    def get_init_st(self, content):
        match = re.search(r'eq Init =([^.]*)\.', content)
        if match:
            init_string = match.group(1)
            return init_string
        else:
            return None
    
    # step 2
    def get_info_from_model(self):
        _, content = self.get_encoding_and_content(self.model_path)
        init = self.get_init_st(content)
        c_names = init.split("||")
        num_of_components = len(c_names)
        
        self.component_names = c_names
        self.num_of_components = num_of_components
        return init, c_names, num_of_components
        
    # step 3
    def generate_components(self):
        maude = MaudeComm(self.direct, self.maude_path, generate_outfile(self.direct, "maude_temp_out"))
        components = {}
        id = 0
        names = getattr(self, 'component_names', None)
        if names is None:
            raise RuntimeError("\'generate_components\' must be called after \'get_info_from_model\' in \'TraceRunner\'")
        for name in names:
            component = Component(maude, self.unfold_depth, self.model_path, name, id, self.num_of_components, self.use_color)
            components[component.id] = component
            id += 1
        self.components = components
        return components
    
# showcase of TracerTool
    def showcase(self):
        t = self.color_builder
        times = {}
        showcase_start = perf_counter()
        t.add_line("==============================WELCOME TO DYNETIKAT TRACER==============================",
                [Colors.GREEN], [Colors.BOLD, Colors.UNDERLINE])
        t.add_text("The tool is also writing in: ")
        log_folder_file = f'{self.OUT_FOLDER_NAME}/{self.call_options.log_filename}'
        t.add_line(f'./{log_folder_file}', [Colors.YELLOW])
        t.add_text("Color:")
        t.add_line(self.use_color, [Colors.GREEN])
        
        t.add_text("Show tracing steps:")
        col = [Colors.GREEN] if self.show_tracing_steps else [Colors.RED]
        t.add_line(self.show_tracing_steps, col)
        
        t.add_text("Make graph(s):")
        if self.graph_type is None:
            graph_type = 'both (\'full\' and \'race\')'
        else:
            graph_type = self.graph_type
        t.add_line(graph_type, [Colors.MAGENTA])
    
    
        # ==================================================================================================
        # SECTION 1: get components
    
        # prepare
        step_txt = "Step 1"
        t.add_text(f'{step_txt}:', self.STEP_COL, self.STEP_ST, new_line=True)
        t.add_line("read model and get num of components")
    
        # do
        step_start = perf_counter()
        init, c_names, num_of_components = self.get_info_from_model()
        step_end = perf_counter()
        
        # print results
        t.add_text('Program (init eq):')
        t.add_line(init, [Colors.BLUE], [Colors.BOLD])
        t.add_text('Components:')
        t.add_line(num_of_components, [Colors.GREEN], [Colors.DIM])
        t.add_text("Unfold:")
        t.add_line(self.unfold_depth, [Colors.YELLOW], [Colors.DIM])
        
        # save and report time
        step_time = step_end - step_start
        times[step_txt] = step_time
        self.report_step_time(step_time, step_txt, t)
    
    
        # ==================================================================================================
        # SECTION 2: convert data to python representation
    
        # prepare
        step_txt = "Step 2"
        t.add_text(f'{step_txt}:', self.STEP_COL, self.STEP_ST)
        t.add_line("convert data to python representation")
        
        # do
        step_start = perf_counter()
        components = self.generate_components()
        step_end = perf_counter()
        
        # print results
        t.add_line("Components:")
        t.add_line(self.SEP, styles=self.LOG_ST)
        for c in components.values():
            t.add_line(c.to_full_str())
            t.add_line(self.SEP, styles=self.LOG_ST)
        
        # save and report time
        step_time = step_end - step_start
        times[step_txt] = step_time
        self.report_step_time(step_time, step_txt, t)
        
        
        # ==================================================================================================
        # SECTION 3: trace
    
        # prepare
        step_txt = "Step 3"
        t.add_text(f'{step_txt}:', self.STEP_COL, self.STEP_ST)
        t.add_line("trace")
        # img_format = ".svg"
        img_format = ".png"
        
                   
        
        # do
        step_start = perf_counter()
                
        # trace all nad make graph
        if self.graph_type is None or self.graph_type == 'full':
            t.add_line('Running full tracer...')
            t.print()
            tracer_full = TracerTool(components, self.output_folder, show_steps=self.show_tracing_steps, use_color=self.use_color)
            trace_start = perf_counter()
            tracer_full.call_trace()
            trace_end = perf_counter()
            tracer_full.make_and_save_graph(f'GRAPH_FULL{img_format}')
            graph_end = perf_counter()
                    
            # save times
            tr_time = trace_end - trace_start
            gr_time = graph_end - trace_end
            times["\n\tFull trace"] = tr_time
            times["\tFull graph"] = gr_time
        
        
        # trace only races
        if self.graph_type is None or self.graph_type == 'race':
            t.add_line('Running race tracer...')
            t.print()
            tracer_race = TracerTool(components, self.output_folder, show_steps=self.show_tracing_steps, use_color=self.use_color)
            trace_start = perf_counter()
            tracer_race.call_trace(get_only_races=True)
            trace_end = perf_counter()
            # similar to full graph, but each branch ends if race was found
            tracer_race.make_and_save_graph(f'GRAPH_PRUNED{img_format}')
            pruned_end = perf_counter()
            # race graph
            tracer_race.make_and_save_race_graph(f'GRAPH_ONLY_RACES{img_format}')
            races_end = perf_counter()
            
            # save times
            tr_time = trace_end - trace_start
            pruned_time = pruned_end - trace_end
            race_time = races_end - pruned_end
            times["\n\tRace trace"] = tr_time
            times["\tPrune graph"] = pruned_time
            times["\tRace graph"] = race_time
        
        
        
        # save and report step time
        step_end = perf_counter()
        step_time = step_end - step_start
        times[f'\n{step_txt}'] = step_time
        self.report_step_time(step_time, step_txt, t)
        
        # ==================================================================================================
        # print traces
        
        if self.show_tracing_steps:
            t.add_line("Initial components (repeated):")
            t.add_line(self.SEP, styles=self.LOG_ST)
            for c in components.values():
                t.add_line(c.to_full_str())
                t.add_line(self.SEP, styles=self.LOG_ST)
                
            t.add_text("Unfold:")
            t.add_line(self.unfold_depth, [Colors.YELLOW], [Colors.DIM])
        
        s_trc = None
        if self.graph_type is None or self.graph_type == 'full':
            s_trc = tracer_full.format_traces()
            l_trc = tracer_full.format_traces(long=True)
            txt = t.apply_style('ALL', [Colors.CYAN], [Colors.UNDERLINE, Colors.BOLD])
            
            t.add_text(txt)
            t.add_line("SHORT TRACES", [Colors.CYAN], [Colors.BOLD])
            t.add_line(s_trc)
            t.add_line()
            
            t.add_text(txt)
            t.add_line("LONG TRACES", [Colors.CYAN], [Colors.BOLD])
            t.add_line(l_trc)
            
        if self.graph_type is None or self.graph_type == 'race':
            if len(tracer_race.last_traces) == 0:
                t.add_line("NO RACE TRACES were found (most likely due to low unfold depth)", [Colors.YELLOW], [Colors.BOLD])
            else:
                if s_trc is not None:
                    t.add_line(self.SEP[:len(self.SEP) // 2], styles=self.LOG_ST)
                s_trc = tracer_race.format_traces()
                l_trc = tracer_race.format_traces(long=True)
                txt = t.apply_style('RACE', [Colors.CYAN], [Colors.UNDERLINE])
                
                t.add_text(txt)
                t.add_line("SHORT TRACES", [Colors.CYAN], [Colors.BOLD])
                t.add_line(s_trc)
                t.add_line()
                
                t.add_text(txt)
                t.add_line("LONG TRACES", [Colors.CYAN], [Colors.BOLD])
                t.add_line(l_trc)
        
        # ==================================================================================================
        # print times
 
        showcase_end = perf_counter()
        t.add_line(self.SEP, styles=self.LOG_ST)
        for who, tm in times.items():
            t.add_text(who, self.STEP_COL, self.STEP_ST)
            time = t.apply_style('{:.2f}'.format(tm), [Colors.GREEN])
            t.add_line(f'done in {time} seconds')
            
        time = t.apply_style('{:.2f}'.format(showcase_end - showcase_start), [Colors.GREEN])
        t.add_line(f"Total time: {time} seconds") 
        t.add_line("========================================GOODBYE========================================", 
                [Colors.GREEN], [Colors.BOLD, Colors.UNDERLINE])
        print(t)
        pass
    
if __name__ == "__main__":
    # program_start = perf_counter()
    runner = TracerRunner()
    
    runner.showcase()
    pass
    
    # program_stop = perf_counter()
    # print('Program finished in {:.2f} seconds'.format(program_stop-program_start))

