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
    Query,
)
from sqlalchemy.orm import Session, joinedload
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
    OriginEnum,
    ObjectStyleEnum,
    StatusTypeEnum,
    GenderEnum,
    ArtObjectType,
)
from sqlalchemy import func, and_, desc
import datetime

router = APIRouter()


def temp_date():
    return datetime.datetime.date(datetime.datetime.now)


@router.post("/create/artist")
async def create_artist_(
    artists: list[ArtistCreate],
    db: Session = Depends(get_db),
):
    artist_exists = []
    new_artists = []
    try:
        for artist in artists:
            artist_exist = db.query(Artist).filter(Artist.name == artist.name).first()
            if artist_exist:
                print(f"artist_exist.name: {artist_exist.name}")
                artist_exists.append(artist_exist.name)
                continue
            new_artist = Artist(
                name=artist.name,
                description=artist.description,
                artist_bio=artist.artist_bio,
                gender=artist.gender,
                origin_country=artist.origin_country,
                date_of_birth=artist.date_of_birth,
                date_of_died=artist.date_of_died,
                wiki_qid=artist.wiki_qid,
                ulan=artist.ulan,
            )
            new_artists.append(new_artist)

        db.add_all(new_artists)
        db.commit()
        for i in range(0, len(new_artists)):
            db.refresh(new_artists[i])
        return {
            "message": "artist created successfully",
            "data": {"new_artists": new_artists, "artist_exists": new_artists},
        }
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.post("/create/art_object/sculpture")
async def create_sculpture_(
    title: str = Form("title"),
    description: str = Form("desc"),
    dimensions: str = Form("12*23"),
    department: str = Form("department"),
    style: str = Form(ObjectStyleEnum.BAROQUE),
    epoch: str = Form("epoch"),
    origin_country: str = Form("country"),
    year: str = Form("2000"),
    artist_id: str = Form("8bac6e53-bd66-4928-bb9d-73e4a8f2b901"),
    material: str = Form("material"),
    height: str = Form("100"),
    width: str = Form("100"),
    weight: str = Form("12gm"),
    files: list[UploadFile] = None,
    db: Session = Depends(get_db),
):
    try:
        object_type = ArtObjectType.SCULPTURE

        object = SculptureCreate(
            title=title,
            description=description,
            dimensions=dimensions,
            department=department,
            style=style,
            object_type=object_type,
            epoch=epoch,
            origin_country=origin_country,
            year=year,
            artist_id=artist_id,
            material=material,
            height=height,
            width=width,
            weight=weight,
        )
        # first creating art object
        new_art_object = ArtObject(
            title=object.title,
            description=object.description,
            dimensions=object.dimensions,
            department=object.department,
            style=object.style,
            object_type=object.object_type,
            epoch=object.epoch,
            origin_country=object.origin_country,
            year=object.year,
            artist_id=object.artist_id,
        )
        db.add(new_art_object)
        db.commit()
        db.refresh(new_art_object)
        results = []
        if files:
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
            width=object.width,
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
            "object_type": new_art_object.object_type,
            "objectOriginCountry": new_art_object.origin_country,
            "objectYear": new_art_object.year,
            "artistId": new_art_object.artist_id,
            "sculptureMaterial": new_sculpture.material,
            "sculptureHeight": new_sculpture.height,
            "sculptureWidth": new_sculpture.weight,
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
    dimensions: str = Form("12*23"),
    department: str = Form("department"),
    style: str = Form(ObjectStyleEnum.BAROQUE),
    epoch: str = Form("epoch"),
    origin_country: str = Form("country"),
    year: str = Form("2000"),
    artist_id: str = Form(""),
    paint_type: str = Form("paint_type"),
    drawn_on: str = Form("drawn_on"),
    files: Annotated[list[UploadFile], File(description="upload images")] = None,
    db: Session = Depends(get_db),
):
    try:
        object_type = ArtObjectType.PAINTING

        object = PaintingCreate(
            title=title,
            description=description,
            style=style,
            epoch=epoch,
            object_type=object_type,
            origin_country=origin_country,
            year=year,
            artist_id=artist_id,
            paint_type=paint_type,
            drawn_on=drawn_on,
            department=department,
            dimensions=dimensions,
        )

        # first creating art object
        new_art_object = ArtObject(
            title=object.title,
            description=object.description,
            dimensions=object.dimensions,
            department=object.department,
            style=object.style,
            object_type=object.object_type,
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
            "object_type": new_art_object.object_type,
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
    dimensions: str = Form("12*23"),
    department: str = Form("department"),
    style: str = Form(ObjectStyleEnum.BAROQUE),
    epoch: str = Form("epoch"),
    origin_country: str = Form("country"),
    year: str = Form("2000"),
    artist_id: str = Form(""),
    other_art_type: str = Form("other_art_type"),
    files: Annotated[list[UploadFile], File(description="upload images")] = None,
    db: Session = Depends(get_db),
):
    try:
        object_type = ArtObjectType.OTHER
        object = OtherArtCreate(
            title=title,
            description=description,
            dimensions=dimensions,
            department=department,
            style=style,
            epoch=epoch,
            object_type=object_type,
            origin_country=origin_country,
            year=year,
            artist_id=artist_id,
            type=other_art_type,
        )

        # first creating art object
        new_art_object = ArtObject(
            title=object.title,
            description=object.description,
            dimensions=object.dimensions,
            department=object.department,
            style=object.style,
            object_type=object.object_type,
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
            "object_type": new_art_object.object_type,
            "objectOriginCountry": new_art_object.origin_country,
            "objectYear": new_art_object.year,
            "artistId": new_art_object.artist_id,
            "OtherArtType": new_other_art.type,
            "OtherArtImage": urls,
        }

        return {
            "message": f"{object_type} Art Object created successfully",
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
    exhibitions: list[ExhibitionArtObjectAssociationCreate],
    db: Session = Depends(get_db),
):
    try:
        exhibition_list = []
        for exhibition in exhibitions:
            new_exhibition = ExhibitionArtObjectAssociation(
                art_object_id=exhibition.art_object_id,
                exhibition_id=exhibition.exhibition_id,
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


@router.get("/get/artist/all/{skip}/{limit}")
async def get_artist_(
    
   sort_by_dob: bool = Query(True),
    sort_by_name: bool = Query(True),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
    ):
    try:
        if sort_by_dob:
            query = (
                db.query(Artist).order_by(Artist.date_of_birth)
            )
        else:
            query = (
                db.query(Artist).order_by(Artist.date_of_birth.desc())
            )
        if sort_by_name:
            query = query.order_by(Artist.name)
        else:
            query = query.order_by(Artist.name.desc())
        artists = query.offset(skip).limit(limit).all()

        return {"message": "Artists fetched successfully", "data": artists}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}", "data": []}


