import traceback
import requests
import json
import urllib

import time
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone

#---- END of import

class UTILS:
  @staticmethod
  def split_camel_case(text):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', text)

  @staticmethod
  def chunk_array(array, chunk_size=100):
    return [lst[i:i + size] for i in range(0, len(lst), size)]

  @staticmethod
  def getConfigValue(configs, key, default=None):
    if key not in configs or configs[key] == None:
      return default
    return configs[key]

  @staticmethod
  def get_epoch_from_offset(hours_offset:float)->int:
    """
    Returns the epoch time (seconds since 1970-01-01) for the current time plus the given offset in hours.

    :param hours_offset: Number of hours to offset from current time (can be negative)
    :return: Epoch time as an integer
    """
    target_time = datetime.datetime.now() + datetime.timedelta(hours=hours_offset)
    return int(target_time.timestamp())

  @staticmethod
  def get_datetime_string_from_offset(hours_offset:float)->str:
    """
    Returns the current Eastern Time(ET) - EST/EDT - Plus the given offset in hours,
    formatted as 'YYYY-MM-DD HH:MM:SS' for use in ESRI REST API queries.
  
    :param hours_offset: Number of hours to offset from current time (can be negative)
    :return: Formatted datetime string
    """

    # Get UTC time with offset
    utc_time = datetime.datetime.now(timezone.utc) + timedelta(hours=hours_offset)
    # Convert to Eastern Time (EST/EDT)
    eastern_time = utc_time.astimezone(ZoneInfo('America/New_York'))

    return eastern_time.strftime("%Y-%m-%d %H:%M:%S")

  @staticmethod
  def safe_to_int(value: str | int)->int:
    """
    Attempts to convert a string or integer to an integer.

    :param value: A string or integer to convert to integer.
    :return: The integer if successful, or -1 if not.
    """

    try:
      return int(value)
    except (ValueError, TypeError):
      return -1

class restHelper:
  def __init__(self, configs) -> None:
    print("Initializing restHelper")
    if "clientId" in configs:
        self._clientId = configs["clientId"] if configs else None
        self._clientSecret = configs["clientSecret"] if configs else None
        self._scope = configs["scope"] if configs else None
        self._apiUrl = configs["apiUrl"] if configs and "apiUrl" in configs else None
    self._token = None
    self._logger = None
    self._expiration = datetime.datetime.now()
    self._logger = logger

  def callRest(self, url, para = None, httpMode = 'GET', isForm = False, isJson = False, ignoreToken = False, verify=True):
    response = None
    headers = None

    if not ignoreToken:
        headers = {
            "Authorization": "Bearer {}".format(self.getToken()),
            "client_id": self.clientId,
            "Content-type": "application/json"
        }

    if (not isForm and not isJson):
        combinedUrl = ""
        if (para):
            combinedUrl = url + "?" + para
        else:
            combinedUrl = url

        if "secret" in combinedUrl.lower() or "pass" in combinedUrl.lower():
            self.logInfo("") # This line seems to have an empty string argument
        else:
            self.logInfo(combinedUrl)

        if (httpMode == "POST"):
            response = requests.post(combinedUrl, headers=headers, verify=verify)
        else:
            response = requests.get(combinedUrl, headers=headers, verify=verify)

    elif isForm:
        self.logInfo(url)
        if (httpMode == "POST"):
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            if not any("secret" in item or "password" in item for item in para.keys()):
                self.logInfo(para)
            else:
                self.logInfo("Secret token requested")

            response = requests.post(url, headers=headers, data=para, verify=verify)
        else:
            response = requests.get(url, headers=headers, verify=verify)

    elif isJson:
        if (httpMode == "POST"):
            if not any("secret" in item or "password" in item for item in para.keys()):
                self.logInfo(para)
            else:
                self.logInfo("Secret token requested")

            response = requests.post(url, headers=headers, json=para, verify=verify)
        else:
            response = requests.get(url, headers=headers, verify=verify)

    self.logInfo("status code: {0}".format(response.status_code))
    self.logInfo(str(response.content))
    return response

