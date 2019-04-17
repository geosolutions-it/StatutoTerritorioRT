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
import {INVIO_PARERI_VAS, CONTRODEDUZIONI} from '../../graphql'
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
    controdeduzioni: (props) => (<Controdeduzioni saveMutation={CONTRODEDUZIONI} showData={false} label="Carica Files" titolo="CONTRODEDUZIONI"   tipo="controdeduzioni" {...props}/>),
    osservazioniRegione: (props) => (<OsservazioniRegione  {...props}/>),
    pianoControdedotto: (props) => (<PianoControdedotto {...props}/>),
    esitoConferenzaPaesaggistica: (props) => (<EsitoPae {...props}/>),
    revPianoPostCp: (props) => (<RevisionePianoCP {...props}/>),
    pareriAdozioneSca: (props) =>(<PareriAdozioneSCA {...props}/>),
    parereMotivatoAc: (props) =>(<ParereMotivatoAc {...props}/>),
    uploadElaboratiAdozioneVas: (props) =>(<UploadElaboratiAdozioneVAS {...props}/>)
    
    

}

