import tkinter as tk
from tkinter import messagebox

class PDA:
    def __init__(self, states, input_symbols, stack_symbols, transitions,
                 start_state, start_stack_symbol, accept_states):
        self.states = states
        self.input_symbols = input_symbols
        self.stack_symbols = stack_symbols
        self.transitions = transitions
        self.start_state = start_state
        self.start_stack_symbol = start_stack_symbol
        self.accept_states = accept_states
        self.reset()

    def reset(self):
        self.stack = [self.start_stack_symbol]
        self.current_state = self.start_state
        self.input_string = ""
        self.input_index = 0
        self.finished = False
        self.accepted = False
        self.history = []

    def load_input(self, input_string):
        self.reset()
        self.input_string = input_string
    
    def step(self):
        if self.finished:
            return False, "Simulation is already finished."

        # Early accept: input is done & in accepting state
        if self.input_index == len(self.input_string) and self.current_state in self.accept_states:
            self.finished = True
            self.accepted = True
            return False, "✅ Accepted!"

        input_symbol = self.input_string[self.input_index] if self.input_index < len(self.input_string) else ''
        stack_top = self.stack[-1] if self.stack else ''
        key = (self.current_state, input_symbol, stack_top)
        epsilon_key = (self.current_state, '', stack_top)

        if key in self.transitions:
            move = self.transitions[key][0]
            symbol_consumed = True
        elif epsilon_key in self.transitions:
            move = self.transitions[epsilon_key][0]
            symbol_consumed = False
        else:
            # ✅ Final check: did we finish in accepting state?
            self.finished = True
            self.accepted = (self.input_index == len(self.input_string) and self.current_state in self.accept_states)
            return False, "✅ Accepted!" if self.accepted else "No valid transition. ❌ Rejected."

        next_state, stack_push = move
        self.history.append((self.current_state, input_symbol if symbol_consumed else 'ε', stack_top, next_state, stack_push))

        if self.stack:
            self.stack.pop()
        if stack_push:
            for symbol in reversed(stack_push):
                self.stack.append(symbol)

        if symbol_consumed:
            self.input_index += 1
        self.current_state = next_state

        # ✅ Check again if we finished by epsilon move
        if self.input_index == len(self.input_string) and self.current_state in self.accept_states:
            self.finished = True
            self.accepted = True
            return False, "✅ Accepted!"

        return True, f"Transitioned to {next_state}"




# --- GUI using Tkinter ---
class PDASimulatorGUI:
    def __init__(self, root, pda):
        self.root = root
        self.pda = pda
        self.root.title("PDA Simulator")

        tk.Label(root, text="Input String:").grid(row=0, column=0, sticky="w")
        self.input_entry = tk.Entry(root, width=30)
        self.input_entry.grid(row=0, column=1)

        self.start_button = tk.Button(root, text="Start Simulation", command=self.start_simulation)
        self.start_button.grid(row=0, column=2)

        self.step_button = tk.Button(root, text="Step Forward", command=self.step_forward, state="disabled")
        self.step_button.grid(row=1, column=2)

        self.stack_label = tk.Label(root, text="Stack: []", font=("Courier", 12))
        self.stack_label.grid(row=2, column=0, columnspan=3, sticky="w")

        self.state_label = tk.Label(root, text="Current State: ", font=("Courier", 12))
        self.state_label.grid(row=3, column=0, columnspan=3, sticky="w")

        self.log_text = tk.Text(root, height=10, width=60)
        self.log_text.grid(row=4, column=0, columnspan=3)

        self.clear_button = tk.Button(root, text="Clear", command=self.clear)
        self.clear_button.grid(row=1, column=1)

    def start_simulation(self):
        input_string = self.input_entry.get()
        if not input_string:
            messagebox.showwarning("Input Required", "Please enter an input string.")
            return
        self.pda.load_input(input_string)
        self.update_gui()
        self.log_text.insert(tk.END, f"🔁 Starting simulation with input: {input_string}\n")
        self.step_button.config(state="normal")

    def step_forward(self):
        success, message = self.pda.step()
        self.update_gui()
        self.log_text.insert(tk.END, message + "\n")
        if self.pda.finished:
            self.step_button.config(state="disabled")

    def update_gui(self):
        self.stack_label.config(text=f"Stack: {self.pda.stack}")
        self.state_label.config(text=f"Current State: {self.pda.current_state}")

    def clear(self):
        self.input_entry.delete(0, tk.END)
        self.stack_label.config(text="Stack: []")
        self.state_label.config(text="Current State: ")
        self.log_text.delete(1.0, tk.END)
        self.pda.reset()
        self.step_button.config(state="disabled")

# --- Example usage: PDA for aⁿbⁿcⁿ ---
if __name__ == '__main__':
    # transitions = {
    #     ('q0', 'a', 'Z'): [('q0', 'AZ')],
    #     ('q0', 'a', 'A'): [('q0', 'AA')],
    #     ('q0', 'b', 'A'): [('q1', '')],
    #     ('q1', 'b', 'A'): [('q1', '')],
    #     ('q1', 'b', 'Z'): [('q2', 'BZ')],
    #     ('q1', '', 'Z'): [('q2', 'Z')],
    #     ('q2', 'b', 'B'): [('q2', 'BB')],
    #     ('q2', 'c', 'B'): [('q3', '')],
    #     ('q2', 'c', 'Z'): [('q3', 'Z')],
    #     ('q3', 'c', 'B'): [('q3', '')],
    #     ('q3', '', 'Z'): [('qf', 'Z')],
    # }

    transitions = {
    ('q', '(', 'Z'): [('q', 'XZ')],
    ('q', '(', 'X'): [('q', 'XX')],
    ('q', ')', 'X'): [('q', '')],
    ('q', '', 'Z'): [('qf', 'Z')]  # Accept if stack has only initial symbol
    }

    pda = PDA(
    states={'q', 'qf'},
    input_symbols={'(', ')'},
    stack_symbols={'Z', 'X'},
    transitions=transitions,
    start_state='q',
    start_stack_symbol='Z',
    accept_states={'qf'}
)

    # pda = PDA(
    #     states={'q0', 'q1', 'q2', 'q3', 'qf'},
    #     input_symbols={'a', 'b', 'c'},
    #     stack_symbols={'Z', 'A', 'B'},
    #     transitions=transitions,
    #     start_state='q0',
    #     start_stack_symbol='Z',
    #     accept_states={'qf'}
    # )

    root = tk.Tk()
    app = PDASimulatorGUI(root, pda)
    root.mainloop()