@router.get("/get/artist/id/{artist_id}")
async def get_artist_(artist_id: str, db: Session = Depends(get_db)):
    try:
        artists_exist = db.query(Artist).filter(Artist.id == artist_id).first()
        if artists_exist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found"
            )
        return {"message": "Artists fetched successfully", "data": artists_exist}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}
@router.get("/get/artist/all/ids")
async def get_artist_ids_(db: Session = Depends(get_db)):
    try:
        # Query to get all artist IDs
            ids = db.query(Artist.id).all()
            return {"data": [id[0] for id in ids]}

    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}
# search artist by name
@router.get("/get/artist/name/{artist_name}")
async def get_artist_(artist_name: str, db: Session = Depends(get_db)):
    try:
        artists = (
            db.query(Artist).filter(Artist.name.like(f"%{artist_name}%")).limit(5).all()
        )
        return {"message": "Artists fetched successfully", "data": artists}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.get("/get/art_object/artist/all/{artist_id}")
async def get_artist_data(
    artist_id: str,  db: Session = Depends(get_db)
):
    try:
     

        artist_exist = db.query(Artist).filter(Artist.id == artist_id).first()
        if artist_exist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found"
            )

        # Query for ArtObjects by artist_id with joined loading of related types
        art_objects_query = (
            db.query(ArtObject)
            .filter(ArtObject.artist_id == artist_id)
            .options(
                joinedload(ArtObject.sculpture),
                joinedload(ArtObject.painting),
                joinedload(ArtObject.other),

            )
        )

        art_objects = art_objects_query.all()
        if art_objects is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ArtObjects not found"
            )
        data = []
        for art_object in art_objects:
            if art_object.object_type == ArtObjectType.SCULPTURE and not art_object.sculpture.image is  None:
                
                data.append(
                    {
                    "id": art_object.id,
                    "object_type": art_object.object_type,
                    "image": art_object.sculpture.image,
                    }
            )
            elif art_object.object_type == ArtObjectType.PAINTING and not art_object.painting.image is  None:
                
                data.append(
                    {
                    "id": art_object.id,
                    "object_type": art_object.object_type,
                    "image": art_object.painting.image,
                    }
            )
            elif art_object.object_type == ArtObjectType.OTHER and not art_object.other.image is  None:
                
                data.append(
                    {
                    "id": art_object.id,
                    "object_type": art_object.object_type,
                    "image": art_object.other.image,
                    }
            )
        
        
        
        return {"art_objects": data, "artist":artist_exist}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.get("/get/art_object/sculpture/all/{skip}/{limit}")
