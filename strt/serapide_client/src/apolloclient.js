import { ApolloClient } from 'apollo-client'
import { InMemoryCache, IntrospectionFragmentMatcher , defaultDataIdFromObject} from 'apollo-cache-inmemory'
import { onError } from 'apollo-link-error'
import { ApolloLink } from 'apollo-link'
import { createUploadLink, buildAxiosFetch } from './UploadLink'
import { withClientState } from 'apollo-link-state';
import axios from 'axios'
import introspectionQueryResultData from './fragmentTypes.json';

const fragmentMatcher = new IntrospectionFragmentMatcher({
  introspectionQueryResultData
});


const _axios = axios.create({xsrfCookieName: 'csrftoken',xsrfHeaderName: "X-CSRFToken"})
const cache = new InMemoryCache({fragmentMatcher,
        dataIdFromObject: object => {
            console.log(object)
          switch (object.__typename) {
            case 'PianoNode': return object.codice; // use `key` as the primary key
            case 'ProceduraVASNode': return object.uuid;
            case 'RisorsaNode': return object.uuid;
            default: return defaultDataIdFromObject(object); // fall back to default handling
          }
        }
      })

const client = new ApolloClient({
    
    link:  ApolloLink.from([
        onError(({ graphQLErrors, networkError }) => {
            if (graphQLErrors)
                graphQLErrors.map(({ message, locations, path }) =>
                    console.log(
                        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`,
                    ),
                )
            if (networkError) console.log(`[Network error]: ${networkError}`)
      }),
      withClientState({
        defaults: {
            authorities: [
              {value: 0, label: "Commisione del paesaggio integrata", __typename: 'Authority'},
              {value: 1, label: "Città Metropolitana di Firenze",__typename: 'Authority'},
              {value: 2, label: "Nucleo VIA-VAS",__typename: 'Authority'},
              {value: 3, label: "Settore Ambiente",__typename: 'Authority'}
            ]},
            resolvers: {},
            typeDefs: `
                type Authority {
                    value: Int!
                    label: String!
                }
                type Query {
                    visibilityFilter: String
                    authorities: [Authority]
                }`,
            cache }),
    createUploadLink({
            uri: "/serapide/graphql",
            credentials: 'same-origin',
            fetch: buildAxiosFetch(_axios)
    })]),
    cache
  });

export default client