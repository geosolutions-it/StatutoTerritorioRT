/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {EnhancedSwitch} from '../../components/Switch'
import {Query} from 'react-apollo'

import {GET_ADOZIONE,
    UPDATE_ADOZIONE,
    TRASMISSIONE_OSSERVAZIONI
} from '../../graphql'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import  {showError, getInputFactory} from '../../utils'

const getInput = getInputFactory("proceduraAdozione")

const UI = ({
    back, 
    proceduraAdozione: { node: {uuid, osservazioniConcluse} = {}},
    piano: {
        conformazionePitPprUrl
        }
    }) => {
        console.log(osservazioniConcluse)
        return (
            <React.Fragment>
                <ActionTitle>Osservazione della Regione Toscana</ActionTitle>
                <h6 className="pt-3 font-weight-light">Redazione delle Osservazioni</h6>
                <div className="row">
                    <div className="col-12 pt-2">
                        {`Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras venenatis risus quis blandit feugiat.
                        Nunc pulvinar auctor sapien, a tincidunt nunc dignissim id. Fusce facilisis augue vel imperdiet molestie.
                        Nulla a nisl metus. In vel sapien vel lacus finibus malesuada eget et mi.
                        Praesent scelerisque dapibus tortor, a iaculis diam eleifend ac.  `}
                    </div> 
                </div>
                <div className="mt-3 pb-2 row d-flex align-items-center border-bottom">
                    <div className="col-12 d-flex">
                        <i className="material-icons text-serapide">link</i><a href={conformazionePitPprUrl} target="_balnk" className="pl-1 text-serapide pointer">{conformazionePitPprUrl}</a>
                    </div>
                </div>
                <div className="mt-4 row">
                    <div className="col-12 pt-2">
                        {`Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras venenatis risus quis blandit feugiat.
                        Nunc pulvinar auctor sapien, a tincidunt nunc dignissim id. Fusce facilisis augue vel imperdiet molestie.
                        Nulla a nisl metus. In vel sapien vel lacus finibus malesuada eget et mi.
                        Praesent scelerisque dapibus tortor, a iaculis diam eleifend ac.  `}
                    </div> 
                </div>
                
                <EnhancedSwitch 
                ignoreChecked
                value={osservazioniConcluse}
                labelClassName="col-auto text-serapide"
                className="mt-3"
                checked={osservazioniConcluse}
                label="OSSERVAZIONI CONCLUSE"
                mutation={UPDATE_ADOZIONE} getInput={getInput(uuid, "osservazioniConcluse")}></EnhancedSwitch>
                
                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={TRASMISSIONE_OSSERVAZIONI} canCommit={true}></SalvaInvia>
                </div>
            </React.Fragment>)
    }

    export default ({piano = {}, back}) => (
        <Query query={GET_ADOZIONE} variables={{codice: piano.codice}} onError={showError}>
             {({loading, data: {procedureAdozione: {edges = []} = []} = {}}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI back={back} proceduraAdozione={edges[0]} piano={piano} />)}
            }
        </Query>)