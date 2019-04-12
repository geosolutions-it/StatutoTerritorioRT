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
import {INVIO_PARERI_VAS} from '../../queries'
import Adozione from './Adozione'
import Osservazioni from './Osservazioni'
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
    avvioEsamePareri_sca: (props) => (<AvviaEsamePareri {...props}/>),
    uploadElaboratiVas: (props) => (<UploadElaboratiVAS {...props}/>),
    protocolloGenioCivileId: (props) => (<GenioCivile {...props}/>),
    formazioneDelPiano: (props) => (<FormazionePiano {...props}/>),
    richiestaConferenzaCopianificazione: (props) => (<RichiestaConferenza {...props}/>),
    esitoConferenzaCopianificazione: (props) => (<SvolgimentoConferenza {...props}/>),
    richiestaIntegrazioni: (props) => (<RichiestaIntegrazioni  {...props}/>),
    integrazioniRichieste: (props) => (<IntegrazioniRichieste  {...props}/>),
    trasmissioneAdozione: (props) => (<Adozione  {...props}/>),
    osservazioniPrivati: (props) => (<Osservazioni  {...props}/>),
    osservazioniEnti: (props) => (<Osservazioni label="OSSERVAZIONI" titolo="Osservazioni Ente"  filterByUser={false} tipo="osservazioni_enti" {...props}/>)
}