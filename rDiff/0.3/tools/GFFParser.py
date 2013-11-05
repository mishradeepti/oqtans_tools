#!/usr/bin/env python
"""
Extract genome annotation from a GFF (a tab delimited format for storing sequence features and annotations) file.

Requirements: 
    Numpy :- http://numpy.org/ 
    Scipy :- http://scipy.org/ 

Copyright (C)	

2009-2012 Friedrich Miescher Laboratory of the Max Planck Society, Tubingen, Germany. 
2012-2013 Memorial Sloan-Kettering Cancer Center, New York City, USA.
"""

import re
import os
import sys
import urllib
import numpy as np
import scipy.io as sio
from collections import defaultdict
import helper as utils 

def _attribute_tags(col9):
    """ 
    Split the key-value tags from the attribute column, it takes column number 9 from GTF/GFF file 
    """
    info = defaultdict(list)
    is_gff = False
    
    if not col9:
        return is_gff, info
        
    # trim the line ending semi-colon  ucsc may have some white-space  
    col9 = col9.rstrip(';| ')
    # attributes from 9th column 
    atbs = col9.split(" ; ")
    if len(atbs) == 1:
        atbs = col9.split("; ")
        if len(atbs) == 1:
            atbs = col9.split(";")
    # check the GFF3 pattern which has key value pairs like:
    gff3_pat = re.compile("\w+=")
    # sometime GTF have: gene_id uc002zkg.1;
    gtf_pat = re.compile("\s?\w+\s")

    key_vals = []

    if gff3_pat.match(atbs[0]): # gff3 pattern 
        is_gff = True
        key_vals = [at.split('=') for at in atbs]
    elif gtf_pat.match(atbs[0]): # gtf pattern
        for at in atbs:
            key_vals.append(at.strip().split(" ",1))
    else:
        # to handle attribute column has only single value 
        key_vals.append(['ID', atbs[0]])
    # get key, val items 
    for item in key_vals:
        key, val = item
        # replace the double qoutes from feature identifier 
        val = re.sub('"', '', val)
        # replace the web formating place holders to plain text format 
        info[key].extend([urllib.unquote(v) for v in val.split(',') if v])

    return is_gff, info
                
def _spec_features_keywd(gff_parts):
    """
    Specify the feature key word according to the GFF specifications
    """
    for t_id in ["transcript_id", "transcriptId", "proteinId"]:
        try:
            gff_parts["info"]["Parent"] = gff_parts["info"][t_id]
            break
        except KeyError:
            pass
    for g_id in ["gene_id", "geneid", "geneId", "name", "gene_name", "genename"]:
        try:
            gff_parts["info"]["GParent"] = gff_parts["info"][g_id]
            break
        except KeyError:
            pass
    ## TODO key words
    for flat_name in ["Transcript", "CDS"]:
        if gff_parts["info"].has_key(flat_name):
            # parents
            if gff_parts['type'] in [flat_name] or re.search(r'transcript', gff_parts['type'], re.IGNORECASE):
                if not gff_parts['id']:
                    gff_parts['id'] = gff_parts['info'][flat_name][0]
                    #gff_parts["info"]["ID"] = [gff_parts["id"]]
            # children 
            elif gff_parts["type"] in ["intron", "exon", "pseudogenic_exon", "three_prime_UTR",
                        "coding_exon", "five_prime_UTR", "CDS", "stop_codon",
                        "start_codon"]:
                gff_parts["info"]["Parent"] = gff_parts["info"][flat_name]
            break
    return gff_parts

