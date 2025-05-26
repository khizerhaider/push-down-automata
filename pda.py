class PDA:
    def __init__(self, states, input_symbols, stack_symbols, transitions,
                 start_state, start_stack_symbol, accept_states):
        self.states = states
        self.input_symbols = input_symbols
        self.stack_symbols = stack_symbols
        self.transitions = transitions  # dict: (state, input_symbol, stack_top) -> [(next_state, push_stack)]
        self.start_state = start_state
        self.start_stack_symbol = start_stack_symbol
        self.accept_states = accept_states

    def accepts(self, input_string):
        return self._accept_recursive(
            current_state=self.start_state,
            remaining_input=input_string,
            stack=[self.start_stack_symbol]
        )

    def _accept_recursive(self, current_state, remaining_input, stack):
        if len(stack) == 0:
            return False

        current_input = remaining_input[0] if remaining_input else ''
        stack_top = stack[-1]

        possible_moves = []

        # Try transitions with actual input symbol
        if (current_state, current_input, stack_top) in self.transitions:
            possible_moves += self.transitions[(current_state, current_input, stack_top)]

        # Try ε-transitions (input symbol = '')
        if (current_state, '', stack_top) in self.transitions:
            possible_moves += self.transitions[(current_state, '', stack_top)]

        for next_state, stack_to_push in possible_moves:
            new_stack = stack[:-1]  # pop
            if stack_to_push:
                for symbol in reversed(stack_to_push):
                    new_stack.append(symbol)

            new_input = remaining_input
            if current_input and (current_state, current_input, stack_top) in self.transitions:
                new_input = remaining_input[1:]

            if not new_input and next_state in self.accept_states:
                return True

            if self._accept_recursive(next_state, new_input, new_stack):
                return True

        return False


# Example usage
if __name__ == '__main__':
    # PDA to recognize language: L = { a^n b^n | n >= 1 }
    pda = PDA(
        states={'q0', 'q1', 'q2'},
        input_symbols={'a', 'b'},
        stack_symbols={'Z', 'A'},
        transitions={
            ('q0', 'a', 'Z'): [('q0', 'AZ')],
            ('q0', 'a', 'A'): [('q0', 'AA')],
            ('q0', 'b', 'A'): [('q1', '')],
            ('q1', 'b', 'A'): [('q1', '')],
            ('q1', '', 'Z'): [('q2', 'Z')],  # ε-transition
        },
        start_state='q0',
        start_stack_symbol='Z',
        accept_states={'q2'}
    )

    test_strings = ['ab', 'aabb', 'aaabbb', 'aab', 'aaabb']
    for s in test_strings:
        result = pda.accepts(s)
        print(f"Input: {s} -> {'Accepted' if result else 'Rejected'}")
