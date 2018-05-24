import logging
logger = logging.getLogger(__name__)

class Unit(object):
    """The parent class for Strain, Sample, Sequence, Attribution, """
    def __init__(self):
        self.unit_type = "dbinfo"
        self.parent = None
        self.children = []

    def fix_single(self, name):
        """ try to apply the fix function (as defined in the config) to a single piece of state (name) """
        try:
            setattr(self, name, self.CONFIG["fix_functions"][name](self, getattr(self, name), logger))
        except KeyError: ## the cleaning function wasn't set
            pass
        except AttributeError: ## the piece of state doesn't exist - run the fix fn with None as the value
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

    def drop(self):
        ## drop values. This is dangerous - make sure all objects.move() have completed
        pass

    def get_data(self):
        return {k:v for k, v in self.__dict__.iteritems() if k in self.CONFIG["mapping"][self.unit_type]}

    def setprop(self, name, value, overwrite=True, try_to_set_on_parents=True):
        """
        This sets an attribute (e.g. "country" or "author") on the relevent unit by jumping into parents / children until
        the unit type has that attribute (known via the CONFIG).
        """
        if self.unit_type == "metadata":
            # @barneypotter could you add a comment here?
            setattr(self, name, value)
            return

        if name in self.CONFIG["mapping"][self.unit_type]:
            # check to make sure there's not already a value here
            if (not hasattr(self, name)) or getattr(self, name) == None or overwrite:
                setattr(self, name, value)
                # print("set {} on {}".format(name, self.unit_type))

        # tell the parents and the children to set the prop on themselves (pseudo recursively)
        # note that a field may be set on multiple units, so this isn't in an "else" clause
        if self.parent and try_to_set_on_parents:
            self.parent.setprop(name, value, overwrite)
        if self.children and self.children != []:
            for child in self.children:
                child.setprop(name, value, overwrite, try_to_set_on_parents=False)

    def getprop(self, name):
        return

    def hasprop(self, name):
        return