async def get_sculpture_all_(
    sort_data_asc: bool = Query(True),
    sort_data_title: bool = Query(True),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    try:
        if sort_data_asc:
            art_objects_query = (
                db.query(ArtObject)
                .options(joinedload(ArtObject.sculpture))
                .filter(ArtObject.sculpture != None)
                .order_by(ArtObject.year)
            )
        else:
            art_objects_query = (
                db.query(ArtObject)
                .options(joinedload(ArtObject.sculpture))
                .filter(ArtObject.sculpture != None)
                .order_by(ArtObject.year.desc())
            )
        if sort_data_title:
            art_objects_query = art_objects_query.order_by(ArtObject.title)
        else:
            art_objects_query = art_objects_query.order_by(ArtObject.title.desc())

        art_objects = art_objects_query.offset(skip).limit(limit).all()

        return {"message": "Sculpture fetched successfully", "data": art_objects}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}", "data": []}


@router.get("/get/art_object/painting/all/{skip}/{limit}")
async def get_painting_all_(
    sort_data_asc: bool = Query(True),
    sort_data_title: bool = Query(True),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    try:
        if sort_data_asc:
            art_objects_query = (
                db.query(ArtObject)
                .options(joinedload(ArtObject.painting))
                .filter(ArtObject.painting != None)
                .order_by(ArtObject.year)
            )
        else:
            art_objects_query = (
                db.query(ArtObject)
                .options(joinedload(ArtObject.painting))
                .filter(ArtObject.painting != None)
                .order_by(ArtObject.year.desc())
            )
        if sort_data_title:
            art_objects_query = art_objects_query.order_by(ArtObject.title)
        else:
            art_objects_query = art_objects_query.order_by(ArtObject.title.desc())

        art_objects = art_objects_query.offset(skip).limit(limit).all()

        return {"message": "Paintings fetched successfully", "data": art_objects}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}", "data": []}


@router.get("/get/art_object/other_art/all/{skip}/{limit}")
async def get_other_art_all_(
    sort_data_asc: bool = Query(True),
    sort_data_title: bool = Query(True),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    try:
        if sort_data_asc:
            art_objects_query = (
                db.query(ArtObject)
                .options(joinedload(ArtObject.other))
                .filter(ArtObject.other != None)
                .order_by(ArtObject.year)
            )
        else:
            art_objects_query = (
                db.query(ArtObject)
                .options(joinedload(ArtObject.other))
                .filter(ArtObject.other != None)
                .order_by(ArtObject.year.desc())
            )
        if sort_data_title:
            art_objects_query = art_objects_query.order_by(ArtObject.title)
        else:
            art_objects_query = art_objects_query.order_by(ArtObject.title.desc())

        art_objects = art_objects_query.offset(skip).limit(limit).all()

        return {"message": "Paintings fetched successfully", "data": art_objects}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}", "data": []}


