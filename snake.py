import sys

if sys.implementation.name == "micropython":
    print("HI")
else:
    print("LOW")
    