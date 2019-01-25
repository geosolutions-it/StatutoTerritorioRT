import gql from "graphql-tag";
/** Fragment sheare field between queries */
const UserFragment = gql`
fragment User on AppUserNode {
        firstName
        lastName
}
`



const RisorsaFragment = gql`
fragment Risorsa on RisorsaNode {
    nome
    uuid
    tipo
    dimensione
}
`
const PianoFragment = gql`
fragment Piano on PianoNode {
    codice
    tipo: tipologia
    descrizione
    lastUpdate
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
}
${RisorsaFragment}
${UserFragment}
` 

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

// MUTATION

export const FILE_UPLOAD = gql`
mutation($file: Upload!, $codice: String!, $tipo: String!) {
    upload(file: $file, codicePiano: $codice, tipoFile: $tipo) {
      success,
      risorse {
          ...Risorsa
      }
    }
  }
  ${RisorsaFragment}
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

export const DELETE_RISORSA = gql`
mutation($id: ID!) {
    deleteRisorsa(risorsaId: $id){
        success
        uuid
    }
}
`