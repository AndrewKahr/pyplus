# Example script demonstrating loop translation behavior

# Currently can translate while loops
index = 0
while index < 10:
    print(index)
    index = index + 1

# Break and Continue are also translated
index = 0
while True:
    if index > 10:
        break
    else:
        print(index)
        index = index + 1   # increment index to avoid infinite loop
        continue
