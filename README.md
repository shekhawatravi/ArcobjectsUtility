# Arcobjects Utilities
Contains frequently used ESRI's Arcobjects Operations. 

## Installation
This is the class library C#.NET project. you can include it as reference in your existing project and start using it.

## Requirements
**For this project, ArcObjects SDK 10.5 is used.** You must have Arcobjects reference .DLLs as mentioned here.

1. ESRI.ArcGIS.DataSourcesGDB
2. ESRI.ArcGIS.Geodatabase
3. ESRI.ArcGIS.Geometry
4. ESRI.ArcGIS.Geoprocessing
5. ESRI.ArcGIS.System

## Examples
1. Create [ISpatialReference](https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#ISpatialReference.htm) using SRID 
  ```cs
  ISpatialReference pSr = ArcobjectsUtilityProject.Utility.GISUtility.Instance.GetSpatialReference_BySrId(4326);
  ```
2. Get [IWorkspace](https://desktop.arcgis.com/en/arcobjects/latest/net/webframe.htm#IWorkspace.htm) using connection file with '.sde' / '.gdb' extension. 
```cs
string conFile = "C://Geodatabase/SampleDatabase.gdb";
IWorkspace pWS = ArcobjectsUtilityProject.Utility.GISUtility.Instance.GetWorkspace(string connectionFile)
```
