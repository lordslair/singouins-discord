# -*- coding: utf8 -*-

import os

# Discord variables
token   = os.environ['TOKEN']

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB_NAME = os.environ['SEP_REDIS_DB']

# PCS variables for remote storage
PCS_URL       = os.environ['SEP_PCS_URL']

# External URL
API_URL       = os.environ['SEP_API_URL']

# Admin token used from Discord
API_ADMIN_TOKEN = os.environ['SEP_ADMIN_TOKEN']
