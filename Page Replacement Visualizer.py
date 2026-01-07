import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# -------------------------
# Simulation helper functions
# -------------------------
def parse_page_string(s):
    s = s.strip()
    if not s:
        return []
    s = s.replace(',', ' ')
    parts = [p for p in s.split() if p != '']
    pages = []
    for p in parts:
        try:
            pages.append(int(p))
        except ValueError:
            pass
    return pages

def simulate_fifo(frame_count, pages):
    frames = [None]*frame_count
    pointer = 0
    steps = []
    for page in pages:
        fault = False
        replaced_index = None
        if page not in frames:
            fault = True
            replaced_index = pointer
            frames[pointer] = page
            pointer = (pointer + 1) % frame_count
        steps.append({'page': page, 'frames': frames.copy(), 'fault': fault, 'replaced_index': replaced_index})
    return steps

def simulate_lru(frame_count, pages):
    frames = [None]*frame_count
    last_used = {}
    steps = []
    time_idx = 0
    for page in pages:
        time_idx += 1
        if page in frames:
            fault = False
            replaced_index = None
            last_used[page] = time_idx
        else:
            fault = True
            if None in frames:
                idx = frames.index(None)
                frames[idx] = page
                replaced_index = idx
            else:
                # choose least recently used
                lru_page = min((p for p in frames), key=lambda x: last_used.get(x, 0))
                idx = frames.index(lru_page)
                frames[idx] = page
                replaced_index = idx
            last_used[page] = time_idx
        steps.append({'page': page, 'frames': frames.copy(), 'fault': fault, 'replaced_index': replaced_index})
    return steps

def simulate_optimal(frame_count, pages):
    frames = [None]*frame_count
    steps = []
    n = len(pages)
    for current_idx, page in enumerate(pages):
        if page in frames:
            steps.append({'page': page, 'frames': frames.copy(), 'fault': False, 'replaced_index': None})
            continue
        if None in frames:
            idx = frames.index(None)
            frames[idx] = page
            steps.append({'page': page, 'frames': frames.copy(), 'fault': True, 'replaced_index': idx})
            continue
        # farthest next use
        farthest_next = -1
        replace_idx = 0
        for i, p in enumerate(frames):
            next_use = None
            for j in range(current_idx+1, n):
                if pages[j] == p:
                    next_use = j
                    break
            if next_use is None:
                replace_idx = i
                farthest_next = float('inf')
                break
            elif next_use > farthest_next:
                farthest_next = next_use
                replace_idx = i
        frames[replace_idx] = page
        steps.append({'page': page, 'frames': frames.copy(), 'fault': True, 'replaced_index': replace_idx})
    return steps

# -------------------------
# UI settings
# -------------------------
CELL_WIDTH = 8
CELL_HEIGHT = 2
FAULT_BG = '#ffcccc'
HIT_BG = '#ccffcc'
NEW_BG = '#fff2b2'
EMPTY_BG = '#f0f0f0'


