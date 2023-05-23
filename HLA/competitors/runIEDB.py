#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
IEDB-AR MHC I binding prediction
https://doi.org/10.1093%2Fnar%2Fgkz452
http://tools.iedb.org/mhci/download/

Usage: predict_binding.py method allele or [options] arg length
---
Following are the available choices -
   method: ann, comblib_sidney2008, consensus, IEDB_recommended, netmhcpan_ba, netmhcpan_el, smm, smmpmbec, pickpocket, netmhccons, netmhcstabpan
   allele: an allele name
   length: a length

Options:
  --version       show program's version number and exit
  -h, --help      show this help message and exit
  -v, --versions  print specific methods and their versions.
  -m FILE         FILE containing a single MHC sequence in fasta format.
'''
