/*
 * Copyright 2018, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


const OneWord = (word, className, dataTip, dataTipDisable) => (
        <span className={`text-nowrap ${className}`}>
            {word[0]}<i data-tip={dataTip} data-tip-disable={dataTipDisable} className="material-icons text-serapide align-top icon-12">info</i>
        </span>)
const ManyWords = (words, className, dataTip, dataTipDisable) => (
    <span className={className}>
        {words.slice(0, -1).join(" ")}
        <span className="text-nowrap">
            {" "}
            {words.slice(-1)}<i data-tip={dataTip} data-tip-disable={dataTipDisable} className="material-icons text-serapide align-top icon-12">info</i>
        </span>
    </span>
)
const getComp = (words = "", className, dataTip = "", dataTipDisable) => (words.length > 1 ? ManyWords(words, className, dataTip, dataTipDisable) : OneWord(words, className, dataTip, dataTipDisable))
export default ({dataTip, dataTipDisable, text = "", className}) => {
    const words = text.replace(/ +(?= )/g,'').split(" ")
    return text ? getComp(words, className, dataTip, dataTipDisable) : (<i data-tip={dataTip} data-tip-disable={dataTipDisable} className="material-icons text-serapide align-top icon-12">info</i>)
}