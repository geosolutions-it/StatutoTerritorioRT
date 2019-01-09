import ApolloClient from 'apollo-boost'
const getCookie = name => document.cookie.split(';').filter(el => el.startsWith("csrftoken")).map(el => el.split("=").pop()).pop()

const client = new ApolloClient({
    uri: "/serapide/graphql",
    credentials: 'same-origin',
    headers: {"X-CSRFToken": getCookie('csrftoken')}})
export default client