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
import ActionSubParagraphTitle from 'components/ActionSubParagraphTitle'
import Spinner from 'components/Spinner'
import FileUpload from 'components/UploadSingleFile'

import {rebuildTooltip} from 'enhancers'
import {showError, getCodice} from 'utils'

import {
    GET_VAS,
    FILE_UPLOAD,
    DELETE_RISORSA,
    FORMAZIONE_PIANO
} from 'schema'



const UI = rebuildTooltip()(({ back, 
            piano: {codice, redazioneNormeTecnicheAttuazioneUrl, compilazioneRapportoAmbientaleUrl, conformazionePitPprUrl, monitoraggioUrbanisticoUrl, risorse : {edges: resources = []}} = {}
            }) => {
            const norme = resources.filter(({node: {tipo, user = {}}}) => tipo === 'norme_tecniche_attuazione').map(({node}) => node).shift()
        return (
            <React.Fragment>
                <ActionTitle>Formazione del Piano</ActionTitle>                
                {/* <ActionParagraphTitle>Per la redazione della Disciplina del Piano è suggerito l'utilizzo del software "Redazione Norme"</ActionParagraphTitle> */}
                <ActionSubParagraphTitle>Per la redazione della Disciplina del Piano è suggerito l'utilizzo del software "Redazione Norme"</ActionSubParagraphTitle>
                <div className="action-uploader py-1 mt-3 align-self-start border-bottom">
                <FileUpload 
                    iconSize="icon-15" fontSize="size-11" vertical useLabel
                    className="border-0"
                    placeholder="DISCIPLINA DEL PIANO"
                    mutation={FILE_UPLOAD} 
                    resourceMutation={DELETE_RISORSA} disabled={false} 
                    isLocked={false} risorsa={norme} variables={{codice, tipo: "norme_tecniche_attuazione" }}/>
                </div>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice}} mutation={FORMAZIONE_PIANO} canCommit={!!norme}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
        <Query query={GET_VAS} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [vas]= []} = {}}}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} vas={vas} />)}
            }
        </Query>)