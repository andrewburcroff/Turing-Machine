import json
import copy
import sys
import os
import collections
import re

kSTATES_PREFIX = "States"
kALPHA_PREFIX = "Alphabet"
kTAPEALPHA_PREFIX = "TapeAlphabet"
kDTABLE_PREFIX = "D-Table"
kTTABLE_PREFIX = "T-Table"
kSTART_PREFIX = "Start"
kACCEPT_PREFIX = "Accept"
kEXEC_OUTPUT = "output"
kEXEC_ACCEPT = "accepted"
kEXEC_TAPE = "tape"
kLAMBA = ""
kEMPTYSET = "∅"
kBLANK = "Б"
kLEFT = "←"
kRIGHT = "→"
kSTATIONARY = "↓"


def generateConfigDFA():
    config = dict()
    config[kSTATES_PREFIX] = list(set("AB"))
    config[kALPHA_PREFIX] = list(set("ab"))
    config[kDTABLE_PREFIX] = collections.defaultdict(dict)
    for this_state in config[kSTATES_PREFIX]:
        for this_alpha in config[kALPHA_PREFIX]:
            config[kDTABLE_PREFIX][this_state][this_alpha] = this_state
    config[kSTART_PREFIX] = "A"
    config[kACCEPT_PREFIX] = list(set("A"))
    filepath = os.path.join(os.path.expanduser("~"), "Desktop", "test_config.dfa")
    with open(filepath, "w+", encoding='utf-8') as f:
        json.dump(config, f, sort_keys=True, indent=4, ensure_ascii=False)


def generateConfigNFAlamba():
    config = dict()
    config[kSTATES_PREFIX] = list(set("AB"))
    config[kALPHA_PREFIX] = [kLAMBA, 'a', 'b']
    config[kDTABLE_PREFIX] = collections.defaultdict(dict)
    for this_state in config[kSTATES_PREFIX]:
        for this_alpha in config[kALPHA_PREFIX]:
            config[kDTABLE_PREFIX][this_state][this_alpha] = this_state
    config[kSTART_PREFIX] = "A"
    config[kACCEPT_PREFIX] = list(set("A"))
    filepath = os.path.join(os.path.expanduser("~"), "Desktop", "test_config.nfal")
    with open(filepath, "w+", encoding='utf-8') as f:
        json.dump(config, f, sort_keys=True, indent=4, ensure_ascii=False)


class Machine:
    def __init__(self, filepath=None):
        self.current_state = None
        self.current_position = 0
        self.loaded_tape = None
        try:
            if filepath:
                self.config(filepath)
        except (InvalidConfigBlock, MissingConfigBlock, FileNotFoundError) as e:
            print(type(e), e, sys.stderr)

    def config(self, filepath):
        """
        uses a given file to configure the
        machine

        :param filepath:
        :return:
        """
        pass

    def export(self, filepath):
        pass

    def dumps(self) -> str:
        pass

    def exec(self):
        """
        performs a execution of the machine
        with the currently loaded tape

        :return:
        """
        pass

    def load(self, tape):
        """
        loads a tape in the machine

        :param Tape tape: tape to load into machine
        """
        self.loaded_tape = tape


class BadTMTransition(Exception):
    pass


class TMTransitionUndefined(Exception):
    pass


class TMTransition():
    def __init__(self, *args):
        if len(args) == 3:
            self.state = args[0]
            self.character = args[1]
            self.direction = args[2]
        elif len(args) == 1:
            self.__parse(*args)
        else:
            raise BadTMTransition(*args)

    def __str__(self) -> str:
        return "{0}, {1}, {2}".format(self.state, self.character, self.direction)

    def __parse(self, string: str) -> None:
        parts = string.split(",")
        if len(parts) != 3:
            raise BadTMTransition(string)
        parts = [x.strip(" ") for x in parts]
        self.state = parts[0]
        self.character = parts[1]
        self.direction = parts[2]


