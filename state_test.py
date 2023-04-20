class State_manager:
    

    def __init__(self) -> None:
        self.state = None

state1 = 0b00000001
state2 = 0b00000010
state1and2 = 0b00000011

print (state1 + state2 == state1and2)