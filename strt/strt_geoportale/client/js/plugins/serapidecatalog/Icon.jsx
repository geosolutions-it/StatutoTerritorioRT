/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import React from 'react';
import PropTypes from 'prop-types';

function Icon({
    type,
    color,
    labels = {
        operativo: 'PO',
        strutturale: 'PS'
    }
}) {
    return (
        <svg
            className="srtr-type-icon"
            viewBox="0 0 64 64">
            <rect
                x="0"
                y="0"
                width="64"
                height="64"
                fill="#343a40"
            />
            <text
                x="32"
                y="32"
                textAnchor="middle"
                alignmentBaseline="middle"
                fontSize="32"
                fontWeight="bold"
                fill={color}
            >
                {labels[type.toLowerCase()] || type.substring(0, 2)}
            </text>
        </svg>
    );
}

Icon.propTypes = {
    type: PropTypes.string,
    color: PropTypes.string
};

Icon.defaultProps = {
    color: '#FED403'
};

export default Icon;
