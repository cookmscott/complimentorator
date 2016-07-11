import random
import csv 
with open('./compliment_bank/compliment_list.txt', 'rb') as f:
    reader = csv.reader(f)
    compliment_list = list(reader)

# function to return position of randomly weighted selection
def weighted_choice(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i

# get all weights and convert to int
compliment_weights = [ int(s) for s in zip(*compliment_list)[0] ]
# select a compliment
compliment_pos = weighted_choice(compliment_weights)
# get compliment text
compliment = compliment_list[compliment_pos][1]

print compliment
