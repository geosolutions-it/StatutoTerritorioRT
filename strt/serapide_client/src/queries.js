import gql from "graphql-tag";
/** Fragment sheare field between queries */
const UserFragment = gql`
fragment User on AppUserNode {
    id
    email
    fiscalCode
    firstName
    lastName
    dateJoined
    alertsCount
}
`
const RisorsaFragment = gql`
fragment Risorsa on RisorsaNode {
    nome
    uuid
    tipo
    dimensione
    downloadUrl
}
`
const AUT_VASFragment = gql`
fragment AUT_VAS on ContattoNode{
        nome
        uuid
}
`
const VASFragment = gql`
fragment VAS on ProceduraVASNode {
        uuid
        tipologia
        piano {
            codice
            autoritaCompetenteVas{
                edges{
                  node{
                    ...AUT_VAS
                  }
                }
            }
            soggettiSca {
                edges{
                    node{
                        ...AUT_VAS
                    }
                }
            }
            soggettoProponente {
              ...AUT_VAS
            }
        }
        risorse{
            edges{
              node{
                ...Risorsa 
              }
            }
        }
}
${RisorsaFragment}
${AUT_VASFragment}
`


const PianoFragment = gql`
fragment Piano on PianoNode {
    codice
    tipo: tipologia
    descrizione
    lastUpdate
    dataDelibera
    dataCreazione
    dataAccettazione
    dataAvvio
    dataApprovazione
    alertsCount
    azioni {
        edges {
            node {
                order
                tipologia
                stato
              	attore
              	data
              	uuid
            }
        }
    }
    ente {
            code
            name
            type {
                tipoente: name
            }
        }
    fase{
        nome
        codice
        descrizione
    }
    user{
        ...User
    }
    risorse{
        edges{
          node{
            ...Risorsa 
          }
        }
      }
    autoritaCompetenteVas{
        edges{
          node{
            ...AUT_VAS
          }
        }
    }
    soggettiSca{
        edges{
          node{
            ...AUT_VAS
          }
        }
    }
    soggettoProponente {
      ...AUT_VAS
    }
}
${RisorsaFragment}
${UserFragment}
${AUT_VASFragment}
` 
export const GET_ENTI = gql`
query {
    enti{
        edges{
            node{
                name
                code
                type{
                    tipo: name
                }
            }
        }
    }
}`

/** queries */
export const CREA_PIANO_PAGE = gql`
query CreaPianoPage{
    enti{
        edges{
            node{
                name
                code
                role
                type{
                    tipo: name
                }
            }
        }
    }
    tipologiaPiano{
        value
        label
      }
}
`

export const GET_UTENTE = gql`
query{
  utenti {
    edges {
      node {
        ...User
        contactType
        attore
        role{
          type
          name
          code
          description
          organization {
            name
            description
            code
            type {
              code
            }
          }
        }
        unreadThreadsCount
        unreadMessages {
          thread {
            id
            subject
            absoluteUrl
          }
          sender {
            email
            firstName
            lastName
          }
          sentAt
          content
        }
      }
    }
  }
}
${UserFragment}`


export const GET_PIANI = gql`
query getPiani($faseCodice: String, $codice: String){
    piani(fase_Codice: $faseCodice, codice: $codice){
        edges{
            node{
                ...Piano
            }
          }
        }
}
    ${PianoFragment}
`

export const GET_VAS = gql`
query getVas($codice: String!) {
    procedureVas(piano_Codice: $codice) {
        edges{
          node{
            ...VAS 
            }
            
        }
    }
}
${VASFragment}
`

export const GET_CONTATTI = gql`
query getContatti($tipo: String){
    contatti(tipologia: $tipo) {
      edges {
        node{
          nome
          uuid
        }
      }
    }
  }
`
// MUTATION
// Upload a generic risources
export const FILE_UPLOAD = gql`
mutation($file: Upload!, $codice: String!, $tipo: String!) {
    upload(file: $file, codice: $codice, tipoFile: $tipo) {
      success
      pianoAggiornato {
        ...Piano
    }
      fileName
    }
  }
  ${PianoFragment}
`
// Upload a vas resources
export const VAS_FILE_UPLOAD = gql`
mutation($file: Upload!, $codice: String!, $tipo: String!) {
    uploadRisorsaVas(file: $file, codice: $codice, tipoFile: $tipo) {
      success
      proceduraVasAggiornata {
          ...VAS
      }
    }
  }
  ${VASFragment}
`



export const CREA_PIANO= gql`mutation CreatePiano($input: CreatePianoInput!) {
    createPiano(input: $input) {
        nuovoPiano {
            ...Piano
      }
    }
  }
  ${PianoFragment}
`
export const UPDATE_PIANO = gql`
mutation UpdatePiano($input: UpdatePianoInput!) {
    updatePiano(input: $input) {
        pianoAggiornato {
            ...Piano
        }
    }
}
${PianoFragment}
`

export const UPDATE_VAS = gql`
mutation UpdateProceduraVas($input: UpdateProceduraVASInput!) {
    updateProceduraVas(input: $input) {
        proceduraVasAggiornata {
            ...VAS
        }
    }
}
${VASFragment}
`

export const DELETE_RISORSA = gql`
mutation($id: ID!, $codice: String!) {
    deleteRisorsa(risorsaId: $id, codice: $codice){
        success
        pianoAggiornato {
            ...Piano
        }
    }
}
${PianoFragment}
`
export const DELETE_RISORSA_VAS = gql`
mutation($id: ID!, $codice: String!) {
    deleteRisorsaVas(risorsaId: $id, codice: $codice){
        success
        proceduraVasAggiornata {
            ...VAS
        }
    }
}
${VASFragment}
`

export const CREATE_CONTATTO = gql`
mutation CreaContatto($input: CreateContattoInput!){
  createContatto(input: $input){
    nuovoContatto{
      uuid
      nome
    }
  }
	
}
`
export const PROMUOVI_PIANO = gql`
mutation PromozionePiano($codice: String!){
  promozionePiano(codicePiano: $codice){
    pianoAggiornato {
      ...Piano
  }
  }
}
${PianoFragment}
`

// LOCAL STATE
// example of local state query
export const GET_VAS_AUTHORITIES = gql`
query getAuth{
    authorities @client
    {
        value
    label   
    }
}
`