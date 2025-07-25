#####################################################################
# Copyright(C), 2025 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import os

from app.core.factory import create_app, setup_routers, setup_cors_middleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# setup variable

# setup app
app = create_app()
app = setup_routers(app)
app = setup_cors_middleware(app)
# Opentelemetery Instrumentation for FastAPI
FastAPIInstrumentor.instrument_app(app)
# Startup functions
@app.on_event("startup")
async def startup_checks():
    # add URL checks here - raise errors
    # add os environment checks here - raise error
    # intialise global values here
    return True

