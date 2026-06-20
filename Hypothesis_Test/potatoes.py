# wassup 

from datascience import *
import numpy as np
import random

def og_format(table):
    table = table.drop(0)
    table = table.relabeled(0, 'City Name').relabeled(1, 'Temperature').relabeled(2, 'Location').relabeled(3, 'Population').relabeled(4, 'Port?')
    return table

def sim_format(table):
    table = table.drop(0)
    table = table.relabeled(0, 'Simulation').relabeled(1, 'Simulated Location').relabeled(2, 'Temperature')
    return table

def sheets_import(sims_include=False):
    sheet_id = "1pVxVW3ucfYS2lWgeX7avVoMvs5e2km21jGva4fTKhx4"
    gid_og = "750705596"
    gid_sim = "464666027"
    csv_og = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid_og}"
    csv_sim = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid_sim}"
    if sims_include == False:
        return og_format(Table.read_table(csv_og))
    else:
        return og_format(Table.read_table(csv_og)), sim_format(Table.read_table(csv_sim))
    