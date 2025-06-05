from models.database import assets_collection as collection
from pymongo.errors import PyMongoError

def fetch_assets_from_db():
    try:
        assets = collection.find({}, {"asset_id": 1, "name": 1}) 
        assets_list = [{"id": str(asset["asset_id"]), "name": asset["name"]} for asset in assets]
        return assets_list
    except PyMongoError as e:
        return {"error": str(e)}
