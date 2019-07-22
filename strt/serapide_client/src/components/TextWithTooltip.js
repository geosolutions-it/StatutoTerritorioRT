/*
 * Copyright 2019, GeoSolutions SAS.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react'


const OneWord = (word, className, dataTip, dataTipDisable, color) => (
        <span className={`text-nowrap ${className}`}>
            {word[0]}<i data-tip={dataTip} data-tip-disable={dataTipDisable} className={`material-icons text-${color} align-top icon-12`}>info</i>
        </span>)
const ManyWords = (words, className, dataTip, dataTipDisable, color) => (
    <span className={className}>
        {words.slice(0, -1).join(" ")}
        <span className="text-nowrap">
            {" "}
            {words.slice(-1)}<i data-tip={dataTip} data-tip-disable={dataTipDisable} className={`material-icons text-${color} align-top icon-12`}>info</i>
        </span>
    </span>
)
const getComp = (words = "", className, dataTip = "", dataTipDisable, color) => (words.length > 1 ? ManyWords(words, className, dataTip, dataTipDisable, color) : OneWord(words, className, dataTip, dataTipDisable, color))

export default ({dataTip, dataTipDisable, text = "", className, color="serapide"}) => {
    const words = text.replace(/ +(?= )/g,'').split(" ")
    return text ? getComp(words, className, dataTip, dataTipDisable, color) : (<i data-tip={dataTip} data-tip-disable={dataTipDisable} className={`material-icons text-${color} align-top icon-12`}>info</i>)
}