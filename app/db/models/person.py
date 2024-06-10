from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Table,
    Column,
    UUID,
    VARCHAR,
    String,
    ForeignKey,
    Boolean,
    Enum,
    Date,
    JSON,
)
from db.models.mixin import Timestamp
from uuid import uuid4
from db.models.data_types import (
    EpochTypeEnum,
    OriginEnum,
    OtherTypeEnum,
    ObjectStyleEnum,
    PaintingDrawnOnEnum,
    PaintingTypeEnum,
    SculptureMaterialEnum,
    StatusTypeEnum,
    CollectionType,
    ArtObjectType,
)




class Artist(Base, Timestamp):
    __tablename__ = "artists"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(VARCHAR(255), index=True, nullable=False)
    description = Column(String, nullable=False)
    main_style = Column(Enum(ObjectStyleEnum), nullable=False)
    epoch = Column(Enum(EpochTypeEnum), nullable=True)
    origin_country = Column(Enum(OriginEnum), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    date_of_died = Column(Date, nullable=True)
    image = Column(JSON, nullable=True)


    art_objects = relationship(
        "ArtObject",back_populates="artist", cascade="save-update"
    )



class ArtObject(Base, Timestamp):
    __tablename__ = "art_objects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(VARCHAR(255), nullable=False)
    description = Column(String, nullable=False)
    style = Column(Enum(ObjectStyleEnum), nullable=False)

    epoch = Column(Enum(EpochTypeEnum), nullable=False)
    origin_country = Column(Enum(OriginEnum), nullable=True)
    year = Column(Date)
    artist_id = Column(UUID, ForeignKey("artists.id"), nullable=True)
   
    artist = relationship("Artist", back_populates="art_objects")
    
    exhibitions = relationship(
        "Exhibition",secondary="exhibition_art_object_association", back_populates="art_objects", 
    )
    sculpture = relationship("Sculpture", uselist=False, back_populates="art_object")
    painting = relationship("Painting", uselist=False, back_populates="art_object")
    other = relationship("OtherArt", uselist=False, back_populates="art_object")
    permanent = relationship("PermanentCollection", uselist=False, back_populates="art_object")
    borrowed_art_object = relationship(
        "BorrowedArtObject", uselist=False, back_populates="art_object"
    )


class ExhibitionArtObjectAssociation(Base, Timestamp):
    __tablename__ = "exhibition_art_object_association"
  
    art_object_id = Column(UUID, ForeignKey('art_objects.id'), primary_key=True)
    exhibition_id = Column(UUID, ForeignKey('exhibitions.id'), primary_key=True)
    

class Exhibition(Base, Timestamp):
    __tablename__ = "exhibitions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(VARCHAR(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    image = Column(JSON, nullable=True)

    art_objects = relationship(
        "ArtObject",secondary="exhibition_art_object_association", back_populates="exhibitions"
    )


class Sculpture(Base, Timestamp):
    __tablename__ = "sculptures"
    id = Column(
        UUID,
        ForeignKey("art_objects.id"),
        primary_key=True,
    )
    material = Column(Enum(SculptureMaterialEnum), nullable=False)
    height = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    image = Column(JSON, nullable=True)

    art_object = relationship("ArtObject", back_populates="sculpture")


class OtherArt(Base, Timestamp):
    __tablename__ = "other_arts"
    id = Column(
        UUID,
        ForeignKey("art_objects.id"),
        primary_key=True,
    )
    type = Column(Enum(OtherTypeEnum), nullable=False)
    image = Column(JSON, nullable=True)

    art_object = relationship("ArtObject", back_populates="other")


class Painting(Base, Timestamp):
    __tablename__ = "paintings"
    id = Column(
        UUID,
        ForeignKey("art_objects.id"),
        primary_key=True,
    )
    paint_type = Column(Enum(PaintingTypeEnum), nullable=False)
    drawn_on = Column(Enum(PaintingDrawnOnEnum), nullable=False)
    image = Column(JSON, nullable=True)

    art_object = relationship("ArtObject", back_populates="painting")


class PermanentCollection(Base, Timestamp):
    __tablename__ = "permanents_collections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date_acquired = Column(Date, nullable=False)
    status = Column(Enum(StatusTypeEnum), nullable=False)
    cost = Column(String, nullable=True)
   
    art_object_id = Column(UUID, ForeignKey('art_objects.id'),nullable=False)
    
    art_object = relationship("ArtObject", back_populates="permanent")


class BorrowedArtObject(Base, Timestamp):
    __tablename__ = "borrowed_art_objects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date_borrowed = Column(Date, nullable=False)
    date_returned = Column(Date, nullable=True)
    
    art_object_id = Column(UUID, ForeignKey('art_objects.id'), nullable=False)
    collection_id = Column(UUID, ForeignKey('collections.id'), nullable=False)
    
    art_object = relationship("ArtObject", back_populates="borrowed_art_object")
    collection = relationship("Collection", back_populates="borrowed_art_objects")


class Collection(Base, Timestamp):
    __tablename__ = "collections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, index=True)
    type = Column(Enum(CollectionType), nullable=True)
    description = Column(String, nullable=True)
    address = Column(String, nullable=True)
    contact = Column(String, nullable=False)
    
    borrowed_art_objects = relationship("BorrowedArtObject", back_populates="collection")





class User(Base, Timestamp):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(VARCHAR(255), index=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_auth = Column(Boolean, default=False)
    image = Column(String, nullable=True)


class Manager(Base, Timestamp):
    __tablename__ = "managers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(255), index=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    image = Column(String, nullable=True)

    authorized_by = Column(UUID(as_uuid=True), ForeignKey("admin.id"), nullable=True)
    authorized_by_admin = relationship("Admin", back_populates="authorized_managers")


class Admin(Base, Timestamp):
    __tablename__ = "admin"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(255), index=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    image = Column(String, nullable=True)

    authorized_managers = relationship("Manager", back_populates="authorized_by_admin")
