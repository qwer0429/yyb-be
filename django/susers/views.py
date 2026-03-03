from django.shortcuts import render
from django.http import HttpResponse
from django.forms.models import model_to_dict
# from django.http import StreamingHttpResponse
from django.http import FileResponse
from django.db.models import Q
from susers.api import token_required
from rest_framework import viewsets, permissions
from .models import User

from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
import logging
logger = logging.getLogger(__name__)

import uuid
import json
import pdb
import re
import requests
import os
import subprocess

from rest_framework.permissions import BasePermission




