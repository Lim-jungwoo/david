import multiprocessing as mp
import string, time, itertools

CHARSET = string.digits + string.ascii_lowercase
LENGTH = 6

def bench(ntries):
    j = ''.join
    t0 = time.perf_counter()
    for tup in itertools.islice(itertools.product(CHARSET, repeat=LENGTH), ntries):
        _ = j(tup)
    return ntries / (time.perf_counter() - t0)

if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)
    ctx = mp.get_context('spawn')
    N = 10_000_000
    for P in (2, 4, 6, 8, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30):
        with ctx.Pool(P) as pool:
            rates = pool.map(bench, [N]*P)
        total = sum(rates)
        print(f'{P} workers: {total:.0f} tries/s (per-core {total/P:.0f})')

