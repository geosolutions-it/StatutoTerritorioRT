import gql from "graphql-tag";
/** Fragment share field between queries */
export const USER = gql`
fragment User on UtenteNode {
      fiscalCode
    	firstName
    	lastName
    	email
    	isStaff
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
`
export const PROFILES = gql`
fragment Profiles on ProfiloChoiceNode {
      ente{
        ipa
        nome
        descrizione
        tipo
      }
      profilo
      qualifiche{
        qualifica
        ufficio
        qualificaUfficio{
          qualifica
          qualificaLabel
        }
      }
    
    }
`


export const RISORSA = gql`
fragment Risorsa on RisorsaNode {
    nome
    uuid
    tipo
    dimensione
    downloadUrl
    lastUpdate
    user{
      fiscalCode
      firstName
      lastName
    }
    label
    tooltip
}
`
export const CONTATTO = gql`
fragment Contatto on QualificaUfficioNode{
        id
        qualifica
        qualificaLabel
        ufficio{
          uuid
          descrizione
          email
          nome
        ente{
          descrizione
          ipa
          nome
    }
  }
}
`
export const AZIONI = gql`
fragment Azioni on AzioneNode {
      order
      tipologia
      stato
      qualificaRichiesta
      data #data di chiusura azione
      uuid
      label
      tooltip
      fase
      eseguibile
      avvioScadenza # data di avvio scadenza
      scadenza #data entro la quale eseguire azione
}
`
export const RISORSE = gql`
fragment Risorse on RisorsaNodeConnection{
  edges {
    node {
      ...Risorsa
    }
  }
}
${RISORSA}`
// Utilizzata per updatare la lista azioni
export const AZIONI_PIANO = gql`
fragment AzioniPiano on PianoNode {
  codice
  fase 
  azioni {
      ...Azioni
  }

}
${AZIONI}
`
export const VAS = gql`
fragment VAS on ProceduraVASNode {
        uuid
        tipologia
        dataVerifica
        dataCreazione
        dataProcedimento
        dataApprovazione
        dataAssoggettamento
        verificaEffettuata
        procedimentoEffettuato
        assoggettamento
        nonNecessaria
        conclusa
        pubblicazioneProvvedimentoVerificaAc
        pubblicazioneProvvedimentoVerificaAp
        piano {
          codice
            soggettoProponente {
              qualifica
              qualificaLabel
              ufficio {
                  uuid
                  nome
                  ente {
                    ipa
                    nome
                  }
                }
              }
          soggettiOperanti {
            qualificaUfficio {
              qualifica
              qualificaLabel
                ufficio {
                uuid
                nome
                ente {
                    ipa
                    nome
                  }
              }
            }
          }
        }
        risorse(archiviata: false){
            ...Risorse
        }
}
${RISORSE}
`
export const PIANO = gql`
fragment Piano on PianoNode {
    codice
    tipo: tipologia
    descrizione
    lastUpdate
    dataDelibera
    numeroDelibera
    dataCreazione
    dataAccettazione
    dataAvvio
    dataApprovazione
    alertsCount
    dataProtocolloGenioCivile
    redazioneNormeTecnicheAttuazioneUrl
    compilazioneRapportoAmbientaleUrl
    conformazionePitPprUrl
    monitoraggioUrbanisticoUrl 
    azioni {
        ...Azioni
    }
    ente {
      ipa
      nome
      tipo
    }
    fase
    responsabile{
        ...User
    }
    risorse(archiviata: false){
        ...Risorse
      }
    soggettoProponente {
        qualifica
        qualificaLabel
        ufficio {
          uuid
          nome
          ente{
              ipa
               nome
          }
        }
    }
    soggettiOperanti {
      qualificaUfficio{
					qualifica
          qualificaLabel
          ufficio{
            uuid
            nome
            ente {
              ipa
               nome
            }
          }
        }
  }
  proceduraVas {uuid}
  proceduraAvvio {uuid}
  
}
${RISORSE}
${USER}
${AZIONI}
` 

export const CONSULTAZIONE_VAS = gql`
fragment  ConsultazioneVAS on ConsultazioneVASNode {
          uuid
          avvioConsultazioniSca
          dataCreazione
          dataScadenza
          dataAvvioConsultazioniSca
          dataRicezionePareri
          proceduraVas{
            uuid
            tipologia
            dataAssoggettamento
            risorse(archiviata: false) {
            ...Risorse
            }
          }
}
  ${RISORSE}
`
export const AVVIO = gql`
fragment AVVIO on ProceduraAvvioNode {
        uuid
        conferenzaCopianificazione
        dataCreazione
        dataScadenzaRisposta
        garanteNominativo
        garantePec
        richiestaIntegrazioni
        messaggioIntegrazione
        notificaGenioCivile
        risorse(archiviata: false) {
            ...Risorse
        }
}
${RISORSE}
`


export const ADOZIONE = gql`
fragment ADOZIONE on ProceduraAdozioneNode {
        uuid
        dataCreazione
        dataDeliberaAdozione
        scadenzaPareriAdozioneSca
        pubblicazioneBurtUrl
        pubblicazioneBurtData
        pubblicazioneSitoUrl
        pubblicazioneBurtBollettino
        osservazioniConcluse
        conclusa
        richiestaConferenzaPaesaggistica
        urlPianoControdedotto
        risorse(archiviata: false) {
            ...Risorse
        }
}
${RISORSE}
`
export const APPROVAZIONE = gql`
fragment APPROVAZIONE on ProceduraApprovazioneNode {
        uuid
        dataCreazione
        dataDeliberaApprovazione
        richiestaConferenzaPaesaggistica
        urlPianoPubblicato
        pubblicazioneUrl
        pubblicazioneUrlData
        risorse(archiviata: false) {
            ...Risorse
        }
}
${RISORSE}
`

export const PUBBLICAZIONE = gql`
fragment PUBBLICAZIONE on ProceduraPubblicazioneNode {
        uuid
        pubblicazioneUrl
        pubblicazioneUrlData
        risorse(archiviata: false) {
            ...Risorse
        }
}
${RISORSE}
`


export const CONFERENZA_COPIANIFICAZIONE = gql`
fragment CONFERENZA on ConferenzaCopianificazioneNode {
        uuid
        idPratica
        dataRichiestaConferenza
        dataScadenzaRisposta
        risorse(archiviata: false) {
            ...Risorse
        }
}
${RISORSE}
`