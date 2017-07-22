import random



in_file = open('wordlist', 'r')
lines = in_file.readlines()[:800]
in_file.close()

out_file = open('../.todo', 'a')

for j in range(4, len(lines), 4):
    label = lines[j].rstrip() + ' '
    label += lines[j - 1].rstrip() + ' '
    label += lines[j - 2].rstrip() + ' '
    label += lines[j - 3].rstrip()
    out_file.write('\n- [' + label + ', ' + str(random.randrange(1, 8)) + ']')

out_file.close()

