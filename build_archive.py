from __future__ import absolute_import, division, print_function
import os
import re
import yaml
import argparse
import xml.etree.cElementTree as ElementTree
import numpy as np
from astropy.table import Table, Column
from astropy.coordinates import SkyCoord


def path_to_xmlpath(path):
    if path is None:
        return path

    return re.sub(r'\$([a-zA-Z\_]+)', r'$(\1)', path)


def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element.
    """
    from xml.dom import minidom
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def isstr(s):
    """String instance testing method that works under both Python 2.X
    and 3.X.  Returns true if the input is a string."""

    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)


def to_xml(xmlfile, name, src_dict):

    params = src_dict['Spectral_Parameters']
    spatial_type = src_dict['Spatial_Function']
    spectral_type = src_dict['Spectral_Function']
    defaults = {
        'Prefactor': {'scale': 1, 'name': 'Prefactor', 'free': 0, 'min': 1, 'max': 1},
        'RA': {'scale': 1, 'name': 'RA', 'free': 0, 'min': 0, 'max': 360},
        'DEC': {'scale': 1, 'name': 'DEC', 'free': 0, 'min': -90, 'max': 90},
        'Radius': {'scale': 1, 'name': 'Radius', 'free': 0, 'min': 0, 'max': 10},
        'Sigma': {'scale': 1, 'name': 'Sigma', 'free': 0, 'min': 0, 'max': 10},
    }

    if spatial_type == 'RadialDisk':
        params_spat = {'RA': defaults['RA'].copy(), 'DEC': defaults['DEC'].copy(),
                       'Radius': defaults['Radius'].copy()}
        params_spat['Radius']['value'] = np.sqrt(src_dict['Model_SemiMajor'] *
                                                 src_dict['Model_SemiMinor'])
        params_spat['RA']['value'] = src_dict['RAJ2000']
        params_spat['DEC']['value'] = src_dict['DEJ2000']
    elif spatial_type == 'RadialGaussian':
        params_spat = {'RA': defaults['RA'].copy(), 'DEC': defaults['DEC'].copy(),
                       'Sigma': defaults['Sigma'].copy()}
        params_spat['Sigma']['value'] = np.sqrt(src_dict['Model_SemiMajor'] *
                                                src_dict['Model_SemiMinor'])
        params_spat['Sigma']['value'] /= 1.5095921854516636
        params_spat['RA']['value'] = src_dict['RAJ2000']
        params_spat['DEC']['value'] = src_dict['DEJ2000']
    else:
        params_spat = { 'Prefactor' : defaults['Prefactor'] }

    root = ElementTree.Element('source_library')
    root.set('title', 'source_library')

    source_element = create_xml_element(root, 'source',
                                        dict(name=name,
                                             type='DiffuseSource'))

    #filename = utils.path_to_xmlpath(self.filefunction)
    spec = create_xml_element(source_element, 'spectrum',
                              dict(type=src_dict['Spectral_Function']))

    attrib = dict(type=spatial_type)
    if spatial_type == 'SpatialMap':
        attrib['file'] = path_to_xmlpath(src_dict['Spatial_Filename'])
        attrib['map_based_integral'] = 'true'
    
    spat = create_xml_element(source_element, 'spatialModel', attrib)

    for k, v in params.items():
        create_xml_element(spec, 'parameter', v)

    for k, v in params_spat.items():
        create_xml_element(spat, 'parameter', v)

    output_file = open(xmlfile, 'w')
    output_file.write(prettify_xml(root))


def create_xml_element(root, name, attrib):
    el = ElementTree.SubElement(root, name)
    for k, v in attrib.items():

        if isinstance(v, bool):
            el.set(k, str(int(v)))
        elif isstr(v):
            el.set(k, v)
        elif np.isfinite(v):
            el.set(k, str(v))

    return el


def set_coordinates(src_dict):

    has_cel = 'RAJ2000' in src_dict and 'DEJ2000' in src_dict
    has_gal = 'GLON' in src_dict and 'GLAT' in src_dict

    if not has_gal and not has_gal:
        raise Exception()

    if not has_gal:
        skydir = SkyCoord(src_dict['RAJ2000'], src_dict['RAJ2000'],
                          unit='deg', frame='icrs')
        skydir = skydir.transform_to('galactic')
        src_dict['GLAT'] = skydir.b.deg
        src_dict['GLON'] = skydir.l.deg


def main():

    usage = "usage: %(prog)s [archive file]"
    description = "Build the extended archive from the master archive YAML file."
    parser = argparse.ArgumentParser(usage=usage, description=description)

    parser.add_argument('--outdir', default=None, required=True)

    parser.add_argument('masterfile',
                        help='Extended archive master YAML file.')

    args = parser.parse_args()
    
    npar_max = 10
    o = yaml.load(open(args.masterfile))
    cols = [Column(name='Source_Name', dtype='S40'),
            Column(name='RAJ2000', dtype=float, unit='deg'),
            Column(name='DEJ2000', dtype=float, unit='deg'),
            Column(name='GLON', dtype=float, unit='deg'),
            Column(name='GLAT', dtype=float, unit='deg'),
            Column(name='Photon_Flux', dtype=float, unit='ph / (cm2 s)'),
            Column(name='Energy_Flux', dtype=float, unit='erg / (cm2 s)'),
            Column(name='Model_Form', dtype='S40'),
            Column(name='Model_SemiMajor', dtype=float, unit='deg'),
            Column(name='Model_SemiMinor', dtype=float, unit='deg'),
            Column(name='Model_PosAng', dtype=float, unit='deg'),
            Column(name='Spatial_Function', dtype='S40'),
            Column(name='Spectral_Function', dtype='S40'),
            Column(name='Spectral_Filename', dtype='S40'),
            Column(name='Name_1FGL', dtype='S18'),
            Column(name='Name_2FGL', dtype='S18'),
            Column(name='Name_3FGL', dtype='S18'),
            Column(name='Spatial_Filename', dtype='S50'),
            Column(name='Spectral_Param_Name', dtype='S40', shape=(npar_max,)),
            Column(name='Spectral_Param_Value',
                   dtype=float, shape=(npar_max,)),
            Column(name='Spectral_Param_Error',
                   dtype=float, shape=(npar_max,)),
            Column(name='Spectral_Param_Scale',
                   dtype=float, shape=(npar_max,)),
            ]

    tab = Table(cols)

    mkdir(args.outdir)
    xmldir = os.path.join(args.outdir, 'XML')
    mkdir(xmldir)

    for k, v in o.items():
        
        set_coordinates(v)
        row = {c: v.get(c, None) for c in tab.columns}

        params = v.get('Spectral_Parameters')
        param_names = params.keys()
        npars = len(param_names)
        row['Spectral_Param_Name'] = param_names + [''] * (npar_max - npars)
        row['Spectral_Param_Value'] = [
            float(params[k]['value']) for k in param_names] + [np.nan] * (npar_max - npars)
        row['Spectral_Param_Error'] = [
            float(params[k]['error']) if 'error' in params[k] else np.nan for k in param_names] + [np.nan] * (npar_max - npars)
        row['Spectral_Param_Scale'] = [
            float(params[k]['scale']) for k in param_names] + [np.nan] * (npar_max - npars)
        row = [row[c] for c in tab.columns]

        tab.add_row(row)
        xmlpath = os.path.join(xmldir, v['Source_Name'].replace(' ', '') + '.xml')
        to_xml(xmlpath, v['Source_Name'], v)

    tab.write(os.path.join(args.outdir,
                           'LAT_extended_sources.fits'), overwrite=True)

    # TODO: Generate region file


if __name__ == "__main__":
    main()
