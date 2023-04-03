from ipywidgets import Output, Text, Button, HBox, VBox
from numpy import where, log
from Base.TLMN._func import get_state_image, get_description, get_env_components, get_main_player_state
from Base.TLMN._env import getValidActions, getActionSize, getReward
from IPython.display import display, clear_output


class Render:
    def __init__(self, list_agent, list_data) -> None:
        self.list_agent = list_agent
        self.list_data = list_data

        self.out_0 = Output()
        with self.out_0:
            display(get_state_image())

        self.cmd_inp = Text(value="", placeholder="Enter command here")
        self.cmd_inp.on_submit(self.handle_submit_command)

        self.first = Button(description=" First state  ")
        self.first.on_click(self.handle_click_first)

        self.pre = Button(description="Previous state")
        self.pre.on_click(self.handle_click_pre)

        self.next = Button(description="  Next state  ")
        self.next.on_click(self.handle_click_next)

        self.last = Button(description="  Last state  ")
        self.last.on_click(self.handle_click_last)

        self.hbox_0 = HBox([self.cmd_inp, self.first, self.pre, self.next, self.last])

        self.system_state = "intro"
        self.valid_command = ["start"]
        self.command_description = {
            "start": "begin new match",
            "(int)": "perform the corresponding action",
            "(int)?": "explain the corresponding action",
            "go to (int)": 'go to the "(int)"th state'
        }

        self.out_1 = Output(layout={'border': '1px solid black'})
        self.show_valid_command()

        self.history_action = []
        self.history_state = []
        self.state_idx = -1

        self.out_2 = Output(layout={'border': '1px solid black'})
        self.show_msg(" ", end="")

        self.vbox = VBox([self.out_0, self.hbox_0, self.out_1, self.out_2])

    def display(self):
        return display(self.vbox)

    def handle_submit_command(self, _):
        cmd_value = self.cmd_inp.value
        self.disable()
        if cmd_value == "start" and "start" in self.valid_command:
            self.start_game()

        elif cmd_value.isdecimal() and "(int)" in self.valid_command:
            action = int(cmd_value)
            if action in self.validActions:
                self.step(action)
            else:
                self.show_msg(f"At the moment, {action} is not a valid action", end="")

        elif cmd_value.endswith("?") and "(int)?" in self.valid_command:
            lst = cmd_value.split("?")
            if len(lst) == 2 and lst[0].isdecimal():
                action = int(lst[0])
                description = get_description(action)
                if description != "":
                    self.show_msg(f"{action}: {description}", end="")
                else:
                    self.show_msg(f"{action} is not an action", end="")
            else:
                self.show_msg("Invalid command", end="")

        elif cmd_value.startswith("go to ") and "go to (int)" in self.valid_command:
            pass

        else:
            self.show_msg("Invalid command", end="")

        self.enable()

    def start_game(self):
        self.env_components = get_env_components()
        self.step()
        self.system_state = "play"

    def step(self, action=None):
        if not action is None:
            self.history_action.append(action)

        win, state, self.env_components = get_main_player_state(self.env_components, self.list_agent, self.list_data, action)
        self.history_state.append(state)

        with self.out_0:
            clear_output(wait=True)
            display(get_state_image(state))

        if win == -1:
            self.validActions = list(where(getValidActions(state) == 1)[0])
            self.valid_command = ["(int)", "(int)?"]
            with self.out_1:
                clear_output(wait=True)

            self.show_valid_action()
        else:
            self.valid_command = []
            with self.out_1:
                clear_output(wait=True)
                print()
                if win == 1:
                    print("You win!")
                elif win == 0:
                    print("You lose!")
                else:
                    raise Exception(f"win trả ra sai: {win}")

            self.system_state = "end"

        self.show_valid_command()

    def show_valid_action(self):
        with self.out_1:
            print("Valid actions:")
            k = 0
            i = 0
            l = int(round(log(getActionSize()-1) / log(10), 9)) + 2
            n = int(100.0/l)
            while True:
                if n*k + i >= len(self.validActions):
                    break

                print(f"%{l}d" % self.validActions[n*k+i], end="")
                i += 1
                if i == n:
                    k += 1
                    i = 0
                    print("")

            if i != 0:
                print("")

    def show_valid_command(self):
        if len(self.valid_command) > 0:
            with self.out_1:
                print()
                print("Valid commands:")
                for command in self.valid_command:
                    print(f'    "{command}": {self.command_description[command]}')

    def show_msg(self, *msg, end="\n"):
        with self.out_2:
            clear_output(wait=True)
            print()
            print(*msg, end=end)

    def handle_click_first(self, _):
        self.disable()
        if len(self.history_state) > 1 and self.state_idx != 0:
            self.state_idx = 0
            self.replay()

        self.enable()

    def handle_click_pre(self, _):
        self.disable()
        if len(self.history_state) > 1 and self.state_idx != 0:
            if self.state_idx == -1:
                self.state_idx = len(self.history_state) - 2
            else:
                self.state_idx -= 1

            self.replay()

        self.enable()

    def handle_click_next(self, _):
        self.disable()
        if self.state_idx != -1:
            self.state_idx += 1
            if self.state_idx == len(self.history_state) - 1:
                self.state_idx = -1

            if self.state_idx != -1:
                self.replay()
            else:
                self.view_last_state()

        self.enable()

    def handle_click_last(self, _):
        self.disable()
        if self.state_idx != -1:
            self.state_idx = -1
            self.view_last_state()

        self.enable()

    def replay(self):
        state = self.history_state[self.state_idx]
        with self.out_0:
            clear_output(wait=True)
            display(get_state_image(state))

        self.validActions = list(where(getValidActions(state) == 1)[0])
        self.valid_command = ["(int)?"]
        with self.out_1:
            clear_output(wait=True)

        self.show_valid_action()
        with self.out_1:
            print()
            print(f"Action: {self.history_action[self.state_idx]}")

        self.show_valid_command()

    def view_last_state(self):
        state = self.history_state[-1]
        with self.out_0:
            clear_output(wait=True)
            display(get_state_image(state))

        if self.system_state == "play":
            self.validActions = list(where(getValidActions(state) == 1)[0])
            self.valid_command = ["(int)", "(int)?"]
            with self.out_1:
                clear_output(wait=True)

            self.show_valid_action()
        else:
            self.valid_command = []
            win = getReward(state)
            with self.out_1:
                clear_output(wait=True)
                print()
                if win == 1:
                    print("You win")
                elif win == 0:
                    print("You lose")
                else:
                    raise Exception(f"win trả ra sai: {win}")

        self.show_valid_command()

    def disable(self):
        self.cmd_inp.disabled = True
        self.cmd_inp.value = "Processing . . ."
        self.first.disabled = True
        self.pre.disabled = True
        self.next.disabled = True
        self.last.disabled = True

    def enable(self):
        self.cmd_inp.disabled = False
        self.cmd_inp.value = ""
        try:
            self.cmd_inp.focus()
        except:
            pass
        self.first.disabled = False
        self.pre.disabled = False
        self.next.disabled = False
        self.last.disabled = False

    def review_agent(self, Agent, Data):
        self.disable()
        self.env_components = get_env_components()
        action = None
        win, state, self.env_components = get_main_player_state(self.env_components, self.list_agent, self.list_data, action)
        self.history_state.append(state)

        while win == -1:
            action, Data = Agent(state, Data)
            self.history_action.append(action)
            win, state, self.env_components = get_main_player_state(self.env_components, self.list_agent, self.list_data, action)
            self.history_state.append(state)
        
        self.system_state = "end"
        self.view_last_state()
        self.enable()