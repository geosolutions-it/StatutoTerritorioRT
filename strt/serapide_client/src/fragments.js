import gql from "graphql-tag";
/** Fragment sheare field between queries */
export const USER = gql`
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
fragment Contatto on ContattoNode{
        nome
        tipologia
        uuid
}
`
export const AZIONI = gql`
fragment Azioni on AzioneNodeConnection {
  edges {
    node {
      order
      tipologia
      stato
      attore
      data
      uuid
      label
      tooltip
    }
  }
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
        piano {
            codice
            autoritaCompetenteVas{
                edges{
                  node{
                    ...Contatto
                  }
                }
            }
            soggettiSca {
                edges{
                    node{
                        ...Contatto
                    }
                }
            }
            soggettoProponente {
              ...Contatto
            }
        }
        risorse(archiviata: false){
            ...Risorse
        }
        documentoPreliminareVerifica{
          ...Risorsa 
        }
        relazioneMotivataVasSemplificata{
          ...Risorsa 
        }
}
${RISORSE}
${CONTATTO}
`
export const PIANO = gql`
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
    numeroProtocolloGenioCivile
    dataProtocolloGenioCivile
    redazioneNormeTecnicheAttuazioneUrl
    compilazioneRapportoAmbientaleUrl
    conformazionePitPprUrl
    monitoraggioUrbanisticoUrl 
    azioni {
        ...Azioni
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
    risorse(archiviata: false){
        ...Risorse
      }
    autoritaCompetenteVas{
        edges{
          node{
            ...Contatto
          }
        }
    }
    soggettiSca{
        edges{
          node{
            ...Contatto
          }
        }
    }
    autoritaIstituzionali{
                edges{
                    node{
                        ...Contatto
                    }
                }
            }
            altriDestinatari{
                edges{
                    node{
                        ...Contatto
                    }
                }
            }
    
    soggettoProponente {
      ...Contatto
    }
}
${RISORSE}
${USER}
${CONTATTO}
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