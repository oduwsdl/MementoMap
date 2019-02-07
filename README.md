# MementoMap

A framework of web archive profiling to express holdings of an archive

```
$ ./main.py
usage: main.py [-h] {generate,compact,lookup,batchlookup} ...

positional arguments:
  {generate,compact,lookup,batchlookup}
    generate            Generate a MementoMap from a sorted file with the
                        first columns as SURT (e.g., CDX/CDXJ)
    compact             Compact a large MementoMap file into a small one
    lookup              Look for a SURT into a MementoMap
    batchlookup         Look for a SURT into a MementoMap

optional arguments:
  -h, --help            show this help message and exit
```

```
$ ./main.py generate -h
usage: main.py generate [-h] [--hcf] [--pcf] [--ha] [--pa] [--hk] [--pk]
                        [--hdepth] [--pdepth]
                        infile outfile

positional arguments:
  infile      Input SURT/CDX/CDXJ (plain or GZip) file path or '-' for STDIN
  outfile     Output MementoMap file path

optional arguments:
  -h, --help  show this help message and exit
  --hcf       Host compaction factor (deafault: Inf)
  --pcf       Path compaction factor (deafault: Inf)
  --ha        Power law alpha parameter for host (default: 16.329)
  --pa        Power law alpha parameter for path (default: 24.546)
  --hk        Power law k parameter for host (default: 0.714)
  --pk        Power law k parameter for path (default: 1.429)
  --hdepth    Max host depth (default: 8)
  --pdepth    Max path depth (default: 9)
```

```
$ ./main.py compact -h
usage: main.py compact [-h] [--hcf] [--pcf] [--ha] [--pa] [--hk] [--pk]
                       [--hdepth] [--pdepth]
                       infile outfile

positional arguments:
  infile      Input MementoMap (plain or GZip) file path or '-' for STDIN
  outfile     Output MementoMap file path

optional arguments:
  -h, --help  show this help message and exit
  --hcf       Host compaction factor (deafault: 1.0)
  --pcf       Path compaction factor (deafault: 1.0)
  --ha        Power law alpha parameter for host (default: 16.329)
  --pa        Power law alpha parameter for path (default: 24.546)
  --hk        Power law k parameter for host (default: 0.714)
  --pk        Power law k parameter for path (default: 1.429)
  --hdepth    Max host depth (default: 8)
  --pdepth    Max path depth (default: 9)
```

```
$ ./main.py lookup -h
usage: main.py lookup [-h] mmap surt

positional arguments:
  mmap        MementoMap file path to look into
  surt        SURT to look for

optional arguments:
  -h, --help  show this help message and exit
```

```
$ ./main.py batchlookup -h
usage: main.py batchlookup [-h] mmap infile

positional arguments:
  mmap        MementoMap file path to look into
  infile      Input SURT (plain or GZip) file path or '-' for STDIN

optional arguments:
  -h, --help  show this help message and exit
```
