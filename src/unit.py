from __future__ import print_function
import logging
logger = logging.getLogger(__name__)

class Unit(object):
    """The parent class for Strain, Sample, Sequence, Attribution, and Titer.

    Todo:
        * Implement titers as a subclass
        * Implement hasprop and getprop (as analogues to hasattr and getattr)
    """
    def __init__(self):
        self.unit_type = "dbinfo"
        self.parent = None
        self.children = []

        self.CONFIG = {}

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
        """TBD"""
        # @jameshadfield: could you write a docstring for this method?
        # Not sure what is meant by "drop values"
        ## drop values. This is dangerous - make sure all objects.move() have completed
        pass

    def get_data(self):
        """Return a dictionary of all metadata fields defined in config mapping."""
        return {k:v for k, v in self.__dict__.iteritems() if k in self.CONFIG["mapping"][self.unit_type]}

    def ensure_metadata_assignment(self, all_fields, dataset):
        """Ensure that metadata fields match unit type mapping.

        If metadata fields are incorrectly placed, try moving them to the proper
        linked unit. Otherwise, add the unit to dataset.invalid_units.
        """
        unit_type_specific_fields = self.CONFIG["mapping"][self.unit_type]
        for field in dir(self):
            if field in all_fields and field not in unit_type_specific_fields:
                try:
                    self.setprop(field, getattr(self, field))
                    delattr(self, field)
                except:
                    logger.warn("Bad unit found, consider removing.")
                    dataset.invalid_units.append(self)

    def setprop(self, name, value, overwrite=True, _try_to_set_on_parents=True):
        """Set a field in the proper location within a dataset structure.

        This sets an attribute (e.g. "country" or "author") on the relevent
        unit by jumping into parents / children until
        the unit type has that attribute (known via the CONFIG).
        """

        # Metadata units do not have parent/child links, so in their case
        # the setprop is the same as setattr.
        if self.unit_type == "metadata":
            if not hasattr(self):
                # print("M: Field not present, writing")
                setattr(self, name, value)
                return
            elif getattr(self, name) is None:
                # print("M: Field equal to none, writing")
                setattr(self, name, value)
                return
            elif overwrite:
                # print("M: Overwrite set to True, overwriting")
                setattr(self, name, value)
                return

        # For non-Metadata units, first check if the
        if name in self.CONFIG["mapping"][self.unit_type]:
            # Check to make sure there's not already a value, if there is,
            # only overwrite if overwrite flag is set to True.
            if not hasattr(self, name):
                # print("U: field not present, writing")
                setattr(self, name, value)
            elif getattr(self, name) is None:
                # print("U: field equal to none, writing")
                setattr(self, name, value)
            elif overwrite:
                # print("U: Overwrite set to True, overwriting")
                setattr(self, name, value)

        # Pseudo-recursively call setprop on parents and children
        # Note: fields may be set on multiple units, so this isn't in an "else" clause
        if self.parent and _try_to_set_on_parents:
            self.parent.setprop(name, value, overwrite)
        if self.children and self.children != []:
            for child in self.children:
                # Setting _try_to_set_on_parents to False prevents stack overflow
                child.setprop(name, value, overwrite, _try_to_set_on_parents=False)

    def getprop(self, name, _output=None, _try_to_get_on_parents=True):
        """Return a list of all attributes of a given name in a dataset."""
        if _output is None:
            _output = []

        # First, check if the field exists in the input unit
        if hasattr(self, name):
            _output.append(getattr(self, name))

        # Pseudo-recursively call getprop on parents and children
        if self.parent and _try_to_get_on_parents:
            self.parent.getprop(name, _output)
        if self.children and self.children != []:
            for child in self.children:
                # Setting _try_to_get_on_parents to False prevents stack overflow
                child.getprop(name, _output, _try_to_get_on_parents=False)

        return list(set(_output))

    def hasprop(self, name):
        """Return a count of the number of times an attribute exists in a dataset."""
        return len(self.getprop(name))

    def __str__(self):
        """Overwrite default __str__ method for units."""
        return "Unit type {}".format(self.unit_type)
