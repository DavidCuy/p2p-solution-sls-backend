from typing import Dict, Type
from core_db.BaseModel import BaseModel
import core_utils.environment as env

class ResourceReference:

    def __init__(self, model: Type[BaseModel], prefix_model: str = "", sufix_model: str = "", action: str = "GET", is_json_resp = True) -> None:
        self.Name = model.__name__
        self.Action = action
        self.Ref = f"{env.APP_URL}/{prefix_model}/{model.model_path_name}{sufix_model}" if is_json_resp is True else f"{env.APP_URL}/{model.model_path_name}{sufix_model}"
    
    def to_dict(self) -> Dict:
        return {
            "Name": self.Name,
            "Action": self.Action,
            "Ref": self.Ref
        }