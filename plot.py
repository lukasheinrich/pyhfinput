import numpy as np
import matplotlib
matplotlib.use('PS')

import matplotlib.pyplot as plt
import json

region = 'regionA'

data = json.load(open('counts.json'))

d = data['data']['nominal'][region]


bottom = None

mc = {k:v for k,v in data.items() if k!='data'}

for k,v in mc.items():
    e = np.asarray(v['nominal'][region]['edges'])
    wdt  = (e[1:]-e[:-1])
    ctrs = e[:-1]+wdt/2.

    counts = np.asarray(v['nominal'][region]['counts'])
    plt.bar(ctrs,counts,
        width = wdt,
        alpha = 1.0,
        bottom = np.zeros_like(counts) if bottom is None else bottom, 
        label = k
    )

    bottom = counts if bottom is None else bottom + counts


e = np.asarray(d['edges'])
wdt  = (e[1:]-e[:-1])
ctrs = e[:-1]+wdt/2.
plt.scatter(ctrs,d['counts'], c = 'k', zorder = 999, label = 'data')
plt.legend()
plt.savefig('plot.png')