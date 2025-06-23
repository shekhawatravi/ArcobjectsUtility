import traceback
import requests
import json
import urllib

---- END of import

def evaluate_url(url:str, params:dict[str, Any]=None):
  """
    Performs the REST request on the provided `url` with provided `params`, and returns the response.

    =====================        =====================================================================================
    **Keys**                     **Description**
    ---------------------        -------------------------------------------------------------------------------------
    url:str                      A REST end point 'URL' of :class: `~ArcGIS Feature Layer. e.g. `https://<host>/arcgis/rest/services/<serviceName>/FeatureServer/<layerId>`
    ---------------------        -------------------------------------------------------------------------------------
    params:dict[str, Any]=None   Valid JSON dictionary. Default value is `None`. (e.g. `{"f": "json", "token": "<TOKEN>"}`)
    ---------------------        -------------------------------------------------------------------------------------
    =====================        =====================================================================================

    :returns:
      HTTP reponse.
  """

  try:
    request_params = {"f": "pjson"}
    if params:
      request_params.update(params)
    encoded_params = urllib.parse.urlencode(request_params)
    request = urllib.request.urlopen(url, encoded_params.encode('UTF-8'))
    response = request.read()
    json_reponse = json.loads(response)
    return json_reponse
  except:
    raise Exception(traceback.format_exc())
    return None
    

def getDomainValues(featureLayer_url:str, subTypeCode:int, fieldName:str)->list
  """
    Returns a list of dictionaries containing domain code and their values for the specified field name, based on the subtypes defined in the provided feature layer URL.

    =====================    =====================================================================================
    **Keys**                 **Description**
    ---------------------    -------------------------------------------------------------------------------------
    featureLayer_url:str     A REST end point 'URL' of :class: `~ArcGIS Feature Layer. e.g. `https://<host>/arcgis/rest/services/<serviceName>/FeatureServer/<layerId>`
    ---------------------    -------------------------------------------------------------------------------------
    subTypeCode:int          Value of subType of the layer. e.g. `0`
    ---------------------    -------------------------------------------------------------------------------------
    fieldName:str            Name of the field for which the domain values should be retrieved (e.g. `"lifecyclestatus"`)
    ---------------------    -------------------------------------------------------------------------------------
    =====================    =====================================================================================

    :returns:
      A list of dictionaries containing domain code and their values.

    .. code-block:: python
      #Returned list Example
      >>> domain_list = getDomainValues(featureLayer_url=https://<host>/arcgis/rest/services/<serviceName>/FeatureServer/<layerId>
                          subTypeCode:int, 
                          fieldName:"lifecyclestatus")
          [{"name": "Generation", "code": 1}, {"name": "Retired", "code": 5}, {"name": "Unknown", "code": 0}]
  """

  if featureLayer_url is None or subTypeCode is None or fieldName is None:
    raise Exception("Error while getting domain value. Invalid Parameters")
  
  domainValues = []

  param = {
      "f": "json",
      "token": "<TOKEN>"
  }
  response = evaluate_url(featureLayer_url, param)
  print(f"Response:: {response}")

  ST_fieldName = response.get('subtypeField')
  ST_list = response.get('types')
  # Loop through subTypes
  for st in ST_list:
    if st.get('id') == subTypeCode:
      if 'domains' in st:
        domains = st.get('domains')
        if fieldName in domains:
          domain_field = domains.get(fieldName)
          if 'codedValues' in domain_field:
            domainValues = domain_field.get('codedValues')
            break

  return domainValues

def getDomainCode(featureLayer_url:str, subTypeCode:int, fieldName:str, domainValue:str)->list
  """
    Returns a domain code as `int` for the specified domainValue of field name, based on the subtypes defined in the provided feature layer URL.

    =====================    =====================================================================================
    **Keys**                 **Description**
    ---------------------    -------------------------------------------------------------------------------------
    featureLayer_url:str     A REST end point 'URL' of :class: `~ArcGIS Feature Layer. e.g. `https://<host>/arcgis/rest/services/<serviceName>/FeatureServer/<layerId>`
    ---------------------    -------------------------------------------------------------------------------------
    subTypeCode:int          Value of subType of the layer. e.g. `0`
    ---------------------    -------------------------------------------------------------------------------------
    fieldName:str            Name of the field for which the domain values should be retrieved (e.g. `"lifecyclestatus"`)
    ---------------------    -------------------------------------------------------------------------------------
    domainValue:str          Domain value for which the domain code should be retrieved (e.g. `"Retired"`)
    ---------------------    -------------------------------------------------------------------------------------
    =====================    =====================================================================================

    :returns:
      A domain code as `int`.

    .. code-block:: python
      #Returned list Example
      >>> domain_list = getDomainCode(featureLayer_url=https://<host>/arcgis/rest/services/<serviceName>/FeatureServer/<layerId>
                          subTypeCode:int, 
                          fieldName:"lifecyclestatus",
                          domainValue:"Retired")
          5
  """
  
  domainValues = getDomainValues(featureLayer_url= featureLayer_url, subTypeCode= subTypeCode, fieldName= fieldName, domainValue= "Retired")
  if len(domainValues)>0:
    return next((d['code'] for d in domainValues if str(d['name']).casefold() == domainValue.casefold()), None)
  else:
    return None
