import sys
import time


start = int(time.time())
def report_progress(checksum, i):
    global start

    now = int(time.time())

    current = int.from_bytes(checksum[:4], byteorder='big')
    last = int.from_bytes(b'\xff\xff\xff\xff', byteorder='big')
    progress = current / last

    if progress < 0.00001:
        return

    elapsed = now - start
    total = elapsed / progress
    eta = start + total

    if elapsed == 0:
        return

    eta_hr = time.strftime('%H:%M', time.localtime(eta))
    percent = progress * 100
    speed = i / elapsed / 1000

    out = f'done={percent:4.1f}% speed={speed:4.0f}k/s ETA={eta_hr}'

    print(f'\r{out}    ', file=sys.stderr, end='')


i = 0
output = sys.stdout.buffer
for line in sys.stdin:
    checksum = bytes.fromhex(line[:40])
    occurences = int(line[41:-1])
    occurences = min(occurences, 255)

    output.write(checksum)
    output.write(occurences.to_bytes(1, byteorder='little'))

    i = i + 1
    if i % 100000 == 0:
        report_progress(checksum, i)
