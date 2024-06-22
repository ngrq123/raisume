"""
Skills
"""

import pandas as pd

from typing import List, Optional
from pydantic import BaseModel, Field

class Skill(BaseModel):
    """
    The skills class represents a skill in the Cosmic Works dataset.

    The alias fields are used to map the dataset field names
    to the pythonic property names.
    """
    id: str = Field(alias="id")
    skill: str = Field(alias="skill")
    aliases: Optional[List[str]] = Field(default=None, alias="aliases")
    source_id: str = Field(alias="sourceId")
    display_name: str = Field(alias="sourceDisplayName")
    shortDescription: str = Field(alias="shortDescription")
    longDescription: str = Field(alias="longDescription")
    url: str = Field(alias="sourceURL")

    class Config:
        """
        The Config inner class is used to configure the 
        behavior of the Pydantic model. In this case, 
        the Pydantic model will be able to deserialize
        data by both the field name and the field alias.
        """
        populate_by_name = True

class SkillList(BaseModel):
    """
    The SkillsList class represents a list of  skills.
    This class is used when deserializing a collection/array
    of  skills.
    """
    items: List[Skill]