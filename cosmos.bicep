@description('Cosmos DB account name')
param accountName string = 'cosmos-${uniqueString(resourceGroup().id)}'

@description('Location for the Cosmos DB account.')
param location string = resourceGroup().location

resource account 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
  name: toLower(accountName)
  location: location
  properties: {
    capabilities: [
      {
        name: 'EnableGremlin'
      }
    ]
    enableFreeTier: true
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
      }
    ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/gremlinDatabases@2024-05-15' = {
  name: 'mealdb'
  parent: account
  properties: {
    resource: {
      id: 'mealdb'
    }
  }
}

resource symbolicname 'Microsoft.DocumentDB/databaseAccounts/gremlinDatabases/graphs@2024-05-15' = {
  name: 'foods'
  parent: database
  properties: {
    resource: {
      id: 'foods'
      partitionKey: {
        kind: 'Hash'
        paths: [
          '/type'
        ]
        version: 2
      }
    }
  }
}