# searching paintings with name
@router.get("/get/paintings/name/")
async def get_painting_by_name_(
    painting_name: str = Query(""),
    art_object_type: ArtObjectType = Query(""),
    db: Session = Depends(get_db),
):
    try:
        if art_object_type.value == "sculpture":
            query = (
                db.query(ArtObject)
                .filter(ArtObject.object_type == ArtObjectType.SCULPTURE)
                .filter(ArtObject.title.ilike(f"%{painting_name}%"))
            )

        elif art_object_type.value == "painting":
            query = (
                db.query(ArtObject)
                .filter(ArtObject.object_type == ArtObjectType.PAINTING)
                .filter(ArtObject.title.ilike(f"%{painting_name}%"))
            )

        elif art_object_type.value == "other":
            query = (
                db.query(ArtObject)
                .filter(ArtObject.object_type == ArtObjectType.OTHER)
                .filter(ArtObject.title.ilike(f"%{painting_name}%"))
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid object type"
            )

        data = query.limit(5).all()
        return {"message": "Painting fetched successfully", "data": data}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


# search exhibition by name
@router.get("/get/exhibitions/name/{exhibition_name}")
async def get_exhibitions_by_name_(exhibition_name: str, db: Session = Depends(get_db)):
    try:
        exhibitions = (
            db.query(Exhibition)
            .filter(Exhibition.name.like(f"%{exhibition_name}%"))
            .limit(5)
            .all()
        )
        return {"message": "Exhibitions fetched successfully", "data": exhibitions}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.get("/get/exhibitions/")
async def get_exhibitions_by_id_(
    exhibition_id: str=Query(""), db: Session = Depends(get_db)):
    try:
        exhibition = (
            db.query(Exhibition)
            .filter(Exhibition.id==exhibition_id).first()
        )
        return {"message": "Exhibition fetched successfully", "data": exhibition}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}



@router.get("/get/exhibitions/all/ids")
async def get_exhibitions_ids_(
     db: Session = Depends(get_db)):
    try:
        query = db.query(Exhibition.id).all()
        ids = [id[0] for id in query]
        return {"data":ids} 
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}

@router.get("/get/exhibitions/all/{skip}/{limit}")
async def get_exhibitions_all_(
    sort_data_asc: bool = Query(True),
    sort_data_title: bool = Query(True),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    try:
        if sort_data_asc:
            exhibitions_query = (
                db.query(Exhibition
                ).order_by(Exhibition.end_date)
            )
        else:
            exhibitions_query = (
                db.query(Exhibition
                ).order_by(Exhibition.end_date.desc())
            )
        if sort_data_title:
            exhibitions_query = exhibitions_query.order_by(Exhibition.name)
        else:
            exhibitions_query = exhibitions_query.order_by(Exhibition.name.desc())

        exhibitions = exhibitions_query.offset(skip).limit(limit).all()

        return {"message": "Paintings fetched successfully", "data": exhibitions}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}", "data": []}



@router.get("/get/exhibitions/art_object/{exhibition_id}")
async def get_exhibitions_(
    exhibition_id: str, db: Session = Depends(get_db)
):
    try:

        exhibition_exist = (
            db.query(Exhibition).filter(Exhibition.id == exhibition_id).first()
        )
        if exhibition_exist is None:
            return {"message": "Exhibition not found"}
        exhibition_data = (
            db.query(ExhibitionArtObjectAssociation)
            .filter(ExhibitionArtObjectAssociation.exhibition_id == exhibition_id).all()
        )
        art_object_data = (
            db.query(ArtObject
            ).options(joinedload(ArtObject.sculpture), joinedload(ArtObject.painting), joinedload(ArtObject.other)
            ).filter(ArtObject.id.in_([x.art_object_id for x in exhibition_data]))
            .all()
        )
        temp_list = []
        for data in art_object_data:
            if data.object_type == ArtObjectType.SCULPTURE and not data.sculpture is None:
                temp_list.append({
                    "id":data.id,
                    "object_type":data.object_type,
                    "image":data.sculpture.image            
                    })
            elif data.object_type == ArtObjectType.PAINTING and not data.painting is None: 
                temp_list.append({
                    "id":data.id,
                    "object_type":data.object_type,
                    "image":data.painting.image            
                    })
            elif data.object_type == ArtObjectType.OTHER and not data.other is None:
                temp_list.append({
                    "id":data.id,
                    "object_type":data.object_type,
                    "image":data.other.image            
                    })
        
        data = {"exhibition": exhibition_exist, 
                "art_objects":temp_list}
        return {"message": "Exhibitions found successfully", "data": data}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


