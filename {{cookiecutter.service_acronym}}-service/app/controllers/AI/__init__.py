#noqa
from app.controllers.AI.classifier import ClassifierModel
from app.controllers.AI.digitizer import DigitizerModel

global G_Model

G_Model = {
    "classifier": ClassifierModel(),
    "digitizer": DigitizerModel()
}