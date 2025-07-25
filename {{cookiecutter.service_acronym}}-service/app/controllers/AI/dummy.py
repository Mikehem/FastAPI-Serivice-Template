#####################################################################
# Copyright(C), {{cookiecutter.devleopment_year}} xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import random

from app.controllers.dbo.files import G_L1_Labels, G_L2_Labels, G_L3_Labels

class DummyModel():
    def __init__(self):
        pass
    
    def L1_Classifier(self, text:str, L2_label:str=None):
        return random.choice(G_L1_Labels).replace("\n","")

    def L2_Classifier(self, text:str):
        return random.choice(G_L2_Labels).replace("\n","")

    def L3_Classifier(self, text:str):
        return random.choice(G_L3_Labels).replace("\n","")

