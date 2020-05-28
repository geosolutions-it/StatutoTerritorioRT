
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



export const View = ({soggettiOperanti = [], useIcon = false, containerClass="col-6 pt-3 mb-3", titleClass="mb-3", elementClass="col-12 px-0 py-1"}) => {
    const soggetti = getSoggettiIsti(soggettiOperanti);
    return (
        <div className={containerClass}><div className={titleClass}>SOGGETTI ISTITUZIONALI</div>
                {soggetti.length > 0 ? soggetti.map(({qualificaUfficio: {ufficio: {nome, uuid, ente: {nome: nomeEnte}} = {}} = {}}) => (
                        <div className={useIcon ? "d-flex align-items-center " + elementClass : elementClass} key={uuid}>
                            {useIcon && <i className="material-icons text-serapide">bookmark</i>}    
                            {`${nomeEnte} ${nome}`}
                        </div>)) : <div className={elementClass}>Nessun soggetto selezionato</div>}
        </div>);
    }

export const List = ({soggettiOperanti = [], title="SOGGETTI ISTITUZIONALI"})  => {
        return (
            <Li 
                title={title}
                contacts={getSoggettiIsti(soggettiOperanti).map(({qualificaUfficio} = {}) => (qualificaUfficio))}/>
            );
        };