def Parse(ga_file):
    """
    Parsing GFF/GTF file based on feature relationship, it takes the input file.
    """
    child_map = defaultdict(list)
    parent_map = dict()

    ga_handle = utils._open_file(ga_file)

    for rec in ga_handle:
        rec = rec.strip('\n\r')

        # skip empty line fasta identifier and commented line
        if not rec or rec[0] in  ['#', '>']:
            continue
        # skip the genome sequence 
        if not re.search('\t', rec):
            continue

        parts = rec.split('\t')
        assert len(parts) >= 8, rec

        # process the attribute column (9th column)
        ftype, tags = _attribute_tags(parts[-1])
        if not tags: # skip the line if no attribute column.
	        continue 
        
        # extract fields  
        if parts[1]:
            tags["source"] = parts[1]
        if parts[7]:
            tags["phase"] = parts[7]

        gff_info = dict()
        gff_info['info'] = dict(tags)
        #gff_info["is_gff3"] = ftype
        gff_info['chr'] = parts[0]

        if parts[3] and parts[4]:
            gff_info['location'] = [int(parts[3]) ,
                        int(parts[4])]
            gff_info['type'] = parts[2]
            gff_info['id'] = tags.get('ID', [''])[0]
            if parts[6] in ['?', '.']:
                parts[6] = None 
            gff_info['strand'] = parts[6]

            # key word according to the GFF spec.
            if not ftype:
                gff_info = _spec_features_keywd(gff_info)
        
            # link the feature relationships
            if gff_info['info'].has_key('Parent'): 
                for p in gff_info['info']['Parent']:
                    if p == gff_info['id']:
                        gff_info['id'] = ''
                        break
                rec_category = 'child'
            elif gff_info['id']:
                rec_category = 'parent'
            else:
                rec_category = 'record'

            # depends on the record category organize the features
            if rec_category == 'child':
                for p in gff_info['info']['Parent']:
                    # create the data structure based on source and feature id 
                    child_map[(gff_info['chr'], gff_info['info']['source'], p)].append(
                                            dict( type = gff_info['type'], 
                                            location =  gff_info['location'], 
                                            strand = gff_info['strand'], 
                                            ID = gff_info['id'],
                                            gene_id = gff_info['info'].get('GParent', '') 
                                            ))
            elif rec_category == 'parent':
                parent_map[(gff_info['chr'], gff_info['info']['source'], gff_info['id'])] = dict( 
                                            type = gff_info['type'], 
                                            location = gff_info['location'],
                                            strand = gff_info['strand'],
                                            name = tags.get('Name', [''])[0])
            elif rec_category == 'record':
                #TODO how to handle plain records?
                c = 1 
    ga_handle.close()
    
    # depends on file type create parent feature  
    if not ftype:
        parent_map, child_map = _create_missing_feature_type(parent_map, child_map)    
    
    # connecting parent child relations  
    # // essentially the parent child features are here from any type of GTF/GFF2/GFF3 file
    gene_mat = _format_gene_models(parent_map, child_map) 

    return gene_mat 
    
def _format_gene_models(parent_nf_map, child_nf_map): 
    """
    Genarate GeneObject based on the parsed file contents

    parent_map: parent features with source and chromosome information 
    child_map: transctipt and exon information are encoded 
    """
    g_cnt = 0 
    gene = np.zeros((len(parent_nf_map),), dtype = utils.init_gene_DE())

    for pkey, pdet in parent_nf_map.items():
        # considering only gene features 
        if not re.search(r'gene', pdet.get('type', '')):
            continue 
        # infer the gene start and stop if not there in the 
        if not pdet.get('location', []):
            GNS, GNE = [], []
            # multiple number of transcripts 
            for L1 in child_nf_map[pkey]:
                GNS.append(L1.get('location', [])[0]) 
                GNE.append(L1.get('location', [])[1]) 
            GNS.sort()
            GNE.sort()
            pdet['location'] = [GNS[0], GNE[-1]]
        orient = pdet.get('strand', '')

        gene[g_cnt]['id'] = g_cnt +1 
        gene[g_cnt]['chr'] = pkey[0]
        gene[g_cnt]['source'] = pkey[1]
        gene[g_cnt]['name'] = pkey[-1]
        gene[g_cnt]['start'] = pdet.get('location', [])[0]
        gene[g_cnt]['stop'] = pdet.get('location', [])[1]
        gene[g_cnt]['strand'] = orient  
        
        # default value 
        gene[g_cnt]['is_alt_spliced'] = 0
        if len(child_nf_map[pkey]) > 1:
            gene[g_cnt]['is_alt_spliced'] = 1

        # complete sub-feature for all transcripts 
        dim = len(child_nf_map[pkey])
        TRS = np.zeros((dim,), dtype=np.object)
        EXON = np.zeros((dim,), dtype=np.object)

        # fetching corresponding transcripts 
        for xq, Lv1 in enumerate(child_nf_map[pkey]):

            TID = Lv1.get('ID', '')
            TRS[xq]= np.array([TID])

            orient = Lv1.get('strand', '')

            # fetching different sub-features 
            child_feat = defaultdict(list)
            for Lv2 in child_nf_map[(pkey[0], pkey[1], TID)]:
                E_TYP = Lv2.get('type', '')
                child_feat[E_TYP].append(Lv2.get('location'))
            
            # make exon coordinate from cds and utr regions 
            if not child_feat.get('exon'):  
                if child_feat.get('CDS'):
                    exon_cod = utils.make_Exon_cod( orient, 
                                NonetoemptyList(child_feat.get('five_prime_UTR')), 
                                NonetoemptyList(child_feat.get('CDS')),
                                NonetoemptyList(child_feat.get('three_prime_UTR')))
                    child_feat['exon'] = exon_cod 
                else:
                    # searching through keys to find a pattern describing exon feature 
                    ex_key_pattern = [k for k in child_feat if k.endswith("exon")]
                    child_feat['exon'] = child_feat[ex_key_pattern[0]]
                    # TODO only UTR's

            # make general ascending order of coordinates 
            if orient == '-':
                for etype, excod in child_feat.items():
                    if len(excod) > 1:
                        if excod[0][0] > excod[-1][0]:
                            excod.reverse()
                            child_feat[etype] = excod

            # add sub-feature # make array for export to different out
            EXON[xq] = np.array(child_feat.get('exon'), np.float64)
            
        # add sub-features to the parent gene feature
        gene[g_cnt]['transcripts'] = TRS 
        gene[g_cnt]['exons'] = EXON
        
        gene[g_cnt]['gene_info'] = dict( ID = pkey[-1], 
                                Name = pdet.get('name'), 
                                Source = pkey[1]) 
        g_cnt += 1 

    ## deleting empty gene records from the main array
    XPFLG=0
    for XP, ens in enumerate(gene):
        if ens[0]==0:
            XPFLG=1
            break
    
    if XPFLG==1:
        XQC = range(XP, len(gene)+1)
        gene = np.delete(gene, XQC)

    return gene 