class esriHelper:
  def __init__(self, restHelper:restHelper, configs)-> None:
    self._restHelper = restHelper
    self._configs = configs
    portalUrl = UTILS.getConfigValue(config, "PORTAL_URL")
    portalUser = UTILS.getConfigValue(config, "PORTAL_USER")
    portalPass = UTILS.getConfigValue(config, "PORTAL_PASS")
    baseServiceUrl = UTILS.getConfigValue(config, "BASE_SERVICE_URL")
    versionName = UTILS.getConfigValue(config, "VERSION_NAME")
    versionOwner = UTILS.getConfigValue(config, "VERSION_OWNER")

    self._gis = GIS(url= portalUrl, username= portalUser, password= portalPass)
    self._featureServerUrl = f"{baseServiceUrl}/FeatureServer"
    self._versionUrl = f"{baseServiceUrl}/VersionManagementServer"
    self._unSererUrl = f"{baseServiceUrl}/UtilityNetworkServer"

    self._portalUrl = portalUrl
    self._portalUserName = portalUser
    self._portalPass = portalPass
    self._versionName = versionName
    self._versionOwner = versionOwner
    self._expiration = datetime.datetime.now()
    self._token = None #needed
    self._token = self.generatePortalToken()


  @property
  def token(self):
    """
    Returns valid token of ArcGIS Portal.
    """
    return self.getPortalToken()

  def getPortalToken(self):
    if "session" not in self._gis.__dict__:
      return self.generatePortalToken()

  def generatePortalToken(self):
    """
    Generates the token if its expired, otherwise retuns the existing token.
    """
    currentDate = datetime.datetime.now()
    if self._token != None and self._expiration > currentDate:
      return self._token

    tokenUrl = f"{self._portalUrl}/sharing/rest/generateToken"
    data = {
      "username": self._portalUserName,
      "password": self._portalPass,
      # "client": "requesttip",
      "referer": self._portalUrl,
      "expiration": 60, #in Minutes
      "f": "json"
    }

    result = self._restHelper.callRest(tokenUrl, data, "POST", True, ignoreToken=True)
    jsonObj = result.json()
    self._token = jsonObj["token"]
    self._expiration = datetime.datetime.fromtimestamp(jsonObj["expires"]/1000)

    return self._token


  def query_arcgis_layer_rest_url(self, url:str, token:str, where_clause:str="1=1", outFields:str="*", returnGeometry:bool=False, resultoffset:int=0, batch_size:int=2000 )->[]:
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

  def evaluate_url(self, url:str, params:dict[str, Any]=None):
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
      

  def getDomainValues(self, featureLayer_url:str, subTypeCode:int, fieldName:str)->list:
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

  def getDomainCode(self, featureLayer_url:str, subTypeCode:int, fieldName:str, domainValue:str)->list:
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

  def get_version_guid(self, version_url:str, full_version_name:str, token:str=None)->str:
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

  def purge_lock(self, version_purge_lock_url:str, full_version_name:str, token:str=None)->str:
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

  def create_version(self, versions_url:str, version_name:str, token:str=None)->str:
    create_version_param = {
      "f": "json", 
      "token": get_token()
    }
    response = evaluate_url(versions_url, params=create_version_param)
    versions = response.get("versions", [])

    if any(v["versionName"] == FULL_VERSION_NAME for v in versions):
      raise Exception("Version {FULL_VERSION_NAME} exists")
    else:
      url = f"{versions_url}/create"
      create_version_param = {"f": "json", "versionName": VERSION_NAME, "accessPermission": "public", "token": get_token()}
      response = evaluate_url(url, data=create_version_param)
      if "error" in response.json():
          raise Exception(f"Version creation failed: {response.json()['error']['message']}")
      print(f"Created version: {FULL_VERSION_NAME}")

  # Session management
  def session_action(self, version_guid:str, action:str = stopEditing | None ):
    if version_guid is None:
      raise Exception("version_guid is required.")

    url = f"{VERSION_MGMT_URL}/versions/{version_guid}/{action}"
    params = {"sessionId": SESSION_ID, "token": get_token(), "f": "json"}

    if action == "stopEditing":
        params["saveEdits"] = "true"

    response = evaluate_url(url, data=params)
    if not response.get("success"):
        raise Exception(f"{action} failed: {response.json().get('error', {}).get('message')}")

  # ==========[END] Version Management Related