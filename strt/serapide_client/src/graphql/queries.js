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
    modello: procedureAvvio(piano_Codice: $codice) {
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
    modello: procedureAdozione(piano_Codice: $codice) {
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
  modello: consultazioneVas(proceduraVas_Piano_Codice: $codice){
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
    modello: procedureVas(piano_Codice: $codice) {
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
    modello: conferenzaCopianificazione(piano_Codice: $codice) {
          edges {
              node {
                  ...CONFERENZA
              }
          }
    }
}
${FR.CONFERENZA_COPIANIFICAZIONE}
`


export const GET_RISORSE_PIANO_CONTRODEDOTTO = gql`
query GetRisorsePianoControdedotto($codice: String!) {
      modello: pianoControdedotto(piano_Codice: $codice){
          edges{node{
            uuid
          risorse(archiviata: false){...Risorse}

          }}        
          
      }
}
${FR.RISORSE}
`
export const GET_PIANO_REV_POST_CP = gql`
query PianoRevPostCp($codice: String!){
    modello: pianoRevPostCp(piano_Codice: $codice){
      edges{
        node{
          uuid
          risorse(archiviata: false){...Risorse}
    }
  }
}}
${FR.RISORSE}
`

// Vas adozione

export const GET_ADOZIONE_VAS = gql`
query AdozioneVas($codice: String!){
  modello: procedureAdozioneVas(piano_Codice: $codice){
      edges{
        node{
          uuid
          risorse(archiviata: false) {...Risorse}
    }
  }
}}
${FR.RISORSE}
`

// Approvazione


export const GET_APPROVAZIONE = gql`
query GetApprovazione($codice: String!) {
  modello: procedureApprovazione(piano_Codice: $codice) {
        edges{
          node{
            ...APPROVAZIONE 
            }  
        }
    }
}
${FR.APPROVAZIONE}
`


export const GET_ADOZIONE_PAGE = gql`

query RisorsePaginaAdozione($codice: String!){
  pianoRevPostCp(piano_Codice: $codice){
      edges{
        node{
          uuid
          risorse(archiviata: false){...Risorse}
        }
    }
  }
  pianoControdedotto(piano_Codice: $codice){
      edges{
        node{
            uuid
            risorse(archiviata: false){...Risorse}
            }
      }        
  }

  procedureAdozione(piano_Codice: $codice) {
      edges{
          node{
            ...ADOZIONE 
            }
            
        }
    }
  procedureAdozioneVas(piano_Codice: $codice){
      edges{
        node{
            uuid
            risorse(archiviata: false) {...Risorse}
        }
      }
    }
}
${FR.ADOZIONE}
${FR.RISORSE}
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