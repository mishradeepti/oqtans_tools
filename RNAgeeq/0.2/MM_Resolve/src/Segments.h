#ifndef __SEGMENTS_H__
#define __SEGMENTS_H__

using namespace std;

#include <map>
#include <set>
#include <utility>
#include <string>

#include "Alignment.h"
#include "Segment.h"

class Segments {

public:


    // outer map: chr/strand pair as key, inner map as value
    // inner map: stores exon start or stop as key, segment id as value
    map<pair<unsigned char, unsigned char>, map<long, long> > exons;
    // stores segment id as key, segment object as value
    map<long, Segment*> exon_ids;
    // outer map: chr/strand pair as key, inner map as value
    // inner map: stores intron start as key, segment id as value
    map<pair<unsigned char, unsigned char>, multimap<unsigned long, unsigned long> > introns;
    // stores segment id as key, segment object as value
    map<unsigned long, Segment*> introns_by_ids;

    Segments() {};
    ~Segments() {
        for (map<long, Segment*>::iterator it = exon_ids.begin(); it != exon_ids.end(); it++)
            delete it->second;
        for (map<unsigned long, Segment*>::iterator it = introns_by_ids.begin(); it != introns_by_ids.end(); it++)
            delete it->second;
    };

    void get_from_file();

    pair<double, double> get_exon_segment_loss(vector<vector<Alignment>::iterator> alignments, set<unsigned long> invariant_pos, bool debug = false);

    double get_total_loss();
};
#endif
