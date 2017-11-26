#!/usr/bin/python

import simplejson
# import regex as RE
import json
import jsonschema as jjsonschema

import xml.etree.cElementTree as ET
import optparse, sys, os
import pdb
import exception
import logging


# TODO commented since they prevented compile. Take a look Mohsen
# S = {
#     "SEC_U": SCHEMA_SECRET_UPDATE,
#     "SEC_INFRA": SCHEMA_SECRET_UPDATE,
#     "SEC_C": SCHEMA_SECRET_CREATE,
# }

class JsonError(Exception):
    def __init__(self, message):
        super(JsonError, self).__init__(message)
        self.message = message


def load(instance_str):
    if isinstance(instance_str, dict):
        return instance_str
    elif not isinstance(instance_str, basestring):
        return []
    return json.loads(instance_str)


def v(instance_str, schema_code):
    if isinstance(instance_str, dict):
        return instance_str
    elif not isinstance(instance_str, basestring):
        raise JsonError("Json instance is not of type string.")
    try:
        jobj = json.loads(instance_str)
    except ValueError as e:
        raise JsonError("could not load json. error is " + str(e))
    try:
        jjsonschema.validate(jobj, S[schema_code])
    except jjsonschema.ValidationError as e:
        raise JsonError("Json Validation error; %s in schema %s" % (e, schema_code))
    except jjsonschema.SchemaError as e:
        raise JsonError("Json Schema error; %s in schema %s" % (e, schema_code))
    except jjsonschema.UnknownType as e:
        raise JsonError("Json Unknown type error; %s in schema %s" % (e, schema_code))
    except Exception as e:
        raise JsonError("Json Unknown error; %s in schema %s" % (e, schema_code))

    return jobj


def str(object, indent=1):
    try:
        sj = simplejson.dumps(object, indent=indent, sort_keys=True)
    except Exception as e:
        return ""
    return sj


def dumps(dictionary):
    return json.dumps(dictionary)