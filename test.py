class Test:
    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b
        self.stuff = [self.a, self.b]
    

test = Test(1, 2)
print(test.stuff)
test.a = 10
print(test.stuff)