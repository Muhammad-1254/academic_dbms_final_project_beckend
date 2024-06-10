from pydantic import BaseModel, UUID4, Json
from db.models.data_types import Role
from db.models.data_types import (
    EpochTypeEnum,
    OriginEnum,
    OtherTypeEnum,
    ObjectStyleEnum,
    PaintingDrawnOnEnum,
    PaintingTypeEnum,
    SculptureMaterialEnum,
    StatusTypeEnum,
    ObjectOwnership,
    CollectionType,
    ArtObjectType
)
import datetime
from fastapi import Form
from typing import Optional

class ArtistCreate(BaseModel):
    name: str
    description: str
    main_style: ObjectStyleEnum
    epoch: EpochTypeEnum
    origin_country: OriginEnum
    date_of_birth: datetime.date
    date_of_died: datetime.date


class ArtObjectBase(BaseModel):
    title: str
    description: str
    style: ObjectStyleEnum
    epoch: EpochTypeEnum
    origin_country: OriginEnum
    year: datetime.date
    artist_id: Optional[UUID4] = None
    
class SculptureCreate(ArtObjectBase):
    material: SculptureMaterialEnum
    height: Optional[str] = None
    weight: Optional[str] = None
    
class PaintingCreate(ArtObjectBase):
    paint_type: PaintingTypeEnum
    drawn_on: PaintingDrawnOnEnum
    

 
class OtherArtCreate(ArtObjectBase):
    type: OtherTypeEnum
   
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
    type: Optional[CollectionType] = None
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