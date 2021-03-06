/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Query, Mutation} from 'react-apollo'

import SalvaInvia from 'components/SalvaInvia'
import ActionTitle from 'components/ActionTitle'
import Button from 'components/IconButton'
import {EnhancedDateSelector} from "components/DateSelector"
import UploadFiles from 'components/UploadFiles'
import Input from 'components/EnhancedInput'
// import AddContact from 'components/AddContact'
import Spinner from 'components/Spinner'
import {EnhancedListSelector} from 'components/ListSelector'

import {compose} from 'recompose'
import {toggleControllableState, rebuildTooltip} from 'enhancers'
import {showError, getCodice, getContatti, getSoggettiIsti, SOGGETTI_ISTITUZIONALI} from 'utils'

import {
    UPDATE_PIANO,
    INVIO_PROTOCOLLO_GENIO,
    GET_AVVIO,
    GET_CONTATTI,
    AVVIO_FILE_UPLOAD,
    DELETE_RISORSA_AVVIO

} from 'schema'

const enhancer = compose(rebuildTooltip(), toggleControllableState("isChecked", "toggleCheck", false))

const  getPianoInput = (codice, field) => (val) => ({
    variables: {
        input: {
            pianoOperativo: { [field]:  val },
            codice
        }
    }
})


const getDataDeliberaInput = (codice) => (val) => ({
    variables: {
        input: {
            pianoOperativo: {
            dataDelibera: val.toISOString()},
        codice}
    }})

const fileProps = {className: `border-0`, mutation: AVVIO_FILE_UPLOAD,
    resourceMutation: DELETE_RISORSA_AVVIO, disabled: false, isLocked: false}

const Messaggio = () => (<React.Fragment>
        <h4>STAI PER SALVARE INCONTRO</h4>
        <h4>IL MESSAGGIO VERRA'</h4>
        <h4>NOTIFICATO AI PARTECIPANTI</h4>
        </React.Fragment>)

const UI = enhancer(({ back,
    piano: {
        numeroProtocolloGenioCivile, codice,
        soggettiOperanti
    
    } = {},
    proceduraAvvio: {node: {
        uuid}} = {},
        isChecked,
        toggleCheck
    }) => {
        const si = getSoggettiIsti(soggettiOperanti).map(({qualificaUfficio} = {}) => (qualificaUfficio))
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
                                    const changed = (val, {tipologia: qualifica, uuid}) => {
                                        let newSO = soggettiOperanti.map(({qualificaUfficio: {qualifica, ufficio: {uuid: ufficioUuid} = {}} = {}} = {}) => ({qualifica, ufficioUuid}))
                                        newSO = newSO.filter(({ufficioUuid}) => ufficioUuid !== uuid)
                                        if (newSO.length === soggettiOperanti.length) {
                                                newSO = newSO.concat({qualifica, ufficioUuid: uuid})
                                            }
                                        onChange({variables:{ input:{
                                                    pianoOperativo: { soggettiOperanti: newSO}, codice}
                                            }})
                                    }
                                    return (
                                        <EnhancedListSelector
                                            selected={si.map(({ufficio: {uuid} = {}}) => uuid)}
                                            query={GET_CONTATTI}
                                            getList={getContatti}
                                            onChange={changed}
                                            variables={{tipo: SOGGETTI_ISTITUZIONALI}}
                                            size="lg"
                                            label="SOGGETTI ISTITUZIONALI"
                                            btn={(toggleOpen) => (
                                                <div className="row">
                                                    <Button fontSize="60%"  classNameLabel="py-0 text-serapide" onClick={toggleOpen} className="ml-3 rounded-pill border"  color="white" icon="add" label="SELEZIONA PARTECIPANTI"/>
                                                </div>
                                                )}
                                            >
                                            {/*<AddContact className="mt-2"></AddContact>*/}
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
                               getInput={getPianoInput(codice, "numeroProtocolloGenioCivile")} mutation={UPDATE_PIANO} disabled={false}
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
                               getInput={getPianoInput(codice, "numeroProtocolloGenioCivile")} mutation={UPDATE_PIANO} disabled={false}
                               onChange={undefined}
                               value={numeroProtocolloGenioCivile} type="text"
                               placeholder="Luogo" />

                            <Input  rows={5} className="col-12 p-2 pl-4 rounded-0 flex-fill p-0 m-0 bg-light"
                               getInput={getPianoInput(codice, "numeroProtocolloGenioCivile")} mutation={UPDATE_PIANO} disabled={false}
                               onChange={undefined}
                               value={numeroProtocolloGenioCivile}
                               placeholder="Messaggio per partecipanti" />
                             <h5 className="col-12 mt-4 pl-1 text-serapide">ALLEGATI</h5>
                             <UploadFiles
                                    {...fileProps}
                                    risorse={allegati}
                                    variables={{codice: uuid, tipo: "altri_allegati_avvio" }}
                                    />
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

export default (props) => (
        <Query query={GET_AVVIO} variables={{codice: getCodice(props)}} onError={showError}>
            {({loading, data: {modello: {edges: [proceduraAvvio] = []} = {}} = {}, error}) => {
                if(loading) {
                    return <Spinner/>
                }
                return (
                    <UI {...props} proceduraAvvio={proceduraAvvio}/>)}
            }
        </Query>)
