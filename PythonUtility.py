import traceback
import requests
import json
import urllib

#---- END of import

def query_arcgis_layer_rest_url(url:str, token:str, where_clause:str="1=1", outFields:str="*", returnGeometry:bool=False, resultoffset:int=0, batch_size:int=2000 )->[]:
  """
    Query `ArcGIS Feature Layer` using the REST request on the provided query `URL` and returns result as `list` of features.

    =====================        =====================================================================================
    **Keys**                     **Description**
    ---------------------        -------------------------------------------------------------------------------------
    url:str                      A REST end point of query 'URL' of :class: `~ArcGIS Feature Layer. e.g. `https://<host>/arcgis/rest/services/<serviceName>/FeatureServer/<layerId>/query`
    ---------------------        -------------------------------------------------------------------------------------
    token:str                    Valid JSON dictionary. Default value is `None`. (e.g. `{"f": "json", "token": "<TOKEN>"}`)
    ---------------------        -------------------------------------------------------------------------------------
    where_clause:str="1=1"       Where clause to restrict the resultset returned from the query. Defautl it will return `All` the records.
    ---------------------        -------------------------------------------------------------------------------------
    outFields:str="*"            Output feields to be returned in the result, field names shall be comma separated incase of multiple fields. Default it will return `All` the fields.
    ---------------------        -------------------------------------------------------------------------------------
    returnGeometry:bool=False    Wether to return geometry or not. Default `does not` return geometry.
    ---------------------        -------------------------------------------------------------------------------------
    resultoffset:int=0           This option can be used for fetching query results by skipping the specified number of records and starting from the next record (that is, `resultOffset` + 1). The default is `0`. This parameter only applies if `supportsPagination` is `true`. You can use this option to fetch records that are beyond `maxRecordCount`.
    ---------------------        -------------------------------------------------------------------------------------
    batch_size:int=2000          This option can be used for fetching query results up to the `resultRecordCount` specified. When `resultOffset` is specified but this parameter is not, the map service defaults it to `maxRecordCount`. The maximum value for this parameter is the value of the layer's `maxRecordCount` property. The minimum value entered for this parameter cannot be below 1. This parameter only applies if `supportsPagination` is `true`.
    =====================        =====================================================================================

    :returns:
      `list` of features.

  """
  features = []
  offset = resultoffset
  while True:
    params = {
      "f": "json",
      "token": token,
      "where": where_clause,
      "outFields": outFields,
      "returnGeometry": returnGeometry,
      resultoffset:offset,
      "resultRecordCount": batch_size
    }
    response = evaluate_url(url=url, params=params)
    batch = res.get("features",[])
    if not batch:
      break
    features.extend(batch)
    offset += batch_size
  
  return features

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
    

def getDomainValues(featureLayer_url:str, subTypeCode:int, fieldName:str)->list:
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
          if 'type' in domain_field and domain_field['type'] == 'inherited':
            flds = [f for f in response['fields'] if f['name'] == fieldName]
            if len(flds) > 0 and 'domain' in flds[0] and 'codedValues' in flds[0]['domain']:
              domainValues = flds[0]['domain']['codedValues']
              break

  return domainValues

def getDomainCode(featureLayer_url:str, subTypeCode:int, fieldName:str, domainValue:str)->list:
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
    return next((d['code'] for d in domainValues if str(d['name']).lower() == domainValue.lower()), None)
  else:
    return None

# ==========[START] Version Management Related ....

def get_version_guid(version_url:str, full_version_name:str, token:str=None)->str:
  """
    Returns the `GUID` of the provided version name from the versions' `URL`.

    =====================    =====================================================================================
    **Keys**                 **Description**
    ---------------------    -------------------------------------------------------------------------------------
    version_url:str          A REST end point 'URL' of ArcGIS Version e.g. `https://<host>/arcgis/rest/services/<serviceName>/VersionManagementServer/versions`.
    ---------------------    -------------------------------------------------------------------------------------
    full_version_name:str    name of the version for which `GUID` to be returned.
    ---------------------    -------------------------------------------------------------------------------------
    token:str                Valid JSON dictionary. Default value is `None`. (e.g. `{"f": "json", "token": "<TOKEN>"}`)
    ---------------------    -------------------------------------------------------------------------------------
    =====================    =====================================================================================

    :returns:
      A version `GUID` as `str`.

  """

  params = {
    "f": "json",
    "token": token,
    }

  response = evaluate_url(url= version_url, params= params)
  versions = response.get('versions')
  if versions is None:
    raise Exception(f"Version '{full_version_name}' not found.")
  
  for version in versions:
    if str(version['versionName']).lower() == full_version_name.lower(): # comparing by ignoring CASE.
      return version['versionGuid'].strip("{}") # Remove curly braces and return without it.

  raise Exception(f"Version '{full_version_name}' not found.")


def purge_lock(version_purge_lock_url:str, full_version_name:str, token:str=None)->str:
  """
    Purge the provided version name. it removes the lock.

    =====================       =====================================================================================
    **Keys**                    **Description**
    ---------------------       -------------------------------------------------------------------------------------
    version_purge_lock_url:str  A REST end point 'URL' of ArcGIS Version e.g. `https://<host>/arcgis/rest/services/<serviceName>/VersionManagementServer/purgeLock`.
    ---------------------       -------------------------------------------------------------------------------------
    full_version_name:str       name of the version to be purged.
    ---------------------       -------------------------------------------------------------------------------------
    token:str                   Valid JSON dictionary. Default value is `None`. (e.g. `{"f": "json", "token": "<TOKEN>"}`)
    ---------------------       -------------------------------------------------------------------------------------
    =====================       =====================================================================================

    :returns:
      A True | False `bool`.

  """

  params = {
    "f": "json",
    "token": token,
    "versionName": full_version_name
    }

  response = evaluate_url(url= version_purge_lock_url, params= params)
  if not response.get('success'):
    return True
  else:
    return False

  raise Exception(f"Purge lock failed for '{full_version_name}'.")

# ==========[END] Version Management Related