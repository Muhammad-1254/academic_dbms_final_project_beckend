from fastapi import (
    Response,
    Request,
    Depends,
    HTTPException,
    status,
    APIRouter,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session
import json
from db.database import get_db
import utils
from uuid import uuid4
from db.models.person import (
    Artist,
    Sculpture,
    BorrowedArtObject,
    Collection,
    ArtObject,
    Painting,
    OtherArt,
    Exhibition,
    PermanentCollection,
    ExhibitionArtObjectAssociation,
)
from fastapi.responses import Response
import cloudinary.uploader

from db.models.data_types import Role
from schemas.museum import (
    ArtistCreate,
    SculptureCreate,
    OtherArtCreate,
    PaintingCreate,
    CollectionCreate,
    ExhibitionCreate,
    PermanentCollectionCreate,
    BorrowedArtObjectBaseCreate,
    ExhibitionArtObjectAssociationCreate,
)

from typing import Annotated, Optional, List
from db.models.data_types import (
    EpochTypeEnum,
    ObjectStyleEnum,
    OriginEnum,
    ObjectOwnership,
    ArtObjectType,
    CollectionType,
    OtherTypeEnum,
    PaintingDrawnOnEnum,
    PaintingTypeEnum,
    Role,
    SculptureMaterialEnum,
    StatusTypeEnum,
)
import datetime

router = APIRouter()


def temp_date():
    return datetime.datetime.date(datetime.datetime.now)


@router.post("/create/artist")
async def create_artist_(
    name: str = Form("sd"),
    description: str = Form("dsa"),
    main_style: str = Form(ObjectStyleEnum.ABSTRACT),
    epoch: str = Form(EpochTypeEnum.ANCIENT),
    origin_country: str = Form(OriginEnum.AMERICAN),
    date_of_birth: str = Form(datetime.datetime.date(datetime.datetime.now())),
    date_of_died: str = Form(datetime.datetime.date(datetime.datetime.now())),
    files: Annotated[list[UploadFile], File(description="upload images")] = None,
    db: Session = Depends(get_db),
):

    try:
        artist = ArtistCreate(
            name=name,
            description=description,
            main_style=main_style,
            epoch=epoch,
            origin_country=origin_country,
            date_of_birth=date_of_birth,
            date_of_died=date_of_died,
        )
        artist_exist = db.query(Artist).filter(Artist.name == artist.name).first()
        print(f"artist_exist: {artist_exist}")
        if artist_exist:
            return {"message": "artist already exist with this name"}
        artist_id = uuid4()
        results = []
        for i, file in enumerate(files):
            result = cloudinary.uploader.upload(
                file.file, public_id=f"{artist_id}:img:{i}:_:artist"
            )
            results.append(result["secure_url"])
        urls = json.dumps(results)

        new_artist = Artist(
            id=artist_id,
            name=artist.name,
            description=artist.description,
            main_style=artist.main_style,
            epoch=artist.epoch,
            origin_country=artist.origin_country,
            date_of_birth=artist.date_of_birth,
            date_of_died=artist.date_of_died,
            image=urls,
        )
        db.add(new_artist)
        db.commit()
        db.refresh(new_artist)
        return {"message": "artist created successfully", "data": new_artist}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/art_object/sculpture")
async def create_sculpture_(
    title: str = Form("title"),
    description: str = Form("desc"),
    style: str = Form(ObjectStyleEnum.BAROQUE),
    epoch: str = Form(EpochTypeEnum.MODERN),
    origin_country: str = Form(OriginEnum.ARAB),
    year: str = Form(datetime.datetime.date(datetime.datetime.now())),
    artist_id: str = Form(""),
    material: str = Form(SculptureMaterialEnum.METAL),
    height: str = Form("100"),
    weight: str = Form("12gm"),
    files: Annotated[list[UploadFile], File(description="upload images")] = None,
    db: Session = Depends(get_db),
):
    try:

        object = SculptureCreate(
            title=title,
            description=description,
            style=style,
            epoch=epoch,
            origin_country=origin_country,
            year=year,
            material=material,
            weight=weight,
            height=height,
            artist_id=artist_id,
        )
        # first creating art object
        new_art_object = ArtObject(
            title=object.title,
            description=object.description,
            style=object.style,
            epoch=object.epoch,
            origin_country=object.origin_country,
            year=object.year,
            artist_id=object.artist_id,
        )
        db.add(new_art_object)
        db.commit()
        db.refresh(new_art_object)
        results = []
        for i, file in enumerate(files):
            result = cloudinary.uploader.upload(
                file.file, public_id=f"{new_art_object.id}:img:{i}:_:sculpture"
            )
            results.append(result["secure_url"])
        urls = json.dumps(results)

        # now creating sculpture
        new_sculpture = Sculpture(
            id=new_art_object.id,
            material=object.material,
            height=object.height,
            weight=object.weight,
            image=urls,
        )
        db.add(new_sculpture)
        db.commit()
        db.refresh(new_sculpture)

        data = {
            "artObjectId": new_art_object.id,
            "objectTitle": new_art_object.title,
            "objectDescription": new_art_object.description,
            "objectStyle": new_art_object.style,
            "objectEpoch": new_art_object.epoch,
            "objectOriginCountry": new_art_object.origin_country,
            "objectYear": new_art_object.year,
            "artistId": new_art_object.artist_id,
            "sculptureMaterial": new_sculpture.material,
            "sculptureHeight": new_sculpture.height,
            "sculptureWeight": new_sculpture.weight,
            "sculptureImage": urls,
        }

        return {
            "message": "Sculpture Art Object created successfully",
            "data": data,
        }
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/art_object/painting")
async def create_painting_(
    title: str = Form("title"),
    description: str = Form("desc"),
    style: str = Form(ObjectStyleEnum.BAROQUE),
    epoch: str = Form(EpochTypeEnum.MODERN),
    origin_country: str = Form(OriginEnum.ARAB),
    year: str = Form(datetime.datetime.date(datetime.datetime.now())),
    artist_id: str = Form(""),
    paint_type: str = Form(PaintingTypeEnum.INK),
    drawn_on: str = Form(PaintingDrawnOnEnum.PAPER),
    files: Annotated[list[UploadFile], File(description="upload images")] = None,
    db: Session = Depends(get_db),
):
    try:
        object = PaintingCreate(
            title=title,
            description=description,
            style=style,
            epoch=epoch,
            origin_country=origin_country,
            year=year,
            artist_id=artist_id,
            paint_type=paint_type,
            drawn_on=drawn_on,
        )

        # first creating art object
        new_art_object = ArtObject(
            title=object.title,
            description=object.description,
            style=object.style,
            epoch=object.epoch,
            origin_country=object.origin_country,
            year=object.year,
            artist_id=object.artist_id,
        )
        db.add(new_art_object)
        db.commit()
        db.refresh(new_art_object)

        results = []
        for i, file in enumerate(files):
            result = cloudinary.uploader.upload(
                file.file, public_id=f"{new_art_object.id}:img:{i}:_:painting"
            )
            results.append(result["secure_url"])
        urls = json.dumps(results)

        # now creating sculpture
        new_painting = Painting(
            id=new_art_object.id,
            paint_type=object.paint_type,
            drawn_on=object.drawn_on,
            image=urls,
        )
        db.add(new_painting)
        db.commit()
        db.refresh(new_painting)

        data = {
            "artObjectId": new_art_object.id,
            "objectTitle": new_art_object.title,
            "objectDescription": new_art_object.description,
            "objectStyle": new_art_object.style,
            "objectEpoch": new_art_object.epoch,
            "objectOriginCountry": new_art_object.origin_country,
            "objectYear": new_art_object.year,
            "artistId": new_art_object.artist_id,
            "paintingPaintType": new_painting.paint_type,
            "paintingDrawnOn": new_painting.drawn_on,
            "paintingImage": urls,
        }

        return {
            "message": "Sculpture Art Object created successfully",
            "data": data,
        }
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/art_object/other_art")
async def create_other_(
    title: str = Form("title"),
    description: str = Form("desc"),
    style: str = Form(ObjectStyleEnum.BAROQUE),
    epoch: str = Form(EpochTypeEnum.MODERN),
    origin_country: str = Form(OriginEnum.ARAB),
    year: str = Form(datetime.datetime.date(datetime.datetime.now())),
    artist_id: str = Form(""),
    type: str = Form(OtherTypeEnum.PHOTO),
    files: Annotated[list[UploadFile], File(description="upload images")] = None,
    db: Session = Depends(get_db),
):
    try:
        object = OtherArtCreate(
            title=title,
            description=description,
            style=style,
            epoch=epoch,
            origin_country=origin_country,
            year=year,
            artist_id=artist_id,
            type=type,
        )
        # first creating art object
        new_art_object = ArtObject(
            title=object.title,
            description=object.description,
            style=object.style,
            epoch=object.epoch,
            origin_country=object.origin_country,
            year=object.year,
            artist_id=object.artist_id,
        )
        db.add(new_art_object)
        db.commit()
        db.refresh(new_art_object)

        results = []
        for i, file in enumerate(files):
            result = cloudinary.uploader.upload(
                file.file, public_id=f"{new_art_object.id}:img:{i}:_:other_art"
            )
            results.append(result["secure_url"])
        urls = json.dumps(results)
        # now creating sculpture
        new_other_art = OtherArt(id=new_art_object.id, type=object.type, image=urls)
        db.add(new_other_art)
        db.commit()
        db.refresh(new_other_art)

        data = {
            "artObjectId": new_art_object.id,
            "objectTitle": new_art_object.title,
            "objectDescription": new_art_object.description,
            "objectStyle": new_art_object.style,
            "objectEpoch": new_art_object.epoch,
            "objectOriginCountry": new_art_object.origin_country,
            "objectYear": new_art_object.year,
            "artistId": new_art_object.artist_id,
            "OtherArtType": new_other_art.type,
            "OtherArtImage": urls,
        }

        return {
            "message": "Sculpture Art Object created successfully",
            "data": data,
        }
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/collection/new_collection")
async def create_new_collection_(
    collection: CollectionCreate,
    db: Session = Depends(get_db),
):
    try:

        new_collection = Collection(
            name=collection.name,
            type=collection.type,
            description=collection.description,
            address=collection.address,
            contact=collection.contact,
        )

        db.add(new_collection)
        db.commit()
        db.refresh(new_collection)
        return {"message": f"{new_collection.name} collection created successfully"}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/collection/borrowed")
async def create_borrowed_collection_(
    collections: list[BorrowedArtObjectBaseCreate],
    db: Session = Depends(get_db),
):
    try:
        collection_list = []
        for collection in collections:
            new_collection = BorrowedArtObject(
                date_borrowed=collection.date_borrowed,
                date_returned=collection.date_returned,
                art_object_id=collection.art_object_id,
                collection_id=collection.collection_id,
            )
            collection_list.append(new_collection)

        db.add_all(collection_list)
        db.commit()
        for i in range(0, len(collection_list)):
            db.refresh(collection_list[i])
        return {"message": "Borrowed collections created successfully"}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/collection/permanent")
async def create_permanent_collection_(
    collections: list[PermanentCollectionCreate],
    db: Session = Depends(get_db),
):
    try:
        collection_list = []
        for collection in collections:
            new_collection = PermanentCollection(
                date_acquired=collection.date_acquired,
                status=collection.status,
                cost=collection.cost,
                art_object_id=collection.art_object_id,
            )
            collection_list.append(new_collection)

        db.add_all(collection_list)
        db.commit()
        for i in range(0, len(collection_list)):
            db.refresh(collection_list[i])
        return {"message": "Permanent collections created successfully"}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/exhibition")
async def create_exhibition_(
    name: str = Form("ex_name"),
    start_date: str = Form(datetime.datetime.date(datetime.datetime.now())),
    end_date: str = Form(datetime.datetime.date(datetime.datetime.now())),
    files: Annotated[list[UploadFile], File(description="upload images")] = None,
    db: Session = Depends(get_db),
):
    try:
        exhibition = ExhibitionCreate(
            name=name, start_date=start_date, end_date=end_date
        )
        exhibition_id = uuid4()
        results = []
        for i, file in enumerate(files):
            result = cloudinary.uploader.upload(
                file.file, public_id=f"{exhibition_id}:img:{i}:_:exhibition"
            )
            results.append(result["secure_url"])
        urls = json.dumps(results)
        new_exhibition = Exhibition(
            name=exhibition.name,
            start_date=exhibition.start_date,
            end_date=exhibition.end_date,
            image=urls,
        )

        db.add(new_exhibition)
        db.commit()
        db.refresh(new_exhibition)
        return {"message": f"Exhibition created successfully", "data": new_exhibition}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/exhibition/upload_data")
async def create_exhibition_association_(
   exhibitions : list[ExhibitionArtObjectAssociationCreate],
    db: Session = Depends(get_db),
):
    try:
        exhibition_list = []
        for exhibition in exhibitions:
            new_exhibition = ExhibitionArtObjectAssociation(
                art_object_id=exhibition.art_object_id,
                exhibition_id=exhibition.exhibition_id
            )
            exhibition_list.append(new_exhibition)

        db.add_all(exhibition_list)
        db.commit()
        for i in range(0, len(exhibition_list)):
            db.refresh(exhibition_list[i])
        return {"message": "Exhibitions data uploaded successfully"}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}



@router.get("/get/artist")
async def get_artist_(db: Session = Depends(get_db)):
    try:
        artists = db.query(Artist).all()
        return {"message": "Artists fetched successfully", "data": artists}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}

@router.get("/get/exhibitions/{skip}/{limit}")
async def get_exhibitions_(skip:int=0, limit: int=10, db: Session = Depends(get_db)):
    try:

        exhibitions = db.query(Exhibition).offset(skip).limit(limit).all()
        return {"message": "Exhibitions found successfully", "data": exhibitions}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.get("/get/exhibitions/art_object/{skip}/{limit}")
async def get_exhibitions_(skip:int=0, limit: int=10, db: Session = Depends(get_db)):
    try:

        exhibitions = db.query(Exhibition).offset(skip).limit(limit).all()
        return {"message": "Exhibitions found successfully", "data": exhibitions}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}






