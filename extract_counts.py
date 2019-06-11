import yaml
import glob
import uproot
import numexpr as ne
import numpy as np
import formulate
import json
from awkward.array.table import Table


def extract_histo(sample, regions):
    chunk_generator = uproot.iterate(
            glob.glob(sample['glob']),
            branches = ['n_*','*weight*'],
            treepath = sample['tree'],
            namedecode="utf-8",
    )
    
    histo, edges = None, None

    collect = {}
    for chunk in chunk_generator:
        for region in regions:
            region_key = region['name']
            binning = np.linspace(*region['binning'])

            collect.setdefault(region_key,{'counts': None,'edges': None})

            table = Table(chunk)
            expr = formulate.from_root(region['filter']).to_numexpr()
            selection = ne.evaluate(expr,Table(chunk))
            table = table[selection]

            expr = formulate.from_root(region['observable']).to_numexpr()
            observable = ne.evaluate(expr,table)


            is_data = sample.get('data',False)

            if not is_data:
                expr = formulate.from_root(sample['weight']).to_numexpr()
                weights = ne.evaluate(expr,table) * sample['lumi']
            else:
                weights = None

            chunk_histo, chunk_edges = np.histogram(observable, weights = weights, bins = binning)

            collect[region_key]['edges'] = chunk_edges

            histo = collect[region_key]['counts']
            collect[region_key]['counts'] = chunk_histo if histo is None else histo + chunk_histo
    for _,v in collect.items():
        for x,a in v.items():
            v[x] = a.tolist()
    return collect


data = yaml.load(open('spec.yml'))

extracted = {}
for sample in data['samples']:
    for variation in sample['variations']:
        histos = extract_histo(variation, data['regions'])
        extracted.setdefault(sample['name'],{})[variation['name']] = histos

json.dump(extracted,open('counts.json','w'))