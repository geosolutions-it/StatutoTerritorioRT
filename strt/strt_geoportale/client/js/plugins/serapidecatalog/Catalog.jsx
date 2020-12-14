/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Pagination, FormGroup, InputGroup, Glyphicon, FormControl as FormControlRB } from 'react-bootstrap';
import Message from '@mapstore/components/I18N/Message';
import Loader from '@mapstore/components/misc/Loader';
import localizedProps from '@mapstore/components/misc/enhancers/localizedProps';
import Icon from '@js/plugins/serapidecatalog/Icon';
import { withResizeDetector } from 'react-resize-detector';
const FormControl = localizedProps('placeholder')(FormControlRB);

function ErrorResults() {
    return (
        <div className="strt-catalog-alert-message">
            <div><Glyphicon glyph="exclamation-mark"/></div>
            <h1><Message msgId="serapide.resultsErrorTitle"/></h1>
            <p><Message msgId="serapide.resultsError"/></p>
        </div>
    );
}

function NoResults() {
    return (
        <div className="strt-catalog-alert-message">
            <div><Glyphicon glyph="info-sign"/></div>
            <h1><Message msgId="serapide.noResultsAvailableTitle"/></h1>
            <p><Message msgId="serapide.noResultsAvailable"/></p>
        </div>
    );
}

function Empty() {
    return (
        <div className="strt-catalog-alert-message">
            <div><Glyphicon glyph="folder-open"/></div>
            <h1><Message msgId="serapide.noResultsAvailableTitle"/></h1>
        </div>
    );
}

function SerapideCatalog({
    loading: loadingProp,
    results,
    limit,
    page,
    totalCount,
    selected,
    onSelect,
    onSearch,
    error,
    width,
    isCatalogEmpty
}) {

    const [ q, setQ ] = useState('');
    function handleSearch(newOptions, isFirstRequest) {
        onSearch({
            limit,
            page,
            q,
            ...newOptions
        }, isFirstRequest);
    }

    useEffect(() => {
        handleSearch(undefined, true);
    }, []);

    const pages = totalCount !== undefined
        ? Math.ceil(totalCount / limit)
        : 1;
    const activePage = page || 1;

    const loading = loadingProp || totalCount === undefined;

    const sizeClassName = width < 480
        ? ' ms-sm'
        : width < 768
            ? ' ms-md'
            : width < 1024
                ? ' ms-lg'
                : ' ms-xl';

    return isCatalogEmpty ? null : (
        <div className={`srtr-serapide-catalog${sizeClassName}`}>
            <div className="srtr-serapide-catalog-head">
                <FormGroup>
                    <InputGroup>
                        <FormControl
                            placeholder="serapide.catalogFilterPlaceholder"
                            value={q || ''}
                            onChange={(event) => setQ(event.target.value)}
                        />
                        {q && <InputGroup.Addon
                            className="btn"
                            onClick={() => {
                                setQ('');
                                handleSearch({ page: 1, q: '' });
                            }}>
                            <Glyphicon glyph="1-close" />
                        </InputGroup.Addon>}
                        <InputGroup.Addon
                            className="btn"
                            onClick={() => handleSearch({ page: 1 })}>
                            {loading
                                ? <Loader size={16}/>
                                : <Glyphicon glyph="filter" />}
                        </InputGroup.Addon>
                    </InputGroup>
                </FormGroup>
            </div>
            <div className="srtr-serapide-catalog-body">
                <div>
                    {error && <ErrorResults />}
                    {!error && totalCount === undefined && <Empty />}
                    {!error && (totalCount === 0 || results.length === 0 && totalCount !== undefined) && <NoResults />}
                    {!error && results.length > 0 &&
                        results.map((entry = {}) => {
                            const selectedClassName = entry.id === selected?.id && ' ms-selected' || '';
                            return (
                                <div
                                    key={entry.id}
                                    className={`srtr-serapide-catalog-card${selectedClassName}`}
                                    onClick={() => {
                                        onSelect(entry);
                                    }}>
                                    <Icon
                                        type={entry?.type || ''}
                                        color="#FED403"
                                    />
                                    <div className="srtr-serapide-catalog-info">
                                        <h4>{entry?.name}</h4>
                                        <p>{entry?.comune}</p>
                                        <small>{entry?.id}</small>
                                    </div>
                                </div>
                            );
                        })}
                </div>
            </div>
            <div className="srtr-serapide-catalog-footer">
                <Pagination
                    prev
                    next
                    first
                    last
                    ellipsis
                    boundaryLinks
                    bsSize="small"
                    items={pages}
                    maxButtons={2}
                    activePage={activePage}
                    onSelect={(selectedPage) => selectedPage !== activePage
                        && handleSearch({ page: selectedPage })}
                />
                {totalCount && <div style={{ padding: 8 }}>
                    Risultati {results.length} di {totalCount}
                </div>}
            </div>

            {loading && <div
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    backgroundColor: 'rgba(255, 255, 255, 0.2)'
                }}>
            </div>}
        </div>
    );
}

SerapideCatalog.propTypes = {
    loading: PropTypes.boolean,
    results: PropTypes.array,
    limit: PropTypes.number,
    page: PropTypes.number,
    totalCount: PropTypes.number,
    selected: PropTypes.object,
    onSelect: PropTypes.func,
    onSearch: PropTypes.func,
    isCatalogEmpty: PropTypes.boolean
};

SerapideCatalog.defaultProps = {
    results: [],
    page: 1,
    limit: 12,
    onSelect: () => {},
    onSearch: () => {},
    isCatalogEmpty: false
};

const SerapideCatalogWithResizeDetector = withResizeDetector(SerapideCatalog);

export default SerapideCatalogWithResizeDetector;
