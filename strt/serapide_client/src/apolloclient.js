import { ApolloClient } from 'apollo-client'
import { InMemoryCache, IntrospectionFragmentMatcher } from 'apollo-cache-inmemory'
import { onError } from 'apollo-link-error'
import { ApolloLink } from 'apollo-link'
import { createUploadLink, buildAxiosFetch } from './UploadLink'
import axios from 'axios'
import introspectionQueryResultData from './fragmentTypes.json';

const fragmentMatcher = new IntrospectionFragmentMatcher({
  introspectionQueryResultData
});




const _axios = axios.create({xsrfCookieName: 'csrftoken',xsrfHeaderName: "X-CSRFToken"})


const client = new ApolloClient({
    cache: new InMemoryCache({fragmentMatcher}),
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
    createUploadLink({
            uri: "/serapide/graphql",
            credentials: 'same-origin',
            fetch: buildAxiosFetch(_axios)
    })])
  });

export default client