import config 

def update_family(family):
    """Update the family list of samples with info record implicit data."""
    mother = None
    father = None

    # First, determine parents
    for sample in family:
        if sample.info.find("mother") != -1:
            sample.motherID = 0
            sample.fatherID = 0
            sample.sex = 2
            mother = sample
            if config.debug:
                print >> sys.stderr, "found mother {}".format(mother.sampleID)

        if sample.info.find("father") != -1:
            sample.fatherID = 0
            sample.motherID = 0
            sample.sex = 1
            father = sample
            if config.debug:
                print >> sys.stderr, "found father {}".format(father.sampleID)

    # To avoid unpleasantness, just give unset people (grandmothers, cousins, 
    # tissues, etc..) founder parent ID 0.

    if mother is None:
        motherID = 0        
    else:
        motherID = mother.sampleID

    if father is None:
        fatherID = 0
    else:
        fatherID = father.sampleID

    # Note that grandmother or grandfather will be marked as mother or father.

    # Singletons have mother, father IDs = 0 regardles.
    if len(family) == 1:
        fatherID = 0
        motherID = 0

   # Then, print parent ids on all kids.
    for sample in family:
        child = False

        if sample.info.find("brother") != -1:
            sample.sex = 1
            child = True
        elif sample.info.find("sister") != -1:
            sample.sex = 2
            child = True
        elif sample.info.find("daughter") != -1:
            sample.sex = 2
            child = True
        elif sample.info.find("son") != -1:
            sample.sex = 1
            child = True
        elif sample.info.find("child") != -1:
            child = True
        elif sample.info.find("foetus") != -1:
            child = True
        elif sample.info.find("sibling") != -1:
            child = True
        elif sample.info.find("boy") != -1:
            sample.sex = 1
            child = True
        elif sample.info.find("girl") != -1:
            sample.sex = 2
            child = True

        # Update parent id for child or anyone who is not the mother or father.
        assert(sample is not None)
        if child or (not child and sample is not mother and 
                     sample is not father):
            sample.motherID = motherID
            sample.fatherID = fatherID

        if sample.info.find("male") != -1:
            sample.sex = 1

        if sample.info.find("female") != -1:
            sample.sex = 2

        if sample.info.find("man") != -1 and sample.info.find("woman") == -1:
            sample.sex = 1

        if sample.info.find("woman") != -1:
            sample.sex = 2

def family_ped(family, family_count):
    """Determine a family ID and return family info strings in PED format."""

    # Determine family id - ideally, sampleID of the first affected child.
    familyID = family_count

    if len(family) == 1:
        familyID = family[0].sampleID
    else:
        for sample in family:
            if sample.affected and (sample.motherID != 0 or 
                                    sample.fatherID != 0): 
                familyID = sample.sampleID
                break

    # If we still don't have an ID, perhaps this is an affected-unaffected
    # tissue pair?  Or several affected from the same family?
    if familyID == family_count:
        for sample in family:
            if sample.affected:
                familyID = sample.sampleID
                break

    # Ok, worst case, just name the family after the first sample.
    if familyID == family_count:
        familyID = family[0].sampleID

    # Then print
    outstring = ""
    for sample in family:
        if sample.affected:
            affected_status = 2
        else:
            affected_status = 1

        outstring += "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            familyID, sample.sampleID, sample.fatherID, sample.motherID, 
            sample.sex, affected_status, sample.tissue)
        
    return outstring
