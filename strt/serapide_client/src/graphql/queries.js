import gql from "graphql-tag";
import * as FR from './fragments'

/** queries */
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

export const GET_TIPO_CONTATTO = gql`
query GetTipoContatto{
  tipologiaContatto {
    label
    value
  }
}
`

export const GET_AVVIO = gql`
query GetAvvio($codice: String!) {
    procedureAvvio(piano_Codice: $codice) {
        edges{
          node{
            ...AVVIO 
            }
            
        }
    }
}
${FR.AVVIO}
`

export const GET_ADOZIONE = gql`
query GetAdozione($codice: String!) {
    procedureAdozione(piano_Codice: $codice) {
        edges{
          node{
            ...ADOZIONE 
            }
            
        }
    }
}
${FR.ADOZIONE}
`


export const GET_CONSULTAZIONE_VAS = gql`
query ConsultazioniVas($codice: String){
  consultazioneVas(proceduraVas_Piano_Codice: $codice){
  edges{
    node{
      ...ConsultazioneVAS
    }
  }
  }
}
${FR.CONSULTAZIONE_VAS}
`



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
              tipo: name
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
${FR.USER}`


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
    ${FR.PIANO}
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
${FR.VAS}
`

export const GET_CONTATTI = gql`
query getContatti($tipo: String){
    contatti(tipologia: $tipo) {
      edges {
        node{
          ...Contatto
        }
      }
    }
  }
  ${FR.CONTATTO}
`

export const GET_CONFERENZA = gql`
query GetConferenzaCopianificazione($codice: String!) {
    conferenzaCopianificazione(piano_Codice: $codice) {
          edges {
              node {
                  ...CONFERENZA
              }
          }
    }
}
${FR.CONFERENZA_COPIANIFICAZIONE}
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
export const GET_RISORSE_PIANO_CONTRODEDOTTO = gql`
query GetRisorsePianoControdedotto($codice: String!) {
      pianoControdedotto(piano_Codice: $codice){
          edges{node{
            uuid
          risorse {...Risorse}

          }}        
          
      }
}
${FR.RISORSE}

`