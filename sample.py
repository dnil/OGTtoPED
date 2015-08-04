import config 

# Sample class
class Sample:
    """Samples, with ID, tissue, family info and affectedness status"""
   
    def __init__(self, ID, info, tissue):
        self.sampleID = ID
        self.info = info.lower()
        self.tissue = tissue.lower()

        if config.debug:
            print >> sys.stderr, ("Sample created with id {} info {}",
                "and tissue {}").format(self.sampleID, self.info, self.tissue)

        # Assume unknown sex
        self.sex = 0

        self.affected = False
        if self.info.find("affected") != -1:
            if self.info.find("unaffected") == -1:
                self.affected = True
