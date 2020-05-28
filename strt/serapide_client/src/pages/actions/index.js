import React from 'react'
// import AvvioConsultazioniSCA from "./AvvioConsultazioneSCA"
import PareriVAS from "./PareriVAS"
import ProvvedimentoVerificaVAS from './ProvvedimentoVerificaVAS'
import AvvioProcedimento from './AvvioProcedimento'
import TrasmissioneDpVerVAS from './TrasmissioneDpVerVAS'

import AvviaEsamePareri from './AvviaEsamePareri'
import PubblicazioneProvv from './PubblicazioneProvvedimento'
import RedazioneDocumentiVAS from './UploadElaboratiVAS'
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
import EsitoPae from './EsitoConferenzaPaesaggistica'
import RevisionePianoCP from './RevisionePianoPostCP'
import PareriAdozioneSCA from './PareriAdozioneSCA'
import ParereMotivatoAc from './ParereMotivatoAdozione'
import UploadElaboratiAdozioneVAS from './UploadElaboratiVASAdozione'
import Approvazione from './Approvazione'
import UploadFile from "./UploadFile"
import Pubblicazione from "./Pubblicazione"
import InvioDocPreliminare from "./InvioDocPreliminare"
import PubblicazioneBURT from './PubblicazioneBurt';
import {VAS_DOCS, ADOZIONE_DOCS, AVVIO_DOCS} from "../../utils"

import {GET_AVVIO, DELETE_RISORSA_AVVIO, 
        TRASMISSIONE_PARERI_SCA,TRASMISSIONE_PARERI_AC, CONTRODEDUZIONI,
        GET_APPROVAZIONE, APPROVAZIONE_FILE_UPLOAD, UPDATE_APPROVAZIONE,
        DELETE_RISORSA_APPROVAZIONE, ESITO_CONFERENZA_PAESAGGISTICA_AP,
        PUBBLICAZIONE_APPROVAZIONE, ATTRIBUZIONE_CONFORMITA_PIT,
        GET_PUBBLICAZIONE, UPDATE_PUBBLICAZIONE, PUBBLICAZIONE_PIANO,
        AVVIO_FILE_UPLOAD, CONTRIBUTI_TECNICI
} from 'schema'



// parametri passati di default piano, back, utente, scadenza

export default {
/************************ FASE AVVIO **********************************/
        avvioProcedimento: (props) => (<AvvioProcedimento {...props}/>),
        contributiTecnici: (props) => (<UploadFile  title="Contributi Tecnici"
                                                placeholder="Contributi Tecnici"
                                                fileType={AVVIO_DOCS.CONTRIBUTI_TECNICI}
                                                subTitle="Caricare il file dei contributi tecnici"
                                                query={GET_AVVIO} 
                                                deleteRes={DELETE_RISORSA_AVVIO} 
                                                uploadRes={AVVIO_FILE_UPLOAD}
                                                closeAction={CONTRIBUTI_TECNICI}
                                                {...props}/>),
        
        /********   PROCEDURA ORDINARIA VAS *****************/
        invioDocPreliminare: (props) => (<InvioDocPreliminare  {...props}/>),
        trasmissionePareriSca: (props) => (<PareriVAS tipo={VAS_DOCS.PAR_SCA}
                                      saveMutation={TRASMISSIONE_PARERI_SCA}
                                      tipoVas={VAS_DOCS.DOC_PRE_VAS}
                                      label="Pareri SCA"
                                      {...props}/>),
        trasmissionePareriAc: (props) => (<PareriVAS 
                                        title="Pareri Autorità Competente (AC)"
                                        tipo={VAS_DOCS.PAR_AC}
                                        saveMutation={TRASMISSIONE_PARERI_AC}
                                        tipoVas={VAS_DOCS.DOC_PRE_VAS}
                                        label="Pareri AC"
                                      {...props}/>),
        redazioneDocumentiVas: (props) => (<RedazioneDocumentiVAS {...props}/>),
        // ********** VERIFICA DI ASSOGGETTABILITA' VAS ***************
        
        trasmissioneDpvVas: (props) => (<TrasmissioneDpVerVAS {...props}/>),
        pareriVerificaSca: (props) => (<PareriVAS  {...props}/>),
        emissioneProvvedimentoVerifica: (props) => (<ProvvedimentoVerificaVAS {...props}/>),
        pubblicazioneProvvedimentoVerificaAc : (props) => (<PubblicazioneProvv {...props}/>),
        pubblicazioneProvvedimentoVerificaAp: (props) => (<PubblicazioneProvv {...props}/>),
        
        //************* ********************/
        
        avvioEsamePareriSca: (props) => (<AvviaEsamePareri {...props}/>),
        

        // *********** CONFERENZA PAESAGGISTICA ***********************
        protocolloGenioCivile: (props) => (<GenioCivile {...props}/>),
        formazioneDelPiano: (props) => (<FormazionePiano {...props}/>),
        richiestaConferenzaCopianificazione: (props) => (<RichiestaConferenza {...props}/>),
        esitoConferenzaCopianificazione: (props) => (<SvolgimentoConferenza {...props}/>),
        richiestaIntegrazioni: (props) => (<RichiestaIntegrazioni  {...props}/>),
        integrazioniRichieste: (props) => (<IntegrazioniRichieste  {...props}/>),

/**********FASE ADOZIONE ******************/
        trasmissioneAdozione: (props) => (<Adozione  {...props}/>),
        pubblicazioneBurt: (props) => (<PubblicazioneBURT  {...props}/>),
        /** Art.19 Osservazioni*/
        uploadOsservazioniPrivati: (props) => (<Osservazioni  {...props}/>),
        osservazioniEnti: (props) => (<Osservazioni hideSave={true} disableSave={true} 
                                        label="OSSERVAZIONI" titolo="Osservazioni Soggetti Istituzionali" 
                                        filterByUser={false} tipo={ADOZIONE_DOCS.OSSERVAZIONI_ENTI} {...props}/>),
        osservazioniRegione: (props) => (<OsservazioniRegione  {...props}/>),

        /** Art.19 Controdedotto*/
        controdeduzioni: (props) => (<Controdeduzioni filterByUser={false} showData={false} label="Carica Files" titolo="CONTRODEDUZIONI"  tipo={ADOZIONE_DOCS.CONTRODEDUZIONI} {...props}/>),
        pianoControdedotto: (props) => (<PianoControdedotto {...props}/>),
        
        /** Art.19 Conferenza*/
        esitoConferenzaPaesaggistica: (props) => (<EsitoPae {...props}/>),
        revPianoPostCp: (props) => (<RevisionePianoCP {...props}/>),
        
        /** VAS art. 24 e 25 */
        pareriAdozioneSca: (props) =>(<PareriAdozioneSCA {...props}/>),
        parereMotivatoAc: (props) =>(<ParereMotivatoAc {...props}/>),
        uploadElaboratiAdozioneVas: (props) => (<UploadElaboratiAdozioneVAS {...props}/>),


/**********FASE APPROVAZIONE ******************/
        
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
/************FASE PUBBLICAZIONE ******************/                                                        
        pubblicazionePiano: (props) => (<Pubblicazione title="Pubblicazione Piano"
                                                procedura="proceduraPubblicazione"
                                                query={GET_PUBBLICAZIONE}
                                                updateM={UPDATE_PUBBLICAZIONE}
                                                closeAction={PUBBLICAZIONE_PIANO}
                                                {...props}/>),
             
}