class TM(Machine):
    def load(self, tape: "Tape") -> None:
        """
        loads a "tape" object into the machine
        :param tape: tape containing string to be processed
        :return:
        """
        if not set(str(tape)).issubset(self.tapealpha):
            raise InvalidCharacterInTape(set(str(tape)).difference(self.tapealpha))
        else:
            super().load(tape)

    def config(self, filepath: str) -> None:
        """
        configures the Turing Machine with a
        given config file. Config files are
        JSON formatted text files.
        :param filepath: file name and path to the config file
        :return:
        """
        with open(filepath, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.states = set(config[kSTATES_PREFIX])
            self.start = config[kSTART_PREFIX]
            if not self.start in self.states:
                raise InvalidConfigBlock("Start state not in states", self.start)
            self.accept = set(config[kACCEPT_PREFIX])
            if not self.accept.issubset(self.states):
                raise InvalidConfigBlock("Accepting state not subset states", self.accept)
            self.alpha = set(config[kALPHA_PREFIX])
            self.tapealpha = set(config[kTAPEALPHA_PREFIX])
            self.d_table = config[kDTABLE_PREFIX]
            for state in self.d_table.keys():
                for char in self.d_table[state].keys():
                    try:
                        trans = TMTransition(self.d_table[state][char])
                        if not trans.state in self.states:
                            raise InvalidConfigBlock("TMTransition not in states", trans.state)
                        if not trans.character in self.tapealpha:
                            raise InvalidConfigBlock("TMTransition not in tapealpha", trans.character)
                        if not trans.direction in set([kLEFT, kRIGHT]):
                            raise InvalidConfigBlock("TMTransition not in directions", trans.direction)
                        self.d_table[state][char] = trans

                    except KeyError:
                        pass
        self.reset()

    def __get_t(self, state: str, character: str) -> TMTransition:
        """
        lookup function for the TM delta table.
        Returns a TMTransition dictating the
        next state of the TM.
        :param state: state to lookup
        :param character: character to lookup
        :return: the transition for this lookup
        """
        try:
            trans = self.d_table[state][character]
        except KeyError:
            raise TMTransitionUndefined(state, character)
        return trans

    def get_c(self) -> str:
        """
        generates a configuration string for the
        current state of the machine. Configuration
        strings consist of the contents of the tape,
        with the current state embedded at the position
        of the head
        :return: the configuration string
        """
        ret_val = "{0}{1}{2}".format(str(self.loaded_tape)[:self.current_position], \
                                     str(self.current_state), \
                                     str(self.loaded_tape)[self.current_position:])
        return ret_val

    def step(self) -> str:
        """
        performs a single step of the TM's execution
        returns a string detailing the resulting
        configuration
        :return: configuration string
        """
        trans = self.__get_t(self.current_state, self.loaded_tape.read(self.current_position))
        self.current_state = trans.state
        self.loaded_tape.write(trans.character, self.current_position)
        if trans.direction == kRIGHT:
            self.current_position += 1
        elif trans.direction == kLEFT:
            self.current_position -= 1

        ret_val = "⊢{0}".format(self.get_c())
        return ret_val

    def is_accepted(self) -> bool:
        """
        checks whether the current state of the machine
        is in an accepted state
        :return:
        """
        return self.current_state in self.accept

    def __gen_config(self) -> dict:
        """
        generates a configuration dictionary for output
        either to file or to std out
        :return: configuration dictionary
        """
        config = dict()
        config[kSTATES_PREFIX] = list(self.states)
        config[kSTATES_PREFIX].sort()
        config[kSTART_PREFIX] = self.start
        config[kACCEPT_PREFIX] = list(self.accept)
        config[kACCEPT_PREFIX].sort()
        config[kALPHA_PREFIX] = list(self.alpha)
        config[kALPHA_PREFIX].sort()
        config[kTAPEALPHA_PREFIX] = list(self.tapealpha)
        config[kTAPEALPHA_PREFIX].sort()
        config[kDTABLE_PREFIX] = collections.defaultdict(dict)
        for state in self.d_table.keys():
            for char in self.d_table[state].keys():
                try:
                    config[kDTABLE_PREFIX][state][char] = str(self.__get_t(state, char))
                except TMTransitionUndefined:
                    pass
        return config

    def export(self, filepath: str) -> None:
        """
        writes the TMs configuration (states, alpha,
        etc.) to a file.
        :param filepath: file path and name
        :return:
        """
        with open(filepath, "w+", encoding="utf-8") as f:
            json.dump(self.__gen_config(), f, indent=4, sort_keys=True, ensure_ascii=False)

    def exec(self) -> list:
        """
        performs an execution of the TM. TM
        runs until it halts either from:
        1. entering a final state
        2. entering a configuration without
        a exiting transition
        the execution is traces, with each step
        string being added in sequence. Finally,
        the accepted state of the machine is
        appended to the trace
        :return: trace list
        """
        self.reset()
        trace = list()
        # initial config
        trace.append(self.get_c())
        while True:
            try:
                trace.append(self.step())
                if self.is_accepted():
                    break
            except TMTransitionUndefined:
                break
        if self.is_accepted() and self.accept != set():
            trace.append("Accepted: {0}".format(str(self.loaded_tape).replace(kBLANK, " ")))
        elif self.accept != set():
            trace.append("Rejected: {0}".format(str(self.loaded_tape).replace(kBLANK, " ")))
        else:
            trace.append("Halted: {0}".format(str(self.loaded_tape).replace(kBLANK, " ")))
        return trace

    def reset(self) -> None:
        self.current_state = self.start
        self.current_position = 0

    def __init__(self, filepath=None):
        """
        instantiates a member of the TM class
        :param filepath: file path and name
        """
        self.current_state = None
        self.current_position = 0
        self.loaded_tape = None
        if filepath:
            self.config(filepath)

    def dumps(self) -> str:
        """
        dumps the configuration of the TM to a
        JSON formatted string
        :return: json config
        """
        return json.dumps(self.__gen_config(), indent=4, sort_keys=True, ensure_ascii=False)


class DFA(Machine):
    def __init__(self, filepath=None):
        self.states = None
        self.alpha = None
        self.d_table = None
        self.start = None
        self.accept = None
        super().__init__(filepath)

    def config(self, filepath):

        file_exists = False

        # open filepath
        with open(filepath, encoding='utf-8') as f:
            file_exists = True
            configuration = json.load(f)

            # validate config
            config_valid = True

            # check blocks
            needed_configs = {kSTATES_PREFIX, kALPHA_PREFIX, \
                              kDTABLE_PREFIX, kSTART_PREFIX, \
                              kACCEPT_PREFIX}
            all_blocks_present = needed_configs == set(configuration.keys())
            if not all_blocks_present:
                raise MissingConfigBlock(set(configuration.keys()).difference(needed_configs))

            # checking configs
            invalid_config_blocks = list()

            # is states a set
            states_are_set = (len(configuration[kSTATES_PREFIX]) == len(set(configuration[kSTATES_PREFIX])))
            config_valid &= states_are_set
            if not states_are_set:
                invalid_config_blocks.append(kSTATES_PREFIX)
            pass

            # is alpha a set
            alpha_is_set = (len(configuration[kALPHA_PREFIX]) == len(set(configuration[kALPHA_PREFIX])))
            config_valid &= alpha_is_set
            if not alpha_is_set:
                invalid_config_blocks.append(kALPHA_PREFIX)
            pass

            # is d-table defined for all states/symbols
            # for every state
            # for evert alpha
            # state is defined
            states = set(configuration[kSTATES_PREFIX])
            alpha = set(configuration[kALPHA_PREFIX])
            d_table = configuration[kDTABLE_PREFIX]
            missing_dtable_elements = list()
            d_table_valid = True
            try:
                for this_state in states:
                    for this_alpha in alpha:
                        if not (d_table[this_state][this_alpha] in states):
                            missing_dtable_elements.append((this_state, this_alpha, d_table[this_state][this_alpha]))
                            d_table_valid = False
            except KeyError as e:
                d_table_valid = False
                missing_dtable_elements.append(e)
            if not d_table_valid:
                invalid_config_blocks.append((kDTABLE_PREFIX, missing_dtable_elements))
            config_valid &= d_table_valid
            pass

            # is accepting subset of states
            accept = set(configuration[kACCEPT_PREFIX])
            accept_is_subset = accept.issubset(states)
            config_valid &= accept_is_subset
            if not accept_is_subset:
                invalid_config_blocks.append(kACCEPT_PREFIX)
            pass

            # is starting state element of states
            start = configuration[kSTART_PREFIX]
            start_in_states = start in states
            config_valid &= start_in_states
            if not start_in_states:
                invalid_config_blocks.append(kSTART_PREFIX)
            pass

            if not config_valid:
                raise InvalidConfigBlock(invalid_config_blocks)
            pass

            # configure DFA

            # set states
            self.states = copy.deepcopy(states)

            # set alpha
            self.alpha = copy.deepcopy(alpha)

            # set d-table
            self.d_table = copy.deepcopy(d_table)

            # set starting-state
            self.start = copy.deepcopy(start)

            # set accepting-states
            self.accept = copy.deepcopy(accept)
        if not file_exists:
            raise FileNotFoundError

    def __config(self) -> dict:
        config = {}
        config[kSTATES_PREFIX] = list(self.states)
        config[kALPHA_PREFIX] = list(self.alpha)
        config[kDTABLE_PREFIX] = self.d_table
        config[kSTART_PREFIX] = self.start
        config[kACCEPT_PREFIX] = list(self.accept)
        return config

    def export(self, filepath):
        # generate a config
        with open(filepath, "w+", encoding='utf-8') as f:
            json.dump(self.__config(), f, sort_keys=True, indent=4, ensure_ascii=False)
        pass

    def dumps(self) -> str:
        return json.dumps(self.__config(), sort_keys=True, indent=4, ensure_ascii=False)

    def exec(self) -> dict:
        self.current_state = self.start
        self.current_position = 0
        ret = dict()
        output = ""
        try:
            while True:
                char = self.loaded_tape.read(self.current_position)
                output += "state: {0}, ".format(self.current_state)
                output += "character: {0}, ".format(char)
                self.current_state = self.d_table[self.current_state][self.loaded_tape.read(self.current_position)]
                output += "new state: {0}\n".format(self.current_state)
                self.current_position += 1
        except IndexError as e:
            if self.current_state in self.accept:
                output += "accepted {1}, state: {0}\n".format(self.current_state, str(self.loaded_tape))
                ret[kEXEC_ACCEPT] = True
            else:
                output += "rejected {1}, state: {0}\n".format(self.current_state, str(self.loaded_tape))
                ret[kEXEC_ACCEPT] = False
        except KeyError as e:
            output = "rejected {0}, invalid character on tape: {1}\n".format(str(self.loaded_tape), e)
            raise InvalidCharacterInTape(*e.args)

        ret[kEXEC_OUTPUT] = output
        ret[kEXEC_TAPE] = str(self.loaded_tape)
        return ret


class InvalidCharacterInTape(Exception):
    pass


class NFAlambda(Machine):
    def __init__(self, filepath=None):
        self.states: set = None
        self.alpha: set = None
        self.d_table: dict = None
        self.start: str = None
        self.accept: set = None
        super().__init__(filepath)

    def config(self, filepath):
        with open(filepath, encoding='utf-8') as f:
            configuration = json.load(f)

            # check needed blocks
            needed_configs = {kSTATES_PREFIX, kALPHA_PREFIX, \
                              kDTABLE_PREFIX, kSTART_PREFIX, \
                              kACCEPT_PREFIX}
            all_blocks_present = needed_configs == set(configuration.keys())
            if not all_blocks_present:
                raise MissingConfigBlock(set(configuration.keys()).difference(needed_configs))

            # validate blocks
            self.states = set(configuration[kSTATES_PREFIX])
            if self.states == set():
                raise InvalidConfigBlock(kSTATES_PREFIX, self.states)
            self.alpha = set(configuration[kALPHA_PREFIX])
            if self.alpha == set():
                raise InvalidConfigBlock(kALPHA_PREFIX, self.alpha)
            self.d_table = configuration[kDTABLE_PREFIX]
            for this_state in self.d_table.keys():
                for this_char in self.d_table[this_state].keys():
                    if self.d_table[this_state][this_char] == kEMPTYSET:
                        self.d_table[this_state][this_char] = set()
                    else:
                        self.d_table[this_state][this_char] = set(self.d_table[this_state][this_char])
                        if not self.d_table[this_state][this_char].issubset(self.states):
                            raise InvalidConfigBlock(kDTABLE_PREFIX, self.d_table[this_state][this_char])
            self.start = configuration[kSTART_PREFIX]
            if not self.start in self.states:
                raise InvalidConfigBlock(kSTART_PREFIX, self.start)
            self.accept = set(configuration[kACCEPT_PREFIX])
            if not self.accept.issubset(self.states):
                raise InvalidConfigBlock(kACCEPT_PREFIX, self.accept)

    def __config(self) -> dict:
        config = {}
        config[kSTATES_PREFIX] = list(self.states)
        config[kALPHA_PREFIX] = list(self.alpha)
        config[kDTABLE_PREFIX] = collections.defaultdict(dict)
        for this_state in self.states:
            for this_char in self.alpha:
                output_list = list(self.d_table[this_state][this_char])
                if len(output_list) == 0:
                    output_list = kEMPTYSET
                config[kDTABLE_PREFIX][this_state][this_char] = output_list
        config[kSTART_PREFIX] = self.start
        config[kACCEPT_PREFIX] = list(self.accept)
        return config

    def export(self, filepath):
        with open(filepath, "w+", encoding='utf-8') as f:
            json.dump(self.__config(), f, sort_keys=True, indent=4, ensure_ascii=False)

    def dumps(self) -> str:
        return json.dumps(self.__config(), sort_keys=True, indent=4, ensure_ascii=False)

    def exec(self):
        raise AttributeError("exec disabled for NFAlambda")

    def lambda_closure2(self, state) -> set:
        """
        stack based lambda closure
        :param state:
        :return:
        """
        # basis
        if type(state) == str:
            lc = {state}
        else:
            lc = state
        state_stack = list(lc)
        while len(state_stack) != 0:
            current_state = state_stack.pop()
            possible_additions = self.d_table[current_state][kLAMBA]
            if possible_additions == set():
                continue
            for this_state in possible_additions:
                if not this_state in lc:
                    lc.add(this_state)
                    state_stack.append(this_state)
        return lc

    def lambda_closure(self, state) -> set:
        """
        recursive lambda closure
        :param state:
        :return:
        """
        lc = set()
        if type(state) == set:
            for this_state in state:
                lc = lc.union(self.lambda_closure2(this_state))
        else:
            lc = {state}
            lambda_trans = self.d_table[state][kLAMBA]
            if not lambda_trans == set():
                for this_l_t in lambda_trans:
                    lc = lc.union(self.lambda_closure2(this_l_t))
        return lc

    def t_table(self) -> dict:
        t_table = collections.defaultdict(dict)
        reduced_alpha = copy.deepcopy(self.alpha)
        reduced_alpha.remove(kLAMBA)
        for this_state in self.states:
            for this_char in reduced_alpha:
                working_set = set()
                lc = self.lambda_closure(this_state)
                for state in lc:
                    possible_transitions = self.lambda_closure(self.d_table[state][this_char])
                    working_set = working_set.union(possible_transitions)
                t_table[this_state][this_char] = working_set

        return t_table

    def dumps_ttable(self) -> str:
        t_table = self.t_table()
        for this_state in t_table.keys():
            for this_key in t_table[this_state].keys():
                item = t_table[this_state][this_key]
                if type(item) == set:
                    t_table[this_state][this_key] = list(item)
        return json.dumps(t_table, sort_keys=True, indent=4, ensure_ascii=False)

    def convert(self) -> DFA:
        # empty DFA
        Mprime = DFA()
        # init q0
        # Mprime.start = copy.deepcopy(self.start)
        Mprime.start = Node(self.lambda_closure(self.start)).label
        # init sigma'
        Mprime.alpha = copy.deepcopy(self.alpha)
        Mprime.alpha.remove(kLAMBA)
        # empty dtable
        Mprime.d_table = collections.defaultdict(dict)

        t_table = self.t_table()

        # init the nodes list
        nodes = set()
        nodes.add(Node(self.lambda_closure(self.start)))
        completed_nodes = set()

        # start loop
        bDone = False
        while not bDone:
            try:
                this_node = nodes.pop()
            except KeyError as e:
                # out of nodes
                bDone = True
                continue
            for this_char in Mprime.alpha:
                X = this_node
                a = this_char
                Y_set = set()
                for this_state in X.set:
                    Y_set = Y_set.union(self.lambda_closure(t_table[this_state][a]))
                Y = Node(Y_set)

                # looping to itself
                if hash(Y) == hash(X):
                    Y = X
                # arcing to an existing node
                elif Y in nodes or Y in completed_nodes:
                    if Y in nodes:
                        for a_node in nodes:
                            if hash(a_node) == hash(Y):
                                Y = a_node
                                break
                    else:
                        for a_node in completed_nodes:
                            if hash(a_node) == hash(Y):
                                Y = a_node
                                break
                # arcing to a new node
                else:
                    nodes.add(Y)
                X.set_d_table_entry(a, Y)
            completed_nodes.add(this_node)

        # now that we have the nodes, fill in the table, states and accepting
        Mprime.states = set()
        Mprime.accept = set()
        for this_node in completed_nodes:
            # add the state to Q
            Mprime.states.add(this_node.label)
            # fill out the d_table
            for this_char in Mprime.alpha:
                Mprime.d_table[this_node.label][this_char] = this_node.get_d_table_entry(this_char).label
            if self.accept.intersection(this_node.set):
                Mprime.accept.add(this_node.label)

        return Mprime


class Node:
    def __init__(self, this_set: set):
        self.set: set = this_set
        self.label: str = self.set2node(self.set)
        self.d_table_entry: dict = {}
        # self.complete = False

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return "Node: {0}".format(self.label)

    def __eq__(self, other):
        if hash(self) == hash(other):
            return True
        else:
            return False

    # def completed(self):
    #     self.complete = True

    # def is_complete(self):
    #     return self.complete

    def set2node(self, _set: set) -> str:
        temp = ""
        temp_list = list()
        for this_item in _set:
            temp_list.append(this_item)
        temp_list.sort()
        for a in temp_list:
            temp += a
        if temp == "":
            temp = kEMPTYSET
        return temp

    def set_d_table_entry(self, _a: str, _node: "Node"):
        self.d_table_entry[_a] = _node

    def get_d_table_entry(self, _a: str) -> "Node":
        try:
            ret = self.d_table_entry[_a]
        except KeyError:
            ret = None
        return ret


class MissingConfigBlock(Exception):
    pass


class InvalidConfigBlock(Exception):
    pass


class Tape:
    def __getitem__(self, item: int) -> str:
        return self.read(item)

    def __setitem__(self, key: int, value: str) -> None:
        self.write(value, key)

    def __add__(self, other: "Tape") -> "Tape":
        return Tape(str(self) + str(other))

    def __init__(self, in_string):
        self.characters = list(in_string)

    def __str__(self):
        contents = ""
        for a in self.characters:
            contents += a
        return contents

    def read(self, position):
        return self.characters[position]

    def write(self, character, position):
        self.characters[position] = character


class TMTape(Tape):
    """
    Implements an infinite tape for use in
    Turing Machines
    """

    def __getitem__(self, item: int) -> str:
        return super().read(item)

    def __setitem__(self, key: int, value: str) -> None:
        return super().write(value, key)

    def __add__(self, other: "TMTape") -> "TMTape":
        return TMTape(str(self).lstrip(kBLANK) + str(other).rstrip(kBLANK))

    def write(self, character: str, position: int) -> None:
        """
        writes a character to a specified position
        on the tape.
        :param character: character to be added to the string
        :param position: index of the location to add the character
        :return:
        """
        if position == 0:
            self.pos_index[0] = character
            self.neg_index[0] = character
        elif position > 0:
            try:
                self.pos_index[position] = character
            except IndexError:
                for i in range(position - len(self.pos_index) + 1):
                    self.pos_index.append(kBLANK)
                self.pos_index[position] = character
        else:
            try:
                self.neg_index[-position] = character
            except IndexError:
                for i in range((-position) - len(self.neg_index) + 1):
                    self.neg_index.append(kBLANK)
                self.neg_index[-position] = character

    def __str__(self) -> str:
        """
        returns a string of the contents of the tape
        :return: tape string
        """
        neg_str = ""
        pos_str = ""
        for character in self.neg_index[1:]:
            neg_str = character + neg_str
        for character in self.pos_index[0:]:
            pos_str = pos_str + character
        if (pos_str[-1] != kBLANK):
            pos_str += kBLANK
        try:
            if (neg_str[-1] != kBLANK):
                neg_str = kBLANK + neg_str
        except IndexError:
            pass
        return "{0}{1}".format(neg_str, pos_str)

    def read(self, position: int) -> str:
        """
        gets the character at the specified position.
        because the tape is infinite, if it's outside
        of the previously specified range, returns a
        blank character
        :param position: index to read
        :return: the character at that position
        """
        try:
            if position >= 0:
                return self.pos_index[position]
            else:
                return self.neg_index[-position]
        except IndexError:
            # self.write(kBLANK, position)
            return kBLANK

    def __init__(self, in_string):
        """
        returns an instance of the TMtape class
        based on the input string
        :param in_string:
        """
        self.neg_index = list()
        self.pos_index = list()
        self.pos_index.append(kBLANK)
        for character in in_string:
            self.pos_index.append(character)
        self.pos_index.append(kBLANK)
        self.neg_index.append(kBLANK)


if __name__ == "__main__":
    filepath = os.path.join("..", "configs", "ex_821.tm")
    myMT = TM(filepath)
    myTape = TMTape("aa")
    myMT.load(myTape)
    # print(myMT.get_c())
    for config in myMT.exec():
        print(config)
        # print(myMT.dumps())
