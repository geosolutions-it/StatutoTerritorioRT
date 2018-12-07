import ApolloClient from 'apollo-boost'

const client = new ApolloClient({
    uri: "https://dqw5rxqivbdgpewjzoea4hqbmm.appsync-api.eu-west-1.amazonaws.com/graphql",
    headers: {"x-api-key": "da2-mkj36zvpovgrfgcjxtestrmtvi"}
})

export default client