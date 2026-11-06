import ast

# ruleid: B307
eval("1 + 1")
# ruleid: B307
eval(user_input)
# ruleid: B307
print(eval("os.getcwd()"))
# ruleid: B307
eval("x", globals(), locals())
# ok: B307
ast.literal_eval("1")

class Test:
    def eval(self):
        pass

    def run(self):
        # ok: B307
        self.eval()

# ok: B307
Test().eval()
