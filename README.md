# MementoMap

A framework of web archive profiling to express summary of the holdings of an archive.

```
$ pip install mementomap
```

```
$ mementomap
usage: mementomap [-h] {generate,compact,lookup,batchlookup} ...

positional arguments:
  {generate,compact,lookup,batchlookup}
    generate            Generate a MementoMap from a sorted file with the
                        first columns as SURT (e.g., CDX/CDXJ)
    compact             Compact a large MementoMap file into a small one
    lookup              Look for a SURT into a MementoMap
    batchlookup         Look for a list of SURTs into a MementoMap

optional arguments:
  -h, --help            show this help message and exit
```

```
$ mementomap generate -h
usage: mementomap generate [-h] [--hcf] [--pcf] [--ha] [--pa] [--hk] [--pk]
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
$ mementomap compact -h
usage: mementomap compact [-h] [--hcf] [--pcf] [--ha] [--pa] [--hk] [--pk]
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
$ mementomap lookup -h
usage: mementomap lookup [-h] mmap surt

positional arguments:
  mmap        MementoMap file path to look into
  surt        SURT to look for

optional arguments:
  -h, --help  show this help message and exit
```

```
$ mementomap batchlookup -h
usage: mementomap batchlookup [-h] mmap infile

positional arguments:
  mmap        MementoMap file path to look into
  infile      Input SURT (plain or GZip) file path or '-' for STDIN

optional arguments:
  -h, --help  show this help message and exit
```


## Citing Project

A publication related to this project appeared in the proceedings of JCDL 2019 ([Read the PDF](https://arxiv.org/pdf/1905.12607.pdf)). Please cite it as below:

> Sawood Alam, Michele C. Weigle, Michael L. Nelson, Fernando Melo, Daniel Bicho, Daniel Gomes. __MementoMap Framework for Flexible and Adaptive Web Archive Profiling__. In _Proceedings of the 19th ACM/IEEE-CS on Joint Conference on Digital Libraries, JCDL 2019_, pp. 172-181, Urbana-Champaign, Illinois, USA, June 2016.

```latex
@inproceedings{jcdl-2019:alam:mementomap,
  author    = {Sawood Alam and
               Michele C. Weigle and
               Michael L. Nelson and
               Fernando Melo and
               Daniel Bicho and
               Daniel Gomes},
  title     = {{MementoMap} Framework for Flexible and Adaptive Web Archive Profiling},
  booktitle = {Proceedings of the 19th {ACM/IEEE-CS} Joint Conference on Digital Libraries},
  series    = {JCDL '19},
  year      = {2019},
  month     = {jun},
  location  = {Urbana-Champaign, Illinois, USA},
  pages     = {172--181},
  numpages  = {10},
  url       = {https://doi.org/10.1109/JCDL.2019.00033},
  doi       = {10.1109/JCDL.2019.00033},
  isbn      = {978-1-7281-1547-4},
  publisher = {{IEEE}}
}
```
