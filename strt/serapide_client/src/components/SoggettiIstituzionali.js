
/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import  {getSoggettiIsti} from 'utils'
import Li from './ListaContatti'; 

export const View = ({soggettiOperanti = [], containerClass="col-6 pt-3 mb-3", titleClass="mb-3", elementClass="col-12 px-0 py-1"}) => {
    return (
        <div className={containerClass}><div className={titleClass}>SOGGETTI ISTITUZIONALI</div>
                {getSoggettiIsti(soggettiOperanti).map(({qualificaUfficio: {ufficio: {nome, uuid, ente: {nome: nomeEnte}} = {}} = {}}) => (
                        <div className={elementClass} key={uuid}>
                                 {`${nomeEnte} ${nome}`}
                        </div>))}
        </div>);
    }

    export const List = ({soggettiOperanti = []}, title="SOGGETTI ISTITUZIONALI")  => (
        <Li 
            title={title}
            contacts={getSoggettiIsti(soggettiOperanti).map(({qualificaUfficio} = {}) => (qualificaUfficio))}/>
        );