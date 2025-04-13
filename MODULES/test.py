import sys
print("Waiting for queries...")
sys.stdout.flush()

for line in sys.stdin:
    print('got line: {}'.format(line))
    sys.stdout.flush()