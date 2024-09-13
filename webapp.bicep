@description('Describes plan\'s pricing tier and instance size. Check details at https://azure.microsoft.com/en-us/pricing/details/app-service/')
@allowed([
  'F1'
])
param skuName string = 'F1'

@description('Describes plan\'s instance count')
@minValue(1)
@maxValue(3)
param skuCapacity int = 1
var hostingPlanName = 'ASP${uniqueString(resourceGroup().id)}'
var websiteName = 'WebApp${uniqueString(resourceGroup().id)}'

param sqlServer string
param sqlDatabase string
param storageAccountName string

resource hostingPlan 'Microsoft.Web/serverfarms@2020-12-01' = {
  name: hostingPlanName
  location: resourceGroup().location
  kind: 'linux'
  properties: {
    reserved: true
  }
  sku: {
    name: skuName
    capacity: skuCapacity
  }
}

resource website 'Microsoft.Web/sites@2020-12-01' = {
  name: websiteName
  location: resourceGroup().location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      linuxFxVersion: 'python|3.11'
      pythonVersion: '3.11'
      appCommandLine: 'gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app'
    }
  }
}

resource webSiteConnectionStrings 'Microsoft.Web/sites/config@2020-12-01' = {
  parent: website
  name: 'connectionstrings'
  properties: {
    DefaultConnection: {
      value: 'Data Source=tcp:${sqlServer}.database.windows.net,1433;Initial Catalog=${sqlDatabase};Authentication=Active Directory Default;TrustServerCertificate=True;'
      type: 'SQLAzure'
    }
    AZURE_SQL_CONNECTIONSTRING:{
      type: 'Custom'
      value: 'Driver={ODBC Driver 18 for SQL Server};${sqlServer}.database.windows.net,1433;Initial Catalog=${sqlDatabase};;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30'
    }
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' existing = {
  name: storageAccountName
}

param baseTime string = utcNow('u')
var sasToken = storageAccount.listServiceSAS('2021-04-01', {
  canonicalizedResource: '/blob/${storageAccount.name}/webapplogs'
  signedResource: 'c'
  signedProtocol: 'https'
  signedPermission: 'rwl'
  signedServices: 'b'
  signedExpiry: dateTimeAdd(baseTime, 'P3D') // Create token to last 3 days
}).serviceSasToken

resource webLogs 'Microsoft.Web/sites/config@2022-09-01' = {
  name: 'logs'
  parent: website
  properties: {
    applicationLogs: {
      azureBlobStorage: {
        level: 'Verbose'
        retentionInDays: 2
        sasUrl: 'https://${storageAccount.name}.blob.${environment().suffixes.storage}/${sasToken}'
      }
    }
    detailedErrorMessages: {
      enabled: true
    }
  }
}

output webSiteName string = website.name
