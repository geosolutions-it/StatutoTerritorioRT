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
    INVIO_PROTOCOLLO_GENIO,
    GET_AVVIO,
    GET_CONTATTI,
    AVVIO_FILE_UPLOAD,
    DELETE_RISORSA_AVVIO

} from '../../graphql'
import SalvaInvia from '../../components/SalvaInvia'
import ActionTitle from '../../components/ActionTitle'
import {toggleControllableState} from '../../enhancers/utils'
import {Query, Mutation} from 'react-apollo'
import AddContact from '../../components/AddContact'
import {EnhancedListSelector} from '../../components/ListSelector'
import {showError} from '../../utils'
import Button from '../../components/IconButton'
import {EnhancedDateSelector} from "../../components/DateSelector"
import UploadFiles from '../../components/UploadFiles'
import Input from '../../components/EnhancedInput'

const enhancer = toggleControllableState("isChecked", "toggleCheck", false)

const getInput = (codice) => (numeroProtocolloGenioCivile) => (
    {variables:{ input:{ 
    pianoOperativo: { numeroProtocolloGenioCivile}, codice}
}})
const getAuthorities = ({contatti: {edges = []} = {}} = {}) => {
    return edges.map(({node: {nome, uuid, tipologia}}) => ({label: nome, value: uuid, tipologia}))
}
const getDataDeliberaInput = (codice) => (val) => ({
    variables: {
        input: { 
            pianoOperativo: {
            dataDelibera: val.toISOString()}, 
        codice}
    }})

const getSuccess = ({uploadRisorsaAvvio: {success}} = {}) => success

const fileProps = {className: `border-0`, getSuccess, mutation: AVVIO_FILE_UPLOAD,
    resourceMutation: DELETE_RISORSA_AVVIO, disabled: false, isLocked: false}
const Messaggio = () => (<React.Fragment>
        <h4>STAI PER SALVARE INCONTRO</h4>
        <h4>IL MESSAGGIO VERRA'</h4>
        <h4>NOTIFICATO AI PARTECIPANTI</h4>
        </React.Fragment>)

const UI = enhancer(({ back, 
    piano: {numeroProtocolloGenioCivile, codice} = {}, 
    procedureAvvio: {node: {
        uuid}} = {},
        isChecked,
        toggleCheck
    }) => {
        const auths = []
        const dataDelibera = new Date().toDateString()
        const allegati = []
        return (
            <React.Fragment>
                <ActionTitle>Convocazione Conf. di copianificazione</ActionTitle>
                
                <div className="row align-items-center mt-3 pl-4 pb-4">
                    <div className="col-auto px-0">
                        <i className="material-icons p-1 rounded-pill border">person_outline</i>
                    </div>
                        <div className="col-auto">
                            <Mutation mutation={UPDATE_PIANO} onError={showError}>
                                {(onChange) => {
                                    const changed = (val) => {
                                        let autoritaIstituzionali = []
                                        if(auths.indexOf(val)!== -1){
                                            autoritaIstituzionali = auths.filter( uuid => uuid !== val)
                                        }else {
                                            autoritaIstituzionali = auths.concat(val)
                                        }
                                            onChange({variables:{ input:{ 
                                                    pianoOperativo: { autoritaIstituzionali}, codice}
                                            }})
                                    }
                                    return (
                                        <EnhancedListSelector
                                            selected={auths}
                                            query={GET_CONTATTI}
                                            getList={getAuthorities}
                                            onChange={changed}
                                            variables={{}}
                                            size="lg"
                                            label="SOGGETTI ISTITUZIONALI"
                                            btn={(toggleOpen) => (
                                                <div className="row">
                                                    <Button fontSize="60%"  classNameLabel="py-0 text-serapide" onClick={toggleOpen} className="ml-3 rounded-pill border"  color="white" icon="add" label="SELEZIONA PARTECIPANTI"/>
                                                </div>
                                                )}
                                            >
                                            <AddContact className="mt-2"></AddContact>
                                            </EnhancedListSelector>)}
                                }
                                </Mutation>
                        </div>
                    </div>
                   
                    <div className="row align-items-center mt-3 pl-4 pb-4">
                        <div className="col-auto px-0">
                            <i className="material-icons text-serapide icon-34">add_circle</i>
                        </div>
                        <h5 className="col-auto text-serapide">CREA INCONTRO</h5>
                    </div> 
                    <div className=" mt-3 px-4 pb-4 border container">
                    <div className="row pt-2">
                        <Input className="col border-bottom border-serapide bg-light border-top-0 border-left-0 border-right-0" 
                               getInput={getInput(codice)} mutation={UPDATE_PIANO} disabled={false}  
                               onChange={undefined} 
                               value={numeroProtocolloGenioCivile} type="text"
                               placeholder="Titolo Incontro" />
                    </div>
                    <div className="row pt-3">
                            <div className="col-12 pb-3 date-time-picker">
                                <EnhancedDateSelector showTimeSelect
                                useDateTime={true}
                                disabled={false}
                                selected={dataDelibera ? new Date(dataDelibera) : undefined}
                                mutation={UPDATE_PIANO} getInput={getDataDeliberaInput(codice)}/>
                            </div>
                       
                            
                            <Input  className="col-12 h-auto p-2 pl-4 mb-3 rounded-0 flex-fill p-0 m-0 bg-light" 
                               getInput={getInput(codice)} mutation={UPDATE_PIANO} disabled={false}  
                               onChange={undefined} 
                               value={numeroProtocolloGenioCivile} type="text"
                               placeholder="Luogo" />
                            
                            <Input  rows={5} className="col-12 p-2 pl-4 rounded-0 flex-fill p-0 m-0 bg-light" 
                               getInput={getInput(codice)} mutation={UPDATE_PIANO} disabled={false}  
                               onChange={undefined} 
                               value={numeroProtocolloGenioCivile}
                               placeholder="Messaggio per partecipanti" />
                             <h5 className="col-12 mt-4 pl-1 text-serapide">ALLEGATI</h5>  
                             <UploadFiles 
                                    {...fileProps}
                                    risorse={allegati} 
                                     variables={{codice: uuid, tipo: "altri_allegati_avvio" }}
                                    getFileName={({uploadRisorsaAvvio: {fileName} = {}}) => fileName}/>
                            </div>
                            <div className="col-5 offset-7  mt-7">
                            <SalvaInvia variables={{codice: uuid}} mutation={INVIO_PROTOCOLLO_GENIO} label="SALVA INCONTRO" messaggio={(<Messaggio/>)} canCommit={true}></SalvaInvia>
                            </div>
                     </div>  

                <div className="align-self-center mt-7">
                    <SalvaInvia onCompleted={back} variables={{codice: uuid}} mutation={INVIO_PROTOCOLLO_GENIO} canCommit={isChecked}></SalvaInvia>
                </div>
            </React.Fragment>)
    })

export default ({back, piano}) => (
        <Query query={GET_AVVIO} variables={{codice: piano.codice}} onError={showError}>
            {({loading, data: {procedureAvvio: {edges = []} = []} = {}, error}) => {
                if(loading) {
                    return (
                        <div className="flex-fill d-flex justify-content-center">
                            <div className="spinner-grow " role="status">
                                <span className="sr-only">Loading...</span>
                            </div>
                        </div>)
                }
                return (
                    <UI procedureAvvio={edges[0]} back={back} piano={piano}/>)}
            }
        </Query>)