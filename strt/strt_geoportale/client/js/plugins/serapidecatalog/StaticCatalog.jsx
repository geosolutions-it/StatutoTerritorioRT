/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import React from 'react';
import PropTypes from 'prop-types';
import Icon from '@js/plugins/serapidecatalog/Icon';
import { withResizeDetector } from 'react-resize-detector';

function StaticCatalog({
    results,
    onSelect,
    width
}) {

    if (results.length === 0) {
        return null;
    }

    return (
        <div className="srtr-serapide-catalog">
            <div className="srtr-serapide-catalog-head">
            </div>
            <div className="srtr-serapide-catalog-body">
                <div>
                    {results.length > 0 &&
                        results.map((entry = {}) => {
                            return (
                                <div
                                    key={entry.id}
                                    className="srtr-serapide-catalog-card"
                                    style={{
                                        ...(width < 768 ? {
                                            minWidth: "calc(100% - 8px)",
                                            maxWidth: "calc(100% - 8px)"
                                        } : {
                                            minWidth: "calc(50% - 8px)",
                                            maxWidth: "calc(50% - 8px)"
                                        }),
                                        border: 'none'
                                    }}
                                    onClick={() => {
                                        onSelect(entry);
                                    }}>
                                    <Icon
                                        type={entry?.type || ''}
                                        color="#FED403"
                                    />
                                    <div
                                        className="srtr-serapide-catalog-info"
                                    >
                                        <h4 style={{ fontSize: 24 }}>{entry?.name}</h4>
                                        <p style={{ whiteSpace: 'normal' }}>{entry?.description}</p>
                                    </div>
                                </div>
                            );
                        })}
                </div>
            </div>
            <div className="srtr-serapide-catalog-footer">
            </div>
        </div>
    );
}

StaticCatalog.propTypes = {
    results: PropTypes.array,
    onSelect: PropTypes.func
};

StaticCatalog.defaultProps = {
    results: [],
    onSelect: () => {}
};

const StaticCatalogWithResizeDetector = withResizeDetector(StaticCatalog);

export default StaticCatalogWithResizeDetector;
