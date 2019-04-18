import gql from "graphql-tag"
import * as FR from './fragments'

// Mutations per upload e delete delle risorse di vario tipo

//Piano
export const FILE_UPLOAD = gql`
  mutation UploadFile($file: Upload!, $codice: String!, $tipo: String!) {
      upload(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        pianoAggiornato {
            ...Piano
        }
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

//VAS
export const VAS_FILE_UPLOAD = gql`
  mutation VasUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
      upload: uploadRisorsaVas(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        proceduraVasAggiornata {
            ...VAS
        }
      }
    }
    ${FR.VAS}
  `

export const DELETE_RISORSA_VAS = gql`
  mutation($id: ID!, $codice: String!) {
      deleteRisorsa: deleteRisorsaVas(risorsaId: $id, codice: $codice){
          success
          proceduraVasAggiornata {
              ...VAS
          }
      }
  }
  ${FR.VAS}
  `

// Confenrenza Copianificazione
export const CONFEREZA_FILE_UPLOAD = gql`
  mutation ConferenzaUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
      upload: uploadRisorsaCopianificazione(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        conferenzaCopianificazioneAggiornata {
            ...CONFERENZA
        }
      }
    }
    ${FR.CONFERENZA_COPIANIFICAZIONE}
  `

export const DELETE_RISORSA_COPIANIFICAZIONE = gql`
  mutation($id: ID!, $codice: String!) {
      deleteRisorsa: deleteRisorsaCopianificazione(risorsaId: $id, codice: $codice){
          success
          conferenzaCopianificazioneAggiornata {
              ...CONFERENZA
          }
      }
  }
  ${FR.CONFERENZA_COPIANIFICAZIONE}
  `

// Avvio
export const AVVIO_FILE_UPLOAD = gql`
  mutation VasUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
      upload: uploadRisorsaAvvio(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        proceduraAvvioAggiornata {
            ...AVVIO
        }      
      }
    }
    ${FR.AVVIO}
  `

export const DELETE_RISORSA_AVVIO = gql`
  mutation DeleteRisorsaAvvio($id: ID!, $codice: String!) {
      deleteRisorsa: deleteRisorsaAvvio(risorsaId: $id, codice: $codice){
          success
          proceduraAvvioAggiornata {
              ...AVVIO
          }
      }
  }
  ${FR.AVVIO}
  `

// Adozione
export const ADOZIONE_FILE_UPLOAD = gql`
  mutation AdozioneUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
      upload: uploadRisorsaAdozione(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        proceduraAdozioneAggiornata {
            ...ADOZIONE
        }
      }
    }
    ${FR.ADOZIONE}
  `

export const DELETE_RISORSA_ADOZIONE = gql`
  mutation DeleteRisorsaAdozione($id: ID!, $codice: String!) {
      deleteRisorsa: deleteRisorsaAdozione(risorsaId: $id, codice: $codice){
          success
          proceduraAdozioneAggiornata {
              ...ADOZIONE
          }
      }
  }
  ${FR.ADOZIONE}
  `

// piano controdedotto 

export const CONTRODEDOTTO_FILE_UPLOAD = gql`
  mutation ControdedottoUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
      upload: uploadRisorsaPianoControdedotto(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        pianoControdedottoAggiornato {
            uuid
            risorse(archiviata: false){
              ...Risorse
            }
        }
      }
    }
    ${FR.RISORSE}
  `

export const DELETE_RISORSA_CONTRODEDOTTO = gql`
  mutation DeleteRisorsaControdedotto($id: ID!, $codice: String!) {
      deleteRisorsa: deleteRisorsaPianoControdedotto(risorsaId: $id, codice: $codice){
          success
          pianoControdedottoAggiornatoAggiornato{
              uuid
              risorse(archiviata: false){
                ...Risorse
              }
          }
      }
  }
  ${FR.RISORSE}
  `
// revisione piano cp

export const PIANO_REV_POST_CP_FILE_UPLOAD = gql`
  mutation PianoRevPortCpUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
      upload: uploadRisorsaPianoRevPostCp(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        pianoRevPostCpAggiornato {
            uuid
            risorse(archiviata: false){
              ...Risorse
            }
        }
      }
    }
    ${FR.RISORSE}
  `

export const DELETE_RISORSA_PIANO_REV_POST_CP = gql`
  mutation DeleteRisorsaPianoRevPostCp($id: ID!, $codice: String!) {
      deleteRisorsa: deleteRisorsaPianoRevPostCp(risorsaId: $id, codice: $codice){
          success
          pianoRevPostCpAggiornato {
              uuid
              risorse(archiviata: false){
                ...Risorse
              }
          }
      }
  }
  ${FR.RISORSE}
  `

// adozione vas

export const ADOZIONE_VAS_FILE_UPLOAD = gql`
  mutation AozioneVasFileUpload($file: Upload!, $codice: String!, $tipo: String!) {
      upload: uploadRisorsaAdozioneVas(file: $file, codice: $codice, tipoFile: $tipo) {
        success
        fileName
        proceduraVasAggiornata{
            uuid
            risorse(archiviata: false){
              ...Risorse
            }
        }
      }
    }
    ${FR.RISORSE}
  `

export const DELETE_RISORSA_ADOZIONE_VAS = gql`
  mutation DeleteRisorsaPianoRevPostCp($id: ID!, $codice: String!) {
      deleteRisorsa: deleteRisorsaAdozioneVas(risorsaId: $id, codice: $codice){
              success
              proceduraVasAggiornata{
                  uuid
                  risorse(archiviata: false){
                    ...Risorse
                  }
              }
      }
  }
  ${FR.RISORSE}
  `