import ast

# ruleid: B307
eval("1+1")
# ruleid: B307
print(eval(data))
# ok: B307
ast.literal_eval(data)
# ok: B307
obj.eval(data)
# ok: B307
eval(data)  # nosec
# ok: B307
eval(data)  # nosec eval
# ruleid: B307
eval("#nosec")
# ruleid: B307
eval(data)  # nosec B301
