#####################################################################
# Copyright(C), 2022 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
from app.controllers.dbo.mongo.jwt_decode import MongoStore
from pydantic import BaseModel
from app.utils import exceptions as E
from typing import Union
from app.core.config import cfg
import jwt
import json
from fastapi import HTTPException
from app.schema.request import User


def get_user_by_client_id(client_id):
    """
    Args:
        client_id: Cognito Client ID
    Description:
        Search MongoDB to fetch Cognito Client Details
    Returns:
        User Details if found else None
    """
    client = MongoStore(db=cfg.store.mongodb.db, collection=cfg.store.mongodb.collection.clients)
    client = json.loads(client.GetDocument(oid=client_id))
    if not client:
        return None
    user = client["client_details"]
    user = User(**user)
    return user


def get_client(token: str):
    """
    Args:
        token: JWT Token
    Description:
        Decode the JWT Token and fetch the client details
    Returns:
        Client Details if found else None
    """
    try:
        client_id = jwt.decode(token, algorithms=["RS256"], options={"verify_signature": False})["client_id"]
        current_user = get_user_by_client_id(client_id)
        if not current_user:
            raise E.ClientNotFound(client_id)
        return current_user
    except Exception as e:
        raise E.JWTDecodeError(e)
