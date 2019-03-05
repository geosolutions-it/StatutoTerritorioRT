

/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Mutation} from 'react-apollo'
import {toggleControllableState} from '../enhancers/utils'
import {showError}  from "../utils"
import Button from './IconButton'
import {Modal, ModalBody, ModalHeader} from 'reactstrap'
const enhancer = toggleControllableState("isOpen", "toggleOpen", false)

export default enhancer(({mutation, variables, toggleOpen, isOpen, canCommit = false}) => (

            <Mutation mutation={mutation} onError={showError}>
                    {(onConfirm, {loading}) => {
                        const updatePiano = () => {onConfirm({variables})}
                      return (
                        <React.Fragment>
                            <Button isLoading={loading} onClick={toggleOpen} className="my-auto text-uppercase" disabled={!canCommit} color="serapide"  label="SALVA ED INVIA"></Button>
                            {isOpen && (
                                <Modal isOpen={isOpen} centered size="md" wrapClassName="serapide" autoFocus={true}>
                                    <ModalHeader className="d-flex justify-content-center"><i className="material-icons text-serapide icon-34">notifications_active</i></ModalHeader>
                                    <ModalBody className="d-flex justify-content-center flex-column pt-0 px-5 pb-5  align-items-center justify-item-center">
                                        
                                        <h4>STAI PER INVIARE I DOCUMENTI</h4>
                                        <h4> AL SISTEMA</h4>
                                        <div style={{minWidth: 200}} className="pt-5 d-flex justify-content-around">
                                            <Button label="ANNULLA" color="serapide" disabled={loading}  onClick={toggleOpen}></Button>
                                            <Button label="SALVA" isLoading={loading} disabled={loading} color="serapide" onClick={updatePiano}></Button>
                                        </div>
                                    </ModalBody>
                                </Modal>)}
                        </React.Fragment>)
                    }}
                    </Mutation>
))