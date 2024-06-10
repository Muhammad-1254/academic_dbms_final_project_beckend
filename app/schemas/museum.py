from pydantic import BaseModel, UUID4, Json
from db.models.data_types import Role
from db.models.data_types import (
    EpochTypeEnum,
    OriginEnum,
    ObjectStyleEnum,
    StatusTypeEnum,
    GenderEnum,
    ArtObjectType
)
import datetime
from fastapi import Form
from typing import Optional

class ArtistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    artist_bio:Optional[str] = None
    epoch: Optional[EpochTypeEnum] =None
    gender: Optional[GenderEnum] = None
    origin_country: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    date_of_died: Optional[datetime.date] = None
    wiki_qid:Optional[str] = None
    ulan:Optional[str] = None


class ArtObjectBase(BaseModel):
    title: str
    description: str
    dimensions:Optional[str] = None
    department:Optional[str] = None
    style: ObjectStyleEnum
    object_type:ArtObjectType
    epoch: str
    origin_country: Optional[str] = None
    year: str
    artist_id: Optional[UUID4] = None
    
class SculptureCreate(ArtObjectBase):
    material: str
    height: Optional[str] = None
    width: Optional[str] = None
    weight: Optional[str] = None
    
class PaintingCreate(ArtObjectBase):
    paint_type: str
    drawn_on: str
    

 
class OtherArtCreate(ArtObjectBase):
    type:str 
   
class PermanentCollectionCreate(BaseModel):
    date_acquired:datetime.date
    status: StatusTypeEnum
    cost: Optional[str] = None
    art_object_id:UUID4    
    
    
class BorrowedArtObjectBaseCreate(BaseModel):
    date_borrowed:datetime.date
    date_returned:datetime.date
    art_object_id:UUID4
    collection_id:UUID4
    

class CollectionCreate(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    contact: str


class ExhibitionCreate(BaseModel):
    name: str
    start_date: datetime.date
    end_date: datetime.date
    
    
class ExhibitionArtObjectAssociationCreate(BaseModel):
    art_object_id: UUID4
    exhibition_id: UUID4   