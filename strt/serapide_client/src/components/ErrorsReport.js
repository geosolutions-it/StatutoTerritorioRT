/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React, { useState } from 'react';
import { Collapse, Button, CardBody, Card, Alert} from 'reactstrap';
    
export default ({report = [], containerClass = "pt-4"}) => {
    const [isOpen, setIsOpen] = useState(true);
    const toggle = () => setIsOpen(!isOpen);
    return report.length === 0 ? null : (
    <div className={containerClass}>
          <Button color="danger" onClick={toggle} className={isOpen ? "mb-3" : ""}>{isOpen ?  "Nascondi Errori" : "Mostra Errori"}</Button>
          <Collapse isOpen={isOpen}>
            <Card>
              <CardBody style={{overflowY: 'scroll', maxHeight: "400px"}}>
              {report.map(({tipo, messaggio} = {},idx) => (
                  <Alert key={idx} color={tipo === "ERR" ? "danger" : "warning"}>
                    {messaggio}
                  </Alert>

              ))}
              </CardBody>
            </Card>
          </Collapse>
        </div>
      );
    }