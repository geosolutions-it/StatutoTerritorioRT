/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {
    UPDATE_PIANO,
    GET_VAS,
    VAS_FILE_UPLOAD,
    DELETE_RISORSA_VAS,
    FORMAZIONE_PIANO
} from '../../graphql'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import Input from '../../components/EnhancedInput'
import {Query} from 'react-apollo'
import {showError, getInputFactory} from '../../utils'
import FileUpload from '../../components/UploadSingleFile'
/*
redazioneNormeTecnicheAttuazioneUrl
    compilazioneRapportoAmbientaleUrl
    conformazionePitPprUrl
    monitoraggioUrbanisticoUrl
*/

const getInput = getInputFactory("pianoOperativo")


const UI = ({ back, 
            piano: {codice, redazioneNormeTecnicheAttuazioneUrl, compilazioneRapportoAmbientaleUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl} = {}, 
            vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}}
            }) => {
            const rapporto = resources.filter(({node: {tipo, user = {}}}) => tipo === 'rapporto_ambientale').map(({node}) => node).shift()
        return (
            <React.Fragment>
                <ActionTitle>FORMAZIONE DEL PIANO</ActionTitle>
                <div className="p-3 m-auto">
                    L'elaborazione del Piano e del Rapporto ambientale deve tener conto di tutte le indicazioni contenute ad esempio nel provvedimento di verifica o dei pareri.
                    Per la Formazione del Piano, e la succesiva redazione del rapporto ambientale, è necessario utilizzare gli strumenti raggiungibili ai links qui di seguito.
                <div className="pl-2 py-4 d-flex flex-column">
                        <a className="d-flex text-dark" href="http://159.213.57.114/vas046021/gotoP/046021/07062018/PS191218" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide pr-1">link</i><span>Redazione norme tecniche di attuazione</span></a>
                        <a className="d-flex text-dark" href="http://159.213.57.114/vas046021/gotoP/046021/07062018/PS191218" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide pr-1">link</i><span>Compilazione del rapporto ambientale</span></a>
                        <a className="d-flex text-dark" href="http://159.213.57.114/crono046021/gotoP/046021/07062018/PS191218" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide pr-1">link</i><span>Conformazione al PIT-PPR</span></a>
                        <a className="d-flex text-dark" href="http://159.213.57.114/Database%20Strumenti%20Urbanistici.html" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide pr-1">link</i><span>Monitoraggio Urbanistico</span></a>
                </div>
                    Ogni strumento permette di redigere i documenti necessari e di registrare nel sistema, a operazione conclusa, tutte le specifiche richieste, creando una URL univoca
                    per accedere ai contenuti in lettura. Le URL devono essere copiate e inserite nei campi qui di seguito indicati. Il Rapporto Ambientale in formato PDF deve essere
                    caricato nella piattaforma utilizzando la funzione di upload
                </div>
                <h5 className="mt-4 font-weight-light">REDAZIONE NORME TECNICHE DI ATTUAZIONE</h5>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-1">URL </div>
                    <div className="col-11 ">
                        <Input placeholder="copiare la URL in questo campo" getInput={getInput(codice, "redazioneNormeTecnicheAttuazioneUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={redazioneNormeTecnicheAttuazioneUrl} type="text" />
                    </div>
                </div>
                <h5 className="mt-4 font-weight-light">COMPILAZIONE RAPPORTO AMBIENTALE</h5>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-1">URL </div>
                    <div className="col-11 ">
                        <Input placeholder="copiare la URL in questo campo" getInput={getInput(codice, "compilazioneRapportoAmbientaleUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={compilazioneRapportoAmbientaleUrl} type="text" />
                    </div>
                </div>
                <div className="action-uploader mt-5 align-self-start border-bottom border-top mb-3">
                <FileUpload 
                    className="border-0"
                    placeholder="RAPPORTO AMBIENTALE"
                    mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={rapporto} variables={{codice: uuid, tipo: "rapporto_ambientale" }}/>
                </div>

                <h5 className="mt-4 font-weight-light">CONFORMAZIONE AL PIT-PPR</h5>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-1">URL </div>
                    <div className="col-11 ">
                        <Input placeholder="copiare la URL in questo campo" getInput={getInput(codice, "conformazionePitPprUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={conformazionePitPprUrl} type="text" />
                    </div>
                </div>
                <h5 className="mt-4 font-weight-light">MONITORAGGIO URBANISTICA</h5>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-1">URL </div>
                    <div className="col-11 ">
                        <Input placeholder="copiare la URL in questo campo" getInput={getInput(codice, "monitoraggioUrbanisticoUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={monitoraggioUrbanisticoUrl} type="text" />
                    </div>
                </div>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice}} mutation={FORMAZIONE_PIANO} canCommit={!!rapporto && !!redazioneNormeTecnicheAttuazioneUrl && !!compilazioneRapportoAmbientaleUrl && !!conformazionePitPprUrl && !!monitoraggioUrbanisticoUrl}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

export default ({back, piano}) => (
        <Query query={GET_VAS} variables={{codice: piano.codice}} onError={showError}>
            {({loading, data: {procedureVas: {edges = []} = []}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI vas={edges[0]} back={back} piano={piano}/>)}
            }
        </Query>)