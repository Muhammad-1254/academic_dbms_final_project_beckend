from enum import Enum


class PaintingTypeEnum(Enum):
    OIL = "oil"
    WATERCOLOR = "watercolor"
    ACRYLIC = "acrylic"
    INK = "ink"
    OTHER = "other"


class PaintingDrawnOnEnum(Enum):
    PAPER = "paper"
    CANVAS = "canvas"
    WOOD = "wood"
    METAL = "metal"
    OTHER = "other"

    

class ObjectStyleEnum(Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    RENAISSANCE = "renaissance"
    BAROQUE = "baroque"
    ROCOCO = "rococo"
    ABSTRACT = "abstract"
    OTHER = "other"


class SculptureMaterialEnum(Enum):
    WOOD = "wood"
    METAL = "metal"
    OTHER = "other"




class StatusTypeEnum(Enum):
    DISPLAY = "display"
    LOAN = "loan"
    STORED = "stored"


class OriginEnum(Enum):
    ITALIAN = "italian"
    EGYPTIAN = "egyptian"
    AMERICAN = "american"
    INDIAN = "indian"
    ARAB = "arab"
    OTHER = "other"


    
class ArtObjectType(Enum):
    PAINTING = "painting"
    SCULPTURE = "sculpture"
    OTHER = "other"
    
    
class EpochTypeEnum(Enum):
    RENAISSANCE = "renaissance"
    MODERN = "modern"
    ANCIENT = "ancient"
    OTHER = "other"


class GenderEnum(Enum):
    MALE = "male"
    FEMALE = "female"
    
class Role( Enum):
    ADMIN = "admin"
    MANAGER = 'manager'
    USER = 'user'
    
    
class ObjectOwnership(Enum):
    PERMANENT = "permanent"
    BORROWED = "borrowed"
    
    

