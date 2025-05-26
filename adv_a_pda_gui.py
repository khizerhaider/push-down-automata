import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import defaultdict
import json
import time

class PDASimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Pushdown Automaton Simulator")
        self.root.geometry("1200x800")
        
        # PDA components
        self.states = set()
        self.alphabet = set()
        self.stack_alphabet = set()
        self.transitions = defaultdict(list)
        self.start_state = ""
        self.accept_states = set()
        self.stack_bottom = "$"
        
        # Visualization variables
        self.simulation_running = False
        self.simulation_speed = 1000  # milliseconds
        self.current_step = 0
        self.simulation_steps = []
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: PDA Definition
        definition_frame = ttk.Frame(notebook)
        notebook.add(definition_frame, text="PDA Definition")
        
        # Tab 2: Simulation
        simulation_frame = ttk.Frame(notebook)
        notebook.add(simulation_frame, text="Simulation")
        
        # Tab 3: Visual Simulation
        visual_frame = ttk.Frame(notebook)
        notebook.add(visual_frame, text="Visual Simulation")
        
        self.setup_definition_tab(definition_frame)
        self.setup_simulation_tab(simulation_frame)
        self.setup_visual_tab(visual_frame)
        
    def setup_definition_tab(self, parent):
        # Main container with scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # States section
        states_frame = ttk.LabelFrame(scrollable_frame, text="States", padding=10)
        states_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(states_frame, text="States (comma-separated):").pack(anchor=tk.W)
        self.states_entry = ttk.Entry(states_frame, width=50)
        self.states_entry.pack(fill=tk.X, pady=2)
        self.states_entry.insert(0, "q0,q1,q2")
        
        ttk.Label(states_frame, text="Start State:").pack(anchor=tk.W, pady=(10,0))
        self.start_state_entry = ttk.Entry(states_frame, width=20)
        self.start_state_entry.pack(anchor=tk.W, pady=2)
        self.start_state_entry.insert(0, "q0")
        
        ttk.Label(states_frame, text="Accept States (comma-separated):").pack(anchor=tk.W, pady=(10,0))
        self.accept_states_entry = ttk.Entry(states_frame, width=50)
        self.accept_states_entry.pack(fill=tk.X, pady=2)
        self.accept_states_entry.insert(0, "q2")
        
        # Alphabet section
        alphabet_frame = ttk.LabelFrame(scrollable_frame, text="Alphabets", padding=10)
        alphabet_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(alphabet_frame, text="Input Alphabet (comma-separated):").pack(anchor=tk.W)
        self.alphabet_entry = ttk.Entry(alphabet_frame, width=50)
        self.alphabet_entry.pack(fill=tk.X, pady=2)
        self.alphabet_entry.insert(0, "(,)")
        
        ttk.Label(alphabet_frame, text="Stack Alphabet (comma-separated):").pack(anchor=tk.W, pady=(10,0))
        self.stack_alphabet_entry = ttk.Entry(alphabet_frame, width=50)
        self.stack_alphabet_entry.pack(fill=tk.X, pady=2)
        self.stack_alphabet_entry.insert(0, "(,$")
        
        # Transitions section
        transitions_frame = ttk.LabelFrame(scrollable_frame, text="Transitions", padding=10)
        transitions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(transitions_frame, text="Transition Format: state,input,stack_top → next_state,stack_push").pack(anchor=tk.W)
        ttk.Label(transitions_frame, text="Use 'ε' for epsilon transitions, 'ε' for empty stack operations").pack(anchor=tk.W)
        
        # Transition input
        trans_input_frame = ttk.Frame(transitions_frame)
        trans_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(trans_input_frame, text="Current State:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.trans_state = ttk.Entry(trans_input_frame, width=10)
        self.trans_state.grid(row=0, column=1, padx=2)
        
        ttk.Label(trans_input_frame, text="Input:").grid(row=0, column=2, sticky=tk.W, padx=2)
        self.trans_input = ttk.Entry(trans_input_frame, width=10)
        self.trans_input.grid(row=0, column=3, padx=2)
        
        ttk.Label(trans_input_frame, text="Stack Top:").grid(row=0, column=4, sticky=tk.W, padx=2)
        self.trans_stack_top = ttk.Entry(trans_input_frame, width=10)
        self.trans_stack_top.grid(row=0, column=5, padx=2)
        
        ttk.Label(trans_input_frame, text="Next State:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.trans_next_state = ttk.Entry(trans_input_frame, width=10)
        self.trans_next_state.grid(row=1, column=1, padx=2)
        
        ttk.Label(trans_input_frame, text="Stack Push:").grid(row=1, column=2, sticky=tk.W, padx=2)
        self.trans_stack_push = ttk.Entry(trans_input_frame, width=15)
        self.trans_stack_push.grid(row=1, column=3, columnspan=2, padx=2, sticky=tk.W)
        
        ttk.Button(trans_input_frame, text="Add Transition", command=self.add_transition).grid(row=1, column=5, padx=5)
        
        # Transitions list
        self.transitions_listbox = tk.Listbox(transitions_frame, height=8)
        self.transitions_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(transitions_frame, text="Remove Selected", command=self.remove_transition).pack(pady=2)
        
        # Control buttons
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(control_frame, text="Load Example (Balanced Parentheses)", command=self.load_example).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Update PDA", command=self.update_pda).pack(side=tk.RIGHT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_simulation_tab(self, parent):
        # Input section
        input_frame = ttk.LabelFrame(parent, text="Input String", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="String to test:").pack(anchor=tk.W)
        self.input_string_entry = ttk.Entry(input_frame, width=50, font=("Courier", 12))
        self.input_string_entry.pack(fill=tk.X, pady=2)
        
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Simulate", command=self.simulate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Step-by-Step", command=self.step_by_step_simulate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.RIGHT, padx=5)
        
        # Result section
        result_frame = ttk.LabelFrame(parent, text="Simulation Results", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=20, font=("Courier", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_visual_tab(self, parent):
        # Input and controls
        control_frame = ttk.LabelFrame(parent, text="Visual Simulation Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input string
        input_row = ttk.Frame(control_frame)
        input_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_row, text="Input String:").pack(side=tk.LEFT)
        self.visual_input_entry = ttk.Entry(input_row, width=30, font=("Courier", 12))
        self.visual_input_entry.pack(side=tk.LEFT, padx=10)
        
        # Speed control
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Animation Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                  values=["Slow", "Normal", "Fast"], state="readonly", width=10)
        speed_combo.pack(side=tk.LEFT, padx=10)
        speed_combo.bind("<<ComboboxSelected>>", self.update_speed)
        
        # Control buttons
        button_row = ttk.Frame(control_frame)
        button_row.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(button_row, text="Start Visual Simulation", command=self.start_visual_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(button_row, text="Pause", command=self.pause_simulation, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_btn = ttk.Button(button_row, text="Next Step", command=self.next_step, state=tk.DISABLED)
        self.step_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = ttk.Button(button_row, text="Reset", command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Visualization area
        viz_frame = ttk.LabelFrame(parent, text="PDA Visualization", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create canvas for visualization
        self.viz_canvas = tk.Canvas(viz_frame, bg="white", height=500)
        self.viz_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status display
        status_frame = ttk.Frame(viz_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        # Current state display
        state_frame = ttk.LabelFrame(status_frame, text="Current State", padding=5)
        state_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.current_state_label = ttk.Label(state_frame, text="Not Started", font=("Arial", 14, "bold"))
        self.current_state_label.pack()
        
        # Input tape display
        tape_frame = ttk.LabelFrame(status_frame, text="Input Tape", padding=5)
        tape_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.tape_canvas = tk.Canvas(tape_frame, height=60, bg="lightgray")
        self.tape_canvas.pack(fill=tk.X)
        
        # Stack display frame
        stack_frame = ttk.LabelFrame(status_frame, text="Stack", padding=5)
        stack_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        self.stack_canvas = tk.Canvas(stack_frame, width=100, height=200, bg="lightyellow")
        self.stack_canvas.pack()
        
        # Step info display
        info_frame = ttk.LabelFrame(parent, text="Step Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.step_info_text = tk.Text(info_frame, height=4, font=("Courier", 10))
        self.step_info_text.pack(fill=tk.X)
        
    def update_speed(self, event=None):
        speed_map = {"Slow": 2000, "Normal": 1000, "Fast": 500}
        self.simulation_speed = speed_map.get(self.speed_var.get(), 1000)
        
    def add_transition(self):
        state = self.trans_state.get().strip()
        input_char = self.trans_input.get().strip()
        stack_top = self.trans_stack_top.get().strip()
        next_state = self.trans_next_state.get().strip()
        stack_push = self.trans_stack_push.get().strip()
        
        if not all([state, next_state]):
            messagebox.showerror("Error", "State and Next State are required!")
            return
        
        # Handle epsilon
        if input_char == "":
            input_char = "ε"
        if stack_top == "":
            stack_top = "ε"
        if stack_push == "":
            stack_push = "ε"
            
        transition_str = f"{state},{input_char},{stack_top} → {next_state},{stack_push}"
        self.transitions_listbox.insert(tk.END, transition_str)
        
        # Clear fields
        self.trans_state.delete(0, tk.END)
        self.trans_input.delete(0, tk.END)
        self.trans_stack_top.delete(0, tk.END)
        self.trans_next_state.delete(0, tk.END)
        self.trans_stack_push.delete(0, tk.END)
        
    def remove_transition(self):
        selection = self.transitions_listbox.curselection()
        if selection:
            self.transitions_listbox.delete(selection[0])
            
    def load_example(self):
        # Balanced Parentheses PDA - CORRECTED VERSION
        self.states_entry.delete(0, tk.END)
        self.states_entry.insert(0, "q0,q1,q2")
        
        self.start_state_entry.delete(0, tk.END)
        self.start_state_entry.insert(0, "q0")
        
        self.accept_states_entry.delete(0, tk.END)
        self.accept_states_entry.insert(0, "q2")
        
        self.alphabet_entry.delete(0, tk.END)
        self.alphabet_entry.insert(0, "(,)")
        
        self.stack_alphabet_entry.delete(0, tk.END)
        self.stack_alphabet_entry.insert(0, "(,$")
        
        # Clear transitions
        self.transitions_listbox.delete(0, tk.END)
        
        # Add CORRECTED example transitions
        example_transitions = [
            "q0,ε,ε → q1,ε",   # FIXED: Just transition, don't push extra $
            "q1,(,ε → q1,(",   # Push opening parenthesis
            "q1,(,( → q1,((",  # Push opening parenthesis on stack
            "q1,(,$ → q1,($",  # Push opening parenthesis on bottom
            "q1,),( → q1,ε",   # Pop matching parenthesis
            "q1,ε,$ → q2,ε"    # Accept if stack has only bottom marker
        ]
        
        for trans in example_transitions:
            self.transitions_listbox.insert(tk.END, trans)
            
    def clear_all(self):
        self.states_entry.delete(0, tk.END)
        self.start_state_entry.delete(0, tk.END)
        self.accept_states_entry.delete(0, tk.END)
        self.alphabet_entry.delete(0, tk.END)
        self.stack_alphabet_entry.delete(0, tk.END)
        self.transitions_listbox.delete(0, tk.END)
        
    def update_pda(self):
        try:
            # Parse states
            self.states = set(s.strip() for s in self.states_entry.get().split(',') if s.strip())
            self.start_state = self.start_state_entry.get().strip()
            self.accept_states = set(s.strip() for s in self.accept_states_entry.get().split(',') if s.strip())
            
            # Parse alphabets
            self.alphabet = set(s.strip() for s in self.alphabet_entry.get().split(',') if s.strip())
            self.stack_alphabet = set(s.strip() for s in self.stack_alphabet_entry.get().split(',') if s.strip())
            
            # Parse transitions
            self.transitions = defaultdict(list)
            for i in range(self.transitions_listbox.size()):
                trans_str = self.transitions_listbox.get(i)
                try:
                    left, right = trans_str.split(' → ')
                    state, input_char, stack_top = left.split(',')
                    next_state, stack_push = right.split(',')
                    
                    key = (state.strip(), input_char.strip(), stack_top.strip())
                    value = (next_state.strip(), stack_push.strip())
                    self.transitions[key].append(value)
                except:
                    messagebox.showerror("Error", f"Invalid transition format: {trans_str}")
                    return
                    
            messagebox.showinfo("Success", "PDA updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating PDA: {str(e)}")
            
    def simulate(self):
        self.update_pda()
        input_string = self.input_string_entry.get()
        
        result = self.run_pda(input_string)
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Input: {input_string}\n")
        self.result_text.insert(tk.END, f"Result: {'ACCEPTED' if result['accepted'] else 'REJECTED'}\n")
        self.result_text.insert(tk.END, f"Final State: {result.get('final_state', 'N/A')}\n")
        self.result_text.insert(tk.END, f"Final Stack: {result.get('final_stack', 'N/A')}\n\n")
        
        if result.get('trace'):
            self.result_text.insert(tk.END, "Execution Trace:\n")
            self.result_text.insert(tk.END, "-" * 50 + "\n")
            for step in result['trace']:
                self.result_text.insert(tk.END, step + "\n")
                
    def step_by_step_simulate(self):
        self.update_pda()
        input_string = self.input_string_entry.get()
        
        result = self.run_pda(input_string, step_by_step=True)
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Step-by-Step Simulation for: {input_string}\n")
        self.result_text.insert(tk.END, "=" * 60 + "\n\n")
        
        if result.get('steps'):
            for i, step in enumerate(result['steps'], 1):
                self.result_text.insert(tk.END, f"Step {i}:\n")
                self.result_text.insert(tk.END, f"  State: {step['state']}\n")
                self.result_text.insert(tk.END, f"  Remaining Input: {step['remaining_input']}\n")
                self.result_text.insert(tk.END, f"  Stack: {step['stack']}\n")
                if step.get('transition'):
                    self.result_text.insert(tk.END, f"  Transition: {step['transition']}\n")
                if step.get('operation'):
                    self.result_text.insert(tk.END, f"  Stack Operation: {step['operation']}\n")
                self.result_text.insert(tk.END, "\n")
                
        self.result_text.insert(tk.END, f"Final Result: {'ACCEPTED' if result['accepted'] else 'REJECTED'}\n")
        
    def start_visual_simulation(self):
        self.update_pda()
        input_string = self.visual_input_entry.get()
        
        if not input_string:
            messagebox.showwarning("Warning", "Please enter an input string!")
            return
            
        # Generate simulation steps
        self.simulation_steps = self.generate_visual_steps(input_string)
        self.current_step = 0
        self.simulation_running = True
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.step_btn.config(state=tk.NORMAL)
        
        # Start animation
        self.animate_step()
        
    def generate_visual_steps(self, input_string):
        if not self.start_state or not self.states:
            return []
            
        steps = []
        
        def explore_path(state, pos, stack_state, path):
            # Record current configuration
            step = {
                'state': state,
                'position': pos,
                'stack': stack_state[:],
                'remaining_input': input_string[pos:] if pos < len(input_string) else "",
                'transition': None,
                'operation': None,
                'path': path[:]
            }
            steps.append(step)
            
            # Check acceptance
            if pos == len(input_string) and state in self.accept_states:
                step['accepted'] = True
                return True
                
            # Try epsilon transitions
            for (s, inp, stack_top), transitions in self.transitions.items():
                if s == state and inp == 'ε':
                    if stack_top == 'ε' or (stack_state and stack_state[-1] == stack_top):
                        for next_state, stack_push in transitions:
                            new_stack = stack_state[:]
                            operation = []
                            
                            # Pop operation
                            if stack_top != 'ε' and new_stack:
                                popped = new_stack.pop()
                                operation.append(f"POP {popped}")
                            
                            # Push operation
                            if stack_push != 'ε':
                                for char in reversed(stack_push):
                                    new_stack.append(char)
                                    operation.append(f"PUSH {char}")
                            
                            transition_info = f"{s},ε,{stack_top} → {next_state},{stack_push}"
                            new_path = path + [transition_info]
                            
                            step_with_trans = {
                                'state': state,
                                'position': pos,
                                'stack': stack_state[:],
                                'remaining_input': input_string[pos:] if pos < len(input_string) else "",
                                'transition': transition_info,
                                'operation': "; ".join(operation) if operation else "No stack operation",
                                'path': new_path,
                                'next_state': next_state,
                                'new_stack': new_stack[:]
                            }
                            steps.append(step_with_trans)
                            
                            if explore_path(next_state, pos, new_stack, new_path):
                                return True
            
            # Try input transitions
            if pos < len(input_string):
                current_char = input_string[pos]
                for (s, inp, stack_top), transitions in self.transitions.items():
                    if s == state and inp == current_char:
                        if stack_top == 'ε' or (stack_state and stack_state[-1] == stack_top):
                            for next_state, stack_push in transitions:
                                new_stack = stack_state[:]
                                operation = []
                                
                                # Pop operation
                                if stack_top != 'ε' and new_stack:
                                    popped = new_stack.pop()
                                    operation.append(f"POP {popped}")
                                
                                # Push operation
                                if stack_push != 'ε':
                                    for char in reversed(stack_push):
                                        new_stack.append(char)
                                        operation.append(f"PUSH {char}")
                                
                                transition_info = f"{s},{inp},{stack_top} → {next_state},{stack_push}"
                                new_path = path + [transition_info]
                                
                                step_with_trans = {
                                    'state': state,
                                    'position': pos,
                                    'stack': stack_state[:],
                                    'remaining_input': input_string[pos:],
                                    'transition': transition_info,
                                    'operation': "; ".join(operation) if operation else "No stack operation",
                                    'path': new_path,
                                    'next_state': next_state,
                                    'new_stack': new_stack[:],
                                    'input_consumed': current_char
                                }
                                steps.append(step_with_trans)
                                
                                if explore_path(next_state, pos + 1, new_stack, new_path):
                                    return True
            
            return False
        
        # Initialize and run
        initial_stack = [self.stack_bottom]
        accepted = explore_path(self.start_state, 0, initial_stack, [])
        
        # Mark final result
        if steps:
            steps[-1]['final_result'] = 'ACCEPTED' if accepted else 'REJECTED'
            
        return steps
        
    def animate_step(self):
        if not self.simulation_running or self.current_step >= len(self.simulation_steps):
            self.simulation_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            return
            
        self.display_current_step()
        
        if self.simulation_running:
            self.root.after(self.simulation_speed, self.next_step)
            
    def display_current_step(self):
        if self.current_step >= len(self.simulation_steps):
            return
            
        step = self.simulation_steps[self.current_step]
        
        # Update current state display
        state_text = step['state']
        if step.get('accepted'):
            state_text += " (ACCEPTED)"
        elif step.get('final_result'):
            state_text += f" ({step['final_result']})"
            
        self.current_state_label.config(text=state_text)
        
        # Update input tape
        self.draw_input_tape(step)
        
        # Update stack visualization
        self.draw_stack(step)
        
        # Update step information
        self.update_step_info(step)
        
    def draw_input_tape(self, step):
        self.tape_canvas.delete("all")
        
        input_string = self.visual_input_entry.get()
        position = step['position']
        
        cell_width = 40
        cell_height = 40
        start_x = 10
        start_y = 10
        
        for i, char in enumerate(input_string):
            x = start_x + i * cell_width
            
            # Draw cell
            color = "lightgreen" if i < position else "lightblue" if i == position else "white"
            self.tape_canvas.create_rectangle(x, start_y, x + cell_width, start_y + cell_height, 
                                            fill=color, outline="black")
            
            # Draw character
            self.tape_canvas.create_text(x + cell_width//2, start_y + cell_height//2, 
                                       text=char, font=("Arial", 12, "bold"))
            
            # Draw position marker
            if i == position:
                self.tape_canvas.create_polygon(x + cell_width//2 - 5, start_y - 10,
                                              x + cell_width//2 + 5, start_y - 10,
                                              x + cell_width//2, start_y - 2,
                                              fill="red")
                                              
    def draw_stack(self, step):
        self.stack_canvas.delete("all")
        
        stack = step.get('new_stack', step.get('stack', []))
        if not stack:
            stack = [self.stack_bottom]
            
        cell_width = 80
        cell_height = 30
        start_x = 10
        canvas_height = self.stack_canvas.winfo_height()
        
        # Draw stack from bottom to top
        for i, symbol in enumerate(reversed(stack)):
            y = canvas_height - 40 - i * cell_height
            
            # Draw cell
            color = "yellow" if symbol == self.stack_bottom else "lightcyan"
            if step.get('operation') and 'PUSH' in step.get('operation', '') and i == 0:
                color = "lightgreen"  # Highlight newly pushed
            elif step.get('operation') and 'POP' in step.get('operation', '') and i == 0:
                color = "lightcoral"  # Highlight popped
                
            self.stack_canvas.create_rectangle(start_x, y, start_x + cell_width, y + cell_height,
                                             fill=color, outline="black", width=2)
            
            # Draw symbol
            self.stack_canvas.create_text(start_x + cell_width//2, y + cell_height//2,
                                        text=symbol, font=("Arial", 12, "bold"))
        
        # Draw stack pointer
        if stack:
            y = canvas_height - 40
            self.stack_canvas.create_text(start_x + cell_width + 15, y + cell_height//2,
                                        text="← TOP", font=("Arial", 10), fill="red")
                                        
    def update_step_info(self, step):
        self.step_info_text.delete(1.0, tk.END)
        
        info = f"Step {self.current_step + 1}/{len(self.simulation_steps)}\n"
        info += f"Current State: {step['state']}\n"
        info += f"Remaining Input: '{step['remaining_input']}'\n"
        
        if step.get('transition'):
            info += f"Transition: {step['transition']}\n"
        if step.get('operation'):
            info += f"Stack Operation: {step['operation']}\n"
        if step.get('input_consumed'):
            info += f"Input Consumed: '{step['input_consumed']}'\n"
        if step.get('final_result'):
            info += f"Final Result: {step['final_result']}\n"
            
        self.step_info_text.insert(1.0, info)
        
    def next_step(self):
        if self.current_step < len(self.simulation_steps) - 1:
            self.current_step += 1
            self.display_current_step()
            
            if self.simulation_running:
                self.root.after(self.simulation_speed, self.next_step)
        else:
            self.simulation_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            
    def pause_simulation(self):
        self.simulation_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        
    def reset_simulation(self):
        self.simulation_running = False
        self.current_step = 0
        self.simulation_steps = []
        
        # Reset UI
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.step_btn.config(state=tk.DISABLED)
        
        # Clear displays
        self.current_state_label.config(text="Not Started")
        self.tape_canvas.delete("all")
        self.stack_canvas.delete("all")
        self.step_info_text.delete(1.0, tk.END)
        
    def run_pda(self, input_string, step_by_step=False):
        if not self.start_state or not self.states:
            return {'accepted': False, 'error': 'PDA not properly defined'}
            
        # Initialize
        stack = [self.stack_bottom]
        current_state = self.start_state
        input_pos = 0
        
        trace = []
        steps = []
        
        def add_step(state, remaining, stack_copy, transition=None, operation=None):
            step_info = {
                'state': state,
                'remaining_input': remaining,
                'stack': list(reversed(stack_copy)),
                'transition': transition,
                'operation': operation
            }
            
            if step_by_step:
                steps.append(step_info)
                
            trace_text = f"State: {state}, Input: '{remaining}', Stack: {list(reversed(stack_copy))}"
            if transition:
                trace_text += f", Transition: {transition}"
            if operation:
                trace_text += f", Operation: {operation}"
            trace.append(trace_text)
            
        add_step(current_state, input_string[input_pos:], stack[:])
        
        # Simulation with detailed tracking
        def simulate_recursive(state, pos, stack_state, depth=0):
            if depth > 1000:  # Prevent infinite recursion
                return False
                
            # Check if we can accept
            if pos == len(input_string) and state in self.accept_states:
                add_step(state, "", stack_state[:], "ACCEPT", "Accepting state reached")
                return True
                
            # Try epsilon transitions first
            for (s, inp, stack_top), transitions in self.transitions.items():
                if s == state and inp == 'ε':
                    if stack_top == 'ε' or (stack_state and stack_state[-1] == stack_top):
                        for next_state, stack_push in transitions:
                            new_stack = stack_state[:]
                            operation_desc = []
                            
                            # Pop if needed
                            if stack_top != 'ε' and new_stack:
                                popped = new_stack.pop()
                                operation_desc.append(f"POP {popped}")
                            
                            # Push if needed
                            if stack_push != 'ε':
                                for char in reversed(stack_push):
                                    new_stack.append(char)
                                    operation_desc.append(f"PUSH {char}")
                            
                            transition_str = f"{s},ε,{stack_top} → {next_state},{stack_push}"
                            operation_str = "; ".join(operation_desc) if operation_desc else "No stack operation"
                            
                            add_step(next_state, input_string[pos:], new_stack[:], 
                                   transition_str, operation_str)
                            
                            if simulate_recursive(next_state, pos, new_stack, depth + 1):
                                return True
            
            # Try input transitions
            if pos < len(input_string):
                current_char = input_string[pos]
                for (s, inp, stack_top), transitions in self.transitions.items():
                    if s == state and inp == current_char:
                        if stack_top == 'ε' or (stack_state and stack_state[-1] == stack_top):
                            for next_state, stack_push in transitions:
                                new_stack = stack_state[:]
                                operation_desc = []
                                
                                # Pop if needed
                                if stack_top != 'ε' and new_stack:
                                    popped = new_stack.pop()
                                    operation_desc.append(f"POP {popped}")
                                
                                # Push if needed
                                if stack_push != 'ε':
                                    for char in reversed(stack_push):
                                        new_stack.append(char)
                                        operation_desc.append(f"PUSH {char}")
                                
                                transition_str = f"{s},{inp},{stack_top} → {next_state},{stack_push}"
                                operation_str = "; ".join(operation_desc) if operation_desc else "No stack operation"
                                operation_str += f" (consumed '{current_char}')"
                                
                                add_step(next_state, input_string[pos+1:], new_stack[:], 
                                       transition_str, operation_str)
                                
                                if simulate_recursive(next_state, pos + 1, new_stack, depth + 1):
                                    return True
            
            return False
        
        # Run simulation
        accepted = simulate_recursive(current_state, 0, stack[:])
        
        return {
            'accepted': accepted,
            'final_state': current_state,
            'final_stack': list(reversed(stack)),
            'trace': trace,
            'steps': steps
        }
        
    def clear_output(self):
        self.result_text.delete(1.0, tk.END)

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PDASimulator(root)
    root.mainloop()