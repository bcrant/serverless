import requests
import json
from pandas import json_normalize

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

import secretz

def restCall(specifier, survey_org, custom_form_id, url="https://parseapi.back4app.com/classes/"):
    """
    Parameters
    ----------
    specificer: string, required
        Parse model to query

    survey_org: string, required
        Organization to query results for

    custom_form_id: string, not required
        Custom form object id 

    url: string, required
        Parse endpoint
    Returns
    ------
    Pandas dataframe with query results

    """

    # combine base url with specifier
    combined_url = url + specifier
    params = dict()

    if specifier != 'FormResults' and specifier != 'FormAssetResults':
        params = {
            "order": "-updatedAt", "limit": 200000, "where":{
                json.dumps({
                    "surveyingOrganization": {
                        "$in": [survey_org]
                    }
                })
            }
        }
    else:
        # custom forms need to ensure that the correct custom form results are returned
        params = {
            "order": "-updatedAt", "limit": 200000, "where":{
                json.dumps({
                    "surveyingOrganization": {
                        "$in": [survey_org]
                    },
                    "formSpecificationsId": {
                        "$in": [custom_form_id]
                    }
                })
            }
        }


    headers = {
        "Content-Type": "application/json",
        "X-Parse-Application-Id": secretz.APP_ID,
        "X-Parse-REST-API-Key": secretz.REST_API_KEY,
    }
    
    response = requests.get(combined_url, params=params, headers=headers)

    json_obj = response.json()
    # normalize (ie flatten) data, turns it into a pandas df
    normalized = json_normalize(json_obj["results"])

    # join non surveyData forms to surveyData
    if specifier != 'SurveyData' and specifier != 'Assets':
        combined_url = url + 'SurveyData' if specifier != 'FormAssetResults' else url + 'Assets'
        params = {
            "order": "-updatedAt", "limit": 200000, "where":{
                json.dumps({
                    "surveyingOrganization": {
                        "$in": [survey_org]
                    }
                })
            }
        }
        response_primary = requests.get(combined_url, params=params, headers=headers)
        json_obj_primary = response_primary.json()
        normalized_primary = json_normalize(json_obj_primary["results"])
        normalized = normalized.rename(columns= {
            'objectId':'objectIdSupplementary',
            'client.objectId':'objectId',
            'surveyingUser':'surveyingUserSupplementary', 
            'surveyingOrganization':'surveyingOrganizationSupplementary',
            'createdAt':'createdAtSupplementary'
            })
        
        
        return normalized_primary, normalized


    return normalized, None