# -------------------------
# Algorithm Panel Class
# -------------------------
class AlgorithmPanel:
    def __init__(self, parent, title):
        self.parent = parent
        self.title = title
        self.frame = ttk.Labelframe(parent, text=title)
        # top info
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill='x', padx=4, pady=4)
        self.page_label = ttk.Label(top_frame, text='Page: -', font=('Helvetica', 12, 'bold'))
        self.page_label.pack(side='left', padx=4)
        self.step_label = ttk.Label(top_frame, text='Step: 0 / 0')
        self.step_label.pack(side='left', padx=8)
        self.faults_label = ttk.Label(top_frame, text='Faults: 0')
        self.faults_label.pack(side='right', padx=4)

        # frame cells
        self.grid_frame = ttk.Frame(self.frame)
        self.grid_frame.pack(padx=4, pady=4)
        self.cells = []

        # bottom info
        self.info_label = ttk.Label(self.frame, text='')
        self.info_label.pack(fill='x', padx=4, pady=4)

        # result box (total faults)
        self.result_box = tk.Label(self.frame, text="Total Faults: 0",
                                   relief="ridge", borderwidth=2,
                                   bg="#e6e6e6", font=('Helvetica', 11, 'bold'))
        self.result_box.pack(pady=(4, 8))

        # data
        self.steps = []
        self.current_step = 0
        self.frame_count = 0
        self.total_faults = 0

    def build_cells(self, frame_count):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.cells = []
        self.frame_count = frame_count
        for i in range(frame_count):
            lbl = tk.Label(self.grid_frame, text='-', width=CELL_WIDTH, height=CELL_HEIGHT,
                           relief='ridge', bg=EMPTY_BG, font=('Helvetica', 12))
            lbl.grid(row=i, column=0, padx=3, pady=3)
            self.cells.append(lbl)

    def load_steps(self, steps):
        self.steps = steps
        self.current_step = 0
        self.total_faults = sum(1 for s in steps if s['fault'])
        self.result_box.config(text=f"Total Faults: {self.total_faults}")
        self.update_display()

    def update_display(self):
        total = len(self.steps)
        if total == 0:
            self.page_label.config(text='Page: -')
            self.step_label.config(text='Step: 0 / 0')
            self.faults_label.config(text='Faults: 0')
            for c in self.cells:
                c.config(text='-', bg=EMPTY_BG)
            self.info_label.config(text='')
            return
        s = self.steps[self.current_step]
        page = s['page']
        frames = s['frames']
        fault = s['fault']
        replaced_index = s['replaced_index']
        self.page_label.config(text=f'Page: {page}')
        self.step_label.config(text=f'Step: {self.current_step+1} / {total}')
        current_faults = sum(1 for i in range(self.current_step+1) if self.steps[i]["fault"])
        self.faults_label.config(text=f'Faults: {current_faults} / {self.total_faults}')
        for i, lbl in enumerate(self.cells):
            content = frames[i]
            lbl.config(text='-' if content is None else str(content), bg=EMPTY_BG)
        if fault:
            if replaced_index is not None and 0 <= replaced_index < len(self.cells):
                self.cells[replaced_index].config(bg=NEW_BG)
            self.page_label.config(background=FAULT_BG)
        else:
            self.page_label.config(background=HIT_BG)
        self.info_label.config(text='Page fault occurred.' if fault else 'Page hit.')

    def step_next(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_display()

    def step_prev(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_display()


# -------------------------
# Main Visualizer App
# -------------------------
class VisualizerApp:
    def __init__(self, root):
        self.root = root
        root.title("Page Replacement Visualizer — FIFO / LRU / Optimal")
        # input area
        inp_frame = ttk.Frame(root)
        inp_frame.pack(fill='x', padx=8, pady=6)
        ttk.Label(inp_frame, text='Frame count:').grid(row=0, column=0, sticky='w')
        self.frame_count_var = tk.StringVar(value='3')
        self.frame_entry = ttk.Entry(inp_frame, width=6, textvariable=self.frame_count_var)
        self.frame_entry.grid(row=0, column=1, sticky='w', padx=(4,12))
        ttk.Label(inp_frame, text='Page request string:').grid(row=0, column=2, sticky='w')
        self.page_str_var = tk.StringVar(value='7 0 1 2 0 3 0 4 2 3 0 3 2')
        self.page_entry = ttk.Entry(inp_frame, width=40, textvariable=self.page_str_var)
        self.page_entry.grid(row=0, column=3, sticky='w', padx=(4,12))
        self.run_button = ttk.Button(inp_frame, text='Run (prepare)', command=self.on_run)
        self.run_button.grid(row=0, column=4, padx=4)
        self.reset_button = ttk.Button(inp_frame, text='Reset', command=self.on_reset)
        self.reset_button.grid(row=0, column=5, padx=4)

        # control buttons
        ctrl_frame = ttk.Frame(root)
        ctrl_frame.pack(fill='x', padx=8, pady=4)
        self.prev_button = ttk.Button(ctrl_frame, text='◀ Prev', command=self.on_prev)
        self.prev_button.pack(side='left', padx=2)
        self.next_button = ttk.Button(ctrl_frame, text='Next ▶', command=self.on_next)
        self.next_button.pack(side='left', padx=2)
        ttk.Label(ctrl_frame, text='Delay (s):').pack(side='left', padx=(12,2))
        self.delay_var = tk.DoubleVar(value=0.8)
        self.delay_spin = ttk.Spinbox(ctrl_frame, from_=0.1, to=5.0, increment=0.1,
                                      width=5, textvariable=self.delay_var)
        self.delay_spin.pack(side='left')
        self.play_button = ttk.Button(ctrl_frame, text='Run All ▶', command=self.on_play)
        self.play_button.pack(side='left', padx=8)
        self.pause_button = ttk.Button(ctrl_frame, text='Pause ⏸', command=self.on_pause)
        self.pause_button.pack(side='left', padx=2)

        # display panels
        display_frame = ttk.Frame(root)
        display_frame.pack(fill='both', expand=True, padx=8, pady=6)
        self.fifo_panel = AlgorithmPanel(display_frame, 'FIFO')
        self.fifo_panel.frame.pack(side='left', fill='both', expand=True, padx=4)
        self.lru_panel = AlgorithmPanel(display_frame, 'LRU')
        self.lru_panel.frame.pack(side='left', fill='both', expand=True, padx=4)
        self.opt_panel = AlgorithmPanel(display_frame, 'Optimal')
        self.opt_panel.frame.pack(side='left', fill='both', expand=True, padx=4)

        # status
        self.status_label = ttk.Label(root, text='Ready.')
        self.status_label.pack(fill='x', padx=8, pady=4)

        # internal vars
        self.pages = []
        self.frame_count = 0
        self.steps_len = 0
        self.playing = False
        self.stop_play_event = threading.Event()

    def parse_inputs(self):
        try:
            fc = int(self.frame_count_var.get())
            if fc <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror('Invalid input', 'Frame count must be a positive integer.')
            return None, None
        pages = parse_page_string(self.page_str_var.get())
        if not pages:
            messagebox.showerror('Invalid input', 'Please enter at least one page number.')
            return None, None
        return fc, pages

    def on_run(self):
        fc, pages = self.parse_inputs()
        if fc is None:
            return
        self.frame_count = fc
        self.pages = pages
        # simulate
        fifo_steps = simulate_fifo(fc, pages)
        lru_steps = simulate_lru(fc, pages)
        opt_steps = simulate_optimal(fc, pages)
        # build UIs
        self.fifo_panel.build_cells(fc)
        self.lru_panel.build_cells(fc)
        self.opt_panel.build_cells(fc)
        self.fifo_panel.load_steps(fifo_steps)
        self.lru_panel.load_steps(lru_steps)
        self.opt_panel.load_steps(opt_steps)
        self.steps_len = len(pages)
        self.status_label.config(text=f'Simulation ready for {len(pages)} requests.')

    def on_reset(self):
        for p in (self.fifo_panel, self.lru_panel, self.opt_panel):
            p.load_steps([])
        self.status_label.config(text='Reset done.')
        self.pages = []
        self.frame_count = 0

    def on_next(self):
        for p in (self.fifo_panel, self.lru_panel, self.opt_panel):
            p.step_next()

    def on_prev(self):
        for p in (self.fifo_panel, self.lru_panel, self.opt_panel):
            p.step_prev()

    def autoplay_loop(self):
        self.stop_play_event.clear()
        while not self.stop_play_event.is_set():
            cur = self.fifo_panel.current_step
            if cur >= self.steps_len - 1:
                break
            time.sleep(self.delay_var.get())
            if self.stop_play_event.is_set():
                break
            self.root.after(0, self.on_next)
        self.playing = False
        self.root.after(0, lambda: self.status_label.config(text='Autoplay finished.'))

    def on_play(self):
        if not self.fifo_panel.steps:
            messagebox.showinfo('No simulation', 'Run simulation first.')
            return
        if self.playing:
            return
        self.playing = True
        self.status_label.config(text='Autoplay running...')
        threading.Thread(target=self.autoplay_loop, daemon=True).start()

    def on_pause(self):
        self.stop_play_event.set()
        self.playing = False
        self.status_label.config(text='Autoplay paused.')

# -------------------------
# Run main app
# -------------------------
def main():
    root = tk.Tk()
    app = VisualizerApp(root)
    root.geometry('1200x550')
    root.mainloop()

if __name__ == '__main__':
    main()
