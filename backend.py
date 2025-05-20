blocks = {
"block_1": 1,
"block_2": 2,
"block_3": 1,
"block_4": 2,
"block_5": 3,
"block_6": 3,
}

while blocks:
    print("Available blocks:")
    for block in blocks:
        print(block)

    choice1 = input("What's your first choice? ")

    if choice1 in blocks:
        print(f"You selected {choice1}, which has value {blocks[choice1]}")
    else:
        print("Invalid block selected. Please try again.")

    choice2 = input("What's your second choice? ")

    if choice2 in blocks:
        print(f"You selected {choice2}, which has value {blocks[choice2]}")
    else:
        print("Invalid block selected. Please try again.")

    if blocks[choice1] == blocks[choice2]:
        print("Congratulations! It's a match.")
        del blocks[choice1]
        del blocks[choice2]
    else:
        print("Not a match. Retry!")

        
print("Congratulations! YOu have won!!!")

