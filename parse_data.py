"""
JRHB Water Testing


"""

from pandas import read_csv
from pandas import to_datetime
import numpy as np

from plotting import StackedArea

df = read_csv('data.csv')

SO4CL_RATIO = {
    0: 'Too Malty',
    0.4: 'Very Malty',
    .6: 'Malty',
    .8: 'Balanced',
    1.5: 'Little Bitter',
    2.01: 'More Bitter',
    4.01: 'Extra Bitter',
    6.01: 'Quite Bitter',
    8.01: 'Very Bitter',
    9.01: 'Too Bitter'
}

# Add calculated columns
df['mg_hardness'] = df['total_hardness'] - df['ca_hardness']
df['res_alkalinity'] = df['total_alkalinity'] - (df['ca_hardness']/3.5 + df['mg_hardness']/7)
df['ca2'] = df['ca_hardness'] * 0.4
df['mg2'] = df['mg_hardness'] * 0.25
df['hco3'] = df['total_alkalinity'] * 1.22
df['so4_cl'] = df['so4'] / df['cl']

# Add descriptor from SO4 / Cl Ratio Lookup
set_ratio = [min(SO4CL_RATIO.keys(), key=lambda x: abs(x - r)) for r in df['so4_cl']]
ratios = [SO4CL_RATIO[value] for value in set_ratio]

df['balance'] = ratios

df['sample_date'] = to_datetime(df['sample_date'])
df = df.sort_values(by='sample_date')

# Plots Needed

## Hardness over time (Total, Ca, Mg)
locations = df.charting.unique()

for location in locations:
    print('<h1>{}</h1>'.format(location))
    filtered = df[df.charting == location]

    StackedArea(
        filtered['sample_date'],
        [filtered['ca_hardness'], filtered['mg_hardness']],
        ['Ca Hardness', 'Mg Hardness'],
        filtered.id
    )


## Alkalinity over time (Total, Residual)

## Ion Concentrations over time (Cl-, SO4-, Ca2+, Mg2+, HCO3-)

## SO4/Cl Ratio over time

## pH over time
