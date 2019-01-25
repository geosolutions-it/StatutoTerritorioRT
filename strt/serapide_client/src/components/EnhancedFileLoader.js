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
import FileLoader from "./FileLoader"

export default ({mutation, refatchQueries, update, variables, file, placeholder, onAbort, ...mutationProps}) => (
            <Mutation mutation={mutation} refetchQueries={refatchQueries} update={update} {...mutationProps}>
                    {(upload, m_props) => {
                        const {error, data: {upload: res} = {}, loading} = m_props
                        const hasError = !loading && ((res && !res.success) || !!error )
                        if (error && !loading) {
                            toast.error(error.message,  {autoClose: true})
                        }else if(!loading && res && !res.success) {
                            toast.error("Impossibile uplodare il file",  {autoClose: true})
                            
                        }
                        return (
                            <FileLoader
                                isLoading={loading} 
                                file={file}
                                placeholder={placeholder}
                                upload={upload}
                                variables={variables}
                                error={hasError}
                                onAbort={onAbort}/>)
                    }}
                </Mutation>
)