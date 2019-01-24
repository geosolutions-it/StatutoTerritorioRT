/**
 *  Original code from https://github.com/jaydenseric/apollo-upload-client/
 *  and https://github.com/lifeomic/axios-fetch
 * 
 */
import { ApolloLink, Observable } from 'apollo-link'
import {
  selectURI,
  selectHttpOptionsAndBody,
  fallbackHttpConfig,
  serializeFetchParameter,
  createSignalIfSupported,
  parseAndCheckHttpResponse
} from 'apollo-link-http-common'
import { extractFiles} from 'extract-files'
import axios from 'axios'
import { Response, Headers } from 'node-fetch'
import mapKeys from 'lodash/mapKeys'

/**
 * A Fetch WebAPI implementation based on the Axios client
 */
async function axiosFetch (axios, input, init = {}) {
  // Convert the `fetch` style arguments into a Axios style config

  const lowerCasedHeaders = mapKeys(init.headers, function (value, key) {
    return key.toLowerCase();
  });
  if (!('content-type' in lowerCasedHeaders)) {
    lowerCasedHeaders['content-type'] = 'text/plain;charset=UTF-8';
  }else if(init.body instanceof FormData) {
    lowerCasedHeaders['content-type'] = 'multipart/form-data';
  }

  const config = {
    url: input,
    method: init.method || 'GET',
    data: init.body instanceof FormData ? init.body : String(init.body),
    headers: lowerCasedHeaders,
    validateStatus: () => true,
    onUploadProgress: init.uploadProgres
    
  };

  const result = await axios.request(config);
 
  // Convert the Axios style response into a `fetch` style response
  const responseBody = typeof result.data === `object` ? JSON.stringify(result.data) : result.data;

  const headers = new Headers();
  Object.entries(result.headers).forEach(function ([key, value]) {
    headers.append(key, value);
  });
  
  return new Response(responseBody, {
    status: result.status,
    statusText: result.statusText,
    headers
  });
}

export function buildAxiosFetch (axios) {
  return axiosFetch.bind(undefined, axios);
}


const CancelToken = axios.CancelToken;
/**
 * GraphQL request `fetch` options.
 * @kind typedef
 * @name FetchOptions
 * @type {Object}
 * @see [Polyfillable fetch options](https://github.github.io/fetch#options).
 * @prop {Object} headers HTTP request headers.
 * @prop {string} [credentials] Authentication credentials mode.
 */

/**
 * Creates a terminating [Apollo Link](https://apollographql.com/docs/link)
 * capable of file uploads. Options match [`createHttpLink`](https://apollographql.com/docs/link/links/http#options).
 * @see [GraphQL multipart request spec](https://github.com/jaydenseric/graphql-multipart-request-spec).
 * @see [apollo-link on GitHub](https://github.com/apollographql/apollo-link).
 * @kind function
 * @name createUploadLink
 * @param {Object} options Options.
 * @param {string} [options.uri=/graphql] GraphQL endpoint URI.
 * @param {function} [options.fetch] [`fetch`](https://fetch.spec.whatwg.org) implementation to use, defaulting to the `fetch` global.
 * @param {FetchOptions} [options.fetchOptions] `fetch` options; overridden by upload requirements.
 * @param {string} [options.credentials] Overrides `options.fetchOptions.credentials`.
 * @param {Object} [options.headers] Merges with and overrides `options.fetchOptions.headers`.
 * @param {boolean} [options.includeExtensions=false] Toggles sending `extensions` fields to the GraphQL server.
 * @returns {ApolloLink} A terminating [Apollo Link](https://apollographql.com/docs/link) capable of file uploads.
 * @example <caption>A basic Apollo Client setup.</caption>
 * ```js
 * const { ApolloClient } = require('apollo-client')
 * const { InMemoryCache } = require('apollo-cache-inmemory')
 * const { createUploadLink } = require('apollo-upload-client')
 *
 * const client = new ApolloClient({
 *   cache: new InMemoryCache(),
 *   link: createUploadLink()
 * })
 * ```
 */
export const createUploadLink = ({
  uri: fetchUri = '/graphql',
  fetch: linkFetch = fetch,
  fetchOptions,
  credentials,
  headers,
  includeExtensions
} = {}) => {
  const linkConfig = {
    http: { includeExtensions },
    options: fetchOptions,
    credentials,
    headers
  }

  return new ApolloLink(operation => {
    const uri = selectURI(operation, fetchUri)
    const context = operation.getContext()
    const contextConfig = {
      http: context.http,
      options: context.fetchOptions,
      credentials: context.credentials,
      headers: context.headers
    }

    const { options, body } = selectHttpOptionsAndBody(
      operation,
      fallbackHttpConfig,
      linkConfig,
      contextConfig
    )

    const { clone, files } = extractFiles(body)
    const payload = serializeFetchParameter(clone, 'Payload')
    if (files.size) {
      // Automatically set by fetch when the body is a FormData instance.
      delete options.headers['content-type']

      // GraphQL multipart request spec:
      // https://github.com/jaydenseric/graphql-multipart-request-spec

      const form = new FormData()

      form.append('operations', payload)

      const map = {}
      let i = 0
      files.forEach(paths => {
        map[++i] = paths
      })
      form.append('map', JSON.stringify(map))

      i = 0
      files.forEach((paths, file) => {
        form.append(++i, file, file.name)
      })

      options.body = form
    } else options.body = payload
    // Sets cancel token
    const source = CancelToken.source()
    options.token = source.token

    // Set uploadprogres
    if (options.body instanceof FormData && context.uploadProgress) 
        options.uploadProgres = (progressEvent) => {
          const {loaded, isTrusted, total} = progressEvent
          if (isTrusted && context.uploadProgress) {
            setInterval(() => {
              context.uploadProgress(options.key,{loaded, total})}, 500)
          }
        }

    return new Observable(observer => {
      // Allow aborting fetch, if supported.
      const { controller, signal } = createSignalIfSupported()
      if (controller) options.signal = signal

      linkFetch(uri, options)
        .then(response => {
          // Forward the response on the context.
          operation.setContext({ response })
          return response
        })
        .then(parseAndCheckHttpResponse(operation))
        .then(result => {
          setInterval(() => {observer.next(result)
            context.uploadProgress = null
            observer.complete()}, 1000)
            
          
        })
        .catch(error => {
            context.uploadProgress = null
          if (error.name === 'AbortError')
            // Fetch was aborted.
            return

          if (error.result && error.result.errors && error.result.data)
            // There is a GraphQL result to forward.
            observer.next(error.result)

          observer.error(error)
        })

      // Cleanup function.
      return () => {
        // Abort fetch.
        context.uploadProgress = null
        source.cancel("Operation canceled")
        if (controller) controller.abort()
      }
    })
  })
}