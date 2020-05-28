/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionSubParagraphTitle from 'components/ActionSubParagraphTitle'

import FileUpload from 'components/UploadSingleFile'

import {rebuildTooltip} from 'enhancers'
import {AVVIO_DOCS, getResourceByType} from 'utils'

import {
    
    FILE_UPLOAD,
    DELETE_RISORSA,
    FORMAZIONE_PIANO
} from 'schema'



const UI = rebuildTooltip()(({ back, 
            piano: {codice, risorse : {edges: resources = []}} = {}
            }) => {
            const norme = getResourceByType(resources, AVVIO_DOCS.NORME_TECNICHE_ATTUAZIONE)
        return (
            <React.Fragment>
                <ActionTitle>Formazione del Piano</ActionTitle>
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

export default (props) => (<UI {...props}/>)