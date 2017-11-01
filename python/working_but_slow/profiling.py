import pstats
p = pstats.Stats('prof.txt')
p.strip_dirs().sort_stats('tottime').print_stats()