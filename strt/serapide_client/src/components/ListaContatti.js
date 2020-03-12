/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'
import ActionSubParagraphTitle from './ActionSubParagraphTitle'



export default ({hideTitle = false, title = "SOGGETTI ISTITUZIONALI", contacts = [], icon = "bookmark"}) => (
        <React.Fragment>
            {!hideTitle && (<ActionSubParagraphTitle className="pb-1 size-13 mt-2">{title}</ActionSubParagraphTitle>)}
                <div className="d-flex flex-wrap mt-2">
                    {contacts.map(({ufficio: {nome, uuid, ente: {nome: nomeEnte}} = {}}) => (<div className="d-flex mr-2 flex-fill align-items-center size-11" key={uuid}>
                                 <i className="material-icons text-serapide icon-13">{icon}</i>
                                 {`${nomeEnte} ${nome}`}
                        </div>))}
                    </div>
        </React.Fragment>
)
