"""RKStreamer - State and State machine module"""


class State:
    """State class"""

    def __init__(self, name, prompt, controller):
        self.name = name
        self.prompt = prompt
        self.controller = controller

    def handle_input(self, user_input):
        """Handle user input"""
        self.controller.handle_input(user_input)


class StateMachine:
    """State machine"""

    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, state):
        """Add state to states list"""
        if isinstance(state, dict):
            self.states = state
        else:
            self.states[state.name] = state

    def set_start_state(self, state_name):
        """Setting the start date - init"""
        self.current_state = self.states[state_name]

    def trigger(self):
        """Triggers the state change or handle current state"""
        while True:
            user_input = input(self.current_state.prompt)
            if user_input.lower().startswith('-e'):
                raise SystemExit('Tata!')
            elif user_input.startswith("--"):
                state_name = user_input[2:]
                if (state_name != self.current_state.name) and (state_name in self.states):
                    # stop player when switching mode.
                    self.current_state.controller.view.stop()
                    self.current_state = self.states[state_name]
            else:
                if user_input:
                    self.current_state.handle_input(user_input)
