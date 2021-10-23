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


def write_index(prev_prefix, prefix, line, index, i):
    if prev_prefix != '' and int(prefix, 16) - int(prev_prefix, 16) != 1:
        raise Exception('unexpected gap in data')

    postfix = '0' + line[5:40]
    index.write(bytes.fromhex(postfix))
    index.write(i.to_bytes(8, byteorder='little'))


with open('passwords-wip.bin', 'wb') as passwords, open('index-wip.bin', 'wb') as index:
    i = 0
    prev_prefix = ''
    for line in sys.stdin:
        checksum = bytes.fromhex(line[:40])
        occurences = int(line[41:-1])
        occurences = min(occurences, 255)

        passwords.write(checksum)
        passwords.write(occurences.to_bytes(1, byteorder='little'))

        prefix = line[:5]
        if prefix != prev_prefix:
            write_index(prev_prefix, prefix, line, index, i)
            prev_prefix = prefix

        i = i + 1
        if i % 100000 == 0:
            report_progress(checksum, i)
