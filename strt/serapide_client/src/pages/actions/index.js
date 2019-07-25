import React from 'react'
import AvvioConsultazioniSCA from "./AvvioConsultazioneSCA"
import PareriSCA from "./PareriSCA"
import ProvvedimentoVerificaVAS from './ProvvedimentoVerificaVAS'
import AvvioProcedimento from './AvvioProcedimento'

import AvviaEsamePareri from './AvviaEsamePareri'
import PubblicazioneProvv from './PubblicazioneProvvedimento'
import UploadElaboratiVAS from './UploadElaboratiVAS'
import GenioCivile from './GenioCivile'
import FormazionePiano from './FormazionePiano'
import RichiestaConferenza from './RichiestaConferenza'
import IntegrazioniRichieste from './IntegrazioniRichieste'
import SvolgimentoConferenza from './SvolgimentoConfernza'
import RichiestaIntegrazioni from './RichiestaIntegrazioni'

import Adozione from './Adozione'
import Osservazioni from './Osservazioni'
import OsservazioniRegione from './OsservazioniRegione'
import PianoControdedotto from './PianoControdedotto'
import Controdeduzioni from './Controdeduzioni'
import EsitoPae from './EsitoConferenzaPaeseggistica'
import RevisionePianoCP from './RevisionePianoPostCP'
import PareriAdozioneSCA from './PareriAdozioneSCA'
import ParereMotivatoAc from './ParereMotivatoAdozione'
import UploadElaboratiAdozioneVAS from './UploadElaboratiVASAdozione'
import Approvazione from './Approvazione'
import UploadFile from "./UploadFile"
import Pubblicazione from "./Pubblicazione"

import {INVIO_PARERI_VAS, CONTRODEDUZIONI,
        GET_APPROVAZIONE, APPROVAZIONE_FILE_UPLOAD, UPDATE_APPROVAZIONE,
        DELETE_RISORSA_APPROVAZIONE, ESITO_CONFERENZA_PAESAGGISTICA_AP,
        PUBBLICAZIONE_APPROVAZIONE, ATTRIBUZIONE_CONFORMITA_PIT,
        GET_PUBBLICAZIONE, UPDATE_PUBBLICAZIONE, PUBBLICAZIONE_PIANO,
        AVVIO_FILE_UPLOAD, CONTRIBUTI_TECNICI
} from 'schema'
import { GET_AVVIO, DELETE_RISORSA_AVVIO } from '../../graphql/index';


// parametri passati di default piano, back, utente, scadenza

export default {
    avvioConsultazioniSca: (props) => (<AvvioConsultazioniSCA {...props}/>),
    pareriVerificaSca: (props) => (<PareriSCA  {...props}/>),
    pareriSca: (props) => (<PareriSCA tipo="parere_sca"
                                      saveMutation={INVIO_PARERI_VAS}
                                      tipoVas="documento_preliminare_vas"
                                      label="Pareri SCA"
                                      {...props}/>),
    emissioneProvvedimentoVerifica: (props) => (<ProvvedimentoVerificaVAS {...props}/>),
    pubblicazioneProvvedimentoVerifica: (props) => (<PubblicazioneProvv {...props}/>),
    avvioProcedimento: (props) => (<AvvioProcedimento {...props}/>),
    avvioEsamePareriSca: (props) => (<AvviaEsamePareri {...props}/>),
    uploadElaboratiVas: (props) => (<UploadElaboratiVAS {...props}/>),
    protocolloGenioCivileId: (props) => (<GenioCivile {...props}/>),
    formazioneDelPiano: (props) => (<FormazionePiano {...props}/>),
    richiestaConferenzaCopianificazione: (props) => (<RichiestaConferenza {...props}/>),
    esitoConferenzaCopianificazione: (props) => (<SvolgimentoConferenza {...props}/>),
    richiestaIntegrazioni: (props) => (<RichiestaIntegrazioni  {...props}/>),
    integrazioniRichieste: (props) => (<IntegrazioniRichieste  {...props}/>),
    trasmissioneAdozione: (props) => (<Adozione  {...props}/>),
    uploadOsservazioniPrivati: (props) => (<Osservazioni  {...props}/>),
    osservazioniEnti: (props) => (<Osservazioni hideSave={true} disableSave={true} label="OSSERVAZIONI" titolo="Osservazioni Ente"  filterByUser={false} tipo="osservazioni_enti" {...props}/>),
    controdeduzioni: (props) => (<Controdeduzioni filterByUser={false} saveMutation={CONTRODEDUZIONI} showData={false} label="Carica Files" titolo="CONTRODEDUZIONI"   tipo="controdeduzioni" {...props}/>),
    osservazioniRegione: (props) => (<OsservazioniRegione  {...props}/>),
    pianoControdedotto: (props) => (<PianoControdedotto {...props}/>),
    esitoConferenzaPaesaggistica: (props) => (<EsitoPae {...props}/>),
    revPianoPostCp: (props) => (<RevisionePianoCP {...props}/>),
    pareriAdozioneSca: (props) =>(<PareriAdozioneSCA {...props}/>),
    parereMotivatoAc: (props) =>(<ParereMotivatoAc {...props}/>),
    uploadElaboratiAdozioneVas: (props) => (<UploadElaboratiAdozioneVAS {...props}/>),
    trasmissioneApprovazione: (props) => (<Approvazione {...props}/>),
    esitoConferenzaPaesaggisticaAp: (props) => (<EsitoPae getM={GET_APPROVAZIONE}
                                                          saveM={ESITO_CONFERENZA_PAESAGGISTICA_AP}
                                                          uploadM={APPROVAZIONE_FILE_UPLOAD}
                                                          deleteM={DELETE_RISORSA_APPROVAZIONE}
                                                          {...props}/>),
    pubblicazioneApprovazione: (props) => (<Pubblicazione 
                                        title="Pubblicazione Approvazione"
                                        query={GET_APPROVAZIONE}
                                        closeAction={PUBBLICAZIONE_APPROVAZIONE}
                                        updateM={UPDATE_APPROVAZIONE}
                                        {...props}/>),
    attribuzioneConformitaPit: (props) => (<UploadFile  title="Conformità PIT"
                                                        placeholder="Documento di conformità Pit"
                                                        fileType="conformita-pit"
                                                        subTitle="Caricare il file di conformità"
                                                        query={GET_APPROVAZIONE} 
                                                        deleteRes={DELETE_RISORSA_APPROVAZIONE} 
                                                        uploadRes={APPROVAZIONE_FILE_UPLOAD}
                                                        closeAction={ATTRIBUZIONE_CONFORMITA_PIT}
                                                        {...props}/>),
   pubblicazionePiano: (props) => (<Pubblicazione title="Pubblicazione Piano"
                                                procedura="proceduraPubblicazione"
                                                query={GET_PUBBLICAZIONE}
                                                updateM={UPDATE_PUBBLICAZIONE}
                                                closeAction={PUBBLICAZIONE_PIANO}
                                                {...props}/>),
    contributiTecnici: (props) => (<UploadFile  title="Contributi Tecnici"
        placeholder="Contributi Tecnici"
        fileType="contributi_tecnici"
        subTitle="Caricare il file dei contributi tecnici"
        query={GET_AVVIO} 
        deleteRes={DELETE_RISORSA_AVVIO} 
        uploadRes={AVVIO_FILE_UPLOAD}
        closeAction={CONTRIBUTI_TECNICI}
        {...props}/>),
    
}

