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
    lastUpdate
    user{
      fiscalCode
    }
    
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
        dataVerifica
        dataCreazione
        dataProcedimento
        dataApprovazione
        verificaEffettuata
        procedimentoEffettuato
        assoggettamento
        nonNecessaria
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
        documentoPreliminareVerifica{
          ...Risorsa 
        }
        relazioneMotivataVasSemplificata{
          ...Risorsa 
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

const ConsultazioneVasFragment = gql`
fragment  ConsultazioneVAS on ConsultazioneVASNode {
          uuid
          avvioConsultazioniSca
          dataCreazione
          dataScadenza
          dataRicezionePareri
          proceduraVas{
            uuid
            risorse {
            edges {
              node {
                ...Risorsa 
              }
            }
          }
        }
  }
  ${RisorsaFragment}
`

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
${ConsultazioneVasFragment}
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
mutation UploadFile($file: Upload!, $codice: String!, $tipo: String!) {
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
mutation VasUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
    uploadRisorsaVas(file: $file, codice: $codice, tipoFile: $tipo) {
      success
      proceduraVasAggiornata {
          ...VAS
      }
      fileName
    }
  }
  ${VASFragment}
`
// //Upload a consultazione vas resources
// export const CONSULTAZIONE_VAS_FILE_UPLOAD = gql`
// mutation($file: Upload!, $codice: String!, $tipo: String!) {
//     uploadConsultazioneVas(file: $file, codice: $codice, tipoFile: $tipo) {
//       success
//       consultazioneVasAggiornata{
//           ...ConsultazioneVAS
//       }
//     }
//   }
//   ${ConsultazioneVasFragment}
// `


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
export const UPDATE_CONSULTAZIONE_VAS = gql`
mutation UpdateConsultazioneVas($input: UpdateConsultazioneVASInput!) {
  updateConsultazioneVas(input: $input) {
      consultazioneVasAggiornata {
            ...ConsultazioneVAS
        }
    }
}
${ConsultazioneVasFragment}
`


export const PUBBLICA_PROVV_VERIFICA = gql`
mutation UpdateProceduraVas($input: UpdateProceduraVASInput!) {
    updateProceduraVas(input: $input) {
        proceduraVasAggiornata {

              piano {
                codice
                azioni{
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
              }
            }
        }
    }
`
export const INVIO_PARERI_VERIFICA = gql`
mutation InvioPareriVerifica($codice: String!) {
  invioPareriVerificaVas(uuid: $codice) {
        vasAggiornata {
          ...VAS
          piano {
            azioni{
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
          }
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
// export const DELETE_RISORSA_CONSULTAZIONE_VAS = gql`
// mutation($id: ID!, $codice: String!) {
//     deleteConsultazioneVas(risorsaId: $id, codice: $codice){
//         success
//         consultazioneVasAggiornata {
//             ...ConsultazioneVAS
//         }
//     }
// }
// ${ConsultazioneVasFragment}
// `



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
export const DELETE_PIANO = gql`
  mutation($codice: String!) {
    deletePiano(codicePiano: $codice){
        success
        codicePiano
    }
}
`
export const PROVVEDIMENTO_VERIFICA_VAS = gql`
mutation ProvveddimentoVerificaVAS($uuid: String!) {
    assoggettamentoVas(uuid: $uuid){
        vasAggiornata{
          uuid
          verificaEffettuata
        piano{
            codice
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
        }  
      }
    }
  }
`
export const CREA_CONSULTAZIONE_VAS = gql`
mutation CreaConsultazione($input: CreateConsultazioneVASInput!){
  createConsultazioneVas(input: $input){
    nuovaConsultazioneVas{     
      ...ConsultazioneVAS
    }
  }
}
${ConsultazioneVasFragment}
`

export const AVVIO_CONSULTAZIONE_VAS = gql`
mutation AvvioConsultazioniVAS($codice: String!) {
    avvioConsultazioniVas(uuid: $codice) {
      errors
      consultazioneVasAggiornata {
        proceduraVas{
        piano{
          codice
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
        }
      }
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