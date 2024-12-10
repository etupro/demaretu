import logging

logger = logging.getLogger(__name__)

def filter_data(self):
    """
    Filter the DataFrame by:
    1. Excluding rows where 'niveau_formation' is "doctorat".
    2. Excluding rows where 'nom_formation' contains the word "Module".
    """
    self.df = self.df[self.df.niveau_formation != "doctorat"]
    self.df = self.df[~self.df.nom_formation.str.contains("Module")]
    logger.info("Filter data done !")
