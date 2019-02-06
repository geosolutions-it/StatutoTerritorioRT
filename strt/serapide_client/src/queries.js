import gql from "graphql-tag";
/** Fragment sheare field between queries */
const UserFragment = gql`
fragment User on AppUserNode {
    id
    email
    fiscalCode
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
const VASFragment = gql`
fragment VAS on ProceduraVASNode {
        uuid
        tipologia
        piano {
            codice
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
// MUTATION
// Upload a generic risources
export const FILE_UPLOAD = gql`
mutation($file: Upload!, $codice: String!, $tipo: String!) {
    upload(file: $file, codice: $codice, tipoFile: $tipo) {
      success,
      risorse {
          ...Risorsa
      }
    }
  }
  ${RisorsaFragment}
`
// Upload a vas resources
export const VAS_FILE_UPLOAD = gql`
mutation($file: Upload!, $codice: String!, $tipo: String!) {
    uploadRisorsaVas(file: $file, codice: $codice, tipoFile: $tipo) {
      success,
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
export const GET_VAS_AUTHORITIES = gql`
query getAuth{
    authorities @client
    {
        value
    label   
    }
}
`