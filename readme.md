# HIBP self-hosted

Self-hosted version of haveibeenpwned leaked passwords database. Requires 4MB of RAM and just single disk read to check a password.

## How to use it

1. Download the 7z file with password hashes from haveibeenpwned.com website or preferably [via torrent](https://downloads.pwnedpasswords.com/passwords/pwned-passwords-sha1-ordered-by-hash-v7.7z.torrent).
1. Move the file to `data` directory.
1. Run `make build`. You need `7z` installed. This will build packed version of the passwords file (12GB) and will take some time.
1. Run `make run`. This will run uvicorn web server.

Now you can check occurences of certain password hash:

    curl -X 'POST' \
      'http://127.0.0.1:8000/check' \
      -H 'Content-Type: application/json' \
      -d '{
      "sha1": "2AAE6C35C94FCFB415DBE95F408B9CE91EE846ED"
    }'

Or list all hashes with certain prefix. This endpoint mimics pwnedpasswords API. Note that prefix is truncated from output:

    curl http://127.0.0.1:8000/range/2AAE6

Or you can explore the API in browser: http://127.0.0.1:8000/docs

## Benchmark

The webserver will handle few 100s requests per second, depending on system configuration. The search itself can handle more, especially if run in parallel.

This table shows performance in lookups/s for single thread and peak parallel performance (number of parallel processes is in parenthesis).

|   | Single thread | Parallel |
| --- | --- | --- |
| Raspberry Pi 3 (sd card) | 682/s | 1360/s (3x) |
| 2009 Laptop | 1550/s | 3960/s (3x) |
| 2018 Laptop | 1835/s | 68160/s (48x) |

Lookup performance is HDD limited. You can expect parallel performance roughly the same as your disk has with 4K random reads.

Benchmark results match this: 2009 laptop SSD has around 16MB/s in 4K random reads (queue depth 32) which gives theoretical 4000 reads/s. 2018 laptop's SSD is much faster SK hynix SC311 with 389MB/s in 4KQD32 performance which means 97000 reads/s. Here the test results were less consistent, but still roughly in region of expected performance.

## Algorithm

Hashed data have interesting property of being more or less uniformly distributed. Therefore we can roll like it's 1957 and use [interpolation search](https://en.wikipedia.org/wiki/Interpolation_search). Generally speaking: If you search for `CCCC`, then you can expect it to be somewhere near 75% of the file and search around there.

That way you can do the search with 2-3 reads on the 12GB file.

This implementation uses additional 4MB index which sends you directly to ~10KB long chunk of data. Then the interpolation search requires just 1 read practically every time.
