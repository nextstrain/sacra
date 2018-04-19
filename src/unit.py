import logging
logger = logging.getLogger(__name__)

class Unit(object):
    """The parent class for Strain, Sample, Sequence, Attribution, """
    def __init__(self):
        self.unit_type = "dbinfo"
        self.parent = None
        self.children = []

    def move(self):
        ## move names. I'm guessing this will need to use self.parent & self.child methods
        pass

    def fix_single(self, name):
        """ try to apply the fix function (as defined in the config) to a single piece of state (name) """
        try:
            setattr(self, name, self.CONFIG["fix_functions"][name](self, getattr(self, name), logger))
        except KeyError: ## the cleaning function wasn't set
            pass
        except AttributeError: ## the piece of state doesn't exist - run the fix fn with "None" as the value
            setattr(self, name, self.CONFIG["fix_functions"][name](self, None, logger))

    def fix(self):
        """ apply the fix method to all pieces of state, that are also in the spec mapping list """
        for name in self.CONFIG["mapping"][self.unit_type]:
            self.fix_single(name)

    def create_single(self, name):
        """ try to apply the create function (as defined in the config) to a single piece of state (name) """
        try:
            v = self.CONFIG["create_functions"][name](self, logger)
            if v:
                setattr(self, name, v)
        except KeyError: ## the cleaning function wasn't set
            pass

    def create(self):
        pass;

    def drop(self):
        ## drop values. This is dangerous - make sure all objects.move() have completed
        pass

    def get_data(self):
        return {k:v for k, v in self.__dict__.iteritems() if k in self.CONFIG["mapping"][self.unit_type]}

    def setprop(self, name, value, overwrite=False, parents=True):
        if name in self.CONFIG["mapping"][self.unit_type]:
            if not hasattr(self, name) or overwrite:
                setattr(self, name, value)
        else:
            if self.parent:
                if parents:
                    self.parent.setprop(name, value, overwrite)
            if self.children and self.children != []:
                for child in self.children:
                    child.setprop(name, value, overwrite, parents=False)
