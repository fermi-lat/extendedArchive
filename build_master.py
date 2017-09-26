from __future__ import absolute_import, division, print_function
import os
import sys
import copy
import numpy as np
import yaml
import xml.etree.cElementTree as ElementTree
from astropy.table import Table

def load_xml_elements(root, path):
    o = {}
    for p in root.findall(path):
        if 'name' in p.attrib:
            o[p.attrib['name']] = copy.deepcopy(p.attrib)
        else:
            o.update(p.attrib)
    return o


def from_xml(xmlfile):
    """Load spectral parameters from an XML file."""
    root = ElementTree.ElementTree(file=xmlfile).getroot()
    srcs = root.findall('source')
    if len(srcs) == 0:
        raise ValueError('Failed to find source in XML.')    
    src_type = srcs[0].attrib['type']
    spec = load_xml_elements(srcs[0], 'spectrum')
    spectral_pars = load_xml_elements(srcs[0], 'spectrum/parameter')
    spectral_type = spec['type']
    return spectral_pars
    

def strip_columns(tab):
    """Strip whitespace from string columns."""
    for colname in tab.colnames:
        if tab[colname].dtype.kind in ['S', 'U']:
            tab[colname] = np.core.defchararray.strip(tab[colname])


def main():
            
    tab = Table.read(sys.argv[1])

    rootdir = os.path.dirname(sys.argv[1])
    os.environ['LATEXTDIR'] = rootdir
    
    strip_columns(tab)
    o = {}

    for row in tab:

        src_dict = {}
        for c in row.colnames:
            c = str(c)        
            src_dict[c] = row[c]
            if isinstance(src_dict[c], np.number):
                src_dict[c] = src_dict[c].tolist()
            elif isinstance(src_dict[c], np.str):
                src_dict[c] = str(src_dict[c])

        if src_dict['Spatial_Function'] == 'RadialGauss':
            src_dict['Spatial_Function'] = 'RadialGaussian'                
        xmlpath = os.path.expandvars(src_dict['Spectral_Filename'])        
        pars_dict = from_xml(xmlpath)
        #del pars_dict['free']
        src_dict['Spectral_Parameters'] = pars_dict        
        o[str(row['Source_Name'])] = src_dict

    yaml.dump(o,open('test.yaml','w'),default_flow_style=False)


if __name__ == "__main__":
    main()
