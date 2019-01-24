/*
 * Copyright 2019, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import {Mutation} from  "react-apollo"
import { toast } from 'react-toastify'
import Risorsa from "./Resource"
import {DELETE_RISORSA} from "../queries"

export default ({ resource, codice, isLocked, mutation = DELETE_RISORSA, ...mutationProps}) => (
            <Mutation mutation={mutation} {...mutationProps}>
                    {(deleteResource, m_props) => {
                        const {error, data: {deleteRisorsa: res} = {}, loading} = m_props
                        if (error && !loading) {
                            toast.error(error.message,  {autoClose: true})
                        }else if(!loading && res && !res.success) {
                            toast.error("Impossibile eliminare la risorsa ",  {autoClose: true})
                        }
                        return (
                            <Risorsa isLoading={loading} onDeleteResource={deleteResource} resource={resource} codice={codice} isLocked={false}/>)
                    }}
            </Mutation>
)