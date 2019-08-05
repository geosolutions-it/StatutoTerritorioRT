/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionParagraphTitle from 'components/ActionParagraphTitle'

import Input from 'components/EnhancedInput'
import FileUpload from 'components/UploadSingleFile'

import {rebuildTooltip} from 'enhancers'
import {showError, getCodice} from 'utils'

import {
    UPDATE_PIANO,
    GET_VAS,
    VAS_FILE_UPLOAD,
    DELETE_RISORSA_VAS,
    FORMAZIONE_PIANO
} from 'schema'

const getInput = (codice, field) => (val) => ({
    variables: {
        input: { 
            pianoOperativo: { [field]:  val }, 
            codice
        }
    }
})


const UI = rebuildTooltip()(({ back, 
            piano: {codice, redazioneNormeTecnicheAttuazioneUrl, compilazioneRapportoAmbientaleUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl} = {}, 
            vas: { node: {uuid, risorse : {edges: resources = []} = {}} = {}}
            }) => {
            const rapporto = resources.filter(({node: {tipo, user = {}}}) => tipo === 'rapporto_ambientale').map(({node}) => node).shift()
        return (
            <React.Fragment>
                <ActionTitle>Formazione del Piano</ActionTitle>
                <div className="pt-3 text-justify size-13">
                    L'elaborazione del Piano e del Rapporto ambientale deve tener conto di tutte le indicazioni contenute ad esempio nel provvedimento di verifica o dei pareri.
                    Per la Formazione del Piano, e la succesiva redazione del rapporto ambientale, è necessario utilizzare gli strumenti raggiungibili ai links qui di seguito.
                <div className="pl-2 py-4 d-flex flex-column">
                        <a className="d-flex size-13 text-dark align-items-center" href="http://159.213.57.114/vas046021/gotoP/046021/07062018/PS191218" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide icon-15 pr-1">link</i><span>Redazione norme tecniche di attuazione</span></a>
                        <a className="d-flex size-13 text-dark align-items-center" href="http://159.213.57.114/vas046021/gotoP/046021/07062018/PS191218" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide icon-15 pr-1">link</i><span>Compilazione del rapporto ambientale</span></a>
                        <a className="d-flex size-13 text-dark align-items-center" href="http://159.213.57.114/crono046021/gotoP/046021/07062018/PS191218" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide icon-15 pr-1">link</i><span>Conformazione al PIT-PPR</span></a>
                        <a className="d-flex size-13 text-dark align-items-center" href="http://159.213.57.114/Database%20Strumenti%20Urbanistici.html" target="_blank" rel="noopener noreferrer"><i className="material-icons text-serapide icon-15 pr-1">link</i><span>Monitoraggio Urbanistico</span></a>
                </div>
                    Ogni strumento permette di redigere i documenti necessari e di registrare nel sistema, a operazione conclusa, tutte le specifiche richieste, creando una URL univoca
                    per accedere ai contenuti in lettura. Le URL devono essere copiate e inserite nei campi qui di seguito indicati. Il Rapporto Ambientale in formato PDF deve essere
                    caricato nella piattaforma utilizzando la funzione di upload
                </div>
                <ActionParagraphTitle>REDAZIONE NORME TECNICHE DI ATTUAZIONE</ActionParagraphTitle>
                <div className="my-3 row d-flex align-items-center">
                    <div className="col-1 size-12">URL </div>
                    <div className="col-11 ">
                        <Input className="size-10" placeholder="copiare la URL in questo campo" getInput={getInput(codice, "redazioneNormeTecnicheAttuazioneUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={redazioneNormeTecnicheAttuazioneUrl} type="text" />
                    </div>
                </div>
                <ActionParagraphTitle>COMPILAZIONE RAPPORTO AMBIENTALE</ActionParagraphTitle>
                <div className="my-3 row d-flex align-items-center">
                    <div className="col-1 size-12">URL </div>
                    <div className="col-11 ">
                        <Input className="size-10"  placeholder="copiare la URL in questo campo" getInput={getInput(codice, "compilazioneRapportoAmbientaleUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={compilazioneRapportoAmbientaleUrl} type="text" />
                    </div>
                </div>

                <div className="action-uploader py-1 mt-3 align-self-start border-bottom">
                <FileUpload 
                    iconSize="icon-15" fontSize="size-11" vertical useLabel
                    className="border-0"
                    placeholder="RAPPORTO AMBIENTALE"
                    mutation={VAS_FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA_VAS} disabled={false} 
                    isLocked={false} risorsa={rapporto} variables={{codice: uuid, tipo: "rapporto_ambientale" }}/>
                </div>

                <ActionParagraphTitle>CONFORMAZIONE AL PIT-PPR</ActionParagraphTitle>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-1 size-12">URL </div>
                    <div className="col-11 ">
                        <Input className="size-10" placeholder="copiare la URL in questo campo" getInput={getInput(codice, "conformazionePitPprUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={conformazionePitPprUrl} type="text" />
                    </div>
                </div>
                <ActionParagraphTitle>MONITORAGGIO URBANISTICA</ActionParagraphTitle>
                <div className="mt-2 row d-flex align-items-center">
                    <div className="col-1 size-12">URL </div>
                    <div className="col-11 ">
                        <Input className="size-10" placeholder="copiare la URL in questo campo" getInput={getInput(codice, "monitoraggioUrbanisticoUrl")} mutation={UPDATE_PIANO} disabled={false}  onChange={undefined} value={monitoraggioUrbanisticoUrl} type="text" />
                    </div>
                </div>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice}} mutation={FORMAZIONE_PIANO} canCommit={!!rapporto && !!redazioneNormeTecnicheAttuazioneUrl && !!compilazioneRapportoAmbientaleUrl && !!conformazionePitPprUrl && !!monitoraggioUrbanisticoUrl}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
        <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vas]= []} = {}}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI {...props} vas={vas} />)}
            }
        </Query>)