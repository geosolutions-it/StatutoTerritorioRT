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
          nome
          uuid
        }
      }
    }
  }
`
// MUTATION
// Mutation per piano
// Upload a generic risources
export const FILE_UPLOAD = gql`
mutation UploadFile($file: Upload!, $codice: String!, $tipo: String!) {
    upload(file: $file, codice: $codice, tipoFile: $tipo) {
      success
      pianoAggiornato {
        ...Piano
    }
      fileName
    }
  }
  ${FR.PIANO}
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
${FR.PIANO}
`

export const CREA_PIANO= gql`mutation CreatePiano($input: CreatePianoInput!) {
    createPiano(input: $input) {
        nuovoPiano {
            ...Piano
      }
    }
  }
  ${FR.PIANO}
`
export const UPDATE_PIANO = gql`
mutation UpdatePiano($input: UpdatePianoInput!) {
    updatePiano(input: $input) {
        pianoAggiornato {
            ...Piano
        }
    }
}
${FR.PIANO}
`
export const PROMUOVI_PIANO = gql`
mutation PromozionePiano($codice: String!){
  promozionePiano(codicePiano: $codice){
    pianoAggiornato {
      ...Piano
  }
  }
}
${FR.PIANO}
`
export const DELETE_PIANO = gql`
  mutation($codice: String!) {
    deletePiano(codicePiano: $codice){
        success
        codicePiano
    }
}
`

// Mutation per VAS

// Upload a vas resources
export const VAS_FILE_UPLOAD = gql`
mutation VasUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
    uploadRisorsaVas(file: $file, codice: $codice, tipoFile: $tipo) {
      success
      proceduraVasAggiornata {
          ...VAS
      }
      fileName
    }
  }
  ${FR.VAS}
`

export const UPDATE_VAS = gql`
mutation UpdateProceduraVas($input: UpdateProceduraVASInput!) {
    updateProceduraVas(input: $input) {
        proceduraVasAggiornata {
            ...VAS
        }
    }
}
${FR.VAS}
`
export const UPDATE_CONSULTAZIONE_VAS = gql`
mutation UpdateConsultazioneVas($input: UpdateConsultazioneVASInput!) {
  updateConsultazioneVas(input: $input) {
      consultazioneVasAggiornata {
            ...ConsultazioneVAS
        }
    }
}
${FR.CONSULTAZIONE_VAS}
`

export const PUBBLICA_PROVV_VERIFICA = gql`
mutation UpdateProceduraVas($input: UpdateProceduraVASInput!) {
    updateProceduraVas(input: $input) {
        proceduraVasAggiornata {
              piano {
                ...AzioniPiano
              }
            }
        }
    }
  ${FR.AZIONI_PIANO}
`

export const INVIO_PARERI_VERIFICA = gql`
mutation InvioPareriVerifica($codice: String!) {
  invioPareriVerificaVas(uuid: $codice) {
        vasAggiornata {
          ...VAS
          piano {
            ...AzioniPiano
          }
        }
    }
}
${FR.AZIONI_PIANO}
${FR.VAS}
`
export const INVIO_PARERI_VAS = gql`
mutation InvioPareriVAS($codice: String!) {
  invioPareriVas(uuid: $codice) {
        vasAggiornata {
          ...VAS
          piano {
            ...AzioniPiano
          }
        }
    }
}
${FR.AZIONI_PIANO}
${FR.VAS}
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
${FR.VAS}
`

export const PROVVEDIMENTO_VERIFICA_VAS = gql`
mutation ProvveddimentoVerificaVAS($uuid: String!) {
    assoggettamentoVas(uuid: $uuid){
        vasAggiornata{
          uuid
          verificaEffettuata
          dataAssoggettamento
          piano{
            ...AzioniPiano
          }
      }
    }
  }
${FR.AZIONI_PIANO}
`
export const AVVIO_ESAME_PARERI_SCA = gql`
mutation AvvioEsamePareriSCA($uuid: String!) {
    avvioEsamePareriSca(uuid: $uuid){
        vasAggiornata{
            piano{
              ...AzioniPiano 
            }
        }
    }
}
${FR.AZIONI_PIANO}
`
export const UPLOAD_ELABORATI_VAS = gql`
mutation UploadElaboratiVas($uuid: String!) {
    uploadElaboratiVas(uuid: $uuid) {
        vasAggiornata{
            piano{  
              ...AzioniPiano
            }
        }
    }
}
${FR.AZIONI_PIANO}
`
export const CREA_CONSULTAZIONE_VAS = gql`
mutation CreaConsultazione($input: CreateConsultazioneVASInput!){
    createConsultazioneVas(input: $input){
        nuovaConsultazioneVas{     
            ...ConsultazioneVAS
        }
    }
}
${FR.CONSULTAZIONE_VAS}
`

export const AVVIO_CONSULTAZIONE_VAS = gql`
mutation AvvioConsultazioniVAS($codice: String!) {
    avvioConsultazioniVas(uuid: $codice) {
        errors
        consultazioneVasAggiornata {
            proceduraVas{
              piano{
                ...AzioniPiano
              }
            }
        }
    }
}
${FR.AZIONI_PIANO}
`

// altre mutations

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