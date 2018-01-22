import logging
logger = logging.getLogger(__name__)

class Sample:

    def __init__(self, data_dictionary):
        logger.info("Sample class initializing")
        pass

    def is_valid(self):
        return False