@router.get("/get/collections/permanent/{permanents_id}/{skip}/{limit}")
async def get_permanent_collection_(
    permanents_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    try:
        permanent_collections = (
            (
                db.query(PermanentCollection)
                .filter(PermanentCollection.id == permanents_id)
                .options(
                    joinedload(PermanentCollection.art_object).joinedload(
                        ArtObject.sculpture
                    ),
                    joinedload(PermanentCollection.art_object).joinedload(
                        ArtObject.painting
                    ),
                    joinedload(PermanentCollection.art_object).joinedload(
                        ArtObject.other
                    ),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        art_objects = {"sculpture": [], "painting": [], "other": []}
        for permanent_collection in permanent_collections:

            art_object = permanent_collection.art_object

            if art_object.sculpture:
                art_objects["sculpture"].append(art_object)
            if art_object.painting:
                art_objects["painting"].append(art_object)

            if art_object.other:
                art_objects["other"].append(art_object)

        return {
            "message": "Permanent collections found successfully",
            "data": art_objects,
        }
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}


# get art object by id
@router.get("/get/art_object/")
async def get_art_object_by_id_(
    object_type: ArtObjectType = Query(""),
    art_object_id: str = Query(""),
    db: Session = Depends(get_db),
):
    try:
        if object_type == ArtObjectType.SCULPTURE:
            art_object = (
                db.query(ArtObject)
                .filter(ArtObject.id == art_object_id)
                .options(joinedload(ArtObject.sculpture))
                .first()
            )

        elif object_type == ArtObjectType.PAINTING:
            art_object = (
                db.query(ArtObject)
                .filter(ArtObject.id == art_object_id)
                .options(joinedload(ArtObject.painting))
                .first()
            )

        elif object_type == ArtObjectType.OTHER:
            art_object = (
                db.query(ArtObject)
                .filter(ArtObject.id == art_object_id)
                .options(joinedload(ArtObject.other))
                .first()
            )

        if art_object is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ArtObject not found"
            )

        return {
            "message": f"Art Object type: {object_type} fetched successfully",
            "data": art_object,
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong: {e}",
        )


# for fetching paths of all art id of art object
@router.get("/get/art_object/id/all")
async def get_painting_object_path_(
    object_type: ArtObjectType = Query(""), db: Session = Depends(get_db)
):
    try:
        if object_type == ArtObjectType.SCULPTURE:
            art_object_ids = db.query(ArtObject.id).filter(
                ArtObject.object_type == ArtObjectType.SCULPTURE
            )
        elif object_type == ArtObjectType.PAINTING:
            art_object_ids = db.query(ArtObject.id).filter(
                ArtObject.object_type == ArtObjectType.PAINTING
            )
        elif object_type == ArtObjectType.OTHER:
            art_object_ids = db.query(ArtObject.id).filter(
                ArtObject.object_type == ArtObjectType.OTHER
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid object type"
            )
        ids = [id[0] for id in art_object_ids.all()]
        return {"data": ids}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}



# fetch homepage data
@router.get("/get/homepage/data")
async def get_homepage_data_(
    db: Session = Depends(get_db),
):
    try:
        sculpture_data = db.query(ArtObject).options(
            joinedload(ArtObject.sculpture)
            ).filter(ArtObject.sculpture !=None
            ).order_by(ArtObject.year).limit(10).all()
        painting_data = db.query(ArtObject).options(
            joinedload(ArtObject.painting)
            ).filter(ArtObject.painting !=None
            ).order_by(ArtObject.year).limit(10).all()
        other_data = db.query(ArtObject).options(
            joinedload(ArtObject.other)
            ).filter(ArtObject.other !=None
            ).order_by(ArtObject.year).limit(10).all()
        exhibition_data = db.query(Exhibition).order_by(Exhibition.end_date).limit(5).all()
        
        

        data = {"sculpture_data":sculpture_data,"painting_data":painting_data,"other_data":other_data,"exhibition_data":exhibition_data}
        
        return {"message": "Home page data fetched successfully", "data": data}
    except Exception as e:
        print(e)
        return {"message": f"something went wrong: {e}"}