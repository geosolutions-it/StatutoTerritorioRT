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


const showError = (error, onError) => {
    if (error && error.message.indexOf("Operation canceled") === -1) {
        toast.error(error.message,  {autoClose: true})
    }
} 
export default ({mutation, update, variables, file, placeholder, onAbort, renderChooser, ...mutationProps}) => (
            <Mutation mutation={mutation} update={update} onError={showError} {...mutationProps}>
                    {(upload, m_props) => {
                        const {error, data: {upload: res} = {}, loading} = m_props
                        const hasError = !loading && ((res && !res.success) || !!error )
                        if(!loading && res && !res.success) {
                            showError({message:"Impossibile uplodare il file"});
                        }
                        return (
                            <React.Fragment>
                            <FileLoader
                                isLoading={loading} 
                                file={file}
                                placeholder={placeholder}
                                upload={upload}
                                variables={variables}
                                error={hasError}
                                onAbort={onAbort}/>
                            {renderChooser && renderChooser(loading)}
                            </React.Fragment>)

                    }}
                </Mutation>
)