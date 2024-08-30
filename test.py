a = 0
b = 0
for letter in "Hello":
    if letter.lower() in "aiueo":
        a = a + 1
    else:
        b = b + 1
        
print(a,b)