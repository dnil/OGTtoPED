import argparse, sys
from openpyxl import load_workbook

# CLI

parser = argparse.ArgumentParser(description="convert OGT sample sheet to PED file")

parser.add_argument("orderform", help="OGT order form containing sample IDs, affectedness status and family grouping.")
parser.add_argument("outfile", help="Output PED file", nargs='?')
parser.add_argument("-D", "--debug", help="Enable DEBUG output.", action="store_true")

args = parser.parse_args()

if args.debug:
    print >> sys.stderr, "DEBUG output turned on."

if args.outfile is not None:
    out = open(args.outfile, 'w')
else:
    out = sys.stderr

# Open workbook

wb = load_workbook(filename = args.orderform)
ws = wb.active

# sanity checks

if ws.title != "material form": 
    print >> sys.stderr, "WARNING: Non standard active sheet name ", ws.title 

if ws['B12'].value != "Customer Sample ID" or ws['M12'].value != "Additional Experimental Comments" or ws['C12'].value != "Source (cells, tissue etc)":
    print >> sys.stderr, "Unexpected table / cell layout: check to see that sheet is ok, and ask to have the script updated. :-)" 
    exit(1)


# sample class
class Sample:
    'Samples, with ID and affectedness status'
   
    def __init__(self, ID, info, tissue):
        self.sampleID = ID
        self.info = info.lower()
        self.tissue = tissue.lower()

        if args.debug:
            print >> sys.stderr, "Sample created with id {} info {} and tissue {}".format(self.sampleID, self.info, self.tissue)

        # assume unknown sex
        self.sex = 0

        self.affected = False
        if self.info.find("affected") != -1:
            if self.info.find("unaffected") == -1:
                self.affected = True

        #family nr?

# iterate over all rows, parse row blocks 
in_sample_section = False
in_family = False

max_rows = 1024

samples_found = 0
family = []
family_count = 0 

def update_family(family):
    mother = None
    father = None

    # first, determine parents
    for sample in family:

        # note that grandmothers and grandfathers will be marked as mother and father..

        if sample.info.find("mother") != -1:
            sample.motherID = 0
            sample.fatherID = 0
            sample.sex = 2
            mother = sample
            if args.debug:
                print >> sys.stderr, "found mother {}".format(mother.sampleID)

        if sample.info.find("father") != -1:
            sample.fatherID = 0
            sample.motherID = 0
            sample.sex = 1
            father = sample
            if args.debug:
                print >> sys.stderr, "found father {}".format(father.sampleID)
    
        if sample.info.find("male") != -1:
            sample.sex = 1

        if sample.info.find("girl") != -1:
            sample.sex = 2

        if sample.info.find("boy") != -1:
            sample.sex = 1

        if sample.info.find("female") != -1:
            sample.sex = 2

        if sample.info.find("man") != -1 and sample.info.find("woman") == -1:
            sample.sex = 1

        if sample.info.find("woman") != -1:
            sample.sex = 2

    # to avoid unpleasantness, just give unset people parentIDs =0 (grandmothers, cousins, tissues, etc..)
    if mother is None:
        motherID = 0
    else:
        motherID = mother.sampleID

    if father is None:
        fatherID = 0
    else: 
        fatherID = father.sampleID

    # singletons have mother, father IDs = 0 regardles
    if len(family) == 1:
        fatherID = 0
        motherID = 0

   # then, print parent ids on all kids
    for sample in family:
        sample.motherID = motherID
        sample.fatherID = fatherID

        if sample.info.find("brother") != -1:
            sample.sex = 1
        elif sample.info.find("sister") != -1:
            sample.sex = 2
        elif sample.info.find("daughter") != -1:
            sample.sex = 2
        elif sample.info.find("son") != -1:
            sample.sex = 1
#        if sample.info.find("child") != -1:
 #       elif sample.info.find("foetus") != -1:
#        elif sample.info.find("sibling") != -1:


def print_family(family, family_count):

    # determine family id - ideally, sampleID of the first affected child
    familyID = family_count

    if len(family) == 1:
        familyID = family[0].sampleID

    else:
        for sample in family:
            if sample.affected and sample.motherID != 0 and sample.fatherID != 0: 
                familyID = sample.sampleID
                break

    # if we still don't have an ID, perhaps this is an affected-unaffected tissue pair? or several affected from the same family?
    if familyID == family_count:
        for sample in family:
            if sample.affected:
                familyID = sample.sampleID
                break

    for sample in family:
        if sample.affected:
            affected_status = 2
        else:
            affected_status = 1

        print >> out, "{}\t{}\t{}\t{}\t{}\t{}\t{}".format(familyID, sample.sampleID, sample.fatherID, sample.motherID, sample.sex, affected_status,tissue)

for rownum in range(1,max_rows+1):
    cell=ws["B" + str(rownum)]

    if not in_sample_section:
        if cell.value == "Customer Sample ID":
            if args.debug:
                print >> sys.stderr, "Found sample ID tag."
            in_sample_section = True
    else:
        if cell.value is not None:
            # found a new sample row
            sample_id = cell.value
            sample_id.rstrip()

            if not in_family:
                if args.debug:
                    print >> sys.stderr, "Found new family, starting with sample '{}'".format(sample_id)
                family_count += 1

            info_cell = ws["M" + str(rownum)]
            info = info_cell.value
            if info is None:
                info = "NA"
            info.rstrip()

            tissue_cell =  ws["C" + str(rownum)]
            tissue = tissue_cell.value
            if tissue is None:
                tissue = "NA"
            tissue.rstrip()

            sample = Sample(sample_id, info, tissue)            
            in_family = True
            family.append(sample)
            
            if sample.info.find("singleton") != -1:          
                # found a singleton!
                sample.affected = True
                update_family(family)
                print_family(family, family_count)
                # this ends the current family.
                if args.debug:
                    print >> sys.stderr, "Found a singleton - that completes the family."

                family = []
                in_family = False
                # note that the next row may be a None or a new family member..

            samples_found += 1

        elif cell.value is None: 
            # empty row
            if in_family:
                # this ends the current family.
                if args.debug:
                    print >> sys.stderr, "Family complete."

                update_family(family)
                print_family(family, family_count)

                family = []
                in_family = False
