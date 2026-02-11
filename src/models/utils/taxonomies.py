from enum import Enum


# ==========================================
# Temporal and Environmental Taxonomies
# ==========================================

class Season(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"
    SPRING = "spring"
    FALL = "fall"


class VisualTimeOfDay(str, Enum):
    DAY = "day"
    NIGHT = "night"


class WeatherCondition(str, Enum):
    CLEAR = "clear"
    RAINY = "rainy"
    CLOUDY = "cloudy"
    SNOWY = "snowy"


class LocationType(str, Enum):
    # Home and Private Spaces
    HOME = "home"

    # Public and Urban Spaces
    URBAN = "urban"
    WORKSPACE = "workspace"
    SCHOOL_UNIVERSITY = "school_university"
    STORE_SHOP = "store_shop"

    # Entertainment and Leisure
    RESTAURANT_CAFE = "restaurant_cafe"
    CLUB_DISCO = "club_disco"
    STADIUM_ARENA = "stadium_arena"

    # Fitness and Wellness
    GYM_FITNESS = "gym_fitness"
    POOL = "pool"
    SPA_WELLNESS = "spa_wellness"

    # Natural Environments
    BEACH_SEA = "beach_sea"
    MOUNTAIN_SNOW = "mountain_snow"
    FOREST_PARK = "forest_park"
    COUNTRYSIDE = "countryside"
    DESERT = "desert"
    LAKE_RIVER = "lake_river"
    AIRPORT_STATION = "airport_station"
    HOTEL_RESORT = "hotel_resort"
    LANDMARK_MONUMENT = "landmark_monument"

    # Transports
    CAR_INTERIOR = "car_interior"
    PUBLIC_TRANSPORT = "public_transport"
    BOAT_YACHT = "boat_yacht"
    PLANE = "plane"



# ==========================================
# Subject and Activity Taxonomies
# ==========================================

class SubjectType(str, Enum):
    HUMAN = "human"
    ANIMAL = "animal"
    FOOD_DRINK = "food_drink"
    LANDSCAPE = "landscape"
    ARCHITECTURE = "architecture"
    VEHICLE = "vehicle"
    PRODUCT_GADGET = "product_gadget"
    ART_ILLUSTRATION = "art_illustration"
    MEME_TEXT = "meme_text"
    SCREENSHOT = "screenshot"
    OBJECT_DETAIL = "object_detail"


class PeopleCount(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    GROUP = "group"
    NONE = "none"


class MainActivity(str, Enum):
    POSING = "posing"
    EATING_DRINKING = "eating_drinking"
    WORKING_STUDYING = "working_studying"
    TRAINING_SPORT = "training_sport"
    TRAVELING_SIGHTSEEING = "traveling_sightseeing"
    DRIVING_RIDING = "driving_riding"
    RELAXING_LEISURE = "relaxing_leisure"
    KISSING_HUGGING = "kissing_hugging"
    CELEBRATING_PARTYING = "celebrating_partying"
    SHOPPING = "shopping"
    ATTENDING_EVENT = "attending_event"
    SPEAKING_PRESENTING = "speaking_presenting"



# ==========================================
# Social and Contextual Taxonomies
# ==========================================

class SocialContext(str, Enum):
    SOLO = "solo"
    COUPLE_ROMANTIC = "couple_romantic"
    FRIENDS_GROUP = "friends_group"
    PARTY_NIGHTLIFE = "party_nightlife"
    FAMILY_GATHERING = "family_gathering"
    PET_COMPANIONSHIP = "pet_companionship"
    WORK_COLLEAGUES = "work_colleagues"
    FORMAL_EVENT = "formal_event"


class ContentIntention(str, Enum):
    MEMORY_NOSTALGIA = "memory_nostalgia"
    FLEXING_ACHIEVEMENT = "flexing_achievement"
    AESTHETIC_VIBE = "aesthetic_vibe"
    LIFE_UPDATE = "life_update"
    HUMOR_ENTERTAINMENT = "humor_entertainment"
    INFORMATIVE_EDUCATIONAL = "informative_educational"
    PROMOTIONAL_AD = "promotional_ad"
    VENTING_EMOTIONAL = "venting_emotional"



# ==========================================
# Emotional and Stylistic Taxonomies
# ==========================================

class Mood(str, Enum):
    JOYFUL_HAPPY = "joyful_happy"
    MELANCHOLIC_SAD = "melancholic_sad"
    RELAXED_CHILL = "relaxed_chill"
    EXCITED_EUPHORIC = "excited_euphoric"
    ROMANTIC_LOVE = "romantic_love"
    CONFIDENT_BOLD = "confident_bold"
    SERIOUS_FOCUSED = "serious_focused"
    TIRED_EXHAUSTED = "tired_exhausted"
    ANGRY_FRUSTRATED = "angry_frustrated"
    SEDUCTIVE_FLIRTY = "seductive_flirty"
    SILLY_PLAYFUL = "silly_playful"


class FashionStyle(str, Enum):
    CASUAL_BASIC = "casual_basic"
    STREETWEAR_URBAN = "streetwear_urban"
    ELEGANT = "elegant"
    SPORTY_ATHLETIC = "sporty_athletic"
    VINTAGE_RETRO = "vintage_retro"
    SWIMWEAR = "swimwear"