"""
Hard Skills
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class HardSkills(BaseModel):
    """
    The hard skills class represents a hard skill in the Cosmic Works dataset.

    The alias fields are used to map the dataset field names
    to the pythonic property names.
    """
    id: str = Field(alias="id")
    hard_skill: str = Field(alias="hardSkill")
    aliases: Optional[str]
    source_id: str = Field(alias="sourceId")
    display_name: str = Field(alias="sourceDisplayName")
    shortDescription: str = Field(alias="ShortDescription")
    longDescription: str = Field(alias="LongDescription")
    url: str = Field(alias="sourceURL")

    class Config:
        """
        The Config inner class is used to configure the 
        behavior of the Pydantic model. In this case, 
        the Pydantic model will be able to deserialize
        data by both the field name and the field alias.
        """
        populate_by_name = True

class HardSkillsList(BaseModel):
    """
    The HardSkillsList class represents a list of hard skills.
    This class is used when deserializing a collection/array
    of hard skills.
    """
    items: List[HardSkills]


