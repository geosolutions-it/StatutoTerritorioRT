/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query} from 'react-apollo'

import {EnhancedSwitch} from 'components/Switch'
import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import ActionParagraphTitle from 'components/ActionParagraphTitle'
import ActionSubParagraphTitle from 'components/ActionSubParagraphTitle'
import Spinner from 'components/Spinner'

import  {showError, getInputFactory, getCodice} from 'utils'
import {rebuildTooltip} from 'enhancers'

import {GET_ADOZIONE,
    UPDATE_ADOZIONE,
    OSSERVAZIONI_REGIONE
} from 'schema'

const getInput = getInputFactory("proceduraAdozione")

const UI = rebuildTooltip()(({
    back, 
    proceduraAdozione: { node: {uuid, osservazioniConcluse} = {}},
    piano: {
        conformazionePitPprUrl
        }
    }) => {
        return (
            <React.Fragment>
                <ActionTitle>Osservazione della Regione Toscana</ActionTitle>
                <ActionParagraphTitle fontWeight="font-weight-light">Redazione delle Osservazioni</ActionParagraphTitle>
                <div className="pt-3 text-justify size-13">
                    
                        {`Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras venenatis risus quis blandit feugiat.
                        Nunc pulvinar auctor sapien, a tincidunt nunc dignissim id. Fusce facilisis augue vel imperdiet molestie.
                        Nulla a nisl metus. In vel sapien vel lacus finibus malesuada eget et mi.
                        Praesent scelerisque dapibus tortor, a iaculis diam eleifend ac.  `}
                </div>
                <ActionSubParagraphTitle>CONFORMAZIONE AL PIT</ActionSubParagraphTitle>
                <div className="mt-2 pb-2 row d-flex border-bottom">
                    <div className="col-12 align-items-center d-flex">
                        <i className="material-icons icon-15 text-serapide">link</i><a href={conformazionePitPprUrl} target="_balnk" className="pl-1 text-serapide size-12  pointer">{conformazionePitPprUrl}</a>
                    </div>
                </div>
                <div className="pt-3 text-justify size-13">
                        {`Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras venenatis risus quis blandit feugiat.
                        Nunc pulvinar auctor sapien, a tincidunt nunc dignissim id. Fusce facilisis augue vel imperdiet molestie.
                        Nulla a nisl metus. In vel sapien vel lacus finibus malesuada eget et mi.
                        Praesent scelerisque dapibus tortor, a iaculis diam eleifend ac.  `}
                </div>
                
                <EnhancedSwitch 
                ignoreChecked
                value={!osservazioniConcluse}
                labelClassName="col-auto text-serapide"
                className="switch-small mt-4"
                checked={osservazioniConcluse}
                label="OSSERVAZIONI CONCLUSE"
                mutation={UPDATE_ADOZIONE} getInput={getInput(uuid, "osservazioniConcluse")}></EnhancedSwitch>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia fontSize="size-8" onCompleted={back} variables={{codice: uuid}} mutation={OSSERVAZIONI_REGIONE} canCommit={osservazioniConcluse}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default (props) => (
    <Query query={GET_ADOZIONE} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [proceduraAdozione]= []} = []} = {}}) => {
            if(loading) {
                return <Spinner/>
            }
            return (
                <UI {...props} proceduraAdozione={proceduraAdozione} />)}
        }
    </Query>)
        