def NonetoemptyList(XS):
    """
    Convert a None type to empty list 
    """
    return [] if XS is None else XS 

def _create_missing_feature_type(p_feat, c_feat):
    """
    GFF/GTF file defines only child features. This function tries to create 
    the parent feature from the information provided in the attribute column. 

    example: 
    chr21   hg19_knownGene  exon    9690071 9690100 0.000000        +       .       gene_id "uc002zkg.1"; transcript_id "uc002zkg.1"; 
    chr21   hg19_knownGene  exon    9692178 9692207 0.000000        +       .       gene_id "uc021wgt.1"; transcript_id "uc021wgt.1"; 
    chr21   hg19_knownGene  exon    9711935 9712038 0.000000        +       .       gene_id "uc011abu.2"; transcript_id "uc011abu.2"; 

    This function gets the parsed feature annotations. 
    """
    child_n_map = defaultdict(list)
    for fid, det in c_feat.items():
        # get the details from grand child  
        GID = STRD = None
        SPOS, EPOS = [], [] 
        TYP = dict()
        for gchild in det:
            GID = gchild.get('gene_id', [''])[0] 
            SPOS.append(gchild.get('location', [])[0]) 
            EPOS.append(gchild.get('location', [])[1]) 
            STRD = gchild.get('strand', '')
            TYP[gchild.get('type', '')] = 1
        SPOS.sort() 
        EPOS.sort()
        
        # infer transcript type
        transcript_type = 'transcript'
        transcript_type = 'mRNA' if TYP.get('CDS', '') or TYP.get('cds', '') else transcript_type
        
        # gene id and transcript id are same
        transcript_id = fid[-1]
        if GID == transcript_id:
            transcript_id = 'Transcript:' + str(GID)
        
        # level -1 feature type 
        p_feat[(fid[0], fid[1], GID)] = dict( type = 'gene',
                                            location = [], ## infer location based on multiple transcripts  
                                            strand = STRD,
                                            name = GID )
        # level -2 feature type 
        child_n_map[(fid[0], fid[1], GID)].append(
                                            dict( type = transcript_type,
                                            location =  [SPOS[0], EPOS[-1]], 
                                            strand = STRD, 
                                            ID = transcript_id,
                                            gene_id = '' ))
        # reorganizing the grand child
        for gchild in det:
            child_n_map[(fid[0], fid[1], transcript_id)].append(
                                            dict( type = gchild.get('type', ''),
                                            location =  gchild.get('location'),
                                            strand = gchild.get('strand'), 
                                            ID = gchild.get('ID'),
                                            gene_id = '' ))
    return p_feat, child_n_map 


## General instruction to use the above functions:
## Usage: GFFParser.py in.gff3 out.mat 

try:
    gff_file = sys.argv[1]
    out_mat = sys.argv[2]
except:
    print __doc__
    sys.exit(-1)

## Parse the file accoring to the type and returns the genes informations --
gene_struct = Parse(gff_file)

## Write the gene annotations to a matlab struct array format --
sio.savemat(out_mat, 
    mdict = dict(genes = gene_struct), 
    format = '5', 
    oned_as = 'row')
