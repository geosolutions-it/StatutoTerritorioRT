import gql from "graphql-tag";
import * as FR from './fragments';

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
query ConsultazioniVas($codice: ID){
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
    tipologiaPiano{
        value
        label
      }
}
`


export const GET_UTENTE = gql`
query {
	auth: userChoices{
    profili {
      ...Profiles
    }
  }
  utenti {
  edges{
    node{
      ...User
  	}
  }
  }}
${FR.PROFILES}
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
query getUffici($tipo: String){
  uffici(qualifica: $tipo) {
      ...Contatto
    }
  }
  ${FR.CONTATTO}
`
export const GET_CONTATTI_M = gql`
query getUffici($tipo: [String]){
  uffici(qualifiche: $tipo) {
      ...Contatto
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


// Pubblicazione 
export const GET_PUBBLICAZIONE = gql`
query GetPubblicazione($codice: String!) {
  modello: procedurePubblicazione(piano_Codice: $codice) {
        edges{
          node{
            ...PUBBLICAZIONE 
            }  
        }
    }
}
${FR.PUBBLICAZIONE}
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

export const GET_AVVIO_PAGE = gql`

query RisorsePaginaAvvio($codice: String){
  procedureAvvio(piano_Codice: $codice) {
        edges{
          node{
            ...AVVIO 
            }
            
        }
    }
  procedureVas(piano_Codice: $codice) {
        edges{
          node{
            uuid
            risorse{...Risorse}
            }
            
        }
    }
}
${FR.AVVIO}
${FR.RISORSE}
`

export const GET_APPROVAZIONE_PAGE = gql`

query RisorsePaginaApprovazione($codice: String!){
  pianoRevPostCp(piano_Codice: $codice){
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
  procedureApprovazione(piano_Codice: $codice) {
      edges{
          node{
            ...APPROVAZIONE 
            }
            
        }
    }
}
${FR.ADOZIONE}
${FR.APPROVAZIONE}
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