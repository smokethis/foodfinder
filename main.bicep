metadata description = 'Creates a web app and SQL server, then assigns some rights to allow passwordless authentication for the web app'

targetScope = 'subscription'
param resourceGroupName string
param resourceGroupLocation string = 'uksouth'

resource newRG 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: resourceGroupLocation
}

module cosmos 'cosmos.bicep' = {
  name: 'cosmosDb'
  scope: newRG
  params: {
    databaseName: 'foodFinder'
    containerName: 'testContainer'
  }
}
