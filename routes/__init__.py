from flask import Blueprint

bp = Blueprint('routes', __name__)

from .auth import *
from .users import *