import gql from "graphql-tag";
import * as FR from './fragments'





// Piano
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

// VAS

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

export const FORMAZIONE_PIANO = gql`
mutation ForamzioneDelPiano($codice: String!) {
  formazioneDelPiano(codicePiano: $codice){
        pianoAggiornato{
              ...AzioniPiano 
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

export const INVIO_PROTOCOLLO_GENIO = gql`
mutation InvioProtocolloGenioCivile($codice: String!) {
    invioProtocolloGenioCivile(uuid: $codice) {
        errors
        avvioAggiornato {
              piano{
                numeroProtocolloGenioCivile,
                dataProtocolloGenioCivile
                ...AzioniPiano
              }
        }
    }
}
${FR.AZIONI_PIANO}
`

// Procedura adozione

export const UPDATE_ADOZIONE = gql`
mutation UpdateProceduraAdozione($input: UpdateProceduraAdozioneInput!) {
    updateProceduraAdozione(input: $input) {
        proceduraAdozioneAggiornata {
            ...ADOZIONE
        }
    }
}
${FR.ADOZIONE}
`

export const TRASMISSIONE_ADOZIONE = gql`
mutation TrasmissioneAdozione($codice: String!){
  trasmissioneAdozione(uuid: $codice){
      errors
        adozioneAggiornata {
              piano{
                ...AzioniPiano
              }
        }
  }
}
${FR.AZIONI_PIANO}
`

export const TRASMISSIONE_OSSERVAZIONI = gql`
mutation TrasmissioneOsservazioni($codice: String!){
  trasmissioneOsservazioni(uuid: $codice){
      errors
        adozioneAggiornata {
              piano{
                ...AzioniPiano
              }
        }
  }
}
${FR.AZIONI_PIANO}
`

export const ESITO_CONFERENZA_PAESAGGISTICA = gql`
mutation EsitoConferenzaPaesaggistica($codice: String!){
  esitoConferenzaPaesaggistica(uuid: $codice){
      errors
        adozioneAggiornata {
              piano{
                ...AzioniPiano
              }
        }
  }
}
${FR.AZIONI_PIANO}
`


export const CONTRODEDUZIONI = gql`
mutation Contorodeduzioni($codice: String!){
  controdeduzioni(uuid: $codice){
      errors
        adozioneAggiornata {
              piano{
                ...AzioniPiano
              }
        }
  }
}
${FR.AZIONI_PIANO}
`

// Piano controdedotto

export const PIANO_CONTRODEDOTTO = gql`
mutation PianoControdedotto($codice: String!) {
  pianoControdedotto(uuid: $codice){
    errors
    adozioneAggiornata {
              piano{
                ...AzioniPiano
              }
        }
  }
}
${FR.AZIONI_PIANO}
`
// Procedura Avvio

export const UPDATE_AVVIO = gql`
mutation UpdateProceduraAvvio($input: UpdateProceduraAvvioInput!) {
    updateProceduraAvvio(input: $input) {
        proceduraAvvioAggiornata {
            ...AVVIO
        }
    }
}
${FR.AVVIO}
`

export const AVVIA_PIANO = gql`
mutation AvvioPiano($codice: String!) {
    avviaPiano(uuid: $codice) {
        errors
        avvioAggiornato {
              piano {
                ...AzioniPiano
              }
        }
    }
}
${FR.AZIONI_PIANO}
`

export const RICHIESTA_INTEGRAZIONI = gql`
mutation RichiestaIntegrazioni($codice: String!) {
  richiestaIntegrazioni(uuid: $codice) {
        errors
        avvioAggiornato {
              piano {
                ...AzioniPiano
              }
        }
    }
}
${FR.AZIONI_PIANO}
`

export const INTEGRAZIONI_RICHIESTE = gql`
mutation IntegrazioniRichieste($codice: String!) {
  integrazioniRichieste(uuid: $codice) {
        errors
        avvioAggiornato {
              piano {
                ...AzioniPiano
              }
        }
    }
}
${FR.AZIONI_PIANO}
`


export const RICHIESTA_CONFERENZA_COPIANIFICAZIONE = gql`
mutation RichiestaConferenzaCopianificazione($codice: String!) {
  richiestaConferenzaCopianificazione(uuid: $codice) {
        errors
        avvioAggiornato {
              piano {
                ...AzioniPiano
              }
        }
    }
}
${FR.AZIONI_PIANO}
`



export const CHIUSURA_CONFERENZA_COPIANIFICAZIONE = gql `
mutation ChiusuraConferenzaCopianificazione($codice: String!) {
    chiusuraConferenzaCopianificazione(uuid: $codice) {
      errors
        avvioAggiornato {
              piano {
                ...AzioniPiano
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
      ...Contatto
    }
  }
	
}
${FR.CONTATTO}
`


// Gestione Risorse piano, vas, conferenza, avvio, adozione
    
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


   // Adozione
export const CONTRODEDOTTO_FILE_UPLOAD = gql`
mutation ControdedottoUploadFile($file: Upload!, $codice: String!, $tipo: String!) {
    upload: uploadRisorsaPianoControdedotto(file: $file, codice: $codice, tipoFile: $tipo) {
      success
      fileName
      pianoControdedottoAggiornato {
          uuid
          risorse {
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
            risorse {
              ...Risorse
            }
        }
    }
}
${FR.ADOZIONE}
`