using ESRI.ArcGIS.DataSourcesGDB;
using ESRI.ArcGIS.esriSystem;
using ESRI.ArcGIS.Geodatabase;
using ESRI.ArcGIS.Geometry;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ArcobjectsUtilityProject.Utility
{
    /// <summary>
    /// Singleton class for Utility methods using ESRI's Arcobjects API
    /// </summary>
    public class GISUtility
    {
        private static GISUtility instance = null;
        private static readonly object padlock = new object();

        public static readonly string SDE_FILE_EXT = ".sde";
        public static readonly string GDB_FILE_EXT = ".gdb";

        private GISUtility()
        {

        }

        /// <summary>
        /// Creates singleton class object of <see cref="GISUtility"/>
        /// </summary>
        public static GISUtility Instance
        {
            get
            {
                lock (padlock)
                {
                    if (instance == null)
                    {
                        instance = new GISUtility();
                    }
                    return instance;
                }
            }
        }

        /// <summary>
        /// Returns an <see cref="IFeatureCursor"/> that can be used to fetch feature Objects selected by the specified by spatial query. 
        /// </summary>
        /// <param name="featureClass"></param>
        /// <param name="filterGeometry"></param>
        /// <param name="spatialRelation"></param>
        /// <param name="outFieldsArray"></param>
        /// <param name="whereClause"></param>
        /// <returns></returns>
        public IFeatureCursor SearchIn(IFeatureClass featureClass, IGeometry filterGeometry, esriSpatialRelEnum spatialRelation, string[] outFieldsArray, string whereClause, bool isRecyclable)
        {
            IFeatureCursor pFCursor = null;
            try
            {
                if (featureClass == null || filterGeometry == null || outFieldsArray == null || whereClause == null)
                {
                    throw new Exception("Invalid Parameters for Spatial Filter Search.");
                }
                else
                {
                    SpatialFilterClass pSFilter = new SpatialFilterClass();
                    pSFilter.SubFields = String.Join(",", outFieldsArray);
                    pSFilter.WhereClause = whereClause;
                    pSFilter.Geometry = filterGeometry;
                    pSFilter.SpatialRel = spatialRelation;
                    /// NOTE:: Passing isRecyclable as false, will not recycle memory when looping through Featurecursor, you shall be able to compare two features
                    pFCursor = featureClass.Search(pSFilter, isRecyclable);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine(String.Format("Exception while doing spatial filter in Feature Class:: {0}", ex.StackTrace));
                throw ex;
            }
            finally
            {
            }
            return pFCursor;
        }

        /// <summary>
        /// Returns an Object Cursor that can be used to fetch feature Objects selected by the specified non-spatial query
        /// </summary>
        /// <param name="featureClass"></param>
        /// <param name="outFieldsArray"></param>
        /// <param name="whereClause"></param>
        /// <returns></returns>
        public IFeatureCursor SearchIn(IFeatureClass featureClass, string[] outFieldsArray, string whereClause, bool isRecyclable, bool isReturnGeom)
        {
            IFeatureCursor pFCursor = null;
            try
            {
                if (featureClass == null || outFieldsArray == null || whereClause == null)
                {
                    throw new Exception("Invalid Parameters for Query Filter Search.");
                }
                else
                {
                    IQueryFilter pQFilter = new QueryFilterClass();
                    pQFilter.SubFields = String.Join(",", outFieldsArray);
                    pQFilter.WhereClause = whereClause;
                    if (isReturnGeom)
                        pQFilter.AddField("Shape"); // Adding this field, to make sure that, it returns Geometry of the Resultant Feature as well.
                    pFCursor = featureClass.Search(pQFilter, isRecyclable);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine(String.Format("Exception while doing query filter in Feature Class:: {0}", ex.StackTrace));
                throw ex;
            }
            finally
            {
            }
            return pFCursor;
        }

        /// <summary>
        /// The number of featurs selected by the specified spatial query.
        /// </summary>
        /// <param name="featureClass"></param>
        /// <param name="filterGeometry"></param>
        /// <param name="spatialRelation"></param>
        /// <param name="outFieldsArray"></param>
        /// <param name="whereClause"></param>
        /// <returns></returns>
        public int FeatureCountIn(IFeatureClass featureClass, IGeometry filterGeometry, esriSpatialRelEnum spatialRelation, string[] outFieldsArray, string whereClause)
        {
            int featureCount = 0;
            try
            {
                if (featureClass == null || filterGeometry == null || outFieldsArray == null || whereClause == null)
                {
                    throw new Exception("Invalid Parameters for Spatial Filter Search.");
                }
                else
                {
                    SpatialFilterClass pSFilter = new SpatialFilterClass();
                    pSFilter.SubFields = String.Join(",", outFieldsArray);
                    pSFilter.WhereClause = whereClause;
                    pSFilter.Geometry = filterGeometry;
                    pSFilter.SpatialRel = spatialRelation;
                    featureCount = featureClass.FeatureCount(pSFilter);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine(String.Format("Exception while calculating Feature Count in the Spatial query:: {0}", ex.StackTrace));
                throw ex;
            }
            finally
            {
            }
            return featureCount;
        }

        /// <summary>
        /// The number of featurs selected by the specified non-spatial query.
        /// </summary>
        /// <param name="featureClass"></param>
        /// <param name="outFieldsArray"></param>
        /// <param name="whereClause"></param>
        /// <returns></returns>
        public int FeatureCountIn(IFeatureClass featureClass, string[] outFieldsArray, string whereClause)
        {
            int featureCount = 0;
            try
            {
                if (featureClass == null || outFieldsArray == null || whereClause == null)
                {
                    throw new Exception("Invalid Parameters for Filter Search.");
                }
                else
                {
                    QueryFilterClass pQFilter = new QueryFilterClass();
                    pQFilter.SubFields = String.Join(",", outFieldsArray);
                    pQFilter.WhereClause = whereClause;
                    featureCount = featureClass.FeatureCount(pQFilter);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine(String.Format("Exception while calculating Feature Count in the Spatial query:: {0}", ex.StackTrace));
                throw ex;
            }
            finally
            {
            }
            return featureCount;
        }

        /// <summary>
        /// Returns the Name of the SubType in a <see cref="IFeatureClass"/> of a particular <see cref="IFeature"/>, if available.
        /// </summary>
        /// <param name="pFeatClass"></param>
        /// <param name="pFeat"></param>
        /// <returns></returns>
        public string GetSubTypeName(IFeatureClass pFeatClass, IFeature pFeat)
        {
            string subTypeName = "";

            //cast for the ISubtypes interface
            ISubtypes subtypes = (ISubtypes)pFeatClass;
            if (subtypes == null)
            {
                return "";
            }
            else
            {
                if (!subtypes.HasSubtype)// does the feature class have subtypes?
                {
                    return "";
                }
                else
                {
                    string subTypFldName = subtypes.SubtypeFieldName;
                    int fieldPositionObjId = pFeatClass.FindField(subTypFldName);
                    object fieldValue = pFeat.get_Value(fieldPositionObjId);
                    int subTypeValue = -1;

                    if (fieldValue == null || fieldValue.GetType() == typeof(DBNull))
                    {
                        subTypeValue = -1;
                    }
                    else
                    {
                        subTypeValue = Convert.ToInt16(fieldValue);
                    }

                    IEnumSubtype pEnumSubType = subtypes.Subtypes;
                    pEnumSubType.Reset();
                    int subTypeCode = -1;
                    string subTypeNm = pEnumSubType.Next(out subTypeCode);

                    while (subTypeNm != null)
                    {
                        if (subTypeCode == subTypeValue)
                        {
                            subTypeName = subTypeNm;
                            break;
                        }
                        subTypeNm = pEnumSubType.Next(out subTypeCode);
                    }
                }
            }

            return subTypeName;
        }

        /// <summary>
        /// Returns the code of the subtype in a <see cref="IFeatureClass"/> of a particular <see cref="IFeature"/>, if available
        /// </summary>
        /// <param name="pFeatClass"></param>
        /// <param name="pFeat"></param>
        /// <returns></returns>
        public int GetSubTypeCode(IFeatureClass pFeatClass, IFeature pFeat)
        {
            int subTypeCode = -1;

            //cast for the ISubtypes interface
            ISubtypes subtypes = (ISubtypes)pFeatClass;
            if (subtypes == null)
            {
                return subTypeCode;
            }
            else
            {
                if (!subtypes.HasSubtype)// does the feature class have subtypes?
                {
                    return subTypeCode;
                }
                else
                {
                    string subTypFldName = subtypes.SubtypeFieldName;
                    int fieldPositionindex = pFeatClass.FindField(subTypFldName);
                    object fieldValue = pFeat.get_Value(fieldPositionindex);

                    if (fieldValue == null || fieldValue.GetType() == typeof(DBNull))
                    {
                        subTypeCode = -1;
                    }
                    else
                    {
                        subTypeCode = Convert.ToInt16(fieldValue);
                    }
                }
            }
            return subTypeCode;
        }

        /// <summary>
        /// Returns the <see cref="IDomain"/> of a field in a <see cref="IFeatureClass"/>, based on the provided subtypecode
        /// </summary>
        /// <param name="pFeatClass"></param>
        /// <param name="subTypeCode"></param>
        /// <param name="fieldName"></param>
        /// <returns></returns>
        public IDomain GetDomainOfAField(IFeatureClass pFeatClass, int subTypeCode, string fieldName)
        {
            IDomain domain = null;
            //cast for the ISubtypes interface
            ISubtypes subtypes = (ISubtypes)pFeatClass;
            if (subtypes == null)
            {
                return null;
            }
            else
            {
                if (!subtypes.HasSubtype)// does the feature class have subtypes?
                {
                    return null;
                }
                else
                {
                    domain = subtypes.Domain[subTypeCode, fieldName];
                }
            }
            return domain;
        }

        /// <summary>
        /// Get the <see cref="IDomain"/> of a field in a <see cref="IFeatureClass"/>, based on the provided subtypecode and <see cref="IField"/>
        /// </summary>
        /// <param name="pFeatClass"></param>
        /// <param name="subTypeCode"></param>
        /// <param name="field"></param>
        /// <returns></returns>
        public IDomain GetDomainOfAField(IFeatureClass pFeatClass, int subTypeCode, IField field)
        {
            IDomain domain = null;
            //cast for the ISubtypes interface
            ISubtypes subtypes = (ISubtypes)pFeatClass;
            if (subtypes == null)
            {
                return null;
            }
            else
            {
                if (!subtypes.HasSubtype)// does the feature class have subtypes?
                {
                    domain = field.Domain;
                }
                else
                {
                    domain = subtypes.Domain[subTypeCode, field.Name];
                }
            }
            return domain;
        }

        /// <summary>
        /// Returns the field's value: It checks for followings.
        /// <list type="number">
        ///     <item>
        ///         <term>SubType: </term>
        ///         <description>If the field has a <see cref="ISubtypes"/> associated with it, it will return name/description correpsonding to subtype.</description>
        ///     </item>
        ///     <item>
        ///         <term>Domain: </term>
        ///         <description>If the field has a coded value <see cref="IDomain"/> associated with it, it will return domain's name/description based on the field value.</description>
        ///     </item>
        ///     <item>
        ///         <term>Field Value: </term>
        ///         <description>If the field has neither a <see cref="ISubtypes"/> nor <see cref="IDomain"/> associated with it, it will return field value itself as <see cref="object"/> type, it might be null as well.</description>
        ///     </item>
        /// </list>
        /// </summary>
        /// <param name="pFeature"></param>
        /// <param name="fieldIndex"></param>
        /// <returns><see cref="object"/></returns>
        public object ReadFieldValue(IFeature pFeature, int fieldIndex)
        {
            object fieldValue = null;

            if (pFeature != null && fieldIndex > -1)
            {
                fieldValue = pFeature.Value[fieldIndex]; // Default Value, overrite if SubType or Domain is found on this field.

                if (fieldValue != DBNull.Value)
                {
                    ISubtypes subtypes = pFeature.Class as ISubtypes;
                    IRowSubtypes rowSubtypes = pFeature as IRowSubtypes;
                    IField2 field = pFeature.Fields.Field[fieldIndex] as IField2;

                    // Set the appropriate domain based on the subtype if a subtype exists.
                    IDomain domain = null;
                    if (field != null)
                    {
                        if (subtypes != null && subtypes.SubtypeFieldIndex > -1)
                        {
                            try
                            {
                                domain = subtypes.get_Domain(rowSubtypes.SubtypeCode, field.Name);
                            }
                            catch (Exception e)
                            {
                                Debug.WriteLine(e.Message, e);
                                domain = field.Domain;
                            }
                        }
                        else
                        {
                            domain = field.Domain;
                        }
                    }

                    // Check for a subtype field first
                    if (subtypes != null && rowSubtypes != null && subtypes.SubtypeFieldIndex == fieldIndex)
                    {
                        try
                        {
                            fieldValue = subtypes.get_SubtypeName(rowSubtypes.SubtypeCode);
                        }
                        catch (Exception ex)
                        {
                            fieldValue = null;
                            Debug.WriteLine("Error occured while getting subtypeName.", ex);
                        }
                    }
                    // If it is not a subtype field, check for a domain field
                    else if (domain != null)
                    {
                        if (domain.Type == esriDomainType.esriDTCodedValue)
                        {
                            ICodedValueDomain2 cvDomain = domain as ICodedValueDomain2;
                            if (cvDomain != null)
                            {
                                for (int i = 0; i < cvDomain.CodeCount; i++)
                                {
                                    if (cvDomain.get_Value(i).Equals(fieldValue))
                                    {
                                        fieldValue = cvDomain.get_Name(i);
                                        break;
                                    }
                                }
                            }
                        }
                        else if (domain.Type == esriDomainType.esriDTRange)
                        {

                        }
                        else if (domain.Type == esriDomainType.esriDTString)
                        {

                        }
                    }
                }
                else
                {
                    return null;
                }
            }

            return fieldValue;
        }

        /// <summary>
        /// Returns the field's value as <see cref="string"/>: It checks for followings.
        /// <list type="number">
        ///     <item>
        ///         <term>SubType: </term>
        ///         <description>If the field has a <see cref="ISubtypes"/> associated with it, it will return name/description correpsonding to subtype.</description>
        ///     </item>
        ///     <item>
        ///         <term>Domain: </term>
        ///         <description>If the field has a coded value <see cref="IDomain"/> associated with it, it will return domain's name/description based on the field value.</description>
        ///     </item>
        ///     <item>
        ///         <term>Field Value: </term>
        ///         <description>If the field has neither a <see cref="ISubtypes"/> nor <see cref="IDomain"/> associated with it, it will return field value itself as <see cref="object"/> type, it might be null as well.</description>
        ///     </item>
        /// </list>
        /// </summary>
        /// <param name="pFeature"></param>
        /// <param name="fieldIndex"></param>
        /// <returns><see cref="object"/></returns>
        public string ReadFieldValueAsString(IFeature pFeature, int fieldIndex)
        {
            string fldValue = "";
            object fldObjValue = ReadFieldValue(pFeature, fieldIndex);
            if (fldObjValue != null)
            {
                if (fldObjValue.GetType() == typeof(int) ||
                    fldObjValue.GetType() == typeof(short) ||
                    fldObjValue.GetType() == typeof(long) ||
                    fldObjValue.GetType() == typeof(double) ||
                    fldObjValue.GetType() == typeof(float) ||
                    fldObjValue.GetType() == typeof(string) ||
                    fldObjValue.GetType() == typeof(DateTime))
                {
                    fldValue = fldObjValue.ToString();
                }
                else
                {
                    Debug.WriteLine("Field Value is other than primitive data types: " + fldObjValue);
                }
            }
            return fldValue;
        }

        /// <summary>
        /// Returns the <see cref="ISpatialReference"/> based on provided Spatial Reference Id as <see cref="int" />
        /// </summary>
        /// <param name="srId"></param>
        /// <returns></returns>
        public ISpatialReference GetSpatialReference_BySrId(int srId)
        {
            ISpatialReference spatialReference = null;
            ISpatialReferenceFactory sr_factory = new SpatialReferenceEnvironment();
            try
            {
                spatialReference = sr_factory.CreateGeographicCoordinateSystem(srId);
            }
            catch
            {
                try
                {
                    spatialReference = sr_factory.CreateProjectedCoordinateSystem(srId);
                }
                catch (Exception e)
                {
                    Debug.WriteLine(e);
                    string msg = String.Format("srId '{0}' is an unkown Spatial Reference", srId);
                    throw new Exception(msg);
                }
            }

            return spatialReference;
        }

        /// <summary>
        /// Returns <see cref="IPolygon"/> based on the input <see cref="IEnvelope"/>
        /// </summary>
        /// <param name="pEnv"></param>
        /// <returns></returns>
        public IPolygon GetPolygonFromEnvelop(IEnvelope pEnv)
        {
            IPolygon polygon = new PolygonClass();

            ISegmentCollection pSegCol = polygon as ISegmentCollection;
            pSegCol.SetRectangle(pEnv);

            return polygon;
        }

        /// <summary>
        /// Return the Non <see cref="null"/> <see cref="IGeometry"/> based on the provided <see cref="IFeatureClass"/> 
        /// and <see cref="IFeature"/>. FYR: Some times, <see cref="IFeature"/> has geometry but it's null,
        /// so this creates default empty <see cref="IGeometry"/> type.
        /// </summary>
        /// <param name="featureClass"></param>
        /// <param name="feature"></param>
        /// <returns></returns>
        public IGeometry GetNonNullGeometry(IFeatureClass featureClass, IFeature feature)
        {
            IGeometry pGeom = null;
            if (feature.Shape != null)
            {
                pGeom = feature.ShapeCopy;
            }
            else
            {
                switch (featureClass.ShapeType)
                {
                    case esriGeometryType.esriGeometryPoint:
                        pGeom = new PointClass();
                        break;
                    case esriGeometryType.esriGeometryPolyline:
                        pGeom = new PolylineClass();
                        break;
                    case esriGeometryType.esriGeometryPolygon:
                        pGeom = new PolygonClass();
                        break;
                }
            }
            return pGeom;
        }

        /// <summary>
        /// Returns <see cref="IWorkspace"/>,based on input connection file.This connection file can be either .SDE or .GDB
        /// </summary>
        /// <param name="connectionFile"> This connection file can be either .SDE or .GDB</param>
        public IWorkspace GetWorkspace(string connectionFile)
        {
            IWorkspaceFactory pWSF = null;
            if (isValidConnectionFile(connectionFile))
            {
                if (connectionFile.EndsWith(Constants.SDE_FILE_EXT))
                {
                    pWSF = new SdeWorkspaceFactory();
                }
                else if (connectionFile.EndsWith(Constants.GDB_FILE_EXT))
                {
                    pWSF = new FileGDBWorkspaceFactoryClass();
                }
            }

            if (pWSF == null)
            {
                string msg = String.Format("Problem while creating Workspace using '{0}' connection file.", connectionFile);
                throw new Exception(msg);
            }

            IWorkspace pWS = (pWSF != null) ? pWSF.OpenFromFile(connectionFile, 0) : null;
            return pWS;
        }

        /// <summary>
        /// Check for valid file extension of connection file. i.e. .sde/.gdb
        /// </summary>
        /// <param name="connectionFile"></param>
        /// <returns></returns>
        public bool isValidConnectionFile(string connectionFile)
        {
            // Check for valid file extension of connection file.
            string extension = System.IO.Path.GetExtension(connectionFile);
            if (!(extension.Equals(Constants.GDB_FILE_EXT, StringComparison.OrdinalIgnoreCase) || extension.Equals(Constants.SDE_FILE_EXT, StringComparison.OrdinalIgnoreCase)))
            {
                string msg = String.Format("Connection file extension is not valid. It should be either '.sde' or '.gdb'.", connectionFile);
                throw new Exception(msg);
            }

            // check if file really exists on disk or not.
            if (extension.Equals(Constants.SDE_FILE_EXT, StringComparison.OrdinalIgnoreCase))
            {
                if (!System.IO.File.Exists(connectionFile))
                {
                    string msg = String.Format("SDE Connection file does not exists at '{0}', Please make sure it exits at specified path.", connectionFile);
                    throw new Exception(msg);
                }
            }
            else if (extension.Equals(Constants.GDB_FILE_EXT, StringComparison.OrdinalIgnoreCase))
            {
                if (!System.IO.Directory.Exists(System.IO.Path.GetFullPath(connectionFile)))
                {
                    string msg = String.Format("File Geodatabase Connection file does not exists at '{0}', Please make sure it exits at specified path.", connectionFile);
                    throw new Exception(msg);
                }
            }


            return true;
        }

        /// <summary>
        /// Open <see cref="IWorkspace"/> if exists, other wise create a new at the spcified Path with specified name.
        /// Input Path- as Directory upto the folder. Inpput fileGdbName- Geodatabase name without .gdb extension
        /// </summary>
        /// <param name="path"> This is the Directory upto the folder</param>
        /// <param name="fileGdbName"> Geodatabase name without .gdb extension</param>
        /// <returns>IWorkspace</returns>
        public IWorkspace GetFileGdbWorkspaceOrCreate(string path, string fileGdbName)
        {
            IWorkspace workspace = null;
            if (!System.IO.Directory.Exists(System.IO.Path.Combine(path, fileGdbName + ".gdb")))
            {
                if (!System.IO.Directory.Exists(System.IO.Path.GetFullPath(path)))
                { // When Parent directory does not exist, then create the directory structure.
                    System.IO.Directory.CreateDirectory(path);
                }
                IWorkspaceFactory pFWSFactory = new FileGDBWorkspaceFactoryClass();
                IWorkspaceName pWSName = pFWSFactory.Create(path, fileGdbName, null, 0);

                // Cast the workspace name object to the IName interface and open the workspace.
                IName name = (IName)pWSName;
                workspace = (IWorkspace)name.Open();
            }
            else
            {
                workspace = GetWorkspace(System.IO.Path.Combine(path, fileGdbName + Constants.GDB_FILE_EXT));
            }
            return workspace;
        }
        
        /// <summary>
        /// Get the <see cref="List<int>"/> of Object Ids from <see cref="IFeatureCursor"/>. it can be used to avoid the duplicate in the returned <see cref="List<int>"/>.
        /// </summary>
        /// <param name="pFeatCursor"><see cref="IFeatureCursor"/></param>
        /// <param name="list"><see cref="List<int>"/></param>
        /// <param name="isAvoidDuplicate"><see cref="Boolean"/></param>
        /// <returns><see cref="List<int>"/></returns>
        public List<int> GetOnlyObjectIdsAsList(IFeatureCursor pFeatCursor, List<int> list, Boolean isAvoidDuplicate)
        {
            if (list == null)
                list = new List<int>();

            if (pFeatCursor != null)
            {
                IFeature pFeature = pFeatCursor.NextFeature();
                while (pFeature != null)
                {
                    if (isAvoidDuplicate)
                    { // Dont's add duplicate in list
                        if (!list.Contains(pFeature.OID))
                            list.Add(pFeature.OID);
                    }
                    else // duplicates can be added
                        list.Add(pFeature.OID);

                    pFeature = pFeatCursor.NextFeature();
                }
            }
            return list;
        }
        
        /// <summary>
        /// Get the <see cref="List<int>"/> of Object Ids from <see cref="IEnumIDs"/>.
        /// </summary>
        /// <param name="enumIds"></param>
        /// <returns></returns>
        public List<int> GetObjectIdsAsList(IEnumIDs enumIds)
        {
            List<int> outIds = new List<int>();

            if(enumIds != null)
            {
                int idOne = enumIds.Next();
                while(idOne != -1)
                {
                    outIds.Add(idOne);

                    idOne = enumIds.Next();
                }
            }

            return outIds;
        }
        
        /// <summary>
        /// Get the subtype field Name as <see cref="string"/>, if exists from a <see cref="IFeatureClass"/>.
        /// </summary>
        /// <param name="pFeatureClass"></param>
        /// <returns><see cref="List<int>"/></returns>
        public string GetSubTypeFieldName(IFeatureClass pFeatureClass)
        {
            string subTypeFieldName = "";
            ISubtypes subtypes = (ISubtypes)pFeatureClass;
            if (subtypes == null)
            {
                subTypeFieldName = "";
            }
            else
            {
                if (!subtypes.HasSubtype)// does the feature class have subtypes?
                {
                    subTypeFieldName = "";
                }
                else
                {
                    subTypeFieldName = subtypes.SubtypeFieldName;
                }
            }
            return subTypeFieldName;
        }
        
        /// <summary>
        /// Get the linked Geometry of a Flowlines. It compares start and end points of each line segment, if they are equals, then they both line segments belongs to the same flowline. The Last argument.
        /// </summary>
        /// <param name="dic_orig_feats"> Dictionary of Original Feature Geometries. In this dictionary, key denotes ObjectId of the Feature, and Value denotes <see cref="IGeometry"/>. </param>
        /// <param name="dic_base_geom">Base Geometry, one of the geometry to compare.</param>
        /// <param name="first_avoid">List of ObjectIds to avoid to compare.</param>
        /// <param name="first_rslt"> List of connected ObjectIds found. These all ObjectIds compose one Flowline. </param>
        private void GetLinkedGeometry(IDictionary<int, IGeometry> dic_orig_feats, KeyValuePair<int, IGeometry> dic_base_geom, List<int> first_avoid, List<int> first_rslt)
        {
            // TODO: Commented Temporarily- AttributeConsistency rule needs to be modified to optimize the way of finding connected flowlines.
            if (dic_orig_feats != null && dic_base_geom.Value != null && first_avoid.Count >= 0)
            {
                foreach (var item in dic_orig_feats)
                {
                    if (!first_avoid.Contains(item.Key) && item.Key != dic_base_geom.Key) // Avoid processing similar geometry
                    {
                        IPoint base_Frst_Pnt = ((IPolyline)dic_base_geom.Value).FromPoint;
                        IPoint base_Last_Pnt = ((IPolyline)dic_base_geom.Value).ToPoint;

                        IPoint compare_Frst_Pnt = ((IPolyline)item.Value).FromPoint;
                        IPoint compare_Last_Pnt = ((IPolyline)item.Value).ToPoint;

                        // Check if there is any intersection connection between these two point geometries
                        IRelationalOperator pRelOper_Base_Frst_Pnt = base_Frst_Pnt as IRelationalOperator;
                        IRelationalOperator pRelOper_Base_Last_Pnt = base_Last_Pnt as IRelationalOperator;
                        if (pRelOper_Base_Last_Pnt.Crosses(compare_Frst_Pnt) || pRelOper_Base_Last_Pnt.Crosses(compare_Last_Pnt) ||
                            pRelOper_Base_Frst_Pnt.Crosses(compare_Frst_Pnt) || pRelOper_Base_Frst_Pnt.Crosses(compare_Last_Pnt))
                            continue;

                        if (pRelOper_Base_Last_Pnt.Equals(compare_Frst_Pnt) || pRelOper_Base_Last_Pnt.Equals(compare_Last_Pnt) ||
                           pRelOper_Base_Frst_Pnt.Equals(compare_Frst_Pnt) || pRelOper_Base_Frst_Pnt.Equals(compare_Last_Pnt))
                        {
                            if (!first_rslt.Contains(item.Key))
                                first_rslt.Add(item.Key); // Adding found line segment's ObjectId(key) as part of a flowline.

                            first_rslt.Add(dic_base_geom.Key); // Adding base geometry's line segment's ObjectId(key) as part of a flowline.

                            first_avoid.Add(item.Key);
                            GetLinkedGeometry(dic_orig_feats, new KeyValuePair<int, IGeometry>(item.Key, item.Value), first_avoid, first_rslt);
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Get the List of Linked <see cref="IFeature"/>, which is of type <see cref="IPolyline"/>, from the <see cref="IFeatureCursor"/>
        /// </summary>
        /// <param name="dic_base_geom">Base Geometry, one of the geometry to compare.</param>
        /// <returns><see cref="List<Dictionary<int, IFeature>>"/></returns>
        public List<Dictionary<int, IFeature>> GetLinkedFeaturesFromFeatureCursor(IFeatureCursor pFCursor)
        {
            // TODO: Commented Temporarily- AttributeConsistency rule needs to be modified to optimize the way of finding connected flowlines.
            List<Dictionary<int, IFeature>> _flowlinesFound = new List<Dictionary<int, IFeature>>(); // holds multiple flowlines

            Dictionary<int, IFeature> dic_orig_IFeats = new Dictionary<int, IFeature>();
            Dictionary<int, IGeometry> dic_orig_IGeoms = new Dictionary<int, IGeometry>();

            if (pFCursor != null)
            {
                IFeature pFeat = pFCursor.NextFeature();
                while (pFeat != null)
                {
                    dic_orig_IFeats.Add(pFeat.OID, pFeat);
                    dic_orig_IGeoms.Add(pFeat.OID, pFeat.ShapeCopy);
                    pFeat = pFCursor.NextFeature();
                }
            }

            Log.Debug($"Finding related Segments to be merged. from '{dic_orig_IGeoms.Count}' flowline segments.");
            if (dic_orig_IGeoms.Count > 0 && dic_orig_IFeats.Count > 0)
            {
                List<int> first_avoid = new List<int>();
                foreach (int key in dic_orig_IGeoms.Keys)
                {
                    first_avoid.Add(key);
                    List<int> first_rslt = new List<int>(); // holds ObjectIds(keys) of line segments which are part of a particular flowline.
                    Dictionary<int, IFeature> first_rslt_IFeat = new Dictionary<int, IFeature>(); // holds ObjectIds(keys) and IFeature of line segments which are part of a particular flowline.
                    IGeometry pGeomOut = null;
                    dic_orig_IGeoms.TryGetValue(key, out pGeomOut);
                    GetLinkedGeometry(dic_orig_IGeoms, new KeyValuePair<int, IGeometry>(key, pGeomOut), first_avoid, first_rslt);

                    if (first_rslt.Count > 0)
                    {
                        _flowlinesFound.Add(first_rslt_IFeat);
                        KeyValuePair<int, IFeature>[] temp = (from kv in dic_orig_IFeats where first_rslt.Contains(kv.Key) select kv).ToArray();
                        foreach (var t in temp)
                        {
                            first_rslt_IFeat.Add(t.Key, t.Value);
                        }
                    }
                }
            }

            Debug.WriteLine($"Total Flowlines found = {_flowlinesFound.Count} ");
            return _flowlinesFound;
        }
    }
}
